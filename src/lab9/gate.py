"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    for name, value in pr.get("metrics", {}).items():
        if isinstance(value, (int, float)) and not math.isfinite(value):
            problems.append(f"non-finite metric {name}")
    rows = pr.get("rows", [])
    manifest = pr["manifest"]
    keys = [(row.get("item_id"), row.get("seed")) for row in rows]
    base_rows = base.get("rows", [])
    base_keys = [(row.get("item_id"), row.get("seed")) for row in base_rows]
    if len(rows) != manifest["items"] * len(manifest["seeds"]) or len(set(keys)) != len(keys):
        problems.append("invalid row count or duplicate rows")
    if set(keys) != set(base_keys):
        problems.append("item/seed pairs differ from baseline")
    if pr.get("evaluator_failures"):
        problems.append("evaluator failures")
    from lab9.graders import GRADERS
    for metric in spec["metrics"]:
        mid = metric["id"]
        if mid in GRADERS and any(row.get(mid) is None for row in rows):
            problems.append(f"missing graded values for {mid}")
    base_slices = {(r["item_id"], r["seed"]): set(r.get("slices", [])) for r in base_rows}
    if any(set(r.get("slices", [])) != base_slices.get((r["item_id"], r["seed"]), set()) for r in rows):
        problems.append("slice tags differ from baseline")
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        for section, key_fields in (("metrics", ("id",)), ("slices", ("name", "metric"))):
            current = {tuple(x.get(k) for k in key_fields): x for x in spec.get(section, [])}
            for old in base_spec.get(section, []):
                key = tuple(old.get(k) for k in key_fields)
                new = current.get(key)
                if new is None:
                    problems.append(f"removed {section} {key}")
                    continue
                old_th = old.get("threshold", {}) if section == "metrics" else old
                new_th = new.get("threshold", {}) if section == "metrics" else new
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"disabled blocking for {key}")
                for bound in ("min", "max", "max_increase"):
                    if bound in old_th and (bound not in new_th or
                        (new_th[bound] < old_th[bound] if bound == "min" else new_th[bound] > old_th[bound])):
                        problems.append(f"loosened {bound} for {key}")
                if old_th.get("no_significant_drop") and not new_th.get("no_significant_drop"):
                    problems.append(f"removed drop check for {key}")
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    for entry in spec.get("slices", []):
        name, metric = entry["name"], entry["metric"]
        values = per_item(pr, metric, slice_name=name)
        reference = per_item(base, metric, slice_name=name)
        keys = sorted(set(values) & set(reference))
        value = sum(values.values()) / len(values) if values else None
        failed = value is None or ("min" in entry and value < entry["min"])
        if entry.get("no_significant_drop") and keys:
            bs = spec.get("bootstrap", {})
            _, _, hi = stats.paired_bootstrap([values[k] for k in keys], [reference[k] for k in keys],
                                              n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            failed = failed or hi < 0
        identifier = f"slice:{name}/{metric}"
        if failed and entry.get("blocking"):
            blocked.append(identifier)
        lines.append(f"  {identifier} {value} {'BLOCK' if failed and entry.get('blocking') else 'warn' if failed else 'ok'}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

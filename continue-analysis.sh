#!/usr/bin/env bash
# continue-analysis.sh - spawn a user-chosen number of parallel coding agents
# through claude-yolo, Codex Luna/Spark, Muse, Agy, or Grok. Each agent takes one open item
# from remaining-work.md, reconstruct that segment of the G2 firmware as
# reviewed, buildable source on this Mac, and report back.  The script is the
# only writer of the Status / Owner / Notes cells in remaining-work.md.
#
#   ./continue-analysis.sh run -n 4              claim 4 items, run 4 agents in parallel, ingest results
#   ./continue-analysis.sh run -n 4 --loop       keep claiming batches until nothing is left
#   ./continue-analysis.sh run -n 2 --cli codex-yolo --component codec --dry-run
#   ./continue-analysis.sh run -n 2 --cli codex-spark-yolo --component codec --dry-run
#   ./continue-analysis.sh status | list [--status todo] [--component X] | show ID | prompt ID
#   ./continue-analysis.sh done|fail|block|release|claim ID [note]      manual status changes
#   ./continue-analysis.sh lock acquire|release|status ID              integration lock (agents use this)
#   ./continue-analysis.sh reset-stale [--to todo|failed]              recover rows whose agent died
#   ./continue-analysis.sh resume-paused       recover saved sessions after stopping/restarting
#   ./continue-analysis.sh dependencies [--reconcile] [--json]
#   ./continue-analysis.sh logs ID
#   ./continue-analysis.sh regenerate     rebuild the list from g2/build/source/flash-plan.json after work lands
#                                         (keeps non-todo status for rows whose ID and range are unchanged)
#
# Environment overrides:
#   CA_CLI             claude-yolo|codex-yolo|codex-spark-yolo|muse|agy|grok
#                      (default: claude-yolo)
#   CA_CLI_BIN         executable override             (default: selected CLI name)
#   CA_MODEL           model override; defaults: Claude claude-sonnet-5,
#                      Codex gpt-5.6-luna, Codex Spark gpt-5.3-codex-spark,
#                      Muse muse-spark-1.3-contributor;
#                      Agy and Grok use their configured defaults
#   CA_EFFORT          provider reasoning/effort level (default: unset)
#   CA_MAX_BUDGET_USD  Claude --max-budget-usd per agent (default: unset)
#   CA_TIMEOUT_MIN     limit each active attempt (excludes reset waits; default: 0)
#   CA_STAGGER_SEC     delay between agent launches    (default: 15)
#   CA_ALLOW_COMMIT=1  let agents git-commit their own files (default: agents must not commit)
#
# Usage limits: preserve files and the provider conversation, wait until reset + 60s,
# then resume the same session automatically. Unknown reset formats retry in 15m.
# Keep this process running for automatic wakeup; after stopping use resume-paused.
# State (logs, prompts, results, locks) lives under build/continue-analysis/,
# which the repository .gitignore already excludes.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_MD="$ROOT/remaining-work.md"
WORK_JSON="$ROOT/remaining-work.json"
STATE="$ROOT/build/continue-analysis"
CLI="${CA_CLI:-claude-yolo}"
CLI_BIN="${CA_CLI_BIN:-}"
CLI_BIN_EXPLICIT=0
[ -n "${CA_CLI_BIN:-}" ] && CLI_BIN_EXPLICIT=1
if [ -z "$CLI_BIN" ] && [ "$CLI" = claude-yolo ] && [ -n "${CA_CLAUDE_BIN:-}" ]; then
    CLI_BIN="$CA_CLAUDE_BIN"
    CLI_BIN_EXPLICIT=1
fi
MODEL="${CA_MODEL:-}"
MODEL_EXPLICIT=0
[ -n "${CA_MODEL:-}" ] && MODEL_EXPLICIT=1
STAGGER="${CA_STAGGER_SEC:-15}"
TIMEOUT_MIN="${CA_TIMEOUT_MIN:-0}"
PYTHON="${PYTHON:-python3}"

mkdir -p "$STATE/logs" "$STATE/prompts" "$STATE/results" "$STATE/running" "$STATE/locks" "$STATE/paused" "$STATE/deferred" "$STATE/knowledge"

die() { echo "continue-analysis: $*" >&2; exit 2; }
note() { echo "[continue-analysis] $*"; }

configure_cli() {
    case "$CLI" in
        claude-yolo)
            [ -n "$CLI_BIN" ] || CLI_BIN="claude-yolo"
            # Preserve compatibility on machines where the yolo wrapper has not been installed.
            if ! command -v "$CLI_BIN" >/dev/null 2>&1 && [ "$CLI_BIN" = claude-yolo ] && command -v claude >/dev/null 2>&1; then
                CLI_BIN="claude"
            fi
            [ -n "$MODEL" ] || MODEL="claude-sonnet-5" ;;
        codex-yolo)
            [ -n "$CLI_BIN" ] || CLI_BIN="codex-yolo"
            [ -n "$MODEL" ] || MODEL="gpt-5.6-luna" ;;
        codex-spark-yolo|codex-yolo-spark)
            [ -n "$CLI_BIN" ] || CLI_BIN="codex-yolo"
            [ -n "$MODEL" ] || MODEL="gpt-5.3-codex-spark"
            # Store the canonical provider name so command, output, and resume
            # handling remain identical to the Luna profile.
            CLI="codex-yolo" ;;
        muse)
            [ -n "$CLI_BIN" ] || CLI_BIN="muse"
            [ -n "$MODEL" ] || MODEL="muse-spark-1.3-contributor" ;;
        agy|grok)
            [ -n "$CLI_BIN" ] || CLI_BIN="$CLI" ;;
        *) die "unsupported CLI '$CLI' (use claude-yolo, codex-yolo, codex-spark-yolo, muse, agy, or grok)" ;;
    esac
}

configure_cli

[ -f "$WORK_MD" ] || die "missing $WORK_MD"
[ -f "$WORK_JSON" ] || die "missing $WORK_JSON"
command -v "$PYTHON" >/dev/null 2>&1 || die "python3 not found"

# ---------------------------------------------------------------------------
# Atomic lock helpers (macOS has no flock; mkdir is atomic on APFS/HFS+)
# ---------------------------------------------------------------------------
md_lock() {
    local tries=0
    while ! mkdir "$STATE/locks/md.lock.d" 2>/dev/null; do
        tries=$((tries + 1))
        [ "$tries" -gt 600 ] && die "could not acquire remaining-work.md lock (stale $STATE/locks/md.lock.d?)"
        sleep 0.1
    done
}
md_unlock() { rmdir "$STATE/locks/md.lock.d" 2>/dev/null || true; }

# ---------------------------------------------------------------------------
# Embedded Python: every read/write of remaining-work.md and prompt rendering
# ---------------------------------------------------------------------------
ca_py() {
    CA_ROOT="$ROOT" CA_WORK_MD="$WORK_MD" CA_WORK_JSON="$WORK_JSON" CA_STATE="$STATE" \
    CA_MODEL_NAME="$MODEL" CA_ALLOW_COMMIT="${CA_ALLOW_COMMIT:-0}" \
    "$PYTHON" - "$@" <<'PY'
import glob, hashlib, json, os, re, sys, datetime, textwrap
from collections import Counter, OrderedDict
sys.path.insert(0, os.path.join(os.environ["CA_ROOT"], "tools"))
from continue_analysis_dependencies import analyze_failure_text, build_record, load_record, merge_failure, refresh_record, save_record

ROOT = os.environ["CA_ROOT"]
MD = os.environ["CA_WORK_MD"]
JS = os.environ["CA_WORK_JSON"]
STATE = os.environ["CA_STATE"]
MODEL = os.environ["CA_MODEL_NAME"]
ALLOW_COMMIT = os.environ.get("CA_ALLOW_COMMIT") == "1"
STATUSES = ("todo", "in-progress", "done", "blocked", "failed")
META_GEN = "?"
DEFERRED = os.path.join(STATE, "deferred")
PRI_ORDER = {"P1": 0, "P2": 1, "P3": 2}
ROW_RE = re.compile(r"^\| ((?:AM|AD|BL|EM|CD|TC|CS|XC)-\d{3}) \|")


def load_rows():
    lines = open(MD, encoding="utf-8").read().split("\n")
    rows = OrderedDict()
    for i, ln in enumerate(lines):
        m = ROW_RE.match(ln)
        if not m:
            continue
        cells = [c.strip() for c in ln.split("|")]
        # ['', ID, Pri, Status, Range, Bytes, Kind, Targets, Owner, Notes, '']
        if len(cells) != 11:
            continue
        rows[cells[1]] = {"line": i, "id": cells[1], "pri": cells[2], "status": cells[3], "range": cells[4],
                          "bytes": cells[5], "kind": cells[6], "targets": cells[7], "owner": cells[8], "notes": cells[9]}
    return lines, rows


def save_rows(lines, rows):
    for r in rows.values():
        lines[r["line"]] = "| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["pri"], r["status"], r["range"], r["bytes"], r["kind"], r["targets"],
            r["owner"].replace("|", "/"), r["notes"].replace("|", "/").replace("\n", " "))
    tmp = MD + ".tmp"
    open(tmp, "w", encoding="utf-8").write("\n".join(lines))
    os.replace(tmp, MD)


def row_statuses(rows):
    return {item_id: row["status"] for item_id, row in rows.items()}


def add_note(row, note):
    if note not in row["notes"]:
        row["notes"] = (row["notes"] + " / " + note).strip(" /")


def refresh_deferred_rows(rows):
    """Refresh dependency status and return whether any work row changed."""
    changed = False
    statuses = row_statuses(rows)
    for path in glob.glob(os.path.join(DEFERRED, "*.json")):
        item_id = os.path.basename(path).split(".")[0]
        record = load_record(DEFERRED, item_id)
        row = rows.get(item_id)
        if not record or not row:
            continue
        was_ready = record.get("ready_for_completion", False)
        record = refresh_record(record, statuses)
        save_record(DEFERRED, record)
        if (row["status"] in ("done", "in-progress")
                or not (record.get("dependencies") or record.get("unresolved_dependencies"))):
            continue
        if record["pending_dependencies"]:
            if row["status"] != "blocked":
                row["status"] = "blocked"
                row["owner"] = ""
                add_note(row, "waiting on " + ",".join(record["pending_dependencies"]))
                changed = True
        elif row["status"] == "blocked":
            row["status"] = "todo"
            row["owner"] = ""
            add_note(row, "dependencies complete; queued for completion verification")
            changed = True
        if record["ready_for_completion"] and not was_ready:
            record["ready_at"] = datetime.datetime.now().astimezone().isoformat()
            save_record(DEFERRED, record)
    return changed


def reconcile_result_logs(rows):
    """Backfill durable dependency records from the newest historical result per item."""
    latest = {}
    paths = glob.glob(os.path.join(STATE, "logs", "*.result.json"))
    paths += glob.glob(os.path.join(STATE, "results", "*.json"))
    for path in paths:
        try:
            result = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        item_id = result.get("id") or os.path.basename(path).split(".")[0]
        if item_id not in rows:
            continue
        if item_id not in latest or os.path.getmtime(path) > os.path.getmtime(latest[item_id][0]):
            latest[item_id] = (path, result)
    structured_ids = set(latest)
    # Older runs often exited without writing the result file. Preserve and classify
    # those failures only when no structured result exists for that item.
    for path in glob.glob(os.path.join(STATE, "logs", "*.json")):
        if path.endswith(".result.json"):
            continue
        item_id = os.path.basename(path).split(".")[0]
        if item_id in structured_ids or item_id not in rows:
            continue
        try:
            envelope = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        text = str(envelope.get("result", "")) if isinstance(envelope, dict) else ""
        match = re.search(r"CA-STATUS:\s*(done|partial|blocked|failed)", text, re.I)
        issue = analyze_failure_text(text)
        if (not match and not (isinstance(envelope, dict) and envelope.get("is_error"))
                and issue["kind"] == "agent-failure"):
            continue
        reported = match.group(1).lower() if match else ("partial" if issue["retryable"] else "blocked")
        if reported == "partial" and issue["kind"] in ("authentication", "permission", "tool"):
            reported = "blocked"
        result = {"id": item_id, "status": reported, "summary": issue["description"][:200],
                  "blockers": [issue["description"]], "followups": [],
                  "missing_requirements": [issue], "infer_dependencies": False,
                  "verification_only": reported == "done"}
        if item_id not in latest or os.path.getmtime(path) > os.path.getmtime(latest[item_id][0]):
            latest[item_id] = (path, result)
    statuses = row_statuses(rows)
    for item_id, (path, result) in latest.items():
        row = rows[item_id]
        if row["status"] == "done":
            continue
        reported = result.get("status")
        if reported not in ("partial", "blocked", "failed", "done"):
            continue
        saved = dict(result)
        if reported == "done":
            saved["status"] = "partial"
            saved["verification_only"] = True
            saved["infer_dependencies"] = False
            remaining = saved.get("remaining_segments") or []
            if not isinstance(remaining, list):
                remaining = [remaining]
            remaining.append("Re-run the reported completion checks; the prior CLI exited nonzero or was not ingested as done.")
            saved["remaining_segments"] = remaining
        record = build_record(saved, item_id, path, set(rows), statuses)
        save_record(DEFERRED, record)
        if not record.get("verification_only"):
            row["notes"] = row["notes"].replace(
                "saved prior progress; queued for completion verification",
                "saved prior progress; queued for continuation")
        if row["status"] == "in-progress":
            continue
        if record["pending_dependencies"]:
            row["status"] = "blocked"
            row["owner"] = ""
            add_note(row, "waiting on " + ",".join(record["pending_dependencies"]))
        elif reported == "blocked":
            row["status"] = "blocked"
            row["owner"] = ""
            add_note(row, "saved missing requirement; inspect dependencies report")
        elif reported in ("partial", "done") and row["status"] == "failed":
            row["status"] = "todo"
            row["owner"] = ""
            add_note(row, ("saved prior progress; queued for completion verification"
                           if record.get("verification_only") else
                           "saved prior progress; queued for continuation"))
    refresh_deferred_rows(rows)
    return len(latest)


def load_items():
    d = json.load(open(JS, encoding="utf-8"))
    return d["meta"], OrderedDict((it["id"], it) for it in d["items"])


def comp_of(item_id):
    return {"AM": "apollo_main", "AD": "apollo_main", "BL": "apollo_bootloader", "EM": "ble_em9305",
            "CD": "codec", "TC": "touch", "CS": "case", "XC": "cross-cutting"}[item_id[:2]]


def cmd_status(args):
    _, rows = load_rows()
    by = OrderedDict()
    for r in rows.values():
        by.setdefault(comp_of(r["id"]), Counter())[r["status"]] += 1
    print("%-18s %6s %12s %6s %8s %7s %6s" % ("component", "todo", "in-progress", "done", "blocked", "failed", "total"))
    tot = Counter()
    for c, cnt in by.items():
        tot.update(cnt)
        print("%-18s %6d %12d %6d %8d %7d %6d" % (c, cnt["todo"], cnt["in-progress"], cnt["done"], cnt["blocked"], cnt["failed"], sum(cnt.values())))
    print("%-18s %6d %12d %6d %8d %7d %6d" % ("TOTAL", tot["todo"], tot["in-progress"], tot["done"], tot["blocked"], tot["failed"], sum(tot.values())))
    ip = [r for r in rows.values() if r["status"] == "in-progress"]
    if ip:
        print("\nin-progress:")
        for r in ip:
            print("  %s  %s  %s" % (r["id"], r["owner"], r["notes"][:100]))

    waiting = []
    for path in sorted(glob.glob(os.path.join(DEFERRED, "*.json"))):
        record = load_record(DEFERRED, os.path.basename(path).split(".")[0])
        if record and record.get("pending_dependencies"):
            waiting.append((record["id"], record["pending_dependencies"]))
    if waiting:
        print("\nwaiting on dependencies:")
        for item_id, pending in waiting:
            print("  %s  %s" % (item_id, ", ".join(pending)))

    paused_dir = os.path.join(STATE, "paused")
    for name in sorted(os.listdir(paused_dir)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(paused_dir, name)) as f:
                checkpoint = json.load(f)
            if checkpoint.get("resume_at"):
                when = datetime.datetime.fromtimestamp(checkpoint["resume_at"]).astimezone().isoformat()
                print("  saved session %s: resume due %s; use resume-paused if supervisor stopped" % (checkpoint["id"], when))
        except (OSError, ValueError, KeyError):
            pass


def parse_filters(args):
    f = {"status": None, "component": None, "kind": None, "ids": None, "priority": None}
    i = 0
    rest = []
    while i < len(args):
        a = args[i]
        if a in ("--status", "--component", "--kind", "--ids", "--priority") and i + 1 < len(args):
            f[a[2:]] = args[i + 1]
            i += 2
        else:
            rest.append(a)
            i += 1
    return f, rest


def matches(r, f):
    if f["status"] and r["status"] != f["status"]:
        return False
    if f["component"] and comp_of(r["id"]) != f["component"]:
        return False
    if f["kind"] and f["kind"] not in r["kind"]:
        return False
    if f["priority"] and r["pri"] != f["priority"]:
        return False
    if f["ids"] and r["id"] not in [x.strip() for x in f["ids"].split(",")]:
        return False
    return True


def cmd_list(args):
    f, _ = parse_filters(args)
    _, rows = load_rows()
    for r in rows.values():
        if matches(r, f):
            print("%s %s %-11s %-28s %9s %-12s %s" % (r["id"], r["pri"], r["status"], r["range"], r["bytes"], r["kind"], r["targets"][:70]))


def cmd_show(args):
    _, items = load_items()
    it = items.get(args[0]) or sys.exit("unknown item %s" % args[0])
    _, rows = load_rows()
    r = rows.get(args[0], {})
    print(json.dumps({"row": r, "item": {k: v for k, v in it.items() if k != "functions"},
                      "functions": it.get("functions", [])[:200],
                      "deferred": load_record(DEFERRED, args[0])}, indent=1))


def cmd_dependencies(args):
    lines, rows = load_rows()
    reconciled = reconcile_result_logs(rows) if "--reconcile" in args else 0
    changed = refresh_deferred_rows(rows)
    if reconciled or changed:
        save_rows(lines, rows)
    records = []
    for path in sorted(glob.glob(os.path.join(DEFERRED, "*.json"))):
        record = load_record(DEFERRED, os.path.basename(path).split(".")[0])
        if record:
            records.append(record)
    if "--json" in args:
        print(json.dumps({"reconciled_results": reconciled, "deferred": records}, indent=2))
        return
    if reconciled:
        print("reconciled %d latest result logs" % reconciled)
    if not records:
        print("no deferred work records")
    for record in records:
        state = ("ready for completion verification" if record.get("ready_for_completion") else
                 "waiting on " + ",".join(record.get("pending_dependencies", [])) if record.get("pending_dependencies") else
                 "saved requirements; continuation available")
        print("%-7s %-38s %s" % (record["id"], state, record.get("summary", "")[:100]))


def cmd_select(args):
    """Print up to N claimable IDs, priority-first, spread across components."""
    f, rest = parse_filters(args)
    n = int(rest[0]) if rest else 1
    retry_failed = "--retry-failed" in rest
    ignore_deps = "--ignore-deps" in rest
    no_spread = "--no-spread" in rest
    lines, rows = load_rows()
    if refresh_deferred_rows(rows):
        save_rows(lines, rows)
    _, items = load_items()
    done = {i for i, r in rows.items() if r["status"] == "done"}
    # Saved sessions must be recovered, never replaced by a fresh claim.
    paused = {name.split(".")[0] for name in os.listdir(os.path.join(STATE, "paused")) if name.endswith(".json")}
    cands = []
    for r in rows.values():
        if r["id"] in paused:
            continue
        if not matches(r, {**f, "status": None}):
            continue
        if r["status"] == "todo" or (retry_failed and r["status"] == "failed"):
            deps = items.get(r["id"], {}).get("depends", [])
            if deps and not ignore_deps and not all(d in done for d in deps):
                continue
            cands.append(r)
    cands.sort(key=lambda r: (PRI_ORDER.get(r["pri"], 9), r["id"]))
    if no_spread:
        picked = cands[:n]
    else:
        # round-robin over components so parallel agents touch different trees
        buckets = OrderedDict()
        for r in cands:
            buckets.setdefault(comp_of(r["id"]), []).append(r)
        picked = []
        while len(picked) < n and any(buckets.values()):
            for c in list(buckets):
                if buckets[c] and len(picked) < n:
                    picked.append(buckets[c].pop(0))
    skipped = [r["id"] for r in rows.values() if r["status"] == "todo" and matches(r, {**f, "status": None})
               and items.get(r["id"], {}).get("depends") and not ignore_deps
               and not all(d in done for d in items[r["id"]]["depends"])]
    if skipped and not picked:
        sys.stderr.write("select: %d matching items are waiting on dependencies (%s...); use --ignore-deps to force\n"
                         % (len(skipped), ", ".join(sorted({d for i in skipped for d in items[i]["depends"]}))))
    for r in picked:
        print(r["id"])


def cmd_set(args):
    item_id, status = args[0], args[1]
    owner = args[2] if len(args) > 2 else None
    notes = args[3] if len(args) > 3 else None
    append = "--append" in args
    if status not in STATUSES:
        sys.exit("bad status %s" % status)
    lines, rows = load_rows()
    r = rows.get(item_id) or sys.exit("unknown item %s" % item_id)
    r["status"] = status
    if owner is not None and owner != "-":
        r["owner"] = owner
    if notes is not None and notes != "-":
        r["notes"] = (r["notes"] + " / " + notes).strip(" /") if append and r["notes"] else notes
    refresh_deferred_rows(rows)
    save_rows(lines, rows)
    print("%s -> %s" % (item_id, status))


def cmd_get(args):
    _, rows = load_rows()
    r = rows.get(args[0]) or sys.exit("unknown item %s" % args[0])
    print(r[args[1]] if len(args) > 1 else json.dumps(r))


PLAYBOOK = {
    "apollo_main": """
Component playbook - Apollo main application (Cortex-M55, Apollo510B):
- Decompilation for every address: `g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl`
  (`grep '"address_hex":"0x0043E1FA"'`).  Names/tiers/buckets: `g2/build/transparent/function-db.json`
  (regenerate with `make -C g2 transparent-db` if missing).  Hand-authored function maps:
  `g2/tools/manifests/*-function-map.tsv`; audits: `g2/docs/research/g2-*.md`, `cordio-*.md`, `lvgl-*.md`, ...
- Ghidra, a JDK, and analyzed Apollo projects exist on this Mac (not on PATH): look under
  /Applications, ~/ghidra*, ~/Library, and `g2/tools/run_apollo_ghidra_chunk_batch.sh` for the env names.
- Upstream families (bucket lvgl/cordio/ambiqsuite/littlefs/nanopb/cmsis-freertos/tlsf/cjson/tinyframe/
  liblc3/easylogger/freetype/lz4/iar-dlib): use the pinned vendored snapshot in `g2/components/shared/<family>/`
  with the recovered configuration (see the family's `*-source-closure` Make targets and audits).  Byte-identical
  compilation under `apple-clang` is the strongest proof; a documented, tested behavioral match is acceptable
  where IAR codegen differs, but it must be reviewed C, not pasted decompiler output.
- First-party functions: write clean-room MIT C in `g2/components/apollo_main/core_overlay/<module>.c` from the
  decompilation, the referenced strings/tables, and the callers.  Preserve the stock ABI and entry address.
- Admission: add the translation unit to `g2/components/apollo_main/core_overlay/overlay.json` (`sources`, a
  `relocated_leaves` entry with expected size/sha256/relocations, and a `patch_sites` entry redirecting the stock
  entry), following an existing entry of the same shape.  Build with `make -C g2 core-component`, then
  `make -C g2 source` and `python3 g2/tools/open_cfw.py verify-artifacts --manifest g2/manifests/g2-2.2.6.10-core-source.json --output-dir g2/build/source --toolchain-profile apple-clang`
  must report zero unresolved flash regions.  Update the manifest provider sha256/size pins the way the
  most recent commits do (`git log -p -3 -- g2/manifests/g2-2.2.6.10-core-source.json`).
- Also add each reviewed function to `g2/tools/transparent/reviewed_sources.json` so the transparent image
  stops trapping it (`make -C g2 transparent-test`).
- Data (AD items): find the referencing code, identify the structure (LVGL `lv_img_dsc_t`/font tables,
  FreeType payloads, Cordio/SMP tables, protobuf descriptors, string pools, descriptor tables), and provide a
  source representation: generator + source asset (with license), or authored C data with a derivation note.
  A `const uint8_t x[] = {...}` copied from the stock image does NOT close the item.
""",
    "apollo_bootloader": """
Component playbook - Apollo bootloader (Cortex-M55, run base 0x00410000):
- Official bytes: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` (file offset = address - 0x00410000).
- Ledgers: `g2/tools/manifests/g2-bootloader-*.tsv`, analyzers `g2/tools/analyze_g2_bootloader_*.py`, audits
  `g2/docs/research/g2-bootloader-*.md`, and the dual-image littlefs / EasyLogger / AmbiqSuite MSPI closures.
  There is no bootloader Ghidra harvest yet (XC-009); disassemble with `llvm-objdump --triple=thumbv8.1m.main`
  (`xcrun llvm-objdump`) or the local Ghidra.
- Admission: `g2/components/bootloader/core_overlay/` (exact in-place source where the compiled bytes fit, or
  relocated leaves in the free tail `[0x004350BC,0x00438000)` with entry redirects), registered in that
  component's overlay.json; `make -C g2 bootloader-component`, then `make -C g2 source` + verify-artifacts.
- AmbiqSuite 5.1.0 functions must come from the vendored snapshot (`make -C g2 ambiqsuite-snapshot`).
""",
    "ble_em9305": """
Component playbook - EM9305 BLE controller (ARCv2 EM7D):
- Image: `g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin`; record table and addresses in
  `g2/docs/memory-map.md` ("EM9305 Bluetooth controller"); per-function names from
  `g2/tools/analyze_em9305_sdk_discovery.py --include-functions` and `g2/tools/manifests/em9305-*.tsv`;
  Ghidra residual rounds in `g2/research/corpus/em9305/ghidra/`; audits `g2/docs/research/em9305-*.md`.
- Most retained bytes match proprietary Packetcraft controller / EM vendor objects (no public source).  Closing
  an item means clean-room C reconstruction from the decompilation, the SDK headers' public ABI, and the
  Packetcraft host-stack conventions in `g2/components/shared/cordio/`, with host tests that replay the
  decoded behavior.  Never copy SDK object bytes; never link `.a`/`.o` from the SDK.
- Toolchain: `components/em9305/source_overlay/build_overlay.py` needs an ARC GCC (`OPENCFW_ARC_GCC`, -mcpu=em).
  This depends on XC-003; if the toolchain is still missing, do only the analysis/C authoring and host tests,
  and report `partial` with the exact blocker.
- Admission: extend `g2/components/em9305/source_overlay/` (tail-branch veneer at the stock entry + relocated
  C in the same sector), rebuild with `python3 g2/components/em9305/source_overlay/build_overlay.py`, update the
  provider pins in the core-source manifest, then `make -C g2 source` + verify-artifacts.
""",
    "codec": """
Component playbook - GX8002 codec/DSP (C-SKY CK804EF):
- Package: `g2/blobs/official/g2-2.2.6.10/firmware_codec.bin`; layout in `g2/tools/manifests/g2-codec-fwpk-segment-map.tsv`
  and `g2-codec-stage2-section-map.tsv`; current ownership in `g2/docs/research/gx8002-source-candidate-build.json`.
- Toolchain: `g2/build/csky-macos/install/bin/csky-unknown-elf-gcc`; public SDK checkout (MIT) at
  `g2/build/upstream-nationalchip-lvp-kws` (headers + boot/platform C usable; its `.o/.a` must never be linked).
  Named driver-symbol candidates: `g2/docs/research/gx8002-upstream-object-candidates.{md,json}`;
  C-SKY Ghidra exports: `gx8002-known-function-harvest.json` and `gx8002-ghidra-processor.md`.
- Pattern (follow the newest tranche, e.g. `git log -3 --stat -- g2/components/shared/gx8002`): C in
  `g2/components/shared/gx8002/runtime_gx8002_<x>.c`, a decoded-trace verifier `g2/tools/verify_gx8002_<x>.py`
  (compile with the C-SKY toolchain, compare instructions/MMIO traces against the stock bytes, allow only
  consistent scratch-register renaming), `g2/tests/test_gx8002_<x>.py`, an audit `g2/docs/research/gx8002-<x>-source.md`
  + JSON, then register the tranche in `g2/tools/build_gx8002_source_candidate.py` and the `gx8002-source-candidate`
  test list in `g2/Makefile`.  `make -C g2 gx8002-source-candidate` and `make -C g2 codec-source-experimental`
  must pass; update `docs/research/gx8002-source-candidate-build.{json,md}` and the experimental manifest pins.
- Runtime addresses: stage1 IRAM 0x10000000, stage2 IRAM 0x10002800, image A XIP text at public XIP base
  0x10200000 + flash offset, image A SRAM text 0x10023400, image B SRAM text 0x10003000 (details in the item).
- Model/NPU items: reconstruct the decoded gxDNN/SNPU descriptor and command formats into a source-authored
  generator (see XC-006); retained weight/command bytes as arrays do not count.
""",
    "touch": """
Component playbook - PSoC 4000T touch controller (Cortex-M0+):
- Candidate source image: `g2/components/touch/source_image/` (build_image.py, /opt/homebrew/opt/llvm/bin/clang,
  --target=armv6m-none-eabi); shared runtime in `g2/components/shared/touch/`; audits `g2/docs/research/g2-touch-*.md`.
- Route it: create/extend a source manifest profile (see `g2/manifests/g2-2.2.6.10-codec-source-experimental.json`
  for the `component_overrides` shape) with `touch` -> `source_build`, size/sha256 pins, a Make target, and
  verify-artifacts.  Turn every hardware-dependent assumption (resident ABI slot indices, vector ownership) into
  explicit, documented configuration with tests; hardware qualification stays deferred, but software routing is not.
""",
    "case": """
Component playbook - STM32G0 charging case (Cortex-M0+):
- Candidate source image: `g2/components/case/source_image/` (build_image.py --check), shared runtime in
  `g2/components/shared/case/`, audits `g2/docs/research/g2-case-*.md` and `g2-box-*.md`, Ghidra frontier in
  `g2/research/corpus/case/ghidra/final-frontier/functions.jsonl`.
- Route it the same way as touch (source manifest profile, `case` -> `source_build`, pins, verify-artifacts).
""",
    "cross-cutting": """
Cross-cutting playbook: read the item summary; the relevant tools are named there.  Keep every change
reproducible on macOS, add tests for new gates, and document the result in `g2/docs/source-only-goal.md`.
""",
}


def render_prompt(it, row):
    comp = it["component"]
    fn_lines = []
    for f in it.get("functions", []):
        fn_lines.append("  %s..%s %5d B  %-40s tier=%-10s bucket=%-34s %s" % (
            f["addr"], f["end"], f["size"], f["name"][:40], f.get("tier"), f.get("bucket"),
            ("families=" + ",".join(f.get("families") or [])) if f.get("families") else ""))
    regions = it.get("regions") or ([it["region"]] if it.get("region") else [])
    reg_lines = []
    for r in regions:
        if "start" in r and "end" in r:
            reg_lines.append("  %s..%s %s" % (r["start"], r["end"], (r.get("description") or r.get("label") or "")[:150]))
        else:
            reg_lines.append("  " + json.dumps(r)[:200])
    extra = []
    for key in ("subranges", "windows", "readiness_rows", "clusters"):
        if it.get(key):
            extra.append("%s:\n%s" % (key, "\n".join("  " + json.dumps(x) for x in it[key][:60])))
    if comp == "codec":
        extra.append("package offsets: %s..%s (runtime resolved: %s)" % (it.get("package_start"), it.get("package_end"), it.get("runtime_resolved")))
    commit_rule = ("You MAY `git commit` only the files you created or changed, with a message naming the item ID."
                   if ALLOW_COMMIT else
                   "Do NOT run `git commit`, `git add`, `git stash`, `git checkout`, `git reset`, or any history-changing git command; leave the working tree for the human to review and commit.")
    result_path = os.path.join(STATE, "results", it["id"] + ".json")
    header = textwrap.dedent("""\
    You are a runner-managed worker reconstructing the Even Realities G2 firmware as buildable
    source in the openCFW repository at %(root)s (macOS build host).  You own exactly ONE work item from
    remaining-work.md. Work only on that item; do not launch additional workers. Read only the "Completion
    conditions" and "Build and evidence tracks" sections of `g2/docs/source-only-goal.md`, then the
    relevant links in `g2/docs/README.md`. Retrieve historical evidence by ID/address, in bounded excerpts.

    HARD RULES
    1. Goal: no functionality in the final firmware may depend on opaque code or on bytes extracted from the
       stock image.  Replace retained executable functionality with reviewed C (or identified, pinned upstream
       source with its recovered configuration); reconstruct required data/assets or provide explicit
       source-authored replacements; the stock firmware is only an analysis / differential-test oracle.
    2. These do NOT count as completion: trap stubs, typed provider interfaces that still call retained bytes,
       decompiler output that merely compiles, binary bytes encoded as C arrays, and "candidate" source that is
       not production-routed.  Never label a retained or inferred region as source-owned without evidence.
    3. No hardware operation of any kind (no flashing, DFU, MMIO probing, signing, publishing).  Hardware
       qualification stays "blocked by unavailable physical evidence" and must be recorded as such.
    4. Clean-room and licensing: no leaked/vendor source, no SDK `.o`/`.a` linking, MIT for new openCFW code,
       upstream license + exact commit for vendored code (see CONTRIBUTING.md).
    5. Scope discipline: only create/modify files needed for this item (its C, headers, verifier/test, audit
       doc, overlay/manifest/Makefile registration).  Other agents are editing this tree at the same time:
       re-read any shared file (overlay.json, Makefile, manifests, build_gx8002_source_candidate.py,
       docs/progress.md, docs/source-only-goal.md) immediately before editing it, make minimal additive edits,
       and never reformat or rewrite whole shared files.  Do not revert or "fix" other people's uncommitted
       work.  %(commit_rule)s
    6. Integration lock: before any step that builds or rewrites shared build outputs or manifests
       (`make -C g2 source`, `make -C g2 core-component`, `make -C g2 bootloader-component`,
       `make -C g2 gx8002-source-candidate`, `make -C g2 codec-source-experimental`, editing a manifest's
       provider pins, or editing overlay.json), run `./continue-analysis.sh lock acquire %(id)s` (it waits),
       do the step, then `./continue-analysis.sh lock release %(id)s`.  Narrow unit tests and compiles of your
       own translation unit do not need the lock.  Prefer private output dirs (`--output`/`--output-dir` under
       `g2/build/continue-analysis/%(id)s/`) for exploratory builds.
    7. Documentation: the four SHA-256-pinned records (`g2/docs/source-coverage.md`, `memory-map.md`,
       `upstream-inventory.md`, `linux-reproducible-build.md`) must NOT be edited by you (XC-008 folds audits
       into them).  Do write: a research audit `g2/docs/research/<family>-<closure>.md` (append if it exists),
       a dated entry appended to `g2/docs/progress.md`, and a short checkpoint appended to
       `g2/docs/source-only-goal.md`.  Also update the component EVIDENCE/README/NOTICE files when they list
       functions or licenses.  Never edit remaining-work.md directly; the runner updates it from your result.
    8. Verify honestly: run the narrow tests you add, the component build, and the applicable gate; report
       exactly what ran and what did not.  Partial progress is fine when reported as `partial`.

    """) % {"root": ROOT, "commit_rule": commit_rule, "id": it["id"]}
    body = []
    policy_path = os.path.join(ROOT, "docs", "g2-reconstruction-driver-prompt.md")
    with open(policy_path, encoding="utf-8") as policy_file:
        policy = policy_file.read().split("\n---\n", 1)[1].strip()
    mode = "tooling" if it.get("kind") == "tooling" else "reconstruction"
    body.append("EXECUTION MODE: %s. The assigned item below is already selected.\n" % mode +
                "Apply this workflow within the hard rules and component admission contract; do not launch a separate process review.\n"
                "For reconstruction items, do not substitute workflow improvements or an evidence-only audit for source recovery.\n" + policy)
    scope = {k: v for k, v in it.items() if k not in ("status", "owner", "notes")}
    scope_hash = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()
    knowledge_path = os.path.join(STATE, "knowledge", it["id"] + ".json")
    body.append("DURABLE KNOWLEDGE CHECKPOINT: %s\n"
                "Read this file if it exists, and validate its evidence before reuse. Write JSON atomically via a sibling temporary file and os.replace.\n"
                "Use schema_version=1, id=%s, scope_sha256=%s, updated_at, input_fingerprints, proven_facts, unresolved_facts,\n"
                "completed_segments, rejected_hypotheses, validation_receipts, blockers, next_action, active_processes.\n"
                "This scope hash identifies the assignment, NOT source freshness; separately hash relevant working-tree inputs.\n"
                "Keep this current checkpoint concise; archive detailed receipts under the item's private output directory.\n"
                "The runner preserves this sidecar but does not interpret it as queue status or automatically watch its fingerprints.\n"
                "If only unchanged blockers remain, write status=blocked with explicit dependencies/wake conditions; do not return partial solely to repeat gates."
                % (knowledge_path, it["id"], scope_hash))
    body.append("WORK ITEM %s  (component %s, priority %s, kind %s, route %s)" % (it["id"], comp, it["priority"], it["kind"], it["route"]))
    body.append("Summary: %s" % it["summary"])
    body.append("Architecture: %s" % it.get("arch"))
    body.append("Flash/runtime range: %s..%s  (%s bytes)" % (it["start"], it["end"], format(it.get("bytes") or 0, ",")))
    if it.get("function_count"):
        body.append("Functions: %s (%s function bytes)" % (it["function_count"], it.get("function_bytes")))
    if it.get("depends"):
        body.append("Depends on: %s" % ", ".join(it["depends"]))
    if reg_lines:
        body.append("Official (retained) regions in the production flash plan touched by this item:\n" + "\n".join(reg_lines[:40]))
    if fn_lines:
        body.append("Retained functions in this item (from g2/build/transparent/function-db.json; FUN_* names are unattributed):\n" + "\n".join(fn_lines))
    if extra:
        body.append("\n".join(extra))
    body.append("Current queue state: %s\nHistorical notes remain in remaining-work.md; retrieve them only if needed."
                % json.dumps({k: v for k, v in row.items() if k != "notes"}))
    deferred = load_record(DEFERRED, it["id"])
    if deferred:
        body.append("SAVED PRIOR PROGRESS (do not redo completed work):\n%s" % json.dumps(deferred, indent=2))
        if deferred.get("ready_for_completion"):
            body.append("All recorded prerequisite items are done. Address the saved remaining segments, rerun the completion gates, and mark this item done only if its full range now meets the definition of done.")
    body.append(PLAYBOOK.get(comp, ""))
    body.append(textwrap.dedent("""\
    BEFORE YOU START
    - Confirm the range is still retained (the list was generated on %(gen)s and other agents land work
      continuously).  For Apollo main / bootloader / EM9305 run from the repo root:
        python3 -c "import json;d=json.load(open('g2/build/source/flash-plan.json'));a,b=int('%(start)s',16),int('%(end)s',16);[print(r['target_address_hex'],r['end_exclusive_hex'],r['address_status'],r['function'][:90]) for r in d['flash_regions'] if r['component']=='%(comp)s' and r['target_address']<b and r['end_exclusive']>a]"
      (rebuild the plan first with `make -C g2 source` under the integration lock if it is stale).  For the
      codec compare the package offsets against the `ownership` list in
      `g2/docs/research/gx8002-source-candidate-build.json` (kind retained_stock).  Skip anything another agent
      already routed (grep overlay.json / the component sources for the address or symbol).
    - Check `git status --short` and `git log --oneline -5` so you do not duplicate landed work.

    DELIVERABLES
    - Reviewed source + registration so the component build produces the bytes of this range from source.
    - Tests/verifiers that pin the behavior against the stock oracle (host tests; no hardware).
    - Audit doc, progress entry, source-only-goal checkpoint (append-only).
    - Write the result file %(result)s as JSON:
      {"id": "%(id)s", "status": "done|partial|blocked|failed",
       "summary": "<= 200 chars, what is now source-owned and what remains",
       "functions_completed": ["0x...."], "bytes_source_owned": <int>,
       "files_changed": ["..."], "tests_run": ["..."], "gates_run": ["..."],
       "blockers": ["..."], "followups": ["..."],
       "dependencies": [{"id": "BL-005", "reason": "why it is required", "required_for": "completion"}],
       "completion_after": ["BL-005"],
       "remaining_segments": ["specific address/range or verification still required"],
       "missing_requirements": [{"kind": "tool|source|configuration|license|hardware|integration", "description": "what is missing"}]}
      Use exact remaining-work IDs in `dependencies` and `completion_after`. Omit those fields when no other
      work item is a prerequisite. The runner saves this state, waits while prerequisites are unfinished,
      and queues this item for completion verification when they become done.
      `done` means every byte of the range is now produced from reviewed source that is production-routed
      (data: from a source-authored representation) and the gates passed.  `partial` means real progress landed
      but the range is not closed; describe precisely what remains so the item can be re-run.  `blocked` means
      the item cannot be closed in software (say why: proprietary inputs, missing toolchain, ...).
    - End your final message with one line: `CA-STATUS: <done|partial|blocked|failed>`.
    """) % {"result": result_path, "id": it["id"], "gen": META_GEN, "start": it["start"], "end": it["end"],
            "comp": comp})
    return header + "\n".join(body) + "\n"


def cmd_prompt(args):
    global META_GEN
    meta, items = load_items()
    META_GEN = meta.get("generated", "?")
    _, rows = load_rows()
    it = items.get(args[0]) or sys.exit("unknown item %s" % args[0])
    sys.stdout.write(render_prompt(it, rows.get(args[0], {})))


def cmd_ingest(args):
    """ingest ID RUNSTAMP EXITCODE -> prints final status; updates the row."""
    item_id, stamp, exit_code = args[0], args[1], int(args[2])
    result_path = os.path.join(STATE, "results", item_id + ".json")
    log_path = os.path.join(STATE, "logs", "%s.%s.json" % (item_id, stamp))
    status, summary, res, log_text = None, "", None, ""
    synthetic_failure, issue = False, None
    if os.path.exists(result_path):
        try:
            res = json.load(open(result_path, encoding="utf-8"))
            status = res.get("status")
            summary = str(res.get("summary", ""))[:160]
        except Exception as e:  # noqa
            summary = "unreadable result file: %s" % e
    if status is None and os.path.exists(log_path):
        try:
            out = json.load(open(log_path, encoding="utf-8"))
            log_text = out.get("result", "") if isinstance(out, dict) else ""
            m = re.search(r"CA-STATUS:\s*(done|partial|blocked|failed)", log_text or "")
            if m:
                status = m.group(1)
                summary = summary or (log_text or "").strip().split("\n")[0][:160]
            if isinstance(out, dict) and out.get("is_error"):
                summary = summary or str(out.get("result", ""))[:160]
        except Exception:
            pass
    if status is None:
        summary = summary or ("agent exited %d without a result file" % exit_code)
        issue = ({"kind": "timeout", "retryable": True, "description": summary}
                 if exit_code == 124 else analyze_failure_text(log_text or summary))
        synthetic_failure = True
        status = "partial" if issue["retryable"] else "blocked"
        res = {"id": item_id, "status": status, "summary": summary,
               "blockers": [issue["description"]], "followups": [],
               "missing_requirements": [issue], "infer_dependencies": False}
    elif res is None and status != "done":
        issue = analyze_failure_text(log_text or summary)
        synthetic_failure = True
        if status == "partial" and issue["kind"] in ("authentication", "permission", "tool"):
            status = "blocked"
        res = {"id": item_id, "status": status, "summary": summary,
               "blockers": [issue["description"]], "followups": [],
               "missing_requirements": [issue], "infer_dependencies": False}
    mapping = {"done": "done", "partial": "todo", "blocked": "blocked", "failed": "failed"}
    new = mapping.get(status, "failed")
    completion_needs_verification = new == "done" and exit_code != 0 and res is not None
    if completion_needs_verification:
        status, new = "partial", "todo"
        summary = "completion claimed with exit %d; saved for verification: %s" % (exit_code, summary)
        res = dict(res)
        res["status"] = "partial"
        res["verification_only"] = True
        res["infer_dependencies"] = False
        remaining = res.get("remaining_segments") or []
        if not isinstance(remaining, list):
            remaining = [remaining]
        remaining.append("Re-run the reported completion checks because the prior CLI exited nonzero.")
        res["remaining_segments"] = remaining
    elif new == "done" and exit_code != 0:
        new, summary = "failed", "exit %d but log says done without a result file: %s" % (exit_code, summary)
    lines, rows = load_rows()
    r = rows[item_id]
    archive_path = os.path.join(STATE, "logs", "%s.%s.result.json" % (item_id, stamp))
    if res is not None and new != "done":
        source_record_path = archive_path if os.path.exists(result_path) else log_path
        existing = load_record(DEFERRED, item_id)
        if synthetic_failure and existing:
            record = merge_failure(existing, issue, source_record_path, row_statuses(rows))
        else:
            record = build_record(res, item_id, source_record_path, set(rows), row_statuses(rows))
        save_record(DEFERRED, record)
        if record["pending_dependencies"]:
            new = "blocked"
            summary = "%s; waiting on %s" % (summary, ",".join(record["pending_dependencies"]))
    elif new == "done":
        deferred_path = os.path.join(DEFERRED, item_id + ".json")
        if os.path.exists(deferred_path):
            os.unlink(deferred_path)
    stampnote = "%s %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), status, summary)
    r["status"] = new
    r["notes"] = (r["notes"] + " / " + stampnote).strip(" /") if r["notes"] else stampnote
    if new != "done":
        r["owner"] = ""
    refresh_deferred_rows(rows)
    save_rows(lines, rows)
    # keep a copy of the result next to the log
    if os.path.exists(result_path):
        os.replace(result_path, archive_path)
    print(new)


cmds = {"status": cmd_status, "list": cmd_list, "show": cmd_show, "dependencies": cmd_dependencies,
        "select": cmd_select, "set": cmd_set, "get": cmd_get, "prompt": cmd_prompt, "ingest": cmd_ingest}
cmds[sys.argv[1]](sys.argv[2:])
PY
}

# ---------------------------------------------------------------------------
# Integration lock used by agents (and by humans) - one holder at a time
# ---------------------------------------------------------------------------
cmd_lock() {
    local op="${1:-status}" id="${2:-manual}" lockd="$STATE/locks/integration.lock.d"
    case "$op" in
        acquire)
            local waited=0 max="${CA_LOCK_TIMEOUT_SEC:-7200}"
            local stale="${CA_LOCK_STALE_SEC:-10800}"
            while ! mkdir "$lockd" 2>/dev/null; do
                # the holder is usually an agent whose shell has already exited, so staleness is age-based only
                local since; since="$(cat "$lockd/since" 2>/dev/null || echo 0)"
                if [ $(( $(date +%s) - since )) -gt "$stale" ]; then
                    note "breaking integration lock held by $(cat "$lockd/owner" 2>/dev/null) for more than ${stale}s"
                    rm -rf "$lockd"; continue
                fi
                [ "$waited" -ge "$max" ] && die "integration lock timeout (held by $(cat "$lockd/owner" 2>/dev/null))"
                sleep 5; waited=$((waited + 5))
            done
            echo "$id" > "$lockd/owner"; date +%s > "$lockd/since"
            note "integration lock acquired by $id" ;;
        release)
            if [ -d "$lockd" ]; then
                local owner; owner="$(cat "$lockd/owner" 2>/dev/null)"
                if [ "$owner" != "$id" ] && [ "${CA_FORCE:-0}" != 1 ]; then
                    die "lock held by $owner, not $id (CA_FORCE=1 to override)"
                fi
                rm -rf "$lockd"; note "integration lock released by $id"
            else
                note "integration lock was not held"
            fi ;;
        status)
            if [ -d "$lockd" ]; then
                echo "held by $(cat "$lockd/owner") since $(date -r "$(cat "$lockd/since")" 2>/dev/null) (age $(( $(date +%s) - $(cat "$lockd/since") ))s)"
            else echo "free"; fi ;;
        *) die "lock acquire|release|status ID" ;;
    esac
}

# ---------------------------------------------------------------------------
# Spawning one agent
# ---------------------------------------------------------------------------
spawn_agent() {
    local id="$1" stamp="$2" dry="$3"
    local prompt="$STATE/prompts/$id.$stamp.md"
    local sid; sid="$(uuidgen | tr '[:upper:]' '[:lower:]')"
    case "$CLI" in codex-yolo|agy) sid="" ;; esac
    ca_py prompt "$id" > "$prompt" || die "prompt render failed for $id"
    rm -f "$STATE/results/$id.json"
    local checkpoint="$STATE/paused/$id.$stamp.json"
    "$PYTHON" - "$checkpoint" "$ROOT" "$id" "$stamp" "$sid" "$prompt" "$TIMEOUT_MIN" \
        "$CLI" "$CLI_BIN" "$MODEL" "$MODEL_EXPLICIT" "${CA_EFFORT:-}" "${CA_MAX_BUDGET_USD:-}" <<'PYCHECKPOINT'
import json, sys
path, root, item, stamp, sid, prompt, timeout, provider, executable, model, model_explicit, effort, budget = sys.argv[1:14]
with open(path, 'w') as f:
    json.dump(dict(root=root, id=item, stamp=stamp, sid=sid, prompt=prompt,
                   timeout=int(timeout), provider=provider, executable=executable,
                   model=model, model_explicit=model_explicit == "1", effort=effort,
                   max_budget_usd=budget), f, indent=2)
PYCHECKPOINT
    if [ "$dry" = 1 ]; then
        "$PYTHON" "$ROOT/tools/continue_analysis_session.py" --describe "$checkpoint"
        rm -f "$checkpoint"
        return 0
    fi
    local identity="$CLI${MODEL:+ model=$MODEL} session=$sid run=$stamp"
    md_lock; ca_py set "$id" in-progress "$identity" "started $(date '+%Y-%m-%d %H:%M')" --append >/dev/null; md_unlock
    launch_checkpoint "$id" "$stamp" "$sid" "$checkpoint"
}

launch_checkpoint() {
    local id="$1" stamp="$2" sid="$3" checkpoint="$4"
    rm -f "$STATE/running/$id.$stamp.exit"
    (
        "$PYTHON" "$ROOT/tools/continue_analysis_session.py" "$checkpoint" &
        local worker=$!
        trap 'kill -TERM "$worker" 2>/dev/null; wait "$worker"; exit 130' INT TERM
        wait "$worker"
        echo $? > "$STATE/running/$id.$stamp.exit"
    ) &
    local pid=$!
    echo "$pid" > "$STATE/running/$id.$stamp.pid"
    echo "$sid" > "$STATE/running/$id.$stamp.session"
    note "supervising $id -> pid $pid session $sid"
}

cmd_resume_paused() {
    local checkpoints=("$STATE"/paused/*.json)
    local f id stamp sid pidfile pid
    for f in "${checkpoints[@]}"; do
        [ -f "$f" ] || continue
        read -r id stamp sid < <("$PYTHON" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["id"],d["stamp"],d["sid"])' "$f")
        pidfile="$STATE/running/$id.$stamp.pid"
        pid="$(cat "$pidfile" 2>/dev/null || true)"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            note "$id already supervised by pid $pid; skipping"
            continue
        fi
        local provider; provider="$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("provider", "claude-yolo"))' "$f")"
        md_lock; ca_py set "$id" in-progress "$provider session=$sid run=$stamp" "recovering saved session" --append >/dev/null; md_unlock
        launch_checkpoint "$id" "$stamp" "$sid" "$f"
    done
    wait
    for f in "${checkpoints[@]}"; do
        local base; base="$(basename "$f" .json)"
        [ -f "$STATE/running/$base.exit" ] || continue
        wait_and_ingest "${base#*.}" "${base%%.*}"
    done
}

wait_and_ingest() {
    local stamp="$1"; shift
    local ids=("$@")
    wait
    for id in "${ids[@]}"; do
        local exit_code; exit_code="$(cat "$STATE/running/$id.$stamp.exit" 2>/dev/null || echo 1)"
        md_lock
        local final; final="$(ca_py ingest "$id" "$stamp" "$exit_code")"
        md_unlock
        note "$id finished: exit $exit_code -> $final  (see $STATE/logs/$id.$stamp.json)"
        rm -f "$STATE/running/$id.$stamp.pid" "$STATE/running/$id.$stamp.exit" "$STATE/running/$id.$stamp.session"
    done
}

cmd_run() {
    local n=1 loop=0 dry=0 max_batches=0
    local -a sel=()
    while [ $# -gt 0 ]; do
        case "$1" in
            -n|--agents) n="$2"; shift 2 ;;
            --loop) loop=1; shift ;;
            --max-batches) max_batches="$2"; shift 2 ;;
            --dry-run) dry=1; shift ;;
            --cli)
                CLI="$2"
                [ "$CLI_BIN_EXPLICIT" = 1 ] || CLI_BIN=""
                [ "$MODEL_EXPLICIT" = 1 ] || MODEL=""
                shift 2 ;;
            --cli-bin) CLI_BIN="$2"; CLI_BIN_EXPLICIT=1; shift 2 ;;
            --model) MODEL="$2"; MODEL_EXPLICIT=1; shift 2 ;;
            --component|--kind|--ids|--priority) sel+=("$1" "$2"); shift 2 ;;
            --retry-failed|--ignore-deps|--no-spread) sel+=("$1"); shift ;;
            *) die "unknown run option $1" ;;
        esac
    done
    configure_cli
    [[ "$n" =~ ^[1-9][0-9]*$ ]] || die "-n must be a positive integer"
    [ "$dry" = 1 ] || command -v "$CLI_BIN" >/dev/null 2>&1 || die "$CLI_BIN not found (set CA_CLI_BIN)"
    local batch=0
    while :; do
        batch=$((batch + 1))
        local stamp; stamp="$(date +%Y%m%d-%H%M%S)"
        md_lock
        local ids; ids="$(ca_py select "$n" ${sel[@]+"${sel[@]}"})"
        md_unlock
        if [ -z "$ids" ]; then
            note "no claimable items (todo with satisfied dependencies) match; nothing to do"
            break
        fi
        local -a arr=()
        while IFS= read -r line; do [ -n "$line" ] && arr+=("$line"); done <<< "$ids"
        local display_model="${MODEL:-provider default}"
        note "batch $batch: ${#arr[@]} item(s): ${arr[*]} (cli $CLI, model $display_model, ${dry:+dry-run=}$dry)"
        local first=1
        for id in "${arr[@]}"; do
            [ "$first" = 1 ] || { [ "$dry" = 1 ] || sleep "$STAGGER"; }
            first=0
            spawn_agent "$id" "$stamp" "$dry"
        done
        [ "$dry" = 1 ] && break
        wait_and_ingest "$stamp" "${arr[@]}"
        ca_py status
        [ "$loop" = 1 ] || break
        [ "$max_batches" != 0 ] && [ "$batch" -ge "$max_batches" ] && break
    done
}

cmd_reset_stale() {
    local to="todo"
    [ "${1:-}" = "--to" ] && to="$2"
    local any=0
    for pidf in "$STATE"/running/*.pid; do
        [ -e "$pidf" ] || continue
        local base; base="$(basename "$pidf" .pid)"; local id="${base%%.*}"
        if ! kill -0 "$(cat "$pidf")" 2>/dev/null; then
            md_lock; ca_py set "$id" "$to" "" "agent process gone; reset by reset-stale" --append; md_unlock
            rm -f "$pidf" "${pidf%.pid}.exit" "${pidf%.pid}.session"; any=1
        fi
    done
    # rows marked in-progress with no running record at all
    for id in $(ca_py list --status in-progress | awk '{print $1}'); do
        if ! ls "$STATE"/running/"$id".*.pid >/dev/null 2>&1; then
            md_lock; ca_py set "$id" "$to" "" "no running record; reset by reset-stale" --append; md_unlock; any=1
        fi
    done
    [ "$any" = 1 ] || note "nothing stale"
}


# ---------------------------------------------------------------------------
# regenerate: rebuild remaining-work.md/json from the live production flash plan
# ---------------------------------------------------------------------------
cmd_regenerate() {
    local plan="$ROOT/g2/build/source/flash-plan.json" db="$ROOT/g2/build/transparent/function-db.json"
    if [ ! -f "$plan" ]; then
        die "$plan is missing: run 'make -C g2 source' (under the integration lock) first"
    fi
    if [ ! -f "$db" ]; then
        note "function database missing; running 'make -C g2 transparent-db'"
        (cd "$ROOT/g2" && make -s transparent-db) || die "make transparent-db failed"
    fi
    md_lock
    CA_ROOT="$ROOT" CA_KEEP_STATUS="${CA_KEEP_STATUS:-1}" "$PYTHON" - <<'PYGEN'
#!/usr/bin/env python3
"""Generate remaining-work.md + remaining-work.json for the G2 source-only goal.

Inputs (all read-only, from g2/):
  build/source/flash-plan.json                 production layout; official_blob regions are the retained set
  build/transparent/function-db.json           Apollo function database (make transparent-db)
  docs/research/gx8002-source-candidate-build.json   codec byte ownership (retained ranges)
  tools/manifests/em9305-final-source-readiness.tsv  EM9305 residual decisions
  tools/manifests/em9305-controller-cluster-map.tsv  EM9305 named clusters
"""
import bisect
import re
import csv
import datetime
import json
import os
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(os.environ["CA_ROOT"]).resolve()
G2 = ROOT / "g2"
OUT_MD = ROOT / "remaining-work.md"
OUT_JSON = ROOT / "remaining-work.json"

plan = json.load(open(G2 / "build/source/flash-plan.json"))
db = json.load(open(G2 / "build/transparent/function-db.json"))["functions"]
db.sort(key=lambda f: f["start"])
starts = [f["start"] for f in db]
codec_own = json.load(open(G2 / "docs/research/gx8002-source-candidate-build.json"))

UPSTREAM_BUCKETS = {
    "lvgl", "cordio", "ambiqsuite", "littlefs", "nanopb", "cmsis-freertos", "tlsf",
    "cjson", "iar-dlib", "tinyframe", "ambiqsuite-ancc", "liblc3", "easylogger", "lz4",
    "freetype",
}

items = []


def hx(v):
    return "0x%08X" % v


def funcs_in(a, b):
    i = bisect.bisect_left(starts, a)
    out = []
    while i < len(db) and db[i]["start"] < b:
        out.append(db[i])
        i += 1
    return out


def fn_record(f):
    fam = f.get("families") or []
    return {
        "addr": hx(f["start"]),
        "end": hx(f["end"]),
        "size": f["size"],
        "name": f.get("name") or f.get("ghidra_name"),
        "ghidra_name": f.get("ghidra_name"),
        "tier": f.get("tier"),
        "bucket": f.get("bucket") or "no-census-row",
        "families": fam,
        "census_detail": (f.get("census_detail") or "")[:120],
    }


def add(item):
    item.setdefault("status", "todo")
    item.setdefault("owner", "")
    item.setdefault("notes", "")
    item.setdefault("depends", [])
    items.append(item)
    return item


# --------------------------------------------------------------------------
# Apollo main: code items (AM) and data items (AD)
# --------------------------------------------------------------------------
am_regions = sorted(
    (r for r in plan["flash_regions"] if r["component"] == "apollo_main" and r["address_status"] == "official_blob"),
    key=lambda r: r["target_address"],
)
CODE_BYTES_TARGET = 10240
CODE_FUNCS_TARGET = 32
CODE_GAP_BREAK = 0x10000
DATA_WINDOW = 0x20000
DATA_CHUNK = 131072
# flat list of retained functions with their region
flat = []
for r in am_regions:
    a, b = r["target_address"], r["end_exclusive"]
    for f in funcs_in(a, b):
        flat.append((f, r, min(f["end"], b) - f["start"]))
am_n = 0
chunk, cbytes = [], 0
chunks = []
for f, r, sz in flat:
    if chunk and (cbytes + sz > CODE_BYTES_TARGET or len(chunk) >= CODE_FUNCS_TARGET
                  or f["start"] - chunk[-1][0]["end"] > CODE_GAP_BREAK):
        chunks.append(chunk)
        chunk, cbytes = [], 0
    chunk.append((f, r, sz))
    cbytes += sz
if chunk:
    chunks.append(chunk)
merged_chunks = []
for ch in chunks:
    if merged_chunks and sum(x[2] for x in merged_chunks[-1]) < 1024:
        merged_chunks[-1].extend(ch)
    else:
        merged_chunks.append(ch)
chunks = merged_chunks
for ch in chunks:
    am_n += 1
    s = ch[0][0]["start"]
    e = min(ch[-1][0]["end"], ch[-1][1]["end_exclusive"])
    fs = [x[0] for x in ch]
    bk = Counter((f.get("bucket") or "no-census-row") for f in fs)
    tiers = Counter(f.get("tier") for f in fs)
    up_bytes = sum(f["size"] for f in fs if (f.get("bucket") in UPSTREAM_BUCKETS))
    fp_bytes = sum(f["size"] for f in fs if f.get("bucket") == "first-party" or f.get("tier") == "attributed")
    tot = sum(f["size"] for f in fs) or 1
    if up_bytes / tot >= 0.5:
        pri, route = "P1", "identified-upstream"
    elif fp_bytes / tot >= 0.5:
        pri, route = "P2", "clean-room-c"
    else:
        pri, route = "P3", "investigate-then-c"
    named = [f.get("name") for f in fs if f.get("name") and not str(f.get("name")).startswith("FUN_")]
    targets = ", ".join(named[:5]) if named else ", ".join(f.get("ghidra_name") for f in fs[:4])
    regs = OrderedDict()
    for f, r, sz in ch:
        regs[r["target_address_hex"]] = {"start": r["target_address_hex"], "end": r["end_exclusive_hex"], "size": r["size"], "description": r["function"], "artifact": r["artifact"]}
    add({
        "id": "AM-%03d" % am_n,
        "component": "apollo_main",
        "section": "Apollo main application - retained executable code",
        "priority": pri,
        "kind": "code",
        "route": route,
        "arch": "Cortex-M55 Thumb-2 (Apollo510B), run base 0x00438000, OTA preamble 0x20 bytes",
        "start": hx(s), "end": hx(e), "bytes": e - s,
        "function_count": len(fs),
        "function_bytes": sum(x[2] for x in ch),
        "regions": list(regs.values()),
        "buckets": dict(bk), "tiers": dict(tiers),
        "targets": targets,
        "functions": [fn_record(f) for f in fs],
        "summary": "%d retained functions (%d bytes) in %s..%s; buckets %s" % (len(fs), sum(x[2] for x in ch), hx(s), hx(e), ", ".join("%s:%d" % kv for kv in bk.most_common(3))),
    })

# data: per region, non-function bytes; big pure-data regions chunked, small ones swept per 128 KiB window
ad_n = 0
window_pool = OrderedDict()
for r in am_regions:
    a, b = r["target_address"], r["end_exclusive"]
    fs = funcs_in(a, b)
    fbytes = sum(min(f["end"], b) - f["start"] for f in fs)
    data_bytes = r["size"] - fbytes
    if data_bytes <= 0:
        continue
    if data_bytes >= 8192:
        n = max(1, (r["size"] + DATA_CHUNK - 1) // DATA_CHUNK)
        for k in range(n):
            cs = a + k * DATA_CHUNK
            ce = min(b, cs + DATA_CHUNK)
            ad_n += 1
            add({
                "id": "AD-%03d" % ad_n,
                "component": "apollo_main",
                "section": "Apollo main application - retained data, tables, and assets",
                "priority": "P3",
                "kind": "data",
                "route": "reconstruct-data",
                "arch": "Apollo510B MRAM data (%d recovered functions in the parent region are covered by AM items)" % len(fs),
                "start": hx(cs), "end": hx(ce), "bytes": ce - cs,
                "function_count": 0, "function_bytes": 0,
                "regions": [{"start": hx(a), "end": hx(b), "size": r["size"], "description": r["function"], "artifact": r["artifact"]}],
                "targets": "non-code region%s" % (" part %d/%d" % (k + 1, n) if n > 1 else ""),
                "functions": [],
                "summary": "%d bytes of retained non-code data%s" % (ce - cs, " (part %d/%d of region %s..%s)" % (k + 1, n, hx(a), hx(b)) if n > 1 else ""),
            })
    else:
        w = a // DATA_WINDOW
        window_pool.setdefault(w, []).append((r, len(fs), data_bytes))
merged = []
for w, lst in window_pool.items():
    if merged and sum(x[2] for x in merged[-1]) < 2048:
        merged[-1].extend(lst)
    else:
        merged.append(list(lst))
for lst in merged:
    ad_n += 1
    ws, we = lst[0][0]["target_address"], lst[-1][0]["end_exclusive"]
    tot = sum(x[2] for x in lst)
    add({
        "id": "AD-%03d" % ad_n,
        "component": "apollo_main",
        "section": "Apollo main application - retained data, tables, and assets",
        "priority": "P3",
        "kind": "data-sweep",
        "route": "reconstruct-data",
        "arch": "Apollo510B MRAM literal pools, tables, strings, and small data islands",
        "start": hx(ws), "end": hx(we), "bytes": tot,
        "function_count": 0, "function_bytes": 0,
        "regions": [{"start": r["target_address_hex"], "end": r["end_exclusive_hex"], "size": r["size"], "non_function_bytes": d, "functions_in_region": n, "description": r["function"], "artifact": r["artifact"]} for r, n, d in lst],
        "targets": "%d non-code bytes across %d official regions (literal pools/tables/strings)" % (tot, len(lst)),
        "functions": [],
        "summary": "Sweep of %d retained non-function bytes in %d official regions within %s..%s" % (tot, len(lst), hx(ws), hx(we)),
    })

# --------------------------------------------------------------------------
# Apollo bootloader (BL)
# --------------------------------------------------------------------------
bl_regions = sorted(
    (r for r in plan["flash_regions"] if r["component"] == "apollo_bootloader" and r["address_status"] == "official_blob"),
    key=lambda r: r["target_address"],
)
bl_n = 0
group = []
gbytes = 0


def flush_bl(group):
    global bl_n
    if not group:
        return
    bl_n += 1
    s, e = group[0]["target_address"], group[-1]["end_exclusive"]
    tot = sum(r["size"] for r in group)
    desc = "; ".join(sorted({r["function"][:110] for r in group}))[:600]
    add({
        "id": "BL-%03d" % bl_n,
        "component": "apollo_bootloader",
        "section": "Apollo bootloader - retained bytes",
        "priority": "P2",
        "kind": "code-and-data",
        "route": "clean-room-c-or-ambiqsuite",
        "arch": "Cortex-M55 Thumb-2 bootloader, run base 0x00410000 (file offset 0)",
        "start": hx(s), "end": hx(e), "bytes": tot,
        "function_count": None, "function_bytes": None,
        "regions": [{"start": r["target_address_hex"], "end": r["end_exclusive_hex"], "size": r["size"], "description": r["function"]} for r in group],
        "targets": desc[:160],
        "functions": [],
        "summary": "%d retained bootloader bytes across %d official regions in %s..%s" % (tot, len(group), hx(s), hx(e)),
    })


for r in bl_regions:
    if group and gbytes >= 1024 and (gbytes + r["size"] > 6144 or r["size"] >= 6144):
        flush_bl(group)
        group, gbytes = [], 0
    group.append(r)
    gbytes += r["size"]
flush_bl(group)

# --------------------------------------------------------------------------
# EM9305 (EM)
# --------------------------------------------------------------------------
em_regions = sorted(
    (r for r in plan["flash_regions"] if r["component"] == "ble_em9305" and r["address_status"] == "official_blob"),
    key=lambda r: r["target_address"],
)
readiness = []
with open(G2 / "tools/manifests/em9305-final-source-readiness.tsv") as h:
    for row in csv.DictReader((l for l in h if not l.startswith("#")), delimiter="\t"):
        readiness.append(row)
clusters = []
with open(G2 / "tools/manifests/em9305-controller-cluster-map.tsv") as h:
    for row in csv.DictReader(h, delimiter="\t"):
        clusters.append(row)
em_n = 0
EM_CHUNK = 8192
# split big regions into <= 8 KiB windows, then group consecutive small windows into items
em_windows = []
for r in em_regions:
    a, b = r["target_address"], r["end_exclusive"]
    n = max(1, (r["size"] + EM_CHUNK - 1) // EM_CHUNK)
    for k in range(n):
        cs = a + k * EM_CHUNK
        ce = min(b, cs + EM_CHUNK)
        em_windows.append((cs, ce, r, k + 1, n))
em_groups = []
group, gbytes = [], 0
for w in em_windows:
    cs, ce = w[0], w[1]
    if group and gbytes >= 1024 and (gbytes + (ce - cs) > EM_CHUNK or (ce - cs) >= EM_CHUNK):
        em_groups.append(group)
        group, gbytes = [], 0
    group.append(w)
    gbytes += ce - cs
if group:
    em_groups.append(group)
for grp in em_groups:
    cs, ce = grp[0][0], grp[-1][1]
    tot = sum(w[1] - w[0] for w in grp)
    em_n += 1
    rows = [x for x in readiness if int(x["start"], 16) < ce and int(x["end"], 16) > cs]
    cl = [x for x in clusters if int(x["start"], 16) < ce and int(x["end"], 16) > cs]
    dec = Counter(x["decision"] for x in rows)
    kind = "record-metadata" if ce <= 0x00302400 else "code-and-data"
    pri = "P2" if any(x["readiness"] == "concrete_source_available" or x["decision"].endswith("boundary") for x in rows) else ("P3" if kind == "code-and-data" else "P2")
    regs = OrderedDict()
    for w in grp:
        r = w[2]
        regs[r["target_address_hex"]] = {"start": r["target_address_hex"], "end": r["end_exclusive_hex"], "size": r["size"], "description": r["function"]}
    add({
        "id": "EM-%03d" % em_n,
        "component": "ble_em9305",
        "section": "EM9305 Bluetooth controller - retained application bytes",
        "priority": pri,
        "kind": kind,
        "route": "clean-room-c-arcv2" if kind == "code-and-data" else "generate-record-metadata",
        "arch": "ARCv2 EM7D (Synopsys MetaWare/ARC GCC -mcpu=em), records at 0x00300000/0x00300400/0x00302000/0x00302400",
        "start": hx(cs), "end": hx(ce), "bytes": tot,
        "function_count": None, "function_bytes": None,
        "regions": list(regs.values()),
        "windows": [{"start": hx(w[0]), "end": hx(w[1]), "part": "%d/%d" % (w[3], w[4])} for w in grp],
        "readiness_rows": [{"start": x["start"], "end": x["end"], "size": int(x["size"]), "readiness": x["readiness"], "decision": x["decision"]} for x in rows],
        "clusters": [{"start": x["start"], "end": x["end"], "name": x["name"], "object": x["object"], "status": x["status"]} for x in cl],
        "targets": ", ".join(sorted({x["name"] for x in cl})[:5]) or ", ".join("%s:%d" % kv for kv in dec.most_common(3)) or ("record table / FHDR metadata" if kind == "record-metadata" else "unnamed retained controller bytes"),
        "functions": [],
        "depends": ["XC-003"] if kind == "code-and-data" else [],
        "summary": "%d retained EM9305 bytes in %d official region%s within %s..%s" % (tot, len(regs), "" if len(regs) == 1 else "s", hx(cs), hx(ce)),
    })

# --------------------------------------------------------------------------
# GX8002 codec (CD)
# --------------------------------------------------------------------------
MAIN = 0x958C
CODEC_LAYOUT = [
    # (pkg_start, pkg_end, label, runtime_base, seg_base, kind)
    (0x0050, 0x2850, "UART boot stage 1 (IRAM)", 0x10000000, 0x0050, "code"),
    (0x2850, MAIN, "UART boot stage 2 (IRAM)", 0x10002800, 0x2850, "code"),
    (MAIN + 0x0000, MAIN + 0x3000, "image A BINH header + stage-1 block (flash 0x0 -> IRAM 0x10000000, vectors at block+0x18)", None, None, "code"),
    (MAIN + 0x3000, MAIN + 0x3004, "image A stage-2 XIP length word", None, None, "metadata"),
    (MAIN + 0x3004, MAIN + 0xBE88, "image A stage-2 XIP text (executes in place; public XIP base 0x10200000 + flash offset)", 0x10200000, MAIN - 0x0000, "code"),
    (MAIN + 0xBE88, MAIN + 0xEF6C, "image A SRAM text (IRAM 0x10023400, entry 0x10023500)", 0x10023400, MAIN + 0xBE88, "code"),
    (MAIN + 0xEF6C, MAIN + 0xEF70, "image A SRAM pad word", None, None, "metadata"),
    (MAIN + 0xEF70, MAIN + 0xF804, "image A SRAM data (0x100264E8)", 0x100264E8, MAIN + 0xEF70, "data"),
    (MAIN + 0xF804, MAIN + 0x11BD0, "image A KWS NPU command stream (DRAM 0x20003304)", 0x20003304, MAIN + 0xF804, "accelerator-program"),
    (MAIN + 0x11BD0, MAIN + 0x2F3B0, "image A KWS model weights (DRAM 0x200056D0)", 0x200056D0, MAIN + 0x11BD0, "model"),
    (MAIN + 0x2F3B0, MAIN + 0x323B4, "image B BINH header + stage-1 block", None, None, "code"),
    (MAIN + 0x323B4, MAIN + 0x458D0, "image B SRAM text (IRAM 0x10003000, entry 0x10003100)", 0x10003000, MAIN + 0x323B4, "code"),
    (MAIN + 0x458D0, MAIN + 0x46440, "image B SRAM data (0x1001651C)", 0x1001651C, MAIN + 0x458D0, "data"),
]


def codec_region(off):
    for s, e, label, rb, sb, kind in CODEC_LAYOUT:
        if s <= off < e:
            return s, e, label, rb, sb, kind
    return None


ret = sorted((o for o in codec_own["ownership"] if o["kind"] == "retained_stock"), key=lambda o: o["offset"])
# split every retained range at region boundaries, then group consecutive pieces of one region into items
pieces = []
for o in ret:
    s, e = o["offset"], o["offset"] + o["size"]
    cur = s
    while cur < e:
        reg = codec_region(cur) or (cur, e, "unmapped package offset", None, None, "unknown")
        rs, re_, label, rb, sb, kind = reg
        ce = min(e, re_)
        pieces.append((cur, ce, reg))
        cur = ce
cd_n = 0
CD_CODE_TARGET = 8192
CD_DATA_TARGET = 32768
group, gbytes = [], 0


def flush_cd(group):
    global cd_n
    if not group:
        return
    cd_n += 1
    # dominant piece (largest) defines label/kind; each sub-range keeps its own region mapping
    dom = max(group, key=lambda x: x[1] - x[0])[2]
    rs, re_, label, rb, sb, kind = dom
    subs = []
    for cs, ce, reg in group:
        _, _, plabel, prb, psb, pkind = reg
        sub = {"package_start": "0x%06X" % cs, "package_end": "0x%06X" % ce, "size": ce - cs, "region": plabel, "kind": pkind}
        if prb is not None and psb is not None:
            sub["runtime_start"] = hx(prb + (cs - psb))
            sub["runtime_end"] = hx(prb + (ce - psb))
        subs.append(sub)
    tot = sum(x["size"] for x in subs)
    first, last = subs[0], subs[-1]
    rt = ("runtime_start" in first) and ("runtime_end" in last)
    pri = "P1" if kind == "code" else ("P2" if kind == "data" else "P3")
    add({
        "id": "CD-%03d" % cd_n,
        "component": "codec",
        "section": "GX8002 codec/DSP - retained stock bytes (package offsets; runtime addresses where resolved)",
        "priority": pri,
        "kind": kind,
        "route": "csky-c-from-grus-sdk-and-decompilation" if kind == "code" else ("source-authored-model-or-generator" if kind in ("model", "accelerator-program") else "reconstruct-data"),
        "arch": "C-SKY CK804EF (csky-unknown-elf-gcc in g2/build/csky-macos/install/bin)",
        "package_start": first["package_start"], "package_end": last["package_end"],
        "start": first["runtime_start"] if rt else first["package_start"],
        "end": last["runtime_end"] if rt else last["package_end"],
        "runtime_resolved": rt,
        "bytes": tot,
        "function_count": None, "function_bytes": None,
        "region": {"label": label, "package_start": "0x%06X" % rs, "package_end": "0x%06X" % re_},
        "subranges": subs,
        "targets": "%s (%d retained span%s)" % (label, len(subs), "" if len(subs) == 1 else "s"),
        "functions": [],
        "summary": "%d retained codec bytes in %d span%s at package %s..%s (%s)" % (tot, len(subs), "" if len(subs) == 1 else "s", first["package_start"], last["package_end"], label),
    })


for cs, ce, reg in pieces:
    kind = reg[5]
    target = CD_CODE_TARGET if kind == "code" else CD_DATA_TARGET
    new_label = group and reg[2] != group[0][2][2]
    tiny = (ce - cs) < 256 or gbytes < 256          # tiny pieces ride along with a neighbour
    if group and ((new_label and not tiny) or gbytes + (ce - cs) > target):
        flush_cd(group)
        group, gbytes = [], 0
    while ce - cs > target:
        flush_cd(group + [(cs, cs + target, reg)])
        group, gbytes = [], 0
        cs += target
    group.append((cs, ce, reg))
    gbytes += ce - cs
flush_cd(group)

# --------------------------------------------------------------------------
# Touch (TC) and case (CS)
# --------------------------------------------------------------------------
add({"id": "TC-001", "component": "touch", "section": "PSoC 4000T touch controller", "priority": "P1", "kind": "routing",
     "route": "route-candidate-source-image", "arch": "Cortex-M0+ (armv6m; /opt/homebrew/opt/llvm/bin/clang)",
     "start": "0x00000000", "end": "0x00008680", "bytes": 34432, "function_count": 178, "function_bytes": 14510,
     "targets": "components/touch/source_image -> production provider in a source manifest profile",
     "functions": [], "summary": "Production-route the complete 31-TU touch source image (15,560 B raw) and make every resident-ABI assumption an explicit, documented configuration instead of a hardware blocker"})
add({"id": "TC-002", "component": "touch", "section": "PSoC 4000T touch controller", "priority": "P2", "kind": "data-and-code-accounting",
     "route": "reconstruct-remainder", "arch": "Cortex-M0+", "start": "0x00000000", "end": "0x00008680", "bytes": 19442,
     "function_count": None, "function_bytes": None,
     "targets": "19,442 typed-retained touch bytes not represented by the 15,560-byte source image",
     "functions": [], "summary": "Account for and reconstruct (or source-author) the shipped touch image bytes that the candidate source image does not produce: tables, descriptors, resident-dependent stubs, and padding"})
add({"id": "TC-003", "component": "touch", "section": "PSoC 4000T touch controller", "priority": "P3", "kind": "blocked-proprietary",
     "route": "document-boundary", "arch": "Cortex-M0+", "start": "0x00008680", "end": "0x00010000", "bytes": 0,
     "function_count": None, "function_bytes": None, "status": "blocked",
     "targets": "resident flash >= 0x8680 (dispatch tables, HAL descriptors, resident DFU engine, boot vectors) is not shipped in any blob",
     "functions": [], "summary": "Not shipped by the OTA package; the source-only build must not depend on it. Keep the boundary documented; re-open only if a lawful source or readout appears"})
add({"id": "CS-001", "component": "case", "section": "STM32G0 charging case", "priority": "P1", "kind": "routing",
     "route": "route-candidate-source-image", "arch": "Cortex-M0+ (armv6m; /opt/homebrew/opt/llvm/bin/clang)",
     "start": "0x08000000", "end": "0x0800D9C8", "bytes": 55752, "function_count": 222, "function_bytes": 14886,
     "targets": "components/case/source_image -> production provider in a source manifest profile",
     "functions": [], "summary": "Production-route the complete 8-TU case source image (18,916 B raw) and make board-routing assumptions (vectors, GPIO/timer bindings, bank swap) explicit configuration with documented defaults"})
add({"id": "CS-002", "component": "case", "section": "STM32G0 charging case", "priority": "P2", "kind": "data-and-code-accounting",
     "route": "reconstruct-remainder", "arch": "Cortex-M0+", "start": "0x08000000", "end": "0x0800D9C8", "bytes": 40866,
     "function_count": None, "function_bytes": None,
     "targets": "40,866 typed-retained case bytes not produced by the 18,916-byte source image",
     "functions": [], "summary": "Account for and reconstruct (or source-author) the shipped case image bytes beyond the candidate source image: data tables, strings, identity windows, fill; then make the source image the same size/layout or document the intentional divergence"})

# --------------------------------------------------------------------------
# Cross-cutting (XC)
# --------------------------------------------------------------------------
XC = [
    ("XC-001", "P1", "source-only manifest and package gate",
     "Create manifests/g2-2.2.6.10-source-only.json (extends core-source) selecting source_build providers for all six components, a `make source-only` target that builds and verifies the EVENOTA package on macOS, and a fail-closed `--require-source-only` gate that rejects any official_blob region, trap, copied byte array, or unreviewed decompilation. Until components finish, the gate must fail with an exact per-component byte report."),
    ("XC-002", "P1", "completion-readiness and transparent ledgers track progress",
     "Keep `make -C g2 completion-readiness` and `make -C g2 transparent-ledger` truthful as items land: refresh docs/reports/*/assessment-data.json via the tool's write path, keep docs/transparent-source-ledger.md regenerated, and make sure newly reviewed C is registered in tools/transparent/reviewed_sources.json so it supersedes decompilation in the transparent image."),
    ("XC-003", "P1", "macOS ARC (EM9305) toolchain",
     "components/em9305/source_overlay/build_overlay.py needs arc-linux-gnu-gcc (-mcpu=em); it is not installed on this Mac (the last build used a Red Hat cross GCC). Build or install a reproducible ARC GCC/binutils on macOS, pin its version and SHA-256 in the component's toolchain description, wire OPENCFW_ARC_* defaults, and prove the existing overlay rebuilds byte-identically. All EM-* items depend on this."),
    ("XC-004", "P2", "transparent-image envelope fitting",
     "1,938 recovered Apollo functions do not fit their stock envelope (80,160 bytes total overshoot, mostly literal-pool materialisation). Design and implement a reviewed placement strategy in tools/build_transparent_image.py / generate_transparent_source.py (shared literal pools, relocated bodies with entry redirects like the production overlay uses) so reviewed C is never trapped for size alone."),
    ("XC-005", "P2", "Apollo data/asset source representation",
     "Define the maintainable source representation for Apollo data regions (LVGL fonts and images, FreeType payloads, Cordio tables, protobuf descriptors, string pools): generator tooling that produces them from source assets (for example lv_font_conv / lv_img_conv inputs under a documented license) rather than byte arrays; AD-* items then use it."),
    ("XC-006", "P2", "codec model and NPU command source pipeline",
     "For CD items of kind model/accelerator-program (KWS weights 120,800 B; NPU command stream 9,164 B): recover the gxDNN/SNPU descriptor format already decoded in docs/research/gx8002-*.md, and provide a source-authored generator (model definition + quantisation + command emitter) or a functionally qualified replacement. Byte arrays of the stock payload do not count."),
    ("XC-007", "P2", "codec KWS parameter and data reconstruction",
     "Reconstruct image A/B SRAM data regions (initialised data, VAD curves, parameter tables) as source-authored C data with derivations, replacing generated_source_data copies where those are still stock-derived."),
    ("XC-008", "P3", "documentation re-pin sweep",
     "docs/source-coverage.md, docs/memory-map.md, docs/upstream-inventory.md and docs/linux-reproducible-build.md are SHA-256 pinned by tests. Periodically fold the per-item research audits into these records and re-pin them through the documented test path; per-item agents must not edit them."),
    ("XC-009", "P3", "bootloader Ghidra harvest",
     "There is no per-function decompilation corpus for the bootloader (only Apollo main, EM9305, and case). Produce research/corpus/apollo-bootloader/ghidra/decomp with tools/harvest_ghidra_decomp.py from the local Ghidra installation so BL-* items have named, bounded functions."),
]
for xid, pri, title, desc in XC:
    add({"id": xid, "component": "cross-cutting", "section": "Cross-cutting tooling, gates, and toolchains", "priority": pri,
         "kind": "tooling", "route": "tooling", "arch": "host tooling (macOS)", "start": "-", "end": "-", "bytes": 0,
         "function_count": None, "function_bytes": None, "targets": title, "functions": [], "summary": desc})

# --------------------------------------------------------------------------
# Emit JSON + Markdown
# --------------------------------------------------------------------------
today = datetime.date.today().isoformat()
meta = {
    "generated": today,
    "generator": "continue-analysis.sh regenerate; inputs: g2/build/source/flash-plan.json, g2/build/transparent/function-db.json, g2/docs/research/gx8002-source-candidate-build.json, EM9305 readiness/cluster manifests",
    "package_expected_sha256": plan.get("package_sha256"),
    "item_count": len(items),
}
json.dump({"meta": meta, "items": items}, open(OUT_JSON, "w"), indent=1)

order = OrderedDict()
for it in items:
    order.setdefault(it["section"], []).append(it)


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ").strip()


L = []
L.append("# G2 source-only firmware: remaining work")
L.append("")
L.append("Generated %s from the production flash plan (`g2/build/source/flash-plan.json`), the Apollo" % today)
L.append("function database (`make -C g2 transparent-db`), the codec ownership ledger, and the EM9305")
L.append("readiness ledgers. Machine-readable detail for every row (function lists, addresses, tiers,")
L.append("buckets, region descriptions) is in `remaining-work.json`; `continue-analysis.sh` reads both.")
L.append("")
L.append("**Goal (from `g2/docs/source-only-goal.md`):** every selected component builds from reviewed")
L.append("source and pinned upstream dependencies; required data, assets, model parameters, and")
L.append("accelerator programs have a maintainable source representation or a functionally qualified")
L.append("source-authored replacement; the original firmware is only an oracle and supplies no bytes.")
L.append("Typed provider interfaces, opaque bytes as C arrays, trap stubs, and merely compilable")
L.append("decompilation do **not** count. macOS is the build host; Linux support is not required.")
L.append("")
L.append("## How the status column is maintained")
L.append("")
L.append("`continue-analysis.sh` is the only writer of the `Status`, `Owner`, and `Notes` cells.")
L.append("Status values: `todo`, `in-progress`, `done`, `blocked`, `failed`. An item is `done` only")
L.append("when its bytes are produced from reviewed source that is production-routed (or, for data,")
L.append("from a source-authored representation), the narrow tests and the component build pass, and the")
L.append("research audit / progress entry is written. Retry a `failed` row with")
L.append("`./continue-analysis.sh run --retry-failed`. Manual overrides: `./continue-analysis.sh done|fail|block|release <ID>`.")
L.append("")
L.append("Priority: `P1` identified upstream source or routing work; `P2` first-party clean-room C;")
L.append("`P3` investigation-required code, data/assets, and long-tail tooling.")
L.append("")
L.append("## Summary")
L.append("")
L.append("| Component | Items | Release-blocking bytes | Notes |")
L.append("|---|---:|---:|---|")
comp_items = Counter(it["component"] for it in items)
comp_bytes = {"apollo_main": 3080790, "apollo_bootloader": 87985, "ble_em9305": 210584, "codec": 307615,
              "touch": 33952, "case": 55752, "cross-cutting": 0}
notes = {
    "apollo_main": "3,046,598 release-blocking bytes; 5,481 retained functions (1.0 MB) + ~2.0 MB data",
    "apollo_bootloader": "87,985 retained bytes in 151 official regions",
    "ble_em9305": "210,584 retained controller bytes; needs macOS ARC toolchain (XC-003)",
    "codec": "307,615 retained bytes incl. 129,964 B KWS model/NPU payload",
    "touch": "candidate source complete (178 fns) but not production-routed",
    "case": "candidate source complete (222 fns) but not production-routed",
    "cross-cutting": "gates, toolchains, generators",
}
for c in ("apollo_main", "apollo_bootloader", "ble_em9305", "codec", "touch", "case", "cross-cutting"):
    L.append("| %s | %d | %s | %s |" % (c, comp_items[c], format(comp_bytes[c], ","), notes[c]))
L.append("")
L.append("Total items: %d. Package under audit: EVENOTA `s200_v2.2.6.10`, expected SHA-256 `%s`." % (len(items), plan.get("package_sha256")))
L.append("")

INTROS = {
    "Apollo main application - retained executable code": [
        "Flash: Apollo510B MRAM, application at `0x00438000..0x00794324` (file offset = address - 0x437FE0).",
        "Evidence: `g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl` (decompilation per",
        "address), `g2/build/transparent/function-db.json` (names, tiers, buckets), 200+ function maps",
        "in `g2/tools/manifests/*-function-map.tsv`, and the per-family audits in `g2/docs/research/`.",
        "Admission path: reviewed C in `g2/components/apollo_main/core_overlay/` registered in",
        "`overlay.json` (relocated leaf + entry redirect / patch site), built by `make -C g2 core-component`,",
        "then `make -C g2 source` must place it with zero unresolved flash regions. Identified upstream",
        "families (LVGL, Cordio host, AmbiqSuite, littlefs, nanopb, CMSIS-FreeRTOS, TLSF, cJSON, TinyFrame,",
        "liblc3, EasyLogger, FreeType) must use the pinned vendored snapshot under `g2/components/shared/`",
        "with the recovered configuration, not a rewrite. Also register reviewed functions in",
        "`g2/tools/transparent/reviewed_sources.json` so the transparent image stops trapping them.",
    ],
    "Apollo main application - retained data, tables, and assets": [
        "Same flash as above. These regions have no recovered functions (or large non-code remainders).",
        "Identify each structure from its referencing code (LVGL image/font descriptors, FreeType payloads,",
        "Cordio/SMP tables, protobuf descriptors, string pools, peripheral descriptor tables) and give it",
        "a source representation per XC-005: generated from source assets or authored C data with a",
        "derivation. A byte array copied from the stock image does not close an item.",
    ],
    "Apollo bootloader - retained bytes": [
        "Flash: `0x00410000..0x00438000` (64 KiB secure bootloader at 0x00400000 is out of scope).",
        "Evidence: `g2/tools/manifests/g2-bootloader-*.tsv`, `g2/docs/research/g2-bootloader-*.md`,",
        "`g2/tools/analyze_g2_bootloader_*.py`, and the dual-image littlefs/EasyLogger/AmbiqSuite audits.",
        "Admission path: `g2/components/bootloader/core_overlay/` (in-place exact source or relocated",
        "leaves with entry redirects), `make -C g2 bootloader-component`, then `make -C g2 source`.",
        "No Ghidra harvest exists for the bootloader yet (XC-009); disassemble from the official blob.",
    ],
    "EM9305 Bluetooth controller - retained application bytes": [
        "Flash: controller records `0x00300000` (224 B), `0x00300400` (656 B), `0x00302000` (FHDR),",
        "application `0x00302400..0x00335BC8` (ARCv2 EM). Evidence: `g2/docs/research/em9305-*.md`,",
        "`g2/tools/manifests/em9305-*.tsv`, `g2/research/corpus/em9305/`, `g2/tools/analyze_em9305_*.py`.",
        "Most bytes are exact matches of proprietary Packetcraft controller / EM vendor objects for which",
        "no source is available; closing them means clean-room C reconstruction from decompilation and the",
        "public Packetcraft host conventions, admitted through `g2/components/em9305/source_overlay/`",
        "(tail branches + relocated C in the same sector). Every EM item depends on XC-003 (ARC toolchain).",
    ],
    "GX8002 codec/DSP - retained stock bytes (package offsets; runtime addresses where resolved)": [
        "Two-segment FWPK: UART boot stages load to IRAM `0x10000000`/`0x10002800`; the dual BINH main",
        "image is written to codec SPI-NOR offset 0 (image A stage-2 XIP text runs from the public XIP",
        "base `0x10200000`, SRAM text at `0x10023400`; image B SRAM text at `0x10003000`).",
        "`Flash range` below is the resolved runtime address where the section map gives one, otherwise",
        "the package offset; `remaining-work.json` always carries both. Evidence:",
        "`g2/docs/research/gx8002-*.md` (700+ audits), `gx8002-upstream-object-candidates.json` (68 named",
        "driver symbols from the NationalChip LVP KWS SDK), `gx8002-known-function-harvest.json`, and the",
        "C-SKY Ghidra processor. Admission path: C in `g2/components/shared/gx8002/`, a",
        "`tools/verify_gx8002_<x>.py` decoded-trace verifier, `tests/test_gx8002_<x>.py`, registration in",
        "`tools/build_gx8002_source_candidate.py`, `make -C g2 gx8002-source-candidate`, then",
        "`make -C g2 codec-source-experimental`. Public SDK C may be used under its MIT license; the SDK's",
        "prebuilt `.o`/`.a` files must never be linked.",
    ],
    "PSoC 4000T touch controller": [
        "Shipped image `0x00000000..0x00008680` (34,432 B raw in a 32-byte FWPK wrapper). The candidate",
        "source image (`g2/components/touch/source_image`, 31 TUs, 15,560 B) links with zero undefined",
        "symbols but is not production-routed because resident-ABI facts could not be confirmed on hardware.",
        "Software completion means routing it under explicit, documented assumptions and accounting for",
        "the bytes it does not produce.",
    ],
    "STM32G0 charging case": [
        "Shipped image logical `0x08000000..0x0800D9C8` (55,752 B). The candidate source image",
        "(`g2/components/case/source_image`, 8 TUs, 18,916 B) is link-complete but unrouted for the same",
        "hardware-evidence reason. Same completion rule as touch.",
    ],
    "Cross-cutting tooling, gates, and toolchains": [
        "Items that unblock whole components or define what counts as done.",
    ],
}

for sec, its in order.items():
    L.append("## %s" % sec)
    L.append("")
    for ln in INTROS.get(sec, []):
        L.append(ln)
    L.append("")
    L.append("| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |")
    L.append("|---|---|---|---|---:|---|---|---|---|")
    for it in its:
        rng = "%s..%s" % (it["start"], it["end"]) if it["start"] != "-" else "-"
        L.append("| %s | %s | %s | `%s` | %s | %s | %s | %s | %s |" % (
            it["id"], it["priority"], it["status"], rng, format(it.get("bytes") or 0, ","), cell(it["kind"]),
            cell(it["targets"])[:160].strip(), cell(it["owner"]), cell(it["notes"])))
    L.append("")

L.append("## Definition of done for a row")
L.append("")
L.append("1. Every executable byte in the range is produced by reviewed C (or reviewed assembly where the")
L.append("   ABI forces it) that is production-routed by the component build; entry addresses and caller")
L.append("   contracts are preserved or the change is a documented, tested divergence.")
L.append("2. Every data byte in the range has a source-authored representation or generator.")
L.append("3. Narrow tests pass, the component build passes, `make -C g2 source` (or the component's")
L.append("   candidate build) places the result with zero unresolved regions, and no trap/copied-array")
L.append("   remains for the range in the transparent ledger.")
L.append("4. A research audit (`g2/docs/research/<family>-<closure>.md`), a dated `g2/docs/progress.md`")
L.append("   entry, and a checkpoint in `g2/docs/source-only-goal.md` record what was proven and what remains.")
L.append("5. No hardware operation was performed; hardware qualification stays explicitly deferred.")
L.append("")
# carry over Status/Owner/Notes for rows whose ID and range are unchanged, then back up the old file
carry = {}
if OUT_MD.exists():
    import re as _re
    for ln in OUT_MD.read_text(encoding="utf-8").split("\n"):
        m = _re.match(r"^\| ((?:AM|AD|BL|EM|CD|TC|CS|XC)-\d{3}) \|", ln)
        if m:
            c = [x.strip() for x in ln.split("|")]
            if len(c) == 11:
                carry[(c[1], c[4])] = (c[3], c[8], c[9])
    bak = OUT_MD.with_name("remaining-work.%s.bak.md" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    bak.write_text(OUT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("backup of previous list:", bak)
if carry and os.environ.get("CA_KEEP_STATUS", "1") == "1":
    kept = 0
    for i, ln in enumerate(L):
        m = re.match(r"^\| ((?:AM|AD|BL|EM|CD|TC|CS|XC)-\d{3}) \|", ln)
        if not m:
            continue
        c = [x.strip() for x in ln.split("|")]
        key = (c[1], c[4])
        if key in carry and carry[key][0] != "todo":
            c[3], c[8], c[9] = carry[key]
            L[i] = "| " + " | ".join(c[1:10]) + " |"
            kept += 1
    print("carried over %d non-todo rows with identical ID and range" % kept)
OUT_MD.write_text("\n".join(L), encoding="utf-8")
print("items", len(items), "md bytes", OUT_MD.stat().st_size, "json bytes", OUT_JSON.stat().st_size)
print(Counter(i["component"] for i in items))
print(Counter(i["priority"] for i in items))

PYGEN
    local rc=$?
    md_unlock
    [ "$rc" = 0 ] || die "regeneration failed"
    note "regenerated $WORK_MD and $WORK_JSON"
}

usage() { sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; }

cmd="${1:-help}"; shift || true
case "$cmd" in
    run) cmd_run "$@" ;;
    resume-paused) cmd_resume_paused "$@" ;;
    dependencies) md_lock; ca_py dependencies "$@"; md_unlock ;;
    status) ca_py status ;;
    list) ca_py list "$@" ;;
    show) [ $# -ge 1 ] || die "show ID"; ca_py show "$1" ;;
    prompt) [ $# -ge 1 ] || die "prompt ID"; ca_py prompt "$1" ;;
    claim) [ $# -ge 1 ] || die "claim ID [note]"; md_lock; ca_py set "$1" in-progress "manual $(whoami)" "${2:-claimed manually}" --append; md_unlock ;;
    release) [ $# -ge 1 ] || die "release ID [note]"; md_lock; ca_py set "$1" todo "" "${2:-released}" --append; md_unlock ;;
    done) [ $# -ge 1 ] || die "done ID [note]"; md_lock; ca_py set "$1" done "manual $(whoami)" "${2:-marked done manually}" --append; md_unlock ;;
    fail) [ $# -ge 1 ] || die "fail ID [note]"; md_lock; ca_py set "$1" failed "" "${2:-marked failed manually}" --append; md_unlock ;;
    block) [ $# -ge 1 ] || die "block ID [note]"; md_lock; ca_py set "$1" blocked "" "${2:-blocked}" --append; md_unlock ;;
    lock) cmd_lock "$@" ;;
    reset-stale) cmd_reset_stale "$@" ;;
    regenerate) cmd_regenerate "$@" ;;
    logs) [ $# -ge 1 ] || die "logs ID"; ls -la "$STATE/logs/$1".* 2>/dev/null || note "no logs for $1"; for f in "$STATE/logs/$1".*.json; do [ -e "$f" ] && { echo "== $f"; "$PYTHON" -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("result") if isinstance(d,dict) and "result" in d else json.dumps(d,indent=1))' "$f" | tail -40; }; done ;;
    help|-h|--help) usage ;;
    *) die "unknown command $cmd (try help)" ;;
esac

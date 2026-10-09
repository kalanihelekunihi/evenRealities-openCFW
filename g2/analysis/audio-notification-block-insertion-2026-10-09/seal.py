from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[3]
TARGETS = [
    R / "g2/components/audio/notification_block_offline",
    R / "g2/analysis/audio-notification-block-insertion-2026-10-09",
    R / "g2/analysis/audio-codec-lifecycle-hal-composition-2026-10-09",
    R / "g2/analysis/audio-notification-block-wake-return-2026-10-09",
    R / "g2/components/audio/codec_uart_irq_offline",
    R / "g2/analysis/audio-codec-uart-irq-delivery-2026-10-09",
    R / "g2/analysis/source-ledger-audit-2026-10-09",
    R / "g2/components/audio/uart_instance_offline",
    R / "g2/analysis/audio-uart-instance-closure-2026-10-09",
    R / "g2/analysis/source-ledger-successor-2026-10-09",
    R / "g2/analysis/source-ledger-reconciliation-2026-10-09",
    R / "g2/analysis/audio-uart3-tx-irq-drain-2026-10-09",
    R / "g2/analysis/source-ledger-final-static-successor-2026-10-09",
    R / "g2/analysis/repository-goal-source-reconciliation-2026-10-09",
    R / "g2/analysis/csky-indexed-word-accessor-2026-10-09",
    R / "g2/analysis/touch-compiler-matrix-2026-10-09",
    R / "g2/analysis/csky-offset256-accessor-2026-10-09",
    R / "g2/analysis/csky-descriptor-initializer-2026-10-09",
    R / "g2/analysis/touch-compiler14-successor-2026-10-09",
    R / "g2/analysis/touch-scb14-holdouts-2026-10-09",
    R / "g2/analysis/touch-gpio14-family-2026-10-09",
    R / "g2/analysis/touch-gpio14-linkage-2026-10-09",
    R / "g2/analysis/touch-scb14-wrappers-2026-10-09",
    R / "g2/analysis/touch-pdl14-finite-census-2026-10-09",
    R / "g2/analysis/touch-pdl14-system-interface-2026-10-09",
    R / "g2/analysis/touch-systick14-literal-extents-2026-10-09",
    R / "g2/analysis/touch-sysint14-linkage-2026-10-09",
    R / "g2/analysis/touch-syslib14-assembly-2026-10-09",
    R / "g2/analysis/touch-syslib14-delay-linkage-2026-10-09",
    R / "g2/analysis/touch-systick14-linkage-2026-10-09",
    R / "g2/analysis/touch-pdl14-inline-emission-2026-10-09",
    R / "g2/analysis/touch-clkhf14-attribution-2026-10-09",
    R / "g2/analysis/touch-sysclk14-frequency-linkage-2026-10-09",
    R / "g2/analysis/touch-syspm14-linkage-2026-10-09",
    R / "g2/analysis/touch-clkpump14-attribution-2026-10-09",
    R / "g2/analysis/touch-i2c14-slave-linkage-2026-10-09",
    R / "g2/analysis/touch-pdl14-residual-boundary-2026-10-09",
    R / "g2/analysis/touch-libgcc14-division-2026-10-09",
    R / "g2/analysis/touch-pdl14-history-layout-2026-10-09",
    R / "g2/analysis/touch-libgcc14-source-rebuild-2026-10-09",
    R / "g2/analysis/touch-newlib14-memcpy-2026-10-09",
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

baseline = json.loads((R / "g2/analysis/rescan-2026-10-09T032723Z/snapshot.json").read_text())
audit = json.loads((R / "g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/preservation-before.json").read_text())["audit"]
bad = []
count = 0
for root in ("g2/analysis", "g2/components"):
    for manifest in (R / root).rglob("DELIVERABLES.json"):
        if manifest.parent in TARGETS:
            continue
        data = json.loads(manifest.read_text())
        files = data.get("files", {}) if isinstance(data, dict) else {}
        if not isinstance(files, dict):
            continue
        for name, value in files.items():
            expected = value if isinstance(value, str) else value.get("sha256") if isinstance(value, dict) else None
            if not expected:
                continue
            path = R / name if name.startswith(("g2/", "r1/", "docs/", "third-party/")) else manifest.parent / name
            count += 1
            if sha(path) != expected:
                bad.append(str(path.relative_to(R)))

index_before = sha(R / ".git/index")
preservation = {
    "prior_sealed_entries": count,
    "seal_mismatches": bad,
    "audit_inputs": len(audit),
    "audit_mismatches": [name for name, value in audit.items() if sha(R / name) != (value if isinstance(value, str) else value["sha256"])],
    "checkpoints": {name: sha(R / value["path"]) == value["sha256"] for name, value in baseline["checkpoints"].items()},
    "index_sha256": index_before,
    "index_matches_previous_scan": index_before == baseline["index_sha256_after"],
    "index_stable_during_seal": sha(R / ".git/index") == index_before,
}
assert not preservation["seal_mismatches"]
assert not preservation["audit_mismatches"]
assert all(preservation["checkpoints"].values())

for target in TARGETS[1:]:
    (target / "preservation.json").write_text(json.dumps(preservation, indent=2) + "\n")
for target in TARGETS:
    files = {
        str(path.relative_to(R)): sha(path)
        for path in sorted(target.iterdir())
        if path.is_file() and path.name != "DELIVERABLES.json"
    }
    (target / "DELIVERABLES.json").write_text(json.dumps({"files": files}, indent=2) + "\n")
print(json.dumps(preservation, indent=2))

#!/usr/bin/env python3
"""Bind proven native HCI names to selected C implementations."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-dependencies.o"
BOUND = OUT / "apollo-main-hci-aliases.o"
RECEIPT = OUT / "hci-source-aliases-receipt.json"
PAIRS = {
    "hciCmdRecvCmpl": "audio_ble_hci_cmd_receive_complete",
    "hciCoreNumCmplPkts": "audio_ble_hci_num_complete_packets",
    "hciCoreCisByHandle": "audio_ble_hci_cis_by_handle",
    "hciCoreCisClose": "audio_ble_hci_cis_close",
    "hciCoreCisOpen": "audio_ble_hci_cis_open",
    "hciCoreConnClose": "audio_ble_hci_conn_close",
    "hciCoreConnOpen": "audio_ble_hci_conn_open",
}
SOURCES = [
    ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_cmd_lower.c",
    ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_event_command_children.c",
    ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_cis.c",
    ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_conn_lifecycle.c",
]
PRIOR_JOIN = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-hci-joins-round435/hci-joins-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def symbols(path):
    result = {}
    for line in run("arm-none-eabi-nm", "--defined-only", str(path)).splitlines():
        bits = line.split()
        if len(bits) == 3:
            result.setdefault(bits[2], []).append((bits[0], bits[1]))
    return result


def unresolved(path):
    return set(run("arm-none-eabi-nm", "-u", str(path)).split()) - {"U"}


def section_bytes(path, section):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "section.bin"
        subprocess.run(
            ["arm-none-eabi-objcopy", "-O", "binary", "-j", section, str(path), str(output)],
            cwd=ROOT,
            check=True,
        )
        return output.read_bytes()


def main():
    base_receipt = OUT / "receipt.json"
    prior = json.loads(base_receipt.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_DEPENDENCY_COMPOSITION"
    assert sha(BASE) == prior["output_sha256"]
    join = json.loads(PRIOR_JOIN.read_text())
    for alias, provider in PAIRS.items():
        assert join["bindings"][alias] == provider
    for source in SOURCES:
        assert sha(source) == join["source_hashes"][str(source.relative_to(ROOT))]
    before = symbols(BASE)
    missing_before = unresolved(BASE)
    assert len(missing_before) == prior["unresolved_after"] == 654
    for alias, provider in PAIRS.items():
        assert alias in missing_before and alias not in before
        assert len(before[provider]) == 1 and before[provider][0][1] == "T"

    args = ["arm-none-eabi-ld", "-r"]
    for alias, provider in PAIRS.items():
        args += ["--defsym", f"{alias}={provider}"]
    subprocess.run(args + [str(BASE), "-o", str(BOUND)], cwd=ROOT, check=True)
    after = symbols(BOUND)
    missing_after = unresolved(BOUND)
    assert set(after) - set(before) == set(PAIRS)
    assert missing_after == missing_before - set(PAIRS)
    for alias, provider in PAIRS.items():
        assert after[alias] == after[provider] == before[provider]
    assert section_bytes(BASE, ".text") == section_bytes(BOUND, ".text")
    assert "hciCb" in missing_after

    receipt = {
        "status": "PASS_SEVEN_SOURCE_HCI_ALIASES",
        "base_receipt": str(base_receipt.relative_to(ROOT)),
        "base_receipt_sha256": sha(base_receipt),
        "base_object_sha256": sha(BASE),
        "source_files": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in SOURCES],
        "prior_join_receipt": "g2/analysis/c-source-completion-20261011/peripherals/root-hci-joins-round435/hci-joins-receipt.json",
        "prior_join_receipt_sha256": sha(PRIOR_JOIN),
        "native_addresses": {"hciCmdRecvCmpl": "0x52aef8", "hciCoreNumCmplPkts": "0x530c08"},
        "aliases": PAIRS,
        "unresolved_before": len(missing_before),
        "unresolved_after": len(missing_after),
        "executable_text_unchanged": True,
        "output": str(BOUND.relative_to(ROOT)),
        "output_sha256": sha(BOUND),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["hciCb allocation and native RAM address are unresolved", "Final placement and hardware behavior are unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(missing_after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()

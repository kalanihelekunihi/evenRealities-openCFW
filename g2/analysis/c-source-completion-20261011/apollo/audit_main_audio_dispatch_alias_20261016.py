#!/usr/bin/env python3
"""Pin the shared C-owned audio dispatch/control RAM alias."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OWNER = G2 / "components/audio/uart_thread_source_candidate/audio_app_control_and_open_20261016.c"
SUBMIT = G2 / "components/audio/audio_submit_source_candidate/submit.c"
LAYOUT = G2 / "analysis/c-source-completion-20261011/apollo/main_audio_dispatch_state_alias_20003f98.ld"
BASE = G2 / "build/c-firmware/20261016/main-pdm-clock-pin-words/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-audio-dispatch-alias"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            int.from_bytes(payload[0x53cd94-0x438000:0x53cd98-0x438000], "little") != 0x20003f98:
        raise RuntimeError("native audio dispatch record changed")
    if ("g2_audio_control_context_20003f98[0x10]" not in OWNER.read_text() or
            "g2_audio_dispatch_state + 12u" not in SUBMIT.read_text() or
            "g2_audio_dispatch_state + 8u" not in SUBMIT.read_text()):
        raise RuntimeError("C audio dispatch record sources changed")
    candidate = OUT / "candidate.o"
    names = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(candidate)], text=True).splitlines():
        parts = line.split()
        if parts and parts[-1] in ("g2_audio_control_context_20003f98", "g2_audio_dispatch_state"):
            names[parts[-1]] = parts
    if (set(names) != {"g2_audio_control_context_20003f98", "g2_audio_dispatch_state"} or
            names["g2_audio_control_context_20003f98"][0] != names["g2_audio_dispatch_state"][0] or
            int(names["g2_audio_control_context_20003f98"][1], 16) != 16 or
            undefined(BASE) - undefined(candidate) != {"g2_audio_dispatch_state"} or
            undefined(candidate) - undefined(BASE) or
            len(undefined(BASE)) != 129 or len(undefined(candidate)) != 128):
        raise RuntimeError("shared audio dispatch alias link changed")
    submit_output = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_submit.py")], text=True).strip()
    app_output = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/c-source-completion-20261011/apollo/verify_audio_app_control_and_open_20261016.py")], text=True).strip()
    if submit_output != "PASS_AUDIO_SUBMIT 96" or \
            not app_output.startswith("PASS_EXPERIMENTAL_AUDIO_APP_CONTROL_AND_OPEN_C_ORACLE 126 "):
        raise RuntimeError("audio dispatch source oracles changed")
    result = {"status": "PASS_BOUNDED_MAIN_AUDIO_DISPATCH_SHARED_RAM_ALIAS",
              "stock_payload_sha256": PAYLOAD_SHA,
              "owner_source": str(OWNER.relative_to(ROOT)), "owner_source_sha256": sha(OWNER),
              "submit_source": str(SUBMIT.relative_to(ROOT)), "submit_source_sha256": sha(SUBMIT),
              "linker_script": str(LAYOUT.relative_to(ROOT)), "linker_script_sha256": sha(LAYOUT),
              "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
              "candidate_object": str(candidate.relative_to(ROOT)), "candidate_object_sha256": sha(candidate),
              "native_record_address": "0x20003f98", "source_record_bytes": 16,
              "queue_offset": 12, "task_offset": 8,
              "audio_submit_oracle": submit_output, "app_control_oracle": app_output,
              "unresolved_before": 129, "unresolved_after": 128,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["The alias joins two source names to one 16-byte C record, not two allocations.",
                         "The final absolute RAM placement, startup writer and complete object extent remain open.",
                         "Isolated body oracles do not establish the whole Main image or hardware behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], result["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()

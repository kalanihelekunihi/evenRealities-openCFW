#!/usr/bin/env python3
"""Bind the bounded EvenAI C chain to the current Apollo main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
NANOPB = ROOT / "third-party/upstream/nanopb"
ARCHIVE = G2 / "build/c-firmware/20261016/main-nanopb-pinned/libg2_nanopb.a"
BASE = G2 / "build/c-firmware/20261016/main-os-list-initialize-bound/apollo-main-os-list-initialize-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-frame-chain-bound"
SOURCES = [
    "even_ai_frame_process_4e31cc.c", "even_ai_decoder_context_48f49c.c",
    "even_ai_descriptor_777144.c", "even_ai_rx_ctrl_4e3530.c",
    "even_ai_rx_vad_4e391a.c", "even_ai_rx_analyse_4e403c.c",
    "even_ai_rx_simple_4e47a0.c", "even_ai_rx_remaining_4e3d34.c",
    "even_ai_tx_ctrl_4e35fc.c", "even_ai_service_dispatch_497ea2.c",
    "even_ai_state_mutex_4e1fa6.c",
    "even_ai_heartbeat_timer_4e304c.c",
    "even_ai_common_response_4e5338.c", "even_ai_response_status_78f6e7.c",
]
ORACLES = [
    ("main-even-ai-frame-transitive-service-4e31cc", "PASS_NATIVE_MAIN_EVEN_AI_FRAME_TRANSITIVE_SERVICE_4E31CC", 15),
    ("main-even-ai-frame-log-extended-4e31cc", "PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_EXTENDED_4E31CC", 16),
    ("main-even-ai-frame-log-short-4e31cc", "PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_SHORT_4E31CC", 16),
    ("main-even-ai-frame-log-short4-4e31cc", "PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_SHORT4_4E31CC", 16),
    ("main-even-ai-service-dispatch-497ea2", "PASS_NATIVE_MAIN_EVEN_AI_SERVICE_DISPATCH_497EA2", 37),
    ("main-even-ai-state-mutex-4e1fa6", "PASS_NATIVE_MAIN_EVEN_AI_STATE_MUTEX_4E1FA6", 6),
    ("main-even-ai-heartbeat-timer-4e304c", "PASS_NATIVE_MAIN_EVEN_AI_HEARTBEAT_TIMER_4E304C", 12),
    ("main-even-ai-common-response-4e5338", "PASS_NATIVE_MAIN_EVEN_AI_COMMON_RESPONSE_4E5338", 16),
]
HANDLERS = {
    "rx": {"ctrl": "4e3530", "vad": "4e391a", "ask": "4e3d34",
           "analyse": "4e403c", "reply": "4e42b4", "skill": "4e4538",
           "prompt": "4e47a0", "event": "4e4a34", "heartbeat": "4e4e5c",
           "config": "4e50d8"},
    "tx": {"ctrl": "4e35fc", "vad": "4e39ea", "ask": "4e3ea4",
           "analyse": "4e412c", "reply": "4e43a0", "skill": "4e4608",
           "prompt": "4e4888", "event": "4e4b20", "heartbeat": "4e4f30",
           "config": "4e51c0"},
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo main payload changed")
    for literal, target, expected in ((0x4e3d28, 0x78f6e7, 7),
                                      (0x4e4108, 0x78f6e8, 8)):
        if int.from_bytes(image[literal-0x438000:literal-0x438000+4], "little") != target or \
                image[target-0x438000] != expected:
            raise RuntimeError("EvenAI response status ROM pointer changed")
    verified = []
    for directory, status, cases in ORACLES:
        path = G2 / "build/c-firmware/20261016" / directory / "oracle-receipt.json"
        data = json.loads(path.read_text())
        if data["status"] != status or data["cases"] != cases or \
                data["stock_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
            raise RuntimeError(f"Oracle changed: {path}")
        source = COMP / ("even_ai_frame_process_4e31cc.c" if "frame" in directory else
                         "even_ai_state_mutex_4e1fa6.c" if "state-mutex" in directory else
                         "even_ai_heartbeat_timer_4e304c.c" if "heartbeat-timer" in directory else
                         "even_ai_common_response_4e5338.c" if "common-response" in directory else
                         "even_ai_service_dispatch_497ea2.c")
        if data["source_sha256"] != sha(source):
            raise RuntimeError(f"Oracle source changed: {source}")
        verified.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    for family, handlers in HANDLERS.items():
        for name, address in handlers.items():
            path = G2 / "build/c-firmware/20261016" / \
                f"main-even-ai-{family}-{name}-{address}/oracle-receipt.json"
            data = json.loads(path.read_text())
            if data["status"] != f"PASS_NATIVE_MAIN_EVEN_AI_{family.upper()}_{name.upper()}_{address.upper()}" or \
                    data["cases"] != (18 if family == "rx" else 17) or \
                    data["source_sha256"] != sha(ROOT / data["source"]):
                raise RuntimeError(f"Handler oracle changed: {path}")
            verified.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
             '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
             "-I", str(CONFIG), "-I", str(NANOPB)]
    objects = []
    for name in SOURCES:
        source = COMP / name
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", *flags, "-c", str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    before = symbols(BASE, "-u")
    if len(before) != 186 or "audio_even_ai_frame_process_4e31cc" not in before:
        raise RuntimeError("Apollo main base frontier changed")
    linked = OUT / "apollo-main-even-ai-frame-chain-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(str(obj) for obj in objects), str(ARCHIVE),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    defined = symbols(linked, "--defined-only")
    if "audio_even_ai_frame_process_4e31cc" in after or \
            "audio_even_ai_frame_process_4e31cc" not in defined or \
            any(name in after for name in ("pb_decode", "pb_encode", "audio_even_ai_service_dispatch_497ea2")):
        raise RuntimeError("EvenAI frame chain did not bind")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_FRAME_CHAIN_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "source": [{"path": str((COMP / name).relative_to(ROOT)), "sha256": sha(COMP / name)}
                   for name in SOURCES],
        "nanopb_archive": str(ARCHIVE.relative_to(ROOT)), "nanopb_archive_sha256": sha(ARCHIVE),
        "oracles": verified,
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["The frame and service oracles exercise bounded no-log cases only.",
                   "The linked object is relocatable and retains unresolved imports.",
                   "RAM ownership, timer/lock/transport providers, and logging remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()

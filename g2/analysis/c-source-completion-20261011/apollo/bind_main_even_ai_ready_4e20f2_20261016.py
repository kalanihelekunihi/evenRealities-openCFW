#!/usr/bin/env python3
"""Bind the stock-compared EvenAI async-update C provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_ready_4e20f2.c"
DISPATCH = G2 / "components/audio/uart_thread_source_candidate/even_ai_service_dispatch_497ea2.c"
LOCAL = G2 / "components/audio/uart_thread_source_candidate/even_ai_local_decode_498092.c"
BASE = G2 / "build/c-firmware/20261016/main-even-ai-ready-ram-bound/apollo-main-even-ai-ready-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ready-bound"
ORACLE = G2 / "build/c-firmware/20261016/main-even-ai-ready-simple-oracle/oracle-receipt.json"
PROVIDER = "audio_even_ai_ready_4e20f2"
ADDED = {
    "audio_even_ai_ancc_state_sync_497cf0", "audio_even_ai_app_acquire_54f380",
    "audio_even_ai_common_timer_stop_4e2e86", "audio_even_ai_display_ctrl_4e1fd2",
    "audio_even_ai_init_text_stream_4e551e", "audio_even_ai_stop_current_streaming_4e557c",
    "audio_even_ai_stream_interval_get_4e550a", "audio_even_ai_sync_remote_4973f4",
    "audio_even_ai_timer_start_all_4e31a0", "audio_text_stream_copy_bytes_553274",
    "audio_text_stream_pending_text_552ce8", "audio_text_stream_set_text_552c20",
}
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_EVEN_AI_READY_SIMPLE_C_ORACLE" or \
            oracle["cases"] != 84 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["payload_sha256"] != PINNED:
        raise RuntimeError("EvenAI ready native oracle or source changed")
    dispatcher = DISPATCH.read_text()
    local = LOCAL.read_text()
    if not all(s in dispatcher for s in ("if (length > 0x200u)",
                                              "set_text(p, 3u", "set_text(p, 5u",
                                              "set_text(p, 6u")) or \
            not all(s in local for s in ("state[0] = 1u", "state[1] = 1u",
                                           "state[2] = 1u")):
        raise RuntimeError("Known EvenAI ingress length contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "even_ai_ready_4e20f2.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER}:
        raise RuntimeError("EvenAI ready C provider symbols changed")
    before = names(BASE, "-u")
    if len(before) != 172 or PROVIDER not in before or ADDED & before:
        raise RuntimeError("Apollo EvenAI ready base frontier changed")
    linked = OUT / "apollo-main-even-ai-ready-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before != ADDED or len(after) != 183:
        raise RuntimeError("Apollo EvenAI ready linked frontier changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
        "dispatcher_source": str(DISPATCH.relative_to(ROOT)), "dispatcher_sha256": sha(DISPATCH),
        "local_decoder_source": str(LOCAL.relative_to(ROOT)), "local_decoder_sha256": sha(LOCAL),
        "payload_sha256": PINNED,
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [PROVIDER], "imports_added": sorted(ADDED),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Eighty-four controlled stock comparisons cover selected actions, text boundaries through 0x200, and enabled log metadata and first values.",
                   "Known service-dispatch text ingress caps at 0x200; indirect or unseen writers and malformed input remain outside the bound.",
                   "Twelve descendant providers are now explicit imports; logger side effects, later variadic values, final layout/startup, and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()

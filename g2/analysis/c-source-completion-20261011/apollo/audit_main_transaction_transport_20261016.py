#!/usr/bin/env python3
"""Verify the bounded C-owned GX8002 receive scratch span."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-offline-assert-fault-alias/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-transaction-transport"
OBJ = OUT / "candidate.o"
SOURCE = G2 / "components/audio/transaction_send_source_candidate/transaction_transport_2007397c.c"
LINK = G2 / "components/audio/transaction_send_source_candidate/transaction_transport_2007397c.ld"
SEND = G2 / "components/audio/transaction_send_source_candidate/send.c"
EXCHANGE = G2 / "components/audio/transaction_exchange_source_candidate/exchange.c"
RESPONSE = G2 / "components/audio/codec_response_offline/response.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = STOCK.read_bytes()[32:]
    if (hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or
            int.from_bytes(payload[0x57ce6c-0x438000:0x57ce70-0x438000], "little") != 0x2007397c):
        raise RuntimeError("stock GX8002 receive base changed")
    if ("30u, &response" not in SEND.read_text() or
            "codec_response_read(buffer, (uint16_t)capacity" not in EXCHANGE.read_text() or
            "if(capacity<total)return -1" not in RESPONSE.read_text()):
        raise RuntimeError("selected GX8002 receive capacity chain changed")
    with OBJ.open("rb") as stream:
        elf = ELFFile(stream)
        section = elf.get_section_by_name(".g2_transaction_transport_2007397c")
        if (section is None or section["sh_type"] != "SHT_NOBITS" or
                section["sh_addr"] != 0x2007397c or section["sh_size"] != 30):
            raise RuntimeError("bounded receive scratch section changed")
    syms = subprocess.check_output(["arm-none-eabi-nm", "-S", str(OBJ)], text=True)
    if not any(line.startswith("2007397c 0000001e B g2_audio_transaction_transport")
               for line in syms.splitlines()):
        raise RuntimeError("receive scratch symbol or size changed")
    if (undefined(BASE) - undefined(OBJ) != {"g2_audio_transaction_transport"} or
            undefined(OBJ) - undefined(BASE) or
            len(undefined(BASE)) != 126 or len(undefined(OBJ)) != 125):
        raise RuntimeError("receive scratch import reduction changed")
    def oracle(name):
        return subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
            str(G2 / f"analysis/c-source-completion-20261011/peripherals/{name}.py")], text=True).strip()
    send_oracle = oracle("verify_audio_transaction_send")
    exchange_oracle = oracle("verify_audio_transaction_exchange")
    if send_oracle != "PASS_AUDIO_TRANSACTION_SEND 16" or exchange_oracle != "PASS_AUDIO_TRANSACTION_EXCHANGE 25":
        raise RuntimeError("GX8002 send/exchange oracle changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_GX8002_RECEIVE_SCRATCH_C",
        "stock_payload_sha256": PAYLOAD_SHA, "native_receive_base": "0x2007397c",
        "receive_bytes": 30, "next_known_tx_packet_base": "0x2007399c",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "send_oracle": send_oracle, "exchange_oracle": exchange_oracle,
        "unresolved_before": 126, "unresolved_after": 125,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The C span covers the selected 30-byte receive capacity, not an inferred full stock allocation.",
                   "UART read callback behavior and runtime initialization remain outside these isolated tests.",
                   "The neighboring TX packet and whole-image RAM collision audit remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()

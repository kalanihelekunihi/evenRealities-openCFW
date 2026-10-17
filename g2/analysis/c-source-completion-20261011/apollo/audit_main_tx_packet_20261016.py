#!/usr/bin/env python3
"""Check nominal GX8002 TX packet C storage and preserve overflow gate."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-transaction-transport/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-tx-packet"
OBJ = OUT / "candidate.o"
SOURCE = G2 / "components/audio/transaction_construct_source_candidate/tx_packet_2007399c.c"
LINK = G2 / "components/audio/transaction_construct_source_candidate/tx_packet_2007399c.ld"
PACK = G2 / "components/audio/codec_request_offline/request.c"
SEND = G2 / "components/audio/transaction_construct_source_candidate/construct.c"
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
            int.from_bytes(payload[0x57cb30-0x438000:0x57cb34-0x438000], "little") != 0x2007399c):
        raise RuntimeError("stock GX8002 TX base changed")
    pack = PACK.read_text()
    if ("if(declared>16)return -2" not in pack or
            "copy(wire+14,payload,length)" not in pack or
            "g2_audio_tx_packet" not in SEND.read_text()):
        raise RuntimeError("selected packet construction changed")
    # 16-bit declared length can wrap while the copy retains the original length.
    if ((65535 + 4) & 0xffff) > 16 or 65535 + 14 <= 30:
        raise RuntimeError("length-wrap gate changed")
    with OBJ.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address in ((".g2_transaction_transport_2007397c", 0x2007397c),
                              (".g2_tx_packet_2007399c", 0x2007399c)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != 30):
                raise RuntimeError(f"composed RX/TX RAM placement changed: {name}")
    syms = subprocess.check_output(["arm-none-eabi-nm", "-S", str(OBJ)], text=True)
    if not any(line.startswith("2007399c 0000001e B g2_audio_tx_packet") for line in syms.splitlines()):
        raise RuntimeError("TX packet symbol or size changed")
    if (undefined(BASE) - undefined(OBJ) != {"g2_audio_tx_packet"} or
            undefined(OBJ) - undefined(BASE) or
            len(undefined(BASE)) != 125 or len(undefined(OBJ)) != 124):
        raise RuntimeError("TX packet import reduction changed")
    oracle = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_transaction_construct.py")], text=True).strip()
    if oracle != "PASS_AUDIO_TRANSACTION_CONSTRUCT 9":
        raise RuntimeError("transaction construct oracle changed")
    wrap_path = OUT / "native-length-wrap-receipt.json"
    wrap = json.loads(wrap_path.read_text())
    if (wrap["status"] != "PASS_NATIVE_MAIN_GX8002_TX_LENGTH_WRAP_GATE" or
            wrap["stock_payload_sha256"] != PAYLOAD_SHA or len(wrap["cases"]) != 5 or
            wrap["cases"][-1]["copy_calls"][1][2] != 65535):
        raise RuntimeError("native TX length-wrap gate changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_GX8002_NOMINAL_TX_PACKET_C",
        "stock_payload_sha256": PAYLOAD_SHA, "native_tx_base": "0x2007399c",
        "nominal_packet_bytes": 30, "adjacent_rx_base": "0x2007397c",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "construct_oracle": oracle,
        "native_wrap_receipt": str(wrap_path.relative_to(ROOT)),
        "native_wrap_receipt_sha256": sha(wrap_path),
        "unresolved_before": 125, "unresolved_after": 124,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["30 bytes cover the ordinary declared-body maximum of 16 plus 14 header bytes.",
                   "Five native constructor cases confirm a 16-bit declared-length wrap can request a 65535-byte copy while reporting a 17-byte packet; this is an explicit unresolved correctness gate, not a safe bound.",
                   "No full allocation extent, arbitrary-input parity, UART behavior or whole-image RAM collision proof is claimed."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(receipt))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Re-check extracted stock data assets against official 2.2.6.10 blobs.

Host-only. Does not open hardware. Exits 0 if KWS command/weight spans, the
compiled C weight words, EVENBAT, and parsed uint8 font/image arrays match.
"""
from __future__ import annotations
import argparse, hashlib, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODEC_SHA = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
OTA_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
WGT_SHA = "397971427d7097180d07eb63f9822904a555e51f7643d946ebb38d71a967f8cf"
CMD_SHA = "c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9"
FWPK_MAIN = 0x958C
CMD_OFF, CMD_N = 0x18D90, 9164
WGT_OFF, WGT_N = 0x1B15C, 120800
EVENBAT_VA = 0x646BF8
EVENBAT_N = 5632
OTA_VA_BIAS = 0x437FE0  # OTA file offset + this = Apollo VA

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def ota_off(va: int) -> int:
    return va - OTA_VA_BIAS

def fail(msg: str) -> None:
    raise SystemExit(msg)

def uint8_arrays(path: Path):
    text = path.read_text()
    pat = re.compile(
        r"static const uint8_t\s+(\w+)\[(0x[0-9a-fA-F]+|\d+)\][^\n]*ROM 0x([0-9a-fA-F]+)"
    )
    for match in pat.finditer(text):
        name, size, rom = match.group(1), match.group(2), match.group(3)
        count = int(size, 16) if size.startswith(("0x", "0X")) else int(size)
        # Parse only the initializer, and strip comments so size notes like
        # "20x20 L8" cannot contribute a phantom 0x20 token.
        brace = text.find("{", match.start())
        end = text.find("\n};", brace)
        if brace < 0 or end < 0:
            fail(f"{path}:{name} has no array end")
        body = re.sub(r"/\*.*?\*/", "", text[brace:end], flags=re.S)
        values = [int(item, 16) for item in re.findall(r"0x([0-9a-fA-F]{2})", body)]
        if len(values) != count:
            fail(f"{path}:{name} parsed {len(values)} != {count}")
        yield name, int(rom, 16), bytes(values)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root
    codec = (root / "g2/blobs/official/g2-2.2.6.10/firmware_codec.bin").read_bytes()
    ota = (root / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()
    weights = (root / "g2/src/codec/npu/kws_weights_2_2_6_10.bin").read_bytes()
    source = (root / "g2/src/codec/npu/kws_weights_source.c").read_text()
    if sha(codec) != CODEC_SHA or sha(ota) != OTA_SHA:
        fail("official 2.2.6.10 blobs do not match the locked SHA-256")
    cmd = codec[CMD_OFF:CMD_OFF + CMD_N]
    wgt = codec[WGT_OFF:WGT_OFF + WGT_N]
    if len(cmd) != CMD_N or sha(cmd) != CMD_SHA:
        fail("KWS command window does not match")
    if wgt != weights or sha(wgt) != WGT_SHA:
        fail("KWS weight window does not match the extracted asset")
    words = [int(item, 0) for item in re.findall(r"UINT32_C\((0x[0-9a-fA-F]+)\)", source)]
    packed = b"".join(struct.pack("<I", word) for word in words)
    if packed != weights:
        fail("kws_weights_source.c words do not match the weight asset")
    if codec[FWPK_MAIN + 0xF804:FWPK_MAIN + 0x2F3B0] != cmd + wgt:
        fail("BINH A NPU tail is not cmd+weights")
    evenbat = ota[ota_off(EVENBAT_VA):ota_off(EVENBAT_VA) + EVENBAT_N]
    if evenbat[0x15C0:0x15C8] != b"EVENBAT\x00":
        fail("EVENBAT name is not at stock struct offset 0x15C0")
    arrays = []
    for rel in (
        "g2/src/apollo-main/app/S6-fonts-residual-data/app_image_assets_data.c",
        "g2/src/apollo-main/ui/S6-fonts-residual-data/rom_fonts_data.c",
    ):
        for name, va, data in uint8_arrays(root / rel):
            stock = ota[ota_off(va):ota_off(va) + len(data)]
            if data != stock:
                fail(f"{rel}:{name} @ {va:#x} differs from official OTA")
            arrays.append({"file": rel, "name": name, "va": f"{va:#x}", "bytes": len(data)})
    print(f"OK kws cmd {CMD_N} weights {WGT_N} evenbat {EVENBAT_N} uint8_arrays {len(arrays)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

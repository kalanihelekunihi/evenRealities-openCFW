#!/usr/bin/env python3
"""Fail-closed section/NPU-payload closure for G2 codec BINH image A/B stage2.

Pins the SRAM text/data load addresses, sizes, and entry points of both BINH
stage2 images plus the gxNPU (KWS model) payload offsets, re-derived from the
hash-pinned blob. Decode was performed with the official C-SKY backend
(c-sky/binutils-gdb objdump, commit 2409f5af709d5fef4f41cbeb30ef59bc1046b252,
validated per the audit doc); this analyzer re-verifies every resulting fact
directly over the blob: vector tables, entry bytes, evidence instructions,
size-getter constants, boundary fill, and exact-fit arithmetic. Read-only and
deterministic; no external disassembler required.
"""
import csv, hashlib, json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEC = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
MANIFEST = ROOT / "tools/manifests/g2-codec-stage2-section-map.tsv"

CODEC_SIZE = 326092
CODEC_SHA256 = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
SEG2_OFF = 38284  # FWPK type-2 record offset; verified by the FWPK analyzer

IRAM_BASE = 0x10000000
KWS_CMD_SIZE = 9164        # movi r0, 9164 at flash 0x8BF4
KWS_WEIGHT_SIZE = 120800   # movi r0, 55264; bseti r0, 16 at flash 0x8BFC

# Canonical GX8002 CRT0 reset prefix (VBR setup + stack load), decoded from
# c-sky objdump: lrw r0,0x80000200; mtcr r0,cr<0,0>; mfcr r1,cr<31,0>;
# bclri r1,3; mtcr r1,cr<31,0>; lrw r3,[sp-pool]; mov r14,r3
CRT0_PREFIX = bytes.fromhex("081000c020641fc02160833901c03f6465108f6f")


class AuditError(Exception):
    pass


def sh(b):
    return hashlib.sha256(b).hexdigest()


def _need(cond, msg):
    if not cond:
        raise AuditError(msg)


def _check_app(seg, base, expect_base, expect_vt_rest, sp_value):
    """Pin one stage2 SRAM application: vector table, entry, CRT0, stack."""
    vt = struct.unpack_from("<64I", seg, base)
    app_base = vt[0] - 0x100
    _need(app_base == expect_base, "app IRAM base changed at 0x%x" % base)
    _need(set(vt[1:]) == set(expect_vt_rest), "app vector handler set changed")
    _need(all(expect_base <= v < expect_base + 0x1408C for v in vt),
          "app vector escapes span")
    _need(seg[base + 0x100:base + 0x100 + len(CRT0_PREFIX)] == CRT0_PREFIX,
          "CRT0 reset prefix changed")
    sp = struct.unpack_from("<I", seg, base + 0x100 + 0x24)[0]
    _need(sp == sp_value, "app stack pointer literal changed")
    return {"iram_base": "0x%08x" % app_base,
            "entry": "0x%08x" % vt[0],
            "vector_entries": 64,
            "handlers": ["0x%08x" % v for v in sorted(set(vt[1:]))],
            "stack_pointer": "0x%08x" % sp,
            "npu_sram_size_implied": app_base - IRAM_BASE}


def analyze():
    blob = CODEC.read_bytes()
    _need(len(blob) == CODEC_SIZE and sh(blob) == CODEC_SHA256, "codec blob changed")
    seg = blob[SEG2_OFF:]
    _need(len(seg) == 287808, "main image size changed")

    # --- BINH headers (fields verified by the FWPK segment analyzer) -------
    a_s2size, a_s1size = struct.unpack_from("<II", seg, 12)
    b_base = 0x2F3B0
    b_s2size = struct.unpack_from("<I", seg, b_base + 12)[0]
    _need((a_s2size, a_s1size, b_s2size) == (0xC800, 0x3000, 0x1408C),
          "BINH stage2 sizes changed")
    a_xip_len = struct.unpack_from("<I", seg, 0x3000)[0]
    b_xip_len = struct.unpack_from("<I", seg, b_base + 0x3000)[0]
    _need(a_xip_len == 0x8E84 and b_xip_len == 0, "XIP lengths changed")

    # --- Image A stage2 section split --------------------------------------
    xip_off = 0x3004
    sram_off = 0x3000 + 4 + a_xip_len           # 0xBE88 (public SPL formula)
    _need(sram_off == 0xBE88, "A SRAM text offset changed")
    app_a = _check_app(seg, sram_off, 0x10023400, (0x10023640, 0x10025574),
                       0x2002F7FC)

    # Text ends with `jmp r15` + two literal-pool words, one 0xFFFFFFFF pad,
    # then zero-initialized data (boundary recovered by objdump sweep).
    text_off, text_size = sram_off, 0x30E4
    pad_off, data_off = text_off + text_size, text_off + text_size + 4
    data_size = (xip_off + a_s2size) - data_off   # stage2 flash end 0xF804
    _need(data_size == 0x894, "A SRAM data size changed")
    _need(seg[text_off + text_size - 8:text_off + text_size] ==
          bytes.fromhex("01103c789ce70220"), "A text tail changed")
    _need(seg[pad_off:pad_off + 4] == b"\xff" * 4, "A pad word changed")
    _need(seg[data_off:data_off + 16] == b"\0" * 16, "A data head changed")
    _need(0x30E4 + 4 + 0x894 == a_s2size - a_xip_len == 0x397C,
          "A SRAM combined size arithmetic broken")

    # --- Image B stage2 (SRAM-only; text boundary by last-return sweep) ----
    b_sram_off = b_base + 0x3000 + 4            # 0x323B4
    app_b = _check_app(seg, b_sram_off, 0x10003000, (0x10003240, 0x10004880),
                       0x2002FFFC)
    b_text_size = 0x1351C                       # last `pop r4-r9, r15` +2
    b_data_size = b_s2size - b_text_size
    _need(b_data_size == 0xB70, "B section arithmetic broken")
    _need(seg[b_sram_off + b_text_size - 4:b_sram_off + b_text_size] ==
          bytes.fromhex("961402f4"), "B text tail changed")

    # --- gxNPU / KWS payload offsets ---------------------------------------
    # LVP_KWS init loads the model from LD_NPU_IMAGE_OFFSET = 0xF804: an
    # lrw32 r8, 0xf804 (encoding ea88 + literal pool word) followed by two
    # flash reads with sizes from tiny constant-return getters.
    _need(seg[0x6D40:0x6D44].hex() == "88ea1100", "KWS lrw32 instruction changed")
    _need(struct.unpack_from("<I", seg, 0x6D84)[0] == 0xF804,
          "LD_NPU_IMAGE_OFFSET literal changed")
    _need(seg[0x8BF4:0x8BFA].hex() == "00eacc233c78", "cmd-size getter changed")
    _need(seg[0x8BFC:0x8C04].hex() == "00eae0d7b0383c78",
          "weight-size getter changed")
    cmd_off = 0xF804
    weight_off = cmd_off + KWS_CMD_SIZE
    payload_end = weight_off + KWS_WEIGHT_SIZE
    _need(payload_end == b_base, "KWS payload no longer ends at image B")
    _need(seg[0xADC1:0xADC1 + 28] == b"[LVP_KWS ]Init Flash Failed\n" and
          seg[0xADDE:0xADDE + 24] == b"[LVP_KWS ]Kws Use:%d ms\n" and
          seg[0xADF7:0xADF7 + 28] == b"[LVP_KWS ]Read Flash Failed\n",
          "KWS identity strings changed")

    regions = {
        "a_xip_text": (xip_off, a_xip_len),
        "a_sram_text": (text_off, text_size),
        "a_sram_pad": (pad_off, 4),
        "a_sram_data": (data_off, data_size),
        "a_kws_cmd": (cmd_off, KWS_CMD_SIZE),
        "a_kws_weight": (weight_off, KWS_WEIGHT_SIZE),
        "b_sram_text": (b_sram_off, b_text_size),
        "b_sram_data": (b_sram_off + b_text_size, b_data_size),
    }
    region_sha = {k: sh(seg[s:s + n]) for k, (s, n) in regions.items()}
    check_manifest(region_sha)

    return {
        "schema_version": 1,
        "analysis_mode": "read-only deterministic closure over hash-pinned blob; "
                         "objdump-derived facts re-verified as raw bytes and arithmetic",
        "decoder": {"tool": "c-sky/binutils-gdb objdump (official C-SKY backend)",
                    "commit": "2409f5af709d5fef4f41cbeb30ef59bc1046b252",
                    "note": "upstream binutils 2.43.1 mis-decodes 32-bit C-SKY "
                            "instructions (mtcr/bsr); the vendor fork is required"},
        "image_a": {
            "stage2": {
                "xip_text": {"flash": "[0x3004, 0xBE88)", "size": a_xip_len,
                             "executes": "XIP from flash (public default XIP base "
                                         "0x10200000; hardware-gated)",
                             "sha256": region_sha["a_xip_text"]},
                "sram_text": {"flash": "[0xBE88, 0xEF6C)", "size": text_size,
                              "iram": "[0x10023400, 0x100264E4)",
                              "sha256": region_sha["a_sram_text"]},
                "pad": {"flash": "[0xEF6C, 0xEF70)", "value": "0xFFFFFFFF"},
                "sram_data": {"flash": "[0xEF70, 0xF804)", "size": data_size,
                              "iram": "[0x100264E8, 0x10026D7C)",
                              "sha256": region_sha["a_sram_data"]},
                "combined_sram_copy": {"iram": "[0x10023400, 0x10026D7C)",
                                       "size": 0x397C}},
            "app": app_a,
            "npu_sram": {"iram": "[0x10000000, 0x10023400)", "size": 0x23400}},
        "image_b": {
            "stage2": {
                "sram_text": {"flash": "[0x323B4, 0x458D0)", "size": b_text_size,
                              "iram": "[0x10003000, 0x1001651C)",
                              "boundary": "derived: last function return at "
                                          "0x10016518 + 2 (heuristic)",
                              "sha256": region_sha["b_sram_text"]},
                "sram_data": {"flash": "[0x458D0, 0x46440)", "size": b_data_size,
                              "iram": "[0x1001651C, 0x1001708C)",
                              "sha256": region_sha["b_sram_data"]},
                "combined_sram_copy": {"iram": "[0x10003000, 0x1001708C)",
                                       "size": b_s2size}},
            "app": app_b},
        "kws_model_payload": {
            "identity": "LVP_KWS keyword-spotting gxNPU model (cmd + weight)",
            "load_offset_literal": "0xF804 (LD_NPU_IMAGE_OFFSET)",
            "cmd": {"flash": "[0xF804, 0x11BD0)", "size": KWS_CMD_SIZE,
                    "dram_staging": "0x20003304 (decoded)",
                    "sha256": region_sha["a_kws_cmd"]},
            "weight": {"flash": "[0x11BD0, 0x2F3B0)", "size": KWS_WEIGHT_SIZE,
                       "dram_staging": "0x200056D0 (decoded)",
                       "sha256": region_sha["a_kws_weight"]},
            "exact_fit": "0xF804 + 9164 + 120800 == 0x2F3B0 (image B offset)"},
        "production": {"production_routed": False,
                       "ownership": "proprietary NationalChip boundary; section/placement "
                                    "facts only, zero claimed source"},
    }


MANIFEST_HEADER = ["region", "segment_offset", "size", "sha256", "load_address",
                   "entry", "evidence"]


def manifest_rows(region_sha):
    return [
        ["a_xip_text", "0x00003004", 36484, region_sha["a_xip_text"],
         "xip-flash", "n/a",
         "executes in place from flash; public default XIP base 0x10200000 (hardware-gated)"],
        ["a_sram_text", "0x0000BE88", 12516, region_sha["a_sram_text"],
         "0x10023400", "0x10023500",
         "64-word vector table at base; CRT0 prefix + SP 0x2002F7FC pinned"],
        ["a_sram_pad", "0x0000EF6C", 4, region_sha["a_sram_pad"],
         "0x100264E4", "n/a", "0xFFFFFFFF flash-fill alignment word"],
        ["a_sram_data", "0x0000EF70", 2196, region_sha["a_sram_data"],
         "0x100264E8", "n/a", "zero-initialized head; combined copy ends 0x10026D7C"],
        ["a_kws_cmd", "0x0000F804", 9164, region_sha["a_kws_cmd"],
         "dram-0x20003304", "n/a",
         "LD_NPU_IMAGE_OFFSET 0xF804 via lrw32; size getter movi r0,9164"],
        ["a_kws_weight", "0x00011BD0", 120800, region_sha["a_kws_weight"],
         "dram-0x200056D0", "n/a",
         "size getter movi r0,55264+bseti r0,16 = 120800; cmd+weight ends exactly at image B"],
        ["b_sram_text", "0x000323B4", 79132, region_sha["b_sram_text"],
         "0x10003000", "0x10003100",
         "64-word vector table at base; CRT0 prefix + SP 0x2002FFFC; "
         "text/data boundary by last-return sweep (heuristic)"],
        ["b_sram_data", "0x000458D0", 2928, region_sha["b_sram_data"],
         "0x1001651C", "n/a", "remainder of combined SRAM copy to 0x1001708C"],
    ]


def check_manifest(region_sha):
    _need(MANIFEST.exists(), "section map manifest missing")
    with MANIFEST.open(newline="", encoding="utf8") as h:
        rows = list(csv.reader(h, delimiter="\t"))
    _need(rows[0] == MANIFEST_HEADER, "manifest header changed")
    expected = [[str(x) for x in row] for row in manifest_rows(region_sha)]
    _need(rows[1:] == expected, "manifest content changed")


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))

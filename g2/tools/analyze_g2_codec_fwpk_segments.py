#!/usr/bin/env python3
"""Fail-closed segment/interface closure for the G2 codec FWPK package.

Resolves both firmware_codec.bin FWPK segment destinations (load addresses,
sizes, entry/vector structure, target memory regions) against the public
NationalChip grus (GX8002) boot/flash container formats, and pins the
Apollo-side DFU flash-command evidence. Read-only and deterministic.
"""
import csv, hashlib, json, struct, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEC = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
APOLLO = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
MANIFEST = ROOT / "tools/manifests/g2-codec-fwpk-segment-map.tsv"
DFU_FM = ROOT / "tools/manifests/g2-service-codec-dfu-function-map.tsv"
CORE_SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

CODEC_SIZE = 326092
CODEC_SHA256 = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
APOLLO_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
DFU_FM_SHA256 = "2b84310693115302683c9136c2c2ca0e26178c4d3b1d7b9cedd250d10428c1e6"

# GX8002 (grus) memory constants, matching the public NationalChip SDK
# (arch/soc/grus/include/soc_config.h and base_addr.h, MIT licensed).
IRAM_BASE = 0x10000000          # CONFIG_STAGE1_IRAM_BASE
DRAM_BASE = 0x20000000          # CONFIG_STAGE1_DRAM_BASE
FLASH_XIP_BASE = 0x10200000     # CONFIG_FLASH_XIP_BASE (public default)
STAGE1_BLOCK = 0x3000           # CONFIG_STAGE1_SRAM_SIZE / CONFIG_STAGE1_IRAM_SIZE

# Apollo run-address delta for the official OTA image (run = file + delta).
RUN_DELTA = 0x00437FE0


class AuditError(Exception):
    pass


def sh(b):
    return hashlib.sha256(b).hexdigest()


def crc32_mpeg2(buf):
    crc = 0xFFFFFFFF
    for byte in buf:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc


def _need(cond, msg):
    if not cond:
        raise AuditError(msg)


def parse_fwpk(b):
    _need(len(b) == CODEC_SIZE and sh(b) == CODEC_SHA256, "codec blob changed")
    magic, version, count, reserved = struct.unpack_from("<4sIII", b, 0)
    _need(magic == b"FWPK" and version == 0x00000203 and count == 2 and reserved == 0,
          "FWPK header changed")
    records = []
    for i in range(count):
        rtype, size, offset, crc = struct.unpack_from("<IIII", b, 16 + 16 * i)
        seg = b[offset:offset + size]
        _need(len(seg) == size, "record overruns file")
        _need(zlib.crc32(seg) & 0xFFFFFFFF == crc, "record CRC mismatch")
        records.append({"type": rtype, "size": size, "offset": offset,
                        "crc32": "0x%08x" % crc, "sha256": sh(seg)})
    _need(records[0]["type"] == 1 and records[1]["type"] == 2, "record types changed")
    _need(16 + 16 * count + records[0]["size"] + records[1]["size"] == len(b),
          "FWPK layout no longer exact")
    return {"version": "0x%08x" % version, "record_count": count, "records": records}


def parse_boot_image(seg):
    """Type-1 segment: NationalChip grus UART boot container (public format)."""
    _need(len(seg) == 38236, "boot image size changed")
    chip_id, ctype, cver, delay, baud, rsv = struct.unpack_from("<HBBHBB", seg, 0)
    s1, s2baud, s2size, s2ck = struct.unpack_from(">IIII", seg, 8)
    rsv8 = seg[24:32]
    # Public identity: CHIP_ID_GX8002 = 0x8002, chip type 1, CHIP_VERSION_V1 = 1.
    _need(chip_id == 0x8002 and ctype == 1 and cver == 1, "boot chip identity changed")
    _need(delay == 0 and baud == 0 and rsv == 0 and rsv8 == b"\0" * 8,
          "boot header reserved fields changed")
    _need((s1, s2baud, s2size, s2ck) == (0x2800, 1500000, 0x6D3C, 0x24D441),
          "boot header stage fields changed")
    _need(32 + s1 + s2size == len(seg), "boot stage split no longer exact")
    stage1 = seg[32:32 + s1]
    stage2 = seg[32 + s1:]
    _need(sum(stage2) & 0xFFFFFFFF == s2ck, "stage2 byte-sum checksum mismatch")

    # Stage1 executes from IRAM 0x10000000: 64-word vector table at its base,
    # reset vector [0] = base + 0x100, traps [1..31] and [32..63] to two stubs.
    vt1 = struct.unpack_from("<64I", stage1, 0)
    _need(vt1[0] == IRAM_BASE + 0x100, "stage1 reset vector changed")
    _need(set(vt1[1:32]) == {IRAM_BASE + 0x130} and set(vt1[32:]) == {IRAM_BASE + 0x134},
          "stage1 vector pattern changed")

    # Stage2 executes from IRAM 0x10002800 (immediately after stage1): its own
    # 64-word vector table, reset = base + 0x100, handlers inside its span.
    s2base = IRAM_BASE + s1
    vt2 = struct.unpack_from("<64I", stage2, 0)
    _need(vt2[0] == s2base + 0x100, "stage2 reset vector changed")
    _need(all(s2base <= v < s2base + s2size for v in vt2),
          "stage2 vector escapes its load span")
    _need(set(vt2[1:]) == {s2base + 0x194, s2base + 0x924},
          "stage2 handler set changed")
    return {
        "chip_id": "0x%04x" % chip_id, "chip": "GX8002 (grus)",
        "chip_type": ctype, "chip_version": cver,
        "stage2_baud_rate": s2baud,
        "stage2_checksum_bytesum": "0x%08x" % s2ck,
        "stage1": {"file_offset": 32, "size": s1, "sha256": sh(stage1),
                   "load_address": "0x%08x" % IRAM_BASE,
                   "reset_vector": "0x%08x" % vt1[0],
                   "vector_entries": 64,
                   "trap_vectors": ["0x%08x" % (IRAM_BASE + 0x130),
                                    "0x%08x" % (IRAM_BASE + 0x134)]},
        "stage2": {"file_offset": 32 + s1, "size": s2size, "sha256": sh(stage2),
                   "load_address": "0x%08x" % s2base,
                   "reset_vector": "0x%08x" % vt2[0],
                   "vector_entries": 64,
                   "distinct_handlers": ["0x%08x" % v for v in sorted(set(vt2[1:]))]},
        "vector_table_sha256": {"stage1": sh(stage1[:256]), "stage2": sh(stage2[:256])},
    }


def parse_binh_image(seg, base, expect_end=None):
    """One BINH flash image: 24-byte header inside the 0x3000 stage1 block."""
    magic, medium, version, s2size, s1size, s1load = struct.unpack_from("<4sIIIII", seg, base)
    # Stored little-endian word reads 0x55AA55AA (public BOOTLOADER_MAGIC_NOR
    # 'AA55AA55' after the SDK's endian swap at image-build time).
    _need(magic == b"BINH" and medium == 0x55AA55AA, "BINH header magic changed")
    _need(s1size == STAGE1_BLOCK and s1load == DRAM_BASE, "BINH stage1 fields changed")
    blk = seg[base:base + STAGE1_BLOCK]
    stored = struct.unpack_from("<I", blk, STAGE1_BLOCK - 4)[0]
    _need(crc32_mpeg2(blk[24:STAGE1_BLOCK - 4]) == stored, "stage1 block CRC mismatch")
    vt = struct.unpack_from("<64I", blk, 24)
    _need(vt[0] == IRAM_BASE + 0x100 and set(vt[1:]) == {IRAM_BASE + 0x130},
          "BINH stage1 vector pattern changed")
    xip_len = struct.unpack_from("<I", seg, base + STAGE1_BLOCK)[0]
    _need(xip_len <= s2size, "xip length exceeds stage2 size")
    s2off = base + STAGE1_BLOCK + 4
    _need(s2off + s2size <= len(seg), "stage2 overruns segment")
    if expect_end is not None:
        _need(s2off + s2size == expect_end, "BINH image no longer ends exactly")
    return {
        "image_offset": base, "soft_version": "0x%08x" % version,
        "stage2_size": s2size, "stage1_block_size": s1size,
        "stage1_load_address": "0x%08x" % s1load,
        "stage1_block_crc32_mpeg2": "0x%08x" % stored,
        "stage2_xip_text_size": xip_len,
        "stage2_offset": s2off, "stage2_end": s2off + s2size,
        "stage1_block_sha256": sh(blk), "stage2_sha256": sh(seg[s2off:s2off + s2size]),
    }


def parse_main_image(seg):
    """Type-2 segment: dual-firmware BINH concatenation for SPI NOR flash."""
    _need(len(seg) == 287808, "main image size changed")
    a = parse_binh_image(seg, 0)
    # Locate every BINH header; exactly one second image is expected.
    hits, pos = [], -1
    while True:
        pos = seg.find(b"BINH", pos + 1)
        if pos < 0:
            break
        hits.append(pos)
    _need(hits == [0, 0x2F3B0], "BINH image set changed")
    b = parse_binh_image(seg, 0x2F3B0, expect_end=len(seg))
    _need(a["soft_version"] == "0x00000203" and b["soft_version"] == "0x00000203",
          "BINH soft versions changed")
    _need(a["stage2_xip_text_size"] == 0x8E84 and b["stage2_xip_text_size"] == 0,
          "XIP split changed")
    extra_off, extra_end = a["stage2_end"], b["image_offset"]
    extra = seg[extra_off:extra_end]
    _need(len(extra) == 129964, "image-A extra payload size changed")
    _need(seg.find(b"0.0.2.3") == 0x96B4, "version string moved")
    return {"image_a": a, "image_b": b,
            "a_extra_payload": {"offset": extra_off, "size": len(extra),
                                "sha256": sh(extra),
                                "identity": "NPU/audio payload (identification-level only)"},
            "version_string_offset": 0x96B4}


def apollo_flash_command_evidence():
    """Pin the Apollo-side DFU `serialdown` call: offset 0, 0x2000 chunks."""
    b = APOLLO.read_bytes()
    _need(sh(b) == APOLLO_SHA256, "apollo image changed")
    _need(sh(DFU_FM.read_bytes()) == DFU_FM_SHA256, "dfu function map changed")
    with DFU_FM.open(newline="", encoding="utf8") as h:
        rows = {r["name"]: r for r in csv.DictReader(h, delimiter="\t")}
    fl = rows["semantic_CodecFlashImage"]
    fs, fe = int(fl["entry"], 16), int(fl["end_exclusive"], 16)
    _need((fs, fe) == (0x005796C8, 0x00579C6A), "flasher bounds changed")

    def at(run, n):
        return b[run - RUN_DELTA:run - RUN_DELTA + n]

    _need(b[0x3435EC:0x3435EC + 20] == b"serialdown %d %d %d\n", "serialdown format changed")
    _need(struct.unpack("<I", at(0x00579FAC, 4))[0] == 0x3435EC + RUN_DELTA,
          "format-string pool word changed")
    # Call site inside semantic_CodecFlashImage:
    #   0x5797DE mov.w r0, #0x2000 / str r0, [sp]   -> chunk argument 0x2000
    #   0x5797E4 ldr r3, [sp, #0x10]                -> firmware image size
    #   0x5797E6 movs r2, #0                        -> flash offset argument 0
    #   0x5797E8 ldr.w r1, [pc, #0x7c0]             -> "serialdown %d %d %d"
    #   0x5797EE bl 0x4B4728                        -> sprintf-like formatter
    pins = {0x005797DE: "4ff40050", 0x005797E2: "0090", 0x005797E4: "049b",
            0x005797E6: "0022", 0x005797E8: "dff8c017", 0x005797EC: "4046",
            0x005797EE: "3af79bff"}
    for run, hexbytes in pins.items():
        _need(at(run, len(hexbytes) // 2).hex() == hexbytes,
              "flash-command call site changed at 0x%08x" % run)
        _need(fs <= run < fe, "call site escaped flasher bounds")
    # The command buffer is the 8-KiB flash-transfer scratch at 0x2035EE18.
    _need(struct.unpack("<I", at(0x005799E4, 4))[0] == 0x2035EE18,
          "command scratch pointer changed")
    return {"command_format": "serialdown %d %d %d",
            "flash_offset_argument": 0, "chunk_argument": 0x2000,
            "size_argument_source": "firmware-image size variable 0x2007493C",
            "command_buffer": "0x2035EE18",
            "call_site": "0x005797EE", "containing_object": "service_codec_dfu.c",
            "containing_function": "semantic_CodecFlashImage"}


MANIFEST_HEADER = ["region", "package_offset", "size", "sha256", "load_address",
                   "destination", "evidence"]


def manifest_rows():
    return [
        ["fwpk_header", "0x00000000", 16, "d43727af93245c0c6f88d780b4553ba97d976d4e296d74778c1f91a27b2917ae",
         "container-only", "FWPK container metadata", "magic/version/record-count parsed and pinned"],
        ["fwpk_records", "0x00000010", 32, "5239fba85a06b9525512f34f075325028bde659ed078daec25a7022b8afc2d29",
         "container-only", "FWPK record table (type1=boot, type2=main)",
         "<type><size><offset><crc32> records; zlib CRC-32 of payloads verified"],
        ["boot_image", "0x00000030", 38236, "393d2ae1f10ed1382f3eec6e3f9f9ac99d744b7ab41d0c89a003f96588afe391",
         "volatile", "streamed over UART during DFU; never flashed",
         "NationalChip grus UART boot container, chip_id 0x8002 (GX8002)"],
        ["boot_header", "0x00000030", 32, "bb0c1a457c4aa90766a38709a1eeef622cf382c1bb1a16f4b058186e2011ad76",
         "host-consumed", "read by Apollo DFU; four BE fields forwarded on wire",
         "public 32-byte boot_header; stage sizes/baud/checksum pinned"],
        ["boot_stage1", "0x00000050", 10240, "cbbe85a2d60f5bb805dddb45fa2eac1632bdf0ab80665c040c0892c64074133f",
         "0x10000000", "codec MCU IRAM (GX8002 on-chip SRAM)",
         "64-word vector table at base; reset 0x10000100; traps 0x10000130/0x10000134"],
        ["boot_stage2", "0x00002850", 27964, "4aacc9e5bf45001bef99785b62302e88bd0b5e6bf4d6186fd7033b1eaeb05b0d",
         "0x10002800", "codec MCU IRAM, immediately after stage1",
         "own 64-word vector table; reset 0x10002900; byte-sum checksum 0x24D441 verified"],
        ["main_image", "0x0000958C", 287808, "60adadb83f3cc544c4f80729b01c20d5f94dc54dcbca254f7e7ca3f45b1b115f",
         "flash+0x00000000", "codec external SPI NOR flash offset 0 (serialdown 0 <size> 8192)",
         "dual-firmware BINH concatenation; Apollo call site pinned"],
        ["binh_a_stage1_block", "0x0000958C", 12288, "9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464",
         "0x10000000", "flash 0x00000000 -> codec MCU IRAM at power-on",
         "24-byte BINH header inside block; vectors at +0x18; CRC-32/MPEG-2 0x21C58EDB verified"],
        ["binh_a_stage2_xip_len", "0x0000C58C", 4, "skip", "container-only",
         "stage2 XIP-text length word 0x00008E84", "public loader_write stage2 header word"],
        ["binh_a_stage2", "0x0000C590", 51200, "2515d7201f82c612cfba7f0c61bb014a0af9fe8b7e9037959f0705b7267850ee",
         "mixed", "flash 0x00003004; XIP text executes from flash (public XIP base 0x10200000); SRAM text/data -> codec IRAM/DRAM",
         "stage2_size 0xC800; XIP text 0x8E84; ends exactly at 0x0000F804 (segment-relative)"],
        ["binh_a_extra_payload", "0x00018D90", 129964, "7bd407a60d16aeb6ad1289184c8d75bad39dc7d7d3704cfea5ce9402e64ec387",
         "unresolved", "flash [0x0000F804, 0x0002F3B0); NPU/audio payload, identification-level only",
         "no header fields in 24-byte BINH format; internal split is a remaining gate"],
        ["binh_b_stage1_block", "0x0003893C", 12288, "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c",
         "0x10000000", "flash 0x0002F3B0 -> codec MCU IRAM (backup/dual-firmware boot path)",
         "second BINH header; CRC-32/MPEG-2 0xA582510C verified; distinct build from image A"],
        ["binh_b_stage2_xip_len", "0x0003B93C", 4, "skip", "container-only",
         "stage2 XIP-text length word 0x00000000 (image B runs fully from SRAM)",
         "public loader_write stage2 header word"],
        ["binh_b_stage2", "0x0003B940", 82060, "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
         "sram-only", "flash 0x000323B4 -> codec SRAM; no XIP",
         "stage2_size 0x1408C; ends exactly at segment end 0x00046440 (exact fit)"],
    ]


def check_manifest():
    _need(MANIFEST.exists(), "segment map manifest missing")
    with MANIFEST.open(newline="", encoding="utf8") as h:
        r = list(csv.reader(h, delimiter="\t"))
    _need(r[0] == MANIFEST_HEADER, "manifest header changed")
    expected = manifest_rows()
    _need(len(r) - 1 == len(expected), "manifest row count changed")
    for got, want in zip(r[1:], expected):
        _need(got == [str(x) for x in want], "manifest row changed: %s" % want[0])


def check_core_source_manifest():
    """Bind the proven codec destinations to the community source profile."""
    source_manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf8"))
    regions = source_manifest["component_overrides"]["codec"]["regions"]
    actual = [
        (
            row["name"], row["file_offset"], row["size"],
            row.get("target"), row.get("target_address"), row["address_status"],
        )
        for row in regions
    ]
    expected = [
        ("fwpk_metadata", 0, 48, None, None, "container_only"),
        ("codec_uart_boot_header", 48, 32, None, None,
         "controller_protocol_metadata"),
        ("codec_uart_boot_stage_1", 80, 10240, "gx8002_iram", 0x10000000,
         "confirmed_from_uart_boot_header_and_vectors"),
        ("codec_uart_boot_stage_2", 10320, 27964, "gx8002_iram", 0x10002800,
         "confirmed_from_uart_boot_header_and_vectors"),
        ("codec_spi_nor_image_a", 38284, 0x2F3B0, "gx8002_spi_nor", 0,
         "confirmed_from_binh_headers_and_apollo_dfu_command"),
        ("codec_spi_nor_image_b", 231740, 94352, "gx8002_spi_nor", 0x2F3B0,
         "confirmed_from_binh_headers_and_apollo_dfu_command"),
    ]
    _need(actual == expected, "core-source codec destination map changed")
    _need(sum(row[2] for row in actual) == CODEC_SIZE,
          "core-source codec regions do not close at EOF")
    _need(not any(row[5] == "unknown" for row in actual),
          "core-source codec destination remains unresolved")
    return {
        "manifest": "manifests/g2-2.2.6.10-core-source.json",
        "regions": len(actual),
        "placed_regions": sum(row[4] is not None for row in actual),
        "protocol_metadata_regions": sum(row[4] is None for row in actual),
        "unresolved_regions": 0,
    }


def analyze():
    blob = CODEC.read_bytes()
    fwpk = parse_fwpk(blob)
    boot = parse_boot_image(blob[48:48 + 38236])
    main = parse_main_image(blob[38284:])
    apollo = apollo_flash_command_evidence()
    check_manifest()
    source_profile = check_core_source_manifest()
    return {
        "schema_version": 1,
        "analysis_mode": "read-only deterministic closure over hash-pinned blobs",
        "blob": {"path": "blobs/official/g2-2.2.6.10/firmware_codec.bin",
                 "size": CODEC_SIZE, "sha256": CODEC_SHA256},
        "fwpk": fwpk,
        "segment_destinations": {
            "type1_boot_image": {
                "volatile": True,
                "stage1": {"load": "0x10000000", "size": 10240,
                           "entry": "0x10000100 (vector[0])"},
                "stage2": {"load": "0x10002800", "size": 27964,
                           "entry": "0x10002900 (vector[0])"},
                "region": "GX8002 on-chip MCU IRAM (base 0x10000000)"},
            "type2_main_image": {
                "volatile": False,
                "flash_offset": 0, "size": 287808,
                "region": "GX8002 external SPI NOR flash",
                "image_a": {"flash": "[0x0, 0x2F3B0)",
                            "stage1_block": "flash 0x0, 0x3000 B -> IRAM 0x10000000",
                            "stage2": "flash 0x3004, 0xC800 B; XIP text 0x8E84 B",
                            "extra_payload": "flash [0xF804, 0x2F3B0), 129964 B"},
                "image_b": {"flash": "[0x2F3B0, 0x46440)",
                            "stage1_block": "flash 0x2F3B0, 0x3000 B -> IRAM 0x10000000",
                            "stage2": "flash 0x323B4, 0x1408C B; no XIP (SRAM only)"}}},
        "boot_image": boot,
        "main_image": main,
        "memory_constants": {"iram_base": "0x10000000", "dram_base": "0x20000000",
                             "flash_xip_base_public_default": "0x10200000",
                             "stage1_block_size": 12288},
        "protocol": {
            "wire_format_owner": "NationalChip public grus UART boot/serialdown protocol "
                                 "(MIT-licensed lvp_kws/lvp_sed uart_sendboot.c); "
                                 "Apollo implementation is Even first-party service_codec_dfu.c; "
                                 "codec-side stage2 CLI remains proprietary NationalChip",
            "boot_stage1_baud": 230400, "boot_stage2_baud": 1500000,
            "flash_command": apollo},
        "community_source_profile": source_profile,
        "production": {"production_routed": False,
                       "codec_image_ownership": "proprietary NationalChip boundary; "
                                                "container/interface facts only, zero claimed source"},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))

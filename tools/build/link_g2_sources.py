#!/usr/bin/env python3
"""Strictly link the seven G2 source-build relocatables into payload images.

The input is a completed ``sources.py build --device g2`` report. This link
does not prove source completeness or hardware behavior. Apollo main uses a typographic C reconstruction of the stock Nordic
nrf_fuel_gauge (c205a2) algorithm, verified bit-exact versus typographic
stock on Renode 1.17 M55; hardware calibration and device behavior remain
unproven.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from em9305_record2 import APP_BASE, NVM_BASE, split_bootloader_image
from source_providers import functions as source_functions


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "g2/tools/em9305_source_image"))
from record_package import Record, build_package, parse_package  # noqa: E402
sys.path.insert(0, str(ROOT / "g2/tools"))
from build_kws_command_stream import build_stream as build_kws_command_stream  # noqa: E402
from open_cfw import (  # noqa: E402
    assemble_evenota, validate_apollo_main, validate_case, wrap_case_image, wrap_codec_binh_a,
    wrap_codec_binh_b, wrap_codec_fwpk, wrap_codec_uart_boot, wrap_main_image,
    wrap_touch_source_image,
)
PAYLOADS = (
    "g2-apollo-bootloader", "g2-apollo-main", "g2-case", "g2-codec-a",
    "g2-codec-b", "g2-em9305", "g2-touch",
)
ARC_TOOL = Path("vendor-cache/g2/arc-gnu-2026.03/toolchain/arc_gnu_prebuilt_elf32_le_linux_install/arc-multilib-elf32")
CSKY_TOOL = Path("vendor-cache/g2/csky-abiv2-gcc-6.3")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(argv: list[str], log: Path) -> None:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    with log.open("a") as stream:
        stream.write("$ " + " ".join(argv) + "\n")
        stream.write(result.stdout)
        stream.write(result.stderr)
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}; see {log}")


def source_object(source_out: Path, payload: str, summary: dict) -> Path:
    compose = summary.get("compose") or {}
    if summary["failed"] or summary["known_failures"] or summary["now_compiling"]:
        raise RuntimeError(f"{payload}: source compilation was not clean")
    if summary["duplicate_strong_symbols"] or compose.get("returncode") != 0:
        raise RuntimeError(f"{payload}: composition was not clean")
    obj = source_out / "g2" / payload / f"{payload}.o"
    if not obj.is_file() or digest(obj) != compose.get("sha256"):
        raise RuntimeError(f"{payload}: composed object is missing or changed: {obj}")
    return obj


def codec_b_stage1_objects(source_out: Path, report: dict) -> list[Path]:
    """The BINH B boot block is compiled separately from the stage-2 object."""
    rows = [row for row in report["devices"]["g2"]["units"]
            if row["source"].startswith("g2/src/codec/image-b-stage1/")]
    if len(rows) != 11:
        raise RuntimeError(f"codec B stage-1 unit set changed: {len(rows)}")
    expected_dir = source_out / "g2/g2-codec-b"
    objects = []
    for row in rows:
        obj = Path(row["object"])
        if (row["payload"] != "g2-codec-b" or row["link"] is not False
                or row["returncode"] != 0 or obj.parent != expected_dir
                or not obj.is_file() or digest(obj) != row["object_sha256"]):
            raise RuntimeError(f"codec B stage-1 object is not a verified compile: {row['source']}")
        objects.append(obj)
    return objects


def codec_a_weights_from_source(source_out: Path, report: dict) -> tuple[bytes, dict]:
    """Read only the named, C-compiled non-executable model data symbol."""
    source = "g2/src/codec/npu/kws_weights_source.c"
    rows = [row for row in report["devices"]["g2"]["units"]
            if row["source"] == source]
    if len(rows) != 1:
        raise RuntimeError(f"codec A weight C unit count changed: {len(rows)}")
    row = rows[0]
    obj = Path(row["object"])
    expected_dir = source_out / "g2/g2-codec-a"
    if (row["payload"] != "g2-codec-a" or row["link"] is not False
            or row["returncode"] != 0 or obj.parent != expected_dir
            or not obj.is_file() or digest(obj) != row["object_sha256"]):
        raise RuntimeError("codec A weight C object is not a verified compile")
    symbols = [symbol for symbol in source_functions(obj, include_objects=True)
               if symbol["symbol"] == "g2_kws_weights_source"]
    if len(symbols) != 1:
        raise RuntimeError("codec A compiled weight symbol is missing or ambiguous")
    symbol = symbols[0]
    if (symbol["machine"] != 252 or symbol["symbol_kind"] != "data"
            or symbol["section"] != ".g2_kws_weights" or symbol["executable"]
            or symbol["writable"] or symbol["relocations"]
            or symbol["size"] != 0x1D7E0 or len(symbol["data"]) != 0x1D7E0):
        raise RuntimeError("codec A compiled weight section is not immutable data of the locked size")
    return symbol["data"], {
        "source": source, "object": str(obj.relative_to(ROOT)),
        "object_sha256": row["object_sha256"], "section": symbol["section"],
        "symbol": symbol["symbol"], "bytes": symbol["size"],
        "sha256": hashlib.sha256(symbol["data"]).hexdigest(),
    }


def codec_a_binh_stage1_objects(source_out: Path, report: dict) -> list[Path]:
    """Verify the separately compiled BINH A boot block candidates."""
    rows = [row for row in report["devices"]["g2"]["units"]
            if row["source"].startswith("g2/src/codec/image-a-stage1/")]
    if len(rows) != 9:
        raise RuntimeError(f"codec A BINH stage-1 unit set changed: {len(rows)}")
    expected_dir = source_out / "g2/g2-codec-a"
    objects = []
    for row in rows:
        obj = Path(row["object"])
        if (row["payload"] != "g2-codec-a" or row["link"] is not False
                or row["returncode"] != 0 or obj.parent != expected_dir
                or not obj.is_file() or digest(obj) != row["object_sha256"]):
            raise RuntimeError(
                f"codec A BINH stage-1 object is not a verified compile: {row['source']}")
        objects.append(obj)
    return objects


def check_inputs(source_out: Path, report: dict) -> None:
    g2 = report["devices"]["g2"]
    if g2["manifest_changed_during_build"]:
        raise RuntimeError("manifest changed during source compilation")
    if digest(ROOT / "g2/src/sources.json") != g2["manifest_sha256"]:
        raise RuntimeError("G2 source manifest changed since compilation")
    stage1_clock_header = ROOT / "g2/src/codec/image-a-stage1/clk_priv_stage1.h"
    if digest(stage1_clock_header) != "09778135f1c0ffd7f969904ddf0443658464c7810fc4e3cdd5e450c35dbba2c2":
        raise RuntimeError("codec A stage-1 clock header changed since qualification")
    for row in g2["units"]:
        source = row["source"]
        path = (source_out / "generated/g2" / source[6:]) if source.startswith("{gen}/") else ROOT / source
        if not path.is_file() or digest(path) != row["source_sha256"]:
            raise RuntimeError(f"source changed since compilation: {source}")


def arm_link(payload: str, obj: Path, out: Path, log: Path) -> None:
    if payload == "g2-apollo-main":
        script = "g2/src/apollo-main/link/g2-apollo-main.ld"
        cpu = ["-mcpu=cortex-m55", "-mthumb", "-mfloat-abi=hard", "-mfpu=fpv5-d16"]
        extras = []
    elif payload == "g2-apollo-bootloader":
        script = "g2/src/apollo-bootloader/link/g2-apollo-bootloader.ld"
        cpu = ["-mcpu=cortex-m55", "-mthumb", "-mfloat-abi=hard", "-mfpu=fpv5-d16"]
        rom = out / "resident_rom_thumb_set.o"
        run(["arm-none-eabi-gcc", "-mcpu=cortex-m55", "-mthumb", "-c",
             "g2/src/apollo-bootloader/link/resident_rom_thumb_set.c", "-o", str(rom)], log)
        undefined = subprocess.run(["arm-none-eabi-nm", "-u", str(obj)], cwd=ROOT,
                                   capture_output=True, text=True, check=True).stdout
        if "opencfw_boot_rom" not in undefined:
            weak = out / "g2-apollo-bootloader.weakrom.o"
            run(["arm-none-eabi-objcopy", "--weaken-symbol=opencfw_boot_rom48",
                 "--weaken-symbol=opencfw_boot_rom_delay_cycles",
                 "--weaken-symbol=opencfw_boot_rom_mram_program", str(obj), str(weak)], log)
            obj = weak
        extras = [str(rom)]
    elif payload == "g2-case":
        script = "g2/src/case/link/g2-case.ld"
        cpu = ["-mcpu=cortex-m0plus", "-mthumb", "-mfloat-abi=soft"]
        extras = []
    else:
        script = "g2/src/touch/link/g2-touch.ld"
        cpu = ["-mcpu=cortex-m0plus", "-mthumb"]
        extras = []
    # apollo-main: --gc-sections is safe with KEEP on vectors, kvdb_migration,
    # ITCM/ramfunc, the OTA flag page, and bond records. The image must still
    # end at or before MAIN_UPDATE_FLAG 0x007FE000 (wrap_main_image / ASSERT).
    gc_sections = ["-Wl,--gc-sections"]
    run(["arm-none-eabi-gcc", *cpu, "-nostartfiles", "-nostdlib", "-T", script,
         f"-Wl,-Map={out / (payload + '.map')}", "-Wl,--no-warn-rwx-segments",
         *gc_sections, "-o", str(out / f"{payload}.elf"), str(obj), *extras, "-lgcc"], log)
    run(["arm-none-eabi-objcopy", "-O", "binary", str(out / f"{payload}.elf"),
         str(out / f"{payload}.bin")], log)


def docker_link(payload: str, obj: Path, out: Path, log: Path,
                stage1_objects: list[Path] | None = None) -> None:
    codec = payload.startswith("g2-codec-")
    tool = (ROOT / (CSKY_TOOL if codec else ARC_TOOL)).resolve()
    if not tool.is_dir():
        raise RuntimeError(f"missing toolchain: {tool}")
    prefix = "csky-abiv2-elf" if codec else "arc-elf32"
    script = f"g2/src/{'codec' if codec else 'em9305'}/link/{payload}.ld"
    common = ["docker", "run", "--rm", "--network=none", "--platform", "linux/amd64",
              "-v", f"{tool}:/tool:ro", "-v", f"{ROOT}:/work", "-w", "/work",
              "opencfw/iar-base:10.10.2-local"]
    rel_obj = obj.relative_to(ROOT)
    rel_out = out.relative_to(ROOT)
    extras = []
    if payload == "g2-codec-b":
        if not stage1_objects:
            raise RuntimeError("codec B stage-1 source objects are required")
        stage1_obj = rel_out / f"{payload}-stage1.o"
        run([*common, f"/tool/bin/{prefix}-ld", "-r", "-o",
             f"/work/{stage1_obj}",
             *(f"/work/{path.relative_to(ROOT)}" for path in stage1_objects)], log)
        extras.append(f"/work/{stage1_obj}")
    run([*common, f"/tool/bin/{prefix}-gcc", "-nostartfiles", "-nostdlib",
         "-T", script, f"-Wl,-Map=/work/{rel_out / (payload + '.map')}",
         "-o", f"/work/{rel_out / (payload + '.elf')}", f"/work/{rel_obj}",
         *extras, "-lgcc"], log)
    run([*common, f"/tool/bin/{prefix}-objcopy", "-O", "binary",
         f"/work/{rel_out / (payload + '.elf')}",
         f"/work/{rel_out / (payload + '.bin')}"], log)
    if payload == "g2-codec-a":
        stages = {
            "stage1": (".stage1.vectors", ".stage1.reset", ".stage1.traps",
                       ".stage1.irq_traps", ".stage1", ".stage1.data"),
            "stage2": (".stage2.vectors", ".stage2.reset", ".stage2.trap",
                       ".stage2.irq", ".stage2"),
            "image-a-xip": (".xip",),
            "image-a-sram": (".res.vectors", ".res.reset", ".res.clear_bss",
                             ".res.system_initialize", ".res.trap_c",
                             ".res.trap", ".res.pre_irq", ".res.irq",
                             ".res.text",
                             ".pin.gx8002.*", ".res.data"),
        }
        for name, sections in stages.items():
            run([*common, f"/tool/bin/{prefix}-objcopy", "-O", "binary",
                 *(f"--only-section={section}" for section in sections),
                 f"/work/{rel_out / (payload + '.elf')}",
                 f"/work/{rel_out / (payload + '-' + name + '.bin')}"], log)
    if payload == "g2-codec-b":
        stages = {
            "stage1": (".spl.vectors", ".spl.reset", ".spl.default",
                       ".spl.text", ".spl.data"),
            "stage2": (".vectors", ".text", ".data"),
        }
        for name, sections in stages.items():
            run([*common, f"/tool/bin/{prefix}-objcopy", "-O", "binary",
                 *(f"--only-section={section}" for section in sections),
                 f"/work/{rel_out / (payload + '.elf')}",
                 f"/work/{rel_out / (payload + '-' + name + '.bin')}"], log)
    if payload == "g2-em9305":
        flat = out / f"{payload}.bin"
        bootloader_path = out / f"{payload}-bootloader.bin"
        run([*common, f"/tool/bin/{prefix}-objcopy", "-O", "binary",
             "--only-section=.nvm_bootloader", f"/work/{rel_out / (payload + '.elf')}",
             f"/work/{rel_out / bootloader_path.name}"], log)
        bootloader, record2, application = split_bootloader_image(
            flat.read_bytes(), bootloader_path.read_bytes())
        bootloader_path.write_bytes(bootloader)
        (out / f"{payload}-record2.bin").write_bytes(record2)
        flat.write_bytes(application)
        last_page = (APP_BASE + len(application) - NVM_BASE + 0x1FFF) // 0x2000
        package = build_package((Record(NVM_BASE, bootloader),
                                 Record(0x00302000, record2),
                                 Record(APP_BASE, application)), range(last_page))
        if len(parse_package(package).records) != 3:
            raise RuntimeError("EM9305 source package did not round-trip")
        (out / f"{payload}-source-candidate-package.bin").write_bytes(package)


def link_codec_a_binh_stage1(source_out: Path, report: dict,
                             out: Path, resident_elf: Path, log: Path) -> dict:
    """Link BINH A's C boot block apart from the overlapping UART boot image."""
    symbol = "gx8002_resident_reset_entry_23500"
    symbols = subprocess.run(["arm-none-eabi-readelf", "-Ws", str(resident_elf)],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    if not any((fields := line.split()) and len(fields) >= 8
               and fields[-1] == symbol and fields[6] != "UND"
               and int(fields[1], 16) == 0x10023500
               for line in symbols.splitlines()):
        raise RuntimeError("codec A source SRAM reset is not at 0x10023500")

    objects = codec_a_binh_stage1_objects(source_out, report)
    tool = (ROOT / CSKY_TOOL).resolve()
    if not tool.is_dir():
        raise RuntimeError(f"missing toolchain: {tool}")
    common = ["docker", "run", "--rm", "--network=none", "--platform", "linux/amd64",
              "-v", f"{tool}:/tool:ro", "-v", f"{ROOT}:/work", "-w", "/work",
              "opencfw/iar-base:10.10.2-local"]
    rel = out.relative_to(ROOT)
    combined = rel / "g2-codec-a-binh-stage1.o"
    elf = rel / "g2-codec-a-binh-stage1.elf"
    binary = rel / "g2-codec-a-binh-stage1.bin"
    run([*common, "/tool/bin/csky-abiv2-elf-ld", "-r", "-o",
         f"/work/{combined}",
         *(f"/work/{path.relative_to(ROOT)}" for path in objects)], log)
    run([*common, "/tool/bin/csky-abiv2-elf-gcc", "-nostartfiles", "-nostdlib",
         "-T", "g2/src/codec/link/g2-codec-a-binh-stage1.ld",
         f"-Wl,--defsym={symbol}=0x10023500",
         f"-Wl,-Map=/work/{rel / 'g2-codec-a-binh-stage1.map'}",
         "-o", f"/work/{elf}", f"/work/{combined}", "-lgcc"], log)
    check_undefined(out / elf.name)
    run([*common, "/tool/bin/csky-abiv2-elf-objcopy", "-O", "binary",
         f"/work/{elf}", f"/work/{binary}"], log)
    image = (out / binary.name).read_bytes()
    if not 0x1294 <= len(image) <= 0x2fe4:
        raise RuntimeError("codec A BINH stage-1 load exceeds the locked block")
    vectors_sha = digest_bytes(image[:0x100])
    data_sha = digest_bytes(image[0x1028:0x1294])
    if vectors_sha != "328d3b985051f93c8159432d043fbcbedc07bf903169996aa7ee625f2dbe9494":
        raise RuntimeError("codec A BINH stage-1 vector table differs from stock")
    if data_sha != "da1c34af1cb2d69320f92ff98edf797243ceeb4414605983611c35e32a756c3a":
        raise RuntimeError("codec A BINH stage-1 initialized data differs from stock")
    exact_c_ranges = (
        (0x138, 18, "e2046581f41222befb24ceaa43d1781b3656b996b9ad822fcb8b778994f331a7"),
        (0x14c, 20, "52175e4de21f4f4eec23119a8b607fd27be6b6dc67fc27d07cbb3c2256021a12"),
        (0x160, 164, "0f629a6637a1530cddcce97a8fb48fbc376e7a17d48a89db9abb59509cda38b5"),
        (0x204, 28, "12ef96242448f65f16211ffa85d455f2beba409320f72f8e2f2779d277470c4a"),
        (0x5a4, 256, "67072a3913d54f83fd76a07d8bbfd306e2e5e99534a5b27dff344355ae63b4cc"),
        (0xb40, 254, "031cbefa0922339d31cd872fffdc24737c3ce0083a7f8356ec03a647cf46c3bd"),
    )
    for offset, length, expected_sha in exact_c_ranges:
        if digest_bytes(image[offset:offset + length]) != expected_sha:
            raise RuntimeError(f"codec A BINH stage-1 C bytes changed at 0x{offset:04x}")
    # The 0xe0-byte switch-table region matches the locked load once branch
    # targets in the C-compiled clock-frequency function are translated to
    # their equivalent locked blocks. Each mapped block was checked against
    # the two disassemblies for the same action (module lookup, module 16/22/
    # 10/19 selection, or zero result). All other table bytes must stay exact.
    clock_table = bytearray(image[0xf48:0x1028])
    stock_clock_table_sha = "602f0b8d59ef20ef49612aebf98bd30739e4eea6269beb66d08357bac2f768b4"
    clock_target_map = {
        0x10000840: 0x1000083c,  # zero result
        0x100006bc: 0x100006be,  # common module lookup
        0x100007d6: 0x100006bc,  # select module 16
        0x100007da: 0x100007d6,  # select module 22
        0x100007de: 0x100007da,  # select module 10
        0x100007e2: 0x100007de,  # select module 19
    }
    relocated_words = 0
    for offset in range(0, len(clock_table), 4):
        word = int.from_bytes(clock_table[offset:offset + 4], "little")
        stock_target = clock_target_map.get(word)
        if stock_target is not None:
            clock_table[offset:offset + 4] = stock_target.to_bytes(4, "little")
            relocated_words += 1
    normalized_clock_table_sha = digest_bytes(clock_table)
    if relocated_words != 19 or normalized_clock_table_sha != stock_clock_table_sha:
        raise RuntimeError("codec A BINH stage-1 clock switch table differs from stock after target mapping")
    return {"elf_sha256": digest(out / elf.name), "binary_sha256": digest(out / binary.name),
            "linked_bytes": len(image), "stock_load_limit": 0x2fe4,
            "stock_vectors_sha256": vectors_sha,
            "stock_initialized_data_sha256": data_sha,
            "stock_identical_c_ranges": [
                {"offset": offset, "bytes": length, "sha256": expected_sha}
                for offset, length, expected_sha in exact_c_ranges
            ],
            "clock_switch_table": {"offset": 0xf48, "bytes": 0xe0,
                                   "mapped_target_words": relocated_words,
                                   "normalized_sha256": normalized_clock_table_sha,
                                   "matches_locked_table_after_target_mapping": True},
            "qualification": "separately linked C BINH A boot candidate; vectors, 0x26c initialized data, and six C-generated code ranges match stock, but remaining code, full BINH A package, byte identity, and hardware boot remain unverified"}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_undefined(elf: Path) -> None:
    result = subprocess.run(["arm-none-eabi-readelf", "-Ws", str(elf)], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    names = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[6] == "UND":
            names.append(fields[7])
    if names:
        raise RuntimeError(f"{elf}: undefined symbols: {', '.join(names[:20])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-out", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--payload", choices=PAYLOADS, action="append")
    parser.add_argument("--codec-a-weights", type=Path,
                        help="declared 120800-byte NPU weight asset for a codec candidate")
    parser.add_argument("--codec-a-weights-from-source", action="store_true",
                        help="use the verified C-compiled KWS weight data unit")
    parser.add_argument("--codec-a-weights-provenance", type=Path,
                        help="JSON provenance for --codec-a-weights; recorded in the link receipt")
    parser.add_argument("--bundle-candidate", action="store_true",
                        help="assemble all seven linked payloads into a six-component G2 OTA candidate")
    args = parser.parse_args()
    if args.codec_a_weights and args.codec_a_weights_from_source:
        parser.error("choose either external or C-compiled codec A weights")
    if bool(args.codec_a_weights or args.codec_a_weights_from_source) != bool(args.codec_a_weights_provenance):
        parser.error("codec A weights and their provenance must be supplied together")
    source_out = args.source_out.resolve()
    out_root = args.out.resolve()
    if not source_out.is_relative_to(ROOT) or not out_root.is_relative_to(ROOT):
        parser.error("input and output directories must be inside the repository")
    report_path = source_out / "report.json"
    report = json.loads(report_path.read_text())
    check_inputs(source_out, report)
    selected = args.payload or PAYLOADS
    if args.bundle_candidate and not (args.codec_a_weights or args.codec_a_weights_from_source):
        parser.error("--bundle-candidate requires declared codec A weights")
    if args.bundle_candidate and set(selected) != set(PAYLOADS):
        parser.error("--bundle-candidate requires all seven G2 source payloads")
    if (args.codec_a_weights or args.codec_a_weights_from_source) and "g2-codec-a" not in selected:
        parser.error("--codec-a-weights requires the g2-codec-a payload")
    weights = None
    weights_source_info = None
    weights_provenance = None
    if args.codec_a_weights or args.codec_a_weights_from_source:
        provenance_path = args.codec_a_weights_provenance.resolve()
        if not provenance_path.is_file():
            parser.error("codec A weight provenance must be an existing file")
        if args.codec_a_weights_from_source:
            weights, weights_source_info = codec_a_weights_from_source(source_out, report)
        else:
            weight_path = args.codec_a_weights.resolve()
            if not weight_path.is_file():
                parser.error("codec A weights must be an existing file")
            weights = weight_path.read_bytes()
        if len(weights) != 0x1D7E0:
            parser.error("codec A NPU weights must be exactly 120800 bytes")
        try:
            weights_provenance = json.loads(provenance_path.read_text())
        except (OSError, ValueError) as error:
            parser.error(f"invalid codec A weight provenance JSON: {error}")
        if not isinstance(weights_provenance, dict) or weights_provenance.get("sha256") != digest_bytes(weights):
            parser.error("codec A weight provenance must declare the matching sha256")
    results = {}
    for payload in selected:
        obj = source_object(source_out, payload, report["devices"]["g2"]["payloads"][payload])
        out = out_root / payload
        out.mkdir(parents=True, exist_ok=True)
        log = out / "link.log"
        log.write_text("")
        if payload in ("g2-apollo-main", "g2-apollo-bootloader", "g2-case", "g2-touch"):
            arm_link(payload, obj, out, log)
        else:
            stage1 = codec_b_stage1_objects(source_out, report) if payload == "g2-codec-b" else None
            docker_link(payload, obj, out, log, stage1)
        elf, binary = out / f"{payload}.elf", out / f"{payload}.bin"
        check_undefined(elf)
        results[payload] = {"elf_sha256": digest(elf), "binary_sha256": digest(binary),
                            "binary_bytes": binary.stat().st_size}
        if payload == "g2-codec-a":
            results[payload]["binh_a_stage1_source"] = link_codec_a_binh_stage1(
                source_out, report, out, elf, log)
            stage1 = out / f"{payload}-stage1.bin"
            stage2 = out / f"{payload}-stage2.bin"
            xip = out / f"{payload}-image-a-xip.bin"
            sram = out / f"{payload}-image-a-sram.bin"
            sram_image = sram.read_bytes()
            if len(sram_image) != 0x397C:
                raise RuntimeError("codec A image-A SRAM differs from the locked span")
            sram_vectors_sha = digest_bytes(sram_image[:0x100])
            if sram_vectors_sha != "d0d1997111e51a07aa63535beffd7d3a0de741c39cd9915aed1ac87b6b978f1a":
                raise RuntimeError("codec A image-A SRAM vectors differ from stock")
            uart = out / f"{payload}-uart-source-candidate.bin"
            uart.write_bytes(wrap_codec_uart_boot(stage1.read_bytes(), stage2.read_bytes()))
            results[payload]["uart_boot"] = {
                "bytes": uart.stat().st_size, "sha256": digest(uart),
                "stage1_linked_bytes": stage1.stat().st_size,
                "stage2_linked_bytes": stage2.stat().st_size,
                "qualification": "source-linked UART stages with fixed-size padding and checksummed boot header; stock equivalence and hardware boot unverified"}
            npu_commands = build_kws_command_stream()
            npu_commands_sha = digest_bytes(npu_commands)
            if npu_commands_sha != "c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9":
                raise RuntimeError("codec A C-authored NPU commands differ from the locked stream")
            npu_source = out / f"{payload}-npu-commands-source.bin"
            npu_source.write_bytes(npu_commands)
            results[payload]["npu_command_source"] = {
                "bytes": len(npu_commands), "sha256": npu_commands_sha,
                "command_count": 212, "matches_locked_command_sha256": True,
                "qualification": "field-level C-authored NPU command region; separate from the linked executable and incomplete without trained weights"}
            results[payload]["binh_a_source_regions"] = {
                "xip_linked_bytes": xip.stat().st_size,
                "xip_sha256": digest(xip),
                "xip_stock_limit": 0x8E84,
                "sram_linked_bytes": sram.stat().st_size,
                "sram_sha256": digest(sram),
                "sram_stock_limit": 0x397C,
                "sram_vectors_sha256": sram_vectors_sha,
                "sram_vectors_match_stock": True,
                "fits_stock_stage2": xip.stat().st_size <= 0x8E84
                and sram.stat().st_size <= 0x397C,
                "qualification": "source-linked BINH A stage-2 XIP and SRAM fit stock size limits, with stock-identical SRAM vectors and a separate C stage-1 candidate; the C-authored NPU command region is separately emitted and matches stock, while trained weights, complete BINH A byte identity, and hardware boot remain unresolved"}
            if weights is not None:
                stage1_a = out / f"{payload}-binh-stage1.bin"
                image_a = out / f"{payload}-binh-source-candidate.bin"
                image_a.write_bytes(wrap_codec_binh_a(
                    stage1_a.read_bytes(), xip.read_bytes(), sram_image,
                    npu_commands, weights))
                results[payload]["binh_a_source_candidate"] = {
                    "bytes": image_a.stat().st_size, "sha256": digest(image_a),
                    "weight_bytes": len(weights), "weight_sha256": digest_bytes(weights),
                    "weight_origin": "C-compiled data unit" if args.codec_a_weights_from_source else "declared external data asset",
                    "weight_source": weights_source_info,
                    "weight_provenance_sha256": digest(args.codec_a_weights_provenance.resolve()),
                    "weight_provenance": weights_provenance,
                    "qualification": "source-linked code and C-authored commands with verified weight data; byte identity, model provenance, and hardware behavior are not inferred"}
        if payload == "g2-codec-b":
            stage1 = out / f"{payload}-stage1.bin"
            stage2 = out / f"{payload}-stage2.bin"
            binh = out / f"{payload}-binh-source-candidate.bin"
            binh.write_bytes(wrap_codec_binh_b(stage1.read_bytes(), stage2.read_bytes()))
            results[payload]["binh_b_source"] = {
                "stage1_linked_bytes": stage1.stat().st_size,
                "stage1_sha256": digest(stage1),
                "stage2_linked_bytes": stage2.stat().st_size,
                "stage2_sha256": digest(stage2),
                "package_bytes": binh.stat().st_size,
                "package_sha256": digest(binh),
                "qualification": "separately linked C BINH B boot block and SRAM image with computed header CRC; stock equivalence and hardware boot unverified"}
        if payload in ("g2-apollo-main", "g2-case"):
            raw = binary.read_bytes()
            wrapped = wrap_main_image(raw) if payload == "g2-apollo-main" else wrap_case_image(raw)
            (validate_apollo_main if payload == "g2-apollo-main" else validate_case)(wrapped)
            package = out / f"{payload}-source-candidate-package.bin"
            package.write_bytes(wrapped)
            results[payload]["package"] = {
                "bytes": len(wrapped), "sha256": digest(package),
                "qualification": "source-linked image with verified OTA wrapper; hardware boot unverified"}
        if payload == "g2-touch":
            package = out / f"{payload}-source-candidate-package.bin"
            package.write_bytes(wrap_touch_source_image(binary.read_bytes()))
            results[payload]["package"] = {
                "bytes": package.stat().st_size, "sha256": digest(package),
                "qualification": "source-linked touch image with calculated DFU footer and FWPK wrapper; hardware boot unverified"}
        if payload == "g2-em9305":
            bootloader = out / f"{payload}-bootloader.bin"
            record2 = out / f"{payload}-record2.bin"
            results[payload]["bootloader"] = {
                "target": "0x00300000", "bytes": bootloader.stat().st_size,
                "sha256": digest(bootloader),
                "qualification": "source-owned NVM boot path; stock equivalence and hardware boot unverified"}
            results[payload]["record2"] = {
                "target": "0x00302000", "bytes": record2.stat().st_size,
                "sha256": digest(record2),
                "qualification": "C header and NVM entry; finalized CRCs"}
            package = out / f"{payload}-source-candidate-package.bin"
            results[payload]["package"] = {
                "records": 3, "bytes": package.stat().st_size,
                "sha256": digest(package),
                "qualification": "source-produced candidate only; not stock-identical or hardware-qualified"}
        print(f"{payload}: linked {results[payload]['binary_bytes']} bytes", flush=True)
    if weights is not None and "g2-codec-b" in results:
        codec_a = out_root / "g2-codec-a"
        codec_b = out_root / "g2-codec-b"
        fwpk = codec_a / "g2-codec-a-fwpk-source-candidate.bin"
        fwpk.write_bytes(wrap_codec_fwpk(
            (codec_a / "g2-codec-a-uart-source-candidate.bin").read_bytes(),
            (codec_a / "g2-codec-a-binh-source-candidate.bin").read_bytes(),
            (codec_b / "g2-codec-b-binh-source-candidate.bin").read_bytes()))
        results["g2-codec-a"]["fwpk_source_candidate"] = {
            "bytes": fwpk.stat().st_size, "sha256": digest(fwpk),
            "qualification": "source-linked codec regions with verified weight data; not byte-identical or hardware-qualified"}
    bundle_receipt = None
    if args.bundle_candidate:
        manifest_path = ROOT / "g2/manifests/g2-2.2.6.10.json"
        manifest = json.loads(manifest_path.read_text())
        component_files = {
            "codec": out_root / "g2-codec-a/g2-codec-a-fwpk-source-candidate.bin",
            "ble_em9305": out_root / "g2-em9305/g2-em9305-source-candidate-package.bin",
            "touch": out_root / "g2-touch/g2-touch-source-candidate-package.bin",
            "case": out_root / "g2-case/g2-case-source-candidate-package.bin",
            "apollo_bootloader": out_root / "g2-apollo-bootloader/g2-apollo-bootloader.bin",
            "apollo_main": out_root / "g2-apollo-main/g2-apollo-main-source-candidate-package.bin",
        }
        components = {name: path.read_bytes() for name, path in component_files.items()}
        bundle, entries = assemble_evenota(manifest, components)
        bundle_path = out_root / "g2-source-candidate.evenota.bin"
        bundle_path.write_bytes(bundle)
        bundle_sha = digest_bytes(bundle)
        bundle_receipt = {
            "bytes": len(bundle), "sha256": bundle_sha,
            "source_completeness_proven": False,
            "locked_target_bytes": manifest["package"]["expected_size"],
            "locked_target_sha256": manifest["package"]["expected_sha256"],
            "matches_locked_target": (len(bundle) == manifest["package"]["expected_size"]
                                      and bundle_sha == manifest["package"]["expected_sha256"]),
            "manifest_sha256": digest(manifest_path),
            "components": [
                {"name": entry.filename, "bytes": entry.payload_size,
                 "sha256": digest_bytes(components[component["name"]])}
                for component, entry in zip(manifest["components"], entries)
            ],
            "qualification": "six-component source-candidate OTA using verified codec weight data; structure validated, source completeness and device behavior unproven",
        }
    receipt = {"schema": 1, "source_completeness_proven": False,
               "source_report_sha256": digest(report_path),
               "manifest_sha256": report["devices"]["g2"]["manifest_sha256"],
               "external_binary_archive_used": False,
               "binary_fuel_gauge_sha256": None,
               "payloads": results,
               "qualification": "Compilation and final linkage of all seven source payload groups, plus a separately emitted C-authored codec A NPU command region. Codec B is source-linked; complete codec packaging requires verified weight input. Stock equivalence and hardware boot remain unproven. EM9305 bootloader is a C candidate spanning stock records 0 and 1; fuel gauge is typographic C, bit-exact versus typographic stock on Renode 1.17 M55 (hardware calibration unproven); whole-artifact C completeness remains unproven."}
    if bundle_receipt is not None:
        receipt["g2_bundle_source_candidate"] = bundle_receipt
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "link-report.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"report: {out_root / 'link-report.json'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, RuntimeError, ValueError) as error:
        print(f"link_g2_sources: {error}", file=sys.stderr)
        sys.exit(1)

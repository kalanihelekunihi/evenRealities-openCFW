#!/usr/bin/env python3
"""Source-only image-B ELF placement probe with explicit resident contracts."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
SCRIPT = HERE / "image_b_flexible_layout_probe.ld"
EXCLUDE = {
    "backup_clock_tables.c", "backup_clock_module_select.c",
    "backup_clock_frequency.c", "backup_platform_gate.c",
    "backup_initialized_runtime_data.c", "backup_fft_profile_data.c",
}
RESIDENT = {}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def target(name: str, out: Path, args: list[str]) -> str:
    command = ["docker", "run", "--rm", "--network=none", "--read-only",
               "--platform", "linux/amd64",
               "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
               "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
               "--mount", f"type=bind,src={out},dst=/out",
               "--tmpfs", "/tmp:rw", "opencfw/iar-base:10.10.2-local",
               f"/tool/bin/csky-abiv2-elf-{name}", *args]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:] or result.stdout[-4000:])
    return result.stdout + result.stderr

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selected-receipt", type=Path, required=True)
    parser.add_argument("--partial-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--script", type=Path,
                        help="explicit experimental linker script")
    args = parser.parse_args()
    script = args.script.resolve() if args.script else SCRIPT
    selected = json.loads(args.selected_receipt.read_text())
    partial = json.loads(args.partial_receipt.read_text())
    if partial["selected_receipt_sha256"] != sha(args.selected_receipt):
        raise RuntimeError("partial link used a different selected source snapshot")
    if partial["linker_script_sha256"] != sha(script):
        raise RuntimeError("linker script changed after partial link")
    if partial["undefined_symbols"]:
        raise RuntimeError("partial link retains imports")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    objects = []
    for unit in selected["units"]:
        if Path(unit["source"]).name in EXCLUDE:
            continue
        source, obj = ROOT / unit["source"], Path(unit["object"])
        if sha(source) != unit["source_sha256"] or sha(obj) != unit["object_sha256"]:
            raise RuntimeError(f"selected source/object drift: {source}")
        objects.append(obj)
    for unit in partial["experimental_units"]:
        source = ROOT / unit["source"]
        if sha(source) != unit["source_sha256"]:
            raise RuntimeError(f"experimental source drift: {source}")
        stem = Path(unit["source"]).stem
        found = [p.resolve() for p in Path(args.partial_receipt).parent.glob("*.o")
                 if sha(p) == unit["object_sha256"]]
        if len(found) != 1:
            raise RuntimeError(f"experimental object missing: {stem}")
        objects.append(found[0])
    elf = out / "image_b_flexible_source_probe.elf"
    arg_paths = ["/repo/" + str(obj.relative_to(ROOT)) for obj in objects]
    target("ld", out, ["-T", "/repo/" + str(script.relative_to(ROOT)),
                       "-o", "/out/" + elf.name, *arg_paths])
    sections = target("objdump", out, ["-h", "/out/" + elf.name])
    header = target("readelf", out, ["-h", "/out/" + elf.name])
    undefined = target("nm", out, ["-u", "/out/" + elf.name]).strip()
    if undefined:
        raise RuntimeError(f"final ELF retains imports: {undefined}")
    section_map = {}
    for line in sections.splitlines():
        columns = line.split()
        if len(columns) >= 7 and columns[0].isdigit():
            section_map[columns[1]] = {
                "size": int(columns[2], 16),
                "vma": int(columns[3], 16),
                "lma": int(columns[4], 16),
            }
    if section_map[".vectors"] != {"size": 256, "vma": 0x10003000,
                                     "lma": 0x10003000}:
        raise RuntimeError("vector placement differs")
    if section_map[".text"]["vma"] != 0x10003100:
        raise RuntimeError("reset/text start differs")
    if (section_map[".rodata"]["vma"] +
            section_map[".rodata"]["size"] > 0x100168c0):
        raise RuntimeError("source rodata overlaps authenticated initialized clock state")
    for name, expected in ((".clock_state", 0x100168c0),
                           (".clock_boot_records", 0x100168fc),
                           (".clock_trim_records", 0x1001694c),
                           (".clock_param", 0x1001699c),
                           (".clock_dto", 0x10016b3c),
                           (".clock_div", 0x10016b40),
                           (".uart0_record", 0x10016b84),
                           (".uart1_record", 0x10016c04),
                           (".audio_out_root", 0x10016c84),
                           (".audio_out_callback_table", 0x10016cb8),
                           (".audio_out_state", 0x10016d0c),
                           (".flash_descriptor", 0x10016d60),
                           (".flash_callback_table", 0x10016d80),
                           (".flash_protection_p25q21l", 0x10016dfc),
                           (".flash_protection_p25q40l", 0x10016e24),
                           (".flash_protection_p25q80l", 0x10016e5c),
                           (".flash_profiles", 0x10016ea4),
                           (".flash_geometry", 0x10016f4c)):
        if (section_map[name]["lma"] != expected or
                section_map[name]["vma"] != expected + 0x10000000):
            raise RuntimeError(f"{name} moved over initialized product data")
    if section_map[".flash_descriptor"]["lma"] + section_map[".flash_descriptor"]["size"] != 0x10016d80:
        raise RuntimeError("flash descriptor extent differs")
    if section_map[".uart0_record"]["size"] != 128 or section_map[".uart1_record"]["size"] != 128:
        raise RuntimeError("UART record extent differs")
    for name, size in ((".audio_out_root", 52),
                       (".audio_out_callback_table", 84),
                       (".audio_out_state", 84)):
        if section_map[name]["size"] != size:
            raise RuntimeError(f"{name} extent differs")
    if section_map[".flash_callback_table"]["size"] != 124:
        raise RuntimeError("flash callback table extent differs")
    if script.name == "image_b_late_audio_layout_probe.ld":
        late = section_map[".late_audio"]
        if (late["vma"] != 0x1002d800 or late["lma"] != 0x1002d800 or
                late["size"] == 0 or late["size"] > 0x1000):
            raise RuntimeError("late audio code exceeds experimental post-BSS island")
    for name, size in ((".flash_protection_p25q21l", 40),
                       (".flash_protection_p25q40l", 56),
                       (".flash_protection_p25q80l", 72),
                       (".flash_profiles", 168),
                       (".flash_geometry", 20)):
        if section_map[name]["size"] != size:
            raise RuntimeError(f"{name} extent differs")
    if section_map[".gsensor_state"]["lma"] != 0x10016f60:
        raise RuntimeError("initialized-data load start differs")
    if section_map[".kernel_coefficients"]["lma"] + 88 != 0x1001708c:
        raise RuntimeError("initialized-data load end differs")
    if (section_map[".bss"]["size"] != 0x1670c or
            section_map[".bss"]["vma"] != 0x20017090):
        raise RuntimeError("BSS reservation differs")
    flash_state = None
    board_pins_ready = None
    console_port = None
    exception_anchor = None
    clock_gate_bits = None
    gpio_irq_masks = None
    irq_descriptors = None
    timer_records = None
    pmu_record = None
    spi_device_state = None
    denoise_runtime = None
    if script.name == "image_b_stock_length_source_fit_probe.ld":
        symbols = target("nm", out, ["-S", "/out/" + elf.name])
        match = re.search(
            r"(?m)^2001765c 00000001 B gx8002_image_b_flash_probe_state_2001765c$",
            symbols)
        if match is None:
            raise RuntimeError("source flash probe byte missing or misplaced")
        flash_state = {"address":"0x2001765c","bytes":1,
                       "storage":"NOLOAD within conditionally cleared BSS",
                       "initial_value_proven":False}
        if re.search(
            r"(?m)^200176d8 00000004 B gx8002_image_b_board_pins_ready_200176d8$",
            symbols) is None:
            raise RuntimeError("source board pins ready word missing or misplaced")
        board_pins_ready = {"address":"0x200176d8","bytes":4,
                            "storage":"NOLOAD within conditionally cleared BSS",
                            "initial_value_proven":False}
        if re.search(
            r"(?m)^2001739c 00000004 B gx8002_image_b_console_port_2001739c$",
            symbols) is None:
            raise RuntimeError("source console port word missing or misplaced")
        console_port = {"address":"0x2001739c","bytes":4,
                        "storage":"NOLOAD within conditionally cleared BSS",
                        "initial_value_proven":False}
        if re.search(
            r"(?m)^20017390 00000004 B gx8002_image_b_exception_scratch_20017390$",
            symbols) is None:
            raise RuntimeError("source exception anchor word missing or misplaced")
        exception_anchor = {"address":"0x20017390","bytes":4,
                            "storage":"NOLOAD within conditionally cleared BSS",
                            "initial_value_proven":False,
                            "adjacent_frame_72_bytes_proven":False}
        if re.search(
            r"(?m)^20017394 00000004 B gx8002_image_b_clock_gate_bits_20017394$",
            symbols) is None:
            raise RuntimeError("source clock gate word missing or misplaced")
        clock_gate_bits = {"address":"0x20017394","bytes":4,
                           "storage":"NOLOAD within conditionally cleared BSS",
                           "initial_value_proven":False,
                           "retained_producer_proven":False}
        if re.search(
            r"(?m)^200173a0 00000008 B gx8002_image_b_gpio_irq_masks_200173a0$",
            symbols) is None:
            raise RuntimeError("source GPIO IRQ masks missing or misplaced")
        gpio_irq_masks = {"address":"0x200173a0","bytes":8,
                          "storage":"NOLOAD within conditionally cleared BSS",
                          "initial_value_proven":False,
                          "retained_producer_proven":False}
        if re.search(
            r"(?m)^200173a8 00000100 B gx8002_image_b_irq_descriptors_200173a8$",
            symbols) is None:
            raise RuntimeError("source IRQ descriptor table missing or misplaced")
        irq_descriptors = {"address":"0x200173a8","bytes":256,
                           "storage":"NOLOAD within conditionally cleared BSS",
                           "registered_line_count":32,
                           "controller_dispatch_line_validity_proven":False}
        if re.search(
            r"(?m)^200174bc 00000168 B gx8002_image_b_timer_records_200174bc$",
            symbols) is None:
            raise RuntimeError("source timer records missing or misplaced")
        timer_records = {"address":"0x200174bc","bytes":360,
                         "storage":"NOLOAD within conditionally cleared BSS",
                         "record_count":10,"record_bytes":36}
        if re.search(
            r"(?m)^2002cb88 00000090 B gx8002_image_b_pmu_record_2002cb88$",
            symbols) is None:
            raise RuntimeError("source PMU record missing or misplaced")
        pmu_record = {"address":"0x2002cb88","bytes":144,
                      "storage":"NOLOAD within conditionally cleared BSS",
                      "warm_callback_contents_proven":False}
        if re.search(
            r"(?m)^20017670 00000060 B gx8002_image_b_spi_device_state_20017670$",
            symbols) is None:
            raise RuntimeError("SDK-correlated SPI state missing or misplaced")
        spi_device_state = {"address":"0x20017670","bytes":96,
                            "storage":"NOLOAD within conditionally cleared BSS",
                            "sdk_correlated_subrecord_bytes":[16,36,44],
                            "physical_controller_effects_proven":False}
        denoise_symbols = (
            ("2002d2bc", "0000001c", "gx8002_image_b_denoise_mode_state_2002d2bc"),
            ("2002d2d8", "00000014", "gx8002_image_b_denoise_ring_2002d2d8"),
            ("2002d2f0", "00000028", "gx8002_image_b_denoise_queue_buffer_2002d2f0"),
        )
        for address, size, name in denoise_symbols:
            if re.search(rf"(?m)^{address} {size} B {name}$", symbols) is None:
                raise RuntimeError(f"source denoise object {name} missing or misplaced")
        denoise_runtime = {"mode_prefix_bytes":28,"queue_bytes":20,
                            "unattributed_gap_bytes":4,"queue_buffer_bytes":40,
                            "storage":"NOLOAD within conditionally cleared BSS",
                            "queue_lifecycle_proven":False}
    entry = re.search(r"Entry point address:\s*(0x[0-9a-f]+)", header)
    if entry is None or int(entry.group(1), 16) != 0x10003100:
        raise RuntimeError("entry is not native reset offset")
    receipt = {
        "result": "PASS_LAYOUT_ONLY",
        "source_complete": False,
        "bootable": False,
        "selected_receipt_sha256": sha(args.selected_receipt),
        "partial_receipt_sha256": sha(args.partial_receipt),
        "linker_script_sha256": sha(script),
        "selected_and_experimental_object_count": len(objects),
        "elf": str(elf.relative_to(ROOT)),
        "elf_sha256": sha(elf),
        "entry": entry.group(1),
        "sections": section_map,
        "external_resident_address_contracts": RESIDENT,
        "source_flash_probe_state": flash_state,
        "source_board_pins_ready": board_pins_ready,
        "source_console_port": console_port,
        "source_exception_anchor": exception_anchor,
        "source_clock_gate_bits": clock_gate_bits,
        "source_gpio_irq_masks": gpio_irq_masks,
        "source_irq_descriptors": irq_descriptors,
        "source_timer_records": timer_records,
        "source_pmu_record": pmu_record,
        "source_spi_device_state": spi_device_state,
        "source_denoise_runtime": denoise_runtime,
        "limits": [
            "The flash callback table has source relocations, but whole physical flash behavior is not validated.",
            "The 91916-byte BSS interval is reserved by native reset bounds; most interior field roles remain untyped.",
            "Product loader/IRAM-DRAM alias behavior and hardware execution remain unqualified.",
        ],
    }
    if script.name == "image_b_late_audio_layout_probe.ld":
        receipt["limits"].append(
            "Late audio code lies beyond the stock 0x1408c-byte stage2 payload; "
            "extended package/loader transfer and runtime stack separation are unqualified.")
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)

if __name__ == "__main__":
    main()

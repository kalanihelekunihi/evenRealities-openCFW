#!/usr/bin/env python3
"""Reproducible source-only touch object census; no firmware payload is linked."""
import hashlib
import json
import subprocess
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOUCH = ROOT / "g2/components/touch"
OUT = Path(__file__).resolve().parent / "build"
OUT.mkdir(exist_ok=True)
# This app-facing decoder is a new analysis API, not an original firmware body.
# Keep its standalone producer tests, but do not admit it as recovered firmware.
analysis_only = {TOUCH / "lp_history_offline/decoder.c"}
sources = sorted(p for p in TOUCH.glob("*_offline/*.c") if p not in analysis_only)
sources += [TOUCH / "reset_layout_candidate_20261010" / name for name in
            ("reset_sensor_descriptors.c", "reset_pin_config.c", "reset_generated_common_config.c", "reset_generated_internal_context.c", "reset_generated_widget_config.c", "reset_active_scan_context.c", "reset_base_frame_context.c", "reset_sensor_frames.c", "reset_capsense_context.c",
             "reset_pm_descriptor.c", "reset_common_context.c", "reset_widget_contexts.c", "reset_sensor_contexts.c", "reset_channel_pending.c", "reset_app_pm.c", "reset_position_history.c")]
flags = ["-target", "armv6m-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
         "-Og", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
         "-fdata-sections", "-fno-common", "-DCY8C4046FNI_T412"]
includes = ["-I" + str(p) for p in sorted(TOUCH.glob("*_offline"))]
pdl = ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc"
includes += ["-I" + str(pdl / "drivers/include"), "-I" + str(pdl / "devices/include")]
includes += ["-I" + str(ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include")]
includes += ["-I" + str(ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/cmsis")]
includes += ["-I" + str(ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source")]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path("/usr/bin/clang")) == "21df4f5520528e31b8632cfb3b4b57a3f2a33126693828bf69d1976f537aaec7"
records = []
objects = []
for src in sources:
    obj = OUT / (src.parent.name + "__" + src.stem + ".o")
    dep = obj.with_suffix(".d")
    argv = ["clang", *flags, *includes, "-MD", "-MF", str(dep), "-c", str(src), "-o", str(obj)]
    run = subprocess.run(argv, capture_output=True, text=True)
    rec = {"source": str(src.relative_to(ROOT)), "source_sha256": sha(src),
           "argv": argv, "exit_code": run.returncode, "diagnostics": run.stdout + run.stderr}
    if run.returncode == 0:
        rec["object_sha256"] = sha(obj)
        paths = dep.read_text().replace("\\\n", " ").split(": ", 1)[1].split()
        rec["input_sha256"] = {str(Path(p).relative_to(ROOT)): sha(Path(p)) for p in paths if Path(p).is_file() and Path(p).is_relative_to(ROOT)}
        objects.append(obj)
    records.append(rec)
provider_records = []
# The pinned PDL SCB implementation is source-owned and has the project's
# device configuration. It is compiled here, independently of the touch units.
scb = pdl / "drivers/source/cy_scb_i2c.c"
assert sha(scb) == "9f3e77675ea3f02798107fe28def78b826b35d6d136785644d90ff10877f248b"
scb_obj = OUT / "provider__cy_scb_i2c.o"
scb_dep = scb_obj.with_suffix(".d")
scb_argv = ["clang", *flags, *includes, "-MD", "-MF", str(scb_dep), "-c", str(scb), "-o", str(scb_obj)]
scb_run = subprocess.run(scb_argv, capture_output=True, text=True)
scb_rec = {"provider": "SCB I2C", "source": str(scb.relative_to(ROOT)),
           "source_sha256": sha(scb), "argv": scb_argv, "exit_code": scb_run.returncode,
           "diagnostics": scb_run.stdout + scb_run.stderr}
if scb_run.returncode == 0:
    paths = scb_dep.read_text().replace("\\\n", " ").split(": ", 1)[1].split()
    scb_rec["input_sha256"] = {str(Path(p).relative_to(ROOT)): sha(Path(p)) for p in paths if Path(p).is_file() and Path(p).is_relative_to(ROOT)}
    scb_rec["object_sha256"] = sha(scb_obj)
    objects.append(scb_obj)
provider_records.append(scb_rec)
# Common SCB transfer helpers are the same pinned PDL source family.
common = ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/source/cy_scb_common.c"
assert sha(common) == "e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1"
common_obj = OUT / "provider__cy_scb_common.o"
common_dep = common_obj.with_suffix(".d")
common_argv = ["clang", *flags, *includes, "-MD", "-MF", str(common_dep), "-c", str(common), "-o", str(common_obj)]
common_run = subprocess.run(common_argv, capture_output=True, text=True)
common_rec = {"provider": "SCB common", "source": str(common.relative_to(ROOT)),
              "source_sha256": sha(common), "argv": common_argv,
              "exit_code": common_run.returncode, "diagnostics": common_run.stdout + common_run.stderr}
if common_run.returncode == 0:
    paths = common_dep.read_text().replace("\\\n", " ").split(": ", 1)[1].split()
    common_rec["input_sha256"] = {str(Path(p).relative_to(ROOT)): sha(Path(p)) for p in paths if Path(p).is_file() and Path(p).is_relative_to(ROOT)}
    common_rec["object_sha256"] = sha(common_obj)
    objects.append(common_obj)
provider_records.append(common_rec)
# Rebuild every GNU provider from pinned source/config/compiler on this run.
troot = ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09"
acq = json.loads((troot / "acquisition.json").read_text())[0]
tool = (troot / acq["gcc"]).parents[1]
assert sha(tool / "bin/arm-none-eabi-gcc") == acq["gcc_sha256"]
vendor = troot / "tools/pdl-input"
headers = ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source"
interface = ROOT / "g2/analysis/touch-pdl14-system-interface-2026-10-09/interface"
runtime = ROOT / "g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/gcc-arm14-runtime"
image = "ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55"
mounts = [("/tool", tool), ("/pdl", vendor), ("/headers", headers),
          ("/interface", interface), ("/source", runtime)]
gflags = ["-mcpu=cortex-m0plus", "-mthumb", "-Og", "-ffreestanding",
          "-fno-builtin", "-DCY8C4046FNI_T412", "-ffunction-sections"]
ginc = ["-I/headers", "-I/headers/cmsis", "-I/pdl/drivers/include",
        "-I/pdl/devices/include", "-I/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include"]

def gnu_provider(label, source, extra, expected, prior_receipt):
    runout = OUT / "gnu" / label
    runout.mkdir(parents=True, exist_ok=True)
    local_mounts = [*mounts, ("/out", runout)]
    base = ["docker", "run", "--rm", "--platform", "linux/amd64",
            "--network", "none", "--cap-drop", "ALL", "--security-opt",
            "no-new-privileges"]
    for dest, host in local_mounts:
        base += ["-v", f"{host}:{dest}:{'rw' if dest == '/out' else 'ro'}"]
    base += [image, "/tool/bin/arm-none-eabi-gcc", *extra]
    argv = [*base, "-c", source, "-o", "/out/public.o"]
    subprocess.run(argv, capture_output=True, text=True, check=True)
    dep_argv = [*base, "-M", source, "-o", "/out/public.d"]
    subprocess.run(dep_argv, capture_output=True, text=True, check=True)
    produced = runout / "public.o"
    assert sha(produced) == expected, (label, sha(produced), expected)
    deps = (runout / "public.d").read_text().replace("\\\n", " ").split(":", 1)[1].split()
    consumed = {}
    for dep in deps:
        target = next((host / dep[len(dest)+1:] for dest, host in local_mounts if dep.startswith(dest + "/")), None)
        assert target and target.is_file(), (label, dep)
        consumed[str(target.relative_to(ROOT))] = sha(target)
    dst = OUT / f"provider__{label}.o"
    shutil.copyfile(produced, dst)
    objects.append(dst)
    source_file = next(host / source[len(dest)+1:] for dest, host in local_mounts if source.startswith(dest + "/"))
    provider_records.append({"provider": label, "source": str(source_file.relative_to(ROOT)),
                             "source_sha256": sha(source_file),
                             "argv": argv, "dependency_argv": dep_argv,
                             "input_sha256": consumed, "object_sha256": sha(dst),
                             "prior_receipt": prior_receipt,
                             "matches_prior_source_build_object_sha256": True})

gnu_provider("msclp", "/pdl/drivers/source/cy_msclp.c", [*gflags, *ginc],
             "42ccabbd5bbe171fde08ae040180fbd28a2f01fb1ee88edbab4ff78202342aa3",
             "g2/analysis/touch-compiler14-successor-2026-10-09/results.json")
gnu_provider("syslib_asm", "/pdl/drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S",
             gflags, "4fcad330e4cc3da31fdbe12a1ad98e0686fd5beb68af993f7e725d44e67d5e39",
             "g2/analysis/touch-syslib14-assembly-2026-10-09/results.json")
gnu_provider("syslib_delay", "/pdl/drivers/source/cy_syslib.c",
             [*gflags, "-I/interface", *ginc],
             "22b1d92ec903546daaf1b768259a4405ca89a81e20bd3eb62cb3c9040eff42b8",
             "g2/analysis/touch-syslib14-delay-linkage-2026-10-09/results.json")
for label, selector, expected in [
    ("uidiv", "L_udivsi3", "060ed7a978673e41519a1d06f7ac78819d4913773905e1ff4d17abd1d81c8e0f"),
    ("zero", "L_dvmd_tls", "4294d0f2a1a7732b97579d7562a6a67a56666d9421217d056be7a21d28494731")]:
    gnu_provider(label, "/source/libgcc/config/arm/lib1funcs.S",
                 ["-mcpu=cortex-m0plus", "-mthumb", "-D" + selector], expected,
                 "g2/analysis/touch-libgcc14-source-rebuild-2026-10-09/results.json")
# Verify the actual stock reset-copy descriptor and each initializer before
# compiling source-owned data. This proves reset values, not later clock updates.
firmware = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_touch.bin"
assert sha(firmware) == "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
payload = firmware.read_bytes()[32:]
word = lambda a: struct.unpack_from("<I", payload, a - 0x3300)[0]
assert [word(a) for a in (0x46e8, 0x46ec, 0x46f0, 0x46f4)] == [0xb578, 0xb584, 0xb584, 0xb58c]
assert [word(a) for a in (0xb578, 0xb57c, 0xb580)] == [0xb58c, 0x200004c0, 0xf1]
reset_values = {}
for symbol, ram, size, value in [
    ("cy_delay32kMs", 0x2000086c, 4, 0x2ee00000),
    ("cy_delayFreqMhz", 0x20000870, 1, 24),
    ("cy_delayFreqKhz", 0x20000874, 4, 24000),
    ("SystemCoreClock", 0x20000878, 4, 24000000),
]:
    flash = 0xb58c + ram - 0x200004c0
    raw = payload[flash - 0x3300:flash - 0x3300 + size]
    assert int.from_bytes(raw, "little") == value, symbol
    reset_values[symbol] = {"ram_address": hex(ram), "flash_source": hex(flash),
                            "size": size, "reset_value": value, "stock_bytes": raw.hex()}
reset_src = Path(__file__).resolve().parent / "reset_data.c"
reset_obj = OUT / "provider__reset_data.o"
reset_dep = reset_obj.with_suffix(".d")
reset_argv = ["clang", *flags, "-MD", "-MF", str(reset_dep), "-c", str(reset_src), "-o", str(reset_obj)]
subprocess.run(reset_argv, capture_output=True, text=True, check=True)
for symbol in ("cy_delay32kMs", "cy_delayFreqMhz", "cy_delayFreqKhz"):
    data_file = OUT / ("reset__" + symbol + ".bin")
    subprocess.run(["/opt/homebrew/bin/arm-none-eabi-objcopy", "--dump-section",
                    f".data.{symbol}={data_file}", str(reset_obj)], check=True)
    assert data_file.read_bytes().hex() == reset_values[symbol]["stock_bytes"], symbol
objects.append(reset_obj)
provider_records.append({"provider": "stock reset-copy delay data", "source": str(reset_src.relative_to(ROOT)),
                         "source_sha256": sha(reset_src), "argv": reset_argv,
                         "input_sha256": {str(reset_src.relative_to(ROOT)): sha(reset_src)},
                         "object_sha256": sha(reset_obj), "reset_copy_descriptor":
                         {"table_start": "0xb578", "table_end": "0xb584", "flash_start": "0xb58c",
                          "ram_start": "0x200004c0", "word_count": 0xf1},
                         "reset_values": reset_values, "lifecycle_limit": "Reset initializers only; SystemInit clock updates not proven for G2."})
# Authentic GCC CRT_BEGIN/CRT_END are rebuilt from their pinned C source;
# installed executable objects are never admitted as source providers.
crt = ROOT / "g2/analysis/touch-crtstuff-source-rebuild-2026-10-09"
crt_commands = json.loads((crt / "commands.json").read_text())
begin_argv = next(x["argv"] for x in crt_commands
                  if "/tool/bin/arm-none-eabi-gcc" in x["argv"] and "-c" in x["argv"])
end_receipt = json.loads((crt / "crtend-results.json").read_text())
end_argv = next(x["argv"] for x in end_receipt["calls"] if "-c" in x["argv"])
for label, argv, expected in [
    ("crtbegin", begin_argv, "8ac3ab1c8860a91acd384f1029e1b0dbacc5acfb6dfc91d06eccf92ed38f9135"),
    ("crtend", end_argv, end_receipt["source_provider_sha256"]),
]:
    mappings = []
    for i, arg in enumerate(argv):
        if arg == "-v":
            host, guest, *_ = argv[i+1].split(":")
            mappings.append((guest, Path(host)))
    dep_file = crt / "outputs" / (label + ".d")
    deps = dep_file.read_text().replace("\\\n", " ").split(":", 1)[1].split()
    consumed = {}
    for dep in deps:
        host = next((p / dep[len(g)+1:] for g,p in mappings if dep.startswith(g+"/")), None)
        assert host and host.is_file(), (label, dep)
        consumed[str(host.relative_to(ROOT))] = sha(host)
    subprocess.run(argv, capture_output=True, text=True, check=True)
    assert all(sha(ROOT / p) == value for p,value in consumed.items()), label
    produced = crt / "outputs" / (label + ".o")
    assert sha(produced) == expected, (label, sha(produced), expected)
    dst = OUT / ("provider__" + label + ".o")
    shutil.copyfile(produced, dst); objects.append(dst)
    source = ROOT / "g2/analysis/touch-crt-array-binding-2026-10-09/source/libgcc/crtstuff.c"
    provider_records.append({"provider": label, "source": str(source.relative_to(ROOT)),
        "source_sha256": sha(source), "argv": argv, "input_sha256": consumed,
        "stable_inputs_during_compile": True, "object_sha256": sha(dst),
        "prior_receipt": str((crt / "linked-results.json").relative_to(ROOT)),
        "scope": "Genuine pinned CRT source; final placement and startup reachability remain open"})
archive = OUT / "touch-source-candidate.a"
if archive.exists():
    archive.unlink()
subprocess.run(["/opt/homebrew/bin/arm-none-eabi-ar", "rcsD", str(archive), *map(str, objects)], check=True)
nm = subprocess.run(["/opt/homebrew/bin/arm-none-eabi-nm", "-g", "-A", str(archive)], capture_output=True, text=True, check=True)
(OUT / "symbols.txt").write_text(nm.stdout)
defined, undefined, strong_definitions = set(), set(), {}
weak_undefined = set()
for line in nm.stdout.splitlines():
    bits = line.split()
    if len(bits) >= 2:
        typ, sym = bits[-2:]
        if typ == "U":
            undefined.add(sym)
        elif typ in {"w", "v"}:
            weak_undefined.add(sym)
        elif typ.upper() == typ and typ.isalpha():
            defined.add(sym)
            if typ in ("T", "D", "B", "R"):
                strong_definitions.setdefault(sym, []).append(line.split(":", 2)[1])
duplicates = {sym: locations for sym, locations in strong_definitions.items() if len(locations) > 1}
assert not duplicates, duplicates
receipt = {"compiler": subprocess.check_output(["clang", "--version"], text=True).splitlines()[0],
           "target": "Cortex-M0+ ARMv6-M Thumb; relocatable source-only archive",
           "source_count": len(sources), "compiled_count": sum(x["exit_code"] == 0 for x in records),
           "provider_object_count": len(provider_records),
           "archive_sha256": sha(archive), "records": records,
           "provider_records": provider_records,
           "symbol_census_scope": "nm -g: global and weak only",
           "duplicate_strong_globals": duplicates,
           "unresolved_provider_symbols": sorted(undefined - defined),
           "optional_weak_reference_symbols": sorted(weak_undefined - defined),
           "unresolved_provider_count": len(undefined - defined)}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({k: receipt[k] for k in ("source_count", "compiled_count", "unresolved_provider_count", "archive_sha256")}, indent=2))

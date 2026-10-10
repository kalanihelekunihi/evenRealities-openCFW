#!/usr/bin/env python3
"""Reproducible source-only touch object census; no firmware payload is linked."""
import hashlib
import json
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOUCH = ROOT / "g2/components/touch"
OUT = Path(__file__).resolve().parent / "build"
OUT.mkdir(exist_ok=True)
sources = sorted(p for p in TOUCH.glob("*_offline/*.c"))
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
# These objects are archived only after checking their exact earlier source
# builds and hashes. They are not extracted firmware bytes.
for label, prior, expected, source in [
    ("MSCLP GNU14.2", ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09/outputs/14.2.Rel1/public.o", "42ccabbd5bbe171fde08ae040180fbd28a2f01fb1ee88edbab4ff78202342aa3", ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/source/cy_msclp.c"),
    ("SysLib GNU14.2", ROOT / "g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o", "4fcad330e4cc3da31fdbe12a1ad98e0686fd5beb68af993f7e725d44e67d5e39", ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S"),
]:
    assert sha(prior) == expected, label
    dst = OUT / ("provider__" + label.split()[0].lower() + ".o")
    shutil.copyfile(prior, dst)
    objects.append(dst)
    provider_records.append({"provider": label, "source": str(source.relative_to(ROOT)),
                             "source_sha256": sha(source), "prior_build_object": str(prior.relative_to(ROOT)),
                             "prior_receipt": str((ROOT / ("g2/analysis/touch-compiler14-successor-2026-10-09/results.json" if label.startswith("MSCLP") else "g2/analysis/touch-syslib14-assembly-2026-10-09/results.json")).relative_to(ROOT)),
                             "object_sha256": sha(dst), "exact_original_section_evidence": True})
# The exact DelayUs source object was separately built and compared with the
# original in touch-syslib14-delay-linkage. Its coefficient data remain external.
delay_source = ROOT / "g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/source/cy_syslib.c"
delay_prior = ROOT / "g2/analysis/touch-pdl14-system-interface-2026-10-09/outputs/cy_syslib.c/public.o"
assert sha(delay_prior) == "22b1d92ec903546daaf1b768259a4405ca89a81e20bd3eb62cb3c9040eff42b8"
delay_obj = OUT / "provider__cy_syslib_delay.o"
shutil.copyfile(delay_prior, delay_obj)
objects.append(delay_obj)
provider_records.append({"provider": "SysLib DelayUs GNU14.2", "source": str(delay_source.relative_to(ROOT)),
                         "source_sha256": sha(delay_source), "prior_build_object": str(delay_prior.relative_to(ROOT)),
                         "prior_receipt": "g2/analysis/touch-syslib14-delay-linkage-2026-10-09/results.json",
                         "object_sha256": sha(delay_obj), "exact_original_section_evidence": True})
# Exact-release GPL+Runtime-Exception libgcc assembly was already rebuilt
# from source and linked against original touch bytes, including the real weak
# divide-zero hook. Import its authenticated source-built relocatables intact.
division_source = ROOT / "g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/gcc-arm14-runtime/libgcc/config/arm/lib1funcs.S"
for name, expected in [("uidiv", "060ed7a978673e41519a1d06f7ac78819d4913773905e1ff4d17abd1d81c8e0f"),
                       ("zero", "4294d0f2a1a7732b97579d7562a6a67a56666d9421217d056be7a21d28494731")]:
    prior = ROOT / f"g2/analysis/touch-libgcc14-source-rebuild-2026-10-09/outputs/{name}.o"
    assert sha(prior) == expected, name
    dst = OUT / f"provider__libgcc_{name}.o"
    shutil.copyfile(prior, dst)
    objects.append(dst)
    provider_records.append({"provider": f"libgcc14 {name}", "source": str(division_source.relative_to(ROOT)),
                             "source_sha256": sha(division_source), "prior_build_object": str(prior.relative_to(ROOT)),
                             "prior_receipt": "g2/analysis/touch-libgcc14-source-rebuild-2026-10-09/results.json",
                             "object_sha256": sha(dst), "exact_original_section_evidence": True})
archive = OUT / "touch-source-candidate.a"
if archive.exists():
    archive.unlink()
subprocess.run(["/opt/homebrew/bin/arm-none-eabi-ar", "rcs", str(archive), *map(str, objects)], check=True)
nm = subprocess.run(["/opt/homebrew/bin/arm-none-eabi-nm", "-A", str(archive)], capture_output=True, text=True, check=True)
(OUT / "symbols.txt").write_text(nm.stdout)
defined, undefined = set(), set()
for line in nm.stdout.splitlines():
    bits = line.split()
    if len(bits) >= 2:
        typ, sym = bits[-2:]
        if typ == "U":
            undefined.add(sym)
        elif typ.upper() == typ and typ.isalpha():
            defined.add(sym)
receipt = {"compiler": subprocess.check_output(["clang", "--version"], text=True).splitlines()[0],
           "target": "Cortex-M0+ ARMv6-M Thumb; relocatable source-only archive",
           "source_count": len(sources), "compiled_count": sum(x["exit_code"] == 0 for x in records),
           "provider_object_count": len(provider_records),
           "archive_sha256": sha(archive), "records": records,
           "provider_records": provider_records,
           "unresolved_provider_symbols": sorted(undefined - defined),
           "unresolved_provider_count": len(undefined - defined)}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({k: receipt[k] for k in ("source_count", "compiled_count", "unresolved_provider_count", "archive_sha256")}, indent=2))

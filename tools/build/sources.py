#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile every reconstructed source listed in a device source manifest.

    python3 tools/build/sources.py check  [--device g2|r1]
    python3 tools/build/sources.py build  [--device g2|r1] [--payload ID] [--out DIR] [--jobs N]
    python3 tools/build/sources.py build --device r1 --normal-svc --out DIR
    python3 tools/build/sources.py build --device r1 --normal-svc --cordio-rtc0 --out DIR

The manifests are ``g2/src/sources.json`` and ``r1/src/sources.json``. Each
unit names one source file, the payload it belongs to and a compile profile.
``build`` compiles every selected unit, checks each payload's linked units for
duplicate strong definitions, composes a relocatable per payload and writes
``report.json``. A unit that fails to compile is reported, never skipped
silently, and the command exits non-zero unless the manifest records it as
``"expect": "fails"`` with a note (a known, pre-existing failure). Byte equality against the stock
payloads is a separate step (``qualify_sources.py``); compiling here does not
establish source completeness.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import re
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DEVICES = ("g2", "r1")
SOURCE_SUFFIXES = (".c", ".S", ".s")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest_path(device):
    return ROOT / device / "src" / "sources.json"


def load(device):
    return json.loads(manifest_path(device).read_text())


def units_of(manifest, payload=None):
    defaults = manifest.get("defaults", {})
    for unit in manifest["units"]:
        if payload and unit["payload"] != payload:
            continue
        merged = dict(defaults.get(unit["payload"], {}))
        merged.update(unit)
        yield merged


def selected_for_build(unit, cordio_rtc0=False):
    """Keep optional Cordio providers out of the stock-compatible R1 link."""
    variant = unit.get("variant")
    if variant not in (None, "cordio-rtc0"):
        raise ValueError(f"unsupported source variant {variant!r}: {unit['source']}")
    return unit.get("build", True) and (variant is None or cordio_rtc0)


# --- ELF symbol census (ELF32 little-endian: ARM, C-SKY, ARC) -------------

def elf_symbols(path):
    data = Path(path).read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise ValueError(f"expected little-endian ELF32: {path}")
    shoff = struct.unpack_from("<I", data, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", data, 46)
    sections = [struct.unpack_from("<10I", data, shoff + i * shentsize) for i in range(shnum)]
    strong, weak, undefined = set(), set(), set()
    for sec in sections:
        if sec[1] != 2:  # SHT_SYMTAB
            continue
        strtab = sections[sec[6]]
        names = data[strtab[4]:strtab[4] + strtab[5]]
        for at in range(sec[4], sec[4] + sec[5], sec[9]):
            name, _value, _size, info, _other, shndx = struct.unpack_from("<IIIBBH", data, at)
            bind = info >> 4
            if not name or bind not in (1, 2):
                continue
            label = names[name:].split(b"\0", 1)[0].decode()
            if shndx == 0:
                undefined.add(label)
            elif bind == 2:
                weak.add(label)
            else:
                strong.add(label)
    return {"strong": sorted(strong), "weak": sorted(weak), "undefined": sorted(undefined)}


# --- toolchains ------------------------------------------------------------

class Toolchain:
    def __init__(self, name, spec):
        self.name, self.spec = name, spec
        self.docker = spec.get("docker")

    def host_path(self, value):
        """Resolve a repository-relative tool path; bare names come from PATH."""
        if "/" not in value:
            found = shutil.which(value)
            if not found:
                raise RuntimeError(f"{self.name}: {value} not found on PATH")
            return found
        path = Path(value) if os.path.isabs(value) else ROOT / value
        if not path.exists():
            raise RuntimeError(f"{self.name}: {path} missing; see {self.spec.get('provision', 'docs/build.md')}")
        return str(path.resolve())  # vendor-cache entries may be symlinks; Docker needs real paths

    def context(self, out, gen):
        if self.docker:
            return {"root": "/repo", "out": "/out", "gen": "/gen"}
        return {"root": str(ROOT), "out": str(out), "gen": str(gen)}

    def prefix(self, out, gen):
        if not self.docker:
            return [self.host_path(self.spec["cc"])]
        d = self.docker
        if self.spec.get("compiler_sha256") and not getattr(self, "_compiler_checked", False):
            compiler = Path(self.host_path(d["mounts"]["/tool"])) / Path(self.spec["cc"]).relative_to("/tool")
            if sha(compiler) != self.spec["compiler_sha256"]:
                raise RuntimeError(f"{self.name}: compiler identity changed: {compiler}")
            self._compiler_checked = True
        argv = [self.host_path("docker"), "run", "--rm", "--network=none", "--read-only",
                "--platform", d.get("platform", "linux/amd64"),
                "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
                "--mount", f"type=bind,src={out},dst=/out",
                "--mount", f"type=bind,src={gen},dst=/gen,readonly",
                "--tmpfs", "/tmp:rw"]
        for dst, src in sorted(d.get("mounts", {}).items()):
            argv += ["--mount", f"type=bind,src={self.host_path(src)},dst={dst},readonly"]
        return argv + [d["image"]]


def render(args, ctx):
    return [a.format(**ctx) for a in args]


def unit_argv(manifest, unit, ctx, normal_svc=False, cordio_rtc0=False):
    profile = manifest["profiles"][unit["profile"]]
    extra = []
    # Diagnostic sim builds only (unset by default): extra clang flags for apollo-main units.
    if unit.get("payload") == "g2-apollo-main" and os.environ.get("G2_SIM_EXTRA_CFLAGS"):
        extra = os.environ["G2_SIM_EXTRA_CFLAGS"].split()
    if normal_svc and unit["payload"].startswith("r1-"):
        extra.append("-DSVCALL_AS_NORMAL_FUNCTION")
    if cordio_rtc0 and unit["payload"] == "r1-application":
        extra.append("-DR1_CORDIO_RTC0=1")
        # The pinned legacy clock driver otherwise disables POWER_CLOCK_IRQn
        # on nrf_sdh enable and routes HFCLK through three S140 calls. The
        # nrfx must keep the clock interrupt and direct HFCLK path.
        if unit["source"] == "vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/integration/nrfx/legacy/nrf_drv_clock.c":
            extra.append("-USOFTDEVICE_PRESENT")
    return render(profile + unit.get("flags", []) + extra, ctx)


# --- generated inputs ------------------------------------------------------

def generate(manifest, gen):
    """Write generated headers (patched copies of pinned vendor files)."""
    gen.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in manifest.get("generated", []):
        source = ROOT / item["from"]
        if not source.is_file():
            raise RuntimeError(f"generated input {item['output']} needs {source}; see {item.get('provision', 'docs/build.md')}")
        text = source.read_text()
        for old, new in item.get("replace", []):
            if text.count(old) != 1:
                raise RuntimeError(f"{item['output']}: expected exactly one {old!r} in {source}")
            text = text.replace(old, new)
        target = gen / item["output"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        rows.append({"output": item["output"], "from": item["from"], "from_sha256": sha(source), "sha256": sha(target)})
    return rows


# --- compilation -----------------------------------------------------------

def object_name(source):
    return source.replace("{gen}", "generated").replace("/", "__") + ".o"


def source_path(unit, gen):
    """Repository source, or a patched vendor file written by generate() as {gen}/name."""
    if unit["source"].startswith("{gen}/"):
        return Path(gen) / unit["source"][len("{gen}/"):]
    return ROOT / unit["source"]


def compile_host(manifest, toolchains, unit, out, gen, normal_svc=False, cordio_rtc0=False):
    tc = toolchains[unit["toolchain"]]
    ctx = tc.context(out, gen)
    obj = out / object_name(unit["source"])
    dep = obj.with_suffix(".d")
    argv = tc.prefix(out, gen) + unit_argv(manifest, unit, ctx, normal_svc, cordio_rtc0) + [
        "-MD", "-MF", str(dep), "-c", str(source_path(unit, gen)), "-o", str(obj)]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    return finish(unit, obj, argv, proc.returncode, proc.stdout + proc.stderr, gen)


def compile_docker(manifest, toolchains, units, out, gen, normal_svc=False, cordio_rtc0=False):
    """One container run per toolchain; every unit still gets its own log and status."""
    tc = toolchains[units[0]["toolchain"]]
    ctx = tc.context(out, gen)
    cc = tc.spec["cc"]
    script = ["set +e"]
    commands = []
    for i, unit in enumerate(units):
        obj = object_name(unit["source"])
        argv = [cc] + unit_argv(manifest, unit, ctx, normal_svc, cordio_rtc0) + [
            "-MD", "-MF", f"/out/{obj[:-2]}.d", "-c", unit["source"].format(gen="/gen") if unit["source"].startswith("{gen}/") else "/repo/" + unit["source"],
            "-o", f"/out/{obj}"]
        commands.append(argv)
        script.append(f"{shlex.join(argv)} > /out/{obj}.log 2>&1; echo $? > /out/{obj}.rc")
    (out / f"{tc.name}.sh").write_text("\n".join(script) + "\n")
    proc = subprocess.run(tc.prefix(out, gen) + ["sh", f"/out/{tc.name}.sh"],
                          cwd=ROOT, capture_output=True, text=True)
    results = []
    for unit, argv in zip(units, commands):
        obj = out / object_name(unit["source"])
        rc_file = Path(str(obj) + ".rc")
        rc = int(rc_file.read_text()) if rc_file.is_file() else (proc.returncode or 125)
        log = Path(str(obj) + ".log")
        results.append(finish(unit, obj, tc.prefix(out, gen) + argv, rc,
                              log.read_text() if log.is_file() else proc.stderr, gen))
    return results


def finish(unit, obj, argv, rc, log, gen):
    row = {"source": unit["source"], "payload": unit["payload"], "role": unit.get("role", "candidate"),
           "toolchain": unit["toolchain"], "link": unit.get("link", True), "expect": unit.get("expect", "compile"),
           "returncode": rc, "argv": argv,
           "source_sha256": sha(source_path(unit, gen))}
    if log.strip():
        Path(str(obj) + ".log").write_text(log)
        row["log"] = str(Path(str(obj) + ".log"))
    if rc == 0 and obj.is_file():
        row["object_sha256"] = sha(obj)
        row["object"] = str(obj)
        try:
            row.update(elf_symbols(obj))
            selection = unit.get("retain")
            if selection is not None:
                if not isinstance(selection, dict):
                    raise ValueError("retain must specify linker and symbols")
                roots = selection.get("symbols", [])
                if not isinstance(roots, list) or not roots or len(set(roots)) != len(roots) or not all(
                        isinstance(s, str) and s and not s.startswith("-") for s in roots):
                    raise ValueError("retain.symbols must name distinct defined roots")
                if set(roots) - set(row["strong"] + row["weak"]):
                    raise ValueError("retain root not defined in compiled object")
                selected = obj.with_suffix(".selected.o")
                command = [selection["linker"], "-r", "--gc-sections"]
                for symbol in roots:
                    command += ["--undefined", symbol]
                command += ["-o", str(selected), str(obj)]
                proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                row["retain"] = {"symbols": roots, "argv": command,
                                 "returncode": proc.returncode,
                                 "log": (proc.stdout + proc.stderr)[-4000:]}
                if proc.returncode != 0:
                    raise ValueError("retained-root relocatable link failed")
                symbols = elf_symbols(selected)
                if set(roots) - set(symbols["strong"] + symbols["weak"]):
                    raise ValueError("retained-root link lost a requested definition")
                row["compiler_object"] = row["object"]
                row["compiler_object_sha256"] = row["object_sha256"]
                row["compiler_symbols"] = {k: row[k] for k in ("strong", "weak", "undefined")}
                row.update(symbols, object=str(selected), object_sha256=sha(selected))
        except (ValueError, OSError, KeyError, TypeError) as exc:
            row["returncode"] = 125
            row["symbol_error"] = str(exc)
            if unit.get("retain") is not None:
                row["compiler_object"] = str(obj)
                row["compiler_object_sha256"] = sha(obj)
                row.setdefault("compiler_symbols", {k: row.get(k, []) for k in ("strong", "weak", "undefined")})
                row.update(strong=[], weak=[], undefined=[])
                row.pop("object", None)
                row.pop("object_sha256", None)
    elif rc == 0:
        row["returncode"] = 125
        row["error"] = "compiler reported success without an object"
    return row


_SECTION_ROW = re.compile(
    r"\s*\[\s*\d+\]\s+(\S+)\s+(?:PROGBITS|NOBITS)\s+\S+\s+\S+\s+([0-9a-f]+)\s+\S+\s+(\S+)\s+\S+\s+\S+\s+(\d+)\s*$")


def align_writable(ld, obj, minimum=4):
    """Set sh_addralign=minimum on writable, allocated, non-executable sections of at least minimum
    bytes whose alignment is lower. Returns the number of sections raised."""
    tool = lambda name: str(ld.with_name(ld.name[:-2] + name)) if ld.name.endswith("ld") else name
    listing = subprocess.run([tool("readelf"), "-SW", str(obj)], capture_output=True, text=True, check=True).stdout
    names = []
    for line in listing.splitlines():
        m = _SECTION_ROW.match(line)
        if m and "W" in m.group(3) and "A" in m.group(3) and "X" not in m.group(3) \
                and int(m.group(2), 16) >= minimum and int(m.group(4)) < minimum:
            names.append(m.group(1))
    for i in range(0, len(names), 200):
        args = [a for n in names[i:i + 200] for a in ("--set-section-alignment", f"{n}={minimum}")]
        subprocess.run([tool("objcopy"), *args, str(obj)], check=True)
    return len(names)


def compose(manifest, toolchains, payload, rows, out, gen):
    spec = manifest.get("payloads", {}).get(payload, {}).get("compose")
    linked = [r for r in rows if r.get("object") and r.get("link", True)]
    if not spec or not linked:
        return None
    tc = toolchains[spec["toolchain"]]
    ctx = tc.context(out, gen)
    target = f"{payload}.o"
    defsyms = [a for k, v in sorted(spec.get("defsym", {}).items()) for a in ("--defsym", f"{k}={v}")]
    objects = [Path(r["object"]).name for r in linked]
    objdir = ctx["out"]
    argv = (tc.prefix(out, gen) if tc.docker else [tc.host_path(spec["ld"])]) + (
        [spec["ld"]] if tc.docker else []) + ["-r", *spec.get("ld_flags", []), *defsyms,
                                               "-o", f"{objdir}/{target}"] + [
        f"{objdir}/{o}" for o in objects]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    result = {"returncode": proc.returncode, "argv": argv[:12] + [f"... {len(objects)} objects"],
              "log": (proc.stdout + proc.stderr)[-4000:]}
    if proc.returncode == 0 and not tc.docker:
        # Word-align writable data. clang gives uint8_t/char arrays and all-byte structs alignment 1, so
        # the final link packed RAM objects (nanopb messages, WSF timers, DMA buffers) at odd addresses;
        # LDRD/STRD/LDM/STM/VLDR/LDREX on them fault on the M55. Raise (never lower) to 4 every writable
        # allocated section of 4 B or more. See build/ws-ramlayout-20261122-1230/pending/README.md (04).
        result["align4"] = align_writable(Path(tc.host_path(spec["ld"])), out / target)
    if proc.returncode == 0:
        result.update(output=str(out / target), sha256=sha(out / target), **elf_symbols(out / target))
        result.pop("strong"); result.pop("weak")
    return result


def build(args):
    report = {"schema": 1, "devices": {}}
    failed = False
    for device in args.devices:
        manifest_bytes = manifest_path(device).read_bytes()
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes)
        toolchains = {k: Toolchain(k, v) for k, v in manifest["toolchains"].items()}
        out = (args.out / device).resolve()
        gen = (args.out / "generated" / device).resolve()
        out.mkdir(parents=True, exist_ok=True)
        generated = generate(manifest, gen)
        selected = [u for u in units_of(manifest, args.payload)
                    if selected_for_build(u, args.cordio_rtc0)]
        host = [u for u in selected if not toolchains[u["toolchain"]].docker]
        docker = {}
        for u in selected:
            if toolchains[u["toolchain"]].docker:
                docker.setdefault((u["payload"], u["toolchain"]), []).append(u)
        rows = []
        for (payload, name), group in sorted(docker.items()):
            d = out / payload
            d.mkdir(exist_ok=True)
            print(f"{device}: {payload}: {len(group)} units in {name}", flush=True)
            rows += compile_docker(manifest, toolchains, group, d, gen, args.normal_svc, args.cordio_rtc0)
        with ThreadPoolExecutor(args.jobs) as pool:
            for u in host:
                (out / u["payload"]).mkdir(exist_ok=True)
            rows += list(pool.map(lambda u: compile_host(manifest, toolchains, u, out / u["payload"], gen, args.normal_svc, args.cordio_rtc0), host))
        payloads = {}
        for payload in sorted({r["payload"] for r in rows}):
            prow = [r for r in rows if r["payload"] == payload]
            owners = {}
            for r in prow:
                if r.get("link", True):
                    for s in r.get("strong", []):
                        owners.setdefault(s, []).append(r["source"])
            dups = {s: o for s, o in sorted(owners.items()) if len(o) > 1}
            defined = set(owners) | {s for r in prow if r.get("link", True) for s in r.get("weak", [])}
            undefined = sorted({s for r in prow if r.get("link", True) for s in r.get("undefined", [])} - defined)
            summary = {"units": len(prow), "compiled": sum(r["returncode"] == 0 for r in prow),
                       "failed": [r["source"] for r in prow if r["returncode"] != 0 and r["expect"] != "fails"],
                       "known_failures": [r["source"] for r in prow if r["returncode"] != 0 and r["expect"] == "fails"],
                       "now_compiling": [r["source"] for r in prow if r["returncode"] == 0 and r["expect"] == "fails"],
                       "duplicate_strong_symbols": dups, "object_unresolved_symbols": len(undefined),
                       "composed_unresolved_symbols": None, "unresolved_symbols": len(undefined),
                       "unresolved_scope": "objects"}
            if not dups and not args.no_compose:
                summary["compose"] = compose(manifest, toolchains, payload, prow, out / payload, gen)
            composition = summary.get("compose")
            compose_failed = composition is not None and composition["returncode"] != 0
            if composition is not None and not compose_failed:
                summary["composed_unresolved_symbols"] = len(composition["undefined"])
                summary["unresolved_symbols"] = summary["composed_unresolved_symbols"]
                summary["unresolved_scope"] = "composed"
            payloads[payload] = summary
            status = "ok" if not summary["failed"] and not dups and not compose_failed else "FAILED"
            scope_note = (f"composed; {len(undefined)} before aliases"
                          if summary["unresolved_scope"] == "composed" else "objects; no successful composition")
            print(f"{device}: {payload}: {summary['compiled']}/{summary['units']} compiled "
                  f"({len(summary['known_failures'])} known failures), {len(dups)} duplicate strong symbols, "
                  f"{summary['unresolved_symbols']} unresolved: {status} ({scope_note})", flush=True)
            for source in summary["failed"]:
                print(f"  failed: {source}", flush=True)
            for source in summary["now_compiling"]:
                print(f"  now compiles (update expect): {source}", flush=True)
            if compose_failed:
                print(f"  relocatable link failed (exit {composition['returncode']}): {composition['log']}", flush=True)
            failed |= bool(summary["failed"] or dups or compose_failed)
        manifest_changed = sha(manifest_path(device)) != manifest_sha256
        if manifest_changed:
            print(f"{device}: source manifest changed during the build; rerun with stable inputs", flush=True)
            failed = True
        report["devices"][device] = {"manifest_sha256": manifest_sha256,
                                     "manifest_changed_during_build": manifest_changed, "generated": generated,
                                     "payloads": payloads, "units": rows,
                                     "normal_svc": args.normal_svc,
                                     "cordio_rtc0": args.cordio_rtc0}
    report["source_completeness"] = "not established by compilation"
    (args.out / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"report: {args.out / 'report.json'}")
    return 1 if failed else 0


def check(args):
    """Manifest and tree agree: every source is listed once and every unit exists."""
    problems = []
    for device in args.devices:
        manifest = load(device)
        listed = {}
        for u in manifest["units"]:
            listed.setdefault(u["source"], []).append(u)
            if u["source"].startswith("{gen}/"):
                if not any(g["output"] == u["source"][len("{gen}/"):] for g in manifest.get("generated", [])):
                    problems.append(f"{device}: {u['source']} is not a generated output")
            elif not (ROOT / u["source"]).is_file():
                problems.append(f"{device}: missing source {u['source']}")
            if u["profile"] not in manifest["profiles"]:
                problems.append(f"{device}: {u['source']}: unknown profile {u['profile']}")
            if u["toolchain"] not in manifest["toolchains"]:
                problems.append(f"{device}: {u['source']}: unknown toolchain {u['toolchain']}")
            if u.get("variant") not in (None, "cordio-rtc0"):
                problems.append(f"{device}: {u['source']}: unknown variant {u['variant']!r}")
            if u.get("variant") == "cordio-rtc0" and (device != "r1" or u["payload"] != "r1-application"):
                problems.append(f"{device}: {u['source']}: Cordio variant belongs to R1 application")
        for s, us in listed.items():
            if len({u["payload"] for u in us}) != len(us):
                problems.append(f"{device}: {s} listed twice for one payload")
        tree = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / device / "src").rglob("*")
                      if p.suffix in SOURCE_SUFFIXES and p.is_file())
        unlisted = [t for t in tree if t not in listed and t not in manifest.get("not_built", {})]
        problems += [f"{device}: {t} is not in sources.json (add a unit or a not_built reason)" for t in unlisted]
        print(f"{device}: {len(manifest['units'])} units, {len(tree)} source files, "
              f"{len(manifest.get('not_built', {}))} not built")
    for p in problems[:200]:
        print(p)
    return 1 if problems else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=("check", "build"))
    p.add_argument("--device", choices=DEVICES)
    p.add_argument("--payload")
    p.add_argument("--out", type=Path, default=ROOT / "build/sources")
    p.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    p.add_argument("--no-compose", action="store_true", help="skip the per-payload relocatable link")
    p.add_argument("--normal-svc", action="store_true",
                   help="compile R1 Nordic SVC calls as external C functions; source-composition probe only")
    p.add_argument("--cordio-rtc0", action="store_true",
                   help="reserve RTC1 for the R1 Cordio source candidate; requires --normal-svc")
    args = p.parse_args()
    args.devices = [args.device] if args.device else list(DEVICES)
    if args.normal_svc and (args.command != "build" or args.device != "r1"):
        p.error("--normal-svc requires build --device r1")
    if args.cordio_rtc0 and not args.normal_svc:
        p.error("--cordio-rtc0 requires --normal-svc")
    if args.command == "build":
        if args.out.exists() and any(args.out.iterdir()):
            p.error(f"{args.out} is not empty; choose a fresh output directory")
        args.out.mkdir(parents=True, exist_ok=True)
        return build(args)
    return check(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile every reconstructed source listed in a device source manifest.

    python3 tools/build/sources.py check  [--device g2|r1]
    python3 tools/build/sources.py build  [--device g2|r1] [--payload ID] [--out DIR] [--jobs N]

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


def unit_argv(manifest, unit, ctx):
    profile = manifest["profiles"][unit["profile"]]
    return render(profile + unit.get("flags", []), ctx)


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


def compile_host(manifest, toolchains, unit, out, gen):
    tc = toolchains[unit["toolchain"]]
    ctx = tc.context(out, gen)
    obj = out / object_name(unit["source"])
    dep = obj.with_suffix(".d")
    argv = tc.prefix(out, gen) + unit_argv(manifest, unit, ctx) + [
        "-MD", "-MF", str(dep), "-c", str(source_path(unit, gen)), "-o", str(obj)]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    return finish(unit, obj, argv, proc.returncode, proc.stdout + proc.stderr, gen)


def compile_docker(manifest, toolchains, units, out, gen):
    """One container run per toolchain; every unit still gets its own log and status."""
    tc = toolchains[units[0]["toolchain"]]
    ctx = tc.context(out, gen)
    cc = tc.spec["cc"]
    script = ["set +e"]
    commands = []
    for i, unit in enumerate(units):
        obj = object_name(unit["source"])
        argv = [cc] + unit_argv(manifest, unit, ctx) + [
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
        except ValueError as exc:
            row["symbol_error"] = str(exc)
    elif rc == 0:
        row["returncode"] = 125
        row["error"] = "compiler reported success without an object"
    return row


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
    if proc.returncode == 0:
        result.update(output=str(out / target), sha256=sha(out / target), **elf_symbols(out / target))
        result.pop("strong"); result.pop("weak")
    return result


def build(args):
    report = {"schema": 1, "devices": {}}
    failed = False
    for device in args.devices:
        manifest = load(device)
        toolchains = {k: Toolchain(k, v) for k, v in manifest["toolchains"].items()}
        out = (args.out / device).resolve()
        gen = (args.out / "generated" / device).resolve()
        out.mkdir(parents=True, exist_ok=True)
        generated = generate(manifest, gen)
        selected = [u for u in units_of(manifest, args.payload) if u.get("build", True)]
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
            rows += compile_docker(manifest, toolchains, group, d, gen)
        with ThreadPoolExecutor(args.jobs) as pool:
            for u in host:
                (out / u["payload"]).mkdir(exist_ok=True)
            rows += list(pool.map(lambda u: compile_host(manifest, toolchains, u, out / u["payload"], gen), host))
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
                       "duplicate_strong_symbols": dups, "unresolved_symbols": len(undefined)}
            if not dups and not args.no_compose:
                summary["compose"] = compose(manifest, toolchains, payload, prow, out / payload, gen)
            payloads[payload] = summary
            status = "ok" if not summary["failed"] and not dups else "FAILED"
            print(f"{device}: {payload}: {summary['compiled']}/{summary['units']} compiled "
                  f"({len(summary['known_failures'])} known failures), {len(dups)} duplicate strong symbols, "
                  f"{len(undefined)} unresolved: {status}", flush=True)
            for source in summary["failed"]:
                print(f"  failed: {source}", flush=True)
            for source in summary["now_compiling"]:
                print(f"  now compiles (update expect): {source}", flush=True)
            failed |= bool(summary["failed"] or dups)
        report["devices"][device] = {"manifest_sha256": sha(manifest_path(device)), "generated": generated,
                                     "payloads": payloads, "units": rows}
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
    args = p.parse_args()
    args.devices = [args.device] if args.device else list(DEVICES)
    if args.command == "build":
        if args.out.exists() and any(args.out.iterdir()):
            p.error(f"{args.out} is not empty; choose a fresh output directory")
        args.out.mkdir(parents=True, exist_ok=True)
        return build(args)
    return check(args)


if __name__ == "__main__":
    sys.exit(main())

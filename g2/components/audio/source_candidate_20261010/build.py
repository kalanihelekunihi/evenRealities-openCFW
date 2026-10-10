#!/usr/bin/env python3
"""Compile a bounded, source-only codec candidate; never produce firmware."""
import argparse
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
SOURCES = (
    "g2/components/audio/codec_request_offline/request.c",
    "g2/components/audio/codec_response_offline/response.c",
    "g2/components/audio/encoder_setup_offline/setup.c",
)
TOOL = ROOT / "third-party/local-vendor/toolchains/csky-linux-x86_64"


def run(command):
    p = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"command": command, "returncode": p.returncode,
            "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=("host", "csky"), required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="g2-audio-source-") as tmp:
        tmp = pathlib.Path(tmp)
        objects = []
        for index, source in enumerate(SOURCES):
            obj = tmp / f"candidate_{index}.o"
            if args.target == "host":
                command = ["cc", "-std=c11", "-O2", "-c", str(ROOT / source), "-o", str(obj)]
            else:
                # The vendor executable is Linux x86_64. Docker supplies only an execution host.
                command = ["docker", "run", "--rm", "--network=none", "--read-only",
                           "-v", f"{ROOT}:/src:ro", "-v", f"{tmp}:/out:rw",
                           "-v", f"{TOOL}:/tool:ro", "opencfw/iar-base:10.10.2-local",
                           "/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804", "-O2", "-c",
                           "/src/" + source, "-o", "/out/" + obj.name]
            result = run(command)
            result["source"] = source
            results.append(result)
            if result["returncode"] == 0:
                objects.append(obj)
        if len(objects) == len(SOURCES):
            archive = args.output / ("libcodec_candidate_" + args.target + ".a")
            ar = "ar" if args.target == "host" else str(TOOL / "bin/csky-abiv2-elf-ar")
            if args.target == "csky":
                command = ["docker", "run", "--rm", "--network=none", "--read-only",
                           "-v", f"{tmp}:/out:rw", "-v", f"{args.output.resolve()}:/result:rw",
                           "-v", f"{TOOL}:/tool:ro", "opencfw/iar-base:10.10.2-local",
                           "/tool/bin/csky-abiv2-elf-ar", "rcs", "/result/" + archive.name,
                           *["/out/" + o.name for o in objects]]
            else:
                command = [ar, "rcs", str(archive), *map(str, objects)]
            results.append(run(command))
    (args.output / "build-results.json").write_text(json.dumps({"target": args.target,
        "sources": list(SOURCES), "results": results}, indent=2) + "\n")
    return int(any(r["returncode"] for r in results))


if __name__ == "__main__":
    raise SystemExit(main())

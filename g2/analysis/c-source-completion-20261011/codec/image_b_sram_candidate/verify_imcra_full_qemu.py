#!/usr/bin/env python3
"""Finite full-call native/source IMCRA state comparison on CK804EF QEMU.

The original test ELF embeds stock bytes only for execution and its typed
initialized data.  The source ELF calls the selected C body; both run one
first-frame, 512-point transform with four adaptive bins.  This is not a
hardware or all-domain numerical proof.
"""
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
QEMU = ROOT / "g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
BUILD = HERE / "build-stage2-imcra-mulsh-round"
RECEIPT = json.loads((BUILD / "receipt.json").read_text())

def repo(path: Path) -> str:
    return "/repo/" + str(path.relative_to(ROOT))

def run_docker(args: list[str], image: str, timeout: int = 60) -> str:
    command = ["docker", "run", "--rm", "--network=none",
               "--platform", "linux/amd64", "-v", f"{ROOT}:/repo",
               "-v", f"{TOOL}:/tool:ro", "-w", repo(HERE), image, *args]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=timeout, check=True)
    return result.stdout + result.stderr

def build(mode: str, frames: int, case_mode: int, signal: int) -> Path:
    elf = HERE / f"imcra-full-{mode}-{frames}frame-mode{case_mode}-signal{signal}-oracle.elf"
    args = ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
            "-mhard-float", "-O2", "-nostdlib", "-nostartfiles",
            f"-DFRAMES={frames}",
            f"-DCASE_MODE={case_mode}",
            f"-DSIGNAL_CASE={signal}",
            "-Wl,-T,process_native_oracle.ld" if mode == "native" else
            "-Wl,-T,imcra_full_source_oracle.ld"]
    if mode != "native":
        args.append("-DSOURCE_MODE")
        if mode == "source":
            for symbol in RECEIPT["undefined_symbols"]:
                if symbol == "gx8002_image_b_bss_start":
                    address = "0x20017090"
                elif symbol == "gx8002_image_b_bss_end":
                    address = "0x2002d79c"
                else:
                    address = "0x" + symbol.rsplit("_", 1)[1]
                args.append(f"-Wl,--defsym,{symbol}={address}")
        else:
            children = {
                "move_10009968": "0x10009968",
                "zero_100113c4": "0x100113c4",
                "imcra_peak_shift_1000e2c4": "0x1000e2c4",
                "imcra_block_scale_1000e28c": "0x1000e28c",
                "rfft_1000ef64": "0x1000ef64",
                "copy_10011344": "0x10011344",
            }
            if mode in ("source_rfft_wrapper", "source_rfft_split", "source_inverse_only", "source_inverse_dsp"):
                del children["rfft_1000ef64"]
                children["cfft_q15_1000f1d4"] = "0x1000f1d4"
                if mode == "source_rfft_wrapper":
                    children.update({
                        "split_rfft_q15_1000efd4": "0x1000efd4",
                        "split_rifft_q15_1000f068": "0x1000f068",
                    })
                elif mode in ("source_inverse_only", "source_inverse_dsp"):
                    children["split_rfft_q15_1000efd4"] = "0x1000efd4"
                elif mode == "source_rfft_split":
                    children["split_rifft_q15_1000f068"] = "0x1000f068"
            for name, address in children.items():
                args.append(f"-Wl,--defsym,gx8002_image_b_{name}={address}")
    args += ["-o", repo(elf), "process_native_oracle_start.S",
             "imcra_full_native_oracle_main.c", "process_native_oracle_stock.S"]
    if mode == "source":
        args.append(repo(Path(RECEIPT["linked_object"])))
    elif mode != "native":
        for name in (
            "process_prefix", "adaptive_prefix", "minimum_smoothing",
            "minimum_flags", "flagged_smoothing", "gain_table",
            "noise_update", "history_rotate", "spectral_output",
            "cold_initialize", "process"
        ):
            args.append(repo(BUILD / f"backup_stage2_imcra_{name}.o"))
        if mode in ("source_rfft_wrapper", "source_rfft_split", "source_inverse_only", "source_inverse_dsp"):
            args.append(repo(BUILD / "backup_rfft_q15.o"))
        if mode == "source_rfft_split":
            args.append(repo(BUILD / "backup_rfft_split_sdk.o"))
        if mode == "source_inverse_only":
            source = HERE / "imcra_source_inverse_only.c"
            obj = HERE / "imcra_source_inverse_only.o"
            run_docker(["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
                        "-mhard-float", "-O2",
                        "-I/repo/third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include",
                        "-I/repo/third-party/upstream/nationalchip-lvp-kws/include",
                        "-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility/libdsp",
                        "-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility",
                        "-c", repo(source),
                        "-o", repo(obj)], "opencfw/iar-base:10.10.2-local")
            args.append(repo(obj))
        if mode == "source_inverse_dsp":
            args.append(repo(HERE / "imcra_inverse_dsp_trial.o"))
    run_docker(args, "opencfw/iar-base:10.10.2-local")
    return elf

def execute(elf: Path) -> list[int]:
    command = ["docker", "run", "--rm", "--network=none",
               "-v", f"{ROOT}:/repo", "-w", "/repo",
               "opencfw/qemu-csky-builddeps:20261009t201800", "sh", "-lc",
               f"timeout 15s {repo(QEMU)} -M virt -m 1G -cpu ck804ef "
               f"-nographic -monitor none -kernel {repo(elf)} "
               "-d guest_errors -D /tmp/imcra-full.log; cat /tmp/imcra-full.log"]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=30, check=True)
    log = result.stdout + result.stderr
    if "csky_exit_write: exit(0)" not in log:
        raise RuntimeError(log)
    return [int(word, 0) for word in re.findall(
        r"label: (0x[0-9a-fA-F]+|[0-9]+)", log)]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--mode", type=int, choices=(1, 2), default=2)
    parser.add_argument("--signal", type=int, choices=(1, 2), default=1)
    parser.add_argument("--build-receipt", type=Path,
                        help="source-coherent alternate selected image-B archive")
    parser.add_argument("--source-only", action="store_true",
                        help="compare only full sourced body and native original")
    options = parser.parse_args()
    global BUILD, RECEIPT
    if options.build_receipt:
        BUILD = options.build_receipt.resolve().parent
        RECEIPT = json.loads(options.build_receipt.read_text())
    frames = options.frames
    case_mode = options.mode
    signal = options.signal
    native = execute(build("native", frames, case_mode, signal))
    source = execute(build("source", frames, case_mode, signal))
    if options.source_only:
        receipt = {
            "native": native, "source": source,
            "matching_words": sum(a == b for a, b in zip(native, source)),
            "native_words": len(native), "source_words": len(source),
            "source_archive_sha256": RECEIPT["linked_object_sha256"],
            "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
            "scope": f"{frames} frame(s), mode {case_mode}, signal {signal}, full sourced QEMU 89-word fixture",
        }
        receipt["result"] = "PASS" if len(native) == len(source) == 89 and native == source else "FAIL"
        path = HERE / f"imcra-full-{BUILD.name}-{frames}frame-mode{case_mode}-signal{signal}-receipt.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n")
        print(path)
        print(receipt["result"], receipt["matching_words"])
        return
    source_native_children = execute(build("source_native_children", frames, case_mode, signal))
    source_rfft_wrapper = execute(build("source_rfft_wrapper", frames, case_mode, signal))
    source_rfft_split = execute(build("source_rfft_split", frames, case_mode, signal))
    source_inverse_only = execute(build("source_inverse_only", frames, case_mode, signal))
    source_inverse_dsp = execute(build("source_inverse_dsp", frames, case_mode, signal))
    receipt = {
        "native": native, "source": source,
        "source_native_children": source_native_children,
        "source_rfft_wrapper": source_rfft_wrapper,
        "source_rfft_split": source_rfft_split,
        "source_inverse_only": source_inverse_only,
        "source_inverse_dsp": source_inverse_dsp,
        "matching_words": sum(a == b for a, b in zip(native, source)),
        "matching_words_native_children": sum(
            a == b for a, b in zip(native, source_native_children)),
        "matching_words_rfft_wrapper": sum(
            a == b for a, b in zip(native, source_rfft_wrapper)),
        "matching_words_rfft_split": sum(
            a == b for a, b in zip(native, source_rfft_split)),
        "matching_words_inverse_only": sum(
            a == b for a, b in zip(native, source_inverse_only)),
        "matching_words_inverse_dsp": sum(
            a == b for a, b in zip(native, source_inverse_dsp)),
        "native_words": len(native), "source_words": len(source),
        "source_archive_sha256": RECEIPT["linked_object_sha256"],
        "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
        "scope": f"{frames} frame(s), mode {case_mode}, signal {signal}, 512-point full-call QEMU fixture; counter, eight output samples, four energy words, four gain-table words, four gain words, four adaptive words, 16 spectrum halfwords, 16 work halfwords, eight residual halfwords, eight residual-before halfwords, eight window halfwords, eight output-window halfwords",
    }
    receipt["result"] = "PASS" if len(native) == len(source) == 89 and native == source else "FAIL"
    receipt["parent_body_result"] = "PASS" if len(native) == len(source_native_children) == 89 and native == source_native_children else "FAIL"
    receipt["rfft_wrapper_result"] = "PASS" if len(native) == len(source_rfft_wrapper) == 89 and native == source_rfft_wrapper else "FAIL"
    receipt["rfft_split_result"] = "PASS" if len(native) == len(source_rfft_split) == 89 and native == source_rfft_split else "FAIL"
    receipt["inverse_only_result"] = "PASS" if len(native) == len(source_inverse_only) == 89 and native == source_inverse_only else "FAIL"
    receipt["inverse_dsp_result"] = "PASS" if len(native) == len(source_inverse_dsp) == 89 and native == source_inverse_dsp else "FAIL"
    path = HERE / f"imcra-full-qemu-{frames}frame-mode{case_mode}-signal{signal}-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)
    print(receipt["result"], receipt["matching_words"],
          receipt["parent_body_result"], receipt["matching_words_native_children"],
          receipt["rfft_wrapper_result"], receipt["matching_words_rfft_wrapper"],
          receipt["rfft_split_result"], receipt["matching_words_rfft_split"],
          receipt["inverse_only_result"], receipt["matching_words_inverse_only"],
          receipt["inverse_dsp_result"], receipt["matching_words_inverse_dsp"],
          len(native), len(source))

if __name__ == "__main__":
    main()

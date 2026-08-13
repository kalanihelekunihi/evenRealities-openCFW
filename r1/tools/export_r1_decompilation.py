#!/usr/bin/env python3
"""Generate the complete local R1 application/bootloader decompilation corpus.

The script is offline and read-only with respect to firmware and hardware. Generated analysis and
rebuild artifacts are written beneath research/decompilation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "research" / "decompilation"
SCRIPT_DIR = REPO_ROOT / "tools"
APPLICATION = REPO_ROOT / "research" / "decompilation" / "rebuild" / "rebuilt-application.bin"
BOOTLOADER = REPO_ROOT / "research" / "decompilation" / "rebuild" / "rebuilt-bootloader.bin"
UICR = REPO_ROOT / "research" / "decompilation" / "rebuild" / "rebuilt-uicr.bin"
APPROTECT = (
    REPO_ROOT
    / "firmware"
    / "analysis"
    / "r1-live-2026-08-10"
    / "r1-approtect-runtime-live.bin"
)

EXPECTED_SHA256 = {
    APPLICATION: "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a",
    BOOTLOADER: "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b",
    UICR: "1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150",
    APPROTECT: "fafdd44c03daf5f7ecfa57113ebd319de6fb8f84fa0b7b0c5ac60d09f811fb71",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_inputs() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.is_file():
            raise SystemExit(f"missing required R1 artifact: {path}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA-256 mismatch for {path}: expected {expected}, got {actual}")


def find_headless() -> Path:
    explicit = os.environ.get("GHIDRA_HEADLESS")
    candidates = [
        Path(explicit) if explicit else None,
        Path("/opt/homebrew/opt/ghidra/libexec/support/analyzeHeadless"),
        Path("/usr/local/opt/ghidra/libexec/support/analyzeHeadless"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    executable = shutil.which("analyzeHeadless")
    if executable:
        return Path(executable)
    raise SystemExit("Ghidra analyzeHeadless not found; set GHIDRA_HEADLESS")


def run_ghidra(
    headless: Path,
    project_root: Path,
    image: Path,
    base: str,
    init_script: str,
    label: str,
    output_root: Path,
    overwrite: bool,
) -> None:
    target = output_root / label
    target.mkdir(parents=True, exist_ok=True)
    project_name = f"r1-{label}"
    project_file = project_root / f"{project_name}.gpr"
    isolated_scripts = project_root / "analysis-scripts"
    isolated_scripts.mkdir(parents=True, exist_ok=True)
    for script_name in (
        "R1Init.java",
        "R1BootInit.java",
        "R1BootloaderSeedKnownFunctions.java",
        "R1WholeImageExport.java",
    ):
        shutil.copy2(SCRIPT_DIR / script_name, isolated_scripts / script_name)

    def process_command() -> list[str]:
        result = [
            str(headless),
            str(project_root),
            project_name,
            "-process",
            image.name,
            "-scriptPath",
            str(isolated_scripts),
        ]
        if label == "bootloader":
            result.extend(["-preScript", "R1BootloaderSeedKnownFunctions.java"])
        result.extend([
            "-postScript",
            "R1WholeImageExport.java",
            str(target),
            label,
        ])
        return result

    if project_file.exists() and not overwrite:
        command = process_command()
    else:
        if overwrite:
            for candidate in (project_file, project_root / f"{project_name}.rep"):
                if candidate.is_dir():
                    shutil.rmtree(candidate)
                elif candidate.exists():
                    candidate.unlink()
        command = [
            str(headless),
            str(project_root),
            project_name,
            "-import",
            str(image),
            "-processor",
            "ARM:LE:32:Cortex",
            "-cspec",
            "default",
            "-loader",
            "BinaryLoader",
            "-loader-baseAddr",
            base,
            "-scriptPath",
            str(isolated_scripts),
            "-preScript",
            init_script,
        ]
        if label == "bootloader":
            command.extend(["-preScript", "R1BootloaderSeedKnownFunctions.java"])
        command.extend([
            "-postScript",
            "R1WholeImageExport.java",
            str(target),
            label,
        ])
    environment = os.environ.copy()
    if not environment.get("JAVA_HOME"):
        java_homes = (
            Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"),
            Path("/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"),
        )
        for java_home in java_homes:
            if java_home.is_dir():
                environment["JAVA_HOME"] = str(java_home)
                environment["PATH"] = str(java_home / "bin") + os.pathsep + environment.get(
                    "PATH", ""
                )
                break
    previous_count = None
    for pass_index in range(8):
        subprocess.run(command, cwd=REPO_ROOT, check=True, env=environment)
        summary_path = target / "analysis-summary.json"
        if not summary_path.is_file():
            raise SystemExit(f"Ghidra did not produce {summary_path}")
        function_count = int(json.loads(summary_path.read_text())["function_count"])
        if previous_count == function_count:
            return
        previous_count = function_count
        command = process_command()
    raise SystemExit(f"Ghidra function analysis did not reach a fixed point for {label}")


def c_identifier(label: str) -> str:
    return "r1_" + "".join(character if character.isalnum() else "_" for character in label)


def write_byte_include(source: Path, destination: Path) -> None:
    data = source.read_bytes()
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for offset in range(0, len(data), 16):
            chunk = data[offset : offset + 16]
            handle.write("    ")
            handle.write(", ".join(f"0x{value:02x}" for value in chunk))
            handle.write(",\n")


def generate_rebuild(output_root: Path) -> None:
    rebuild = output_root / "rebuild"
    rebuild.mkdir(parents=True, exist_ok=True)
    images = {
        "application": APPLICATION,
        "bootloader": BOOTLOADER,
        "uicr": UICR,
        "approtect-runtime": APPROTECT,
    }
    manifest: dict[str, object] = {"format": 1, "images": {}}
    declarations: list[str] = []
    table_rows: list[str] = []
    for label, source in images.items():
        identifier = c_identifier(label)
        include_name = f"{label}.bytes.inc"
        write_byte_include(source, rebuild / include_name)
        declarations.append(
            f"static const unsigned char {identifier}[] = {{\n"
            f'#include "{include_name}"\n'
            "};\n"
        )
        table_rows.append(
            f'    {{"{label}", {identifier}, sizeof({identifier}), "{sha256(source)}"}},'
        )
        manifest["images"][label] = {
            "bytes": source.stat().st_size,
            "sha256": sha256(source),
            "source": str(source.relative_to(REPO_ROOT)),
            "signing_material_included": False,
        }

    emitter = """/* Generated exact-byte unsigned R1 image emitter. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

""" + "\n".join(declarations) + """
struct image_record {
    const char *name;
    const unsigned char *bytes;
    size_t size;
    const char *sha256;
};

static const struct image_record images[] = {
""" + "\n".join(table_rows) + """
};

static void usage(const char *program) {
    fprintf(stderr, "usage: %s IMAGE OUTPUT\\nimages:", program);
    for (size_t i = 0; i < sizeof(images) / sizeof(images[0]); ++i) {
        fprintf(stderr, " %s", images[i].name);
    }
    fputc('\\n', stderr);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        usage(argv[0]);
        return 64;
    }
    const struct image_record *selected = NULL;
    for (size_t i = 0; i < sizeof(images) / sizeof(images[0]); ++i) {
        if (strcmp(argv[1], images[i].name) == 0) {
            selected = &images[i];
            break;
        }
    }
    if (selected == NULL) {
        usage(argv[0]);
        return 64;
    }
    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        fprintf(stderr, "cannot open %s: %s\\n", argv[2], strerror(errno));
        return 1;
    }
    size_t written = fwrite(selected->bytes, 1, selected->size, output);
    int close_result = fclose(output);
    if (written != selected->size || close_result != 0) {
        fprintf(stderr, "failed writing %s\\n", argv[2]);
        return 1;
    }
    fprintf(stderr, "%s: %zu bytes; expected SHA-256 %s\\n",
            selected->name, selected->size, selected->sha256);
    return 0;
}
"""
    (rebuild / "emit_image.c").write_text(emitter, encoding="utf-8")
    (rebuild / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    makefile = """CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror

.PHONY: all verify clean

all: emit_image

emit_image: emit_image.c application.bytes.inc bootloader.bytes.inc uicr.bytes.inc approtect-runtime.bytes.inc
	$(CC) $(CFLAGS) emit_image.c -o $@

verify: emit_image
	./verify.py

clean:
	rm -f emit_image rebuilt-*.bin
"""
    (rebuild / "Makefile").write_text(makefile, encoding="utf-8")
    verifier = """#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text())
for name, metadata in manifest["images"].items():
    output = root / f"rebuilt-{name}.bin"
    subprocess.run([str(root / "emit_image"), name, str(output)], check=True)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if digest != metadata["sha256"] or output.stat().st_size != metadata["bytes"]:
        raise SystemExit(f"verification failed for {name}")
    print(f"verified {name}: {metadata['bytes']} bytes {digest}")
"""
    verifier_path = rebuild / "verify.py"
    verifier_path.write_text(verifier, encoding="utf-8")
    verifier_path.chmod(0o755)


def write_inventory(output_root: Path) -> None:
    rows = ["artifact,load_address,bytes,sha256,role,signing_material"]
    entries = [
        (APPLICATION, "0x00027000", "OTA application payload", "no"),
        (BOOTLOADER, "0x000f8000", "live bootloader flash span", "contains public verification key; no private key/signature"),
        (UICR, "0x10001000", "live UICR snapshot", "no"),
        (APPROTECT, "mixed runtime registers", "live protection-state words", "no"),
    ]
    for path, address, role, signing in entries:
        rows.append(
            f"{path.relative_to(REPO_ROOT)},{address},{path.stat().st_size},{sha256(path)},{role},{signing}"
        )
    (output_root / "artifact-inventory.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def normalize_generated_text(output_root: Path) -> None:
    text_suffixes = {".c", ".csv", ".inc", ".json", ".md", ".py", ".s"}
    for path in output_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        content = path.read_text(encoding="utf-8")
        normalized = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        if normalized != content:
            path.write_text(normalized, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-ghidra", action="store_true")
    parser.add_argument("--overwrite-projects", action="store_true")
    arguments = parser.parse_args()

    require_inputs()
    output_root = arguments.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    write_inventory(output_root)
    generate_rebuild(output_root)

    if not arguments.skip_ghidra:
        headless = find_headless()
        project_root = REPO_ROOT / "build" / "r1-ghidra-projects"
        project_root.mkdir(parents=True, exist_ok=True)
        run_ghidra(
            headless,
            project_root,
            APPLICATION,
            "0x00027000",
            "R1Init.java",
            "application",
            output_root,
            arguments.overwrite_projects,
        )
        run_ghidra(
            headless,
            project_root,
            BOOTLOADER,
            "0x000f8000",
            "R1BootInit.java",
            "bootloader",
            output_root,
            arguments.overwrite_projects,
        )
    normalize_generated_text(output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

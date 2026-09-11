#!/usr/bin/env python3
"""Generate nanopb message-descriptor C source from a source `.proto` file.

XC-005 host tooling: an Apollo protobuf descriptor data region (the
`pb_msgdesc_t`/field-table bytes nanopb emits for a message type) should be
reconstructed as a documented `.proto` schema plus the real, version-pinned
nanopb generator, not as an opaque byte array. The schema is the AD-* item's
job to author (recovering field numbers/types/names from the decoder call
sites the matching `nanopb-*` audit already establishes) and license.

This wraps two *external* host build tools, deliberately not vendored into
this repository (the same treatment already given to the C compiler and to
`protoc` itself, see `tools/detect_toolchain.py`):

  * `protoc`               - compiles the `.proto` into a `FileDescriptorSet`
  * the `nanopb` PyPI package - the reference nanopb generator, at the exact
                                 version already vendored as this repo's
                                 nanopb runtime (`third_party/nanopb`, Zlib
                                 license, tag `nanopb-0.4.9`,
                                 commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`)

Both are required at generation time; this tool fails closed (does not fall
back to any retained bytes) if either is missing or at the wrong version, so
a mismatch can never be silently absorbed into a build.

Install: `pip install nanopb==0.4.9` (or `pip install -r
g2/tools/requirements-assetgen.txt`).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED_NANOPB_VERSION = "0.4.9"
# Matches third_party/nanopb/PROVENANCE.json ("selected_tag"/"selected_commit").
REQUIRED_NANOPB_TAG = "nanopb-0.4.9"
REQUIRED_NANOPB_COMMIT = "98bf4db69897b53434f3d0ba72e0a3ab1a902824"


class AssetGenError(Exception):
    pass


def _require_protoc() -> str:
    protoc = shutil.which("protoc")
    if protoc is None:
        raise AssetGenError("protoc not found on PATH; install the protobuf compiler")
    return protoc


def _require_nanopb_generator() -> Path:
    try:
        import nanopb  # type: ignore
    except ImportError as exc:
        raise AssetGenError(
            f"the 'nanopb' Python package is not installed; run "
            f"'pip install nanopb=={REQUIRED_NANOPB_VERSION}' to match "
            f"third_party/nanopb (tag {REQUIRED_NANOPB_TAG})"
        ) from exc
    version = getattr(nanopb, "__version__", None)
    if version is None:
        # 0.4.9 ships without a top-level __version__; confirm via metadata instead.
        try:
            from importlib.metadata import version as pkg_version
            version = pkg_version("nanopb")
        except Exception as exc:  # pragma: no cover - defensive
            raise AssetGenError("could not determine installed nanopb package version") from exc
    if version != REQUIRED_NANOPB_VERSION:
        raise AssetGenError(
            f"installed nanopb generator is {version!r}, but third_party/nanopb "
            f"pins {REQUIRED_NANOPB_TAG}; install nanopb=={REQUIRED_NANOPB_VERSION}"
        )
    generator = Path(nanopb.__file__).resolve().parent / "generator" / "nanopb_generator.py"
    if not generator.is_file():
        raise AssetGenError(f"nanopb package is missing its generator at {generator}")
    return generator


def generate(proto_path: Path, output_dir: Path, proto_search_path: Path | None = None) -> dict:
    """Compile `proto_path` into `<stem>.pb.c` / `<stem>.pb.h` under
    `output_dir`. Returns a small report dict. Raises AssetGenError and
    writes nothing on any failure (fail closed)."""
    protoc = _require_protoc()
    generator = _require_nanopb_generator()
    search_path = proto_search_path or proto_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="assetgen-nanopb-") as tmp:
        descriptor = Path(tmp) / (proto_path.stem + ".pb")
        protoc_result = subprocess.run(
            [protoc, f"-I{search_path}", f"-o{descriptor}", str(proto_path)],
            capture_output=True, text=True,
        )
        if protoc_result.returncode != 0:
            raise AssetGenError(f"protoc failed:\n{protoc_result.stderr}")

        gen_result = subprocess.run(
            [sys.executable, str(generator), "-q", "-T", "-D", str(output_dir), str(descriptor)],
            capture_output=True, text=True,
        )
        if gen_result.returncode != 0:
            raise AssetGenError(f"nanopb_generator.py failed:\n{gen_result.stderr}")

    header = output_dir / (proto_path.stem + ".pb.h")
    source = output_dir / (proto_path.stem + ".pb.c")
    if not header.is_file() or not source.is_file():
        raise AssetGenError(f"expected {header} and {source} were not produced")
    return {
        "header": str(header), "source": str(source),
        "header_bytes": header.stat().st_size, "source_bytes": source.stat().st_size,
        "nanopb_version": REQUIRED_NANOPB_VERSION,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proto", type=Path, help="source .proto schema")
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("-I", "--proto-path", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        report = generate(args.proto, args.output_dir, args.proto_path)
    except AssetGenError as exc:
        print(f"assetgen_nanopb_descriptor: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {report['source']} ({report['source_bytes']} bytes) and {report['header']} ({report['header_bytes']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

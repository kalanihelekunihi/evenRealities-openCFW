#!/usr/bin/env python3
"""Generate and verify the transparent R1 model-data C initializer."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
DEFAULT_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_model_data_generated.inc"
)
DEFAULT_HRV_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_hrv_weighted_generated.inc"
)
DEFAULT_HBA_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_hba_generated.inc"
)
DEFAULT_HBA_CONFIGURATION_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_hba_configuration_generated.inc"
)
DEFAULT_SPO2_CONFIGURATION_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_spo2_configuration_generated.inc"
)
DEFAULT_SPO2_SCALE_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_spo2_scale_generated.inc"
)
DEFAULT_SPO2_SPECTRAL_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_spo2_spectral_generated.inc"
)
DEFAULT_HBA_SCHEMA_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_goodix_hba_schema_generated.inc"
)
LOAD_BASE = 0x00027000
IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
MODEL_START = 0x000B19E4
MODEL_END = 0x000BCED8
MODEL_SHA256 = "cde455f534ef8528509bca8e7c65460af63187d835274ec4fa007ce1811dd470"
SPO2_CONFIGURATION_START = 0x000AD160
SPO2_CONFIGURATION_END = 0x000AD1AC
SPO2_CONFIGURATION_SHA256 = (
    "afa9429b02ee229c0363000ebc02be13b51ec6ac0e5b9c06d621947d65eb7fe5"
)
HBA_CONFIGURATION_START = 0x000AD13C
HBA_CONFIGURATION_END = 0x000AD160
HBA_CONFIGURATION_SHA256 = (
    "9c1f99d4a578e6a23b6309b25f6bbfc568c9b7dafad7a32ba3e7fe44c61fea99"
)
# The retail startup record at 0x000C43EC expands the compressed image at
# 0x000C4610 into 0x200064A8..<0x20007E04.  Decoder 0x000335B4 loads its
# table-bank anchor from the literal at 0x000337C8 (0x20007D68).  Its three
# bases are anchor, anchor - 0x58, and anchor - 0x24.  The adjacent numeric
# sequences and the scale-code domains establish exact counts 8, 13, and 9.
INITIALIZED_DATA_COMPRESSED_START = 0x000C4610
INITIALIZED_DATA_RAM_START = 0x200064A8
INITIALIZED_DATA_BYTE_COUNT = 0x195C
INITIALIZED_DATA_SHA256 = (
    "87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317"
)
SPO2_SCALE_TABLES = (
    ("mode-0 scale table", 0x20007D68, 8,
     "6c7c02b6133965defad895eb8c1419c20569209c78b1dac39d7cae92cf571fe6"),
    ("mode-1 scale table", 0x20007D10, 13,
     "486ca77bc848823385797ecad2e56c97143ac2e28b164cc59bc54b844f7d220e"),
    ("mode-2 scale table", 0x20007D44, 9,
     "bd29af4660d18dd81a6e49402dbd88506ce1d02747b37a82941a0a3b74072e28"),
)
# 0x00032744 loads the factor through the literal at 0x00032784 and the
# 125-word mode-one scale vector through 0x00032780.  Those literals resolve
# to the adjacent non-executable Float32 data at 0x000BD450..<0x000BD648.
SPO2_SPECTRAL_START = 0x000BD450
SPO2_SPECTRAL_END = 0x000BD648
SPO2_SPECTRAL_SHA256 = (
    "da778a0dcc9f120630d6cf7d708abfbfe130d342e9e89c6f0efe5f1713e14851"
)
HBA_TAIL_SCHEMA_START = 0x20007D98
HBA_TAIL_SCHEMA_END = 0x20007DB0
HBA_TAIL_SCHEMA_SHA256 = (
    "97704368684bc6840c5549e1f37ef63c16d923e86374c4be93e297a0d664b59d"
)
HRV_WEIGHTED_START = 0x000B0F8C
HRV_WEIGHTED_END = 0x000B149C
HRV_WEIGHTED_SHA256 = (
    "86e5fe43c9800e3ac192bf96bf1c1166e161738404c270937a1cc0ce45d4e5af"
)
HRV_CURVE_START = 0x000B14FC
HRV_CURVE_END = 0x000B151C
HRV_CURVE_SHA256 = (
    "976be3d9fd848a0b792a7d6c06b3c31211d0cc8579296b275553dc89cdc315d7"
)
HBA_REGIONS = (
    (
        "mode-1 complete model arena",
        0x0009D640,
        0x000A04CC,
        "42b5f4af036691b1ba7c00e80f7d46cd3ed7f13794447230f85c6a640a1a1f95",
    ),
    (
        "mode-0 descriptor/remap",
        0x000A04CC,
        0x000A50B0,
        "2f7f29d655d9743d95d5d5a5f6c9b192833663dd8a59066b5abfb789852be49e",
    ),
    (
        "second Goodix graph",
        0x000A50B0,
        0x000A692C,
        "4037e6445e0234932bbfbd5584b387be5152541b17db8219f612bb1c661d6715",
    ),
    (
        "mode-0 complete model arena",
        0x000A692C,
        0x000AD13C,
        "9e77da9a55d62e8a156073f323b6e3b11536ebaff32edf369f6072297b2adbc1",
    ),
    (
        "stream filter coefficients",
        0x000B0F0C,
        0x000B0F5C,
        "fb1e5e2a6d67f5bd3d802808a1c7db954c81f1d699412dca2e9353c89e86fb90",
    ),
)
VIEWS = {
    "Goodix generated model": (
        0x000B19E4,
        0x000B5734,
        "655f94539fd186e8c99d5e616c296dba63b247a114963870c044798cd75fef47",
    ),
    "GoMore sleep model below 100": (
        0x000B2458,
        0x000B7998,
        "da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861",
    ),
    "GoMore sleep model 100 and above": (
        0x000B7998,
        0x000BCED8,
        "09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c",
    ),
}


def recovered_region(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[MODEL_START - LOAD_BASE:MODEL_END - LOAD_BASE]
    if len(region) != MODEL_END - MODEL_START or \
            hashlib.sha256(region).hexdigest() != MODEL_SHA256:
        raise ValueError("recovered model-region extent or SHA-256 changed")
    for name, (start, end, expected) in VIEWS.items():
        data = image[start - LOAD_BASE:end - LOAD_BASE]
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"{name} SHA-256 changed")
    return region


def recovered_hrv_weighted_region(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[
        HRV_WEIGHTED_START - LOAD_BASE:HRV_WEIGHTED_END - LOAD_BASE
    ]
    if len(region) != HRV_WEIGHTED_END - HRV_WEIGHTED_START or \
            hashlib.sha256(region).hexdigest() != HRV_WEIGHTED_SHA256:
        raise ValueError("recovered GH_HRV coefficient extent or SHA-256 changed")
    curve = image[HRV_CURVE_START - LOAD_BASE:HRV_CURVE_END - LOAD_BASE]
    if len(curve) != HRV_CURVE_END - HRV_CURVE_START or \
            hashlib.sha256(curve).hexdigest() != HRV_CURVE_SHA256:
        raise ValueError("recovered GH_HRV curve extent or SHA-256 changed")
    return region


def recovered_hba_regions(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    recovered = bytearray()
    for name, start, end, expected in HBA_REGIONS:
        region = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(region) != end - start or \
                hashlib.sha256(region).hexdigest() != expected:
            raise ValueError(f"recovered HBA {name} extent or SHA-256 changed")
        recovered.extend(region)
    return bytes(recovered)


def recovered_spo2_configuration(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[
        SPO2_CONFIGURATION_START - LOAD_BASE:
        SPO2_CONFIGURATION_END - LOAD_BASE
    ]
    if len(region) != SPO2_CONFIGURATION_END - SPO2_CONFIGURATION_START or \
            hashlib.sha256(region).hexdigest() != SPO2_CONFIGURATION_SHA256:
        raise ValueError(
            "recovered GH_SPO2 configuration extent or SHA-256 changed"
        )
    return region


def recovered_hba_configuration(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[
        HBA_CONFIGURATION_START - LOAD_BASE:
        HBA_CONFIGURATION_END - LOAD_BASE
    ]
    if len(region) != HBA_CONFIGURATION_END - HBA_CONFIGURATION_START or \
            hashlib.sha256(region).hexdigest() != HBA_CONFIGURATION_SHA256:
        raise ValueError(
            "recovered GH_HBA configuration extent or SHA-256 changed"
        )
    return region


def recovered_initialized_data(image_path: Path) -> bytes:
    """Expand the exact compact initialized-data stream used by startup."""
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    cursor = INITIALIZED_DATA_COMPRESSED_START - LOAD_BASE
    output = bytearray()
    while len(output) < INITIALIZED_DATA_BYTE_COUNT:
        token = image[cursor]
        cursor += 1
        literal_count = token & 7
        if literal_count == 0:
            literal_count = image[cursor]
            cursor += 1
        run_count = token >> 4
        if run_count == 0:
            run_count = image[cursor]
            cursor += 1
        # 0x286F4 decrements before copying, so the encoded literal length
        # includes the token-owned sentinel byte.
        literal_bytes = literal_count - 1
        output.extend(image[cursor:cursor + literal_bytes])
        cursor += literal_bytes
        if token & 8:
            distance = image[cursor]
            cursor += 1
            if distance == 0 or distance > len(output):
                raise ValueError("invalid initialized-data back-reference")
            for _ in range(run_count + 2):
                output.append(output[-distance])
        else:
            output.extend(bytes(run_count))
    if len(output) != INITIALIZED_DATA_BYTE_COUNT or \
            hashlib.sha256(output).hexdigest() != INITIALIZED_DATA_SHA256:
        raise ValueError("initialized-data expansion or SHA-256 changed")
    return bytes(output)


def recovered_spo2_scale_tables(image_path: Path) -> bytes:
    initialized = recovered_initialized_data(image_path)
    recovered = bytearray()
    for name, ram_start, word_count, expected in SPO2_SCALE_TABLES:
        offset = ram_start - INITIALIZED_DATA_RAM_START
        region = initialized[offset:offset + word_count * 4]
        if len(region) != word_count * 4 or \
                hashlib.sha256(region).hexdigest() != expected:
            raise ValueError(f"recovered GH_SPO2 {name} changed")
        recovered.extend(region)
    return bytes(recovered)


def recovered_spo2_spectral_constants(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[
        SPO2_SPECTRAL_START - LOAD_BASE:SPO2_SPECTRAL_END - LOAD_BASE
    ]
    if len(region) != SPO2_SPECTRAL_END - SPO2_SPECTRAL_START or \
            hashlib.sha256(region).hexdigest() != SPO2_SPECTRAL_SHA256:
        raise ValueError("recovered GH_SPO2 spectral constants changed")
    return region


def recovered_hba_tail_schema(image_path: Path) -> bytes:
    initialized = recovered_initialized_data(image_path)
    offset = HBA_TAIL_SCHEMA_START - INITIALIZED_DATA_RAM_START
    region = initialized[offset:offset + HBA_TAIL_SCHEMA_END -
                         HBA_TAIL_SCHEMA_START]
    if len(region) != HBA_TAIL_SCHEMA_END - HBA_TAIL_SCHEMA_START or \
            hashlib.sha256(region).hexdigest() != HBA_TAIL_SCHEMA_SHA256:
        raise ValueError("recovered GH_HBA tail schema changed")
    return region


def render(region: bytes, label: str = "model-data",
           start: int = MODEL_START, end: int = MODEL_END) -> str:
    if len(region) % 4:
        raise ValueError("model region is not word aligned")
    words = struct.unpack(f"<{len(region) // 4}I", region)
    lines = [
        f"/* Generated from the SHA-pinned Ghidra {label} region",
        f" * 0x{start:08X}..<0x{end:08X}.  Do not edit by hand. */",
    ]
    for offset in range(0, len(words), 6):
        values = ", ".join(
            f"UINT32_C(0x{word:08X})" for word in words[offset:offset + 6]
        )
        lines.append(f"    {values},")
    return "\n".join(lines) + "\n"


def render_bytes(region: bytes, label: str, start: int, end: int) -> str:
    lines = [
        f"/* Generated from the SHA-pinned Ghidra {label} region",
        f" * 0x{start:08X}..<0x{end:08X}.  Do not edit by hand. */",
    ]
    for offset in range(0, len(region), 12):
        values = ", ".join(
            f"UINT8_C(0x{value:02X})" for value in region[offset:offset + 12]
        )
        lines.append(f"    {values},")
    return "\n".join(lines) + "\n"


def verify(image_path: Path = DEFAULT_IMAGE,
           output_path: Path = DEFAULT_OUTPUT,
           hrv_output_path: Path = DEFAULT_HRV_OUTPUT,
           hba_output_path: Path = DEFAULT_HBA_OUTPUT,
           hba_configuration_output_path: Path =
               DEFAULT_HBA_CONFIGURATION_OUTPUT,
           spo2_configuration_output_path: Path =
               DEFAULT_SPO2_CONFIGURATION_OUTPUT,
           spo2_scale_output_path: Path = DEFAULT_SPO2_SCALE_OUTPUT,
           spo2_spectral_output_path: Path = DEFAULT_SPO2_SPECTRAL_OUTPUT,
           hba_schema_output_path: Path = DEFAULT_HBA_SCHEMA_OUTPUT) -> None:
    expected = render(recovered_region(image_path))
    if not output_path.is_file() or output_path.read_text() != expected:
        raise AssertionError(
            f"transparent model-data initializer is stale: {output_path}"
        )
    expected_hrv = render(
        recovered_hrv_weighted_region(image_path), "GH_HRV coefficient",
        HRV_WEIGHTED_START, HRV_WEIGHTED_END)
    if not hrv_output_path.is_file() or \
            hrv_output_path.read_text() != expected_hrv:
        raise AssertionError(
            f"transparent GH_HRV coefficient initializer is stale: "
            f"{hrv_output_path}"
        )
    expected_hba = render(
        recovered_hba_regions(image_path), "GH_HBA initializer data",
        HBA_REGIONS[0][1], HBA_REGIONS[-1][2])
    if not hba_output_path.is_file() or \
            hba_output_path.read_text() != expected_hba:
        raise AssertionError(
            f"transparent GH_HBA initializer data is stale: "
            f"{hba_output_path}"
        )
    expected_hba_configuration = render(
        recovered_hba_configuration(image_path), "GH_HBA configuration",
        HBA_CONFIGURATION_START, HBA_CONFIGURATION_END)
    if not hba_configuration_output_path.is_file() or \
            hba_configuration_output_path.read_text() != \
            expected_hba_configuration:
        raise AssertionError(
            f"transparent GH_HBA configuration is stale: "
            f"{hba_configuration_output_path}"
        )
    expected_spo2_configuration = render_bytes(
        recovered_spo2_configuration(image_path), "GH_SPO2 configuration",
        SPO2_CONFIGURATION_START, SPO2_CONFIGURATION_END)
    if not spo2_configuration_output_path.is_file() or \
            spo2_configuration_output_path.read_text() != \
            expected_spo2_configuration:
        raise AssertionError(
            f"transparent GH_SPO2 configuration is stale: "
            f"{spo2_configuration_output_path}"
        )
    expected_spo2_scale = render(
        recovered_spo2_scale_tables(image_path),
        "GH_SPO2 initialized-RAM scale tables",
        min(table[1] for table in SPO2_SCALE_TABLES),
        max(table[1] + table[2] * 4 for table in SPO2_SCALE_TABLES))
    if not spo2_scale_output_path.is_file() or \
            spo2_scale_output_path.read_text() != expected_spo2_scale:
        raise AssertionError(
            f"transparent GH_SPO2 scale tables are stale: "
            f"{spo2_scale_output_path}"
        )
    expected_spo2_spectral = render(
        recovered_spo2_spectral_constants(image_path),
        "GH_SPO2 spectral factor and mode-one scales",
        SPO2_SPECTRAL_START, SPO2_SPECTRAL_END)
    if not spo2_spectral_output_path.is_file() or \
            spo2_spectral_output_path.read_text() != expected_spo2_spectral:
        raise AssertionError(
            f"transparent GH_SPO2 spectral constants are stale: "
            f"{spo2_spectral_output_path}"
        )
    expected_hba_schema = render_bytes(
        recovered_hba_tail_schema(image_path),
        "GH_HBA initialized-RAM tail schema",
        HBA_TAIL_SCHEMA_START, HBA_TAIL_SCHEMA_END)
    if not hba_schema_output_path.is_file() or \
            hba_schema_output_path.read_text() != expected_hba_schema:
        raise AssertionError(
            f"transparent GH_HBA tail schema is stale: "
            f"{hba_schema_output_path}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hrv-output", type=Path, default=DEFAULT_HRV_OUTPUT)
    parser.add_argument("--hba-output", type=Path, default=DEFAULT_HBA_OUTPUT)
    parser.add_argument(
        "--hba-configuration-output", type=Path,
        default=DEFAULT_HBA_CONFIGURATION_OUTPUT)
    parser.add_argument(
        "--spo2-configuration-output", type=Path,
        default=DEFAULT_SPO2_CONFIGURATION_OUTPUT)
    parser.add_argument(
        "--spo2-scale-output", type=Path,
        default=DEFAULT_SPO2_SCALE_OUTPUT)
    parser.add_argument(
        "--spo2-spectral-output", type=Path,
        default=DEFAULT_SPO2_SPECTRAL_OUTPUT)
    parser.add_argument(
        "--hba-schema-output", type=Path,
        default=DEFAULT_HBA_SCHEMA_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render(recovered_region(args.image))
    generated_hrv = render(
        recovered_hrv_weighted_region(args.image), "GH_HRV coefficient",
        HRV_WEIGHTED_START, HRV_WEIGHTED_END)
    generated_hba = render(
        recovered_hba_regions(args.image), "GH_HBA initializer data",
        HBA_REGIONS[0][1], HBA_REGIONS[-1][2])
    generated_hba_configuration = render(
        recovered_hba_configuration(args.image), "GH_HBA configuration",
        HBA_CONFIGURATION_START, HBA_CONFIGURATION_END)
    generated_spo2_configuration = render_bytes(
        recovered_spo2_configuration(args.image), "GH_SPO2 configuration",
        SPO2_CONFIGURATION_START, SPO2_CONFIGURATION_END)
    generated_spo2_scale = render(
        recovered_spo2_scale_tables(args.image),
        "GH_SPO2 initialized-RAM scale tables",
        min(table[1] for table in SPO2_SCALE_TABLES),
        max(table[1] + table[2] * 4 for table in SPO2_SCALE_TABLES))
    generated_spo2_spectral = render(
        recovered_spo2_spectral_constants(args.image),
        "GH_SPO2 spectral factor and mode-one scales",
        SPO2_SPECTRAL_START, SPO2_SPECTRAL_END)
    generated_hba_schema = render_bytes(
        recovered_hba_tail_schema(args.image),
        "GH_HBA initialized-RAM tail schema",
        HBA_TAIL_SCHEMA_START, HBA_TAIL_SCHEMA_END)
    if args.check:
        if not args.output.is_file() or args.output.read_text() != generated:
            raise SystemExit(f"stale generated model data: {args.output}")
        if not args.hrv_output.is_file() or \
                args.hrv_output.read_text() != generated_hrv:
            raise SystemExit(
                f"stale generated GH_HRV coefficients: {args.hrv_output}"
            )
        if not args.hba_output.is_file() or \
                args.hba_output.read_text() != generated_hba:
            raise SystemExit(
                f"stale generated GH_HBA initializer data: {args.hba_output}"
            )
        if not args.hba_configuration_output.is_file() or \
                args.hba_configuration_output.read_text() != \
                generated_hba_configuration:
            raise SystemExit(
                "stale generated GH_HBA configuration: "
                f"{args.hba_configuration_output}"
            )
        if not args.spo2_configuration_output.is_file() or \
                args.spo2_configuration_output.read_text() != \
                generated_spo2_configuration:
            raise SystemExit(
                "stale generated GH_SPO2 configuration: "
                f"{args.spo2_configuration_output}"
            )
        if not args.spo2_scale_output.is_file() or \
                args.spo2_scale_output.read_text() != generated_spo2_scale:
            raise SystemExit(
                "stale generated GH_SPO2 scale tables: "
                f"{args.spo2_scale_output}"
            )
        if not args.spo2_spectral_output.is_file() or \
                args.spo2_spectral_output.read_text() != \
                generated_spo2_spectral:
            raise SystemExit(
                "stale generated GH_SPO2 spectral constants: "
                f"{args.spo2_spectral_output}"
            )
        if not args.hba_schema_output.is_file() or \
                args.hba_schema_output.read_text() != generated_hba_schema:
            raise SystemExit(
                "stale generated GH_HBA tail schema: "
                f"{args.hba_schema_output}"
            )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(generated)
        args.hrv_output.write_text(generated_hrv)
        args.hba_output.write_text(generated_hba)
        args.hba_configuration_output.write_text(
            generated_hba_configuration)
        args.spo2_configuration_output.write_text(
            generated_spo2_configuration)
        args.spo2_scale_output.write_text(generated_spo2_scale)
        args.spo2_spectral_output.write_text(generated_spo2_spectral)
        args.hba_schema_output.write_text(generated_hba_schema)
    print(
        "R1 model data verified: 11,581 transparent words, "
        "Goodix 3,924 words, GoMore 5,456 + 5,456 words, "
        "GH_HRV 324 coefficient words + 8 curve words, "
        "GH_HBA 16,083 model/remap/filter words + 9 configuration words "
        "+ 24 schema bytes, "
        "GH_SPO2 76 configuration bytes + 30 scale-table words + "
        "126 spectral words"
    )


if __name__ == "__main__":
    main()

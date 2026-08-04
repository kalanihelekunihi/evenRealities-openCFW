#!/usr/bin/env python3
"""Focused fail-closed gates for the nanopb 0.4.9 source snapshot."""

from __future__ import annotations

import hashlib
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "nanopb"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
CONFIG = SNAPSHOT / "g2-config" / "pb_g2_options.h"
PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint.c"
)
SKIP_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_skip_varint.c"
)
SKIP_PRODUCTION_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_skip_varint.h"
)
CLOSE_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_close_string_substream.c"
)
CLOSE_PRODUCTION_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_close_string_substream.h"
)
FIXED32_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
)
FIXED32_PRODUCTION_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed32.h"
)
FIXED64_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
)
FIXED64_PRODUCTION_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
)
READ_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_read.c"
)
READ_PRODUCTION_HEADER = READ_PRODUCTION_SOURCE.with_suffix(".h")
BUF_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_buf_read.c"
)
BYTE_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_readbyte.c"
)
PRIVATE_READ_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_private_read_pair.h"
)
PRIVATE_READ_AUDIT = (
    ROOT / "docs/research/nanopb-private-read-pair-source-audit.md"
)
ISTREAM_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_istream_from_buffer.c"
)
ISTREAM_PRODUCTION_HEADER = ISTREAM_PRODUCTION_SOURCE.with_suffix(".h")
SVARINT_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_svarint.c"
)
SVARINT_PRODUCTION_HEADER = SVARINT_PRODUCTION_SOURCE.with_suffix(".h")
SVARINT_PRODUCTION_AUDIT = (
    ROOT / "docs/research/nanopb-decode-svarint-source-audit.md"
)
VARINT32_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint32.c"
)
VARINT32_PRODUCTION_HEADER = VARINT32_PRODUCTION_SOURCE.with_suffix(".h")
VARINT32_PRODUCTION_AUDIT = (
    ROOT / "docs/research/nanopb-decode-varint32-pair-source-audit.md"
)
SKIP_STRING_PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb/runtime_nanopb_skip_string.c"
)
SKIP_STRING_PRODUCTION_HEADER = SKIP_STRING_PRODUCTION_SOURCE.with_suffix(".h")
SKIP_STRING_PRODUCTION_AUDIT = (
    ROOT / "docs/research/nanopb-skip-string-source-audit.md"
)
PRODUCTION_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
EXPECTED_PROVENANCE_SIZE = 56997
EXPECTED_PROVENANCE_SHA256 = "b4341b0ed98a697a0156d9d0c9fca2a03bed304ca890f56ea70c7eb590fa4283"
EXPECTED_VERIFIER_SIZE = 146028
EXPECTED_VERIFIER_SHA256 = "67e7681f1bb31086d9eb3b95700b883196030e2b702cb05ef47205f77d6d2cc6"
EXPECTED_RECORDS_SHA256 = "bb36791b9ae9a6cff412516db0b93911240fff8e8109d56136ca76173ac3a3e0"
EXPECTED_SOURCE_PATHS = [
    "LICENSE.txt",
    "pb.h",
    "pb_common.c",
    "pb_common.h",
    "pb_decode.c",
    "pb_decode.h",
    "pb_encode.c",
    "pb_encode.h",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_nanopb_snapshot", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_valid_production_registration(root: Path) -> None:
    (root / "Makefile").write_text(
        "NANOPB_DIR := third_party/nanopb\n"
        "nanopb-snapshot:\n"
        "\t$(PYTHON) $(NANOPB_DIR)/verify_snapshot.py\n",
        encoding="utf-8",
    )
    source = root / "components/shared/nanopb/runtime_nanopb_decode_varint.c"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(PRODUCTION_SOURCE.read_bytes())
    skip_source = root / "components/shared/nanopb/runtime_nanopb_skip_varint.c"
    skip_source.write_bytes(SKIP_PRODUCTION_SOURCE.read_bytes())
    skip_header = root / "components/shared/nanopb/runtime_nanopb_skip_varint.h"
    skip_header.write_bytes(SKIP_PRODUCTION_HEADER.read_bytes())
    close_source = (
        root
        / "components/shared/nanopb/runtime_nanopb_close_string_substream.c"
    )
    close_source.write_bytes(CLOSE_PRODUCTION_SOURCE.read_bytes())
    close_header = (
        root
        / "components/shared/nanopb/runtime_nanopb_close_string_substream.h"
    )
    close_header.write_bytes(CLOSE_PRODUCTION_HEADER.read_bytes())
    fixed32_source = (
        root / "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
    )
    fixed32_source.write_bytes(FIXED32_PRODUCTION_SOURCE.read_bytes())
    fixed32_header = (
        root / "components/shared/nanopb/runtime_nanopb_decode_fixed32.h"
    )
    fixed32_header.write_bytes(FIXED32_PRODUCTION_HEADER.read_bytes())
    fixed64_source = (
        root / "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
    )
    fixed64_source.write_bytes(FIXED64_PRODUCTION_SOURCE.read_bytes())
    fixed64_header = (
        root / "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
    )
    fixed64_header.write_bytes(FIXED64_PRODUCTION_HEADER.read_bytes())
    read_source = root / "components/shared/nanopb/runtime_nanopb_read.c"
    read_source.write_bytes(READ_PRODUCTION_SOURCE.read_bytes())
    read_header = root / "components/shared/nanopb/runtime_nanopb_read.h"
    read_header.write_bytes(READ_PRODUCTION_HEADER.read_bytes())
    buf_source = root / "components/shared/nanopb/runtime_nanopb_buf_read.c"
    buf_source.write_bytes(BUF_PRODUCTION_SOURCE.read_bytes())
    byte_source = root / "components/shared/nanopb/runtime_nanopb_readbyte.c"
    byte_source.write_bytes(BYTE_PRODUCTION_SOURCE.read_bytes())
    private_header = (
        root / "components/shared/nanopb/runtime_nanopb_private_read_pair.h"
    )
    private_header.write_bytes(PRIVATE_READ_HEADER.read_bytes())
    istream_source = (
        root / "components/shared/nanopb/runtime_nanopb_istream_from_buffer.c"
    )
    istream_source.write_bytes(ISTREAM_PRODUCTION_SOURCE.read_bytes())
    istream_header = istream_source.with_suffix(".h")
    istream_header.write_bytes(ISTREAM_PRODUCTION_HEADER.read_bytes())
    svarint_source = (
        root / "components/shared/nanopb/runtime_nanopb_decode_svarint.c"
    )
    svarint_source.write_bytes(SVARINT_PRODUCTION_SOURCE.read_bytes())
    svarint_header = svarint_source.with_suffix(".h")
    svarint_header.write_bytes(SVARINT_PRODUCTION_HEADER.read_bytes())
    varint32_source = (
        root / "components/shared/nanopb/runtime_nanopb_decode_varint32.c"
    )
    varint32_source.write_bytes(VARINT32_PRODUCTION_SOURCE.read_bytes())
    varint32_source.with_suffix(".h").write_bytes(
        VARINT32_PRODUCTION_HEADER.read_bytes()
    )
    skip_string_source = (
        root / "components/shared/nanopb/runtime_nanopb_skip_string.c"
    )
    skip_string_source.write_bytes(SKIP_STRING_PRODUCTION_SOURCE.read_bytes())
    skip_string_source.with_suffix(".h").write_bytes(
        SKIP_STRING_PRODUCTION_HEADER.read_bytes()
    )
    audit = root / "docs/research/nanopb-istream-from-buffer-source-audit.md"
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_bytes(
        (ROOT / "docs/research/nanopb-istream-from-buffer-source-audit.md").read_bytes()
    )
    svarint_audit = (
        root / "docs/research/nanopb-decode-svarint-source-audit.md"
    )
    svarint_audit.write_bytes(SVARINT_PRODUCTION_AUDIT.read_bytes())
    varint32_audit = (
        root / "docs/research/nanopb-decode-varint32-pair-source-audit.md"
    )
    varint32_audit.write_bytes(VARINT32_PRODUCTION_AUDIT.read_bytes())
    skip_string_audit = (
        root / "docs/research/nanopb-skip-string-source-audit.md"
    )
    skip_string_audit.write_bytes(SKIP_STRING_PRODUCTION_AUDIT.read_bytes())
    private_audit = (
        root / "docs/research/nanopb-private-read-pair-source-audit.md"
    )
    private_audit.write_bytes(PRIVATE_READ_AUDIT.read_bytes())
    manifest = root / "manifests/g2-2.2.6.10-core-source.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_bytes(
        (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_bytes()
    )
    current = json.loads(PRODUCTION_OVERLAY.read_text(encoding="utf-8"))
    leaves = [
        item for item in current["relocated_leaves"]
        if item["function"]
        in {
            "open_cfw_nanopb_decode_varint",
            "open_cfw_nanopb_skip_varint",
            "open_cfw_nanopb_close_string_substream",
            "open_cfw_nanopb_decode_fixed32",
            "open_cfw_nanopb_decode_fixed64",
            "open_cfw_nanopb_read",
            "open_cfw_nanopb_buf_read",
            "open_cfw_nanopb_readbyte",
            "open_cfw_nanopb_istream_from_buffer",
            "open_cfw_nanopb_decode_svarint",
            "open_cfw_nanopb_decode_varint32_eof",
            "open_cfw_nanopb_decode_varint32",
            "open_cfw_nanopb_skip_string",
        }
    ]
    if not any(
        item["function"] == "open_cfw_nanopb_decode_fixed32"
        for item in leaves
    ):
        fixed32_call = {
            "offset": 10,
            "type": "R_ARM_THM_CALL",
            "symbol": "open_cfw_nanopb_read",
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x0048F3BE,
        }
        leaves.append(
            {
                "function": "open_cfw_nanopb_decode_fixed32",
                "source": {
                    "path": (
                        "components/shared/nanopb/"
                        "runtime_nanopb_decode_fixed32.c"
                    ),
                    "size": 1975,
                    "sha256": (
                        "fefd8a899174fb9332c366df691dc2c8"
                        "ec6f4792f3fd464b65dbb573ace8ee19"
                    ),
                    "license": "Zlib",
                    "upstream_commit": (
                        "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
                    ),
                },
                "strict_relocation_contract": True,
                "expected": {
                    "size": 50,
                    "sha256": (
                        "c9fc88c025ec843fa3ad3f77b4e1bfb8"
                        "4126fd397a81d96c271646eb70632539"
                    ),
                    "alignment": 4,
                    "offset": 124496,
                    "unrelocated_sha256": (
                        "798f8f7cbed57f6ba11dad46a6de9d25"
                        "cb1f1710eb4fa904d79b6fe449952a04"
                    ),
                },
                "relocations": [fixed32_call],
                "toolchain_profiles": {
                    "linux-clang": {
                        "expected": {
                            "size": 50,
                            "sha256": (
                                "53a1961d2df94674da6890611087ab865"
                                "498084ced6a6f0c6850dcee23c7bf60"
                            ),
                            "alignment": 4,
                            "offset": 126316,
                            "unrelocated_sha256": (
                                "798f8f7cbed57f6ba11dad46a6de9d25"
                                "cb1f1710eb4fa904d79b6fe449952a04"
                            ),
                        },
                        "relocations": [fixed32_call],
                    }
                },
            }
        )
    overlay = root / "components/apollo_main/core_overlay/overlay.json"
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.write_text(
        json.dumps(
            {
                "relocated_leaves": leaves,
                "patch_sites": [
                    {
                        "name": "replace_nanopb_decode_varint32_eof",
                        "runtime_address": 0x0048F4B8,
                        "expected_size": 246,
                        "expected_sha256": (
                            "8583fa17383d72bbdcab6c2a7a20369d"
                            "c0598d3ac3061feaf8a7b29dfa520150"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_decode_varint32_eof",
                    },
                    {
                        "name": "replace_nanopb_decode_varint32",
                        "runtime_address": 0x0048F5AE,
                        "expected_size": 10,
                        "expected_sha256": (
                            "48218a658cffd7aeddfb623c9d0e7bd0"
                            "38ceb2a6898e9f8d08b10d5779f4f79b"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_decode_varint32",
                    },
                    {
                        "name": "replace_nanopb_skip_string",
                        "runtime_address": 0x0048F64C,
                        "expected_size": 32,
                        "expected_sha256": (
                            "03afe2d60436676fffba342c7b8c9504"
                            "992fa903d7cba768396fd1de2c6c66cd"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_skip_string",
                    },
                    {
                        "name": "replace_nanopb_decode_svarint",
                        "runtime_address": 0x00490150,
                        "expected_size": 64,
                        "expected_sha256": (
                            "80b24be422cf924f3ae1b79669312535d"
                            "c0d5a56dd88be8a6b9e4ee5ff064048"
                        ),
                        "branch": "b_w",
                        "target_function": (
                            "open_cfw_nanopb_decode_svarint"
                        ),
                    },
                    {
                        "name": "replace_nanopb_istream_from_buffer",
                        "runtime_address": 0x0048F49C,
                        "expected_size": 28,
                        "expected_sha256": (
                            "852314bb8f86dcbd550deb0f51bc285b"
                            "662e39c1b4fae66690c44a7bf4f7a674"
                        ),
                        "branch": "b_w",
                        "target_function": (
                            "open_cfw_nanopb_istream_from_buffer"
                        ),
                    },
                    {
                        "name": "replace_nanopb_buf_read",
                        "runtime_address": 0x0048F3A4,
                        "expected_size": 26,
                        "expected_sha256": (
                            "9d6c6690294b82bbafba82ec0f63a6bb"
                            "5b78e4146543db3a30fac92469ace723"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_buf_read",
                    },
                    {
                        "name": "replace_nanopb_read",
                        "runtime_address": 0x0048F3BE,
                        "expected_size": 150,
                        "expected_sha256": (
                            "69aecb900c749fd98bd2d05e2229e9a3d"
                            "6829bd36f3e393f624e3579a9b4af7f"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_read",
                    },
                    {
                        "name": "replace_nanopb_readbyte",
                        "runtime_address": 0x0048F454,
                        "expected_size": 72,
                        "expected_sha256": (
                            "15c8303c5c1dbf1b3f143142c6169026"
                            "cb8bc56b37a6291dd0457b3664b67ae5"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_readbyte",
                    },
                    {
                        "name": "replace_nanopb_decode_fixed32",
                        "runtime_address": 0x00490190,
                        "expected_size": 28,
                        "expected_sha256": (
                            "1ee27599a8ac5b8d2a0cbaac59986fb4"
                            "9be7b24c348a960a216b8cbbecce5bf3"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_decode_fixed32",
                    },
                    {
                        "name": "replace_nanopb_decode_fixed64",
                        "runtime_address": 0x004901AC,
                        "expected_size": 32,
                        "expected_sha256": (
                            "96228dfbdfe30665d79281ba0fd5ba3b3"
                            "af38701396671cd20b77623ffd82d54"
                        ),
                        "branch": "b_w",
                        "target_function": "open_cfw_nanopb_decode_fixed64",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


class NanopbSnapshotTests(unittest.TestCase):
    def test_skip_string_production_record_is_exact(self) -> None:
        selection = json.loads(PROVENANCE.read_text(encoding="utf-8"))["selection"]
        record = selection["production_skip_string_leaf"]
        verifier = load_verifier()
        verifier.verify_skip_string_provenance(selection)

        scalar_paths: list[tuple[object, ...]] = []
        def collect(value: object, path: tuple[object, ...] = ()) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    collect(item, path + (key,))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    collect(item, path + (index,))
            else:
                scalar_paths.append(path)
        collect(record)
        self.assertGreaterEqual(len(scalar_paths), 150)
        for path in scalar_paths:
            with self.subTest(path=path):
                changed = copy.deepcopy(selection)
                target: object = changed["production_skip_string_leaf"]
                for key in path[:-1]:
                    target = target[key]  # type: ignore[index]
                key = path[-1]
                old = target[key]  # type: ignore[index]
                if isinstance(old, bool):
                    new = not old
                elif isinstance(old, int):
                    new = old + 1
                else:
                    new = str(old) + "-mutated"
                target[key] = new  # type: ignore[index]
                with self.assertRaisesRegex(
                    SystemExit, "pb_skip_string production provenance changed"
                ):
                    verifier.verify_skip_string_provenance(changed)

    def test_skip_string_actual_source_header_evidence_and_upstream_are_pinned(self) -> None:
        verifier = load_verifier()
        verifier.verify_skip_string_source_pins()
        for source, label in (
            (SKIP_STRING_PRODUCTION_SOURCE, "source"),
            (SKIP_STRING_PRODUCTION_HEADER, "header"),
            (SKIP_STRING_PRODUCTION_AUDIT, "evidence"),
        ):
            old_root = verifier.ROOT
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    for original in (
                        SKIP_STRING_PRODUCTION_SOURCE,
                        SKIP_STRING_PRODUCTION_HEADER,
                        SKIP_STRING_PRODUCTION_AUDIT,
                    ):
                        target = root / original.relative_to(ROOT)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(original.read_bytes())
                    verifier.ROOT = root
                    target = root / source.relative_to(ROOT)
                    target.write_bytes(source.read_bytes() + b"x")
                    with self.assertRaisesRegex(SystemExit, f"{label} size changed"):
                        verifier.verify_skip_string_source_pins()
            finally:
                verifier.ROOT = old_root

    def test_skip_string_manifest_regions_mutate_independently(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        names = (
            "nanopb_skip_string_source_replacement",
            "opaque_application_between_nanopb_skip_string_and_nanopb_close_string_substream",
            "apollo_nanopb_skip_string_source_alignment",
            "apollo_nanopb_skip_string_source_leaf",
        )
        try:
            for name in names:
                with self.subTest(region=name), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    write_valid_production_registration(root)
                    manifest_path = (
                        root / "manifests/g2-2.2.6.10-core-source.json"
                    )
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    regions = manifest["component_overrides"]["apollo_main"]["regions"]
                    region = next(item for item in regions if item["name"] == name)
                    region["size"] += 1
                    manifest_path.write_text(
                        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
                    )
                    verifier.ROOT = root
                    with self.assertRaisesRegex(
                        SystemExit, "pb_skip_string manifest ownership changed"
                    ):
                        verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_varint32_pair_has_two_independently_auditable_source_records(self) -> None:
        selection = json.loads(PROVENANCE.read_text(encoding="utf-8"))["selection"]
        private = selection["production_decode_varint32_eof_leaf"]
        public = selection["production_decode_varint32_leaf"]
        self.assertEqual(private["upstream_function"], "pb_decode_varint32_eof")
        self.assertEqual(public["upstream_function"], "pb_decode_varint32")
        self.assertEqual(private["pair_order"], 0)
        self.assertEqual(public["pair_order"], 1)
        self.assertEqual(private["source_dependency_calls"], [
            "open_cfw_nanopb_readbyte", "open_cfw_nanopb_readbyte"
        ])
        self.assertEqual(public["source_dependency_calls"], [
            "open_cfw_nanopb_decode_varint32_eof"
        ])
        self.assertEqual(private["local_source"], str(
            VARINT32_PRODUCTION_SOURCE.relative_to(ROOT)
        ))
        self.assertEqual(public["local_source"], private["local_source"])
        self.assertEqual(private["local_header"], str(
            VARINT32_PRODUCTION_HEADER.relative_to(ROOT)
        ))
        self.assertEqual(public["local_header"], private["local_header"])
        self.assertEqual(private["evidence"], str(
            VARINT32_PRODUCTION_AUDIT.relative_to(ROOT)
        ))
        self.assertEqual(public["evidence"], private["evidence"])
        self.assertNotEqual(private["stock_span"], public["stock_span"])
        self.assertNotEqual(
            private["manifest_regions"]["entry_replacement"],
            public["manifest_regions"]["entry_replacement"],
        )
        self.assertEqual(
            set(private["toolchain_profiles"]), {"apple-clang", "linux-clang"}
        )
        self.assertEqual(
            set(public["toolchain_profiles"]), {"apple-clang", "linux-clang"}
        )
        self.assertEqual(
            private["toolchain_profiles"]["linux-clang"]["text_offset"], 126796
        )
        self.assertEqual(
            public["toolchain_profiles"]["linux-clang"]["text_offset"], 127036
        )
        self.assertEqual(
            selection["production_varint32_linux_aggregate"]
            ["effective_flash_region_count"],
            847,
        )

    def test_varint32_pair_provenance_mutations_fail_independently(self) -> None:
        verifier = load_verifier()
        selection = json.loads(PROVENANCE.read_text(encoding="utf-8"))["selection"]
        verifier.verify_varint32_provenance(selection)

        private = "production_decode_varint32_eof_leaf"
        public = "production_decode_varint32_leaf"
        mutations = (
            ("private upstream span", lambda s: s[private].update(upstream_definition_span="pb_decode.c bytes [5763,7483)"), "private pb_decode_varint32 provenance changed"),
            ("private upstream hash", lambda s: s[private].update(upstream_definition_sha256="0" * 64), "private pb_decode_varint32 provenance changed"),
            ("public upstream span", lambda s: s[public].update(upstream_definition_span="pb_decode.c bytes [7486,7617)"), "public pb_decode_varint32 provenance changed"),
            ("public upstream hash", lambda s: s[public].update(upstream_definition_sha256="0" * 64), "public pb_decode_varint32 provenance changed"),
            ("private source hash", lambda s: s[private].update(local_source_sha256="0" * 64), "private source/header/evidence contract changed"),
            ("public source hash", lambda s: s[public].update(local_source_sha256="0" * 64), "public source/header/evidence contract changed"),
            ("private header hash", lambda s: s[private].update(local_header_sha256="0" * 64), "private source/header/evidence contract changed"),
            ("public header hash", lambda s: s[public].update(local_header_sha256="0" * 64), "public source/header/evidence contract changed"),
            ("private stock span", lambda s: s[private].update(stock_span="[0x0048F4BA,0x0048F5AE)"), "private pb_decode_varint32 provenance changed"),
            ("private stock hash", lambda s: s[private].update(stock_sha256="0" * 64), "private pb_decode_varint32 provenance changed"),
            ("public stock span", lambda s: s[public].update(stock_span="[0x0048F5B0,0x0048F5B8)"), "public pb_decode_varint32 provenance changed"),
            ("public stock hash", lambda s: s[public].update(stock_sha256="0" * 64), "public pb_decode_varint32 provenance changed"),
            ("private call one", lambda s: s[private]["relocations"][0].update(target_function="opaque"), "private pb_decode_varint32 dependency closure changed"),
            ("private call two", lambda s: s[private]["relocations"][1].update(target_function="opaque"), "private pb_decode_varint32 dependency closure changed"),
            ("public call", lambda s: s[public]["relocations"][0].update(target_function="opaque"), "public pb_decode_varint32 dependency closure changed"),
            ("private patch", lambda s: s[private]["patch_region"].update(size=244), "private pb_decode_varint32 provenance changed"),
            ("private patch hash", lambda s: s[private]["patch_region"].update(stock_sha256="0" * 64), "private pb_decode_varint32 provenance changed"),
            ("public patch span", lambda s: s[public]["patch_region"].update(size=8), "public pb_decode_varint32 provenance changed"),
            ("public patch", lambda s: s[public]["patch_region"].update(stock_sha256="0" * 64), "public pb_decode_varint32 provenance changed"),
            ("pair order", lambda s: s[public].update(pair_order=0), "pair ordering changed"),
            ("literal closure", lambda s: s[private]["literal_closure"].update(contents="overflow"), "literal closure changed"),
            ("private manifest", lambda s: s[private]["manifest_regions"].update(source_leaf="opaque"), "private pb_decode_varint32 provenance changed"),
            ("public manifest", lambda s: s[public]["manifest_regions"].update(source_leaf="opaque"), "public pb_decode_varint32 provenance changed"),
            ("private license", lambda s: s[private].update(license="unknown"), "private source/header/evidence contract changed"),
            ("public license", lambda s: s[public].update(license="unknown"), "public source/header/evidence contract changed"),
            ("compatibility wording", lambda s: s[private].update(qualification="exact vendor release; hardware execution remain deferred; No bootloader homolog"), "private qualification changed"),
            ("evidence pin", lambda s: s[public].update(evidence_sha256="0" * 64), "public source/header/evidence contract changed"),
            ("boot exclusion", lambda s: s[private].update(bootloader_homolog=True), "private source/header/evidence contract changed"),
            ("hardware deferral", lambda s: s[public].update(qualification=s[public]["qualification"].replace("hardware execution remain deferred", "hardware tested")), "public qualification changed"),
            ("extra key", lambda s: s[private].update(combined_pair=True), "private pb_decode_varint32 provenance schema changed"),
            ("aggregate", lambda s: s["production_varint32_apple_aggregate"]["overlay"].update(size=0), "Apple aggregate pins changed"),
            ("private Linux profile", lambda s: s[private]["toolchain_profiles"]["linux-clang"].update(text_offset=0), "private pb_decode_varint32 Linux object/placement changed"),
            ("public Linux profile", lambda s: s[public]["toolchain_profiles"]["linux-clang"].update(text_offset=0), "public pb_decode_varint32 Linux object/placement changed"),
            ("Linux aggregate", lambda s: s["production_varint32_linux_aggregate"]["overlay"].update(size=0), "Linux aggregate pins changed"),
        )
        for name, mutate, message in mutations:
            with self.subTest(name=name):
                changed = copy.deepcopy(selection)
                mutate(changed)
                with self.assertRaisesRegex(SystemExit, message):
                    verifier.verify_varint32_provenance(changed)

    def test_varint32_pair_actual_source_header_evidence_bytes_are_pinned(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                for source in (
                    VARINT32_PRODUCTION_SOURCE,
                    VARINT32_PRODUCTION_HEADER,
                    VARINT32_PRODUCTION_AUDIT,
                ):
                    target = root / source.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
                verifier.ROOT = root
                verifier.verify_varint32_source_pins()
                for source, label in (
                    (VARINT32_PRODUCTION_SOURCE, "source"),
                    (VARINT32_PRODUCTION_HEADER, "header"),
                    (VARINT32_PRODUCTION_AUDIT, "evidence"),
                ):
                    target = root / source.relative_to(ROOT)
                    target.write_bytes(source.read_bytes() + b"x")
                    with self.assertRaisesRegex(SystemExit, f"{label} size changed"):
                        verifier.verify_varint32_source_pins()
                    target.write_bytes(source.read_bytes())
                    changed = bytearray(source.read_bytes())
                    changed[0] ^= 1
                    target.write_bytes(changed)
                    with self.assertRaisesRegex(SystemExit, f"{label} hash changed"):
                        verifier.verify_varint32_source_pins()
                    target.write_bytes(source.read_bytes())
        finally:
            verifier.ROOT = old_root

    def test_varint32_pair_actual_upstream_spans_and_hashes_are_pinned(self) -> None:
        verifier = load_verifier()
        old_root, old_here = verifier.ROOT, verifier.HERE
        pristine = (SNAPSHOT / "pb_decode.c").read_bytes()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                snapshot = root / "third_party/nanopb"
                snapshot.mkdir(parents=True)
                upstream = snapshot / "pb_decode.c"
                upstream.write_bytes(pristine)
                for source in (
                    VARINT32_PRODUCTION_SOURCE,
                    VARINT32_PRODUCTION_HEADER,
                    VARINT32_PRODUCTION_AUDIT,
                ):
                    target = root / source.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
                verifier.ROOT, verifier.HERE = root, snapshot
                verifier.verify_varint32_source_pins()
                cases = (
                    (6000, "private hash changed"),
                    (7575, "public hash changed"),
                )
                for offset, message in cases:
                    changed = bytearray(pristine)
                    changed[offset] ^= 1
                    upstream.write_bytes(changed)
                    with self.assertRaisesRegex(SystemExit, message):
                        verifier.verify_varint32_source_pins()
                for offset, message in (
                    (5762, "private extraction span changed"),
                    (7485, "public extraction span changed"),
                ):
                    changed = pristine[:offset] + b" " + pristine[offset:-1]
                    upstream.write_bytes(changed)
                    with self.assertRaisesRegex(SystemExit, message):
                        verifier.verify_varint32_source_pins()
        finally:
            verifier.ROOT, verifier.HERE = old_root, old_here

    maxDiff = None

    def run_verifier(self, verifier: Path = VERIFIER) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(verifier)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            result.stdout,
            "nanopb 0.4.9 compatibility snapshot verification passed\n",
        )
        self.assertEqual(PROVENANCE.stat().st_size, EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(sha256(PROVENANCE.read_bytes()), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(VERIFIER.stat().st_size, EXPECTED_VERIFIER_SIZE)
        self.assertEqual(sha256(VERIFIER.read_bytes()), EXPECTED_VERIFIER_SHA256)

    def test_release_chain_and_minimal_closure_are_exact(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        upstream = value["upstream"]
        self.assertEqual(upstream["tag_type"], "annotated")
        self.assertEqual(
            upstream["tag_object"],
            "b3056c326da0e6cf702fd13ae2fe63225caa0801",
        )
        self.assertEqual(
            upstream["selected_commit"],
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "2c4c260bcff3f9f7081238d377274dd385d76582",
        )
        self.assertEqual(upstream["tree_object_count"], 1)
        self.assertEqual(upstream["root_tree_entry_count"], 38)
        records = value["files"]
        self.assertEqual([item["local_path"] for item in records], EXPECTED_SOURCE_PATHS)
        self.assertEqual(canonical_sha256(records), EXPECTED_RECORDS_SHA256)
        self.assertEqual(
            records[0]["sha256"],
            "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d",
        )

    def test_selection_is_a_qualified_compatibility_choice(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        selection = value["selection"]
        upstream = value["upstream"]
        self.assertEqual(selection["compatibility_choice"], "nanopb-0.4.9")
        self.assertFalse(selection["exact_g2_point_release_proven"])
        self.assertEqual(
            selection["g2_compatible_pristine_release_range"],
            ["0.4.7", "0.4.8", "0.4.9"],
        )
        self.assertIn("not proof", selection["qualification"])
        self.assertEqual(
            selection["integration_status"],
            (
                "authenticated and verified offline; thirteen bounded altered "
                "production functions registered: pb_istream_from_buffer, "
                "pb_decode_varint, pb_decode_svarint, private "
                "pb_decode_varint32_eof, pb_decode_varint32, pb_skip_varint, "
                "pb_skip_string, "
                "pb_close_string_substream, "
                "pb_decode_fixed32, pb_decode_fixed64, pb_read, private "
                "buf_read, and private pb_readbyte"
            ),
        )
        production = selection["production_leaf"]
        self.assertEqual(production["upstream_function"], "pb_decode_varint")
        self.assertEqual(
            production["local_source"],
            "components/shared/nanopb/runtime_nanopb_decode_varint.c",
        )
        self.assertEqual(production["stock_span"], "[0x0048F5B8,0x0048F628)")
        self.assertEqual(production["source_backed_readbyte_entry"], "0x0048F454")
        self.assertIn("broader pristine", production["qualification"])
        constructor = selection["production_istream_from_buffer_leaf"]
        self.assertEqual(constructor["upstream_function"], "pb_istream_from_buffer")
        self.assertEqual(
            constructor["upstream_definition_span"],
            "pb_decode.c bytes [5114,5692)",
        )
        self.assertEqual(constructor["canonical_callback_identity"], "0x0048F3A5")
        self.assertEqual(set(constructor["toolchain_profiles"]), {"apple-clang", "linux-clang"})
        self.assertFalse(constructor["bootloader_homolog"])
        self.assertIn("does not prove", constructor["qualification"])
        private_pair = selection["production_private_read_pair"]
        self.assertEqual(
            [item["function"] for item in private_pair["local_sources"]],
            ["open_cfw_nanopb_buf_read", "open_cfw_nanopb_readbyte"],
        )
        self.assertEqual(
            [item["symbol"] for item in private_pair["retained_stock_seams"]],
            [
                "__aeabi_memcpy",
                "open_cfw_nanopb_end_of_stream_error",
                "open_cfw_nanopb_io_error",
            ],
        )
        self.assertEqual(
            set(private_pair["toolchain_profiles"]),
            {"apple-clang", "linux-clang"},
        )
        skip_production = selection["production_skip_varint_leaf"]
        self.assertEqual(skip_production["upstream_function"], "pb_skip_varint")
        self.assertEqual(skip_production["upstream_commit"], upstream["selected_commit"])
        self.assertEqual(
            skip_production["upstream_definition_span"],
            "pb_decode.c bytes [8160,8360)",
        )
        self.assertEqual(skip_production["upstream_definition_size"], 200)
        self.assertEqual(
            skip_production["upstream_definition_sha256"],
            "4c9c2629d6c8bf7e8e986a8cb54413d39a804ddb0e848c64aae009d3b10aac62",
        )
        self.assertEqual(
            skip_production["local_source"],
            "components/shared/nanopb/runtime_nanopb_skip_varint.c",
        )
        self.assertEqual(skip_production["local_source_size"], 1925)
        self.assertEqual(
            skip_production["local_source_sha256"],
            "89e53ebc01a2d28c4a94ac4a38313b8213788a23ed55bf767a9e8a5c6d961225",
        )
        self.assertEqual(
            skip_production["local_header"],
            "components/shared/nanopb/runtime_nanopb_skip_varint.h",
        )
        self.assertEqual(skip_production["local_header_size"], 2401)
        self.assertEqual(
            skip_production["local_header_sha256"],
            "30a8aea087894af29396746a31bbebfc9195e12ee4d66e79b4b637828eeab103",
        )
        self.assertEqual(skip_production["stock_span"], "[0x0048F628,0x0048F64C)")
        self.assertEqual(skip_production["stock_size"], 36)
        self.assertEqual(
            skip_production["stock_sha256"],
            "fae83b1a62a07bb9c7a3d3f6c398bc13433ebe1cd75d01945f83f30e6fcc9c5d",
        )
        self.assertEqual(skip_production["stock_read_seam"], "0x0048F3BE")
        self.assertIn("0.4.7-0.4.9", skip_production["qualification"])
        self.assertIn("not proof", skip_production["qualification"])
        self.assertIn("broader pristine", skip_production["qualification"])
        close_production = selection["production_close_string_substream_leaf"]
        self.assertEqual(
            close_production,
            {
                "upstream_function": "pb_close_string_substream",
                "upstream_source": "pb_decode.c",
                "upstream_commit": upstream["selected_commit"],
                "upstream_definition_span": "pb_decode.c bytes [11223,11568)",
                "upstream_definition_size": 345,
                "upstream_definition_sha256": (
                    "527e5ca208a04366c0911baf793af7dc"
                    "7045fd73014eefc6e31ce3a8b6dc332f"
                ),
                "local_source": (
                    "components/shared/nanopb/"
                    "runtime_nanopb_close_string_substream.c"
                ),
                "local_source_size": 2061,
                "local_source_sha256": (
                    "736e7ec228f9282ba5b093fd482441e6"
                    "e2017fff860d989dc3aadb2bdeff0fcb"
                ),
                "local_header": (
                    "components/shared/nanopb/"
                    "runtime_nanopb_close_string_substream.h"
                ),
                "local_header_size": 2537,
                "local_header_sha256": (
                    "851af370162d79f4bd0be8b8bb9a5731"
                    "d47cf02527078b9e278019340f2d65d4"
                ),
                "stock_span": "[0x0048F7CA,0x0048F7F4)",
                "stock_size": 42,
                "stock_sha256": (
                    "439bbeecb6a0b8266dc3dcd913e987933"
                    "52b6b346a7a58cdd44322c734621818"
                ),
                "stock_read_seam": "0x0048F3BE",
                "configuration": "g2-config/pb_g2_options.h",
                "qualification": (
                    "Altered local source selected against authenticated "
                    "nanopb 0.4.9 as a compatibility baseline within the "
                    "authenticated 0.4.7-0.4.9 range; not proof of the vendor "
                    "nanopb revision or checkout. The broader pristine "
                    "pb_common, pb_decode, and pb_encode translation units "
                    "remain unregistered."
                ),
            },
        )
        fixed32_production = selection["production_decode_fixed32_leaf"]
        self.assertEqual(
            fixed32_production,
            {
                "upstream_function": "pb_decode_fixed32",
                "upstream_source": "pb_decode.c",
                "upstream_commit": upstream["selected_commit"],
                "upstream_definition_span": "pb_decode.c bytes [43210,43828)",
                "upstream_definition_size": 618,
                "upstream_definition_sha256": (
                    "1952ee1f743334c82f206c910392f63b"
                    "2e7fdd702cbdd404dae04367aa8ae518"
                ),
                "local_source": (
                    "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
                ),
                "local_source_size": 1975,
                "local_source_sha256": (
                    "fefd8a899174fb9332c366df691dc2c8"
                    "ec6f4792f3fd464b65dbb573ace8ee19"
                ),
                "local_header": (
                    "components/shared/nanopb/runtime_nanopb_decode_fixed32.h"
                ),
                "local_header_size": 1750,
                "local_header_sha256": (
                    "738e4c7d4ea983b0ba967fa42cdcc61c"
                    "b2e20837531bc6176b7f95a5fe8e2460"
                ),
                "stock_span": "[0x00490190,0x004901AC)",
                "stock_size": 28,
                "stock_sha256": (
                    "1ee27599a8ac5b8d2a0cbaac59986fb4"
                    "9be7b24c348a960a216b8cbbecce5bf3"
                ),
                "stock_read_seam": "0x0048F3BE",
                "configuration": "g2-config/pb_g2_options.h",
                "qualification": (
                    "Altered local source selected against authenticated "
                    "nanopb 0.4.9 as a compatibility baseline within the "
                    "authenticated 0.4.7-0.4.9 range; not proof of the vendor "
                    "nanopb revision or checkout. The broader pristine "
                    "pb_common, pb_decode, and pb_encode translation units "
                    "remain unregistered."
                ),
            },
        )
        fixed64_production = selection["production_decode_fixed64_leaf"]
        self.assertEqual(
            fixed64_production,
            {
                "upstream_function": "pb_decode_fixed64",
                "upstream_source": "pb_decode.c",
                "upstream_commit": upstream["selected_commit"],
                "upstream_definition_span": "pb_decode.c bytes [43854,44688)",
                "upstream_definition_size": 834,
                "upstream_definition_sha256": (
                    "7f9da692a631280aa5b91a5d08440ac6"
                    "8f5060a64814997dde8dcbdb2f0b4974"
                ),
                "local_source": (
                    "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
                ),
                "local_source_size": 2083,
                "local_source_sha256": (
                    "865fa587e7b783e83f24107e52bf3010"
                    "053d0660b06dc0ac2e7f72bb8ad969bc"
                ),
                "local_header": (
                    "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
                ),
                "local_header_size": 1726,
                "local_header_sha256": (
                    "6394df89057700817341e0550ae21033"
                    "629d3a1ea458d5a68a6edc2b233cc6bd"
                ),
                "stock_span": "[0x004901AC,0x004901CC)",
                "stock_size": 32,
                "stock_sha256": (
                    "96228dfbdfe30665d79281ba0fd5ba3b3"
                    "af38701396671cd20b77623ffd82d54"
                ),
                "stock_read_seam": "0x0048F3BE",
                "configuration": "g2-config/pb_g2_options.h",
                "qualification": (
                    "Altered local source selected against authenticated "
                    "nanopb 0.4.9 as a compatibility baseline within the "
                    "authenticated 0.4.7-0.4.9 range; not proof of the "
                    "vendor nanopb revision or checkout. Its pb_read ABI entry "
                    "now redirects to the separately pinned production_read_leaf, "
                    "while that provider retains three authenticated stock "
                    "identity/data seams. The broader pristine pb_common, "
                    "pb_decode, and pb_encode translation units remain "
                    "unregistered."
                ),
            },
        )
        read_production = selection["production_read_leaf"]
        self.assertEqual(read_production["upstream_function"], "pb_read")
        self.assertEqual(read_production["upstream_source"], "pb_decode.c")
        self.assertEqual(read_production["upstream_commit"], upstream["selected_commit"])
        self.assertEqual(
            [item["release"] for item in read_production["authenticated_release_definitions"]],
            ["0.4.7", "0.4.8", "0.4.9"],
        )
        self.assertEqual(
            {
                (item["size"], item["sha256"])
                for item in read_production["authenticated_release_definitions"]
            },
            {
                (
                    814,
                    "3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c",
                )
            },
        )
        self.assertEqual(
            (
                read_production["local_source"],
                read_production["local_source_size"],
                read_production["local_source_sha256"],
            ),
            (
                "components/shared/nanopb/runtime_nanopb_read.c",
                2944,
                "e4f99df8121553d4cb6d6c2f94aa7ef1b1445efd200cee4d872dd75894d24089",
            ),
        )
        self.assertEqual(
            (
                read_production["local_header"],
                read_production["local_header_size"],
                read_production["local_header_sha256"],
            ),
            (
                "components/shared/nanopb/runtime_nanopb_read.h",
                2032,
                "22203e33b8cd9e07b94d24477ffb8a6f096a9ea8393c5723071b5f12c3ec4296",
            ),
        )
        self.assertEqual(
            (
                read_production["stock_span"],
                read_production["stock_size"],
                read_production["stock_sha256"],
            ),
            (
                "[0x0048F3BE,0x0048F454)",
                150,
                "69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f",
            ),
        )
        self.assertEqual(
            read_production["stock_topology"],
            {
                "internal_recursive_calls": ["0x0048F3EA", "0x0048F3FC"],
                "external_direct_callers": [
                    "0x0048F632", "0x0048F666", "0x0048F6C0", "0x0048F6D0",
                    "0x0048F71A", "0x0048F754", "0x0048F764", "0x0048F7DC",
                    "0x00490198", "0x004901B4", "0x004903E4", "0x00490478",
                    "0x004905A2",
                ],
                "external_direct_caller_count": 13,
                "interior_ingress_count": 0,
                "stored_pointer_ingress_count": 0,
            },
        )
        self.assertEqual(
            [
                (item["symbol"], item["target_address"])
                for item in read_production["retained_stock_seams"]
            ],
            [
                ("open_cfw_nanopb_end_of_stream_error", "0x00787C70"),
                ("open_cfw_nanopb_stock_buffer_read_identity", "0x0048F3A5"),
                ("open_cfw_nanopb_io_error", "0x0078B690"),
            ],
        )
        self.assertEqual(
            [
                (item["offset"], item["type"], item["symbol"], item["target_address"])
                for item in read_production["relocations"]
            ],
            [
                (28, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_end_of_stream_error", "0x00787C70"),
                (32, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_end_of_stream_error", "0x00787C70"),
                (66, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_stock_buffer_read_identity", "0x0048F3A5"),
                (70, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_stock_buffer_read_identity", "0x0048F3A5"),
                (134, "R_ARM_THM_MOVW_ABS_NC", "open_cfw_nanopb_io_error", "0x0078B690"),
                (138, "R_ARM_THM_MOVT_ABS", "open_cfw_nanopb_io_error", "0x0078B690"),
            ],
        )
        self.assertEqual(
            {
                name: (profile["size"], profile["offset"], profile["runtime_address"])
                for name, profile in read_production["toolchain_profiles"].items()
            },
            {
                "apple-clang": (158, 124640, "0x007B2A04"),
                "linux-clang": (158, 126464, "0x007B3124"),
            },
        )
        self.assertFalse(read_production["bootloader_homolog"]["found"])
        self.assertIn("source-backed stock entry", read_production["qualification"])
        self.assertIn("retains two stock error strings", read_production["qualification"])

    def test_signed_varint_ownership_contract_is_exact(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        selection = value["selection"]
        self.assertIn("thirteen bounded altered production functions", selection["integration_status"])
        production = selection["production_decode_svarint_leaf"]
        self.assertEqual(
            {
                "upstream_function": production["upstream_function"],
                "upstream_definition_span": production["upstream_definition_span"],
                "upstream_definition_size": production["upstream_definition_size"],
                "upstream_definition_sha256": production["upstream_definition_sha256"],
                "local_source": production["local_source"],
                "local_source_size": production["local_source_size"],
                "local_source_sha256": production["local_source_sha256"],
                "local_header": production["local_header"],
                "local_header_size": production["local_header_size"],
                "local_header_sha256": production["local_header_sha256"],
                "stock_span": production["stock_span"],
                "stock_size": production["stock_size"],
                "stock_sha256": production["stock_sha256"],
                "source_dependency": production["source_dependency"],
                "manifest_regions": production["manifest_regions"],
                "evidence": production["evidence"],
                "bootloader_homolog": production["bootloader_homolog"],
            },
            {
                "upstream_function": "pb_decode_svarint",
                "upstream_definition_span": "pb_decode.c bytes [42912,43210)",
                "upstream_definition_size": 298,
                "upstream_definition_sha256": "df1caa71053163bdefaea7d6b19bdc72f10c63f09430003b88f10fb7dac3ff6e",
                "local_source": "components/shared/nanopb/runtime_nanopb_decode_svarint.c",
                "local_source_size": 1943,
                "local_source_sha256": "f361cafc8813257e16fafb9ee986c88c632eb2c7edc604dcb02e27ec85a7df4d",
                "local_header": "components/shared/nanopb/runtime_nanopb_decode_svarint.h",
                "local_header_size": 1789,
                "local_header_sha256": "d1ca3c0520784c4837c9570416934c7884eeeba2eba2a42091cd040d5222e72c",
                "stock_span": "[0x00490150,0x00490190)",
                "stock_size": 64,
                "stock_sha256": "80b24be422cf924f3ae1b79669312535dc0d5a56dd88be8a6b9e4ee5ff064048",
                "source_dependency": "open_cfw_nanopb_decode_varint",
                "manifest_regions": {
                    "entry_replacement": "nanopb_decode_svarint_source_replacement",
                    "source_leaf": "apollo_nanopb_decode_svarint_source_leaf",
                },
                "evidence": "docs/research/nanopb-decode-svarint-source-audit.md",
                "bootloader_homolog": False,
            },
        )
        self.assertEqual(
            production["relocations"],
            [{
                "offset": 8,
                "type": "R_ARM_THM_CALL",
                "symbol": "open_cfw_nanopb_decode_varint",
                "target_function": "open_cfw_nanopb_decode_varint",
            }],
        )
        apple = production["toolchain_profiles"]["apple-clang"]
        self.assertEqual(
            {
                key: apple[key]
                for key in (
                    "size", "alignment", "offset", "runtime_address",
                    "unrelocated_sha256", "relocated_sha256",
                    "entry_patch_sha256",
                )
            },
            {
                "size": 54,
                "alignment": 4,
                "offset": 124916,
                "runtime_address": "0x007B2B18",
                "unrelocated_sha256": "19e103f83ab8879d36eb1b0513bf541601e40bc82e69e0dc252308c0646d1286",
                "relocated_sha256": "1b181a82adbbb72dc6fc09b1b70dd48f4c0eefdf25a8c4e71701710cb12dae3f",
                "entry_patch_sha256": "e8c5601b86e9a38362fb292b0a8ba70250d2ccc3094d0c8c117b1c33f5bf11cc",
            },
        )
        linux = production["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            {
                key: linux[key]
                for key in (
                    "compiler", "reviewed_source_root", "object_size",
                    "object_sha256", "size", "alignment", "offset",
                    "runtime_address", "unrelocated_sha256",
                    "relocated_sha256", "entry_patch_sha256",
                )
            },
            {
                "compiler": "Homebrew clang version 22.1.8",
                "reviewed_source_root": (
                    "/Users/kalani/Repo/SybilSightABCD/openCFW"
                ),
                "object_size": 968,
                "object_sha256": (
                    "866820ef347453a3cbf2feed221eeab0"
                    "b571a9b79b6988cc17d2861b1aeaced5"
                ),
                "size": 50,
                "alignment": 4,
                "offset": 126744,
                "runtime_address": "0x007B323C",
                "unrelocated_sha256": (
                    "3617ea95d4a2cbabf3a1abb375e57232"
                    "3fffcebfa68cb4e19874cb4a831d9662"
                ),
                "relocated_sha256": (
                    "63e4707f5fd537094855d38f6b4df857"
                    "8b77644c131e180db2e682d32fbc1fab"
                ),
                "entry_patch_sha256": (
                    "e6bb4ee4baec73757a5f465cf99a32e7"
                    "87fb25bd651b2b16e2e76fda4c6d18fd"
                ),
            },
        )

        overlay = json.loads(PRODUCTION_OVERLAY.read_text(encoding="utf-8"))
        allowed = {
            item["function"]
            for item in overlay["relocated_leaves"]
            if item["source"].get("upstream_commit")
            == "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
        }
        self.assertEqual(len(allowed), 13)
        self.assertIn("open_cfw_nanopb_decode_svarint", allowed)

        manifest = json.loads(
            (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text(
                encoding="utf-8"
            )
        )
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        self.assertEqual(len(regions), 960)
        by_name = {item["name"]: item for item in regions}
        entry = by_name["nanopb_decode_svarint_source_replacement"]
        self.assertEqual(
            (entry["file_offset"], entry["size"], entry["target_address"], entry["address_status"]),
            (360816, 64, 0x00490150, "generated_source_entry_replacement"),
        )
        source = by_name["apollo_nanopb_decode_svarint_source_leaf"]
        self.assertEqual(
            (source["file_offset"], source["size"], source["target_address"], source["address_status"]),
            (3648312, 54, 0x007B2B18, "source_compiled"),
        )
        self.assertEqual((SVARINT_PRODUCTION_SOURCE.stat().st_size, SVARINT_PRODUCTION_HEADER.stat().st_size), (1943, 1789))
        self.assertTrue(SVARINT_PRODUCTION_AUDIT.is_file())

    def test_recovered_config_compiles_complete_runtime(self) -> None:
        compiler = shutil.which("clang")
        if compiler is None:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="openCFW-nanopb-compile-") as tmp:
            output = Path(tmp)
            for source_name in ("pb_common.c", "pb_decode.c", "pb_encode.c"):
                result = subprocess.run(
                    [
                        compiler,
                        "-std=c11",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                        "-ffreestanding",
                        "-fno-builtin",
                        f"-I{SNAPSHOT}",
                        "-include",
                        str(CONFIG),
                        "-c",
                        str(SNAPSHOT / source_name),
                        "-o",
                        str(output / f"{source_name}.o"),
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)

            smoke = output / "abi_smoke.c"
            smoke.write_text(
                '#include "g2-config/pb_g2_options.h"\n'
                '#include "pb.h"\n'
                "#if defined(PB_ENABLE_MALLOC) || defined(PB_FIELD_32BIT)\n"
                '#error "forbidden G2 option"\n'
                "#endif\n"
                "_Static_assert(sizeof(pb_size_t) == 2, \"pb_size_t ABI\");\n"
                "_Static_assert(sizeof(double) == 8, \"native FP64 ABI\");\n"
                "_Static_assert(PB_MAX_REQUIRED_FIELDS == 64, \"required fields\");\n"
                "int main(void) { return 0; }\n",
                encoding="ascii",
            )
            smoke_result = subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    f"-I{SNAPSHOT}",
                    "-fsyntax-only",
                    str(smoke),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(smoke_result.returncode, 0, smoke_result.stdout)

            rejected = subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-DPB_ENABLE_MALLOC=1",
                    f"-I{SNAPSHOT}",
                    "-fsyntax-only",
                    str(smoke),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("PB_ENABLE_MALLOC to remain undefined", rejected.stdout)

    def test_even_generated_messages_are_absent(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        glue = value["g2_boundary"]["first_party_glue"]
        self.assertFalse(glue["included"])
        self.assertIn("Even .proto schemas", glue["separate_required_inputs"])
        self.assertEqual(list(SNAPSHOT.glob("*.proto")), [])
        self.assertEqual(list(SNAPSHOT.glob("*.pb.c")), [])
        self.assertEqual(list(SNAPSHOT.glob("*.pb.h")), [])

    def test_verifier_registration_is_allowed_but_production_references_fail_closed(self) -> None:
        verifier = load_verifier()
        registrations = {
            "manifests/production.json": '{"source":"third_party/nanopb/pb_decode.c"}\n',
            "components/apollo_main/core_overlay/overlay.json": (
                '{"sources":[{"path":"third_party/nanopb/pb_encode.c"}]}\n'
            ),
            "components/apollo_main/core_overlay/build_component.py": (
                'NANOPB_SOURCE = "third_party/nanopb/pb_common.c"\n'
            ),
            "components/apollo_main/core_overlay/nanopb_glue.c": (
                '#include "third_party/nanopb/pb.h"\n'
            ),
            "tools/apollo_overlay.py": (
                'NANOPB_SOURCE = "third_party/nanopb/pb_decode.c"\n'
            ),
        }
        old_root = verifier.ROOT
        try:
            for relative, content in registrations.items():
                with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    write_valid_production_registration(root)
                    verifier.ROOT = root
                    verifier.verify_production_exclusion()

                    configured = root / relative
                    configured.parent.mkdir(parents=True, exist_ok=True)
                    configured.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(
                        SystemExit,
                        (
                            "snapshot is production-configured|"
                            "production leaf set is not exact"
                        ),
                    ):
                        verifier.verify_production_exclusion()

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                root.mkdir()
                write_valid_production_registration(root)
                (root / "Makefile").write_text(
                    "NANOPB_DIR := third_party/nanopb\n"
                    "nanopb-snapshot:\n"
                    "\t$(PYTHON) $(NANOPB_DIR)/verify_snapshot.py\n"
                    "core-component:\n"
                    "\t$(CC) -c $(NANOPB_DIR)/pb_decode.c\n",
                    encoding="utf-8",
                )
                verifier.ROOT = root
                with self.assertRaisesRegex(
                    SystemExit,
                    "snapshot is production-configured by Makefile:5",
                ):
                    verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_bounded_production_registration_mutations_fail_closed(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        mutations = (
            (
                "missing leaf",
                lambda root, overlay: overlay.update(relocated_leaves=[]),
                "production leaf set is not exact",
            ),
            (
                "missing pb_skip_varint leaf",
                lambda root, overlay: overlay.update(
                    relocated_leaves=[
                        item
                        for item in overlay["relocated_leaves"]
                        if item["function"] != "open_cfw_nanopb_skip_varint"
                    ]
                ),
                "production leaf set is not exact",
            ),
            (
                "missing pb_close_string_substream leaf",
                lambda root, overlay: overlay.update(
                    relocated_leaves=[
                        item
                        for item in overlay["relocated_leaves"]
                        if item["function"]
                        != "open_cfw_nanopb_close_string_substream"
                    ]
                ),
                "production leaf set is not exact",
            ),
            (
                "missing pb_decode_fixed32 leaf",
                lambda root, overlay: overlay.update(
                    relocated_leaves=[
                        item
                        for item in overlay["relocated_leaves"]
                        if item["function"] != "open_cfw_nanopb_decode_fixed32"
                    ]
                ),
                "production leaf set is not exact",
            ),
            (
                "missing pb_decode_fixed64 leaf",
                lambda root, overlay: overlay.update(
                    relocated_leaves=[
                        item
                        for item in overlay["relocated_leaves"]
                        if item["function"] != "open_cfw_nanopb_decode_fixed64"
                    ]
                ),
                "production leaf set is not exact",
            ),
            (
                "missing pb_read leaf",
                lambda root, overlay: overlay.update(
                    relocated_leaves=[
                        item
                        for item in overlay["relocated_leaves"]
                        if item["function"] != "open_cfw_nanopb_read"
                    ]
                ),
                "production leaf set is not exact",
            ),
            (
                "duplicate leaf",
                lambda root, overlay: overlay["relocated_leaves"].append(
                    json.loads(json.dumps(overlay["relocated_leaves"][0]))
                ),
                "production leaf set is not exact",
            ),
            (
                "renamed leaf",
                lambda root, overlay: overlay["relocated_leaves"][0].update(
                    function="renamed_nanopb_leaf"
                ),
                "production function changed",
            ),
            (
                "seam drift",
                lambda root, overlay: overlay["relocated_leaves"][0][
                    "relocations"
                ][0].update(target_address=0x0048F456),
                "canonical relocation closure changed",
            ),
            (
                "extra relocation",
                lambda root, overlay: overlay["relocated_leaves"][0][
                    "relocations"
                ].append({"offset": 0, "type": "R_ARM_ABS32", "symbol": "x"}),
                "canonical relocation closure changed",
            ),
            (
                "broad include inside leaf flags",
                lambda root, overlay: overlay["relocated_leaves"][0][
                    "toolchain"
                ]["flags"].append("-Ithird_party/nanopb"),
                "runtime reference exists inside the bounded leaf",
            ),
            (
                "source drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_varint.c"
                ).write_bytes(PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "production source size changed",
            ),
            (
                "pb_skip_varint source drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_skip_varint.c"
                ).write_bytes(SKIP_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "pb_skip_varint source size changed",
            ),
            (
                "pb_skip_varint header drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_skip_varint.h"
                ).write_bytes(SKIP_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "pb_skip_varint header size changed",
            ),
            (
                "pb_skip_varint seam drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_skip_varint"
                )["relocations"][0].update(target_address=0x0048F3C0),
                "pb_skip_varint canonical relocation closure changed",
            ),
            (
                "pb_close_string_substream source drift",
                lambda root, overlay: (
                    root
                    / (
                        "components/shared/nanopb/"
                        "runtime_nanopb_close_string_substream.c"
                    )
                ).write_bytes(CLOSE_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "pb_close_string_substream source size changed",
            ),
            (
                "pb_close_string_substream header drift",
                lambda root, overlay: (
                    root
                    / (
                        "components/shared/nanopb/"
                        "runtime_nanopb_close_string_substream.h"
                    )
                ).write_bytes(CLOSE_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "pb_close_string_substream header size changed",
            ),
            (
                "pb_close_string_substream seam drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"]
                    == "open_cfw_nanopb_close_string_substream"
                )["relocations"][0].update(target_address=0x0048F3C0),
                "pb_close_string_substream canonical relocation closure changed",
            ),
            (
                "pb_close_string_substream Apple text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"]
                    == "open_cfw_nanopb_close_string_substream"
                )["expected"].update(offset=124448),
                "pb_close_string_substream canonical text contract changed",
            ),
            (
                "pb_close_string_substream Linux text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"]
                    == "open_cfw_nanopb_close_string_substream"
                )["toolchain_profiles"]["linux-clang"]["expected"].update(
                    offset=126268
                ),
                "pb_close_string_substream Linux configuration contract changed",
            ),
            (
                "pb_decode_fixed32 source drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_fixed32.c"
                ).write_bytes(FIXED32_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "pb_decode_fixed32 source size changed",
            ),
            (
                "pb_decode_fixed32 header drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_fixed32.h"
                ).write_bytes(FIXED32_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "pb_decode_fixed32 header size changed",
            ),
            (
                "pb_decode_fixed32 seam drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_fixed32"
                )["relocations"][0].update(target_address=0x0048F3C0),
                "pb_decode_fixed32 canonical relocation closure changed",
            ),
            (
                "pb_decode_fixed32 stock patch drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["patch_sites"]
                    if item["target_function"]
                    == "open_cfw_nanopb_decode_fixed32"
                ).update(expected_size=30),
                "pb_decode_fixed32 stock patch contract changed",
            ),
            (
                "pb_decode_fixed64 source drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_fixed64.c"
                ).write_bytes(FIXED64_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "pb_decode_fixed64 source size changed",
            ),
            (
                "pb_decode_fixed64 header drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_fixed64.h"
                ).write_bytes(FIXED64_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "pb_decode_fixed64 header size changed",
            ),
            (
                "pb_decode_fixed64 seam drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_fixed64"
                )["relocations"][0].update(target_address=0x0048F3C0),
                "pb_decode_fixed64 canonical relocation closure changed",
            ),
            (
                "pb_decode_fixed64 Apple text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_fixed64"
                )["expected"].update(offset=124616),
                "pb_decode_fixed64 canonical text contract changed",
            ),
            (
                "pb_decode_fixed64 Linux text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_fixed64"
                )["toolchain_profiles"]["linux-clang"]["expected"].update(
                    offset=126436
                ),
                "pb_decode_fixed64 Linux text contract changed",
            ),
            (
                "pb_decode_fixed64 stock patch drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["patch_sites"]
                    if item["target_function"]
                    == "open_cfw_nanopb_decode_fixed64"
                ).update(expected_size=34),
                "pb_decode_fixed64 stock patch contract changed",
            ),
            (
                "pb_read source drift",
                lambda root, overlay: (
                    root / "components/shared/nanopb/runtime_nanopb_read.c"
                ).write_bytes(READ_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "bounded pb_read source size changed",
            ),
            (
                "pb_read header drift",
                lambda root, overlay: (
                    root / "components/shared/nanopb/runtime_nanopb_read.h"
                ).write_bytes(READ_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "bounded pb_read header size changed",
            ),
            (
                "pb_read retained seam drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_read"
                )["relocations"][0].update(target_address=0x00787C72),
                "pb_read retained-seam relocation closure changed",
            ),
            (
                "pb_read Apple text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_read"
                )["expected"].update(offset=124644),
                "pb_read canonical text contract changed",
            ),
            (
                "pb_read Linux text drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_read"
                )["toolchain_profiles"]["linux-clang"]["expected"].update(
                    offset=126468
                ),
                "pb_read Linux text contract changed",
            ),
            (
                "pb_read stock patch drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["patch_sites"]
                    if item["target_function"] == "open_cfw_nanopb_read"
                ).update(expected_size=152),
                "pb_read stock patch contract changed",
            ),
            (
                "pb_decode_svarint source drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_svarint.c"
                ).write_bytes(SVARINT_PRODUCTION_SOURCE.read_bytes() + b"\n"),
                "pb_decode_svarint source size changed",
            ),
            (
                "pb_decode_svarint header drift",
                lambda root, overlay: (
                    root
                    / "components/shared/nanopb/runtime_nanopb_decode_svarint.h"
                ).write_bytes(SVARINT_PRODUCTION_HEADER.read_bytes() + b"\n"),
                "pb_decode_svarint header size changed",
            ),
            (
                "pb_decode_svarint source dependency drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_svarint"
                )["relocations"][0].update(
                    target_function="open_cfw_nanopb_decode_fixed32"
                ),
                "pb_decode_svarint Apple text/relocation contract changed",
            ),
            (
                "pb_decode_svarint stock patch span drift",
                lambda root, overlay: next(
                    item
                    for item in overlay["patch_sites"]
                    if item["target_function"]
                    == "open_cfw_nanopb_decode_svarint"
                ).update(expected_size=62),
                "pb_decode_svarint stock patch contract changed",
            ),
            (
                "private pb_decode_varint32 call one drift",
                lambda root, overlay: next(
                    item for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_varint32_eof"
                )["relocations"][0].update(target_function="opaque"),
                "private pb_decode_varint32 Apple text/literal contract changed",
            ),
            (
                "private pb_decode_varint32 call two drift",
                lambda root, overlay: next(
                    item for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_varint32_eof"
                )["relocations"][1].update(target_function="opaque"),
                "private pb_decode_varint32 Apple text/literal contract changed",
            ),
            (
                "public pb_decode_varint32 call drift",
                lambda root, overlay: next(
                    item for item in overlay["relocated_leaves"]
                    if item["function"] == "open_cfw_nanopb_decode_varint32"
                )["relocations"][0].update(target_function="opaque"),
                "public pb_decode_varint32 Apple text contract changed",
            ),
            (
                "private pb_decode_varint32 patch span drift",
                lambda root, overlay: next(
                    item for item in overlay["patch_sites"]
                    if item["target_function"] == "open_cfw_nanopb_decode_varint32_eof"
                ).update(expected_size=244),
                "pb_decode_varint32 stock patch contracts changed",
            ),
            (
                "public pb_decode_varint32 patch hash drift",
                lambda root, overlay: next(
                    item for item in overlay["patch_sites"]
                    if item["target_function"] == "open_cfw_nanopb_decode_varint32"
                ).update(expected_sha256="0" * 64),
                "pb_decode_varint32 stock patch contracts changed",
            ),
            (
                "public pb_decode_varint32 patch span drift",
                lambda root, overlay: next(
                    item for item in overlay["patch_sites"]
                    if item["target_function"] == "open_cfw_nanopb_decode_varint32"
                ).update(expected_size=8),
                "pb_decode_varint32 stock patch contracts changed",
            ),
            (
                "private pb_decode_varint32 patch hash drift",
                lambda root, overlay: next(
                    item for item in overlay["patch_sites"]
                    if item["target_function"] == "open_cfw_nanopb_decode_varint32_eof"
                ).update(expected_sha256="0" * 64),
                "pb_decode_varint32 stock patch contracts changed",
            ),
            (
                "duplicate-shadow pb_decode_varint32 patch",
                lambda root, overlay: overlay["patch_sites"].insert(
                    0,
                    dict(
                        copy.deepcopy(next(
                            item for item in overlay["patch_sites"]
                            if item["target_function"]
                            == "open_cfw_nanopb_decode_varint32"
                        )),
                        expected_size=999,
                    ),
                ),
                "pb_decode_varint32 stock patches are not unique",
            ),
            (
                "URL outside overlay",
                lambda root, overlay: (
                    root / "components/apollo_main/core_overlay/build_component.py"
                ).write_text(
                    "SOURCE = 'https://github.com/nanopb/nanopb/blob/"
                    "98bf4db69897b53434f3d0ba72e0a3ab1a902824/pb_decode.c'\n",
                    encoding="utf-8",
                ),
                "snapshot is production-configured",
            ),
        )
        try:
            for name, mutate, message in mutations:
                with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    write_valid_production_registration(root)
                    overlay_path = (
                        root / "components/apollo_main/core_overlay/overlay.json"
                    )
                    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
                    mutate(root, overlay)
                    overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
                    verifier.ROOT = root
                    with self.assertRaisesRegex(SystemExit, message):
                        verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_istream_manifest_source_function_mutation_fails_closed(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                root.mkdir()
                write_valid_production_registration(root)
                manifest_path = (
                    root / "manifests/g2-2.2.6.10-core-source.json"
                )
                manifest = json.loads(
                    manifest_path.read_text(encoding="utf-8")
                )
                region = next(
                    item
                    for item in manifest["component_overrides"][
                        "apollo_main"
                    ]["regions"]
                    if item["name"]
                    == "apollo_nanopb_istream_from_buffer_source_leaf"
                )
                region["function"] += " WRONG"
                manifest_path.write_text(
                    json.dumps(manifest),
                    encoding="utf-8",
                )
                verifier.ROOT = root
                with self.assertRaisesRegex(
                    SystemExit,
                    "pb_istream_from_buffer manifest source ownership changed",
                ):
                    verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_svarint_manifest_ownership_mutations_fail_closed(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        mutations = (
            (
                "nanopb_decode_svarint_source_replacement",
                "size",
                62,
                "pb_decode_svarint manifest entry ownership changed",
            ),
            (
                "apollo_nanopb_decode_svarint_source_leaf",
                "target_address",
                0x007B2B1A,
                "pb_decode_svarint manifest source ownership changed",
            ),
        )
        try:
            for name, key, value, message in mutations:
                with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    write_valid_production_registration(root)
                    manifest_path = (
                        root / "manifests/g2-2.2.6.10-core-source.json"
                    )
                    manifest = json.loads(
                        manifest_path.read_text(encoding="utf-8")
                    )
                    region = next(
                        item
                        for item in manifest["component_overrides"]
                        ["apollo_main"]["regions"]
                        if item["name"] == name
                    )
                    region[key] = value
                    manifest_path.write_text(
                        json.dumps(manifest), encoding="utf-8"
                    )
                    verifier.ROOT = root
                    with self.assertRaisesRegex(SystemExit, message):
                        verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_varint32_manifest_regions_mutate_independently(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        names = (
            "nanopb_decode_varint32_eof_source_replacement",
            "nanopb_decode_varint32_source_replacement",
            "apollo_nanopb_decode_varint32_eof_source_alignment",
            "apollo_nanopb_decode_varint32_eof_source_leaf",
            "apollo_nanopb_decode_varint32_overflow_rodata",
            "apollo_nanopb_decode_varint32_source_alignment",
            "apollo_nanopb_decode_varint32_source_leaf",
        )
        try:
            for name in names:
                with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    write_valid_production_registration(root)
                    verifier.ROOT = root
                    verifier.verify_production_exclusion()
                    manifest_path = (
                        root / "manifests/g2-2.2.6.10-core-source.json"
                    )
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    region = next(
                        item for item in manifest["component_overrides"]
                        ["apollo_main"]["regions"] if item["name"] == name
                    )
                    region["size"] += 1
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaisesRegex(
                        SystemExit, "pb_decode_varint32 manifest ownership changed"
                    ):
                        verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_varint32_manifest_duplicate_shadow_is_rejected(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                root.mkdir()
                write_valid_production_registration(root)
                verifier.ROOT = root
                verifier.verify_production_exclusion()
                manifest_path = root / "manifests/g2-2.2.6.10-core-source.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                regions = manifest["component_overrides"]["apollo_main"]["regions"]
                canonical = next(
                    item for item in regions
                    if item["name"] == "apollo_nanopb_decode_varint32_source_leaf"
                )
                duplicate = copy.deepcopy(canonical)
                duplicate["size"] = 11
                regions.insert(0, duplicate)
                regions.pop(1)
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(
                    SystemExit, "manifest region names are not unique"
                ):
                    verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_generated_build_reports_do_not_affect_registration_verification(self) -> None:
        verifier = load_verifier()
        old_root = verifier.ROOT
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                root.mkdir()
                write_valid_production_registration(root)
                for generated_name in (
                    "build",
                    "build-linux",
                    "build-console-apple-a",
                ):
                    stale_report = (
                        root
                        / "components/apollo_main/core_overlay"
                        / generated_name
                        / "build-report.json"
                    )
                    stale_report.parent.mkdir(parents=True)
                    stale_report.write_text(
                        json.dumps(
                            {
                                "relocated_leaves": [
                                    {
                                        "source": "third_party/nanopb/pb_decode.c",
                                        "note": "stale foreign generated output",
                                    },
                                    {
                                        "source": "third_party/nanopb/pb_decode.c",
                                        "note": "duplicate stale generated output",
                                    },
                                ]
                            }
                        ),
                        encoding="utf-8",
                    )
                nested_report = root / "components/foreign/build/nested/report.json"
                nested_report.parent.mkdir(parents=True)
                nested_report.write_text(
                    '{"source":"third_party/nanopb/pb_encode.c"}\n',
                    encoding="utf-8",
                )
                verifier.ROOT = root
                verifier.verify_production_exclusion()

                actual_config = root / "components/foreign/runtime.json"
                actual_config.write_text(
                    '{"source":"third_party/nanopb/pb_encode.c"}\n',
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    SystemExit,
                    "snapshot is production-configured",
                ):
                    verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_source_config_and_git_object_mutations_fail_closed(self) -> None:
        mutations = (
            ("pb_decode.c", b"\n/* drift */\n", "size changed: pb_decode.c"),
            ("g2-config/pb_g2_options.h", b"\n", "G2 option header size changed"),
            (
                "upstream/b3056c326da0e6cf702fd13ae2fe63225caa0801.tag",
                b"drift",
                "tag payload size changed",
            ),
            ("upstream/trees.json", b" ", "tree closure size changed"),
            ("PROVENANCE.json", b" ", "provenance size changed"),
        )
        for relative, suffix, expected in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "openCFW" / "third_party" / "nanopb"
                copied.parent.mkdir(parents=True)
                shutil.copytree(SNAPSHOT, copied)
                target = copied / relative
                target.write_bytes(target.read_bytes() + suffix)
                result = self.run_verifier(copied / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stdout)

    def test_tree_membership_tampering_is_rejected_semantically(self) -> None:
        verifier = load_verifier()
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        closure = json.loads((SNAPSHOT / "upstream" / "trees.json").read_text())
        tampered = json.loads(json.dumps(closure))
        entry = next(item for item in tampered["trees"][0]["entries"] if item["name"] == "pb.h")
        entry["oid"] = "0" + entry["oid"][1:]
        with self.assertRaises(SystemExit) as raised:
            verifier.verify_tree_closure(provenance, tampered)
        self.assertIn("root tree object ID mismatch", str(raised.exception))

        tampered_provenance = json.loads(json.dumps(provenance))
        tampered_provenance["files"][1]["git_blob_sha1"] = "0" * 40
        with self.assertRaises(SystemExit) as raised:
            verifier.verify_tree_closure(tampered_provenance, closure)
        self.assertIn("tree blob mismatch: pb.h", str(raised.exception))

    def test_verifier_is_offline_and_does_not_require_firmware_blob(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "openCFW" / "third_party" / "nanopb"
            copied.parent.mkdir(parents=True)
            shutil.copytree(SNAPSHOT, copied)
            write_valid_production_registration(copied.parents[1])
            result = self.run_verifier(copied / "verify_snapshot.py")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(
                result.stdout,
                "nanopb 0.4.9 compatibility snapshot verification passed\n",
            )


if __name__ == "__main__":
    unittest.main()

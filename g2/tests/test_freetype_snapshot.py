#!/usr/bin/env python3
"""Focused authentication and fail-closed gates for the FreeType snapshot."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "freetype"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 102377
EXPECTED_PROVENANCE_SHA256 = (
    "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"
)
EXPECTED_VERIFIER_SIZE = 25438
EXPECTED_VERIFIER_SHA256 = (
    "517e54823d33c95a8d0007e07ff513d796183470a0286a7cca00d9ea93ed9709"
)
EXPECTED_RECORDS_SHA256 = (
    "62e233bc18e6ada5974c98d65dfc4faaf15058e39edbc435662337d60549ec32"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(data)


class FreeTypeSnapshotTests(unittest.TestCase):
    maxDiff = None

    def run_verifier(self, verifier: Path = VERIFIER) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            ["python3", str(verifier)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "FreeType 2.9.1 snapshot verification passed\n")
        provenance_data = PROVENANCE.read_bytes()
        verifier_data = VERIFIER.read_bytes()
        self.assertEqual(len(provenance_data), EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(provenance_data), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(len(verifier_data), EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(verifier_data), EXPECTED_VERIFIER_SHA256)

    def test_per_file_manifest_and_release_object_chain_are_exact(self) -> None:
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        records = provenance["files"]
        self.assertEqual(len(records), 297)
        self.assertEqual(canonical_digest(records), EXPECTED_RECORDS_SHA256)
        self.assertEqual(records[0]["local_path"], "LICENSE")
        self.assertEqual(records[0]["upstream_path"], "docs/FTL.TXT")
        self.assertEqual(records[0]["size"], 6743)
        self.assertEqual(
            records[0]["sha256"],
            "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1",
        )
        upstream = provenance["upstream"]
        self.assertEqual(
            upstream["annotated_tag_object"],
            "ad55868d889b6ba8d2aed846b4b4b460f8a83e42",
        )
        self.assertEqual(
            upstream["peeled_commit"],
            "86bc8a95056c97a810986434a3f268cbe67f2902",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "34694611454c8e95bd398d54da805ffb4e94577b",
        )
        self.assertTrue(upstream["tag_signature"]["present"])
        self.assertFalse(upstream["tag_signature"]["signer_trust_verified"])

    def test_g2_boundary_records_modules_and_recovered_configuration(self) -> None:
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        g2 = provenance["g2_boundary"]
        self.assertEqual(g2["default_module_table"]["entry_count"], 10)
        self.assertEqual(
            [item["module_name"] for item in g2["modules"]],
            [
                "autofitter",
                "truetype",
                "cff",
                "psaux",
                "psnames",
                "pshinter",
                "sfnt",
                "smooth",
                "smooth-lcd",
                "smooth-lcdv",
            ],
        )
        self.assertEqual(
            g2["recovered_configuration"],
            {
                "base": {
                    "FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES": False,
                    "FT_CONFIG_OPTION_INCREMENTAL": True,
                    "FT_CONFIG_OPTION_PIC": False,
                    "FT_CONFIG_OPTION_SUBPIXEL_RENDERING": False,
                    "stream_support": True,
                },
                "cff": {
                    "CFF_CONFIG_OPTION_OLD_ENGINE": False,
                    "default_hinting_engine": "Adobe",
                },
                "autofit": {
                    "AF_CONFIG_OPTION_CJK": True,
                    "AF_CONFIG_OPTION_INDIC": True,
                    "AF_CONFIG_OPTION_USE_WARPER": True,
                    "fallback_style": {
                        "name": "AF_STYLE_HANI_DFLT",
                        "enum": 83,
                        "qualification": (
                            "HANI_DFLT is 79 without the four guarded Indic styles "
                            "and 83 with them in authenticated 2.9.1"
                        ),
                    },
                },
                "true_type": {
                    "interpreter_default": 40,
                    "supported_interpreter_versions": [35, 40],
                    "TT_CONFIG_OPTION_SUBPIXEL_HINTING": 2,
                    "TT_CONFIG_OPTION_GX_VAR_SUPPORT": True,
                    "TT_CONFIG_OPTION_EMBEDDED_BITMAPS": True,
                },
                "gx_variations": {
                    "multi_masters_record": "0x007505A4",
                    "multi_masters_callable_slots": 8,
                    "metrics_variations_record": "0x00767290",
                    "metrics_variations_callable_slots": 3,
                },
                "allocator_lifecycle": {
                    "FT_Memory_size": 16,
                    "heap_descriptor": "0x20000354",
                    "generic_allocate": "0x00484180",
                    "generic_reallocate": "0x00484234",
                    "generic_free": "0x0048429E",
                    "callbacks": {
                        "alloc": "0x005676D4",
                        "realloc": "0x005676E0",
                        "free": "0x005676EC",
                    },
                    "lifecycle": {
                        "FT_Init_FreeType": "0x0052431C",
                        "FT_New_Memory": "0x005676A0",
                        "FT_Done_Memory": "0x005676C6",
                        "FT_New_Library": "0x005274B2",
                        "FT_Add_Default_Modules": "0x005242FC",
                        "FT_Done_Face": {
                            "entry": "0x00526814",
                            "end": "0x0052687E",
                            "direct_callers": [
                                {"address": "0x004B2310", "kind": "BL"},
                                {"address": "0x0052659C", "kind": "BL"},
                                {"address": "0x005267D0", "kind": "BL"},
                            ],
                            "caller_roles": [
                                "LVGL/FTC face-cache destructor",
                                "FT_Open_Face failure cleanup",
                                "FT_Open_Face no-output cleanup",
                            ],
                        },
                        "lv_freetype_font_create": "0x004B1C9C",
                        "lv_freetype_font_delete": "0x004B1EF6",
                    },
                },
                "font_registration": {
                    "font_chain_entries_per_role": 4,
                    "configuration_arrays": {
                        "background": "0x20002C48",
                        "foreground": "0x20002C78",
                    },
                    "configuration_record": {
                        "size": 12,
                        "type": {"offset": 0, "size": 1},
                        "font_pointer_or_face_path": {"offset": 4, "size": 4},
                        "pixel_size": {"offset": 8, "size": 2},
                        "style": {"offset": 10, "size": 1},
                        "type_semantics": {
                            "0": "native lv_font_t pointer",
                            "1": "FreeType face path passed to lv_freetype_font_create",
                            "2": "binary-font path disabled in this build",
                        },
                    },
                },
            },
        )
        self.assertEqual(
            g2["unresolved"],
            [
                "complete FT_CONFIG_OPTION_* state outside the proven subset",
                "optional compression helpers",
                "an exact stock FT_Done_FreeType entry (no conventional retained topology was found)",
                "IAR version and exact compiler/linker flags",
                "external font payload identities and runtime configuration-array contents",
            ],
        )
        self.assertEqual(
            g2["promotion_status"],
            "production-excluded; source configuration and explicit promotion review still required",
        )
        self.assertEqual(
            g2["recovered_module_header_sha256"],
            "522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74",
        )
        self.assertEqual(
            provenance["selection"]["integration_status"],
            "authenticated and verified offline; not production-configured",
        )

    def test_verifier_rejects_source_metadata_object_header_and_inventory_tampering(self) -> None:
        def alter_source(copy: Path) -> None:
            path = copy / "include" / "freetype" / "freetype.h"
            data = path.read_bytes()
            path.write_bytes(data.replace(b"FREETYPE_PATCH  1", b"FREETYPE_PATCH  2", 1))

        def alter_provenance(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["upstream"]["peeled_commit"] = "0" * 40
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_recovered_configuration(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["g2_boundary"]["recovered_configuration"]["true_type"][
                "interpreter_default"
            ] = 35
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_recovered_feature_toggle(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["g2_boundary"]["recovered_configuration"]["autofit"][
                "AF_CONFIG_OPTION_CJK"
            ] = False
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_recovered_done_face(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["g2_boundary"]["recovered_configuration"]["allocator_lifecycle"][
                "lifecycle"
            ]["FT_Done_Face"]["entry"] = "0x00526816"
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_recovered_manager_schema(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["g2_boundary"]["recovered_configuration"]["font_registration"][
                "configuration_record"
            ]["size"] = 16
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_unresolved_boundary(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["g2_boundary"]["unresolved"] = [
                item
                for item in value["g2_boundary"]["unresolved"]
                if "FT_Done_FreeType" not in item
            ]
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_tag(copy: Path) -> None:
            path = copy / "upstream" / "VER-2-9-1.tag"
            path.write_bytes(path.read_bytes().replace(b"VER-2-9-1", b"VER-2-9-0", 1))

        def alter_module_header(copy: Path) -> None:
            path = copy / "g2-config" / "freetype" / "config" / "ftmodule.h"
            data = path.read_bytes()
            path.write_bytes(data.replace(b"tt_driver_class", b"t1_driver_class", 1))

        def add_unrecorded_file(copy: Path) -> None:
            (copy / "unexpected.c").write_text("/* not authenticated */\n", encoding="utf-8")

        def make_source_executable(copy: Path) -> None:
            (copy / "include" / "freetype" / "freetype.h").chmod(0o755)

        def add_json_escaped_production_link(copy: Path) -> None:
            manifest = copy.parents[1] / "manifests" / "encoded.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                '{"source_root":"third_party/\\u0066reetype/src"}\n',
                encoding="utf-8",
            )

        mutations = {
            "source": alter_source,
            "provenance": alter_provenance,
            "recovered configuration metadata": alter_recovered_configuration,
            "recovered feature-toggle metadata": alter_recovered_feature_toggle,
            "recovered FT_Done_Face metadata": alter_recovered_done_face,
            "recovered manager-schema metadata": alter_recovered_manager_schema,
            "unresolved boundary metadata": alter_unresolved_boundary,
            "annotated tag": alter_tag,
            "G2 module header": alter_module_header,
            "subtree inventory": add_unrecorded_file,
            "source Git mode": make_source_executable,
            "JSON-escaped production link": add_json_escaped_production_link,
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp:
                copied = Path(temp) / "third_party" / "freetype"
                shutil.copytree(SNAPSHOT, copied)
                mutate(copied)
                result = self.run_verifier(copied / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("FreeType snapshot verification failed:", result.stdout)

    def test_only_pinned_community_source_and_retained_abi_reference_snapshot(self) -> None:
        configured = list((ROOT / "manifests").glob("*.json"))
        configured.extend(
            path
            for path in (ROOT / "components").glob("**/*")
            if path.is_file()
            and path.suffix in {".json", ".c", ".h", ".py", ".s", ".S", ".ld", ".lds", ".mk"}
            and "build" not in path.relative_to(ROOT / "components").parts
        )
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in configured
            if "freetype" in path.read_text(encoding="utf-8").lower()
        ]
        self.assertEqual(
            set(offenders),
            {
                "components/apollo_main/core_overlay/overlay.json",
                "components/apollo_main/core_overlay/lvgl_font_manager.c",
                "components/shared/freetype/runtime_freetype_truetype.c",
                "components/shared/freetype/runtime_freetype_truetype.h",
                "components/shared/freetype/source_admission.json",
            },
        )


if __name__ == "__main__":
    unittest.main()

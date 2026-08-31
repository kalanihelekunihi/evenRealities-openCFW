from __future__ import annotations

import ctypes
import hashlib
import json
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = ROOT / "components" / "apollo_main" / "core_overlay"
RUNTIME_SOURCE = COMPONENT_ROOT / "runtime_tlsf.c"
COMPAT_ROOT = COMPONENT_ROOT / "tlsf_compat"
VENDOR_ROOT = ROOT / "third_party" / "tlsf"
VENDOR_SOURCE = VENDOR_ROOT / "tlsf.c"
VENDOR_HEADER = VENDOR_ROOT / "tlsf.h"
VENDOR_README = VENDOR_ROOT / "README.openCFW.md"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_tlsf_host.c"
WASM_FIXTURE = ROOT / "tests" / "fixtures" / "runtime_tlsf_wasm.c"
WASM_RUNNER = (
    ROOT / "tests" / "fixtures" / "runtime_tlsf_wasm_runner.js"
)
LOCAL_WASM_LINKER = (
    ROOT
    / "build"
    / "toolchains"
    / "lld-23.1.0"
    / "bin"
    / "wasm-ld"
)
WASM_OBJECT_SIZE = 145930
WASM_OBJECT_SHA256 = (
    "d192923b3956053c98d10105df19922be37ea153a9941f003f583702dfd516c9"
)
WASM_MODULE_SIZE = 9008
WASM_MODULE_SHA256 = (
    "11bd1b0dbab90c5ca463c01d5be52b9795bb0b2eda0915fecbdd7315c97e02b9"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

APPLICATION_BASE = 0x00438000
STOCK_START = 0x004CFD18
STOCK_END = 0x004D09B4
STOCK_SHA256 = (
    "007d8ac1f0e118281a07f6bde1049256800894d9684dff16e1d316f1ea4a7f9d"
)
VENDOR_HASHES = {
    VENDOR_SOURCE: (
        "2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2"
    ),
    VENDOR_HEADER: (
        "f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f"
    ),
}

PUBLIC_FUNCTIONS = {
    "open_cfw_tlsf_create",
    "open_cfw_tlsf_create_with_pool",
    "open_cfw_tlsf_destroy",
    "open_cfw_tlsf_get_pool",
    "open_cfw_tlsf_add_pool",
    "open_cfw_tlsf_remove_pool",
    "open_cfw_tlsf_malloc",
    "open_cfw_tlsf_memalign",
    "open_cfw_tlsf_realloc",
    "open_cfw_tlsf_free",
    "open_cfw_tlsf_block_size",
    "open_cfw_tlsf_size",
    "open_cfw_tlsf_align_size",
    "open_cfw_tlsf_block_size_min",
    "open_cfw_tlsf_block_size_max",
    "open_cfw_tlsf_pool_overhead",
    "open_cfw_tlsf_alloc_overhead",
    "open_cfw_tlsf_walk_pool",
    "open_cfw_tlsf_check",
    "open_cfw_tlsf_check_pool",
}
PORT_FUNCTIONS = {
    "open_cfw_tlsf_assert_fail",
    "open_cfw_tlsf_diagnostic",
    "open_cfw_tlsf_memcpy",
}
INTEGRATED_LOCAL_FUNCTIONS = {
    "default_walker",
    "block_insert",
    "block_locate_free",
    "block_merge_next",
    "block_prepare_used",
    "block_remove",
    "block_split",
}
INTEGRATED_INPUT_HASHES = {
    "components/apollo_main/core_overlay/runtime_tlsf.c": (
        "12ac5787711713de2610b71fe3d9875cc383717ce7ecd9ce5af16bf5709d76cf"
    ),
    "third_party/tlsf/tlsf.c": (
        "2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2"
    ),
    "third_party/tlsf/tlsf.h": (
        "f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/assert.h": (
        "4696db77e62a7c0a61aa6d07a4b0cb2fcd778c8f77d80646fb31307390185f7e"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/limits.h": (
        "cb33bcc2beb04eede00b4c7e939f0b2ad8a2b2ffd9133f2e8176392b1bab9387"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/stddef.h": (
        "1103494bc89f20fbe6bd95a9312c47af11ba2fb40a246e74efdeea8166e607a5"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/stdio.h": (
        "f765dcabcb6215fed307e4a0665180ae497e86eeb432ee21cf3276289cf97101"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/stdlib.h": (
        "de648e00e3a88a69cbf327d7d8d52bdfaa9e9d19711c177c9e028c456bd8a496"
    ),
    "components/apollo_main/core_overlay/tlsf_compat/string.h": (
        "b5b51f6f3baddace8e5fb9964f813e5754dfdf28499c4a4db5660c521d76b868"
    ),
}
STOCK_PUBLIC_REDIRECTS = {
    0x004D0580: "open_cfw_tlsf_walk_pool",
    0x004D05E4: "open_cfw_tlsf_block_size",
    0x004D05FA: "open_cfw_tlsf_pool_overhead",
    0x004D06EC: "open_cfw_tlsf_create_with_pool",
    0x004D0716: "open_cfw_tlsf_get_pool",
    0x004D0722: "open_cfw_tlsf_malloc",
    0x004D0744: "open_cfw_tlsf_memalign",
    0x004D0808: "open_cfw_tlsf_free",
    0x004D0868: "open_cfw_tlsf_realloc",
}
STOCK_REDIRECT_SPANS = {
    0x004D0580: (
        100,
        "387065af5f49439c736ae479d48bb51da18413863c4fad7c06fd5e013d2d8e4a",
    ),
    0x004D05E4: (
        22,
        "edbb5ddd98897bc59d466f3915a8aeda3406fa492942a0f9f25a0a4c2776eead",
    ),
    0x004D05FA: (
        10,
        "06a8fda7cea29923fddee0fad896584788a30c6a2bbcc862d81ffb6d6658dfca",
    ),
    0x004D06EC: (
        42,
        "3299fcb5966228ccc504f99d7fc74f3721e2b6a8eb294ec921df8a7a6c54fba3",
    ),
    0x004D0716: (
        12,
        "2bad574e98282d970beea89187dd75da869c499cf0202dce0ccf4a94b9c5cf55",
    ),
    0x004D0722: (
        34,
        "13a5cfb9e7c0787b215d02f411726522b18926adfcbbfaf4e64c0f73526e8539",
    ),
    0x004D0744: (
        190,
        "bf61aff3a89d3499fe24bac533b009e7c24d8e5b6aadf1fed383ef0984f9b94c",
    ),
    0x004D0808: (
        74,
        "6e865a6172cfb972c34bd6ff037c41850292646029ebb069c0d1f4385ecd739f",
    ),
    0x004D0868: (
        226,
        "a4d4941ab74a2ef25d2b52a11bd567b2015bdaefc7c1ef5dc70c73e8b39a192b",
    ),
}
EXTERNAL_STOCK_TLSF_CALLS = (
    (0x00474CEE, 0x004D0722),
    (0x00474D30, 0x004D0808),
    (0x00474D74, 0x004D0868),
    (0x00484148, 0x004D06EC),
    (0x004841A2, 0x004D0722),
    (0x004841AE, 0x004D05E4),
    (0x004841FE, 0x004D0744),
    (0x0048420A, 0x004D05E4),
    (0x00484250, 0x004D05E4),
    (0x0048425C, 0x004D0868),
    (0x00484272, 0x004D05E4),
    (0x004842B8, 0x004D05E4),
    (0x004842C2, 0x004D0808),
    (0x0057F56C, 0x004D0716),
    (0x0057F596, 0x004D0580),
    (0x0057F5AA, 0x004D05FA),
    (0x0057FAEC, 0x004D0722),
    (0x0057FB1C, 0x004D0722),
    (0x0057FB48, 0x004D0808),
    (0x0057FC08, 0x004D0808),
    (0x0057FC1A, 0x004D0808),
    (0x0057FE44, 0x004D0722),
    (0x0057FED6, 0x004D0808),
    (0x005EDA7C, 0x004D06EC),
)
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-nostdinc",
]


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeTlsfTests(unittest.TestCase):
    """TLSF source-integration and host-semantic verification."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_tlsf_host.dylib"
            if sys.platform == "darwin"
            else "runtime_tlsf_host.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls._configure_native_api()

        cls.target_object = temporary / "runtime_tlsf.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-I",
                str(COMPAT_ROOT),
                "-I",
                str(VENDOR_ROOT),
                "-DOPEN_CFW_TEST_TLSF_TARGET=1",
                "-c",
                str(FIXTURE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.target_data, cls.target_sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        (
            cls.extracted_overlay,
            cls.extracted_functions,
            cls.extraction_report,
        ) = apollo_overlay.extract_linked_overlay(cls.target_object)
        cls.target_symbols = cls._parse_target_symbols(apollo_overlay)
        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        cls.integrated_temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-tlsf-integrated-",
            dir=build_root,
        )
        integrated_root = Path(cls.integrated_temporary.name)
        stage_config = json.loads(
            (COMPONENT_ROOT / "overlay.json").read_text(encoding="utf-8")
        )
        stage_config["expected"] = stage_config["core_stage_expected"]
        for profile in stage_config.get("toolchain_profiles", {}).values():
            if "core_stage_expected" in profile:
                profile["expected"] = profile["core_stage_expected"]
        stage_config_path = integrated_root / "core-stage-overlay.json"
        stage_config_path.write_text(json.dumps(stage_config), encoding="utf-8")
        cls.integrated_report = apollo_overlay.build(
            root=ROOT,
            config_path=stage_config_path,
            output_dir=integrated_root,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.integrated_temporary.cleanup()
        cls.temporary.cleanup()

    @classmethod
    def _configure_native_api(cls) -> None:
        size_functions = (
            "open_cfw_tlsf_size",
            "open_cfw_tlsf_align_size",
            "open_cfw_tlsf_block_size_min",
            "open_cfw_tlsf_block_size_max",
            "open_cfw_tlsf_pool_overhead",
            "open_cfw_tlsf_alloc_overhead",
            "open_cfw_test_tlsf_host_pointer_size",
            "open_cfw_test_tlsf_host_size_t_size",
            "open_cfw_test_tlsf_host_ptrdiff_t_size",
        )
        for name in size_functions:
            function = getattr(cls.loaded, name)
            function.argtypes = []
            function.restype = ctypes.c_size_t

        cls.host_lane_label = (
            cls.loaded.open_cfw_test_tlsf_host_lane_label
        )
        cls.host_lane_label.argtypes = []
        cls.host_lane_label.restype = ctypes.c_char_p

        cls.create = cls.loaded.open_cfw_tlsf_create
        cls.create.argtypes = [ctypes.c_void_p]
        cls.create.restype = ctypes.c_void_p
        cls.create_with_pool = cls.loaded.open_cfw_tlsf_create_with_pool
        cls.create_with_pool.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.create_with_pool.restype = ctypes.c_void_p
        cls.destroy = cls.loaded.open_cfw_tlsf_destroy
        cls.destroy.argtypes = [ctypes.c_void_p]
        cls.destroy.restype = None
        cls.get_pool = cls.loaded.open_cfw_tlsf_get_pool
        cls.get_pool.argtypes = [ctypes.c_void_p]
        cls.get_pool.restype = ctypes.c_void_p
        cls.add_pool = cls.loaded.open_cfw_tlsf_add_pool
        cls.add_pool.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        cls.add_pool.restype = ctypes.c_void_p
        cls.remove_pool = cls.loaded.open_cfw_tlsf_remove_pool
        cls.remove_pool.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.remove_pool.restype = None
        cls.allocate = cls.loaded.open_cfw_tlsf_malloc
        cls.allocate.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.allocate.restype = ctypes.c_void_p
        cls.memalign = cls.loaded.open_cfw_tlsf_memalign
        cls.memalign.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        cls.memalign.restype = ctypes.c_void_p
        cls.reallocate = cls.loaded.open_cfw_tlsf_realloc
        cls.reallocate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        cls.reallocate.restype = ctypes.c_void_p
        cls.free = cls.loaded.open_cfw_tlsf_free
        cls.free.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.free.restype = None
        cls.block_size = cls.loaded.open_cfw_tlsf_block_size
        cls.block_size.argtypes = [ctypes.c_void_p]
        cls.block_size.restype = ctypes.c_size_t
        cls.check = cls.loaded.open_cfw_tlsf_check
        cls.check.argtypes = [ctypes.c_void_p]
        cls.check.restype = ctypes.c_int
        cls.check_pool = cls.loaded.open_cfw_tlsf_check_pool
        cls.check_pool.argtypes = [ctypes.c_void_p]
        cls.check_pool.restype = ctypes.c_int
        cls.walker_type = ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_int,
            ctypes.c_void_p,
        )
        cls.walk_pool = cls.loaded.open_cfw_tlsf_walk_pool
        cls.walk_pool.argtypes = [
            ctypes.c_void_p,
            cls.walker_type,
            ctypes.c_void_p,
        ]
        cls.walk_pool.restype = None

    @classmethod
    def _parse_target_symbols(cls, apollo_overlay):
        data = cls.target_data
        sections = cls.target_sections
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append(
                {
                    "name": apollo_overlay.elf_string(
                        strings, fields[0], "symbol"
                    ),
                    "value": fields[1],
                    "size": fields[2],
                    "binding": fields[3] >> 4,
                    "type": fields[3] & 0x0F,
                    "section": fields[5],
                }
            )
        return symbols

    @classmethod
    def _new_allocator(cls, byte_count: int = 64 * 1024):
        alignment = cls.loaded.open_cfw_tlsf_align_size()
        storage = ctypes.create_string_buffer(byte_count + alignment)
        address = ctypes.addressof(storage)
        aligned = (address + alignment - 1) & ~(alignment - 1)
        allocator = cls.create_with_pool(aligned, byte_count)
        if not allocator:
            raise AssertionError("native TLSF pool creation failed")
        return storage, int(allocator), int(cls.get_pool(allocator))

    @classmethod
    def _walk(cls, pool: int):
        observed = []

        @cls.walker_type
        def walker(pointer, size, used, _user):
            observed.append((int(pointer), int(size), int(used)))

        cls.walk_pool(pool, walker, None)
        return observed

    def test_vendored_files_hash_line_endings_and_license_are_exact(
        self,
    ) -> None:
        for path, expected_hash in VENDOR_HASHES.items():
            data = path.read_bytes()
            with self.subTest(path=path.name):
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected_hash)
                self.assertIn(b"\r\n", data)
                self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

        header = VENDOR_HEADER.read_text(encoding="ascii")
        license_fragments = (
            "Copyright (c) 2006-2016, Matthew Conte",
            "Redistribution and use in source and binary forms, with or without",
            "Redistributions of source code must retain the above copyright",
            "Redistributions in binary form must reproduce the above copyright",
            "Neither the name of the copyright holder nor the",
            'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
            "IN NO EVENT SHALL MATTHEW CONTE BE LIABLE",
        )
        for fragment in license_fragments:
            self.assertIn(fragment, header)
        readme = VENDOR_README.read_text(encoding="utf-8")
        self.assertIn("deff9ab509341f264addbd3c8ada533678591905", readme)
        self.assertIn("BSD 3-Clause", readme)

    def test_recovered_g2_configuration_and_stock_span_are_exact(
        self,
    ) -> None:
        source = VENDOR_SOURCE.read_text(encoding="ascii")
        for fragment in (
            "SL_INDEX_COUNT_LOG2 = 5,",
            "ALIGN_SIZE_LOG2 = 2,",
            "FL_INDEX_MAX = 30,",
            "SL_INDEX_COUNT = (1 << SL_INDEX_COUNT_LOG2),",
            "FL_INDEX_SHIFT = (SL_INDEX_COUNT_LOG2 + ALIGN_SIZE_LOG2),",
            "FL_INDEX_COUNT = (FL_INDEX_MAX - FL_INDEX_SHIFT + 1),",
            "SMALL_BLOCK_SIZE = (1 << FL_INDEX_SHIFT),",
            "static const size_t block_header_overhead = sizeof(size_t);",
            "sizeof(block_header_t) - sizeof(block_header_t*);",
            "static const size_t block_size_max = tlsf_cast(size_t, 1) << FL_INDEX_MAX;",
            "block_header_t* blocks[FL_INDEX_COUNT][SL_INDEX_COUNT];",
            "typedef ptrdiff_t tlsfptr_t;",
        ):
            self.assertIn(fragment, source)

        image = OFFICIAL.read_bytes()
        start = 0x20 + STOCK_START - APPLICATION_BASE
        end = 0x20 + STOCK_END - APPLICATION_BASE
        span = image[start:end]
        self.assertEqual(len(span), 3228)
        self.assertEqual(hashlib.sha256(span).hexdigest(), STOCK_SHA256)

    def test_stock_caller_closure_reaches_only_the_nine_redirect_entries(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[0x20:]
        branches = []
        for offset in range(0, len(application) - 3, 2):
            first, second = struct.unpack_from("<HH", application, offset)
            if first & 0xF800 != 0xF000 or second & 0x9000 != 0x9000:
                continue
            sign = (first >> 10) & 1
            j1 = (second >> 13) & 1
            j2 = (second >> 11) & 1
            i1 = (~(j1 ^ sign)) & 1
            i2 = (~(j2 ^ sign)) & 1
            immediate = (
                (sign << 24)
                | (i1 << 23)
                | (i2 << 22)
                | ((first & 0x03FF) << 12)
                | ((second & 0x07FF) << 1)
            )
            if immediate & (1 << 24):
                immediate -= 1 << 25
            source = APPLICATION_BASE + offset
            target = source + 4 + immediate
            if STOCK_START <= target < STOCK_END:
                branches.append(
                    (
                        source,
                        target,
                        "BL" if second & 0x4000 else "B.W",
                        application[offset:offset + 4].hex(),
                    )
                )

        self.assertEqual(len(branches), 157)
        self.assertTrue(all(kind == "BL" for _s, _t, kind, _b in branches))
        canonical = "".join(
            f"{source:08x},{target:08x},{kind},{encoded}\n"
            for source, target, kind, encoded in branches
        ).encode("ascii")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            "0df083115ba1b63547b05e494985fe24e6d6a7e70aa4f887e5e7b47312e6e1db",
        )

        external = [
            record
            for record in branches
            if not STOCK_START <= record[0] < STOCK_END
        ]
        internal = [
            record
            for record in branches
            if STOCK_START <= record[0] < STOCK_END
        ]
        self.assertEqual(len(external), 24)
        self.assertEqual(len(internal), 133)
        self.assertEqual(
            tuple((source, target) for source, target, _kind, _bytes in external),
            EXTERNAL_STOCK_TLSF_CALLS,
        )
        self.assertEqual(
            {target for _source, target, _kind, _bytes in external},
            set(STOCK_PUBLIC_REDIRECTS),
        )
        external_canonical = "".join(
            f"{source:08x},{target:08x},{kind},{encoded}\n"
            for source, target, kind, encoded in external
        ).encode("ascii")
        self.assertEqual(
            hashlib.sha256(external_canonical).hexdigest(),
            "722e5abdbf52daf7cbe038bd03332c3853fa6dd48e1f1eed9bce104c33e9d97b",
        )

    def test_native_lane_is_explicitly_semantic_not_abi_proof(self) -> None:
        self.assertEqual(
            self.host_lane_label().decode("ascii"),
            "semantic coverage only; not 32-bit ABI proof",
        )
        pointer_size = (
            self.loaded.open_cfw_test_tlsf_host_pointer_size()
        )
        size_t_size = self.loaded.open_cfw_test_tlsf_host_size_t_size()
        ptrdiff_size = (
            self.loaded.open_cfw_test_tlsf_host_ptrdiff_t_size()
        )
        self.assertEqual(pointer_size, ctypes.sizeof(ctypes.c_void_p))
        self.assertEqual(size_t_size, ctypes.sizeof(ctypes.c_size_t))
        self.assertEqual(ptrdiff_size, ctypes.sizeof(ctypes.c_ssize_t))
        self.assertIn(
            "native lane provides allocator semantic coverage only",
            FIXTURE.read_text(encoding="utf-8"),
        )

    def test_native_pool_creation_alignment_and_constants(self) -> None:
        pointer_size = ctypes.sizeof(ctypes.c_void_p)
        alignment = self.loaded.open_cfw_tlsf_align_size()
        self.assertEqual(alignment, 8 if pointer_size == 8 else 4)
        self.assertEqual(
            self.loaded.open_cfw_tlsf_alloc_overhead(),
            ctypes.sizeof(ctypes.c_size_t),
        )
        self.assertEqual(
            self.loaded.open_cfw_tlsf_pool_overhead(),
            2 * ctypes.sizeof(ctypes.c_size_t),
        )
        self.assertEqual(
            self.loaded.open_cfw_tlsf_block_size_min(),
            3 * pointer_size,
        )
        self.assertEqual(
            self.loaded.open_cfw_tlsf_block_size_max(),
            1 << (32 if pointer_size == 8 else 30),
        )
        fl_count = (
            (32 if pointer_size == 8 else 30)
            - (5 + (3 if pointer_size == 8 else 2))
            + 1
        )
        expected_control = (
            4 * pointer_size
            + 4
            + fl_count * 4
            + fl_count * 32 * pointer_size
        )
        expected_control = (
            expected_control + pointer_size - 1
        ) & ~(pointer_size - 1)
        self.assertEqual(self.loaded.open_cfw_tlsf_size(), expected_control)

        raw = ctypes.create_string_buffer(expected_control + alignment)
        base = ctypes.addressof(raw)
        aligned = (base + alignment - 1) & ~(alignment - 1)
        control = self.create(aligned)
        self.assertEqual(control, aligned)
        pool_storage = ctypes.create_string_buffer(8192 + alignment)
        pool_base = ctypes.addressof(pool_storage)
        pool_address = (
            pool_base + alignment - 1
        ) & ~(alignment - 1)
        self.assertEqual(
            self.add_pool(control, pool_address, 8192),
            pool_address,
        )
        allocation = self.allocate(control, 257)
        self.assertTrue(allocation)
        self.free(control, allocation)
        self.assertEqual(self.check(control), 0)
        self.assertEqual(self.check_pool(pool_address), 0)
        self.remove_pool(control, pool_address)
        self.destroy(control)
        self.assertFalse(self.create(aligned + 1))
        host_libc = ctypes.CDLL(None)
        host_libc.fflush.argtypes = [ctypes.c_void_p]
        host_libc.fflush.restype = ctypes.c_int
        self.assertEqual(host_libc.fflush(None), 0)

        storage, allocator, pool = self._new_allocator()
        self.assertIsNotNone(storage)
        self.assertEqual(pool, allocator + expected_control)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

    def test_native_allocation_exhaustion_and_block_sizes(self) -> None:
        storage, allocator, pool = self._new_allocator(48 * 1024)
        self.assertIsNotNone(storage)
        allocations = []
        requested_sizes = (1, 2, 3, 7, 12, 31, 128, 511, 1024)
        for requested in requested_sizes:
            pointer = self.allocate(allocator, requested)
            self.assertTrue(pointer)
            allocations.append(int(pointer))
            self.assertEqual(int(pointer) % self.loaded.open_cfw_tlsf_align_size(), 0)
            self.assertGreaterEqual(self.block_size(pointer), requested)
            ctypes.memset(pointer, requested & 0xFF, requested)

        while True:
            pointer = self.allocate(allocator, 1024)
            if not pointer:
                break
            allocations.append(int(pointer))
        self.assertGreater(len(allocations), len(requested_sizes))
        self.assertFalse(self.allocate(allocator, 1024))
        self.assertEqual(self.block_size(None), 0)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

        for pointer in allocations:
            self.free(allocator, pointer)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self._walk(pool)[0][2], 0)

    def test_native_memalign_obeys_requested_power_of_two(self) -> None:
        storage, allocator, pool = self._new_allocator()
        self.assertIsNotNone(storage)
        allocations = []
        for alignment in (4, 8, 16, 32, 64, 256, 1024):
            pointer = self.memalign(allocator, alignment, 173)
            with self.subTest(alignment=alignment):
                self.assertTrue(pointer)
                self.assertEqual(int(pointer) % alignment, 0)
                self.assertGreaterEqual(self.block_size(pointer), 173)
            allocations.append(int(pointer))
        self.assertFalse(self.memalign(allocator, 64, 0))
        for pointer in allocations:
            self.free(allocator, pointer)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

    def test_native_realloc_preserves_grows_shrinks_zero_and_null(
        self,
    ) -> None:
        storage, allocator, pool = self._new_allocator()
        self.assertIsNotNone(storage)

        pointer = self.reallocate(allocator, None, 64)
        self.assertTrue(pointer)
        initial = bytes((index * 11 + 7) & 0xFF for index in range(64))
        ctypes.memmove(pointer, initial, len(initial))

        grown = self.reallocate(allocator, pointer, 1024)
        self.assertTrue(grown)
        self.assertEqual(ctypes.string_at(grown, len(initial)), initial)
        grown_data = bytes((index * 19 + 3) & 0xFF for index in range(1024))
        ctypes.memmove(grown, grown_data, len(grown_data))

        shrunk = self.reallocate(allocator, grown, 37)
        self.assertTrue(shrunk)
        self.assertEqual(int(shrunk), int(grown))
        self.assertEqual(ctypes.string_at(shrunk, 37), grown_data[:37])
        self.assertGreaterEqual(self.block_size(shrunk), 37)

        self.assertFalse(self.reallocate(allocator, shrunk, 0))
        replacement = self.allocate(allocator, 64)
        self.assertTrue(replacement)
        self.free(allocator, replacement)
        self.assertFalse(self.reallocate(allocator, None, 0))
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

    def test_native_free_coalesces_adjacent_blocks(self) -> None:
        storage, allocator, pool = self._new_allocator(24 * 1024)
        self.assertIsNotNone(storage)
        allocations = []
        while True:
            pointer = self.allocate(allocator, 256)
            if not pointer:
                break
            allocations.append(int(pointer))
        self.assertGreater(len(allocations), 3)
        first, second = allocations[:2]
        first_size = self.block_size(first)
        second_size = self.block_size(second)
        self.free(allocator, first)
        self.free(allocator, second)
        combined = self.allocate(allocator, first_size + second_size)
        self.assertEqual(int(combined), first)

        self.free(allocator, combined)
        for pointer in allocations[2:]:
            self.free(allocator, pointer)
        walked = self._walk(pool)
        self.assertEqual(len(walked), 1)
        self.assertEqual(walked[0][2], 0)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

    def test_native_pool_walk_and_integrity_checks_track_usage(self) -> None:
        storage, allocator, pool = self._new_allocator()
        self.assertIsNotNone(storage)
        pointers = [
            int(self.allocate(allocator, size))
            for size in (48, 96, 192)
        ]
        walked = self._walk(pool)
        self.assertEqual(sum(used for _ptr, _size, used in walked), 3)
        self.assertTrue(all(size > 0 for _ptr, size, _used in walked))

        self.free(allocator, pointers[1])
        walked = self._walk(pool)
        self.assertEqual(sum(used for _ptr, _size, used in walked), 2)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)

        self.free(allocator, pointers[0])
        self.free(allocator, pointers[2])
        walked = self._walk(pool)
        self.assertEqual(len(walked), 1)
        self.assertEqual(walked[0][2], 0)

    def test_native_deterministic_randomized_stress(self) -> None:
        storage, allocator, pool = self._new_allocator(256 * 1024)
        self.assertIsNotNone(storage)
        generator = random.Random(0x004CFD18)
        live = {}

        for step in range(2000):
            choice = generator.randrange(100)
            if not live or choice < 52:
                requested = generator.randint(1, 2048)
                if choice % 5 == 0:
                    alignment = 1 << generator.randint(3, 9)
                    pointer = self.memalign(
                        allocator, alignment, requested
                    )
                    if pointer:
                        self.assertEqual(int(pointer) % alignment, 0)
                else:
                    pointer = self.allocate(allocator, requested)
                if pointer:
                    pointer = int(pointer)
                    pattern = (step * 37 + 13) & 0xFF
                    ctypes.memset(pointer, pattern, requested)
                    live[pointer] = (requested, pattern)
            elif choice < 77:
                pointer = generator.choice(tuple(live))
                old_size, old_pattern = live[pointer]
                requested = generator.randint(1, 3072)
                resized = self.reallocate(allocator, pointer, requested)
                if resized:
                    resized = int(resized)
                    preserved = min(old_size, requested)
                    self.assertEqual(
                        ctypes.string_at(resized, preserved),
                        bytes([old_pattern]) * preserved,
                    )
                    del live[pointer]
                    pattern = (step * 53 + 29) & 0xFF
                    ctypes.memset(resized, pattern, requested)
                    live[resized] = (requested, pattern)
                else:
                    self.assertEqual(
                        ctypes.string_at(pointer, old_size),
                        bytes([old_pattern]) * old_size,
                    )
            else:
                pointer = generator.choice(tuple(live))
                requested, pattern = live.pop(pointer)
                self.assertEqual(
                    ctypes.string_at(pointer, requested),
                    bytes([pattern]) * requested,
                )
                self.free(allocator, pointer)

            if step % 25 == 0:
                self.assertEqual(self.check(allocator), 0)
                self.assertEqual(self.check_pool(pool), 0)

        for pointer, (requested, pattern) in live.items():
            self.assertEqual(
                ctypes.string_at(pointer, requested),
                bytes([pattern]) * requested,
            )
            self.free(allocator, pointer)
        self.assertEqual(self.check(allocator), 0)
        self.assertEqual(self.check_pool(pool), 0)
        self.assertEqual(len(self._walk(pool)), 1)

    def test_target_combined_elf32_arm_abi_symbols_and_extractor(
        self,
    ) -> None:
        data = self.target_data
        self.assertEqual(data[:4], b"\x7fELF")
        self.assertEqual(data[4], 1, "target object must be ELF32")
        self.assertEqual(data[5], 1, "target object must be little-endian")
        self.assertEqual(struct.unpack_from("<H", data, 18)[0], 40)

        runtime = RUNTIME_SOURCE.read_text(encoding="utf-8")
        for assertion in (
            '_Static_assert(sizeof(void *) == 4,',
            "_Static_assert(sizeof(size_t) == 4,",
            "_Static_assert(sizeof(ptrdiff_t) == 4,",
        ):
            self.assertIn(assertion, runtime)
        fixture = FIXTURE.read_text(encoding="utf-8")
        self.assertIn(
            '#include "../../components/apollo_main/core_overlay/runtime_tlsf.c"',
            fixture,
        )
        self.assertIn(
            '#include "../../third_party/tlsf/tlsf.c"',
            fixture,
        )

        global_functions = {
            symbol["name"]
            for symbol in self.target_symbols
            if symbol["binding"] == 1
            and symbol["type"] == 2
            and symbol["section"] != 0
        }
        self.assertEqual(global_functions, PUBLIC_FUNCTIONS | PORT_FUNCTIONS)
        self.assertEqual(
            PUBLIC_FUNCTIONS,
            {
                name
                for name in global_functions
                if name not in PORT_FUNCTIONS
            },
        )

        undefined = {
            symbol["name"]
            for symbol in self.target_symbols
            if symbol["name"] and symbol["section"] == 0
        }
        self.assertEqual(undefined, set())
        self.assertTrue(self.extracted_overlay)
        self.assertTrue(
            PUBLIC_FUNCTIONS.issubset(self.extracted_functions)
        )
        self.assertTrue(
            PORT_FUNCTIONS.issubset(self.extracted_functions)
        )
        self.assertGreater(
            self.extraction_report["resolved_relocation_count"], 0
        )

    @_APPLE_ONLY
    def test_source_module_and_all_stock_entries_are_integrated_atomically(
        self,
    ) -> None:
        config = json.loads(
            (COMPONENT_ROOT / "overlay.json").read_text(encoding="utf-8")
        )
        source_records = {
            record["path"]: record
            for record in config["sources"]
        }
        for path, expected_hash in INTEGRATED_INPUT_HASHES.items():
            with self.subTest(path=path):
                self.assertIn(path, source_records)
                self.assertEqual(
                    source_records[path]["sha256"],
                    expected_hash,
                )
                self.assertEqual(
                    hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                    expected_hash,
                )
        self.assertEqual(
            config["toolchain"]["include_dirs"],
            [
                "components/apollo_main/core_overlay/tlsf_compat",
                "third_party/cJSON/g2-compat",
            ],
        )
        integrated_names = (
            PUBLIC_FUNCTIONS
            | PORT_FUNCTIONS
            | INTEGRATED_LOCAL_FUNCTIONS
        )
        self.assertTrue(integrated_names.issubset(config["functions"]))
        self.assertTrue(
            integrated_names.issubset(
                self.integrated_report["overlay"]["functions"]
            )
        )
        redirect_sites = {
            site["runtime_address"]: site
            for site in config["patch_sites"]
            if site["runtime_address"] in STOCK_PUBLIC_REDIRECTS
        }
        self.assertEqual(
            set(redirect_sites),
            set(STOCK_PUBLIC_REDIRECTS),
        )
        for address, target in STOCK_PUBLIC_REDIRECTS.items():
            with self.subTest(address=f"0x{address:08X}"):
                site = redirect_sites[address]
                self.assertEqual(site["target_function"], target)
                self.assertEqual(site["branch"], "b_w")
                expected_size, expected_hash = STOCK_REDIRECT_SPANS[address]
                self.assertEqual(site["expected_size"], expected_size)
                self.assertEqual(site["expected_sha256"], expected_hash)
                stock_offset = 0x20 + address - APPLICATION_BASE
                stock_bytes = OFFICIAL.read_bytes()[
                    stock_offset:stock_offset + expected_size
                ]
                self.assertEqual(
                    hashlib.sha256(stock_bytes).hexdigest(),
                    expected_hash,
                )

        overlay = self.integrated_report["overlay"]
        self.assertEqual(overlay["size"], 360578)
        self.assertEqual(
            overlay["sha256"],
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
        )
        self.assertEqual(overlay["overlay_end_exclusive"], 0x007EC3A6)
        self.assertEqual(len(overlay["functions"]), 2_436)
        self.assertEqual(len(overlay["patched_sites"]), 2_324)
        self.assertEqual(overlay["link"]["text_size"], 109592)
        self.assertEqual(overlay["link"]["rodata_size"], 3996)
        self.assertEqual(
            overlay["link"]["resolved_relocation_count"],
            906,
        )
        self.assertEqual(
            overlay["functions"]["block_split"],
            {"offset": 109188, "size": 184},
        )
        self.assertEqual(
            overlay["functions"]["block_remove"],
            {"offset": 109372, "size": 220},
        )
        self.assertEqual(len(self.integrated_report["sources"]), 296)
        isolated_leaves = self.integrated_report["isolated_leaves"]
        self.assertEqual(
            {
                leaf["extraction"]["function"]: (
                    leaf["placement"]["offset"],
                    leaf["placement"]["size"],
                    leaf["placement"]["padding_before"],
                )
                for leaf in isolated_leaves
            },
            {
                "am_hal_mspi_interrupt_clear": (113588, 48, 0),
                "ulSetInterruptMask": (113636, 22, 0),
                "vClearInterruptMask": (113658, 14, 0),
                "open_cfw_littlefs_mlist_isopen": (113672, 44, 0),
                "open_cfw_littlefs_util_fromle32": (113716, 2, 0),
                "open_cfw_littlefs_util_tole32": (113720, 2, 2),
                "open_cfw_littlefs_util_frombe32": (113724, 4, 2),
                "open_cfw_littlefs_util_tobe32": (113728, 4, 0),
            },
        )
        self.assertEqual(
            sum(leaf["extraction"]["size"] for leaf in isolated_leaves),
            140,
        )
        component = self.integrated_report["component"]
        self.assertEqual(component["size"], 3883974)
        self.assertEqual(
            component["sha256"],
            "71d4e2b8011cc1e7503bdbe9e7251963f04b0092a80934d00e5a5ad181c651eb",
        )
        self.assertEqual(component["generated_patch_site_bytes"], 397_446)
        self.assertEqual(component["replaced_stock_function_bytes"], 397_626)
        self.assertEqual(component["source_owned_in_place_bytes"], 184)
        self.assertEqual(component["source_owned_bytes"], 362_962)
        self.assertEqual(component["opaque_base_bytes"], 3_123_534)
        built_sites = {
            site["runtime_address"]: site
            for site in overlay["patched_sites"]
            if site["runtime_address"] in STOCK_PUBLIC_REDIRECTS
        }
        self.assertEqual(set(built_sites), set(STOCK_PUBLIC_REDIRECTS))
        for address, target in STOCK_PUBLIC_REDIRECTS.items():
            with self.subTest(built_address=f"0x{address:08X}"):
                built = built_sites[address]
                replacement = bytes.fromhex(built["replacement_hex"])
                expected_size = STOCK_REDIRECT_SPANS[address][0]
                self.assertEqual(len(replacement), expected_size)
                self.assertEqual(
                    replacement[4:],
                    b"\x00\xbf" * ((expected_size - 4) // 2),
                )
                function = overlay["functions"][target]
                self.assertEqual(
                    built["target_address"],
                    overlay["overlay_runtime_address"]
                    + function["offset"],
                )

    def test_wasm32_ilp32_allocator_oracle_compiles_links_and_runs(
        self,
    ) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not available for the wasm32 oracle")
        linker_candidates = (
            os.environ.get("OPENCFW_WASM_LD"),
            shutil.which("wasm-ld"),
            str(LOCAL_WASM_LINKER) if LOCAL_WASM_LINKER.is_file() else None,
        )
        linker = next(
            (
                Path(os.path.abspath(candidate))
                for candidate in linker_candidates
                if candidate and Path(candidate).is_file()
            ),
            None,
        )
        if linker is None:
            self.skipTest(
                "wasm-ld is unavailable; set OPENCFW_WASM_LD to a compatible "
                "LLD 23.1.0 executable"
            )
        linker_version = subprocess.run(
            [str(linker), "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertIn("LLD 23.1.0", linker_version)
        temporary = Path(self.temporary.name)
        wasm_object = temporary / "runtime_tlsf_wasm.o"
        wasm_module = temporary / "runtime_tlsf.wasm"

        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                "--target=wasm32-unknown-unknown",
                "-O2",
                "-ffreestanding",
                "-fno-builtin",
                "-fvisibility=hidden",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-nostdinc",
                "-I",
                str(COMPAT_ROOT),
                "-I",
                str(VENDOR_ROOT),
                "-c",
                str(WASM_FIXTURE.relative_to(ROOT)),
                "-o",
                str(wasm_object),
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        subprocess.run(
            [
                str(linker),
                "--no-entry",
                "--export=open_cfw_tlsf_wasm_run",
                "--export-memory",
                "--strip-all",
                str(wasm_object),
                "-o",
                str(wasm_module),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        completed = subprocess.run(
            [str(node), str(WASM_RUNNER), str(wasm_module)],
            check=True,
            capture_output=True,
            text=True,
        )
        proof = json.loads(completed.stdout)
        wasm_object_bytes = wasm_object.read_bytes()
        module = wasm_module.read_bytes()
        self.assertEqual(module[:8], b"\x00asm\x01\x00\x00\x00")
        self.assertEqual(len(wasm_object_bytes), WASM_OBJECT_SIZE)
        self.assertEqual(
            hashlib.sha256(wasm_object_bytes).hexdigest(),
            WASM_OBJECT_SHA256,
        )
        self.assertEqual(len(module), WASM_MODULE_SIZE)
        self.assertEqual(
            hashlib.sha256(module).hexdigest(),
            WASM_MODULE_SHA256,
        )
        self.assertEqual(proof["abi"], "wasm32-ilp32")
        self.assertEqual(proof["imports"], 0)
        self.assertEqual(proof["memory_bytes"], 256 * 1024)
        self.assertEqual(proof["module_bytes"], len(module))
        self.assertEqual(proof["result"], 0)
        self.assertEqual(
            proof["sha256"],
            hashlib.sha256(module).hexdigest(),
        )

    def test_source_prefix_locks_complete_public_api_and_generic_path(
        self,
    ) -> None:
        runtime = RUNTIME_SOURCE.read_text(encoding="utf-8")
        for name in PUBLIC_FUNCTIONS:
            upstream = name.removeprefix("open_cfw_")
            self.assertIn(f"#define {upstream} {name}", runtime)
        for header in (
            "assert.h",
            "limits.h",
            "stddef.h",
            "stdio.h",
            "stdlib.h",
            "string.h",
        ):
            self.assertTrue((COMPAT_ROOT / header).is_file())
            self.assertIn(f'#include "tlsf_compat/{header}"', runtime)
        for macro in (
            "__GNUC__",
            "__GNUC_MINOR__",
            "__GNUC_PATCHLEVEL__",
            "__GNUC_STDC_INLINE__",
        ):
            self.assertIn(f"#undef {macro}", runtime)

        self.assertIn(
            "#elif defined (__ARMCC_VERSION)",
            VENDOR_SOURCE.read_text(encoding="ascii"),
        )


if __name__ == "__main__":
    unittest.main()

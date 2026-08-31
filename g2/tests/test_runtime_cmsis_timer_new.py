from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_cmsis_timer_new.c"
FIXTURE = ROOT / "tests/fixtures/runtime_cmsis_timer_new_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
TARGET = {
    "open_cfw_cmsis_timer_callback": (24, "18011968869555744b904c0083ef7e1f3af44522a0d795c0518902ea3969e1ba", [(2,10,"open_cfw_rtos_timer_get_context")]),
    "open_cfw_cmsis_timer_new": (212, "76ab027748ff511b9e88b65ce73cd289c95a29c634cccf1698cbe8c1df67874e", [(14,10,"open_cfw_cmsis_irq_context"),(74,10,"open_cfw_freertos_heap4_malloc"),(112,49,"open_cfw_cmsis_timer_callback"),(116,50,"open_cfw_cmsis_timer_callback"),(130,10,"open_cfw_rtos_timer_static_create"),(140,49,"open_cfw_cmsis_timer_callback"),(144,50,"open_cfw_cmsis_timer_callback"),(160,10,"open_cfw_rtos_timer_dynamic_create"),(200,10,"open_cfw_freertos_heap4_free")]),
}
APPLE_LINKED = {
    "open_cfw_cmsis_timer_callback": "9154e6d1e4447e52ee3d5a32b6fc1091e3a670f5df286dbbbf04989dac2fe9dd",
    "open_cfw_cmsis_timer_new": "96334d98338228a2f2f3f7e7f7ae5a8cb03dd8e25bfb9d0312e56765ad59e1d4",
}
LINUX_LINKED = {
    "open_cfw_cmsis_timer_callback": "9698269134171d47145eb11523f028367c5930d1f5fd4b9777e6eff44b3ac853",
    "open_cfw_cmsis_timer_new": "ba78ba7b90b28fc93c925e30dd94ccd1337be4c2e6c5d1eb3ff719d9b17991bc",
}


class RuntimeCmsisTimerNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(); temporary=Path(cls.temporary.name)
        clang=os.environ.get("OPENCFW_CLANG","/usr/bin/clang"); library=temporary/("new.dylib" if sys.platform=="darwin" else "new.so")
        command=[clang,"-O2","-Wall","-Wextra","-Werror",str(FIXTURE),"-dynamiclib" if sys.platform=="darwin" else "-shared"]
        if sys.platform!="darwin": command.append("-fPIC")
        subprocess.run([*command,"-o",str(library)],check=True,capture_output=True,text=True)
        cls.lib=ctypes.CDLL(str(library)); cls.lib.open_cfw_test_timer_new_reset.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_int]
        cls.lib.open_cfw_test_timer_new_call.argtypes=[ctypes.c_uint32,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_uint32]; cls.lib.open_cfw_test_timer_new_call.restype=ctypes.c_void_p
        cls.lib.open_cfw_test_timer_new_null_function.restype=ctypes.c_void_p; cls.lib.open_cfw_test_timer_new_invoke.argtypes=[ctypes.c_size_t]
        for name in ("malloc_calls","free_calls","static_calls","dynamic_calls","callback_calls","freed","buffer","context","callback","name","argument","period","reload"):
            getattr(cls.lib,f"open_cfw_test_timer_new_{name}").restype=ctypes.c_size_t
        target=temporary/"new.o"; flags=["--target=thumbv7em-none-eabi","-mthumb","-O2","-ffreestanding","-fno-jump-tables","-fomit-frame-pointer","-fno-builtin","-mno-unaligned-access","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fropi","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror"]
        subprocess.run([clang,*flags,"-c",str(SOURCE),"-o",str(target)],check=True,capture_output=True,text=True)
        sys.path.insert(0,str(ROOT/"tools")); import apollo_overlay
        data,sections=apollo_overlay.parse_elf32(target); cls.target={}
        for function in TARGET:
            section=apollo_overlay.section_named(sections,f".text.{function}"); body=data[int(section["offset"]):int(section["offset"])+int(section["size"])]; relocations=[]
            for relocation_section in sections:
                if int(relocation_section["type"])!=9 or int(relocation_section["info"])!=int(section["index"]): continue
                symbols=sections[int(relocation_section["link"])]; string_section=sections[int(symbols["link"])]; strings=data[int(string_section["offset"]):int(string_section["offset"])+int(string_section["size"])]
                names=[apollo_overlay.elf_string(strings,struct.unpack_from("<IIIBBH",data,int(symbols["offset"])+i*16)[0],"symbol") for i in range(int(symbols["size"])//16)]
                for i in range(int(relocation_section["size"])//8): offset,information=struct.unpack_from("<II",data,int(relocation_section["offset"])+i*8); relocations.append((offset,information&255,names[information>>8]))
            cls.target[function]=(body,relocations)

    @classmethod
    def tearDownClass(cls) -> None: cls.temporary.cleanup()
    def reset(self,irq=0,malloc_fail=0,create_fail=0): self.lib.open_cfw_test_timer_new_reset(irq,malloc_fail,create_fail)
    def get(self,name): return getattr(self.lib,f"open_cfw_test_timer_new_{name}")()

    def test_source_fixture_stock_and_target_contracts_are_pinned(self):
        self.assertEqual((SOURCE.stat().st_size,hashlib.sha256(SOURCE.read_bytes()).hexdigest()),(5023,"a090ccbb1938c7ff475b25ebd424fbaa480bace78a232814ab0124eba17c2684")); self.assertEqual((FIXTURE.stat().st_size,hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),(3103,"11e3b4d3a91f1937dd36d786f83af28e8787910e26c76434d69587c1b0015c52"))
        image=OFFICIAL.read_bytes()[32:]
        for a,b,sha in ((0x449398,0x4493B0,"bf6d5f543d1e89b912b7a2f6d108791ef9158d4e206ec00c42ea7187d166d5ab"),(0x4493B0,0x449498,"164802e5b4bea4aaeef33a296bf4641ad47579367fc04accb3d62b04a0cc8146")):
            body=image[a-0x438000:b-0x438000]; self.assertEqual((len(body),hashlib.sha256(body).hexdigest()),(b-a,sha))
        for name,(size,sha,relocations) in TARGET.items():
            body,actual=self.target[name]; self.assertEqual((len(body),hashlib.sha256(body).hexdigest(),actual),(size,sha,relocations))

    def test_rejects_irq_null_function_and_allocation_failure(self):
        self.reset(irq=1); self.assertIsNone(self.lib.open_cfw_test_timer_new_call(0,1,0,0,0,0)); self.assertEqual(self.get("malloc_calls"),0)
        self.reset(); self.assertIsNone(self.lib.open_cfw_test_timer_new_null_function()); self.assertEqual(self.get("malloc_calls"),0)
        self.reset(malloc_fail=1); self.assertIsNone(self.lib.open_cfw_test_timer_new_call(0,1,0,0,0,0)); self.assertEqual((self.get("malloc_calls"),self.get("dynamic_calls")),(1,0))

    def test_dynamic_create_tags_record_and_callback_invokes_application(self):
        self.reset(); self.assertEqual(self.lib.open_cfw_test_timer_new_call(0,0xA5,0,0,0,0),0x2220); self.assertEqual((self.get("malloc_calls"),self.get("dynamic_calls"),self.get("period"),self.get("reload")),(1,1,1,0)); self.assertEqual(self.get("context")&1,1)
        self.lib.open_cfw_test_timer_new_invoke(self.get("context")); self.assertEqual((self.get("callback_calls"),self.get("argument")),(1,0xA5))
        self.reset(); self.lib.open_cfw_test_timer_new_call(257,1,0,0,0,0); self.assertEqual(self.get("reload"),1)

    def test_static_buffer_layout_and_mixed_callback_allocation(self):
        buffer=ctypes.create_string_buffer(64); address=ctypes.addressof(buffer)
        self.reset(); self.assertEqual(self.lib.open_cfw_test_timer_new_call(0,0xB6,0x1234,address,52,1),0x1110); self.assertEqual((self.get("malloc_calls"),self.get("static_calls"),self.get("buffer"),self.get("context")),(0,1,address,address+44))
        self.lib.open_cfw_test_timer_new_invoke(self.get("context")); self.assertEqual((self.get("callback_calls"),self.get("argument")),(1,0xB6))
        self.reset(); self.assertEqual(self.lib.open_cfw_test_timer_new_call(0,1,0,address,44,1),0x1110); self.assertEqual((self.get("malloc_calls"),self.get("static_calls"),self.get("context")&1),(1,1,1))

    def test_invalid_attr_and_create_failure_free_only_dynamic_record(self):
        buffer=ctypes.create_string_buffer(64); address=ctypes.addressof(buffer)
        self.reset(create_fail=1); self.assertIsNone(self.lib.open_cfw_test_timer_new_call(0,1,0,address,8,1)); self.assertEqual((self.get("malloc_calls"),self.get("free_calls"),self.get("static_calls"),self.get("dynamic_calls")),(1,1,0,0))
        self.reset(create_fail=1); self.assertIsNone(self.lib.open_cfw_test_timer_new_call(0,1,0,address,52,1)); self.assertEqual((self.get("malloc_calls"),self.get("free_calls"),self.get("static_calls")),(0,0,1))

    def test_production_overlay_and_manifest_admit_callback_and_constructor(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in TARGET
        }
        self.assertEqual(set(leaves), set(TARGET))
        patches = {
            item["target_function"]
            for item in config["patch_sites"]
            if item["target_function"] in TARGET
        }
        self.assertEqual(patches, {"open_cfw_cmsis_timer_new"})
        for name, item in leaves.items():
            with self.subTest(name=name):
                self.assertEqual(
                    item["source"]["path"], SOURCE.relative_to(ROOT).as_posix()
                )
                self.assertEqual(
                    item["source"]["upstream_commit"],
                    "d213f261b5be6bb29a7cce8b84071706b72f4d53",
                )
                self.assertEqual(item["expected"]["sha256"], APPLE_LINKED[name])
                self.assertEqual(
                    item["toolchain_profiles"]["linux-clang"]["expected"][
                        "sha256"
                    ],
                    LINUX_LINKED[name],
                )
        self.assertEqual(config["expected"]["overlay_size"], 360_578)
        self.assertEqual(config["expected"]["component_size"], 3_883_974)
        self.assertEqual(
            config["toolchain_profiles"]["linux-clang"]["expected"][
                "overlay_size"
            ],
            152_912,
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(main["provider"]["size"], 3_883_974)
        self.assertEqual(
            main["provider"]["profiles"]["linux-clang"]["size"], 3_676_308
        )
        regions = {item["name"]: item for item in main["regions"]}
        self.assertEqual(
            (
                regions["apollo_cmsis_timer_callback_source_leaf"]["file_offset"],
                regions["apollo_cmsis_timer_new_source_leaf"]["file_offset"],
            ),
            (3_655_952, 3_655_976),
        )
        self.assertEqual(
            (
                manifest["package"]["expected_size"],
                manifest["package"]["profiles"]["linux-clang"]["expected_size"],
            ),
            (4_677_046, 4_469_364),
        )


if __name__=="__main__": unittest.main()

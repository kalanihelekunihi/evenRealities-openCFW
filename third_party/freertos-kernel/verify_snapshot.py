#!/usr/bin/env python3
"""Offline integrity verification for the FreeRTOS-Kernel V10.5.1 snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE_PATH = HERE / "PROVENANCE.json"

EXPECTED_REPOSITORY = "https://github.com/FreeRTOS/FreeRTOS-Kernel.git"
EXPECTED_REF = "refs/tags/V10.5.1"
EXPECTED_TAG = "V10.5.1"
EXPECTED_TAG_OBJECT = "d7b40dbed508c305c2a32ccf3982045ec9ba8734"
EXPECTED_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
EXPECTED_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
EXPECTED_UPSTREAM_BYTES = 1_476_027

# These pins are deliberately duplicated outside PROVENANCE.json.  Each row is:
# repository path, byte count, SHA-256, Git blob SHA-1.  Git blob IDs establish
# identity within the selected upstream tree; SHA-256 is the independent local
# byte-integrity check.
EXPECTED_FILE_ROWS = """
LICENSE.md	1036	508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1	9cf106272ac3b56b0c4c80218e8fc10a664ca5f4
croutine.c	16174	ebf0cdce261dc4a256c06c0d4ad2582e6026a6da0e973d4cb92092e94ce8f370	9e58334f06ece6c66b0ca2e86920f33e345c5c4d
event_groups.c	31755	76e967b14d231e4f31f014f1564f359a7bfd36bfa263ee6f437afa8c056df657	9313455a96a52c0d5e44cd0acd96a9248f2aee7f
include/FreeRTOS.h	51577	03e9c94aba57e3cf7f4f73bc2d3eb4a96ae38f3425eedb5450622ca286475a0b	4ac433230075cd13d8af0da1ae6c64b4b4153ab2
include/StackMacros.h	1608	6460e81c910496d51bc39011e35d17f5b5437b5deb03f9e91222f796d8c8bf79	6ec5063b19e987543560b3a07074063bf63aeeec
include/atomic.h	13261	e6eb26727c6cd0a87e4dec91cc55b2b1313cc3829e06662a0c73e62cafd1e751	a7866edafcb971ab4bf7a5f89571f8d6dc8522e6
include/croutine.h	28908	cf52c15fa26a8d4f82b55909b75ebfe2aab25468ba7780748912ddead9812b4e	4edf47b7cf63d71d0439ca9c9c6e93dfb1f5058b
include/deprecated_definitions.h	7800	35000a143464bbbd8df7c9a6f066a64598a24da5174a7be33972e62bfbd75f4d	6ca125b09e9e5a1f26e4b5dc126125920f7ecc95
include/event_groups.h	32529	7a38d7a3ce24bd2ff6c6003c94eea7aa7972179b1f17c1a91374334c6069f027	275f316bdcae562b86bf90ebfea33b00704e940a
include/list.h	24332	dc572f54391c0407fc25db360d912fca9118cddae7bd2e3099eb13f18804e5a9	e3663199721172989973479967716a28b14f3121
include/message_buffer.h	41008	9a8141d3d6c8044a57d7e448180c9bd2ed32e45ded32be288d095a39dced91ab	24d59e257cadc2e607925b609f1d75373fc678be
include/mpu_prototypes.h	18344	2b46a2511ce5d23a56bc83079333d8d0a2e33763e5829c9383252806887a3dc0	8e19ea0985eaded19732bfb1c8af746cdfee34dc
include/mpu_wrappers.h	11134	5014408cc33f0f616215f2b48c67b0d47ccc35bfd5f0044ac653b5bbc6cf5778	0a26d88f244eaa37518114ebcf2d4ad0f960262a
include/portable.h	10158	7ade8f368002778c723b3c4e14084910b7225cd36363ed0c948e9ea36c6f251f	a69e637441125aea4c11b13157ac9b8a1ad7aa67
include/projdefs.h	6397	8faf4220ded25b00fd72424a2fa4e63e154713ae7b42f7270f1e3289362a6312	595cbedd3c2e3cbae8ecde7c87d64bc4d70d438f
include/queue.h	65746	a3763e24a5a3a38413996fc8392efd6add1d1ee3ef507fba22daf75682241feb	df572e16fb7ba3e62dc592edd8271d917e20ba62
include/semphr.h	50523	c624e8cdfc07844d4cf35382f3cc908c872375c7a3048482bdc110bda88cc4f2	e0193bd95ccf957c87a4267bc764ae4ca6db63b3
include/stack_macros.h	8660	3cddf2b3d47ae387e376ac75eb468f9d8ffb575d68c143e08d54af4087474cce	e15adf977ed84dc0073db21aa358e41b3334bd29
include/stdint.readme	2235	69af0e53a019583b7638cd83d588179f4900693bf9c4680f4b85ad71454eca41	03208f83a2358e918b90416e8596be288a890017
include/stream_buffer.h	42757	b876d839460197d94d0f95fb93c6aeb457f6fc572d32258480fed7d4de686b6b	955c09400006785cbddf0f71f16a1c438a1f9e09
include/task.h	137375	cb1b0bbcdc66e39ba3b5a09b3e2829a5d376b8990735980613514903a3c5f493	ab8eeb82f7fad460e10be0f61b93ee63a6d20a1b
include/timers.h	63322	08d73a99380a1ba61376258c52f4fddf5df5b6dcbe0f86b0ea03f11a5ca58459	4b73908bd1b2dddd3a11564833b8e4e64de9621f
list.c	10338	db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4	afcae87f11413a14a5a95138fb9bffb6787826c4
portable/ARMv8M/ReadMe.txt	600	521d5ae0e32eca74571a7525e865740098686e1c2416376981ca45b9e798b17c	c0db1455792a764ba59188d557a7e295538b0e3c
portable/Common/mpu_wrappers.c	85800	d27f541277f2ea4f0335bc594f6574e40d5c97652f0973b710afecca44f6b637	23f8ff942330acc60d1b7a94d256beb88887bc84
portable/IAR/ARM_CM55/non_secure/port.c	54648	c2762e124d700d26ceb0dc737af706f361dd45c9e40bf683b916f1e430e37a08	349aeffb9c2fad0923fb736fa5b66c6611c5e8e4
portable/IAR/ARM_CM55/non_secure/portasm.h	3759	61af2aed89b618689b69c2e80f75a7cf8c9a46d0eaf1951f4454b775ee6fda0e	93606b14038890655efc6af872778382573a479a
portable/IAR/ARM_CM55/non_secure/portasm.s	17453	274571223c2926a7ca332fb792077c5fab43f24f2b007bcdce011515f2f0aaf4	2f0fb7eb8b4dbe0f29a60079aed563f6c6b44aa8
portable/IAR/ARM_CM55/non_secure/portmacro.h	2976	6a832802876e67a75682400354ada16ebf94cc8910936079a904cf6413a14468	538406291b7575d0c94a9714d24f45e386bb6c39
portable/IAR/ARM_CM55/non_secure/portmacrocommon.h	12636	c184e6b1727732bbdd0d4dd33b9af4ea25d13040620666123941fff464bffc99	e68692a5addc314ddc595373c15631c03789faa8
portable/IAR/ARM_CM55/secure/secure_context.c	14497	5427da21e4cb96044ca7ce3306b6bc1e0d1cf35e5775f68b6c52ba09b6251ed5	1996693f01eb2a51e98331dbf9863d9030ca0c9d
portable/IAR/ARM_CM55/secure/secure_context.h	4900	c1b017c52c8ce27b91713cc49b5ffece337f6a2edd4966fd62d53c7f1b657570	de33d15c6f5d0eb5ebc3dd2d5d9204a04a08bc77
portable/IAR/ARM_CM55/secure/secure_context_port_asm.s	4043	f7ffd63788cd984f1a0a9f58770b255f1aaf0621824e1373f6f7e1fa0853ac0e	4e26cf99dd6287f9059efafe18d19f05bdba304d
portable/IAR/ARM_CM55/secure/secure_heap.c	15951	8909249c1f06e6ce54eef447ef066f85204dcf046adb379f6b55b1a00e41fcbb	b3bf00750238986965d9023898e7a333ed2490aa
portable/IAR/ARM_CM55/secure/secure_heap.h	2070	85a4b0b34b096b0d8d4246a1d8545359952bc8e958c491d4f66e14eb60b5b1d8	e469f2ca92470c38c93f8eee9e425ee5c859c390
portable/IAR/ARM_CM55/secure/secure_init.c	4820	72bdc72a1f9cfa335ab00e90eb5b6d3b0c2457e618b3a14960d2afef79e5bc68	f6570d8636f3f55c0386008ee416dc676e9cef0a
portable/IAR/ARM_CM55/secure/secure_init.h	2094	b0b982eaff9c26a66038e8600d01d3ba5924891897e73e078999745b3c46e551	e89af71e3c54cb50587297db8a11e691f64d4eb3
portable/IAR/ARM_CM55/secure/secure_port_macros.h	4676	8c2ec8b8bdca51d42327276928de969f15b00639b4874a78f1ed3e4df0a7f453	2fb7c595ff1584586f28dfb5ba49a56ad34a47da
portable/IAR/ARM_CM55_NTZ/non_secure/port.c	54648	c2762e124d700d26ceb0dc737af706f361dd45c9e40bf683b916f1e430e37a08	349aeffb9c2fad0923fb736fa5b66c6611c5e8e4
portable/IAR/ARM_CM55_NTZ/non_secure/portasm.h	3759	61af2aed89b618689b69c2e80f75a7cf8c9a46d0eaf1951f4454b775ee6fda0e	93606b14038890655efc6af872778382573a479a
portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s	11686	eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f	4d02a431e1d759f12f50e70fc55a7b0b4d368e89
portable/IAR/ARM_CM55_NTZ/non_secure/portmacro.h	2976	6a832802876e67a75682400354ada16ebf94cc8910936079a904cf6413a14468	538406291b7575d0c94a9714d24f45e386bb6c39
portable/IAR/ARM_CM55_NTZ/non_secure/portmacrocommon.h	12636	c184e6b1727732bbdd0d4dd33b9af4ea25d13040620666123941fff464bffc99	e68692a5addc314ddc595373c15631c03789faa8
portable/MemMang/heap_4.c	20608	d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05	3af0caf2b60fc4adfb103a115fefbf1b09b21dd8
portable/readme.txt	867	a1a3d054203d05c5ec147a3acb67c70d5089cc54a6b40989ce8884fed4782ba4	af93a4b6a28787f5b6dcdd76c51d402fc69eba72
queue.c	125614	5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894	5c872e0302839d96aab90919788fdc2b0be1c09e
stream_buffer.c	61493	86d948694c723b814c9606a6c804ea7c1bd30b3da518d1d6a83b81f972e3a152	fed7eb8f956b5fd01e1879f2b4fded01d73c6558
tasks.c	223695	14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463	d97085d8736905c1eeb9d9e871c81e5970ee70ed
timers.c	50145	24962ef361f396aaa5e6e33776eeeddaf2fb251c87b6fe50602acc56c537b093	6b7be77c24b3233ca730278bda9451b8e4f99613
""".strip()


def parse_expected_files() -> dict[str, dict[str, str | int]]:
    expected: dict[str, dict[str, str | int]] = {}
    for row in EXPECTED_FILE_ROWS.splitlines():
        path, size, sha256_value, git_blob = row.split("\t")
        expected[path] = {
            "size": int(size),
            "sha256": sha256_value,
            "git_blob_sha1": git_blob,
        }
    return expected


EXPECTED_FILES = parse_expected_files()
EXPECTED_METADATA = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FreeRTOS-Kernel snapshot verification failed: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_provenance() -> dict[str, Any]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(provenance["schema_version"] == 1, "unknown provenance schema")
    require(provenance["component"] == "FreeRTOS-Kernel", "component changed")
    require(provenance["license"] == "MIT", "license changed")

    upstream = provenance["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_ref"] == EXPECTED_REF, "selected ref changed")
    require(upstream["selected_tag"] == EXPECTED_TAG, "selected tag changed")
    require(
        upstream["annotated_tag_object"] == EXPECTED_TAG_OBJECT,
        "annotated tag object changed",
    )
    require(
        upstream["tag_peeled_commit"] == EXPECTED_COMMIT,
        "tag no longer peels to selected commit",
    )
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(
        upstream["declared_kernel_version"] == "V10.5.1",
        "declared version changed",
    )
    require(upstream["tag_kind"] == "annotated", "tag kind changed")
    require(
        upstream["tag_cryptographically_signed"] is False,
        "metadata must not claim the unsigned release tag is signed",
    )

    selection = provenance["selection"]
    require(
        selection["classification"]
        == "exact official release snapshot and source-replacement baseline",
        "selection classification changed",
    )
    require(selection["upstream_file_count"] == 49, "file count changed")
    require(
        set(selection["core_sources"])
        == {
            "croutine.c",
            "event_groups.c",
            "list.c",
            "queue.c",
            "stream_buffer.c",
            "tasks.c",
            "timers.c",
        },
        "kernel core selection changed",
    )
    require(
        set(selection["portable_scope"])
        == {
            "portable/Common/mpu_wrappers.c",
            "portable/IAR/ARM_CM55/non_secure",
            "portable/IAR/ARM_CM55/secure",
            "portable/IAR/ARM_CM55_NTZ/non_secure",
            "portable/MemMang/heap_4.c",
        },
        "portable scope changed",
    )

    boundary = provenance["g2_boundary"]
    require(
        boundary["includes_freertos_config_h"] is False,
        "vendor tree must not include G2 FreeRTOSConfig.h",
    )
    require(
        boundary["includes_g2_port_or_device_support"] is False,
        "vendor tree must not claim G2 device support",
    )
    require(
        boundary["includes_g2_application_hooks"] is False,
        "vendor tree must not include G2 application hooks",
    )
    require(
        boundary["includes_task_application_allocator"] is False,
        "vendor tree must not select a task/application allocator",
    )
    require(
        boundary["authenticated_unselected_allocator_reference"]
        == "portable/MemMang/heap_4.c",
        "authenticated allocator reference changed",
    )
    require(
        boundary["snapshot_selects_portable_variant"] is False,
        "vendor snapshot must preserve both port alternatives without selecting "
        "one for compilation",
    )
    require(
        boundary["g2_selected_portable_variant"]
        == "portable/IAR/ARM_CM55_NTZ/non_secure",
        "audited G2 portable-layer selection changed",
    )
    require(
        "unequivocally selects" in boundary["g2_port_selection_status"],
        "audited G2 port-selection status changed",
    )

    require(
        provenance["files"] == EXPECTED_FILES,
        "provenance per-file pins changed",
    )
    return provenance


def verify_inventory_and_bytes() -> None:
    actual_files = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(
        actual_files == set(EXPECTED_FILES) | EXPECTED_METADATA,
        "subtree inventory changed",
    )
    require(len(EXPECTED_FILES) == 49, "hard-coded file inventory is incomplete")
    require(
        sum(int(entry["size"]) for entry in EXPECTED_FILES.values())
        == EXPECTED_UPSTREAM_BYTES,
        "hard-coded aggregate byte count changed",
    )

    for relative_path, expected in EXPECTED_FILES.items():
        path = HERE / relative_path
        require(not path.is_symlink(), f"{relative_path} became a symlink")
        data = path.read_bytes()
        require(
            len(data) == expected["size"],
            f"{relative_path} byte count changed",
        )
        require(
            sha256(data) == expected["sha256"],
            f"{relative_path} SHA-256 changed",
        )
        require(
            git_blob_sha1(data) == expected["git_blob_sha1"],
            f"{relative_path} Git blob identity changed",
        )


def verify_kernel_and_port_markers() -> None:
    task_header = (HERE / "include/task.h").read_text(encoding="ascii")
    require(
        '#define tskKERNEL_VERSION_NUMBER       "V10.5.1"' in task_header,
        "task.h lost the V10.5.1 version declaration",
    )
    for marker in (
        "#define tskKERNEL_VERSION_MAJOR        10",
        "#define tskKERNEL_VERSION_MINOR        5",
        "#define tskKERNEL_VERSION_BUILD        1",
    ):
        require(marker in task_header, f"task.h lost {marker!r}")

    source_markers = {
        "queue.c": "BaseType_t xQueueGenericSend( QueueHandle_t xQueue,",
        "tasks.c": "BaseType_t xTaskCreate( TaskFunction_t pxTaskCode,",
        "list.c": "void vListInitialise( List_t * const pxList )",
        "timers.c": "BaseType_t xTimerCreateTimerTask( void )",
        "event_groups.c": "EventGroupHandle_t xEventGroupCreate( void )",
        "stream_buffer.c": (
            "StreamBufferHandle_t xStreamBufferGenericCreate( "
            "size_t xBufferSizeBytes,"
        ),
        "croutine.c": "void vCoRoutineSchedule( void )",
    }
    for relative_path, marker in source_markers.items():
        source = (HERE / relative_path).read_text(encoding="ascii")
        require(
            "FreeRTOS Kernel V10.5.1" in source,
            f"{relative_path} lost its release marker",
        )
        require(marker in source, f"{relative_path} lost {marker!r}")

    heap_4_data = (HERE / "portable/MemMang/heap_4.c").read_bytes()
    require(
        heap_4_data.count(b"\r\n") == 537
        and heap_4_data.count(b"\n") == 537
        and heap_4_data.count(b"\r") == 537,
        "heap_4.c lost its exact upstream CRLF line endings",
    )
    heap_4_source = heap_4_data.decode("ascii")
    for marker in (
        "FreeRTOS Kernel V10.5.1",
        "SPDX-License-Identifier: MIT",
        "void * pvPortMalloc( size_t xWantedSize )",
        "void vPortFree( void * pv )",
        "#if ( configAPPLICATION_ALLOCATED_HEAP == 1 )",
        "uint8_t ucHeap[ configTOTAL_HEAP_SIZE ]",
    ):
        require(marker in heap_4_source, f"heap_4.c lost {marker!r}")

    cm55 = HERE / "portable/IAR/ARM_CM55"
    ntz = HERE / "portable/IAR/ARM_CM55_NTZ"
    require(cm55.is_dir(), "IAR ARM_CM55 port missing")
    require(ntz.is_dir(), "IAR ARM_CM55_NTZ port missing")
    require((cm55 / "secure/secure_context.c").is_file(), "secure port missing")
    require(
        not (ntz / "secure").exists(),
        "no-TrustZone alternative unexpectedly gained secure sources",
    )

    cm55_macro = (cm55 / "non_secure/portmacro.h").read_text(encoding="ascii")
    ntz_macro = (ntz / "non_secure/portmacro.h").read_text(encoding="ascii")
    for text, name in ((cm55_macro, "ARM_CM55"), (ntz_macro, "ARM_CM55_NTZ")):
        require(
            '#define portARCH_NAME                       "Cortex-M55"' in text,
            f"{name} lost its Cortex-M55 architecture marker",
        )
        require(
            "configENABLE_MVE must be defined in FreeRTOSConfig.h" in text,
            f"{name} lost its MVE configuration boundary",
        )

    shared_names = ("port.c", "portasm.h", "portmacro.h", "portmacrocommon.h")
    for name in shared_names:
        require(
            (cm55 / "non_secure" / name).read_bytes()
            == (ntz / "non_secure" / name).read_bytes(),
            f"upstream shared port file {name} no longer matches",
        )
    require(
        (cm55 / "non_secure/portasm.s").read_bytes()
        != (ntz / "non_secure/portasm.s").read_bytes(),
        "TrustZone-aware and NTZ assembly alternatives became indistinguishable",
    )

    armv8_note = (HERE / "portable/ARMv8M/ReadMe.txt").read_text(
        encoding="ascii"
    )
    require(
        "uses TrustZone then use the files from" in armv8_note,
        "upstream port-selection note lost TrustZone guidance",
    )
    require(
        "does not use TrustZone then use the files from" in armv8_note,
        "upstream port-selection note lost no-TrustZone guidance",
    )


def verify_license_and_boundary() -> None:
    license_text = (HERE / "LICENSE.md").read_text(encoding="ascii")
    for fragment in (
        "MIT License",
        "Permission is hereby granted, free of charge",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    ):
        require(fragment in license_text, f"MIT license lost {fragment!r}")

    forbidden_names = {
        "FreeRTOSConfig.h",
        "freertosconfig.h",
        "am_mcu_apollo.h",
        "am_bsp.h",
    }
    actual_names = {path.name for path in HERE.rglob("*") if path.is_file()}
    require(
        forbidden_names.isdisjoint(actual_names),
        "a G2 configuration or device file entered the vendor tree",
    )
    require(
        {
            path
            for path in EXPECTED_FILES
            if "/MemMang/" in f"/{path}/"
        }
        == {"portable/MemMang/heap_4.c"},
        "authenticated heap reference scope changed",
    )


def main() -> None:
    verify_provenance()
    verify_inventory_and_bytes()
    verify_kernel_and_port_markers()
    verify_license_and_boundary()
    print(
        "FreeRTOS-Kernel V10.5.1 official snapshot, unsigned annotated tag, "
        "49 upstream files including unselected heap_4.c reference, dual "
        "unselected port alternatives, audited G2 IAR ARM_CM55_NTZ/non_secure "
        "selection, MIT license, Git blobs, and SHA-256 pins: OK"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fail-closed Cortex-M55 link audit for the G2 LVGL/Ambiq/Nema boundary.

The default mode compiles every C translation unit in the authenticated Ambiq
draw subtree plus the cache-free software mask provider.  It emits the exact
direct provider and residual-link ledgers without fetching or importing binary
artifacts.  ``--sdk-root`` additionally accepts only the already pinned public
AmbiqSuite 5.1.0 Nema archives, performs a relocatable target link, and verifies
the resulting symbol/member/relocation closure.  No device access is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tools/build_g2_lvgl_ambiq_backend.py"
PROVENANCE = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
VECTOR_PATCH = (
    ROOT / "third_party/lvgl-ambiq-backend/g2-compat/lvgl-g2-vector-compile.patch"
)
BUFFER_HELPER_SOURCE = (
    ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.c"
)
BUFFER_HELPER_HEADER = BUFFER_HELPER_SOURCE.with_suffix(".h")
OFFICIAL_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

PUBLIC_COMMIT = "b853fded7e545f005727e13bf2ce83018c7e242d"
VECTOR_PATCH_SHA256 = "3b436c84a8aa6c9c922e33d04491a9eb716e1bb72d2bd4d96f18ce495abfca34"
EXPECTED_CANDIDATE_FILES = 20
EXPECTED_CANDIDATE_BYTES = 57_754
EXPECTED_CANDIDATE_DIGEST = "2f1b92bed322b40987cd96850afbbde963cc7d33af49dd39080249a161d49fbd"
EXPECTED_AGGREGATE_UNRESOLVED = {
    "count": 154,
    "digest": "76d1245dfa9837db10f11aa55dd2d8ca036d8d5f743a3e99918a717c618ad3a3",
}
EXPECTED_DIRECT_NEMA = {
    "count": 96,
    "digest": "497b66dd88dc1d4b8aa13ad1f3d6f2e45ee6d0afe745a09f38b3a16e76fdf051",
}
EXPECTED_PUBLIC_RESIDUAL_DIGEST = (
    "db934f5d3d45c767227f50cd4b4d02160aff380a0885cb2735814accd9c78a29"
)
EXPECTED_MAXIMAL_RESIDUAL_DIGEST = (
    "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744"
)
EXPECTED_BACKEND_GC_ROOTS = (
    "lv_ambiq_blend_mode_change", "lv_ambiq_blend_mode_clear",
    "lv_ambiq_clip_area_change", "lv_ambiq_clip_area_clear",
    "lv_ambiq_color_convert", "lv_ambiq_color_format_map_des",
    "lv_ambiq_color_format_map_src", "lv_ambiq_set_blend_blit",
    "lv_ambiq_set_blend_fill", "lv_draw_ambiq_arc",
    "lv_draw_ambiq_bind_image_texture", "lv_draw_ambiq_bind_mask_texture",
    "lv_draw_ambiq_border", "lv_draw_ambiq_box_shadow",
    "lv_draw_ambiq_common_end", "lv_draw_ambiq_common_start",
    "lv_draw_ambiq_decode_image", "lv_draw_ambiq_deinit", "lv_draw_ambiq_fill",
    "lv_draw_ambiq_get_default_unit", "lv_draw_ambiq_image", "lv_draw_ambiq_init",
    "lv_draw_ambiq_init_buf_handlers", "lv_draw_ambiq_label", "lv_draw_ambiq_layer",
    "lv_draw_ambiq_line", "lv_draw_ambiq_mask_rect",
    "lv_draw_ambiq_stencil_buffer_adjust", "lv_draw_ambiq_triangle",
    "lv_draw_ambiq_vector", "lv_draw_ambiq_vector_font",
    "lv_draw_ambiq_vector_font_init", "lv_draw_ambiq_vg_start",
    "lv_draw_sw_mask_free_param", "lv_draw_sw_mask_radius_init",
    "lv_vector_blend_to_nema", "nema_raster_error_interpret",
    "nema_raster_line_aa", "nema_vg_error_interpret",
)
EXPECTED_BACKEND_GC_ROOT_DIGEST = (
    "81c9819050afa8b9e07fd08ee11f1023bcf577b7f466fc2577d2b597bcde91f3"
)
PLATFORM_PROVIDER_SYMBOLS = frozenset({
    "am_hal_cachectrl_dcache_clean",
    "am_hal_cachectrl_dcache_invalidate",
    "am_hal_pwrctrl_periph_disable",
    "am_hal_pwrctrl_periph_enable",
    "am_hal_pwrctrl_periph_enabled",
})
PLATFORM_PROVIDER_EXPORTS = frozenset({
    *PLATFORM_PROVIDER_SYMBOLS,
    "open_cfw_cache_dcache_clean",
    "open_cfw_cache_dcache_invalidate",
    "open_cfw_delay_us",
    "open_cfw_lv_irq_disable",
    "open_cfw_pwrctrl_gpu_mode_select",
    "open_cfw_pwrctrl_periph_disable",
    "open_cfw_pwrctrl_periph_disable_mask_check",
    "open_cfw_pwrctrl_periph_enable",
    "open_cfw_pwrctrl_periph_enabled",
    "open_cfw_pwrctrl_peripheral_descriptor_get",
})
PLATFORM_PROVIDER_ARTIFACT = {
    "size": 11_320,
    "sha256": "04504e7e026eb53a08a187e037269d0f42a2e818842fc5320710c2a5952a06b7",
}
PLATFORM_PROVIDER_INPUTS = {
    "adapter": ("third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_apollo_hal_provider.c", 1_844, "11dbe37d42fe8fb4ccaf804af3034137041c8b32e44038959ff2d1b9e743bc4f", "MIT"),
    "adapter_header": ("third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_apollo_hal_provider.h", 213, "48bdf848006c9b406a9401c27b6275f504119ca88e8cdea643d18ccd235c2175", "MIT"),
    "cachectrl": ("components/apollo_main/core_overlay/cachectrl.c", 8_497, "a3ef246758074462d0e9f7d5d9046a0450e8adf8407f3fc0050c032a31c7cd22", "BSD-3-Clause"),
    "pwr_enable": ("components/apollo_main/core_overlay/pwrctrl_periph_enable.c", 11_723, "7a2a382590d734fe2020242d28a39059b67e3f10e77ecfb17db3c3201e37e3d2", "BSD-3-Clause"),
    "pwr_disable": ("components/apollo_main/core_overlay/pwrctrl_periph_disable.c", 13_469, "7af651f900d25b29bec7fe71d70893009c3d0e48c14db995d0a3a1d32494c57a", "BSD-3-Clause"),
    "pwr_enabled": ("components/apollo_main/core_overlay/pwrctrl_periph_enabled.c", 2_121, "12689a577aff71fd5ea378399ae9139585c53f76f14e93a43184d4ec730f7b34", "BSD-3-Clause"),
    "gpu_mode": ("components/apollo_main/core_overlay/pwrctrl_gpu_mode_select.c", 8_081, "ae0e754919056fa48c695ccec040983d13f1a0036d6ee920436ecbb434fc0657", "BSD-3-Clause"),
    "disable_mask": ("components/apollo_main/core_overlay/pwrctrl_periph_disable_mask_check.c", 2_967, "d9624ec87cea75f3119bfc57bf1411918be848476828b28b6a30658d9adbe74e", "BSD-3-Clause"),
    "descriptor": ("components/apollo_main/core_overlay/pwrctrl_peripheral_descriptor.c", 4_375, "5eac8ba6a9d7d8674d2ce762d29cbd234eb8cc5bc18e8da6213e350ae61e9741", "BSD-3-Clause"),
    "delay": ("components/apollo_main/core_overlay/duration_delay.c", 4_890, "3fbe50caa058994609e59b8e17871168c35c763fd4f5b1f7bee68779a9bd19ce", "BSD-3-Clause"),
    "irq": ("components/apollo_main/core_overlay/lv_runtime.c", 1_723, "b479d195b2954b07158eb74f1ae8efcb007b45142dcb612bb7d3540d275f8c3f", "MIT"),
}
PLATFORM_FIXED_IMPORTS = {
    "0x0047F90D": "stock am_hal_pwrctrl_periph_enabled entry",
    "0x004803C3": "stock GPU TON update entry",
    "0x0048032D": "stock temperature-coefficient postpone entry",
    "0x004C44BD": "stock clock request entry",
    "0x00480313": "stock SPOT update entry",
    "0x00480343": "stock temperature-coefficient pending entry",
    "0x00480827": "stock status check entry",
    "0x004807FD": "stock status change entry",
    "0x004C4531": "stock clock release entry",
    "0x004C45A5": "stock clock release-all entry",
    "0x00000041": "stock ITCM delay-cycle entry",
}
FREERTOS_PROVIDER_SYMBOLS = frozenset({
    "xQueueGenericCreate",
    "xQueueGiveFromISR",
    "xQueueSemaphoreTake",
})
FREERTOS_PROVIDER_EXPORTS = frozenset({
    *FREERTOS_PROVIDER_SYMBOLS,
    "open_cfw_freertos_queue_generic_create",
    "open_cfw_freertos_queue_get_disinherit_priority_after_timeout",
    "open_cfw_freertos_queue_give_from_isr",
    "open_cfw_freertos_queue_initialise_new",
    "open_cfw_freertos_queue_semaphore_take_upstream_candidate",
    "open_cfw_freertos_task_remove_from_event_list",
})
FREERTOS_PROVIDER_ARTIFACT = {
    "size": 6_404,
    "sha256": "926b0597a2d78ea441151b2c21cfc813be29bb246606b2a6b0c5d84e5b175608",
}
FREERTOS_PROVIDER_INPUTS = {
    "adapter": ("third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_freertos_queue_provider.c", 2_916, "78ff7889b1880028964f600901d4c51d844b20843acf5c3f821181caee280e88", "MIT"),
    "adapter_header": ("third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_freertos_queue_provider.h", 1_551, "4790b18460b1b039397804ff22353d614be8ab28e23a09e8dc4b77155683c403", "MIT"),
    "queue_create": ("components/apollo_main/core_overlay/runtime_freertos_queue_create.c", 11_038, "c830936bda7ad816b0ec6aa560630c2665df0a7e3a6e142ec455b5fdf316c4f3", "MIT"),
    "queue_give": ("components/shared/freertos/runtime_freertos_queue_next_closure.c", 7_277, "b13a24bf4538016109194500c9ff7d9bfe5feac0b9f2c9708b390b028aad6f61", "MIT"),
    "queue_give_header": ("components/shared/freertos/runtime_freertos_queue_next_closure.h", 14_564, "84592af1b7beed6201f927d59e18fcf52a4edaf2b58360c96efce276770a5239", "MIT"),
    "semaphore_take": ("components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.c", 5_867, "7bc1adb794188c36fe0693ef4dcf0e45b83cb32ba523142ecb72e703d65979e2", "MIT"),
    "semaphore_take_header": ("components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.h", 10_052, "e570c374e46115987810cd958773292bc80a8ef98b5cb9503a51327ef15328fd", "MIT"),
    "disinherit": ("components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c", 2_620, "37a4ea5a258befb3b607bf5b0c3e6f28b60ed11279b98e13910e0a125519db3a", "MIT"),
    "disinherit_header": ("components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.h", 4_456, "cd97393461faefa962b91b286977226e1e7c3f1e3dc5a5167c415d5e33c5bd1f", "MIT"),
}
FREERTOS_PUBLIC_ABI_INPUTS = {
    "abi_probe": ("tests/fixtures/lvgl_ambiq_freertos_queue_provider_abi.c", 835, "a63328221cc42af3d9e17358d57f21df6a3d7c7b7cdc1fa2757e51152745c55f", "MIT"),
    "queue_source": ("third_party/freertos-kernel/queue.c", 125_614, "5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894", "MIT"),
    "queue_header": ("third_party/freertos-kernel/include/queue.h", 65_746, "a3763e24a5a3a38413996fc8392efd6add1d1ee3ef507fba22daf75682241feb", "MIT"),
    "kernel_header": ("third_party/freertos-kernel/include/FreeRTOS.h", 51_577, "03e9c94aba57e3cf7f4f73bc2d3eb4a96ae38f3425eedb5450622ca286475a0b", "MIT"),
    "port_header": ("third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure/portmacrocommon.h", 12_636, "c184e6b1727732bbdd0d4dd33b9af4ea25d13040620666123941fff464bffc99", "MIT"),
    "compile_config": ("components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/FreeRTOSConfig.h", 5_184, "537e12cd879b06d7748f9b0e177f6ad0e17cd176405945771580e6d9c8312889", "MIT"),
    "compile_port": ("components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/portmacro.h", 910, "6e1ac1013191a6bd3e4924656a03a1515a1d5f06df83b8fbb9073a489961e675", "MIT"),
    "license": ("third_party/freertos-kernel/LICENSE.md", 1_036, "508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1", "MIT"),
}
FREERTOS_ABI_PROBE_ARTIFACT = {
    "size": 912,
    "sha256": "6e8878ec3fd45b9be8f409c13497953819f01dce665fb28bb3e5ae37cfa3622f",
}
FREERTOS_FIXED_IMPORTS = {
    "0x005FA0A5": "stock configASSERT/interrupt-mask entry",
    "0x00441517": "stock queue reset entry",
    "0x00456111": "stock heap allocation entry",
    "0x005FA0BB": "stock ISR-mask clear entry",
    "0x00454F11": "stock task-count entry",
    "0x00455877": "stock next-unblock-time reset entry",
    "0x20074A20": "current-TCB pointer",
    "0x20074A38": "top-ready-priority word",
    "0x20074A44": "yield-pending word",
    "0x20074A58": "scheduler-suspended word",
    "0x2006A49C": "ready-list array",
    "0x20073D24": "pending-ready list",
    "0x004558A5": "stock scheduler-state entry",
    "0x004420D1": "stock task critical-enter entry",
    "0x004420E9": "stock task critical-exit entry",
    "0x00455371": "stock task event-list removal entry",
    "0x004420BD": "stock within-API yield entry",
    "0x00455557": "stock timeout-state entry",
    "0x00454D7D": "stock scheduler-suspend entry",
    "0x00455567": "stock timeout-check entry",
    "0x00441FF5": "stock queue-empty predicate entry",
    "0x00455283": "stock event-list placement entry",
    "0x00441F89": "stock queue-unlock entry",
    "0x00454DCD": "stock scheduler-resume entry",
    "0x00455AE1": "stock mutex-held increment entry",
    "0x004558CD": "stock priority-inherit entry",
    "0x00455A1D": "stock timeout priority-disinherit entry",
}
LVGL_CORE_PROVIDER_SYMBOLS = frozenset({
    "lv_area_get_height", "lv_area_get_width", "lv_area_increase",
    "lv_area_intersect", "lv_area_is_in", "lv_area_move", "lv_area_set",
    "lv_area_set_height", "lv_area_set_width", "lv_color_format_get_bpp",
    "lv_event_get_code", "lv_event_get_param", "lv_matrix_transform_point",
    "lv_matrix_translate",
})
LVGL_CORE_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_core_provider.c",
        9_171, "26cc6cfe55a1418f1b59c8d516ba416b5ac27472e218c7a44f6abaa8af53b114", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_core_provider.h",
        725, "66fdb6d2aef3422797ddbb3003750da17854607a4f2b9706349a4dfa59361071", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_core_provider_abi.c", 1_207,
        "99dc3abb258b5052a666dfebb7e6bbfb37d05f4464e8413884ce4bb56b24fc9c", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_core_provider_host.c", 3_889,
        "a89e51a31a6fa2a464f4935cbbd57bb0c67fd35a859b33f991d291091ae11f75", "MIT",
    ),
}
LVGL_CORE_PROVIDER_ARTIFACT = {
    "size": 7_452,
    "sha256": "9342103b5ae256c72221216d754d21020a92218fbd3024d7e17303ed6ef7111a",
}
LVGL_CORE_ABI_PROBE_ARTIFACT = {
    "size": 896,
    "sha256": "f194076301eaed4ecabf74b3d4df75e227f443c1b33d945ee9b545cdb66d71e8",
}
LVGL_CORE_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": {
        "path": "third_party/lvgl/upstream/trees.json",
        "size": 149_312,
        "sha256": "9aa5b7adccc1e74492a02858859ae9abf4f8b05468adeb45ae3e9dde9df80a17",
    },
    "commit_record": {
        "path": "third_party/lvgl/upstream/344c7c318047b7348e1be8572a9fd4260c251cfa.commit.json",
        "size": 1_634,
        "sha256": "acb765f0389ebfe50ff7ff1f834a31d8088e118dd176dac0362c3d97feea797a",
    },
    "source_blobs": {
        "src/draw/lv_draw_vector.c": "a33a6da02d06af20da5a523b0f15310767363bd3",
        "src/misc/lv_area.c": "34743e8e540c5a8e8fd7607b9015cca50c6e5010",
        "src/misc/lv_color.c": "1096e3b9b6923077d195c1478d5121d46d75c7c0",
        "src/misc/lv_event.c": "8cf7670d51035ece54a5fca9cea6902a73b260b2",
        "src/misc/lv_matrix.c": "29ad09d09cf3befc0b1ccf07561d5a282bd47e11",
    },
    "license": "MIT",
}
LVGL_STATELESS_PROVIDER_SYMBOLS = frozenset({
    "lv_array_at", "lv_array_init_from_buf", "lv_draw_buf_flush_cache",
    "lv_draw_buf_invalidate_cache", "lv_draw_image_dsc_init",
    "lv_font_get_glyph_bitmap", "lv_freetype_is_outline_font",
    "lv_freetype_outline_get_scale", "lv_image_buf_get_transformed_area",
    "lv_memcpy", "lv_memset",
})
LVGL_STATELESS_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_stateless_provider.c",
        9_168, "9f5964de744fcf185799400396979c312cf6e48d4a384373df21961da29f2b5b", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_stateless_provider.h",
        433, "e01f27c9d3dbee24d5c609eb2bcc96b05fd5b940697d1cbdfeb15bc9840a6f7d", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_stateless_provider_abi.c", 1_643,
        "8e1bc22f5cb8497ec9beb28ce87191cc3df95a543cd1c70a0d7ad7f7c578545c", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_stateless_provider_host.c", 6_205,
        "18b4e6da44b67a75219f73f93adbe9a4c500ed03e653544298051903c07eac4c", "MIT",
    ),
}
LVGL_STATELESS_PROVIDER_ARTIFACT = {
    "size": 6_692,
    "sha256": "bcebd4a63cc1366be7ab0006fdab5f31e6645a3583c4aa9a0d72d9ea9ce932a4",
}
LVGL_STATELESS_SOURCE_ARTIFACT = {
    "size": 5_412,
    "sha256": "6b1b93bad33f4710a7ec8987765b43d0fc90e0786801009eca36e7325fa5da73",
}
LVGL_STATELESS_ABI_PROBE_ARTIFACT = {
    "size": 908,
    "sha256": "3e99b5d4ca068929d9e7e8dcae18e326da666b04c77b24589462c760b02f76b1",
}
LVGL_STATELESS_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_blobs": {
        "src/draw/lv_draw_buf.c": "58562a86e55ca5897c3b79b3a486d3f7107aeea0",
        "src/draw/lv_draw_image.c": "ee29d6b7a0b468bae8ce8913d090b22ef35a17b3",
        "src/font/lv_font.c": "a509621cc02be9022f8e947e491e814daab5a29d",
        "src/libs/freetype/lv_freetype_outline.c": "f7d5edbd0ddd40e3ed6a62a66916b10c72974ac7",
        "src/misc/lv_area.c": "34743e8e540c5a8e8fd7607b9015cca50c6e5010",
        "src/misc/lv_array.c": "4f7b97a348c2bd8c210546db5e45b2c309d7ec05",
        "src/misc/lv_math.c": "a6d51a0555d2e33eb69ca7a5c182fc83a26cac0b",
        "src/stdlib/builtin/lv_string_builtin.c": "9c28592a0dfcd1dd5712630456a450f9b61ad1b4",
    },
    "license": "MIT",
}
TARGET_RUNTIME_PROVIDER_SYMBOLS = frozenset({
    "__aeabi_d2lz", "__aeabi_f2ulz", "__aeabi_memcpy4", "memcpy", "memset",
})
TARGET_RUNTIME_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_target_runtime_provider.c",
        2_943, "e19c668ee6eee8d7814104e4d383b901462a1c56e2aeb1f4d4851c8361117994", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_target_runtime_provider.h",
        724, "93a709db1ebb9151d6001e7f3272728a3ab4c96c0f56ce54291bd0f9fb99084e", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_target_runtime_provider_abi.c", 1_167,
        "61de03292ce687d733f819c0254cb367c1e5d3ee9f3b1099418045680b054071", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_target_runtime_provider_host.c", 3_978,
        "5ac6baf402fc4f1739443e18eae3d94e6bf864698c7351d9ceb6167dd7dfaff2", "MIT",
    ),
    "reviewed_scalar_runtime": (
        "research/candidates/target_runtime/runtime_target_scalar_candidate.c", 12_567,
        "aad6d15e8b64fe9f8fb9ae4611bb8663c1fa6a67bdc75c3e3cbc853a7b22093b", "MIT",
    ),
}
TARGET_RUNTIME_PROVIDER_ARTIFACT = {
    "size": 2_736,
    "sha256": "c009f816e4d59547783e88272d77bf9fccaf765f5d66d6339fc3296ca4256bf7",
}
TARGET_RUNTIME_SOURCE_ARTIFACT = {
    "size": 2_308,
    "sha256": "2a43b8130fe85d3e2b27e25efa386ac92f466fb83de85c6f6c083b9643a92a88",
}
TARGET_RUNTIME_ABI_PROBE_ARTIFACT = {
    "size": 1_648,
    "sha256": "918bd5ffff80d2240c8924c7b299f80a286d1c13002a656a5a9acb670c805c4b",
}
TARGET_RUNTIME_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/llvm/llvm-project.git",
    "tag": "llvmorg-20.1.8",
    "commit": "87f0227cb60147a26a1eeb4fb06e3b505e9c7261",
    "license": "Apache-2.0 WITH LLVM-exception",
    "algorithmic_sources": {
        "compiler-rt/lib/builtins/fixdfdi.c": {
            "size": 1_343,
            "git_blob_sha1": "a48facb68598a5ce0eb3c80e027cf7f3c12757b2",
            "sha256": "5542e35a576e96c17e5c9731ffa24f72cedc7369d18079d8c29c5df6702feb94",
        },
        "compiler-rt/lib/builtins/fixunssfdi.c": {
            "size": 1_430,
            "git_blob_sha1": "e8f600df97661a0476be2f111125db60841cfb70",
            "sha256": "19ca6247d9d5238809d07d74fe6645e585479b4c0229655afc0782e35da3a1cd",
        },
        "compiler-rt/lib/builtins/fp_fixint_impl.inc": {
            "size": 1_582,
            "git_blob_sha1": "2f2f77ce781ae278fee43151e1b9e4733817e6b4",
            "sha256": "9f783582b31c028721a14561f2c5741b5bb19befa557a4575e1436381f966f4e",
        },
        "compiler-rt/lib/builtins/fp_fixuint_impl.inc": {
            "size": 1_453,
            "git_blob_sha1": "cb2bf54ffaf5b194a4d5db39de9df7e07a0d5e45",
            "sha256": "fc0d0b1b6fd1b3ec61ed3cd96e634de9f380eb76b7161fea91ddbddece71ac09",
        },
    },
    "qualification": (
        "algorithmic provenance only; the local MIT implementation is independently bounded "
        "and does not claim textual identity with compiler-rt"
    ),
}
MATH_PROVIDER_SYMBOLS = frozenset({"acosf", "atan2f", "atanf", "fmod", "fmodf"})
MATH_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_math_provider.c",
        1_269, "6f1050d9befed1b262458a349a74458cd80784de22094e62d9cd2d7743ddcae5", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_math_provider.h",
        355, "da0a4d14df4c858a9f546a733b28af466679102044e31f22fa2c5dd0793bae01", "MIT",
    ),
    "compat_math_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/math.h",
        894, "f05e0046ba3602528014cf9f0a7efb4ee82d31ad9ec6b4b8cda918ae75a2322a", "MIT",
    ),
    "compat_libm_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/libm.h",
        1_757, "2ccf61453946a264e9b7c8d2535f58a25356b2e052e70e5b9c12bbed1d680205", "MIT",
    ),
    "compat_patch": (
        "third_party/lvgl-ambiq-backend/g2-compat/musl-math-failclosed.patch",
        1_758, "4de9dcfec25503530f0451fff8b2b95ed1980b4c4c526a783dad2b2a42ab3ecf", "MIT",
    ),
    "musl_copyright": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/COPYRIGHT.musl",
        6_204, "f9bc4423732350eb0b3f7ed7e91d530298476f8fec0c6c427a1c04ade22655af", "MIT",
    ),
    "acosf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/acosf.c",
        1_567, "b20b3dcb58ce7cc55963945f8cb83efbf064b29d2da3011f2cec5d08459f2aa7", "Sun-permissive",
    ),
    "atan2f": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/atan2f.c",
        2_216, "31a61a0a4c7b00db625b708525f24673a83df868a3e363042c9cc9dcf0aaeec8", "Sun-permissive",
    ),
    "atanf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/atanf.c",
        2_373, "e0533d7b72aabce311a758a1f94fd15e5d4067be73b716cb1f425df5bc9039d6", "Sun-permissive",
    ),
    "fmod": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/fmod.c",
        1_270, "33fb61093e04783081b9e8f8a8a303456b2f919c215cd0c378c1ed0acf41934c", "MIT",
    ),
    "fmodf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/fmodf.c",
        1_106, "eecc1cf499f143181880a33a95f1614be323aca704815a7b57d4969a7cacc2d4", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_math_provider_abi.c",
        1_034, "6de746aa0ec1282992ecaa447202f39766e273d03b487b38d2b68f39562b432c", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_math_provider_host.c",
        1_522, "818bcf090ea54b62053236ae62a4bed05618f056863b2e1a819909119d012a88", "MIT",
    ),
}
MATH_PROVIDER_ARTIFACT = {
    "size": 6_576,
    "sha256": "123f1163b67fa953c3a77aa9ce3da7652fa6aae1001dc206b9f742f75f14a1af",
}
MATH_ABI_PROBE_ARTIFACT = {
    "size": 2_556,
    "sha256": "6cf6b2cde6c8035b10faf35fac4a1e6ef2e9b134d617548a2659a671f5cc222e",
}
MATH_UPSTREAM_EVIDENCE = {
    "repository": "https://git.musl-libc.org/cgit/musl",
    "tag": "v1.2.5",
    "commit": "0784374d561435f7c787a555aeab8ede699ed298",
    "license": "MIT and preserved Sun permissive notices",
    "copyright_git_blob": "c1628e9ac84f927fe791124ec172fb61c760bb9b",
    "source_git_blobs": {
        "src/math/acosf.c": "8ee1a71d0cc2965e08e170be1dc4529d0165f3b4",
        "src/math/atan2f.c": "c634d00fc93195f63d25b59c0ae6e4a0e8e826d2",
        "src/math/atanf.c": "178341b670fa249fa50157d878ac2a66bd7f1843",
        "src/math/fmod.c": "6849722bac50e477b9210f57f0271dcdabd8ae0c",
        "src/math/fmodf.c": "ff58f93365b47a7083678fc4693db293afbb6f46",
    },
    "qualification": (
        "the five source files and COPYRIGHT are byte-exact to the pinned tag; component-local "
        "headers provide only the required musl internal macros; the deterministic patch changes "
        "only fmod/fmodf invalid and signed-zero paths to avoid unavailable binary64 helpers"
    ),
}
MATH_DP_PROVIDER_SYMBOLS = frozenset({"cosf", "sinf", "sqrt", "tanf"})
MATH_DP_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_math_dp_provider.c",
        837, "2ae2cf3c6fda5c33e463f6b30384d197bbb2fcfabd3d3318ff31ac8a776b8aad", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_math_dp_provider.h",
        282, "1f8b71774c315da55479bfe39cda66c94b35b3c4a74a6542eeef9f5408e9ae4e", "MIT",
    ),
    "compat_math_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/math.h",
        894, "f05e0046ba3602528014cf9f0a7efb4ee82d31ad9ec6b4b8cda918ae75a2322a", "MIT",
    ),
    "compat_libm_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/libm.h",
        1_757, "2ccf61453946a264e9b7c8d2535f58a25356b2e052e70e5b9c12bbed1d680205", "MIT",
    ),
    "compat_features_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/features.h",
        282, "fae5cef0c2e11ff04137637de7cfadcde88ada62e14f256f1e8f96b613c3ed44", "MIT",
    ),
    "musl_copyright": MATH_PROVIDER_INPUTS["musl_copyright"],
    "cosf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/cosf.c",
        1_921, "33cf828e8e733da2b72c723b9ff20057b9a4f10df72a3923dadcb626c23d222c", "Sun-permissive",
    ),
    "sinf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/sinf.c",
        1_970, "2583af55446f07da3225186c368a7aae5a0a0a0edab268967f4122b92e222b87", "Sun-permissive",
    ),
    "tanf": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/tanf.c",
        1_781, "38b39aaf03d33341e606b67b3743ee5fa436b7e8338af155994d4b794b366003", "Sun-permissive",
    ),
    "cos_kernel": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__cosdf.c",
        1_102, "0ba872cc7e26b93bb9784d19fee84b263e1fa3543a76ec3c0893aea47453a2a7", "Sun-permissive",
    ),
    "sin_kernel": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__sindf.c",
        1_101, "de7026bcd159b7d06a8cbcc162df722014f3b1a3cc4183116b6b7829eef1d118", "Sun-permissive",
    ),
    "tan_kernel": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__tandf.c",
        1_869, "60455f3cc0ac743f3eaf0017a3a4f0adbab37c0ee30d29397852d22904c40444", "Sun-permissive",
    ),
    "rem_pio2f": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__rem_pio2f.c",
        2_242, "b73a0219ba4a34e39ed904b5008126ff1b12dfa1a4a380941363c8db5088d756", "Sun-permissive",
    ),
    "rem_pio2_large": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__rem_pio2_large.c",
        16_408, "b97f19fb5951c83a0c10506fab35646caefde13bd03100ad2af55ef00af0b9fb", "Sun-permissive",
    ),
    "floor": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/floor.c",
        653, "b9ccb9363719a84be218d60c56717f4fb0234e170c305e36ce21c30e1f42f8e1", "MIT",
    ),
    "scalbn": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/scalbn.c",
        576, "a2e766283ed30c2b30c71e01dbdabef58faf92cc9aa84a01c1ce1069b6625696", "MIT",
    ),
    "sqrt": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/sqrt.c",
        4_558, "688908f94c3edf7a439cb64094034a596a1fbff08445b9158a22874cb52ead4f", "MIT",
    ),
    "sqrt_data": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/sqrt_data.c",
        974, "590aaadff964dcfc36ef9e5302423a779cda4f1608e15dbeee8e43e6e5f1c6fe", "MIT",
    ),
    "sqrt_data_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/sqrt_data.h",
        352, "5fa47a8b8c1afbee4dcd10f71d2f6c433a24f9aa5ce7a90924cd1db236cbc03c", "MIT",
    ),
    "math_invalid": (
        "third_party/lvgl-ambiq-backend/g2-runtime/musl-math/__math_invalid.c",
        82, "b56440ed59fa1e1aaaf6bf8b672c8bb71eaf844457906f7773da1d67d7ef013b", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_math_dp_provider_abi.c",
        829, "ea9b00cf809a9e156c076607cbe5abaeb0e8333bb447e8fccfe72f7d288922ab", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_math_dp_provider_host.c",
        1_197, "b405fec200b941acea1b199adb725626695f8e0890cc1cecab073b674161edfe", "MIT",
    ),
}
MATH_DP_PROVIDER_ARTIFACT = {
    "size": 13_144,
    "sha256": "3b67eea354a8f12f48faed3177b9d170fa7c8191ced9e30803cbe6b31b2e8c8a",
}
MATH_DP_ABI_PROBE_ARTIFACT = {
    "size": 2_240,
    "sha256": "c7122f705fa35d40f468d4bbc9e68c56746fc6da089639e7526a639add3bf354",
}
MATH_DP_UPSTREAM_EVIDENCE = {
    "repository": "https://git.musl-libc.org/cgit/musl",
    "tag": "v1.2.5",
    "commit": "0784374d561435f7c787a555aeab8ede699ed298",
    "license": "MIT and preserved Sun permissive notices",
    "source_git_blobs": {
        "src/math/cosf.c": "23f3e5bf69f29e3177035c0368f8778e2fc50ce1",
        "src/math/sinf.c": "64e39f50177ca1f3330a6dffa687c7f78841b975",
        "src/math/tanf.c": "aba197777d3aeb0dfb5621f92ade9f0e7615223c",
        "src/math/__cosdf.c": "2124989b3299e53893f2fc9267567e2e7738509b",
        "src/math/__sindf.c": "8fec2a3f660c627b9dd575f96601c9530dc9a67e",
        "src/math/__tandf.c": "25047eeee9c098894010a3984372ba63cb698656",
        "src/math/__rem_pio2f.c": "e67656431a825480c779fd08ab0735f1a6a63572",
        "src/math/__rem_pio2_large.c": "958f28c2557caf23ce9476771f1787cf071d19de",
        "src/math/floor.c": "14a31cd8c4c549750205369a6fe9e71eec8f71c5",
        "src/math/scalbn.c": "182f561068fda7bc8321dfc7991df8b6d58e1b56",
        "src/math/sqrt.c": "5ba26559621357018857a49e40b5745aaca4cc51",
        "src/math/sqrt_data.c": "61bc22f4309586e220da450aaff948a561071d54",
        "src/math/sqrt_data.h": "260c7f9c292beb48fd7a0985a58a7740d38c0d5e",
        "src/math/__math_invalid.c": "177404900d161e4224c1424ec59f08353269d114",
    },
    "qualification": (
        "four public algorithms and ten hidden reduction/kernel/table helpers are byte-exact "
        "to the pinned tag; component-local headers supply only declarations and visibility"
    ),
}
LVGL_MUTEX_PROVIDER_SYMBOLS = frozenset({
    "lv_mutex_delete", "lv_mutex_init", "lv_mutex_lock", "lv_mutex_unlock",
})
LVGL_MUTEX_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_mutex_provider.c",
        4_488, "10aa48f24ef68f9ffd73f5c838d9169c6519f896b23a005e00908190a5647896", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_mutex_provider.h",
        744, "5a50c317277d8b798671db3512789fade53a56b5728008590b8bfc9a043018b4", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_mutex_provider_abi.c",
        877, "e183f01afb59883043b376109f64785265166f671297f9fe50167f31d05e970e", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_mutex_provider_host.c",
        3_738, "e179c37d66405dc968942a744c158943d3c670ce4b3a3ac54bb0e4000cdc8b28", "MIT",
    ),
    "host_config": (
        "tests/fixtures/lvgl_ambiq_lvgl_mutex_provider_host_config.h",
        1_016, "384b81d968ee4f5730cff3c9e38676219d7f464e9039c87f5552f8e13fcea63c", "MIT",
    ),
    "upstream_lv_freertos": (
        "third_party/lvgl/src/osal/lv_freertos.c", 17_471,
        "75b52375c7ef6ff4d084658337d9e40bf515669bf95d76f417ad6a636a1f6e7d", "MIT",
    ),
    "upstream_lv_freertos_header": (
        "third_party/lvgl/src/osal/lv_freertos.h", 2_562,
        "dd6c80811b28a6e51392252d52e09e61955917c1781d74d8a16d063e78e41a4d", "MIT",
    ),
    "upstream_lv_os_header": (
        "third_party/lvgl/src/osal/lv_os.h", 7_707,
        "8e9c6638f75c29910ba6fd9b61e24afcad666f0c91ec9d771eb8255514009c89", "MIT",
    ),
    "source_owned_queue": (
        "components/apollo_main/core_overlay/runtime_freertos_queue.c", 23_669,
        "d54c7970600fd7719a9e847f431512bcc8e45ed942413621de7e93385f2376e0", "MIT",
    ),
    "source_owned_queue_delete": (
        "components/apollo_main/core_overlay/runtime_freertos_queue_delete.c", 5_851,
        "fa8033f61e418dbfb304dd7443dea340bfff88958df493e276ea92db4491da2b", "MIT",
    ),
    "source_owned_scheduler_port": (
        "research/candidates/freertos_scheduler_port_trio.c", 5_437,
        "8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e", "MIT",
    ),
}
LVGL_MUTEX_PROVIDER_ARTIFACT = {
    "size": 2_168,
    "sha256": "5067d94d102f8f6ce7090534a482657761ddee527f796db2cb330bedb36baf3a",
}
LVGL_MUTEX_SOURCE_ARTIFACT = {
    "size": 1_776,
    "sha256": "e8fc442adba6730f9d00ee07a2b67e57f711831b4f2f92328c1ad620349390a6",
}
LVGL_MUTEX_ABI_PROBE_ARTIFACT = {
    "size": 2_056,
    "sha256": "2067a9388bfeac43fe5ac2594c8bbdd35047b913cf3c5cb28ff442f319736d64",
}
LVGL_MUTEX_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "source_git_blobs": {
        "src/osal/lv_freertos.c": "c1eeccdf0dbd0bfd73021fa14aacc7827f8d379c",
        "src/osal/lv_freertos.h": "a3bafca74e5518795e15ee76b87eae8baffb2e53",
        "src/osal/lv_os.h": "47fd80108dc19c1811d471cdfdd2a1ce31486457",
    },
    "freertos_repository": "https://github.com/FreeRTOS/FreeRTOS-Kernel.git",
    "freertos_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
    "qualification": (
        "the selected four LVGL functions do not depend on LV_USE_FREERTOS_TASK_NOTIFY; "
        "their lazy-init/result semantics and 8-byte mutex layout are copied from the "
        "authenticated LVGL source, while every fixed target callee is already source-owned"
    ),
}
LVGL_MUTEX_FIXED_IMPORTS = {
    "0x004420D1": "source-owned vPortEnterCritical Thumb entry",
    "0x004420E9": "source-owned vPortExitCritical Thumb entry",
    "0x004416D7": "source-owned xQueueCreateMutex Thumb entry",
    "0x00441751": "source-owned xQueueTakeMutexRecursive Thumb entry",
    "0x00441711": "source-owned xQueueGiveMutexRecursive Thumb entry",
    "0x00441EA3": "source-owned vQueueDelete Thumb entry",
}
LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS = frozenset({
    "lv_array_deinit", "lv_array_push_back", "lv_free", "lv_malloc",
    "lv_malloc_zeroed",
})
LVGL_HEAP_ARRAY_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_heap_array_provider.c",
        5_523, "95e506d7a86b3520cf13455de5c7dce1c7a10218462245adc5d055c64f7bb5ee", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_heap_array_provider.h",
        527, "ec8db6b87cf9e225a2097884c330dde31254840b6e145fe3dc89da974c7c5116", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_heap_array_provider_abi.c",
        1_069, "4ecae5f325e2439f4cf2166e00618fdca476b1b16336008bb4971582a7bd68a7", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_heap_array_provider_host.c",
        3_078, "86fa5c7a04df8c1dcb3becd00ff453550e6b1c9b877814646643a017bbf18c42", "MIT",
    ),
    "host_config": (
        "tests/fixtures/lvgl_ambiq_lvgl_heap_array_provider_host_config.h",
        650, "6482bc35b1bd069c5b5afde6025a2fc6ab197bc9ded30846b8a9f3a674a89bee", "MIT",
    ),
    "upstream_lv_mem": (
        "third_party/lvgl/src/stdlib/lv_mem.c", 4_379,
        "00d8226e661600d059aecad01f28fadb2bc469cd7cd87a84c7a069b0b4b35d76", "MIT",
    ),
    "upstream_lv_array": (
        "third_party/lvgl/src/misc/lv_array.c", 5_471,
        "c194246f1038177e437e576fa8cb8007d293566efcdaefebc381230cfe57d5fc", "MIT",
    ),
    "upstream_lv_array_header": (
        "third_party/lvgl/src/misc/lv_array.h", 7_027,
        "81c2fcfe0fb65de1aa73f2ee64ce7a86999339a52a8a953aa5b9f4af1e6a1f72", "MIT",
    ),
    "source_owned_heap_facade": (
        "components/apollo_main/core_overlay/file_runtime.c", 34_100,
        "85b94aed03ce45a21186230bd7f398300f32f3fd07c3387413ccc5150a8d0349", "MIT",
    ),
    "heap_facade_function_map": (
        "tools/manifests/g2-file-runtime-function-map.tsv", 4_664,
        "06cc6de63d0ab9acd28305f5beadcb1b4e78ed4f37d5d0337c2f05655516d6fd", "CC0-1.0",
    ),
}
LVGL_HEAP_ARRAY_SOURCE_ARTIFACT = {
    "size": 2_572,
    "sha256": "bf258e13a8d6e259c39e0acfd8cc02bc18d9f030deedb4009fa3c800c6cdd1f1",
}
LVGL_HEAP_ARRAY_PROVIDER_ARTIFACT = {
    "size": 3_060,
    "sha256": "e37759628d884e20f3c788d7b16e21997a667fddd8a6271e2cdd818a74661458",
}
LVGL_HEAP_ARRAY_ABI_PROBE_ARTIFACT = {
    "size": 2_472,
    "sha256": "028f1e607d6aac51df51f26535be9a42edc60475afa2e71c78deff7c3c81faba",
}
LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/stdlib/lv_mem.c": "41a002d7452d0efbdda5f66ab7a28048c50792bb",
        "src/misc/lv_array.c": "4f7b97a348c2bd8c210546db5e45b2c309d7ec05",
        "src/misc/lv_array.h": "c8a159081d64467d2d9e9a1d27bffbcb5338c05d",
    },
    "license": "MIT",
    "qualification": (
        "valid-input semantics and public layouts follow the authenticated LVGL sources; "
        "the custom allocation core binds to the already source-owned synchronized G2 heap facade"
    ),
}
LVGL_HEAP_ARRAY_FIXED_IMPORTS = {
    "0x00474CD2": "source-owned synchronized allocation facade",
    "0x00474D16": "source-owned synchronized free facade",
    "0x00474D54": "source-owned synchronized reallocation facade",
}
LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS = frozenset({"lv_draw_buf_destroy"})
LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.c",
        823, "aefa6b40c0e8227add7534997f46904114747acf569dc89cbfef74f533fdd2c1", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.h",
        342, "908381bd53cb874cba6275f0398379af35758cda590725d114021f3e5351f3d3", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider_abi.c",
        751, "c0ec2e4254e6b52491ce521d8b162db5afad8b3611cb405481189020ea029def", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider_host.c",
        1_724, "cc806ad632634e12c6ae1de013752c3b9bdb9647935bbd2a3a8e76f9a75d3cc5", "MIT",
    ),
    "upstream_draw_buf": (
        "third_party/lvgl/src/draw/lv_draw_buf.c", 22_801,
        "94ba137be50d8516e17314da33992fb53995ea071d9043fa7174d4e52d629f4e", "MIT",
    ),
    "upstream_draw_buf_header": (
        "third_party/lvgl/src/draw/lv_draw_buf.h", 14_311,
        "45fa9990279ef5aecd1808e78d06681bdae598e8def00932d03360de294cf9b6", "MIT",
    ),
}
LVGL_DRAW_BUF_LIFECYCLE_SOURCE_ARTIFACT = {
    "size": 1_044,
    "sha256": "b3ac827b8cb8dc8de639e1518ec64affced61c36ef24c31609c37cfb1d0bd2c9",
}
LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_ARTIFACT = {
    "size": 1_192,
    "sha256": "4b633e5f8f0b2fe765678d8525317aa4c8df3e10d4c22a5e216baeb6393888ca",
}
LVGL_DRAW_BUF_LIFECYCLE_ABI_PROBE_ARTIFACT = {
    "size": 1_036,
    "sha256": "a65afe066d348288c6cde31b6e7839e7ce2f550ea243e0220b7b4ad2873aab32",
}
LVGL_DRAW_BUF_LIFECYCLE_AGGREGATE_ARTIFACT = {
    "size": 3_584,
    "sha256": "ee9e7d0d5419d12a70e3707b99bac1b6bc4ce79c536aa811d3a027ea7c303823",
}
LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/draw/lv_draw_buf.c": "58562a86e55ca5897c3b79b3a486d3f7107aeea0",
        "src/draw/lv_draw_buf.h": "c36e0a612f7fb46f69f5a7a4ae97000dd76a3837",
    },
    "license": "MIT",
    "qualification": (
        "descriptor-owned free-callback and allocation-flag behavior follows the authenticated "
        "LVGL source; the public descriptor release binds to the admitted local lv_free provider"
    ),
}
LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS = frozenset({"lv_global"})
LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_global_storage_provider.c",
        1_267, "58f2c8c8bc2cc98f95fdb7bcc57472fb463d487b3105139ec694044fa2246aef", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_global_storage_provider.h",
        363, "c9fd130d9c368e9910b1cb817ed197281977cb093e7f8672bcc8d6bb68996877", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_global_storage_provider_abi.c",
        615, "90125093cf8556a6039c233a201987ff9579ca650ad8f2b0c1b719e3bc729417", "MIT",
    ),
    "placement_linker_script": (
        "tests/fixtures/lvgl_ambiq_lvgl_global_storage_provider.ld",
        330, "ef97f8b5bdbbbe991f0eedfaa3b8891c5d32f51a80307c5fd8d286b50f1c969d", "MIT",
    ),
    "upstream_lv_init": (
        "third_party/lvgl/src/lv_init.c", 10_851,
        "746f095ba61943a7852f7ceee3a7dd2665ec010a392484f2837e25ead7ab147c", "MIT",
    ),
    "upstream_lv_global_header": (
        "third_party/lvgl/src/core/lv_global.h", 6_197,
        "cfbf0696f3f62a4ed3cfe2f16a94fda107e321ca3ec33491f64d4d54dda80921", "MIT",
    ),
}
LVGL_GLOBAL_STORAGE_SOURCE_ARTIFACT = {
    "size": 716,
    "sha256": "11ce9df99cecff701ba5ba4d8b8f3e17f6db562ac56f0c2b3a40378187c6dca3",
}
LVGL_GLOBAL_STORAGE_PROVIDER_ARTIFACT = {
    "size": 796,
    "sha256": "a11c7c766758ae759bd4f0fc198246d3eab4425cb1a9b57b5d12905a6687966a",
}
LVGL_GLOBAL_STORAGE_ABI_PROBE_ARTIFACT = {
    "size": 1_036,
    "sha256": "1a7890f722106fa2b0a39e8a3fbe909965f6f06fb1858cabe7bac8b001f3f211",
}
LVGL_GLOBAL_STORAGE_PLACEMENT_ARTIFACT = {
    "size": 63_396,
    "sha256": "7165c79720cca1c7f333ac4eeb9d1e68ce223888ebb18722b15e7be200d0ef40",
}
LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/lv_init.c": "e0c58a2d65c835f5ea93f946b030d2c58a012dd1",
        "src/core/lv_global.h": "4515c01c9b80779a7d61701e28b4fb3554a92ba9",
    },
    "license": "MIT",
    "qualification": (
        "the authenticated default-global object definition, recovered 0x1EC layout, and stock "
        "0x2006F548 base are exact; initializer order, handler state, collision, and production "
        "linker ownership remain unqualified"
    ),
}
LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS = frozenset({"lv_freetype_outline_add_event"})
LVGL_FREETYPE_EVENT_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_freetype_event_provider.c",
        987, "adf49dc7d0b8ebbce9e0b24790f4656fc188745702a3ab5b8c981e99d834f01e", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_freetype_event_provider.h",
        381, "65aa21dda2e7e67230f9f5909b825835ce29490423903e827e1b6d8ec87dacc6", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_freetype_event_provider_abi.c",
        277, "9dad6ecfbcc81ca013f9b97a73d2d5469641a5e19799c5ac03b1789adc684486", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_freetype_event_provider_host.c",
        1_147, "42f1e9c8a39ea14df2aafb85384eafa03dec462c4721651a55e61ffd6cded49a", "MIT",
    ),
    "host_config": (
        "tests/fixtures/lvgl_ambiq_lvgl_freetype_event_provider_host_config.h",
        322, "646ff7aa1411939bd7f6156e57d40f7dcafd8b4c4e0f3be46c0ab0456f54fa00", "MIT",
    ),
    "upstream_outline": (
        "third_party/lvgl/src/libs/freetype/lv_freetype_outline.c", 14_465,
        "3f5bf86d89f8d68bfb5d9d157190a446f68b92f284f4d8a5089361c1aee4e07b", "MIT",
    ),
    "upstream_context": (
        "third_party/lvgl/src/libs/freetype/lv_freetype.c", 12_606,
        "064f2d1ac54aefcd71d2d1a723b38496c55be97cb2f3df9389fb455e6f4956a9", "MIT",
    ),
    "upstream_public_header": (
        "third_party/lvgl/src/libs/freetype/lv_freetype.h", 3_413,
        "41d11cbe7c6321486776bce3d98de76c0a702cf2a650f0fffe94c4a539a71d36", "MIT",
    ),
    "upstream_private_header": (
        "third_party/lvgl/src/libs/freetype/lv_freetype_private.h", 4_202,
        "0545ccc25a496c7cc9c52be1b0c5e09eaf9543e7b34102695b509254cc78c5eb", "MIT",
    ),
}
LVGL_FREETYPE_EVENT_SOURCE_ARTIFACT = {
    "size": 1_028,
    "sha256": "48a7d72f38c54e98ff296df1c1630e9a0f4e8895dea41d7f74caf9934468203a",
}
LVGL_FREETYPE_EVENT_PROVIDER_ARTIFACT = {
    "size": 1_208,
    "sha256": "f4d90b85f22b784d3922cc16b7cb58c5f3df8c1c1b937e2a44332498eb07774e",
}
LVGL_FREETYPE_EVENT_ABI_PROBE_ARTIFACT = {
    "size": 1_040,
    "sha256": "cd6de046286a8765255f6a844a7f845289fd6e6ef33283f3b83439d277e0201e",
}
LVGL_FREETYPE_EVENT_AGGREGATE_ARTIFACT = {
    "size": 1_340,
    "sha256": "1ab0eb432566d8c19d5bcf2e5621fda099d532adc123297014f480465e9ffa5a",
}
LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/libs/freetype/lv_freetype_outline.c": "f7d5edbd0ddd40e3ed6a62a66916b10c72974ac7",
        "src/libs/freetype/lv_freetype.c": "c6edfb80794608bdb5e8b58e007fbe8301927013",
        "src/libs/freetype/lv_freetype.h": "3bade7dbd681086a233d4fb244c43e5afcb4cbb7",
        "src/libs/freetype/lv_freetype_private.h": "f851704564afcb9e2030c7c563d2bd96563481c9",
    },
    "license": "MIT",
    "qualification": (
        "valid-context callback storage and ignored filter/user-data behavior follow authenticated "
        "LVGL sources; null context fails closed and context lifetime/initialization remain unqualified"
    ),
}
LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS = frozenset({
    "lv_draw_buf_create", "lv_draw_buf_reshape",
})
LVGL_DRAW_BUF_SHAPE_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_shape_provider.c",
        3_931, "5ad94d291063a7c84e69f52631eba673fe49dd85fe2330a124d5e46adf949068", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_shape_provider.h",
        529, "84168b01455e0b7fcf2045847aaa7bc44484f13c84adb812dd2ae39056d5db39", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_shape_provider_abi.c",
        504, "ee43fb80fbe45e4eaf2d062ae8fe235e45499070a8d799391bf996907eb01de8", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_shape_provider_host.c",
        4_696, "badd5f09c0bc410196aed928b31b6eeb75487d7ec661db93870eec04f3caa42c", "MIT",
    ),
    "host_config": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_shape_provider_host_config.h",
        347, "1c148513da501fbef92b50ea0e14e0fabc033aa4e7229529e7469747835a736a", "MIT",
    ),
    "upstream_draw_buf": LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS["upstream_draw_buf"],
    "upstream_draw_buf_header": LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS["upstream_draw_buf_header"],
    "upstream_draw_buf_private_header": (
        "third_party/lvgl/src/draw/lv_draw_buf_private.h", 1_016,
        "afb2268e7bb91163b422b8095eab814f308fef438c6f2a817e0a5fc8f74b703b", "MIT",
    ),
    "upstream_global_header": (
        "third_party/lvgl/src/core/lv_global.h", 6_197,
        "cfbf0696f3f62a4ed3cfe2f16a94fda107e321ca3ec33491f64d4d54dda80921", "MIT",
    ),
}
LVGL_DRAW_BUF_SHAPE_SOURCE_ARTIFACT = {
    "size": 1_996,
    "sha256": "368557fddaad7fd1fc4c0da1803a659934725fa3fa0a51ff361ec4d6b154ab69",
}
LVGL_DRAW_BUF_SHAPE_PROVIDER_ARTIFACT = {
    "size": 2_296,
    "sha256": "2cf520c1f7d814e9594f93520b638d15e107128c1882fadabff3342eb5448933",
}
LVGL_DRAW_BUF_SHAPE_ABI_PROBE_ARTIFACT = {
    "size": 1_412,
    "sha256": "eb117a909d01a5efbb549229431835ef54748ff9b8581e6b521beb11518388dc",
}
LVGL_DRAW_BUF_SHAPE_AGGREGATE_ARTIFACT = {
    "size": 4_780,
    "sha256": "286aa21ed029d21e21428beccfa082c8044e2019d7d7403c5f3529b512f6e9c5",
}
LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/draw/lv_draw_buf.c": "58562a86e55ca5897c3b79b3a486d3f7107aeea0",
        "src/draw/lv_draw_buf.h": "c36e0a612f7fb46f69f5a7a4ae97000dd76a3837",
        "src/draw/lv_draw_buf_private.h": "a22640315e37433b77605d4ac8f36e689d3b5e9c",
        "src/core/lv_global.h": "4515c01c9b80779a7d61701e28b4fb3554a92ba9",
    },
    "license": "MIT",
    "qualification": (
        "valid-input creation/reshape and default-handler dispatch follow authenticated LVGL "
        "sources; the retained Ambiq initializer owns callback population, while malformed "
        "callbacks and all representational/size overflow fail closed"
    ),
}
LVGL_FONT_FMT_PROVIDER_SYMBOLS = frozenset({"lv_font_get_bitmap_fmt_txt"})
LVGL_FONT_FMT_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_font_fmt_provider.c",
        9_283, "788440431423a6380954b7f98edac1cc72f151e8335695d56a059c383ef64e54", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_font_fmt_provider.h",
        382, "88a9ffbac1b1a8e2641c7b859e904c77e804b2f2b3df8a84c465459613cb1421", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_font_fmt_provider_abi.c",
        282, "85d8eb723a8e6a2d0fa1b7e787d122a2ae5dbc660d1a69a7edc7686df4b0bb0c", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_font_fmt_provider_host.c",
        6_729, "43651d5265c6dd1771458e493133eb9e50cab116d19440621a4189c245fed36e", "MIT",
    ),
    "upstream_font_source": (
        "third_party/lvgl/src/font/lv_font_fmt_txt.c", 19_756,
        "b8f6a61e03b3d47181b7994a4588f1d8e5fd566c618928306d55cd216e80a949", "MIT",
    ),
    "upstream_font_header": (
        "third_party/lvgl/src/font/lv_font_fmt_txt.h", 7_864,
        "21e5a76c55b3bc438a0f6cfe663a1ba024045948e8a79c64264ffcd907b7ab59", "MIT",
    ),
    "upstream_font_private_header": (
        "third_party/lvgl/src/font/lv_font_fmt_txt_private.h", 921,
        "509384e80e9a679c82cc533b895594e02d1da9461faca3b89a908e1fae7a21ef", "MIT",
    ),
    "upstream_draw_buf_private_header": (
        "third_party/lvgl/src/draw/lv_draw_buf_private.h", 1_016,
        "afb2268e7bb91163b422b8095eab814f308fef438c6f2a817e0a5fc8f74b703b", "MIT",
    ),
}
LVGL_FONT_FMT_SOURCE_ARTIFACT = {
    "size": 4_176,
    "sha256": "000a0c4bc5bd8ca6886b6a821f3cdbbbfd331d67a12b4a3a87e3581aaed6a8a4",
}
LVGL_FONT_FMT_PROVIDER_ARTIFACT = {
    "size": 4_688,
    "sha256": "9d4333cf6277960f46d5ce5e0cb8ef0b49e203861bb275afbcf7e409a789ef66",
}
LVGL_FONT_FMT_ABI_PROBE_ARTIFACT = {
    "size": 1_016,
    "sha256": "adad17c030719f3bc67ab0b525ea303221fb941caeadc0ab87d053588bef195e",
}
LVGL_FONT_FMT_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/font/lv_font_fmt_txt.c": "53a927439f4af90cf5a3d591663f4098f22fea16",
        "src/font/lv_font_fmt_txt.h": "f534b8abe5b4d2b76f5d7b6f4f06ac1229625802",
        "src/font/lv_font_fmt_txt_private.h": "66df402d6b932029a6c2e67a635b207e6643cafc",
        "src/draw/lv_draw_buf_private.h": "a22640315e37433b77605d4ac8f36e689d3b5e9c",
    },
    "license": "MIT",
    "qualification": (
        "plain/aligned and compressed fmt_txt decoding follows authenticated LVGL algorithms; "
        "RLE state is invocation-local and cache flush remains draw-buffer-handler-owned"
    ),
}
LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS = frozenset({"lv_vector_for_each_destroy_tasks"})
LVGL_VECTOR_DESTROY_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_vector_destroy_provider.c",
        1_840, "ec9f85e6d6b175df71971c936d451813de501521460f964e278727d90d149f1c", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_vector_destroy_provider.h",
        197, "ae684c3622e659b743ac408ddefa8d8f0e06d88de5bff51ead168f622a11fc64", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_vector_destroy_provider_abi.c",
        332, "e72478e2d29053b1db5cafde3498a01a32bda29fd4d8a09321c39d8eb7e9fcd1", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_vector_destroy_provider_host.c",
        5_073, "54c750ce609ec2c74afc019963b60f5072a0d427b77a8d260811a8d7ce180c35", "MIT",
    ),
    "upstream_vector_private_header": (
        "third_party/lvgl/src/draw/lv_draw_vector_private.h", 2_303,
        "f3e6ed45887fc0429300030f7f7c980a953d84026dad62ff17df9fb30f2247af", "MIT",
    ),
    "upstream_ll_header": (
        "third_party/lvgl/src/misc/lv_ll.h", 4_203,
        "7a020a8d646c37f5760ec228c49955da3f731865e63bf6af4d83f6080d389d7c", "MIT",
    ),
    "upstream_array_source": (
        "third_party/lvgl/src/misc/lv_array.c", 5_471,
        "c194246f1038177e437e576fa8cb8007d293566efcdaefebc381230cfe57d5fc", "MIT",
    ),
    "upstream_array_header": (
        "third_party/lvgl/src/misc/lv_array.h", 7_027,
        "81c2fcfe0fb65de1aa73f2ee64ce7a86999339a52a8a953aa5b9f4af1e6a1f72", "MIT",
    ),
}
LVGL_VECTOR_DESTROY_SOURCE_ARTIFACT = {
    "size": 1_196,
    "sha256": "f0540a5bde0aa91596c7cada7e83d393375e025b0ac3502e30dd7b2c59699bd1",
}
LVGL_VECTOR_DESTROY_PROVIDER_ARTIFACT = {
    "size": 1_388,
    "sha256": "ed7735e3535a5f1e13760986a598be99b8703335a5acae36279acf4a0a56e72c",
}
LVGL_VECTOR_DESTROY_ABI_PROBE_ARTIFACT = {
    "size": 1_040,
    "sha256": "3245185d32527a143391078e0b9a583a92d8a8378332bf1e01fa0fe538bf7c1f",
}
LVGL_VECTOR_DESTROY_AGGREGATE_ARTIFACT = {
    "size": 3_744,
    "sha256": "acb2421d3af2d4b6a3ba4f45169c50a2553d17d2cbc81459f6f7909998bed27a",
}
LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/draw/lv_draw_vector.c": "a33a6da02d06af20da5a523b0f15310767363bd3",
        "src/draw/lv_draw_vector_private.h": "7b2d4e04a8b7cba5392ea73972fb002851e08f96",
        "src/misc/lv_ll.c": "9d86f1daac5182d860debdcb1890b2277c449f1e",
        "src/misc/lv_ll.h": "ee0836ef5e6a51666ffdbcb9787df22faff317af",
        "src/misc/lv_array.c": "4f7b97a348c2bd8c210546db5e45b2c309d7ec05",
        "src/misc/lv_array.h": "c8a159081d64467d2d9e9a1d27bffbcb5338c05d",
    },
    "license": "MIT",
    "qualification": (
        "task-list unlink, callback ordering, vector-path release, dash-array release, and final "
        "list release follow the exact authenticated LVGL implementation"
    ),
}
LVGL_DRAW_UNIT_PROVIDER_SYMBOLS = frozenset({"lv_draw_create_unit"})
LVGL_DRAW_UNIT_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_unit_provider.c",
        1_448, "398cfad6014dbb561f7941269f2246c05ccbdb1fe027bfb24b71e1ee09d7faa0", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_unit_provider.h",
        291, "0bce8fa9a41753ffd4be681ce1562b5b2feb2081ee9fef9739097cbe3ec853d7", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_unit_provider_abi.c",
        183, "12be9367d16c751c3ae9f16670a5a7c874539ca49a7bf0e35d8545126f6d0fbc", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_unit_provider_host.c",
        2_535, "5b1c8b16b863f06db346b2c1740bb0c0f63fdaea237a5f5f6070692ca5a87dda", "MIT",
    ),
    "upstream_draw_source": (
        "third_party/lvgl/src/draw/lv_draw.c", 20_652,
        "3a8779642bbdba4b303864e55fbf2292a7ee31de21f826c8bcd4d4dd153dd817", "MIT",
    ),
    "upstream_draw_header": (
        "third_party/lvgl/src/draw/lv_draw.h", 10_355,
        "96eed74c7547d92627ac4f794396e6acc642d452b94689deb0e481d8ae010359", "MIT",
    ),
    "upstream_draw_private_header": (
        "third_party/lvgl/src/draw/lv_draw_private.h", 6_368,
        "adcbf9990329ae2d1649f3682872852c5bafde9d189cc54d65ba4dd47fb98c99", "MIT",
    ),
    "upstream_global_header": LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS["upstream_lv_global_header"],
    "upstream_mem_header": (
        "third_party/lvgl/src/stdlib/lv_mem.h", 4_272,
        "93adf94a575981657bd15176488e833aa18065acc42604dc72a61379820d58ad", "MIT",
    ),
}
LVGL_DRAW_UNIT_SOURCE_ARTIFACT = {
    "size": 1_108,
    "sha256": "0e4477b7ccd8baaf853d17c4a6725ba4e53075d472cc9a828e5f329b6228cdfd",
}
LVGL_DRAW_UNIT_PROVIDER_ARTIFACT = {
    "size": 1_260,
    "sha256": "67c6f571e7d904438deccaa9de331449a59cecdf9d26ab78c618dbaf96489206",
}
LVGL_DRAW_UNIT_ABI_PROBE_ARTIFACT = {
    "size": 1_028,
    "sha256": "ee45e95ecb3515d8f7b9031c70fb7e33c2947ec010901c21c9144d6d5c9233ee",
}
LVGL_DRAW_UNIT_AGGREGATE_ARTIFACT = {
    "size": 3_768,
    "sha256": "7ca28abfb72e6413ac30afc2ae7bd7b3f55b4e58815f62af8e113ae35c07cb09",
}
LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/draw/lv_draw.c": "b24dda671bf57cecc80e0f30ab8df00b29d2fdf4",
        "src/draw/lv_draw.h": "b35cb52f8298d591d56ce50a03fb21c64f7e7f50",
        "src/draw/lv_draw_private.h": "057d4dd08a7d61417ecea732e4ff3401419d3af9",
        "src/core/lv_global.h": "4515c01c9b80779a7d61701e28b4fb3554a92ba9",
        "src/stdlib/lv_mem.h": "2b9e2defb6b1389d15e76c9842ecd5e339ea4bfb",
    },
    "license": "MIT",
    "qualification": (
        "valid extents preserve authenticated zeroed allocation, head insertion, count, and "
        "one-based index behavior; invalid extents, allocation failure, and unrepresentable IDs "
        "fail before global-list mutation"
    ),
}
LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS = frozenset({"lv_draw_dispatch_request"})
LVGL_DRAW_DISPATCH_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_dispatch_provider.c",
        1_019, "d2e89179ea1a9f581e3a5dce5b5966f5592f731f52cbf5da5c19d4e74b411e8d", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_dispatch_provider.h",
        287, "a2ca7d5b44fa5a13b785a01749bb05cc9a4afc5603fc4a2a21edbde5c7b1db00", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_dispatch_provider_abi.c",
        177, "bee01dfdcec32990f844b1db09ed6106bcb33298db4681e592d2e80a2880c7a8", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_draw_dispatch_provider_host.c",
        818, "f7172ba7080f2d92ddf55d27fc48f5c4cd49569b78c66365eec401d0c092d623", "MIT",
    ),
    "upstream_draw_source": LVGL_DRAW_UNIT_PROVIDER_INPUTS["upstream_draw_source"],
    "upstream_draw_header": LVGL_DRAW_UNIT_PROVIDER_INPUTS["upstream_draw_header"],
    "upstream_draw_private_header": LVGL_DRAW_UNIT_PROVIDER_INPUTS["upstream_draw_private_header"],
    "upstream_global_header": LVGL_DRAW_UNIT_PROVIDER_INPUTS["upstream_global_header"],
    "upstream_os_header": (
        "third_party/lvgl/src/osal/lv_os.h", 7_707,
        "8e9c6638f75c29910ba6fd9b61e24afcad666f0c91ec9d771eb8255514009c89", "MIT",
    ),
}
LVGL_DRAW_DISPATCH_SOURCE_ARTIFACT = {
    "size": 1_084,
    "sha256": "3521e40f536ed4c3e39ebbabc8396c6052272f5ebed0907ad617cf1256015766",
}
LVGL_DRAW_DISPATCH_PROVIDER_ARTIFACT = {
    "size": 1_248,
    "sha256": "5add8d9b27247a4d2e059cbf5783f6f9961de975adb4509e594641fef235ee62",
}
LVGL_DRAW_DISPATCH_ABI_PROBE_ARTIFACT = {
    "size": 1_048,
    "sha256": "f4172c6054d14694ae3aef4cc92905c9084a662bc20d2f1dc411376233e8cbdc",
}
LVGL_DRAW_DISPATCH_AGGREGATE_ARTIFACT = {
    "size": 1_380,
    "sha256": "ec5f9f6e2f0e97781e0b8f29065b9a93134126451a71bcd64b20f611ced21990",
}
LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/draw/lv_draw.c": "b24dda671bf57cecc80e0f30ab8df00b29d2fdf4",
        "src/draw/lv_draw.h": "b35cb52f8298d591d56ce50a03fb21c64f7e7f50",
        "src/draw/lv_draw_private.h": "057d4dd08a7d61417ecea732e4ff3401419d3af9",
        "src/core/lv_global.h": "4515c01c9b80779a7d61701e28b4fb3554a92ba9",
        "src/osal/lv_os.h": "47fd80108dc19c1811d471cdfdd2a1ce31486457",
    },
    "license": "MIT",
    "qualification": (
        "the recovered FreeRTOS branch calls lv_thread_sync_signal twice on the exact default "
        "draw synchronization object and deliberately ignores both results"
    ),
}
LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS = frozenset({"lv_thread_sync_signal"})
LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS = {
    "provider": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_thread_sync_signal_provider.c",
        3_018, "c3243b85717b42fa610ce9d62ca9212e6d9dbb5ee58b347d4ec9773aa0d19cf8", "MIT",
    ),
    "provider_header": (
        "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_thread_sync_signal_provider.h",
        585, "f45cf159a935ffd71e980e1de1ceb9d5845ad7bb954dfa4aa8e773b8915e38b4", "MIT",
    ),
    "abi_probe": (
        "tests/fixtures/lvgl_ambiq_lvgl_thread_sync_signal_provider_abi.c",
        871, "fe5d9fe0ad39ccd02ff576ae9378fa518e04a54da0cd2e5dd38a7c257a5913bf", "MIT",
    ),
    "hostile_host_fixture": (
        "tests/fixtures/lvgl_ambiq_lvgl_thread_sync_signal_provider_host.c",
        3_191, "6598a84dfea87bde5449a9a1c6259a26c84bf119e7bf3804e1e39900b5237205", "MIT",
    ),
    "host_config": (
        "tests/fixtures/lvgl_ambiq_lvgl_thread_sync_signal_provider_host_config.h",
        663, "8a873ee14edc662fa4b7e12dc059e255f7c01830e5eec709eb0d41fe7dbd8f54", "MIT",
    ),
    "upstream_lv_freertos": LVGL_MUTEX_PROVIDER_INPUTS["upstream_lv_freertos"],
    "upstream_lv_freertos_header": LVGL_MUTEX_PROVIDER_INPUTS["upstream_lv_freertos_header"],
    "upstream_lv_os_header": LVGL_MUTEX_PROVIDER_INPUTS["upstream_lv_os_header"],
    "upstream_lv_conf_internal": (
        "third_party/lvgl/src/lv_conf_internal.h", 138_515,
        "3a6f7bbff3d8d57f1df2b060fdd3a126c9da6770fce8eee3dee545f0a22aa432", "MIT",
    ),
    "recovered_lv_conf": (
        "third_party/lvgl/g2-config/lv_conf_recovered.h", 1_125,
        "2876e2abb3821103d0f8dd7dda71e2b1cea70ab194ffe5c4955a194798d86b5b", "MIT",
    ),
    "source_owned_task_notify": (
        "components/shared/freertos/runtime_freertos_task_notify.c", 8_632,
        "e33a4a76b2f018fd191d10d1a9a3f1c1c777031e2a41c7b3a6b459d5cb07e2ab", "MIT",
    ),
    "source_owned_scheduler_port": LVGL_MUTEX_PROVIDER_INPUTS["source_owned_scheduler_port"],
}
LVGL_THREAD_SYNC_SIGNAL_SOURCE_ARTIFACT = {
    "size": 984,
    "sha256": "311b0db237f5051bce92970186641d2771c29e0a1c382387ede9c204af84909d",
}
LVGL_THREAD_SYNC_SIGNAL_PROVIDER_ARTIFACT = {
    "size": 1_140,
    "sha256": "48251997ef18222cd29f8397f049ad5ca3c20b95b789d8917bbb03632db69269",
}
LVGL_THREAD_SYNC_SIGNAL_ABI_PROBE_ARTIFACT = {
    "size": 1_044,
    "sha256": "9895a3e05c4f9405ac0aabf7cb0c09d32946d8a7d13340fccb567d81be513787",
}
LVGL_THREAD_SYNC_SIGNAL_AGGREGATE_ARTIFACT = {
    "size": 1_836,
    "sha256": "4d9ee85c604f6ad3f18a8d547fad3a775f326d2f2cf9c866cc144e1c330bb79b",
}
LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE = {
    "repository": "https://github.com/lvgl/lvgl.git",
    "commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
    "tree": "2c76db856ec570f3ee12565181e5cf52bdd33d78",
    "tree_record": LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"],
    "commit_record": LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"],
    "source_git_blobs": {
        "src/osal/lv_freertos.c": "c1eeccdf0dbd0bfd73021fa14aacc7827f8d379c",
        "src/osal/lv_freertos.h": "a3bafca74e5518795e15ee76b87eae8baffb2e53",
        "src/osal/lv_os.h": "47fd80108dc19c1811d471cdfdd2a1ce31486457",
        "src/lv_conf_internal.h": "a848f30f7d68e5550af4eaf8b4bd7a54c770b4e7",
    },
    "freertos_repository": "https://github.com/FreeRTOS/FreeRTOS-Kernel.git",
    "freertos_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
    "notify_mode": 1,
    "qualification": (
        "the recovered non-Kconfig FreeRTOS configuration selects task notifications; the exact "
        "12-byte condition ABI, lazy initialization, pending-signal and waiter-notify paths are "
        "bound to already source-owned fixed FreeRTOS entries"
    ),
}
LVGL_THREAD_SYNC_SIGNAL_FIXED_IMPORTS = {
    "0x004420D1": "source-owned vPortEnterCritical Thumb entry",
    "0x004420E9": "source-owned vPortExitCritical Thumb entry",
    "0x00455C49": "source-owned xTaskGenericNotify Thumb entry",
}
BUFFER_HELPER_INPUTS = {
    "source": {
        "path": "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.c",
        "size": 3_789,
        "sha256": "a133d0c01b152097cc0d3032b9d52ed163b2671d1b060dcb9cf93a24f2fa6c74",
    },
    "header": {
        "path": "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.h",
        "size": 406,
        "sha256": "07ad0025f8223c4acd1a5ca0ccf51fd4edb08251436f5925985587cadfca2f51",
    },
}
STOCK_BUFFER_HELPERS = {
    "nema_buffer_invalidate": {
        "start": 0x0051411A,
        "end_exclusive": 0x00514148,
        "sha256": "7899709976ddd9c5dff28a3f0d312b79d6bea138a2fdcf85af83b2d1c737e260",
        "hex": "1cb504006068fff796ff007e002801d0012000e00020c0b2002807d020680190e06800900021684660f767ff13bd",
    },
    "nema_buffer_is_within_pool": {
        "start": 0x00514148,
        "end_exclusive": 0x0051416C,
        "sha256": "aa2873c2e579c1e1ff6d0914451629553552d54175ca2f0ee8b64853901eda07",
        "hex": "38b50c001500fff77fff41694269006980188c4202d32c19a04201d2002000e0012032bd",
    },
}

PUBLIC_ARTIFACTS = {
    "nema_archive": {
        "path": "libraries/lib_nema_apollo5x_nemagfx.a",
        "size": 1_809_800,
        "sha256": "109840f6e0bbeb8618a1a853966cdf68cf169620bcc4075ed7a1c86ab0d3286f",
        "git_blob_sha1": "98cfec6fa60c7372777ec0a31cea477c33df1483",
        "license": "LicenseRef-Think-Silicon-NemaSDK-Permissive",
    },
    "gpu_patch_archive": {
        "path": "extensions/gpu_patch.a",
        "size": 51_902,
        "sha256": "31a0e5494cf27a3794212118c152513c16efa0424c51311c70a6f55024b4c95c",
        "git_blob_sha1": "f05c83b4306c9f21efc495325d1214eb72f85e49",
        "license": "BSD-3-Clause",
    },
    "public_zephyr_hal": {
        "path": "port/nema_hal.c",
        "size": 17_527,
        "sha256": "053044dd8db3a84e57ff1c55200fdfefaef3e463361ea8de3fc238c40ed51cac",
        "git_blob_sha1": "3db4d884dce154c3f4107688d8992184e67b88d5",
        "license": "BSD-3-Clause AND LicenseRef-Think-Silicon-NemaSDK-Permissive",
    },
    "nema_license": {
        "path": "headers/LICENSE",
        "size": 1_232,
        "sha256": "bb504491bd00c656c9622c9b9cfe805273c8c626ceb35480b5907983de718fbc",
        "git_blob_sha1": "4ba5d2cc1db909af5c8111414976cc9ce23e215b",
    },
    "gpu_patch_header": {
        "path": "extensions/gpu_patch.h",
        "size": 13_595,
        "sha256": "9aa403a02f5ef6c88f362337b85007cf7af77206d0218fd3b3d0ac408efd45e3",
        "git_blob_sha1": "79e6e220c5798a76e75d4af3789b19fa7ffc3f9a",
    },
}

ALL_AMBIQ_UNITS = (
    "lv_draw_ambiq.c",
    "lv_draw_ambiq_arc.c",
    "lv_draw_ambiq_border.c",
    "lv_draw_ambiq_box_shadow.c",
    "lv_draw_ambiq_buffer.c",
    "lv_draw_ambiq_fill.c",
    "lv_draw_ambiq_img.c",
    "lv_draw_ambiq_letter.c",
    "lv_draw_ambiq_line.c",
    "lv_draw_ambiq_mask_rect.c",
    "lv_draw_ambiq_private.c",
    "lv_draw_ambiq_triangle.c",
    "lv_draw_ambiq_vector.c",
    "lv_draw_ambiq_vector_font.c",
    "lvgl_ambiq_sw_mask_cache_free.c",
)

SELECTED_NEMA_MEMBERS = (
    "nema_blender.o",
    "nema_cmdlist.o",
    "nema_graphics.o",
    "nema_interpolators.o",
    "nema_math.o",
    "nema_matrix3x3.o",
    "nema_programHW.o",
    "nema_ringbuffer.o",
    "nema_vg.o",
    "nema_vg_aabb.o",
    "nema_vg_clipped_path.o",
    "nema_vg_context.o",
    "nema_vg_dashing.o",
    "nema_vg_font.o",
    "nema_vg_paint.o",
    "nema_vg_path.o",
    "nema_vg_shapes.o",
    "nema_vg_tsvg.o",
)

# Exact undefined set after the 15 local objects are relocatably linked with
# the two authenticated public archives.  Static validation below makes any
# accidental omission in this machine ledger a hard failure.
EXPECTED_PUBLIC_RESIDUAL_SYMBOLS = (
    "__aeabi_d2lz", "__aeabi_f2ulz", "__aeabi_memcpy4", "acosf", "atan2f",
    "atanf", "cosf", "fmod", "fmodf", "lv_area_get_height",
    "lv_area_get_width", "lv_area_increase", "lv_area_intersect", "lv_area_is_in",
    "lv_area_move", "lv_area_set", "lv_area_set_height", "lv_area_set_width",
    "lv_array_at", "lv_array_deinit", "lv_array_init_from_buf", "lv_array_push_back",
    "lv_color_format_get_bpp", "lv_draw_buf_create", "lv_draw_buf_destroy",
    "lv_draw_buf_flush_cache", "lv_draw_buf_invalidate_cache", "lv_draw_buf_reshape",
    "lv_draw_create_unit", "lv_draw_dispatch_request", "lv_draw_get_available_task",
    "lv_draw_image_dsc_init", "lv_draw_label_iterate_characters",
    "lv_draw_layer_alloc_buf", "lv_event_get_code", "lv_event_get_param",
    "lv_font_get_bitmap_fmt_txt", "lv_font_get_glyph_bitmap", "lv_free",
    "lv_freetype_is_outline_font", "lv_freetype_outline_add_event",
    "lv_freetype_outline_get_scale", "lv_global", "lv_image_buf_get_transformed_area",
    "lv_image_decoder_close", "lv_image_decoder_open", "lv_log_add", "lv_malloc",
    "lv_malloc_zeroed", "lv_matrix_transform_point", "lv_matrix_translate",
    "lv_memcpy", "lv_memset", "lv_mutex_delete", "lv_mutex_init", "lv_mutex_lock",
    "lv_mutex_unlock", "lv_thread_delete", "lv_thread_init", "lv_thread_sync_delete",
    "lv_thread_sync_init", "lv_thread_sync_signal", "lv_thread_sync_wait",
    "lv_vector_for_each_destroy_tasks", "memcpy", "memset", "nema_buffer_create_pool",
    "nema_buffer_destroy", "nema_buffer_flush", "nema_buffer_invalidate",
    "nema_buffer_is_within_pool", "nema_buffer_map", "nema_buffer_unmap",
    "nema_get_last_cl_id", "nema_get_last_submission_id", "nema_host_free",
    "nema_host_malloc", "nema_mutex_lock", "nema_mutex_unlock", "nema_reg_read",
    "nema_reg_write", "nema_sys_init", "nema_wait_irq_brk", "nema_wait_irq_cl",
    "nemagfx_power_control", "sinf", "sqrt", "tanf", "utf8_codepoint_size",
)

EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS = (
    "lv_draw_get_available_task",
    "lv_draw_label_iterate_characters",
    "lv_draw_layer_alloc_buf",
    "lv_image_decoder_close", "lv_image_decoder_open", "lv_log_add",
    "lv_thread_delete", "lv_thread_init", "lv_thread_sync_delete",
    "lv_thread_sync_init", "lv_thread_sync_wait",
)

HAL_SYMBOLS = frozenset(
    {
        "nema_buffer_create_pool", "nema_buffer_destroy", "nema_buffer_flush",
        "nema_buffer_invalidate", "nema_buffer_is_within_pool", "nema_buffer_map",
        "nema_buffer_unmap", "nema_get_last_cl_id", "nema_get_last_submission_id",
        "nema_host_free", "nema_host_malloc", "nema_mutex_lock", "nema_mutex_unlock",
        "nema_reg_read", "nema_reg_write", "nema_sys_init", "nema_wait_irq_brk",
        "nema_wait_irq_cl", "nemagfx_power_control",
    }
)

STOCK_PROVIDER_BYTES = {
    "nema_sys_init": 110,
    "nema_wait_irq_cl": 22,
    "nema_reg_read": 10,
    "nema_reg_write": 10,
    "nema_buffer_create_pool": 86,
    "nema_buffer_destroy": 36,
    "nema_buffer_flush": 48,
    "nema_buffer_invalidate": 46,
    "nema_buffer_is_within_pool": 36,
    "nema_host_malloc": 12,
    "nema_host_free": 12,
    "nema_get_last_cl_id": 6,
    "nema_get_last_submission_id": 6,
    "nemagfx_power_control": 158,
}

ARCHIVE_CONSUMERS = {
    "__aeabi_d2lz": (("nema_graphics.o", 3),),
    "__aeabi_f2ulz": (("nema_interpolators.o", 3),),
    "acosf": (("nema_vg_aabb.o", 14),),
    "atan2f": (("nema_vg.o", 8), ("nema_vg_aabb.o", 2), ("nema_vg_clipped_path.o", 4)),
    "atanf": (("nema_vg_aabb.o", 2),),
    "cosf": (("nema_vg.o", 4), ("nema_vg_aabb.o", 8), ("nema_vg_clipped_path.o", 4)),
    "fmodf": (("nema_vg_aabb.o", 14),),
    "memcpy": (("nema_vg_clipped_path.o", 2),),
    "memset": (("nema_cmdlist.o", 3), ("nema_graphics.o", 2), ("nema_vg.o", 4),
               ("nema_vg_clipped_path.o", 1), ("nema_vg_shapes.o", 2)),
    "nema_buffer_create_pool": (("nema_cmdlist.o", 2), ("nema_vg_context.o", 1),
                                ("nema_vg_font.o", 1), ("nema_vg_paint.o", 1)),
    "nema_buffer_destroy": (("nema_cmdlist.o", 1), ("nema_vg_context.o", 1),
                            ("nema_vg_font.o", 1), ("nema_vg_paint.o", 1)),
    "nema_buffer_flush": (("nema_cmdlist.o", 10), ("nema_ringbuffer.o", 4)),
    "nema_buffer_map": (("nema_cmdlist.o", 2),),
    "nema_buffer_unmap": (("nema_cmdlist.o", 1),),
    "nema_host_free": (("nema_cmdlist.o", 2), ("nema_vg_clipped_path.o", 8),
                       ("nema_vg_font.o", 9), ("nema_vg_paint.o", 2),
                       ("nema_vg_path.o", 1)),
    "nema_host_malloc": (("nema_cmdlist.o", 1), ("nema_vg_clipped_path.o", 4),
                         ("nema_vg_font.o", 4), ("nema_vg_paint.o", 2),
                         ("nema_vg_path.o", 1)),
    "nema_mutex_lock": (("nema_cmdlist.o", 2),),
    "nema_mutex_unlock": (("nema_cmdlist.o", 2),),
    "nema_reg_read": (("nema_cmdlist.o", 1), ("nema_graphics.o", 6),
                      ("nema_programHW.o", 14)),
    "nema_reg_write": (("nema_graphics.o", 6), ("nema_programHW.o", 11),
                       ("nema_ringbuffer.o", 7)),
    "nema_sys_init": (("nema_graphics.o", 1),),
    "nema_wait_irq_brk": (("nema_programHW.o", 2),),
    "nema_wait_irq_cl": (("nema_cmdlist.o", 4),),
    "sinf": (("nema_vg.o", 4), ("nema_vg_aabb.o", 7),
             ("nema_vg_clipped_path.o", 4)),
    "tanf": (("nema_vg.o", 1), ("nema_vg_aabb.o", 1),
             ("nema_vg_clipped_path.o", 1)),
    "utf8_codepoint_size": (("ambiq_nema_extension.o", 1),),
}

EVB_HAL_CONSUMERS = {
    "am_hal_cachectrl_dcache_clean": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "am_hal_pwrctrl_periph_disable": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "am_hal_pwrctrl_periph_enable": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "am_hal_pwrctrl_periph_enabled": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "xQueueGenericCreate": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "xQueueGiveFromISR": (("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),),
    "xQueueSemaphoreTake": (
        ("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_CALL"),
        ("apollo510_evb_nema_hal.o", 1, "R_ARM_THM_JUMP24"),
    ),
}

BUFFER_HELPER_CONSUMERS = {
    "am_hal_cachectrl_dcache_invalidate": (
        ("lvgl_ambiq_nema_buffer_helpers.o", 1, "R_ARM_THM_CALL"),
    ),
}

EVB_EVIDENCE = {
    "scoped_root_hint": "evenrealitiesg2-swiftsdk/openCFW/sdks/Apollo510-EVB",
    "repository_origin": "ssh://git@ssh.github.com:443/kalanihelekunihi/evenrealitiesg2-swiftsdk.git",
    "local_repository_commit": "edbf8d8e324029f4cd9071b490dd125f97e1bf95",
    "source_introducing_commit": "88f3c6c4fe7da2d2c90debbc118984e2bef49071",
    "source": {
        "path": "ThirdParty/ApolloSDK/third_party/ThinkSi/config/apollo510_nemagfx/nema_hal.c",
        "size": 21_402,
        "sha256": "643e5769126db273c638348c9f2aa0d7f0448a75fcc88c968c0e0bdd3a107416",
        "git_blob_sha1": "af266492d4dd1f117f56fd1d8481fcc7206d659f",
    },
    "sys_defs": {
        "path": "ThirdParty/ApolloSDK/third_party/ThinkSi/config/apollo510_nemagfx/nema_sys_defs.h",
        "size": 20_458,
        "sha256": "89878471e6f1294c2e1ea034a94fda130a10b582d9de5be1d036c7e526b518f3",
        "git_blob_sha1": "41aadcf04292d45822739391e6662a1edbc7e0ec",
    },
    "freertos_config": {
        "path": "Application/Source/FreeRTOSConfig.h",
        "size": 8_223,
        "sha256": "f49c73d79f2bb592719c55c832d92ed6a05fcad1aa31ceb4a11f65252d34fc0b",
        "git_blob_sha1": "2aa7d69f3ccf40912334280ce06473809c4c88ac",
    },
    "makefile": {
        "path": "Application/Project/GCC/Makefile",
        "size": 19_528,
        "sha256": "47093df2f35023459aedb6ea038a544668dc2e58f45af5ca3e73b1b98c4945a4",
        "git_blob_sha1": "93b6e69cf8d83513d622a301d1e608bfbb3dc1f7",
    },
}


class AuditError(RuntimeError):
    """Raised when the pinned source, symbol, or link boundary changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def _digest(value: Any) -> str:
    return _sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    if result.returncode != 0:
        raise AuditError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def _load_builder():
    spec = importlib.util.spec_from_file_location("g2_lvgl_ambiq_link_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Ambiq LVGL builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _tool(builder, name: str) -> str:
    try:
        return builder._llvm_tool(name)
    except builder.BuildError as exc:
        raise AuditError(str(exc)) from exc


def _sibling_tool(reference: str, name: str) -> str:
    direct = shutil.which(name)
    if direct is not None:
        return direct
    candidates = (
        Path(reference).with_name(name),
        Path("/opt/homebrew/opt/llvm/bin") / name,
        Path("/usr/local/opt/llvm/bin") / name,
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise AuditError(f"Cortex-M55 object gate requires {name}")


def _symbols(nm: str, obj: Path, *, undefined: bool) -> set[str]:
    options = ["--undefined-only"] if undefined else ["--defined-only", "--extern-only"]
    return {
        line.split()[-1]
        for line in _run([nm, *options, str(obj)]).splitlines()
        if line.strip() and not line.rstrip().endswith(":")
    }


def _relocations(objdump: str, obj: Path, undefined: set[str]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for line in _run([objdump, "-r", str(obj)]).splitlines():
        match = re.match(r"^\s*[0-9a-fA-F]+\s+(R_ARM_\S+)\s+(\S+)", line)
        if match is None or match.group(2) not in undefined:
            continue
        types = result.setdefault(match.group(2), {})
        types[match.group(1)] = types.get(match.group(1), 0) + 1
    return result


def _candidate_inventory() -> list[dict[str, Any]]:
    directory = ROOT / "components/shared/lvgl"
    paths = sorted(
        list(directory.glob("runtime_ambiq_*candidate.[ch]"))
        + list(directory.glob("runtime_nemavg_stroke_caps_candidate.[ch]"))
    )
    rows = []
    for path in paths:
        data = path.read_bytes()
        if b"SPDX-License-Identifier: MIT" not in data[:1024]:
            raise AuditError(f"candidate license marker changed: {path.name}")
        rows.append({
            "path": path.relative_to(ROOT).as_posix(),
            "size": len(data),
            "sha256": _sha256(data),
            "license": "MIT",
            "production_provider": False,
        })
    digest_rows = [{k: row[k] for k in ("path", "size", "sha256")} for row in rows]
    if (
        len(rows) != EXPECTED_CANDIDATE_FILES
        or sum(row["size"] for row in rows) != EXPECTED_CANDIDATE_BYTES
        or _digest(digest_rows) != EXPECTED_CANDIDATE_DIGEST
    ):
        raise AuditError("workspace Nema/GPU candidate inventory changed")
    return rows


def _validate_static_boundary() -> None:
    symbols = list(EXPECTED_PUBLIC_RESIDUAL_SYMBOLS)
    if len(symbols) != 89 or symbols != sorted(set(symbols)):
        raise AuditError("public residual symbol ledger has an omission or duplicate")
    if _digest(symbols) != EXPECTED_PUBLIC_RESIDUAL_DIGEST:
        raise AuditError("public residual symbol ledger identity changed")
    if set(HAL_SYMBOLS) - set(symbols):
        raise AuditError("Apollo510 Nema HAL ledger omits a required symbol")
    if set(ARCHIVE_CONSUMERS) - set(symbols):
        raise AuditError("archive relocation ledger contains a non-residual symbol")
    maximal = list(EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS)
    if len(maximal) != 11 or maximal != sorted(set(maximal)):
        raise AuditError("maximal residual symbol ledger has an omission or duplicate")
    if _digest(maximal) != EXPECTED_MAXIMAL_RESIDUAL_DIGEST:
        raise AuditError("maximal residual symbol ledger identity changed")
    remaining_hal = set(HAL_SYMBOLS) & set(maximal)
    if remaining_hal:
        raise AuditError("maximal Apollo510 Nema HAL boundary changed")
    if (
        set(EVB_HAL_CONSUMERS)
        - set(maximal)
        - set(PLATFORM_PROVIDER_SYMBOLS)
        - set(FREERTOS_PROVIDER_SYMBOLS)
    ):
        raise AuditError("EVB HAL relocation ledger contains a non-residual symbol")
    if set(BUFFER_HELPER_CONSUMERS) - set(maximal) - set(PLATFORM_PROVIDER_SYMBOLS):
        raise AuditError("buffer-helper relocation ledger contains a non-residual symbol")
    if set(LVGL_CORE_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL core provider symbols remain in maximal residual ledger")
    if set(LVGL_STATELESS_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL stateless provider symbols remain in maximal residual ledger")
    if set(TARGET_RUNTIME_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local target runtime provider symbols remain in maximal residual ledger")
    if set(MATH_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local math provider symbols remain in maximal residual ledger")
    if set(MATH_DP_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local FPv5-D16 math provider symbols remain in maximal residual ledger")
    if set(LVGL_MUTEX_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL mutex provider symbols remain in maximal residual ledger")
    if set(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL heap/array provider symbols remain in maximal residual ledger")
    if set(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL draw-buffer lifecycle symbol remains in maximal residual ledger")
    if set(LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL global-storage symbol remains in maximal residual ledger")
    if set(LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL FreeType-event symbol remains in maximal residual ledger")
    if set(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL draw-buffer shape symbols remain in maximal residual ledger")
    if set(LVGL_FONT_FMT_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL font-format symbol remains in maximal residual ledger")
    if set(LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL vector-destroy symbol remains in maximal residual ledger")
    if set(LVGL_DRAW_UNIT_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL draw-unit symbol remains in maximal residual ledger")
    if set(LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL draw-dispatch symbol remains in maximal residual ledger")
    if set(LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS) & set(maximal):
        raise AuditError("local LVGL thread-sync-signal symbol remains in maximal residual ledger")
    gc_roots = list(EXPECTED_BACKEND_GC_ROOTS)
    if (
        len(gc_roots) != 39
        or gc_roots != sorted(set(gc_roots))
        or _digest(gc_roots) != EXPECTED_BACKEND_GC_ROOT_DIGEST
    ):
        raise AuditError("backend section-GC root ledger has an omission or duplicate")


def _compile_local_objects(
    builder, output_dir: Path, clang: str, nm: str, objdump: str,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], list[str]]:
    if _sha256(VECTOR_PATCH.read_bytes()) != VECTOR_PATCH_SHA256:
        raise AuditError("Ambiq vector compatibility patch identity changed")
    output_dir.mkdir(parents=True, exist_ok=True)
    objects_dir = output_dir / "objects"
    objects_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-nema-stage-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        _run(["patch", "-s", "-p1", "-i", str(VECTOR_PATCH)], cwd=lvgl)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = builder._compiler_flags(clang, stage, lvgl, stubs)
        rows: list[dict[str, Any]] = []
        all_defined: set[str] = set()
        all_undefined: set[str] = set()
        consumers: dict[str, list[dict[str, Any]]] = {}
        warnings: list[str] = []
        for unit in ALL_AMBIQ_UNITS:
            source = lvgl / "src/draw/ambiq" / unit
            obj = objects_dir / (source.stem + ".o")
            output = _run([*flags, "-c", str(source), "-o", str(obj)], cwd=stage)
            warnings.extend(line.strip() for line in output.splitlines() if "warning:" in line)
            defined = _symbols(nm, obj, undefined=False)
            undefined = _symbols(nm, obj, undefined=True)
            relocation_map = _relocations(objdump, obj, undefined)
            for symbol in undefined:
                type_counts = relocation_map.get(symbol, {})
                consumers.setdefault(symbol, []).append({
                    "object": obj.name,
                    "relocation_count": sum(type_counts.values()),
                    "relocation_types": dict(sorted(type_counts.items())),
                })
            all_defined.update(defined)
            all_undefined.update(undefined)
            data = obj.read_bytes()
            rows.append({"unit": unit, "size": len(data), "sha256": _sha256(data)})
        if warnings:
            raise AuditError("warning in all-unit Ambiq compile:\n" + "\n".join(warnings))
        aggregate = sorted(all_undefined - all_defined)
        if (
            len(aggregate) != EXPECTED_AGGREGATE_UNRESOLVED["count"]
            or _digest(aggregate) != EXPECTED_AGGREGATE_UNRESOLVED["digest"]
        ):
            raise AuditError("all-unit Ambiq aggregate unresolved set changed")
        direct_nema = sorted(
            symbol for symbol in aggregate
            if symbol.startswith("nema") or symbol.startswith("lv_ambiq_")
        )
        if (
            len(direct_nema) != EXPECTED_DIRECT_NEMA["count"]
            or _digest(direct_nema) != EXPECTED_DIRECT_NEMA["digest"]
        ):
            raise AuditError("all-unit Ambiq direct Nema requirement set changed")
        filtered_consumers = {
            symbol: sorted(consumers.get(symbol, []), key=lambda row: row["object"])
            for symbol in aggregate
        }
        return rows, filtered_consumers, direct_nema


def _compile_buffer_helpers(
    builder, output_dir: Path, clang: str, nm: str, objdump: str,
) -> tuple[Path, dict[str, Any]]:
    authenticated_inputs: dict[str, dict[str, Any]] = {}
    for name, metadata in BUFFER_HELPER_INPUTS.items():
        path = ROOT / metadata["path"]
        data = path.read_bytes()
        if len(data) != metadata["size"] or _sha256(data) != metadata["sha256"]:
            raise AuditError(f"Nema buffer-helper {name} identity changed")
        authenticated_inputs[name] = dict(metadata)

    image = OFFICIAL_IMAGE.read_bytes()
    image_base = 0x00437FE0
    stock_rows: dict[str, dict[str, Any]] = {}
    for name, metadata in STOCK_BUFFER_HELPERS.items():
        start = metadata["start"] - image_base
        end = metadata["end_exclusive"] - image_base
        body = image[start:end]
        if body.hex() != metadata["hex"] or _sha256(body) != metadata["sha256"]:
            raise AuditError(f"authenticated stock Nema helper changed: {name}")
        stock_rows[name] = {
            "start": f"0x{metadata['start']:08X}",
            "end_exclusive": f"0x{metadata['end_exclusive']:08X}",
            "bytes": len(body),
            "sha256": metadata["sha256"],
        }
    descriptor_literals = {
        "assets": int.from_bytes(image[0x00514268 - image_base:0x0051426C - image_base], "little"),
        "render": int.from_bytes(image[0x0051426C - image_base:0x00514270 - image_base], "little"),
        "cpu": int.from_bytes(image[0x00514270 - image_base:0x00514274 - image_base], "little"),
    }
    if descriptor_literals != {
        "assets": 0x20000370, "render": 0x20000354, "cpu": 0x20000338,
    }:
        raise AuditError("authenticated stock Nema heap descriptor literals changed")

    providers = output_dir / "providers"
    providers.mkdir(parents=True, exist_ok=True)
    obj = providers / "lvgl_ambiq_nema_buffer_helpers.o"
    with tempfile.TemporaryDirectory(prefix="opencfw-nema-helper-stage-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = builder._compiler_flags(clang, stage, lvgl, stubs)
        flags.extend([
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu"),
            "-Wall", "-Wextra", "-Werror",
        ])
        output = _run([*flags, "-c", str(BUFFER_HELPER_SOURCE), "-o", str(obj)], cwd=stage)
    if "warning:" in output:
        raise AuditError("warning in Nema buffer-helper target compile:\n" + output)
    defined = _symbols(nm, obj, undefined=False)
    undefined = _symbols(nm, obj, undefined=True)
    expected_defined = {"nema_buffer_invalidate", "nema_buffer_is_within_pool"}
    if defined != expected_defined or undefined != {"am_hal_cachectrl_dcache_invalidate"}:
        raise AuditError("Nema buffer-helper target symbol boundary changed")
    relocations = _relocations(objdump, obj, undefined)
    if relocations != {
        "am_hal_cachectrl_dcache_invalidate": {"R_ARM_THM_CALL": 1},
    }:
        raise AuditError("Nema buffer-helper target relocation boundary changed")
    data = obj.read_bytes()
    if len(data) != 1_436 or _sha256(data) != "ff6dd3f339eebd009310abc3d7fe610b97e1501c1d0a1dcebc53ce22ac60fca9":
        raise AuditError("Nema buffer-helper target object identity changed")
    return obj, {
        "inputs": authenticated_inputs,
        "stock_functions": stock_rows,
        "stock_heap_descriptor_addresses": {
            name: f"0x{address:08X}" for name, address in descriptor_literals.items()
        },
        "artifact": {"path": obj.name, "size": len(data), "sha256": _sha256(data)},
        "defined_symbols": sorted(defined),
        "undefined_symbols": sorted(undefined),
        "relocations": relocations,
        "warning_count": 0,
        "hostile_input_policy": (
            "null, negative-size, out-of-pool, range-wrap, and descriptor-wrap inputs fail closed"
        ),
        "production_overlay_registered": False,
        "hardware_qualified": False,
    }


def _compile_platform_provider(
    output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    objects: list[Path] = []
    parts = output_dir / "providers/apollo-hal-parts"
    parts.mkdir(parents=True, exist_ok=True)
    common_flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-std=gnu11", "-O2",
        "-ffreestanding", "-fshort-enums", "-ffunction-sections", "-fdata-sections",
        "-Wall", "-Wextra", "-Werror", f"-ffile-prefix-map={ROOT}=/openCFW/g2",
    ]
    include_flags = [
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510"),
        "-I", str(ROOT / "third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include"),
        "-I", str(ROOT / "third_party/cmsis-core/CMSIS/Core/Include"),
    ]
    for name, (relative, size, sha256, license_id) in PLATFORM_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"Apollo HAL provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }
        if path.suffix != ".c":
            continue
        obj = parts / (path.stem + ".o")
        output = _run([*common_flags, *include_flags, "-c", str(path), "-o", str(obj)])
        if "warning:" in output:
            raise AuditError(f"warning in Apollo HAL provider compile: {relative}\n{output}")
        objects.append(obj)

    adapter = parts / "lvgl_ambiq_apollo_hal_provider.o"
    adapter_undefined = _symbols(nm, adapter, undefined=True)
    expected_adapter_imports = {
        "open_cfw_cache_dcache_clean", "open_cfw_cache_dcache_invalidate",
        "open_cfw_pwrctrl_periph_disable", "open_cfw_pwrctrl_periph_enable",
        "open_cfw_pwrctrl_periph_enabled",
    }
    if adapter_undefined != expected_adapter_imports:
        raise AuditError("Apollo HAL adapter import boundary changed")
    adapter_relocations = _relocations(objdump, adapter, adapter_undefined)
    if set(adapter_relocations) != expected_adapter_imports or any(
        counts != {"R_ARM_THM_JUMP24": 1} and counts != {"R_ARM_THM_CALL": 1}
        for counts in adapter_relocations.values()
    ):
        raise AuditError("Apollo HAL adapter relocation boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-apollo-hal-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(PLATFORM_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), *[str(obj) for obj in objects]])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    if undefined or defined != PLATFORM_PROVIDER_EXPORTS:
        raise AuditError("Apollo HAL isolated provider symbol/import closure changed")
    for address in PLATFORM_FIXED_IMPORTS:
        token = address.removeprefix("0x")
        if not any(token in path.read_text(encoding="utf-8").upper() for path in (
            ROOT / "components/apollo_main/core_overlay/pwrctrl_periph_enable.c",
            ROOT / "components/apollo_main/core_overlay/pwrctrl_periph_disable.c",
            ROOT / "components/apollo_main/core_overlay/pwrctrl_gpu_mode_select.c",
            ROOT / "components/apollo_main/core_overlay/duration_delay.c",
        )):
            raise AuditError(f"Apollo HAL fixed-address import evidence changed: {address}")
    data = provider.read_bytes()
    if (
        len(data) != PLATFORM_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != PLATFORM_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("Apollo HAL isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "required_exports": sorted(PLATFORM_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "adapter_relocations": adapter_relocations,
        "fixed_address_imports": PLATFORM_FIXED_IMPORTS,
        "fixed_address_import_count": len(PLATFORM_FIXED_IMPORTS),
        "warning_count": 0,
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated source and ELF import closure; fixed G2 calls and MMIO are enumerated, "
            "not routed or hardware-qualified"
        ),
    }


def _compile_freertos_queue_provider(
    output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    public_abi_inputs: dict[str, dict[str, Any]] = {}
    objects: list[Path] = []
    parts = output_dir / "providers/freertos-queue-parts"
    parts.mkdir(parents=True, exist_ok=True)
    common_flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-std=gnu11", "-O2",
        "-ffreestanding", "-fshort-enums", "-ffunction-sections", "-fdata-sections",
        "-Wall", "-Wextra", "-Werror", f"-ffile-prefix-map={ROOT}=/openCFW/g2",
    ]
    include_flags = [
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "components/apollo_main/core_overlay"),
        "-I", str(ROOT / "components/shared/freertos"),
    ]
    for name, (relative, size, sha256, license_id) in FREERTOS_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"FreeRTOS queue provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }
        if path.suffix != ".c":
            continue
        obj = parts / (path.stem + ".o")
        output = _run([*common_flags, *include_flags, "-c", str(path), "-o", str(obj)])
        if "warning:" in output:
            raise AuditError(f"warning in FreeRTOS queue provider compile: {relative}\n{output}")
        objects.append(obj)

    for name, (relative, size, sha256, license_id) in FREERTOS_PUBLIC_ABI_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"FreeRTOS public ABI input identity changed: {relative}")
        public_abi_inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    abi_probe = parts / "lvgl_ambiq_freertos_queue_provider_abi.o"
    abi_output = _run([
        *common_flags,
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors"),
        "-I", str(ROOT / "third_party/freertos-kernel/include"),
        "-I", str(ROOT / "third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure"),
        "-c", str(ROOT / FREERTOS_PUBLIC_ABI_INPUTS["abi_probe"][0]),
        "-o", str(abi_probe),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in FreeRTOS public ABI probe compile:\n{abi_output}")
    abi_data = abi_probe.read_bytes()
    if (
        len(abi_data) != FREERTOS_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != FREERTOS_ABI_PROBE_ARTIFACT["sha256"]
        or _symbols(nm, abi_probe, undefined=True)
        or _symbols(nm, abi_probe, undefined=False)
        != {"open_cfw_lvgl_freertos_queue_provider_abi_probe"}
    ):
        raise AuditError("FreeRTOS public ABI probe artifact boundary changed")

    adapter = parts / "lvgl_ambiq_freertos_queue_provider.o"
    expected_adapter_imports = {
        "open_cfw_freertos_queue_generic_create",
        "open_cfw_freertos_queue_give_from_isr",
        "open_cfw_freertos_queue_semaphore_take_upstream_candidate",
    }
    adapter_undefined = _symbols(nm, adapter, undefined=True)
    if adapter_undefined != expected_adapter_imports:
        raise AuditError("FreeRTOS queue adapter import boundary changed")
    adapter_relocations = _relocations(objdump, adapter, adapter_undefined)
    expected_adapter_relocations = {
        "open_cfw_freertos_queue_generic_create": {"R_ARM_THM_JUMP24": 2},
        "open_cfw_freertos_queue_give_from_isr": {
            "R_ARM_THM_CALL": 1,
            "R_ARM_THM_JUMP24": 1,
        },
        "open_cfw_freertos_queue_semaphore_take_upstream_candidate": {
            "R_ARM_THM_JUMP24": 1,
        },
    }
    if adapter_relocations != expected_adapter_relocations:
        raise AuditError("FreeRTOS queue adapter relocation boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-freertos-queue-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(FREERTOS_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), *[str(obj) for obj in objects]])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    if undefined or defined != FREERTOS_PROVIDER_EXPORTS:
        raise AuditError("FreeRTOS queue isolated provider symbol/import closure changed")

    source_text = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative, _size, _sha256_value, _license in FREERTOS_PROVIDER_INPUTS.values()
    ).upper()
    for address in FREERTOS_FIXED_IMPORTS:
        value = int(address, 16)
        tokens = {f"{value:08X}"}
        if (value & 1) != 0:
            tokens.add(f"{value & ~1:08X}")
        if not any(token in source_text for token in tokens):
            raise AuditError(f"FreeRTOS queue fixed-address evidence changed: {address}")

    data = provider.read_bytes()
    if (
        len(data) != FREERTOS_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != FREERTOS_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("FreeRTOS queue isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": {
            "repository": "https://github.com/FreeRTOS/FreeRTOS-Kernel.git",
            "commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "license": "MIT",
            "inputs": public_abi_inputs,
            "abi_probe_artifact": {
                "path": abi_probe.name,
                "size": len(abi_data),
                "sha256": _sha256(abi_data),
            },
            "target_prototypes_compatible": True,
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "required_exports": sorted(FREERTOS_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "adapter_relocations": adapter_relocations,
        "fixed_address_imports": FREERTOS_FIXED_IMPORTS,
        "fixed_address_import_count": len(FREERTOS_FIXED_IMPORTS),
        "warning_count": 0,
        "hostile_input_policy": (
            "zero-length and overflowing constructors plus null queue operations fail closed"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated source and ELF import closure; fixed G2 scheduler calls/RAM are "
            "enumerated and not newly routed or runtime-qualified"
        ),
    }


def _compile_lvgl_core_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_CORE_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL core provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads((ROOT / LVGL_CORE_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text())
    if upstream.get("root_tree") != LVGL_CORE_UPSTREAM_EVIDENCE["tree"]:
        raise AuditError("LVGL core provider upstream tree identity changed")
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_CORE_UPSTREAM_EVIDENCE["source_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL upstream tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL upstream tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if observed_blobs != LVGL_CORE_UPSTREAM_EVIDENCE["source_blobs"]:
        raise AuditError("LVGL core provider source-blob identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_CORE_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL upstream {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_CORE_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_CORE_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL core provider upstream commit identity changed")

    parts = output_dir / "providers/lvgl-core-parts"
    parts.mkdir(parents=True, exist_ok=True)
    stubs = parts / "stubs"
    builder._write_stubs(stubs)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2", "-I", str(stubs),
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "third_party/lvgl"), "-DLV_CONF_SKIP=1",
        "-DLV_COLOR_DEPTH=8", "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1",
        "-DLV_USE_FLOAT=1", "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_NONE",
        "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
    ]
    source_obj = parts / "lvgl_ambiq_lvgl_core_provider.o"
    output = _run([
        *flags, "-c", str(ROOT / LVGL_CORE_PROVIDER_INPUTS["provider"][0]),
        "-o", str(source_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in LVGL core provider compile:\n{output}")
    source_defined = _symbols(nm, source_obj, undefined=False)
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if source_defined != set(LVGL_CORE_PROVIDER_SYMBOLS) or source_undefined:
        raise AuditError("LVGL core provider source symbol/import closure changed")

    abi_obj = parts / "lvgl_ambiq_lvgl_core_provider_abi.o"
    abi_output = _run([
        *flags, "-c", str(ROOT / LVGL_CORE_PROVIDER_INPUTS["abi_probe"][0]),
        "-o", str(abi_obj),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in LVGL core ABI probe compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    if (
        len(abi_data) != LVGL_CORE_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_CORE_ABI_PROBE_ARTIFACT["sha256"]
        or _symbols(nm, abi_obj, undefined=True)
        or _symbols(nm, abi_obj, undefined=False)
        != {"open_cfw_lvgl_core_provider_abi_probe"}
    ):
        raise AuditError("LVGL core ABI probe artifact boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-core-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(LVGL_CORE_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(LVGL_CORE_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("LVGL core isolated provider ELF closure changed")
    if (
        len(data) != LVGL_CORE_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != LVGL_CORE_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL core isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_CORE_UPSTREAM_EVIDENCE,
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "required_exports": sorted(LVGL_CORE_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "null pointers fail closed; area arithmetic has defined two's-complement wrapping; "
            "invalid color formats return zero; malformed rounded areas are rejected"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated exact-ABI software provider with no allocator, scheduler, MMIO, libc, "
            "libm, or fixed-address imports; complete LVGL core admission remains separate"
        ),
    }


def _compile_lvgl_stateless_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_STATELESS_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL stateless provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_STATELESS_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    if upstream.get("root_tree") != LVGL_STATELESS_UPSTREAM_EVIDENCE["tree"]:
        raise AuditError("LVGL stateless provider upstream tree identity changed")
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_STATELESS_UPSTREAM_EVIDENCE["source_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL upstream tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL upstream tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if observed_blobs != LVGL_STATELESS_UPSTREAM_EVIDENCE["source_blobs"]:
        raise AuditError("LVGL stateless provider source-blob identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_STATELESS_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL upstream {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_STATELESS_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_STATELESS_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL stateless provider upstream commit identity changed")

    parts = output_dir / "providers/lvgl-stateless-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-stateless-stage-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
            "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
            "-fdata-sections", "-fno-common", "-Wall", "-Wextra", "-Werror",
            f"-ffile-prefix-map={ROOT}=/openCFW/g2", "-I", str(stubs),
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(lvgl), "-I", str(ROOT / "third_party/freetype/include"),
            "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_OS=LV_OS_FREERTOS", "-DLV_DRAW_THREAD_STACK_SIZE=32768",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM", "-DLV_USE_FREETYPE=1",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=0",
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_stateless_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_STATELESS_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ])
        if "warning:" in output:
            raise AuditError(f"warning in LVGL stateless provider compile:\n{output}")
        source_defined = _symbols(nm, source_obj, undefined=False)
        source_undefined = _symbols(nm, source_obj, undefined=True)
        if source_defined != set(LVGL_STATELESS_PROVIDER_SYMBOLS) or source_undefined:
            raise AuditError("LVGL stateless provider source symbol/import closure changed")
        source_data = source_obj.read_bytes()
        if (
            len(source_data) != LVGL_STATELESS_SOURCE_ARTIFACT["size"]
            or _sha256(source_data) != LVGL_STATELESS_SOURCE_ARTIFACT["sha256"]
        ):
            raise AuditError("LVGL stateless target source artifact identity changed")

        abi_obj = parts / "lvgl_ambiq_lvgl_stateless_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_STATELESS_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ])
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL stateless ABI probe compile:\n{abi_output}")
        abi_data = abi_obj.read_bytes()
        if (
            len(abi_data) != LVGL_STATELESS_ABI_PROBE_ARTIFACT["size"]
            or _sha256(abi_data) != LVGL_STATELESS_ABI_PROBE_ARTIFACT["sha256"]
            or _symbols(nm, abi_obj, undefined=True)
            or _symbols(nm, abi_obj, undefined=False)
            != {"open_cfw_lvgl_stateless_provider_abi_probe"}
        ):
            raise AuditError("LVGL stateless ABI probe artifact boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-stateless-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(LVGL_STATELESS_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(LVGL_STATELESS_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("LVGL stateless isolated provider ELF closure changed")
    if (
        len(data) != LVGL_STATELESS_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != LVGL_STATELESS_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL stateless isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_STATELESS_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name,
            "size": len(source_data),
            "sha256": _sha256(source_data),
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "required_exports": sorted(LVGL_STATELESS_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "indirect_callback_boundaries": {
            "lv_draw_buf_flush_cache": "caller-supplied draw-buffer flush_cache_cb",
            "lv_draw_buf_invalidate_cache": "caller-supplied draw-buffer invalidate_cache_cb",
        },
        "warning_count": 0,
        "hostile_input_policy": (
            "null descriptors, callbacks, and buffers fail closed; array offset arithmetic is "
            "bounded; invalid FreeType descriptors and zero reference sizes return false/zero; "
            "negative image dimensions produce an empty area"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated exact-ABI stateless software provider with no allocator, scheduler, MMIO, "
            "libc, libm, global LVGL state, fixed-address, or ELF imports; cache callbacks remain "
            "caller-owned and hardware-unqualified"
        ),
    }


def _compile_target_runtime_provider(
    output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in TARGET_RUNTIME_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"target runtime provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    parts = output_dir / "providers/target-runtime-parts"
    parts.mkdir(parents=True, exist_ok=True)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2",
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
    ]
    source_obj = parts / "lvgl_ambiq_target_runtime_provider.o"
    output = _run([
        *flags, "-c", str(ROOT / TARGET_RUNTIME_PROVIDER_INPUTS["provider"][0]),
        "-o", str(source_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in target runtime provider compile:\n{output}")
    source_defined = _symbols(nm, source_obj, undefined=False)
    source_undefined = _symbols(nm, source_obj, undefined=True)
    source_data = source_obj.read_bytes()
    if source_defined != set(TARGET_RUNTIME_PROVIDER_SYMBOLS) or source_undefined:
        raise AuditError("target runtime provider source symbol/import closure changed")
    if (
        len(source_data) != TARGET_RUNTIME_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != TARGET_RUNTIME_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("target runtime target source artifact identity changed")

    abi_obj = parts / "lvgl_ambiq_target_runtime_provider_abi.o"
    abi_output = _run([
        *flags, "-c", str(ROOT / TARGET_RUNTIME_PROVIDER_INPUTS["abi_probe"][0]),
        "-o", str(abi_obj),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in target runtime ABI probe compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != TARGET_RUNTIME_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != TARGET_RUNTIME_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != {"__aeabi_d2lz", "__aeabi_f2ulz"}
        or abi_defined != {
            "open_cfw_target_runtime_probe_d2lz",
            "open_cfw_target_runtime_probe_f2ulz",
            "open_cfw_target_runtime_provider_abi_probe",
        }
        or abi_relocations != {
            "__aeabi_d2lz": {"R_ARM_THM_JUMP24": 1},
            "__aeabi_f2ulz": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("target runtime ABI probe artifact boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-target-runtime-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(TARGET_RUNTIME_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(TARGET_RUNTIME_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("target runtime isolated provider ELF closure changed")
    if (
        len(data) != TARGET_RUNTIME_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != TARGET_RUNTIME_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("target runtime isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": TARGET_RUNTIME_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name,
            "size": len(source_data),
            "sha256": _sha256(source_data),
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "abi_probe_external_relocations": abi_relocations,
        "hard_float_to_aeabi_base_pcs_marshalling_verified": True,
        "required_exports": sorted(TARGET_RUNTIME_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "zero-length memory operations accept null; other null memory inputs do not "
            "dereference; finite in-range conversions truncate toward zero; signed overflow, "
            "infinity, and NaN saturate; negative unsigned inputs return zero"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated exact-symbol target runtime provider with no allocator, scheduler, MMIO, "
            "libc, libm, fixed-address, or ELF imports; firmware collision/routing remains separate"
        ),
    }


def _compile_math_provider(
    output_dir: Path, clang: str, nm: str, objdump: str, lld: str, objcopy: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in MATH_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"math provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    if _git_blob(
        (ROOT / MATH_PROVIDER_INPUTS["musl_copyright"][0]).read_bytes()
    ) != MATH_UPSTREAM_EVIDENCE["copyright_git_blob"]:
        raise AuditError("authenticated musl COPYRIGHT Git blob identity changed")
    for key in ("acosf", "atan2f", "atanf", "fmod", "fmodf"):
        upstream_path = f"src/math/{key}.c"
        if _git_blob((ROOT / MATH_PROVIDER_INPUTS[key][0]).read_bytes()) != (
            MATH_UPSTREAM_EVIDENCE["source_git_blobs"][upstream_path]
        ):
            raise AuditError(f"authenticated musl Git blob identity changed: {upstream_path}")

    parts = output_dir / "providers/math-parts"
    parts.mkdir(parents=True, exist_ok=True)
    source_keys = ("acosf", "atan2f", "atanf", "fmod", "fmodf")
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-math-stage-") as temporary:
        stage = Path(temporary)
        for key in source_keys:
            shutil.copy2(ROOT / MATH_PROVIDER_INPUTS[key][0], stage / f"{key}.c")
        _run([
            "patch", "-s", "-p1", "-i",
            str(ROOT / MATH_PROVIDER_INPUTS["compat_patch"][0]),
        ], cwd=stage)
        flags = [
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
            "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
            "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fvisibility=hidden",
            "-Wall", "-Wextra", "-Werror",
            f"-ffile-prefix-map={ROOT}=/openCFW/g2",
            f"-ffile-prefix-map={stage}=/openCFW/musl-math",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/musl-math"),
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        definitions = {
            "acosf": ["-Dacosf=open_cfw_musl_acosf", "-Dsqrtf=open_cfw_musl_sqrtf"],
            "atan2f": ["-Datan2f=open_cfw_musl_atan2f", "-Datanf=open_cfw_musl_atanf"],
            "atanf": ["-Datanf=open_cfw_musl_atanf"],
            "fmod": ["-Dfmod=open_cfw_musl_fmod"],
            "fmodf": ["-Dfmodf=open_cfw_musl_fmodf"],
        }
        objects: list[Path] = []
        target_parts: list[dict[str, Any]] = []
        for key in source_keys:
            obj = parts / f"{key}.o"
            output = _run([
                *flags, *definitions[key], "-c", str(stage / f"{key}.c"),
                "-o", str(obj),
            ])
            if "warning:" in output:
                raise AuditError(f"warning in math provider compile: {key}\n{output}")
            objects.append(obj)
            data = obj.read_bytes()
            target_parts.append({
                "path": obj.name, "size": len(data), "sha256": _sha256(data),
                "defined_symbols": sorted(_symbols(nm, obj, undefined=False)),
                "undefined_symbols": sorted(_symbols(nm, obj, undefined=True)),
            })

        wrapper_obj = parts / "lvgl_ambiq_math_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / MATH_PROVIDER_INPUTS["provider"][0]),
            "-o", str(wrapper_obj),
        ])
        if "warning:" in output:
            raise AuditError(f"warning in math provider wrapper compile:\n{output}")
        objects.append(wrapper_obj)
        wrapper_data = wrapper_obj.read_bytes()
        target_parts.append({
            "path": wrapper_obj.name, "size": len(wrapper_data),
            "sha256": _sha256(wrapper_data),
            "defined_symbols": sorted(_symbols(nm, wrapper_obj, undefined=False)),
            "undefined_symbols": sorted(_symbols(nm, wrapper_obj, undefined=True)),
        })

        abi_obj = parts / "lvgl_ambiq_math_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / MATH_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ])
        if "warning:" in abi_output:
            raise AuditError(f"warning in math provider ABI probe compile:\n{abi_output}")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    expected_probe_exports = {
        "open_cfw_math_probe_acosf", "open_cfw_math_probe_atan2f",
        "open_cfw_math_probe_atanf", "open_cfw_math_probe_fmod",
        "open_cfw_math_probe_fmodf", "open_cfw_math_provider_abi_probe",
    }
    expected_probe_relocations = {
        symbol: {"R_ARM_THM_JUMP24": 1} for symbol in MATH_PROVIDER_SYMBOLS
    }
    if (
        len(abi_data) != MATH_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != MATH_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(MATH_PROVIDER_SYMBOLS)
        or abi_defined != expected_probe_exports
        or abi_relocations != expected_probe_relocations
    ):
        raise AuditError("math provider ABI probe artifact boundary changed")

    prelocalized = parts / "lvgl-ambiq-math-provider-prelocalized.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(MATH_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(prelocalized), *[str(obj) for obj in objects]])
    provider = output_dir / "providers/lvgl-ambiq-math-provider.o"
    _run([objcopy, "--localize-hidden", str(prelocalized), str(provider)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(MATH_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("math isolated provider ELF closure changed")
    if (
        len(data) != MATH_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != MATH_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("math isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": MATH_UPSTREAM_EVIDENCE,
        "target_parts": target_parts,
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "abi_probe_external_relocations": abi_relocations,
        "required_exports": sorted(MATH_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "domain-invalid acosf and invalid fmod/fmodf inputs return quiet NaN; exact-zero "
            "remainders preserve the numerator sign; no errno or floating-exception guarantee"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated Cortex-M55 exact-ABI software provider with zero ELF, allocator, scheduler, "
            "MMIO, fixed-address, libc, or libm imports; VSQRT.F32 is compile-proven only and "
            "target floating-point status/rounding behavior is not hardware-qualified"
        ),
    }


def _compile_math_dp_provider(
    output_dir: Path, clang: str, nm: str, objdump: str, lld: str, objcopy: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in MATH_DP_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"FPv5-D16 math provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    if _git_blob(
        (ROOT / MATH_DP_PROVIDER_INPUTS["musl_copyright"][0]).read_bytes()
    ) != MATH_UPSTREAM_EVIDENCE["copyright_git_blob"]:
        raise AuditError("authenticated musl COPYRIGHT Git blob identity changed")
    upstream_keys = {
        "cosf": "src/math/cosf.c",
        "sinf": "src/math/sinf.c",
        "tanf": "src/math/tanf.c",
        "cos_kernel": "src/math/__cosdf.c",
        "sin_kernel": "src/math/__sindf.c",
        "tan_kernel": "src/math/__tandf.c",
        "rem_pio2f": "src/math/__rem_pio2f.c",
        "rem_pio2_large": "src/math/__rem_pio2_large.c",
        "floor": "src/math/floor.c",
        "scalbn": "src/math/scalbn.c",
        "sqrt": "src/math/sqrt.c",
        "sqrt_data": "src/math/sqrt_data.c",
        "sqrt_data_header": "src/math/sqrt_data.h",
        "math_invalid": "src/math/__math_invalid.c",
    }
    for key, upstream_path in upstream_keys.items():
        if _git_blob((ROOT / MATH_DP_PROVIDER_INPUTS[key][0]).read_bytes()) != (
            MATH_DP_UPSTREAM_EVIDENCE["source_git_blobs"][upstream_path]
        ):
            raise AuditError(f"authenticated musl Git blob identity changed: {upstream_path}")

    parts = output_dir / "providers/math-dp-parts"
    parts.mkdir(parents=True, exist_ok=True)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-fvisibility=hidden",
        "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2",
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/musl-math"),
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
    ]
    internal_definitions = [
        "-D__cosdf=open_cfw_musl_cos_kernel",
        "-D__sindf=open_cfw_musl_sin_kernel",
        "-D__tandf=open_cfw_musl_tan_kernel",
        "-D__rem_pio2f=open_cfw_musl_rem_pio2f",
        "-D__rem_pio2_large=open_cfw_musl_rem_pio2_large",
        "-D__math_invalid=open_cfw_musl_math_invalid",
        "-D__rsqrt_tab=open_cfw_musl_rsqrt_tab",
        "-Dfloor=open_cfw_musl_floor",
        "-Dscalbn=open_cfw_musl_scalbn",
    ]
    source_specs = (
        ("cosf", "cosf", ["-Dcosf=open_cfw_musl_cosf"]),
        ("sinf", "sinf", ["-Dsinf=open_cfw_musl_sinf"]),
        ("tanf", "tanf", ["-Dtanf=open_cfw_musl_tanf"]),
        ("cos_kernel", "__cosdf", []),
        ("sin_kernel", "__sindf", []),
        ("tan_kernel", "__tandf", []),
        ("rem_pio2f", "__rem_pio2f", []),
        ("rem_pio2_large", "__rem_pio2_large", []),
        ("floor", "floor", []),
        ("scalbn", "scalbn", []),
        ("sqrt", "sqrt", ["-Dsqrt=open_cfw_musl_sqrt"]),
        ("sqrt_data", "sqrt_data", []),
        ("math_invalid", "__math_invalid", []),
    )
    objects: list[Path] = []
    target_parts: list[dict[str, Any]] = []
    for key, object_name, definitions in source_specs:
        obj = parts / f"{object_name}.o"
        output = _run([
            *flags, *internal_definitions, *definitions, "-c",
            str(ROOT / MATH_DP_PROVIDER_INPUTS[key][0]), "-o", str(obj),
        ])
        if "warning:" in output:
            raise AuditError(f"warning in FPv5-D16 math provider compile: {key}\n{output}")
        objects.append(obj)
        data = obj.read_bytes()
        target_parts.append({
            "path": obj.name, "size": len(data), "sha256": _sha256(data),
            "defined_symbols": sorted(_symbols(nm, obj, undefined=False)),
            "undefined_symbols": sorted(_symbols(nm, obj, undefined=True)),
        })

    wrapper_obj = parts / "lvgl_ambiq_math_dp_provider.o"
    output = _run([
        *flags, "-c", str(ROOT / MATH_DP_PROVIDER_INPUTS["provider"][0]),
        "-o", str(wrapper_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in FPv5-D16 math provider wrapper compile:\n{output}")
    objects.append(wrapper_obj)
    wrapper_data = wrapper_obj.read_bytes()
    target_parts.append({
        "path": wrapper_obj.name, "size": len(wrapper_data),
        "sha256": _sha256(wrapper_data),
        "defined_symbols": sorted(_symbols(nm, wrapper_obj, undefined=False)),
        "undefined_symbols": sorted(_symbols(nm, wrapper_obj, undefined=True)),
    })

    abi_obj = parts / "lvgl_ambiq_math_dp_provider_abi.o"
    abi_output = _run([
        *flags, "-c", str(ROOT / MATH_DP_PROVIDER_INPUTS["abi_probe"][0]),
        "-o", str(abi_obj),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in FPv5-D16 math ABI probe compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    expected_probe_exports = {
        "open_cfw_math_dp_probe_cosf", "open_cfw_math_dp_probe_sinf",
        "open_cfw_math_dp_probe_sqrt", "open_cfw_math_dp_probe_tanf",
        "open_cfw_math_dp_provider_abi_probe",
    }
    expected_probe_relocations = {
        symbol: {"R_ARM_THM_JUMP24": 1} for symbol in MATH_DP_PROVIDER_SYMBOLS
    }
    if (
        len(abi_data) != MATH_DP_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != MATH_DP_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(MATH_DP_PROVIDER_SYMBOLS)
        or abi_defined != expected_probe_exports
        or abi_relocations != expected_probe_relocations
    ):
        raise AuditError("FPv5-D16 math provider ABI probe artifact boundary changed")

    prelocalized = parts / "lvgl-ambiq-math-dp-provider-prelocalized.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(MATH_DP_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(prelocalized), *[str(obj) for obj in objects]])
    provider = output_dir / "providers/lvgl-ambiq-math-dp-provider.o"
    _run([objcopy, "--localize-hidden", str(prelocalized), str(provider)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(MATH_DP_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("FPv5-D16 math isolated provider ELF closure changed")
    if (
        len(data) != MATH_DP_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != MATH_DP_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("FPv5-D16 math isolated provider artifact identity changed")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": MATH_DP_UPSTREAM_EVIDENCE,
        "target_parts": target_parts,
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "abi_probe_external_relocations": abi_relocations,
        "required_exports": sorted(MATH_DP_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "trigonometric infinities and NaNs return NaN; signed-zero sine/tangent and square "
            "root are preserved; negative finite square-root inputs return NaN; no errno or "
            "floating-exception guarantee"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated exact-ABI Cortex-M55 FPv5-D16 provider with no ELF, allocator, scheduler, "
            "MMIO, fixed-address, libc, or libm imports; stock instruction evidence supports "
            "the optional DP ISA but runtime FPU state/rounding and collision remain unqualified"
        ),
    }


def _compile_lvgl_mutex_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_MUTEX_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL mutex provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }
    for key, upstream_path in (
        ("upstream_lv_freertos", "src/osal/lv_freertos.c"),
        ("upstream_lv_freertos_header", "src/osal/lv_freertos.h"),
        ("upstream_lv_os_header", "src/osal/lv_os.h"),
    ):
        if _git_blob((ROOT / LVGL_MUTEX_PROVIDER_INPUTS[key][0]).read_bytes()) != (
            LVGL_MUTEX_UPSTREAM_EVIDENCE["source_git_blobs"][upstream_path]
        ):
            raise AuditError(f"authenticated LVGL mutex Git blob changed: {upstream_path}")

    parts = output_dir / "providers/lvgl-mutex-parts"
    parts.mkdir(parents=True, exist_ok=True)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2",
    ]
    source_obj = parts / "lvgl_ambiq_lvgl_mutex_provider.o"
    output = _run([
        *flags, "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-c", str(ROOT / LVGL_MUTEX_PROVIDER_INPUTS["provider"][0]),
        "-o", str(source_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in LVGL mutex provider compile:\n{output}")
    source_data = source_obj.read_bytes()
    source_defined = _symbols(nm, source_obj, undefined=False)
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if source_defined != set(LVGL_MUTEX_PROVIDER_SYMBOLS) or source_undefined:
        raise AuditError("LVGL mutex source symbol/import closure changed")
    if (
        len(source_data) != LVGL_MUTEX_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_MUTEX_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL mutex target source artifact identity changed")

    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-mutex-stubs-") as temporary:
        stubs = Path(temporary) / "stubs"
        builder._write_stubs(stubs)
        abi_obj = parts / "lvgl_ambiq_lvgl_mutex_provider_abi.o"
        abi_output = _run([
            *flags,
            "-DLV_CONF_SKIP=1", "-DLV_USE_OS=LV_OS_FREERTOS",
            "-DLV_USE_FREERTOS_TASK_NOTIFY=1",
            "-I", str(stubs), "-I", str(ROOT / "third_party/lvgl"),
            "-c", str(ROOT / LVGL_MUTEX_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in LVGL mutex ABI probe compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    expected_probe_exports = {
        "open_cfw_mutex_probe_delete", "open_cfw_mutex_probe_init",
        "open_cfw_mutex_probe_lock", "open_cfw_mutex_probe_unlock",
    }
    expected_probe_relocations = {
        symbol: {"R_ARM_THM_JUMP24": 1} for symbol in LVGL_MUTEX_PROVIDER_SYMBOLS
    }
    if (
        len(abi_data) != LVGL_MUTEX_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_MUTEX_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_MUTEX_PROVIDER_SYMBOLS)
        or abi_defined != expected_probe_exports
        or abi_relocations != expected_probe_relocations
    ):
        raise AuditError("LVGL mutex ABI probe artifact boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-mutex-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(LVGL_MUTEX_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(LVGL_MUTEX_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("LVGL mutex isolated provider ELF closure changed")
    if (
        len(data) != LVGL_MUTEX_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != LVGL_MUTEX_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL mutex isolated provider artifact identity changed")
    source_text = (ROOT / LVGL_MUTEX_PROVIDER_INPUTS["provider"][0]).read_text(
        encoding="utf-8"
    ).upper()
    for address in LVGL_MUTEX_FIXED_IMPORTS:
        if address.removeprefix("0x") not in source_text:
            raise AuditError(f"LVGL mutex fixed-provider evidence changed: {address}")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_MUTEX_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "abi_probe_external_relocations": abi_relocations,
        "required_exports": sorted(LVGL_MUTEX_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": LVGL_MUTEX_FIXED_IMPORTS,
        "fixed_address_import_count": len(LVGL_MUTEX_FIXED_IMPORTS),
        "warning_count": 0,
        "hostile_input_policy": (
            "null descriptors and malformed initialized/null-handle states return invalid without "
            "calling FreeRTOS; failed lazy allocation leaves the descriptor uninitialized; delete "
            "clears the stale handle after the source-owned queue deletion"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated notify-mode-independent LVGL mutex ABI with no ELF imports; all six fixed "
            "callees are source-owned canonical entries, but scheduler state, heap, critical nesting, "
            "RAM placement, and live concurrency remain unqualified"
        ),
    }


def _compile_lvgl_heap_array_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_HEAP_ARRAY_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL heap/array provider input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL heap/array tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL heap/array tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL heap/array authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL heap/array {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL heap/array upstream commit identity changed")

    parts = output_dir / "providers/lvgl-heap-array-parts"
    parts.mkdir(parents=True, exist_ok=True)
    stubs = parts / "stubs"
    builder._write_stubs(stubs)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2", "-I", str(stubs),
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "third_party/lvgl"), "-DLV_CONF_SKIP=1",
        "-DLV_COLOR_DEPTH=8", "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1",
        "-DLV_USE_FLOAT=1", "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_FREERTOS",
        "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM",
    ]
    source_obj = parts / "lvgl_ambiq_lvgl_heap_array_provider.o"
    output = _run([
        *flags, "-c", str(ROOT / LVGL_HEAP_ARRAY_PROVIDER_INPUTS["provider"][0]),
        "-o", str(source_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in LVGL heap/array provider compile:\n{output}")
    source_data = source_obj.read_bytes()
    source_defined = _symbols(nm, source_obj, undefined=False)
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if source_defined != set(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS) or source_undefined:
        raise AuditError("LVGL heap/array source symbol/import closure changed")
    if (
        len(source_data) != LVGL_HEAP_ARRAY_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_HEAP_ARRAY_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL heap/array target source artifact identity changed")

    abi_obj = parts / "lvgl_ambiq_lvgl_heap_array_provider_abi.o"
    abi_output = _run([
        *flags, "-c", str(ROOT / LVGL_HEAP_ARRAY_PROVIDER_INPUTS["abi_probe"][0]),
        "-o", str(abi_obj),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in LVGL heap/array ABI probe compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    expected_probe_exports = {
        "open_cfw_heap_array_probe_deinit", "open_cfw_heap_array_probe_free",
        "open_cfw_heap_array_probe_malloc", "open_cfw_heap_array_probe_malloc_zeroed",
        "open_cfw_heap_array_probe_push",
    }
    expected_probe_relocations = {
        symbol: {"R_ARM_THM_JUMP24": 1}
        for symbol in LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS
    }
    if (
        len(abi_data) != LVGL_HEAP_ARRAY_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_HEAP_ARRAY_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS)
        or abi_defined != expected_probe_exports
        or abi_relocations != expected_probe_relocations
    ):
        raise AuditError("LVGL heap/array ABI probe artifact boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-heap-array-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if undefined or defined != set(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS) or external_relocations:
        raise AuditError("LVGL heap/array isolated provider ELF closure changed")
    if (
        len(data) != LVGL_HEAP_ARRAY_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != LVGL_HEAP_ARRAY_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL heap/array isolated provider artifact identity changed")
    source_text = (ROOT / LVGL_HEAP_ARRAY_PROVIDER_INPUTS["provider"][0]).read_text(
        encoding="utf-8"
    ).upper()
    for address in LVGL_HEAP_ARRAY_FIXED_IMPORTS:
        thumb_address = f"{int(address, 16) + 1:08X}"
        if thumb_address not in source_text:
            raise AuditError(f"LVGL heap/array fixed-provider evidence changed: {address}")
    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_HEAP_ARRAY_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "abi_probe_external_relocations": abi_relocations,
        "required_exports": sorted(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": LVGL_HEAP_ARRAY_FIXED_IMPORTS,
        "fixed_address_import_count": len(LVGL_HEAP_ARRAY_FIXED_IMPORTS),
        "warning_count": 0,
        "hostile_input_policy": (
            "null and inconsistent descriptors, capacity/byte/address overflow, external-buffer "
            "growth, overlapping element copies, and realloc failure return invalid without an "
            "out-of-bounds access; zero-size allocations use one stable non-heap byte"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "isolated exact-ABI Cortex-M55 provider with zero ELF imports; three fixed G2 heap "
            "facade calls are already source-owned, while live heap locking/RAM placement and "
            "provider collision remain runtime-unqualified"
        ),
    }


def _compile_lvgl_draw_buf_lifecycle_provider(
    builder, output_dir: Path, heap_array_obj: Path, clang: str, nm: str,
    objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL draw-buffer lifecycle input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL draw-buffer lifecycle tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL draw-buffer lifecycle tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL draw-buffer lifecycle authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL draw-buffer lifecycle {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL draw-buffer lifecycle upstream commit identity changed")

    parts = output_dir / "providers/lvgl-draw-buf-lifecycle-parts"
    parts.mkdir(parents=True, exist_ok=True)
    stubs = parts / "stubs"
    builder._write_stubs(stubs)
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-ffreestanding",
        "-fshort-enums", "-std=gnu11", "-O2", "-ffunction-sections",
        "-fdata-sections", "-fno-common", "-fno-builtin", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
        f"-ffile-prefix-map={ROOT}=/openCFW/g2", "-I", str(stubs),
        "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        "-I", str(ROOT / "third_party/lvgl"), "-DLV_CONF_SKIP=1",
        "-DLV_COLOR_DEPTH=8", "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1",
        "-DLV_USE_FLOAT=1", "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_FREERTOS",
        "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM",
    ]
    source_obj = parts / "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.o"
    output = _run([
        *flags, "-c",
        str(ROOT / LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS["provider"][0]),
        "-o", str(source_obj),
    ])
    if "warning:" in output:
        raise AuditError(f"warning in LVGL draw-buffer lifecycle compile:\n{output}")
    source_data = source_obj.read_bytes()
    source_defined = _symbols(nm, source_obj, undefined=False)
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if (
        source_defined != set(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS)
        or source_undefined != {"lv_free"}
        or _relocations(objdump, source_obj, source_undefined)
        != {"lv_free": {"R_ARM_THM_JUMP24": 2}}
    ):
        raise AuditError("LVGL draw-buffer lifecycle source import closure changed")
    if (
        len(source_data) != LVGL_DRAW_BUF_LIFECYCLE_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_DRAW_BUF_LIFECYCLE_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-buffer lifecycle source artifact identity changed")

    abi_obj = parts / "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider_abi.o"
    abi_output = _run([
        *flags, "-c",
        str(ROOT / LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_INPUTS["abi_probe"][0]),
        "-o", str(abi_obj),
    ])
    if "warning:" in abi_output:
        raise AuditError(f"warning in LVGL draw-buffer lifecycle ABI compile:\n{abi_output}")
    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_defined = _symbols(nm, abi_obj, undefined=False)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != LVGL_DRAW_BUF_LIFECYCLE_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_DRAW_BUF_LIFECYCLE_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS)
        or abi_defined != {"open_cfw_draw_buf_lifecycle_probe"}
        or abi_relocations != {"lv_draw_buf_destroy": {"R_ARM_THM_JUMP24": 1}}
    ):
        raise AuditError("LVGL draw-buffer lifecycle ABI boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-draw-buf-lifecycle-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_draw_buf_destroy",
        "-o", str(provider), str(source_obj),
    ])
    undefined = _symbols(nm, provider, undefined=True)
    defined = _symbols(nm, provider, undefined=False)
    external_relocations = _relocations(objdump, provider, undefined)
    data = provider.read_bytes()
    if (
        undefined != {"lv_free"}
        or defined != set(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS)
        or external_relocations != {"lv_free": {"R_ARM_THM_JUMP24": 2}}
    ):
        raise AuditError("LVGL draw-buffer lifecycle isolated provider closure changed")
    if (
        len(data) != LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_ARTIFACT["size"]
        or _sha256(data) != LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-buffer lifecycle provider artifact identity changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-heap-lifecycle-aggregate.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(
        LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS | LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS
    ):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(aggregate), str(provider), str(heap_array_obj)])
    aggregate_data = aggregate.read_bytes()
    aggregate_defined = _symbols(nm, aggregate, undefined=False)
    if (
        _symbols(nm, aggregate, undefined=True)
        or aggregate_defined
        != set(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS | LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS)
        or len(aggregate_data) != LVGL_DRAW_BUF_LIFECYCLE_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_DRAW_BUF_LIFECYCLE_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL heap/lifecycle aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_DRAW_BUF_LIFECYCLE_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {"path": provider.name, "size": len(data), "sha256": _sha256(data)},
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(defined),
        "elf_undefined_symbols": sorted(undefined),
        "external_relocations": external_relocations,
        "reviewed_runtime_dependencies": {
            "lv_free": "local_lvgl_heap_array_provider",
        },
        "aggregate_elf_undefined_symbols": [],
        "indirect_callback_boundaries": {
            "buf_free_cb": "descriptor-owned buffer-release callback",
        },
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "null, non-allocated, and allocated/null-handler descriptors return without a callback "
            "or heap call; valid allocated descriptors preserve callback-before-descriptor-free order"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact-ABI Cortex-M55 lifecycle provider; its sole ELF import resolves in the reviewed "
            "heap/array aggregate, while callback ownership and live heap behavior remain unqualified"
        ),
    }


def _compile_lvgl_global_storage_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL global-storage input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL global-storage tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL global-storage tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL global-storage authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL global-storage {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL global-storage upstream commit identity changed")

    parts = output_dir / "providers/lvgl-global-storage-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-global-stage-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_global_storage_provider.o"
        output = _run([
            *flags, "-c",
            str(ROOT / LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL global-storage compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_global_storage_provider_abi.o"
        abi_output = _run([
            *flags, "-c",
            str(ROOT / LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL global-storage ABI compile:\n{abi_output}")

    def symbol_record(path: Path, symbol: str) -> tuple[str, int, int]:
        for line in _run([nm, "--format=posix", "--print-size", str(path)]).splitlines():
            fields = line.split()
            if len(fields) >= 4 and fields[0] == symbol:
                return fields[1], int(fields[2], 16), int(fields[3], 16)
        raise AuditError(f"missing target symbol record: {symbol}")

    source_data = source_obj.read_bytes()
    if (
        _symbols(nm, source_obj, undefined=True)
        or _symbols(nm, source_obj, undefined=False) != set(LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS)
        or symbol_record(source_obj, "lv_global") != ("B", 0, 0x1EC)
        or len(source_data) != LVGL_GLOBAL_STORAGE_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_GLOBAL_STORAGE_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL global-storage source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != LVGL_GLOBAL_STORAGE_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_GLOBAL_STORAGE_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False)
        != {"open_cfw_lvgl_global_storage_probe"}
        or abi_relocations != {
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1}
        }
    ):
        raise AuditError("LVGL global-storage ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-global-storage-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_global",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True)
        or _symbols(nm, provider, undefined=False) != set(LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS)
        or symbol_record(provider, "lv_global") != ("B", 0, 0x1EC)
        or len(provider_data) != LVGL_GLOBAL_STORAGE_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_GLOBAL_STORAGE_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL global-storage isolated provider closure changed")

    placement = output_dir / "providers/lvgl-ambiq-lvgl-global-storage-placement.elf"
    _run([
        lld, "-T", str(ROOT / LVGL_GLOBAL_STORAGE_PROVIDER_INPUTS["placement_linker_script"][0]),
        "--entry=0", "-o", str(placement), str(provider),
    ])
    placement_data = placement.read_bytes()
    if (
        _symbols(nm, placement, undefined=True)
        or symbol_record(placement, "lv_global") != ("B", 0x2006F548, 0x1EC)
        or len(placement_data) != LVGL_GLOBAL_STORAGE_PLACEMENT_ARTIFACT["size"]
        or _sha256(placement_data) != LVGL_GLOBAL_STORAGE_PLACEMENT_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL global-storage placement proof changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_GLOBAL_STORAGE_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "placement_proof_artifact": {
            "path": placement.name, "size": len(placement_data),
            "sha256": _sha256(placement_data),
        },
        "required_exports": ["lv_global"],
        "all_external_exports": ["lv_global"],
        "symbol_type": "OBJECT/BSS",
        "symbol_size": 0x1EC,
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "abi_probe_external_relocations": abi_relocations,
        "authenticated_stock_address": "0x2006F548",
        "isolated_placement_proof": "0x2006F548",
        "initial_state": "C static-storage zero initialization",
        "callable_hostile_input_surface": False,
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact 492-byte source object and isolated stock-address placement proof only; live "
            "linker ownership, collision, initializer ordering, and handler contents remain unqualified"
        ),
    }


def _compile_lvgl_freetype_event_provider(
    builder, output_dir: Path, global_storage_obj: Path, clang: str,
    nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_FREETYPE_EVENT_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL FreeType-event input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL FreeType-event tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL FreeType-event tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL FreeType-event authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL FreeType-event {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL FreeType-event upstream commit identity changed")

    parts = output_dir / "providers/lvgl-freetype-event-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-freetype-event-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_freetype_event_provider.o"
        output = _run([
            *flags, "-c",
            str(ROOT / LVGL_FREETYPE_EVENT_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL FreeType-event compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_freetype_event_provider_abi.o"
        abi_output = _run([
            *flags, "-c",
            str(ROOT / LVGL_FREETYPE_EVENT_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL FreeType-event ABI compile:\n{abi_output}")

    source_data = source_obj.read_bytes()
    source_undefined = _symbols(nm, source_obj, undefined=True)
    source_relocations = _relocations(objdump, source_obj, source_undefined)
    if (
        _symbols(nm, source_obj, undefined=False) != set(LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS)
        or source_undefined != {"lv_global"}
        or source_relocations != {
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1}
        }
        or len(source_data) != LVGL_FREETYPE_EVENT_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_FREETYPE_EVENT_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL FreeType-event source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != LVGL_FREETYPE_EVENT_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_FREETYPE_EVENT_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False)
        != {"open_cfw_lvgl_freetype_event_probe"}
        or abi_relocations != {
            "lv_freetype_outline_add_event": {"R_ARM_THM_JUMP24": 1}
        }
    ):
        raise AuditError("LVGL FreeType-event ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-freetype-event-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_freetype_outline_add_event",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    undefined = _symbols(nm, provider, undefined=True)
    if (
        undefined != {"lv_global"}
        or _symbols(nm, provider, undefined=False) != set(LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, undefined) != source_relocations
        or len(provider_data) != LVGL_FREETYPE_EVENT_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_FREETYPE_EVENT_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL FreeType-event isolated provider closure changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-global-freetype-event-aggregate.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(
        LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS | LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS
    ):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(aggregate), str(provider), str(global_storage_obj)])
    aggregate_data = aggregate.read_bytes()
    if (
        _symbols(nm, aggregate, undefined=True)
        or _symbols(nm, aggregate, undefined=False)
        != set(LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS | LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS)
        or len(aggregate_data) != LVGL_FREETYPE_EVENT_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_FREETYPE_EVENT_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL global/FreeType-event aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_FREETYPE_EVENT_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": sorted(undefined),
        "external_relocations": source_relocations,
        "reviewed_runtime_dependencies": {
            "lv_global": "local_lvgl_global_storage_provider",
        },
        "aggregate_elf_undefined_symbols": [],
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "a null FreeType context returns without a write; valid context stores the callback "
            "and preserves authenticated ignored filter/user-data behavior"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact-ABI callback setter with global-storage aggregate closure; live FreeType context "
            "allocation/lifetime, initializer order, collision, and concurrency remain unqualified"
        ),
    }


def _compile_lvgl_draw_buf_shape_provider(
    builder, output_dir: Path, heap_array_obj: Path, global_storage_obj: Path,
    clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_DRAW_BUF_SHAPE_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL draw-buffer shape input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL draw-buffer shape tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL draw-buffer shape tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL draw-buffer shape authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL draw-buffer shape {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL draw-buffer shape upstream commit identity changed")

    parts = output_dir / "providers/lvgl-draw-buf-shape-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-draw-buf-shape-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_draw_buf_shape_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_BUF_SHAPE_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL draw-buffer shape compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_draw_buf_shape_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_BUF_SHAPE_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL draw-buffer shape ABI compile:\n{abi_output}")

    source_data = source_obj.read_bytes()
    source_undefined = _symbols(nm, source_obj, undefined=True)
    source_relocations = _relocations(objdump, source_obj, source_undefined)
    expected_source_relocations = {
        "lv_free": {"R_ARM_THM_CALL": 1},
        "lv_global": {"R_ARM_THM_MOVT_ABS": 2, "R_ARM_THM_MOVW_ABS_NC": 2},
        "lv_malloc_zeroed": {"R_ARM_THM_CALL": 1},
    }
    if (
        _symbols(nm, source_obj, undefined=False) != set(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS)
        or source_undefined != {"lv_free", "lv_global", "lv_malloc_zeroed"}
        or source_relocations != expected_source_relocations
        or len(source_data) != LVGL_DRAW_BUF_SHAPE_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_DRAW_BUF_SHAPE_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-buffer shape source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != LVGL_DRAW_BUF_SHAPE_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_DRAW_BUF_SHAPE_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False) != {
            "open_cfw_lvgl_draw_buf_create_probe",
            "open_cfw_lvgl_draw_buf_reshape_probe",
        }
        or abi_relocations != {
            "lv_draw_buf_create": {"R_ARM_THM_JUMP24": 1},
            "lv_draw_buf_reshape": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("LVGL draw-buffer shape ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-draw-buf-shape-provider.o"
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(provider), str(source_obj)])
    provider_data = provider.read_bytes()
    undefined = _symbols(nm, provider, undefined=True)
    if (
        undefined != source_undefined
        or _symbols(nm, provider, undefined=False) != set(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, undefined) != expected_source_relocations
        or len(provider_data) != LVGL_DRAW_BUF_SHAPE_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_DRAW_BUF_SHAPE_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-buffer shape isolated provider closure changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-draw-buf-shape-aggregate.o"
    aggregate_exports = (
        LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS
        | LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS
        | LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS
    )
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(aggregate_exports):
        command.extend(["-u", symbol])
    _run([
        *command, "-o", str(aggregate), str(provider),
        str(global_storage_obj), str(heap_array_obj),
    ])
    aggregate_data = aggregate.read_bytes()
    if (
        _symbols(nm, aggregate, undefined=True)
        or _symbols(nm, aggregate, undefined=False) != set(aggregate_exports)
        or len(aggregate_data) != LVGL_DRAW_BUF_SHAPE_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_DRAW_BUF_SHAPE_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-buffer shape aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_DRAW_BUF_SHAPE_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": sorted(undefined),
        "external_relocations": expected_source_relocations,
        "reviewed_runtime_dependencies": {
            "lv_free": "local_lvgl_heap_array_provider",
            "lv_global": "local_lvgl_global_storage_provider",
            "lv_malloc_zeroed": "local_lvgl_heap_array_provider",
        },
        "aggregate_elf_undefined_symbols": [],
        "indirect_callback_boundaries": {
            "buf_malloc_cb": "retained Ambiq initializer-owned allocation callback",
            "buf_free_cb": "retained Ambiq initializer-owned release callback",
            "align_pointer_cb": "retained Ambiq initializer-owned alignment callback",
            "width_to_stride_cb": "retained Ambiq initializer-owned stride callback",
        },
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "null/missing callbacks, zero or nonrepresentable geometry/stride, byte-size overflow, "
            "descriptor/buffer allocation failure, null alignment, and over-capacity reshape fail "
            "without a partial descriptor mutation or leaked owned allocation"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact-ABI create/reshape provider with reviewed heap/global aggregate closure; callback "
            "population is retained Ambiq source but live initialization, pools, collision, RAM, and "
            "concurrency remain unqualified"
        ),
    }


def _compile_lvgl_font_fmt_provider(
    builder, output_dir: Path, clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_FONT_FMT_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL font-format input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_FONT_FMT_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_FONT_FMT_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL font-format tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL font-format tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_FONT_FMT_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_FONT_FMT_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL font-format authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_FONT_FMT_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL font-format {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_FONT_FMT_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_FONT_FMT_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL font-format upstream commit identity changed")

    parts = output_dir / "providers/lvgl-font-fmt-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-font-fmt-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_font_fmt_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_FONT_FMT_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL font-format compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_font_fmt_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_FONT_FMT_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL font-format ABI compile:\n{abi_output}")

    source_data = source_obj.read_bytes()
    if (
        _symbols(nm, source_obj, undefined=True)
        or _symbols(nm, source_obj, undefined=False) != set(LVGL_FONT_FMT_PROVIDER_SYMBOLS)
        or _relocations(objdump, source_obj, set())
        or len(source_data) != LVGL_FONT_FMT_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_FONT_FMT_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL font-format source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    abi_relocations = _relocations(objdump, abi_obj, abi_undefined)
    if (
        len(abi_data) != LVGL_FONT_FMT_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_FONT_FMT_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_FONT_FMT_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False) != {"open_cfw_lvgl_font_fmt_probe"}
        or abi_relocations != {"lv_font_get_bitmap_fmt_txt": {"R_ARM_THM_JUMP24": 1}}
    ):
        raise AuditError("LVGL font-format ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-font-fmt-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_font_get_bitmap_fmt_txt",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True)
        or _symbols(nm, provider, undefined=False) != set(LVGL_FONT_FMT_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, set())
        or len(provider_data) != LVGL_FONT_FMT_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_FONT_FMT_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL font-format isolated provider closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_FONT_FMT_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "required_exports": sorted(LVGL_FONT_FMT_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "indirect_callback_boundaries": {
            "flush_cache_cb": "caller-supplied draw-buffer handler; absence is a no-op",
        },
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "null descriptors/data, zero or over-capacity geometry, invalid stride, and unsupported "
            "plain/compressed bpp fail without output mutation or cache callback"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "zero-import exact-ABI fmt_txt decoder with bounded output and invocation-local RLE "
            "state; input blob length is absent from the LVGL ABI and remains a caller precondition"
        ),
    }


def _compile_lvgl_vector_destroy_provider(
    builder, output_dir: Path, heap_array_obj: Path,
    clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_VECTOR_DESTROY_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL vector-destroy input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL vector-destroy tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL vector-destroy tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL vector-destroy authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL vector-destroy {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL vector-destroy upstream commit identity changed")

    parts = output_dir / "providers/lvgl-vector-destroy-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-vector-destroy-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_vector_destroy_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_VECTOR_DESTROY_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL vector-destroy compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_vector_destroy_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_VECTOR_DESTROY_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL vector-destroy ABI compile:\n{abi_output}")

    expected_imports = {"lv_array_deinit", "lv_free"}
    expected_relocations = {
        "lv_array_deinit": {"R_ARM_THM_CALL": 3},
        "lv_free": {"R_ARM_THM_CALL": 2, "R_ARM_THM_JUMP24": 1},
    }
    source_data = source_obj.read_bytes()
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if (
        source_undefined != expected_imports
        or _symbols(nm, source_obj, undefined=False)
        != set(LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS)
        or _relocations(objdump, source_obj, source_undefined) != expected_relocations
        or len(source_data) != LVGL_VECTOR_DESTROY_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_VECTOR_DESTROY_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL vector-destroy source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    if (
        len(abi_data) != LVGL_VECTOR_DESTROY_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_VECTOR_DESTROY_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False) != {"open_cfw_lvgl_vector_destroy_probe"}
        or _relocations(objdump, abi_obj, abi_undefined) != {
            "lv_vector_for_each_destroy_tasks": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("LVGL vector-destroy ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-vector-destroy-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_vector_for_each_destroy_tasks",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True) != expected_imports
        or _symbols(nm, provider, undefined=False) != set(LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, expected_imports) != expected_relocations
        or len(provider_data) != LVGL_VECTOR_DESTROY_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_VECTOR_DESTROY_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL vector-destroy isolated provider closure changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-vector-destroy-aggregate.o"
    aggregate_exports = LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS | LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(aggregate_exports):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(aggregate), str(provider), str(heap_array_obj)])
    aggregate_data = aggregate.read_bytes()
    if (
        _symbols(nm, aggregate, undefined=True)
        or _symbols(nm, aggregate, undefined=False) != set(aggregate_exports)
        or len(aggregate_data) != LVGL_VECTOR_DESTROY_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_VECTOR_DESTROY_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL vector-destroy aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_VECTOR_DESTROY_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_VECTOR_DESTROY_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": sorted(expected_imports),
        "external_relocations": expected_relocations,
        "reviewed_runtime_dependencies": {
            "lv_array_deinit": "local_lvgl_heap_array_provider",
            "lv_free": "local_lvgl_heap_array_provider",
        },
        "aggregate_elf_undefined_symbols": [],
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "a null list is a no-op; empty and multi-node lists preserve unlink-before-callback "
            "ordering and release path arrays, dash arrays, tasks, and the list exactly once"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact-ABI task-list lifecycle with reviewed allocator/array aggregate closure; list "
            "node extent and callback mutation remain caller-owned LVGL preconditions"
        ),
    }


def _compile_lvgl_draw_unit_provider(
    builder, output_dir: Path, heap_array_obj: Path, global_storage_obj: Path,
    clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_DRAW_UNIT_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL draw-unit input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL draw-unit tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL draw-unit tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL draw-unit authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL draw-unit {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL draw-unit upstream commit identity changed")

    parts = output_dir / "providers/lvgl-draw-unit-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-draw-unit-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_draw_unit_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_UNIT_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL draw-unit compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_draw_unit_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_UNIT_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL draw-unit ABI compile:\n{abi_output}")

    expected_imports = {"lv_global", "lv_malloc_zeroed"}
    expected_relocations = {
        "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
        "lv_malloc_zeroed": {"R_ARM_THM_CALL": 1},
    }
    source_data = source_obj.read_bytes()
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if (
        source_undefined != expected_imports
        or _symbols(nm, source_obj, undefined=False) != set(LVGL_DRAW_UNIT_PROVIDER_SYMBOLS)
        or _relocations(objdump, source_obj, source_undefined) != expected_relocations
        or len(source_data) != LVGL_DRAW_UNIT_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_DRAW_UNIT_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-unit source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    if (
        len(abi_data) != LVGL_DRAW_UNIT_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_DRAW_UNIT_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_DRAW_UNIT_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False) != {"open_cfw_lvgl_draw_create_unit_probe"}
        or _relocations(objdump, abi_obj, abi_undefined) != {
            "lv_draw_create_unit": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("LVGL draw-unit ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-draw-unit-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_draw_create_unit",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True) != expected_imports
        or _symbols(nm, provider, undefined=False) != set(LVGL_DRAW_UNIT_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, expected_imports) != expected_relocations
        or len(provider_data) != LVGL_DRAW_UNIT_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_DRAW_UNIT_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-unit isolated provider closure changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-draw-unit-aggregate.o"
    aggregate_exports = (
        LVGL_DRAW_UNIT_PROVIDER_SYMBOLS
        | LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS
        | LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS
    )
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(aggregate_exports):
        command.extend(["-u", symbol])
    _run([
        *command, "-o", str(aggregate), str(provider),
        str(heap_array_obj), str(global_storage_obj),
    ])
    aggregate_data = aggregate.read_bytes()
    if (
        _symbols(nm, aggregate, undefined=True)
        or _symbols(nm, aggregate, undefined=False) != set(aggregate_exports)
        or len(aggregate_data) != LVGL_DRAW_UNIT_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_DRAW_UNIT_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-unit aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_DRAW_UNIT_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_DRAW_UNIT_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": sorted(expected_imports),
        "external_relocations": expected_relocations,
        "reviewed_runtime_dependencies": {
            "lv_global": "local_lvgl_global_storage_provider",
            "lv_malloc_zeroed": "local_lvgl_heap_array_provider",
        },
        "aggregate_elf_undefined_symbols": [],
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "undersized extents, allocator failure, and IDs above INT32_MAX fail before allocation "
            "or global-list mutation; valid allocations preserve zeroed extension bytes"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact-ABI draw-unit creation with reviewed allocator/global aggregate closure; "
            "initializer order, list ownership, concurrency, collision, RAM placement, and "
            "allocation lifetime remain unqualified"
        ),
    }


def _compile_lvgl_draw_dispatch_provider(
    builder, output_dir: Path, global_storage_obj: Path,
    clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in LVGL_DRAW_DISPATCH_PROVIDER_INPUTS.items():
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL draw-dispatch input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    upstream = json.loads(
        (ROOT / LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL draw-dispatch tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL draw-dispatch tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL draw-dispatch authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL draw-dispatch {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL draw-dispatch upstream commit identity changed")

    parts = output_dir / "providers/lvgl-draw-dispatch-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-draw-dispatch-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_draw_dispatch_provider.o"
        output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_DISPATCH_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL draw-dispatch compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_draw_dispatch_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_DRAW_DISPATCH_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL draw-dispatch ABI compile:\n{abi_output}")

    expected_imports = {"lv_global", "lv_thread_sync_signal"}
    expected_relocations = {
        "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
        "lv_thread_sync_signal": {"R_ARM_THM_CALL": 1, "R_ARM_THM_JUMP24": 1},
    }
    source_data = source_obj.read_bytes()
    source_undefined = _symbols(nm, source_obj, undefined=True)
    if (
        source_undefined != expected_imports
        or _symbols(nm, source_obj, undefined=False) != set(LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS)
        or _relocations(objdump, source_obj, source_undefined) != expected_relocations
        or len(source_data) != LVGL_DRAW_DISPATCH_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_DRAW_DISPATCH_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-dispatch source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    if (
        len(abi_data) != LVGL_DRAW_DISPATCH_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_DRAW_DISPATCH_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False)
        != {"open_cfw_lvgl_draw_dispatch_request_probe"}
        or _relocations(objdump, abi_obj, abi_undefined) != {
            "lv_draw_dispatch_request": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("LVGL draw-dispatch ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-draw-dispatch-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_draw_dispatch_request",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True) != expected_imports
        or _symbols(nm, provider, undefined=False) != set(LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, expected_imports) != expected_relocations
        or len(provider_data) != LVGL_DRAW_DISPATCH_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_DRAW_DISPATCH_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-dispatch isolated provider closure changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-draw-dispatch-aggregate.o"
    aggregate_exports = LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS | LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(aggregate_exports):
        command.extend(["-u", symbol])
    _run([*command, "-o", str(aggregate), str(provider), str(global_storage_obj)])
    aggregate_data = aggregate.read_bytes()
    transitive_residual = {"lv_thread_sync_signal"}
    if (
        _symbols(nm, aggregate, undefined=True) != transitive_residual
        or _symbols(nm, aggregate, undefined=False) != set(aggregate_exports)
        or _relocations(objdump, aggregate, transitive_residual)
        != {"lv_thread_sync_signal": {"R_ARM_THM_CALL": 1, "R_ARM_THM_JUMP24": 1}}
        or len(aggregate_data) != LVGL_DRAW_DISPATCH_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_DRAW_DISPATCH_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL draw-dispatch aggregate boundary changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_DRAW_DISPATCH_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": sorted(expected_imports),
        "external_relocations": expected_relocations,
        "reviewed_runtime_dependencies": {
            "lv_global": "local_lvgl_global_storage_provider",
            "lv_thread_sync_signal": "remaining FreeRTOS OSAL residual owner",
        },
        "aggregate_elf_undefined_symbols": sorted(transitive_residual),
        "transitive_residual_dependencies": sorted(transitive_residual),
        "dependency_admitted": False,
        "fixed_address_imports": {},
        "fixed_address_import_count": 0,
        "warning_count": 0,
        "hostile_input_policy": (
            "the no-argument request always emits both exact signals even if the first signal "
            "reports failure; sync-object validity remains an initialization precondition"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact recovered FreeRTOS-branch request sequence; the global sync initializer, "
            "thread-sync provider, scheduler/task-notification mode, RAM, and concurrency "
            "remain separately unqualified"
        ),
    }


def _compile_lvgl_thread_sync_signal_provider(
    builder, output_dir: Path, global_storage_obj: Path, draw_dispatch_obj: Path,
    clang: str, nm: str, objdump: str, lld: str,
) -> tuple[Path, dict[str, Any]]:
    inputs: dict[str, dict[str, Any]] = {}
    for name, (relative, size, sha256, license_id) in (
        LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS.items()
    ):
        path = ROOT / relative
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != sha256:
            raise AuditError(f"LVGL thread-sync-signal input identity changed: {relative}")
        inputs[name] = {
            "path": relative, "size": size, "sha256": sha256, "license": license_id,
        }

    for key, blob in {
        "upstream_lv_freertos": "c1eeccdf0dbd0bfd73021fa14aacc7827f8d379c",
        "upstream_lv_freertos_header": "a3bafca74e5518795e15ee76b87eae8baffb2e53",
        "upstream_lv_os_header": "47fd80108dc19c1811d471cdfdd2a1ce31486457",
        "upstream_lv_conf_internal": "a848f30f7d68e5550af4eaf8b4bd7a54c770b4e7",
    }.items():
        if _git_blob((ROOT / LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS[key][0]).read_bytes()) != blob:
            raise AuditError(f"LVGL thread-sync-signal upstream blob changed: {key}")

    upstream = json.loads(
        (ROOT / LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["tree_record"]["path"]).read_text()
    )
    observed_blobs: dict[str, str] = {}
    for source_path in LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["source_git_blobs"]:
        parent, name = source_path.rsplit("/", 1)
        tree = next((row for row in upstream.get("trees", []) if row.get("path") == parent), None)
        if tree is None:
            raise AuditError(f"LVGL thread-sync-signal tree record omits {parent}")
        entry = next((row for row in tree.get("entries", []) if row.get("name") == name), None)
        if entry is None or entry.get("type") != "blob":
            raise AuditError(f"LVGL thread-sync-signal tree record omits {source_path}")
        observed_blobs[source_path] = entry["oid"]
    if (
        upstream.get("root_tree") != LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["tree"]
        or observed_blobs != LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["source_git_blobs"]
    ):
        raise AuditError("LVGL thread-sync-signal authenticated source identity changed")
    for record_name in ("tree_record", "commit_record"):
        record = LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE[record_name]
        data = (ROOT / record["path"]).read_bytes()
        if len(data) != record["size"] or _sha256(data) != record["sha256"]:
            raise AuditError(f"LVGL thread-sync-signal {record_name} identity changed")
    commit_record = json.loads(
        (ROOT / LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["commit_record"]["path"]).read_text()
    )
    if commit_record.get("oid") != LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE["commit"]:
        raise AuditError("LVGL thread-sync-signal upstream commit identity changed")

    recovered_config = (
        ROOT / LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS["recovered_lv_conf"][0]
    ).read_text(encoding="utf-8")
    if (
        "#define LV_USE_OS LV_OS_FREERTOS" not in recovered_config
        or "LV_USE_FREERTOS_TASK_NOTIFY" in recovered_config
        or "LV_KCONFIG_PRESENT" in recovered_config
    ):
        raise AuditError("recovered G2 LVGL task-notification selection changed")

    parts = output_dir / "providers/lvgl-thread-sync-signal-parts"
    parts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-thread-sync-signal-") as temporary:
        stage = Path(temporary)
        lvgl = builder._stage_tree(stage)
        stubs = stage / "stubs"
        builder._write_stubs(stubs)
        flags = [
            *builder._compiler_flags(clang, stage, lvgl, stubs),
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
        ]
        source_obj = parts / "lvgl_ambiq_lvgl_thread_sync_signal_provider.o"
        output = _run([
            *flags, "-c",
            str(ROOT / LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS["provider"][0]),
            "-o", str(source_obj),
        ], cwd=stage)
        if "warning:" in output:
            raise AuditError(f"warning in LVGL thread-sync-signal compile:\n{output}")
        abi_obj = parts / "lvgl_ambiq_lvgl_thread_sync_signal_provider_abi.o"
        abi_output = _run([
            *flags, "-c", str(ROOT / LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS["abi_probe"][0]),
            "-o", str(abi_obj),
        ], cwd=stage)
        if "warning:" in abi_output:
            raise AuditError(f"warning in LVGL thread-sync-signal ABI compile:\n{abi_output}")

    source_data = source_obj.read_bytes()
    if (
        _symbols(nm, source_obj, undefined=True)
        or _symbols(nm, source_obj, undefined=False)
        != set(LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS)
        or _relocations(objdump, source_obj, set())
        or len(source_data) != LVGL_THREAD_SYNC_SIGNAL_SOURCE_ARTIFACT["size"]
        or _sha256(source_data) != LVGL_THREAD_SYNC_SIGNAL_SOURCE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL thread-sync-signal source object boundary changed")

    abi_data = abi_obj.read_bytes()
    abi_undefined = _symbols(nm, abi_obj, undefined=True)
    if (
        len(abi_data) != LVGL_THREAD_SYNC_SIGNAL_ABI_PROBE_ARTIFACT["size"]
        or _sha256(abi_data) != LVGL_THREAD_SYNC_SIGNAL_ABI_PROBE_ARTIFACT["sha256"]
        or abi_undefined != set(LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS)
        or _symbols(nm, abi_obj, undefined=False)
        != {"open_cfw_lvgl_thread_sync_signal_probe"}
        or _relocations(objdump, abi_obj, abi_undefined) != {
            "lv_thread_sync_signal": {"R_ARM_THM_JUMP24": 1},
        }
    ):
        raise AuditError("LVGL thread-sync-signal ABI probe boundary changed")

    provider = output_dir / "providers/lvgl-ambiq-lvgl-thread-sync-signal-provider.o"
    _run([
        lld, "-r", "--gc-sections", "-u", "lv_thread_sync_signal",
        "-o", str(provider), str(source_obj),
    ])
    provider_data = provider.read_bytes()
    if (
        _symbols(nm, provider, undefined=True)
        or _symbols(nm, provider, undefined=False)
        != set(LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS)
        or _relocations(objdump, provider, set())
        or len(provider_data) != LVGL_THREAD_SYNC_SIGNAL_PROVIDER_ARTIFACT["size"]
        or _sha256(provider_data) != LVGL_THREAD_SYNC_SIGNAL_PROVIDER_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL thread-sync-signal isolated provider closure changed")

    source_text = (
        ROOT / LVGL_THREAD_SYNC_SIGNAL_PROVIDER_INPUTS["provider"][0]
    ).read_text(encoding="utf-8")
    fixed_addresses = {
        f"0x{int(match, 16):08X}"
        for match in re.findall(r"\(uintptr_t\)0x([0-9A-Fa-f]{8})U", source_text)
    }
    if fixed_addresses != set(LVGL_THREAD_SYNC_SIGNAL_FIXED_IMPORTS):
        raise AuditError("LVGL thread-sync-signal fixed provider boundary changed")

    aggregate = output_dir / "providers/lvgl-ambiq-lvgl-thread-sync-signal-aggregate.o"
    aggregate_exports = (
        LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS
        | LVGL_DRAW_DISPATCH_PROVIDER_SYMBOLS
        | LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS
    )
    command = [lld, "-r", "--gc-sections"]
    for symbol in sorted(aggregate_exports):
        command.extend(["-u", symbol])
    _run([
        *command, "-o", str(aggregate), str(provider),
        str(draw_dispatch_obj), str(global_storage_obj),
    ])
    aggregate_data = aggregate.read_bytes()
    if (
        _symbols(nm, aggregate, undefined=True)
        or _symbols(nm, aggregate, undefined=False) != set(aggregate_exports)
        or len(aggregate_data) != LVGL_THREAD_SYNC_SIGNAL_AGGREGATE_ARTIFACT["size"]
        or _sha256(aggregate_data) != LVGL_THREAD_SYNC_SIGNAL_AGGREGATE_ARTIFACT["sha256"]
    ):
        raise AuditError("LVGL thread-sync-signal aggregate closure changed")

    return provider, {
        "inputs": inputs,
        "authenticated_upstream": LVGL_THREAD_SYNC_SIGNAL_UPSTREAM_EVIDENCE,
        "target_source_artifact": {
            "path": source_obj.name, "size": len(source_data), "sha256": _sha256(source_data),
        },
        "artifact": {
            "path": provider.name, "size": len(provider_data), "sha256": _sha256(provider_data),
        },
        "abi_probe_artifact": {
            "path": abi_obj.name, "size": len(abi_data), "sha256": _sha256(abi_data),
        },
        "aggregate_link_artifact": {
            "path": aggregate.name, "size": len(aggregate_data),
            "sha256": _sha256(aggregate_data),
        },
        "required_exports": sorted(LVGL_THREAD_SYNC_SIGNAL_PROVIDER_SYMBOLS),
        "all_external_exports": sorted(_symbols(nm, provider, undefined=False)),
        "elf_undefined_symbols": [],
        "external_relocations": {},
        "fixed_address_imports": LVGL_THREAD_SYNC_SIGNAL_FIXED_IMPORTS,
        "fixed_address_import_count": len(LVGL_THREAD_SYNC_SIGNAL_FIXED_IMPORTS),
        "reviewed_runtime_dependencies": {
            "0x004420D1": "source-owned scheduler-port critical entry",
            "0x004420E9": "source-owned scheduler-port critical exit",
            "0x00455C49": "source-owned FreeRTOS xTaskGenericNotify entry",
        },
        "aggregate_elf_undefined_symbols": [],
        "closes_transitive_provider_dependency": "local_lvgl_draw_dispatch_provider",
        "warning_count": 0,
        "hostile_input_policy": (
            "null input fails before fixed calls; lazy-init, pending signal, waiter handoff, "
            "double-check race, ignored notify failure, and noncanonical initialized state are "
            "covered by the sanitizer host oracle"
        ),
        "source_admitted": True,
        "production_overlay_registered": False,
        "hardware_qualified": False,
        "qualification": (
            "exact task-notification-mode ABI and source behavior with source-owned fixed calls; "
            "live scheduler, critical nesting, TCB lifetime, RAM, collision, paired wait, and "
            "wakeup behavior remain unqualified"
        ),
    }


def _direct_provider(symbol: str) -> tuple[str, str]:
    if symbol in HAL_SYMBOLS:
        return "apollo510-nema-hal", "private G2 bare-metal/CMSIS-FreeRTOS port or admitted ABI adapter"
    if symbol.startswith("lv_ambiq_"):
        return "ambiq-gpu-patch", PUBLIC_ARTIFACTS["gpu_patch_archive"]["path"]
    if symbol.startswith("nema_vg_"):
        return "nemavg", PUBLIC_ARTIFACTS["nema_archive"]["path"]
    return "nemagfx", PUBLIC_ARTIFACTS["nema_archive"]["path"]


def _missing_family(symbol: str) -> tuple[str, str]:
    if symbol in HAL_SYMBOLS:
        detail = (
            "the scoped Apollo510 FreeRTOS HAL does not define this required out-of-line ABI; "
            "an exact G2 provider or authenticated ABI adapter is unavailable"
        )
        return "apollo510-nema-hal", detail
    if symbol.startswith("am_hal_"):
        return (
            "apollo510-hal",
            "atomic G2 admission of the exact Apollo510 Ambiq HAL implementation and configuration",
        )
    if symbol.startswith("xQueue"):
        return (
            "freertos-kernel",
            "atomic G2 admission of the exact configured FreeRTOS queue/semaphore implementation",
        )
    if symbol == "utf8_codepoint_size":
        return (
            "gpu-patch-private-helper",
            "private gpu_patch/ambiq_nema_extension.c helper or final section-GC proof",
        )
    if symbol.startswith("lv_"):
        return "lvgl-core", "atomic production link of the checked LVGL 9.3-development source closure"
    return "target-runtime", "admitted Cortex-M55 C/compiler-runtime/libm provider"


def _missing_ledger(
    consumers: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    rows = []
    for symbol in EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS:
        family, unavailable = _missing_family(symbol)
        owners = list(consumers.get(symbol, []))
        owners.extend(
            {
                "object": obj,
                "relocation_count": count,
                "relocation_types": {"authenticated-public-archive-relocations": count},
            }
            for obj, count in ARCHIVE_CONSUMERS.get(symbol, ())
        )
        owners.extend(
            {
                "object": obj,
                "relocation_count": count,
                "relocation_types": {relocation_type: count},
            }
            for obj, count, relocation_type in EVB_HAL_CONSUMERS.get(symbol, ())
        )
        owners.extend(
            {
                "object": obj,
                "relocation_count": count,
                "relocation_types": {relocation_type: count},
            }
            for obj, count, relocation_type in BUFFER_HELPER_CONSUMERS.get(symbol, ())
        )
        if not owners:
            raise AuditError(f"maximal residual symbol lacks a pinned consumer: {symbol}")
        rows.append({
            "symbol": symbol,
            "api_family": family,
            "consumer_objects": sorted(owners, key=lambda row: row["object"]),
            "retained_stock_provider_bytes": STOCK_PROVIDER_BYTES.get(symbol),
            "exact_unavailable_input": unavailable,
            "provider_admitted": False,
        })
    return rows


def _resolve_sdk_component(sdk_root: Path) -> Path:
    nested = sdk_root / "components/graphics/NemaGFX_SDK"
    if nested.is_dir():
        return nested
    if sdk_root.name == "NemaGFX_SDK" and sdk_root.is_dir():
        return sdk_root
    raise AuditError("--sdk-root must be AmbiqSuite root or NemaGFX_SDK directory")


def _audit_artifact(component: Path, metadata: dict[str, Any]) -> Path:
    path = component / metadata["path"]
    data = path.read_bytes()
    if (
        len(data) != metadata["size"]
        or _sha256(data) != metadata["sha256"]
        or _git_blob(data) != metadata["git_blob_sha1"]
    ):
        raise AuditError(f"public Ambiq artifact identity changed: {metadata['path']}")
    return path


def _audit_evb_inputs(evb_root: Path) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for name in ("source", "sys_defs", "freertos_config", "makefile"):
        metadata = EVB_EVIDENCE[name]
        path = evb_root / metadata["path"]
        data = path.read_bytes()
        if (
            len(data) != metadata["size"]
            or _sha256(data) != metadata["sha256"]
            or _git_blob(data) != metadata["git_blob_sha1"]
        ):
            raise AuditError(f"scoped Apollo510-EVB input identity changed: {metadata['path']}")
        observed[name] = {
            "path": metadata["path"],
            "size": len(data),
            "sha256": _sha256(data),
            "git_blob_sha1": _git_blob(data),
        }
    repository = evb_root.parents[2]
    head = _run(["git", "-C", str(repository), "rev-parse", "HEAD"]).strip()
    origin = _run(["git", "-C", str(repository), "remote", "get-url", "origin"]).strip()
    source = str(evb_root / EVB_EVIDENCE["source"]["path"])
    introduced = _run([
        "git", "-C", str(repository), "log", "--diff-filter=A", "--format=%H", "--", source,
    ]).splitlines()
    if (
        head != EVB_EVIDENCE["local_repository_commit"]
        or origin != EVB_EVIDENCE["repository_origin"]
        or not introduced
        or introduced[-1] != EVB_EVIDENCE["source_introducing_commit"]
    ):
        raise AuditError("scoped Apollo510-EVB private commit/origin boundary changed")
    return observed


def _compile_evb_hal(
    builder, evb_root: Path, output_dir: Path, clang: str, nm: str, objdump: str,
) -> tuple[Path, dict[str, Any]]:
    inputs = _audit_evb_inputs(evb_root)
    sdk = evb_root / "ThirdParty/ApolloSDK"
    nema = sdk / "third_party/ThinkSi/NemaGFX_SDK"
    freertos = sdk / "third_party/FreeRTOSv10.5.1/Source"
    stubs = output_dir / "evb-stubs"
    builder._write_stubs(stubs)
    source = evb_root / EVB_EVIDENCE["source"]["path"]
    obj = output_dir / "apollo510_evb_nema_hal.o"
    include_dirs = (
        evb_root / "Application/Source",
        sdk,
        sdk / "devices",
        sdk / "mcu/apollo510",
        sdk / "mcu/apollo510/hal",
        sdk / "utils",
        sdk / "CMSIS/ARM/Include",
        sdk / "CMSIS/AmbiqMicro/Include",
        sdk / "third_party/ThinkSi/config/apollo510_nemagfx",
        nema / "common/mem",
        nema / "include/tsi/common",
        nema / "include/tsi/NemaGFX",
        nema / "include/tsi/NemaDC",
        nema / "include/tsi/NemaVG",
        nema / "NemaGFX/Nema",
        nema / "NemaDC",
        freertos / "include",
        freertos / "portable/GCC/AMapollo5",
        stubs,
    )
    flags = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-std=gnu11", "-O2",
        "-Wall", "-Wno-missing-field-initializers", "-Wno-unused-but-set-variable",
        "-Werror", "-fno-common", "-ffunction-sections",
        "-fdata-sections", "-ffreestanding", "-fno-builtin", "-fomit-frame-pointer",
        "-fshort-enums", f"-ffile-prefix-map={evb_root}=/openCFW/scoped/Apollo510-EVB",
        "-DPART_apollo510", "-DAM_PART_APOLLO510", "-DAM_PACKAGE_BGA", "-Dgcc",
        "-DAM_FREERTOS", "-DPLATFORM=apollo510_nemagfx",
        "-DNEMA_PLATFORM=apollo510_nemagfx", "-DVMEM_SIZE=0x20000",
        "-DUSE_TSI_MALLOC", "-DMAX_PENDING_CL=100",
        "-DWAIT_IRQ_BINARY_SEMAPHORE=1",
        *[f"-I{path}" for path in include_dirs],
    ]
    output = _run([*flags, "-c", str(source), "-o", str(obj)], cwd=evb_root)
    if "warning:" in output:
        raise AuditError("warning in scoped Apollo510-EVB Nema HAL compile:\n" + output)
    defined = _symbols(nm, obj, undefined=False)
    undefined = _symbols(nm, obj, undefined=True)
    expected_defined_hal = set(HAL_SYMBOLS) - {
        "nema_buffer_invalidate", "nema_buffer_is_within_pool",
    }
    if defined & set(HAL_SYMBOLS) != expected_defined_hal:
        raise AuditError("scoped Apollo510-EVB Nema HAL defined-symbol boundary changed")
    relocations = _relocations(objdump, obj, undefined)
    expected_relocations: dict[str, dict[str, int]] = {}
    for symbol, rows in EVB_HAL_CONSUMERS.items():
        for _owner, count, relocation_type in rows:
            types = expected_relocations.setdefault(symbol, {})
            types[relocation_type] = types.get(relocation_type, 0) + count
    observed_relocations = {
        symbol: relocations.get(symbol, {}) for symbol in EVB_HAL_CONSUMERS
    }
    if observed_relocations != expected_relocations:
        raise AuditError("scoped Apollo510-EVB Nema HAL relocation graph changed")
    data = obj.read_bytes()
    return obj, {
        "inputs": inputs,
        "artifact": {"path": obj.name, "size": len(data), "sha256": _sha256(data)},
        "compiler_target": "arm-none-eabi/cortex-m55/thumb/hard-float/short-enums/gnu11",
        "defined_required_nema_hal_symbols": sorted(expected_defined_hal),
        "missing_required_nema_hal_symbols": [
            "nema_buffer_invalidate", "nema_buffer_is_within_pool",
        ],
        "undefined_symbols": sorted(undefined),
        "residual_relocation_graph_verified": True,
        "warning_count": 0,
    }


def _archive_defined_symbols(nm: str, archive: Path) -> set[str]:
    return _symbols(nm, archive, undefined=False)


def _public_link(
    component: Path, output_dir: Path, objects: list[Path], direct_nema: list[str],
    nm: str, objdump: str, lld: str,
) -> dict[str, Any]:
    paths = {name: _audit_artifact(component, metadata) for name, metadata in PUBLIC_ARTIFACTS.items()}
    nema_defined = _archive_defined_symbols(nm, paths["nema_archive"])
    patch_defined = _archive_defined_symbols(nm, paths["gpu_patch_archive"])
    direct_set = set(direct_nema)
    resolved_nema = sorted(direct_set & nema_defined)
    resolved_patch = sorted(direct_set & patch_defined)
    direct_hal = sorted(direct_set - nema_defined - patch_defined)
    if len(resolved_nema) != 82 or len(resolved_patch) != 6 or set(direct_hal) != {
        "nema_buffer_create_pool", "nema_buffer_destroy", "nema_buffer_flush",
        "nema_buffer_invalidate", "nema_buffer_is_within_pool", "nema_get_last_cl_id",
        "nema_get_last_submission_id", "nemagfx_power_control",
    }:
        raise AuditError("authenticated public archive direct-provider closure changed")

    partial = output_dir / "lvgl-ambiq-nema-public-partial.o"
    map_path = output_dir / "lvgl-ambiq-nema-public-partial.map"
    _run([
        lld, "-r", f"-Map={map_path}", "-o", str(partial),
        *[str(path) for path in objects],
        str(paths["nema_archive"]), str(paths["gpu_patch_archive"]),
    ])
    residual = sorted(_symbols(nm, partial, undefined=True))
    if residual != list(EXPECTED_PUBLIC_RESIDUAL_SYMBOLS):
        raise AuditError("authenticated public archive residual set changed")
    map_text = map_path.read_text(encoding="utf-8")
    selected_nema = sorted(set(re.findall(
        r"lib_nema_apollo5x_nemagfx\.a\(([^)]+)\)", map_text
    )))
    selected_patch = sorted(set(re.findall(r"gpu_patch\.a\(([^)]+)\)", map_text)))
    if selected_nema != sorted(SELECTED_NEMA_MEMBERS) or selected_patch != ["ambiq_nema_extension.o"]:
        raise AuditError("authenticated public archive member selection changed")

    # Re-derive every pinned transitive archive relocation count.
    observed: dict[str, dict[str, int]] = {}
    for archive in (paths["nema_archive"], paths["gpu_patch_archive"]):
        current_member: str | None = None
        for line in _run([objdump, "-r", str(archive)]).splitlines():
            member = re.match(r".*\(([^()]+\.o)\):\s+file format", line)
            if member is not None:
                current_member = member.group(1)
                continue
            relocation = re.match(r"^\s*[0-9a-fA-F]+\s+R_ARM_\S+\s+(\S+)", line)
            if (
                relocation is None or current_member is None
                or current_member not in set(SELECTED_NEMA_MEMBERS) | {"ambiq_nema_extension.o"}
                or relocation.group(1) not in ARCHIVE_CONSUMERS
            ):
                continue
            counts = observed.setdefault(relocation.group(1), {})
            counts[current_member] = counts.get(current_member, 0) + 1
    expected = {
        symbol: {obj: count for obj, count in rows}
        for symbol, rows in ARCHIVE_CONSUMERS.items()
    }
    if observed != expected:
        raise AuditError("authenticated public archive residual relocation graph changed")

    data = partial.read_bytes()
    return {
        "performed": True,
        "artifact": {"path": partial.name, "size": len(data), "sha256": _sha256(data)},
        "direct_requirements_resolved": len(resolved_nema) + len(resolved_patch),
        "nemagfx_nemavg_direct_symbols": len(resolved_nema),
        "gpu_patch_direct_symbols": len(resolved_patch),
        "direct_hal_symbols_unresolved": direct_hal,
        "selected_nema_members": selected_nema,
        "selected_gpu_patch_members": selected_patch,
        "residual_symbol_count": len(residual),
        "residual_symbol_digest": _digest(residual),
        "residual_relocation_graph_verified": True,
        "production_admitted": False,
    }


def _evb_link(
    component: Path, output_dir: Path, objects: list[Path], direct_nema: list[str],
    evb_obj: Path,
    helper_obj: Path, platform_obj: Path, freertos_obj: Path, lvgl_core_obj: Path,
    lvgl_stateless_obj: Path, target_runtime_obj: Path, math_obj: Path,
    math_dp_obj: Path,
    lvgl_mutex_obj: Path, lvgl_heap_array_obj: Path,
    lvgl_draw_buf_lifecycle_obj: Path, lvgl_global_storage_obj: Path,
    lvgl_freetype_event_obj: Path, lvgl_draw_buf_shape_obj: Path,
    lvgl_font_fmt_obj: Path, lvgl_vector_destroy_obj: Path, lvgl_draw_unit_obj: Path,
    lvgl_draw_dispatch_obj: Path, lvgl_thread_sync_signal_obj: Path,
    nm: str, lld: str,
) -> dict[str, Any]:
    nema_archive = _audit_artifact(component, PUBLIC_ARTIFACTS["nema_archive"])
    gpu_patch = _audit_artifact(component, PUBLIC_ARTIFACTS["gpu_patch_archive"])
    partial = output_dir / "lvgl-ambiq-nema-evb-maximal-partial.o"
    map_path = output_dir / "lvgl-ambiq-nema-evb-maximal-partial.map"
    gc_roots = sorted({symbol for obj in objects for symbol in _symbols(nm, obj, undefined=False)})
    if (
        gc_roots != list(EXPECTED_BACKEND_GC_ROOTS)
        or _digest(gc_roots) != EXPECTED_BACKEND_GC_ROOT_DIGEST
    ):
        raise AuditError("compiled Ambiq backend section-GC root set changed")
    command = [lld, "-r", "--gc-sections", f"-Map={map_path}"]
    for symbol in gc_roots:
        command.extend(["-u", symbol])
    _run([*command, "-o", str(partial),
        *[str(path) for path in objects], str(nema_archive), str(gpu_patch),
        str(evb_obj), str(helper_obj), str(platform_obj), str(freertos_obj),
        str(lvgl_core_obj), str(lvgl_stateless_obj), str(target_runtime_obj), str(math_obj),
        str(math_dp_obj),
        str(lvgl_mutex_obj),
        str(lvgl_heap_array_obj),
        str(lvgl_draw_buf_lifecycle_obj),
        str(lvgl_global_storage_obj),
        str(lvgl_freetype_event_obj),
        str(lvgl_draw_buf_shape_obj),
        str(lvgl_font_fmt_obj),
        str(lvgl_vector_destroy_obj),
        str(lvgl_draw_unit_obj),
        str(lvgl_draw_dispatch_obj),
        str(lvgl_thread_sync_signal_obj),
    ])
    residual = sorted(_symbols(nm, partial, undefined=True))
    if residual != list(EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS):
        raise AuditError("scoped Apollo510-EVB maximal residual set changed")
    remaining_hal = sorted(set(residual) & set(HAL_SYMBOLS))
    if remaining_hal:
        raise AuditError("scoped Apollo510-EVB maximal Nema HAL boundary changed")
    defined = _symbols(nm, partial, undefined=False)
    if set(direct_nema) - defined:
        raise AuditError("section-GC removed a directly required Nema/GPU symbol")
    if "lv_ambiq_get_glyph" in defined or "utf8_codepoint_size" in residual:
        raise AuditError("unreferenced GPU glyph/UTF-8 section-GC boundary changed")
    data = partial.read_bytes()
    return {
        "performed": True,
        "artifact": {"path": partial.name, "size": len(data), "sha256": _sha256(data)},
        "residual_symbol_count": len(residual),
        "residual_symbol_digest": _digest(residual),
        "remaining_nema_hal_symbols": remaining_hal,
        "remaining_nema_hal_symbol_count": len(remaining_hal),
        "section_gc": {
            "enabled": True,
            "root_policy": "all 39 externally visible functions from the exact 15 local backend objects",
            "root_symbols": gc_roots,
            "root_symbol_count": len(gc_roots),
            "root_symbol_digest": _digest(gc_roots),
            "direct_nema_symbols_retained": len(direct_nema),
            "elided_unreferenced_exports": ["lv_ambiq_get_glyph"],
            "elided_unreferenced_imports": ["utf8_codepoint_size"],
        },
        "source_origin_qualification": (
            "scoped sibling private-repository evidence; not authenticated to the public Ambiq commit"
        ),
        "semantic_platform_qualified": False,
        "qualification": (
            "symbol/relocation closure only; the EVB allocator configuration does not establish "
            "the authenticated G2 heap-descriptor semantics used by the local helpers"
        ),
        "production_admitted": False,
    }


def audit(
    *, sdk_root: Path | None = None, output_dir: Path | None = None,
    clang: str | None = None, evb_root: Path | None = None,
) -> dict[str, Any]:
    if evb_root is not None and sdk_root is None:
        raise AuditError("--evb-root requires --sdk-root for the authenticated public archives")
    _validate_static_boundary()
    builder = _load_builder()
    try:
        source_report = builder.audit_inputs()
    except builder.BuildError as exc:
        raise AuditError(str(exc)) from exc
    candidates = _candidate_inventory()
    clang = clang or os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
    if clang is None:
        raise AuditError("Cortex-M55 compile requires clang")
    nm = _tool(builder, "llvm-nm")
    objdump = _tool(builder, "llvm-objdump")
    lld = _tool(builder, "ld.lld")
    objcopy = _sibling_tool(nm, "llvm-objcopy")

    managed_temp = None
    if output_dir is None:
        managed_temp = tempfile.TemporaryDirectory(prefix="opencfw-lvgl-nema-audit-")
        build_dir = Path(managed_temp.name)
    else:
        build_dir = output_dir
    try:
        rows, consumers, direct_nema = _compile_local_objects(
            builder, build_dir, clang, nm, objdump
        )
        helper_obj, helper_compile = _compile_buffer_helpers(
            builder, build_dir, clang, nm, objdump
        )
        platform_obj, platform_compile = _compile_platform_provider(
            build_dir, clang, nm, objdump, lld
        )
        freertos_obj, freertos_compile = _compile_freertos_queue_provider(
            build_dir, clang, nm, objdump, lld
        )
        lvgl_core_obj, lvgl_core_compile = _compile_lvgl_core_provider(
            builder, build_dir, clang, nm, objdump, lld
        )
        lvgl_stateless_obj, lvgl_stateless_compile = _compile_lvgl_stateless_provider(
            builder, build_dir, clang, nm, objdump, lld
        )
        target_runtime_obj, target_runtime_compile = _compile_target_runtime_provider(
            build_dir, clang, nm, objdump, lld
        )
        math_obj, math_compile = _compile_math_provider(
            build_dir, clang, nm, objdump, lld, objcopy
        )
        math_dp_obj, math_dp_compile = _compile_math_dp_provider(
            build_dir, clang, nm, objdump, lld, objcopy
        )
        lvgl_mutex_obj, lvgl_mutex_compile = _compile_lvgl_mutex_provider(
            builder, build_dir, clang, nm, objdump, lld
        )
        lvgl_heap_array_obj, lvgl_heap_array_compile = _compile_lvgl_heap_array_provider(
            builder, build_dir, clang, nm, objdump, lld
        )
        lvgl_draw_buf_lifecycle_obj, lvgl_draw_buf_lifecycle_compile = (
            _compile_lvgl_draw_buf_lifecycle_provider(
                builder, build_dir, lvgl_heap_array_obj, clang, nm, objdump, lld
            )
        )
        lvgl_global_storage_obj, lvgl_global_storage_compile = (
            _compile_lvgl_global_storage_provider(
                builder, build_dir, clang, nm, objdump, lld
            )
        )
        lvgl_freetype_event_obj, lvgl_freetype_event_compile = (
            _compile_lvgl_freetype_event_provider(
                builder, build_dir, lvgl_global_storage_obj, clang, nm, objdump, lld
            )
        )
        lvgl_draw_buf_shape_obj, lvgl_draw_buf_shape_compile = (
            _compile_lvgl_draw_buf_shape_provider(
                builder, build_dir, lvgl_heap_array_obj, lvgl_global_storage_obj,
                clang, nm, objdump, lld
            )
        )
        lvgl_font_fmt_obj, lvgl_font_fmt_compile = _compile_lvgl_font_fmt_provider(
            builder, build_dir, clang, nm, objdump, lld
        )
        lvgl_vector_destroy_obj, lvgl_vector_destroy_compile = (
            _compile_lvgl_vector_destroy_provider(
                builder, build_dir, lvgl_heap_array_obj, clang, nm, objdump, lld
            )
        )
        lvgl_draw_unit_obj, lvgl_draw_unit_compile = _compile_lvgl_draw_unit_provider(
            builder, build_dir, lvgl_heap_array_obj, lvgl_global_storage_obj,
            clang, nm, objdump, lld
        )
        lvgl_draw_dispatch_obj, lvgl_draw_dispatch_compile = (
            _compile_lvgl_draw_dispatch_provider(
                builder, build_dir, lvgl_global_storage_obj, clang, nm, objdump, lld
            )
        )
        lvgl_thread_sync_signal_obj, lvgl_thread_sync_signal_compile = (
            _compile_lvgl_thread_sync_signal_provider(
                builder, build_dir, lvgl_global_storage_obj, lvgl_draw_dispatch_obj,
                clang, nm, objdump, lld
            )
        )
        for symbol in LVGL_CORE_PROVIDER_SYMBOLS:
            owners = consumers.get(symbol, [])
            if not owners or any(
                row.get("relocation_count", 0) <= 0
                or set(row.get("relocation_types", {})) != {"R_ARM_THM_CALL"}
                for row in owners
            ):
                raise AuditError(
                    f"LVGL core provider consumer relocation boundary changed: {symbol}"
                )
        for symbol in LVGL_STATELESS_PROVIDER_SYMBOLS:
            owners = consumers.get(symbol, [])
            if not owners or any(
                row.get("relocation_count", 0) <= 0
                or not set(row.get("relocation_types", {}))
                or not set(row.get("relocation_types", {})).issubset(
                    {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                )
                for row in owners
            ):
                raise AuditError(
                    f"LVGL stateless provider consumer relocation boundary changed: {symbol}"
                )
        target_runtime_consumers: dict[str, list[dict[str, Any]]] = {}
        for symbol in TARGET_RUNTIME_PROVIDER_SYMBOLS:
            owners = list(consumers.get(symbol, []))
            owners.extend(
                {
                    "object": obj,
                    "relocation_count": count,
                    "relocation_types": {"authenticated-public-archive-relocations": count},
                }
                for obj, count in ARCHIVE_CONSUMERS.get(symbol, ())
            )
            owners.sort(key=lambda row: row["object"])
            if not owners or any(row.get("relocation_count", 0) <= 0 for row in owners):
                raise AuditError(
                    f"target runtime provider consumer relocation boundary changed: {symbol}"
                )
            target_runtime_consumers[symbol] = owners
        math_consumers: dict[str, list[dict[str, Any]]] = {}
        for symbol in MATH_PROVIDER_SYMBOLS:
            owners = list(consumers.get(symbol, []))
            owners.extend(
                {
                    "object": obj,
                    "relocation_count": count,
                    "relocation_types": {"authenticated-public-archive-relocations": count},
                }
                for obj, count in ARCHIVE_CONSUMERS.get(symbol, ())
            )
            owners.sort(key=lambda row: row["object"])
            if not owners or any(row.get("relocation_count", 0) <= 0 for row in owners):
                raise AuditError(
                    f"math provider consumer relocation boundary changed: {symbol}"
                )
            math_consumers[symbol] = owners
        math_dp_consumers: dict[str, list[dict[str, Any]]] = {}
        for symbol in MATH_DP_PROVIDER_SYMBOLS:
            owners = list(consumers.get(symbol, []))
            owners.extend(
                {
                    "object": obj,
                    "relocation_count": count,
                    "relocation_types": {"authenticated-public-archive-relocations": count},
                }
                for obj, count in ARCHIVE_CONSUMERS.get(symbol, ())
            )
            owners.sort(key=lambda row: row["object"])
            if not owners or any(row.get("relocation_count", 0) <= 0 for row in owners):
                raise AuditError(
                    f"FPv5-D16 math provider consumer relocation boundary changed: {symbol}"
                )
            math_dp_consumers[symbol] = owners
        for symbol in LVGL_MUTEX_PROVIDER_SYMBOLS:
            owners = consumers.get(symbol, [])
            if not owners or any(
                row.get("relocation_count", 0) <= 0
                or not set(row.get("relocation_types", {})).issubset(
                    {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                )
                for row in owners
            ):
                raise AuditError(
                    f"LVGL mutex provider consumer relocation boundary changed: {symbol}"
                )
        for symbol in LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS:
            owners = consumers.get(symbol, [])
            if not owners or any(
                row.get("relocation_count", 0) <= 0
                or not set(row.get("relocation_types", {})).issubset(
                    {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                )
                for row in owners
            ):
                raise AuditError(
                    f"LVGL heap/array provider consumer relocation boundary changed: {symbol}"
                )
        for symbol in LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS:
            owners = consumers.get(symbol, [])
            if not owners or any(
                row.get("relocation_count", 0) <= 0
                or not set(row.get("relocation_types", {})).issubset(
                    {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                )
                for row in owners
            ):
                raise AuditError(
                    f"LVGL draw-buffer lifecycle consumer boundary changed: {symbol}"
                )
        global_storage_consumers = consumers.get("lv_global", [])
        if global_storage_consumers != [{
            "object": "lv_draw_ambiq_buffer.o",
            "relocation_count": 2,
            "relocation_types": {
                "R_ARM_THM_MOVT_ABS": 1,
                "R_ARM_THM_MOVW_ABS_NC": 1,
            },
        }]:
            raise AuditError("LVGL global-storage consumer boundary changed")
        freetype_event_consumers = consumers.get("lv_freetype_outline_add_event", [])
        if freetype_event_consumers != [{
            "object": "lv_draw_ambiq_vector_font.o",
            "relocation_count": 1,
            "relocation_types": {"R_ARM_THM_JUMP24": 1},
        }]:
            raise AuditError("LVGL FreeType-event consumer boundary changed")
        expected_shape_consumers = {
            "lv_draw_buf_create": [
                {"object": "lv_draw_ambiq.o", "relocation_count": 1,
                 "relocation_types": {"R_ARM_THM_CALL": 1}},
                {"object": "lv_draw_ambiq_box_shadow.o", "relocation_count": 1,
                 "relocation_types": {"R_ARM_THM_CALL": 1}},
                {"object": "lv_draw_ambiq_private.o", "relocation_count": 1,
                 "relocation_types": {"R_ARM_THM_CALL": 1}},
            ],
            "lv_draw_buf_reshape": [
                {"object": "lv_draw_ambiq_private.o", "relocation_count": 1,
                 "relocation_types": {"R_ARM_THM_CALL": 1}},
            ],
        }
        draw_buf_shape_consumers = {
            symbol: consumers.get(symbol, [])
            for symbol in sorted(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS)
        }
        if draw_buf_shape_consumers != expected_shape_consumers:
            raise AuditError("LVGL draw-buffer shape consumer boundary changed")
        font_fmt_consumers = consumers.get("lv_font_get_bitmap_fmt_txt", [])
        if font_fmt_consumers != [{
            "object": "lv_draw_ambiq_letter.o",
            "relocation_count": 2,
            "relocation_types": {
                "R_ARM_THM_MOVT_ABS": 1,
                "R_ARM_THM_MOVW_ABS_NC": 1,
            },
        }]:
            raise AuditError("LVGL font-format consumer boundary changed")
        vector_destroy_consumers = consumers.get("lv_vector_for_each_destroy_tasks", [])
        if vector_destroy_consumers != [{
            "object": "lv_draw_ambiq_vector.o",
            "relocation_count": 1,
            "relocation_types": {"R_ARM_THM_CALL": 1},
        }]:
            raise AuditError("LVGL vector-destroy consumer boundary changed")
        draw_unit_consumers = consumers.get("lv_draw_create_unit", [])
        if draw_unit_consumers != [{
            "object": "lv_draw_ambiq.o",
            "relocation_count": 1,
            "relocation_types": {"R_ARM_THM_CALL": 1},
        }]:
            raise AuditError("LVGL draw-unit consumer boundary changed")
        draw_dispatch_consumers = consumers.get("lv_draw_dispatch_request", [])
        if draw_dispatch_consumers != [{
            "object": "lv_draw_ambiq.o",
            "relocation_count": 1,
            "relocation_types": {"R_ARM_THM_CALL": 1},
        }]:
            raise AuditError("LVGL draw-dispatch consumer boundary changed")
        thread_sync_signal_consumers = consumers.get("lv_thread_sync_signal", [])
        if thread_sync_signal_consumers != [{
            "object": "lv_draw_ambiq.o",
            "relocation_count": 2,
            "relocation_types": {"R_ARM_THM_CALL": 2},
        }]:
            raise AuditError("LVGL thread-sync-signal consumer boundary changed")
        helper_symbols = {"nema_buffer_invalidate", "nema_buffer_is_within_pool"}
        direct_ledger = []
        for symbol in direct_nema:
            family, provider = _direct_provider(symbol)
            direct_ledger.append({
                "symbol": symbol,
                "api_family": family,
                "consumer_objects": consumers[symbol],
                "expected_provider": provider,
                "provider_available_in_workspace": symbol in helper_symbols,
                "local_provider_target_compiled": symbol in helper_symbols,
                "provider_admitted": False,
            })
        missing = _missing_ledger(consumers)
        report: dict[str, Any] = {
            "schema_version": 1,
            "component": "G2 LVGL Ambiq/Nema atomic-link readiness",
            "analysis_mode": "offline source/object audit; no hardware or flash operation",
            "source_boundary": {
                "ambiq_subtree_git_tree_sha1": source_report["source"]["subtree_git_tree_sha1"],
                "compiled_exact_ambiq_translation_units": 14,
                "cache_free_radius_provider_units": 1,
                "vector_compatibility_patch": {
                    "path": VECTOR_PATCH.relative_to(ROOT).as_posix(),
                    "sha256": VECTOR_PATCH_SHA256,
                    "effect": "const-preserving local matrix copies for LVGL 9.3/Nema matrix ABI",
                },
            },
            "workspace_implementation_inventory": {
                "candidate_files": candidates,
                "files": len(candidates),
                "bytes": sum(row["size"] for row in candidates),
                "digest": EXPECTED_CANDIDATE_DIGEST,
                "qualification": "clean-room candidates use open_cfw names/ports and are not production ABI providers",
            },
            "scoped_source_inventory": {
                "search_boundary": [
                    "this repository via rg --files",
                    "/Users/kalani/Repo via rg --files",
                    "exact AmbiqSuite and Apollo510-EVB roots named by pinned provenance",
                ],
                "broad_home_scan_performed": False,
                "current_repository_implementation_archives": False,
                "scoped_sibling_ambiqsuite_archives_observed": True,
                "scoped_sibling_apollo510_evb_hal_observed": True,
                "precise_observed_paths": [
                    "evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5/components/graphics/NemaGFX_SDK/libraries/lib_nema_apollo5x_nemagfx.a",
                    "evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5/components/graphics/NemaGFX_SDK/extensions/gpu_patch.a",
                    "evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5/components/graphics/NemaGFX_SDK/port/nema_hal.c",
                    EVB_EVIDENCE["scoped_root_hint"] + "/" + EVB_EVIDENCE["source"]["path"],
                ],
                "evidence_limit": (
                    "the EVB source is tracked only in the scoped sibling private repository; "
                    "no public upstream commit for that exact source was authenticated"
                ),
            },
            "local_target_compile": {
                "compiler": _run([clang, "--version"]).splitlines()[0],
                "target": "arm-none-eabi/cortex-m55/thumb/short-enums/gnu11",
                "objects": rows,
                "object_count": len(rows),
                "object_bytes": sum(row["size"] for row in rows),
                "warning_count": 0,
                "aggregate_unresolved_symbol_count": EXPECTED_AGGREGATE_UNRESOLVED["count"],
                "aggregate_unresolved_symbol_digest": EXPECTED_AGGREGATE_UNRESOLVED["digest"],
            },
            "local_buffer_helper_provider": helper_compile,
            "local_apollo_hal_provider": platform_compile,
            "local_freertos_queue_provider": freertos_compile,
            "local_lvgl_core_provider": {
                **lvgl_core_compile,
                "closed_consumer_relocations": {
                    symbol: consumers[symbol] for symbol in sorted(LVGL_CORE_PROVIDER_SYMBOLS)
                },
                "closed_residual_symbol_count": len(LVGL_CORE_PROVIDER_SYMBOLS),
            },
            "local_lvgl_stateless_provider": {
                **lvgl_stateless_compile,
                "closed_consumer_relocations": {
                    symbol: consumers[symbol]
                    for symbol in sorted(LVGL_STATELESS_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for symbol in LVGL_STATELESS_PROVIDER_SYMBOLS
                    for row in consumers[symbol]
                ),
                "closed_residual_symbol_count": len(LVGL_STATELESS_PROVIDER_SYMBOLS),
            },
            "local_target_runtime_provider": {
                **target_runtime_compile,
                "closed_consumer_relocations": {
                    symbol: target_runtime_consumers[symbol]
                    for symbol in sorted(TARGET_RUNTIME_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for rows in target_runtime_consumers.values()
                    for row in rows
                ),
                "closed_residual_symbol_count": len(TARGET_RUNTIME_PROVIDER_SYMBOLS),
            },
            "local_math_provider": {
                **math_compile,
                "closed_consumer_relocations": {
                    symbol: math_consumers[symbol]
                    for symbol in sorted(MATH_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for rows in math_consumers.values()
                    for row in rows
                ),
                "closed_residual_symbol_count": len(MATH_PROVIDER_SYMBOLS),
            },
            "local_math_dp_provider": {
                **math_dp_compile,
                "closed_consumer_relocations": {
                    symbol: math_dp_consumers[symbol]
                    for symbol in sorted(MATH_DP_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for rows in math_dp_consumers.values()
                    for row in rows
                ),
                "closed_residual_symbol_count": len(MATH_DP_PROVIDER_SYMBOLS),
            },
            "local_lvgl_mutex_provider": {
                **lvgl_mutex_compile,
                "closed_consumer_relocations": {
                    symbol: consumers[symbol]
                    for symbol in sorted(LVGL_MUTEX_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for symbol in LVGL_MUTEX_PROVIDER_SYMBOLS
                    for row in consumers[symbol]
                ),
                "closed_residual_symbol_count": len(LVGL_MUTEX_PROVIDER_SYMBOLS),
            },
            "local_lvgl_heap_array_provider": {
                **lvgl_heap_array_compile,
                "closed_consumer_relocations": {
                    symbol: consumers[symbol]
                    for symbol in sorted(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for symbol in LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS
                    for row in consumers[symbol]
                ),
                "closed_residual_symbol_count": len(LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS),
            },
            "local_lvgl_draw_buf_lifecycle_provider": {
                **lvgl_draw_buf_lifecycle_compile,
                "closed_consumer_relocations": {
                    symbol: consumers[symbol]
                    for symbol in sorted(LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS)
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for symbol in LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS
                    for row in consumers[symbol]
                ),
                "closed_residual_symbol_count": len(
                    LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS
                ),
            },
            "local_lvgl_global_storage_provider": {
                **lvgl_global_storage_compile,
                "closed_consumer_relocations": {
                    "lv_global": global_storage_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in global_storage_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_freetype_event_provider": {
                **lvgl_freetype_event_compile,
                "closed_consumer_relocations": {
                    "lv_freetype_outline_add_event": freetype_event_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in freetype_event_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_draw_buf_shape_provider": {
                **lvgl_draw_buf_shape_compile,
                "closed_consumer_relocations": draw_buf_shape_consumers,
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"]
                    for rows in draw_buf_shape_consumers.values()
                    for row in rows
                ),
                "closed_residual_symbol_count": len(LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS),
            },
            "local_lvgl_font_fmt_provider": {
                **lvgl_font_fmt_compile,
                "closed_consumer_relocations": {
                    "lv_font_get_bitmap_fmt_txt": font_fmt_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in font_fmt_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_vector_destroy_provider": {
                **lvgl_vector_destroy_compile,
                "closed_consumer_relocations": {
                    "lv_vector_for_each_destroy_tasks": vector_destroy_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in vector_destroy_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_draw_unit_provider": {
                **lvgl_draw_unit_compile,
                "closed_consumer_relocations": {
                    "lv_draw_create_unit": draw_unit_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in draw_unit_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_draw_dispatch_provider": {
                **lvgl_draw_dispatch_compile,
                "dependency_admitted": True,
                "transitive_dependency_provider": "local_lvgl_thread_sync_signal_provider",
                "closed_consumer_relocations": {
                    "lv_draw_dispatch_request": draw_dispatch_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in draw_dispatch_consumers
                ),
                "closed_residual_symbol_count": 1,
            },
            "local_lvgl_thread_sync_signal_provider": {
                **lvgl_thread_sync_signal_compile,
                "closed_consumer_relocations": {
                    "lv_thread_sync_signal": thread_sync_signal_consumers,
                },
                "closed_consumer_relocation_count": sum(
                    row["relocation_count"] for row in thread_sync_signal_consumers
                ),
                "closed_transitive_relocation_count": 2,
                "closed_residual_symbol_count": 1,
            },
            "public_provider_boundary": {
                "repository": "https://github.com/AmbiqMicro/ambiqhal_ambiq.git",
                "commit": PUBLIC_COMMIT,
                "artifacts": PUBLIC_ARTIFACTS,
                "archives_present_in_current_repository": False,
                "archives_present_in_scoped_sibling_sdk": True,
                "public_hal_qualification": (
                    "implementation source exists but is Zephyr-specific, differs from the stock "
                    "CMSIS-FreeRTOS port, and omits nema_wait_irq_brk"
                ),
                "binary_license_review_required": True,
            },
            "direct_nema_requirement_ledger": direct_ledger,
            "direct_nema_requirement_count": len(direct_ledger),
            "direct_nema_requirement_digest": EXPECTED_DIRECT_NEMA["digest"],
            "maximal_public_archive_closure": {
                "performed": False,
                "expected_direct_symbols_resolved": 88,
                "expected_selected_nema_members": list(SELECTED_NEMA_MEMBERS),
                "expected_selected_gpu_patch_members": ["ambiq_nema_extension.o"],
                "expected_residual_symbol_count": len(EXPECTED_PUBLIC_RESIDUAL_SYMBOLS),
                "expected_residual_symbol_digest": EXPECTED_PUBLIC_RESIDUAL_DIGEST,
            },
            "maximal_scoped_candidate_closure": {
                "performed": False,
                "evidence": EVB_EVIDENCE,
                "expected_residual_symbol_count": len(EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS),
                "expected_residual_symbol_digest": EXPECTED_MAXIMAL_RESIDUAL_DIGEST,
                "expected_remaining_nema_hal_symbols": [],
                "expected_section_gc_root_count": len(EXPECTED_BACKEND_GC_ROOTS),
                "expected_section_gc_root_digest": EXPECTED_BACKEND_GC_ROOT_DIGEST,
                "expected_section_gc_elided_imports": ["utf8_codepoint_size"],
                "qualification": (
                    "compile/link evidence only; private sibling origin and non-G2 platform configuration"
                ),
            },
            "missing_provider_ledger": missing,
            "missing_provider_count": len(missing),
            "missing_nema_hal_provider_count": 0,
            "production_admission": {
                "ready": False,
                "hardware_qualified": False,
                "blockers": [
                    "the exact pinned public implementation archives are available only in the scoped sibling SDK and are not imported into this repository",
                    "the two local buffer helpers are target-compiled but not registered in a production overlay",
                    "the EVB HAL is not authenticated to a public upstream commit and its memory, IRQ, power, and FreeRTOS configuration is not the G2 configuration",
                    "the isolated Apollo510 HAL provider is source-closed but not routed, and its fixed G2 calls/MMIO remain hardware-unqualified",
                    "the isolated FreeRTOS queue provider is source-closed but not routed, and its fixed G2 scheduler/RAM dependencies remain runtime-unqualified",
                    "the isolated 14-symbol LVGL core utility and 11-symbol stateless providers are source-closed but not routed; cache callbacks remain caller-owned and hardware-unqualified",
                    "the isolated five-symbol memory/AEABI conversion provider is source-closed but not routed; production libc/compiler-runtime collision review is incomplete",
                    "the isolated five-symbol musl math provider is source-closed but not routed; target floating-point status/rounding and symbol-collision review remain incomplete",
                    "the isolated four-symbol FPv5-D16 musl math provider is source-closed but not routed; optional-DP FPU state/rounding and symbol-collision review remain incomplete",
                    "the isolated four-symbol LVGL mutex provider is source-closed but not routed; scheduler state, heap, critical nesting, RAM placement, and concurrency remain runtime-unqualified",
                    "the isolated five-symbol LVGL heap/array provider is source-closed but not routed; live heap locking/RAM placement and provider collision remain runtime-unqualified",
                    "the isolated LVGL draw-buffer destroy provider is source-closed but not routed; descriptor callback ownership and live heap behavior remain runtime-unqualified",
                    "the isolated LVGL global-storage object is source-closed but not routed; live linker ownership, collision, initializer ordering, and handler contents remain runtime-unqualified",
                    "the isolated LVGL FreeType outline-event setter is source-closed but not routed; live context allocation/lifetime, initializer order, collision, and concurrency remain runtime-unqualified",
                    "the isolated LVGL draw-buffer create/reshape provider is source-closed but not routed; live Ambiq handler initialization, Nema pools, heap/global collisions, RAM, and concurrency remain runtime-unqualified",
                    "the isolated LVGL font-format provider is source-closed but not routed; source bitmap extent and live draw-buffer cache callback ownership remain caller/runtime-unqualified",
                    "the isolated LVGL vector-task destroy provider is source-closed but not routed; list extent, callback mutation, and live allocator ownership remain runtime-unqualified",
                    "the isolated LVGL draw-unit create provider is source-closed but not routed; global initialization, list/count ownership, serialization, collision, RAM placement, and allocation lifetime remain runtime-unqualified",
                    "the isolated LVGL draw-dispatch request provider and its exact task-notification-mode lv_thread_sync_signal dependency are source-closed but not routed; sync initialization, scheduler/TCB state, critical nesting, RAM, collision, paired wait, and concurrency remain runtime-unqualified",
                    "the remaining FreeRTOS thread/sync OSAL, draw scheduling/layer, decoder/cache, logging, and global-state initializer closure is incomplete; the stock FreeRTOS task-notification selection remains unrecovered",
                    "binary notice/license policy and GNU-versus-stock-IAR compatibility require explicit admission",
                    "Apollo510 command-list, IRQ, cache, power-retention, antialiasing, and output evidence is unavailable",
                ],
            },
        }
        if sdk_root is not None:
            component = _resolve_sdk_component(sdk_root)
            object_paths = [
                build_dir / "objects" / (Path(unit).stem + ".o")
                for unit in ALL_AMBIQ_UNITS
            ]
            report["maximal_public_archive_closure"] = _public_link(
                component, build_dir, object_paths, direct_nema, nm, objdump, lld,
            )
            if evb_root is not None:
                evb_obj, evb_compile = _compile_evb_hal(
                    builder, evb_root, build_dir, clang, nm, objdump,
                )
                maximal = _evb_link(
                    component, build_dir, object_paths, direct_nema, evb_obj, helper_obj,
                    platform_obj, freertos_obj, lvgl_core_obj, lvgl_stateless_obj,
                    target_runtime_obj, math_obj, math_dp_obj, lvgl_mutex_obj,
                    lvgl_heap_array_obj, lvgl_draw_buf_lifecycle_obj,
                    lvgl_global_storage_obj, lvgl_freetype_event_obj,
                    lvgl_draw_buf_shape_obj, lvgl_font_fmt_obj,
                    lvgl_vector_destroy_obj, lvgl_draw_unit_obj,
                    lvgl_draw_dispatch_obj, lvgl_thread_sync_signal_obj, nm, lld
                )
                maximal["compile"] = evb_compile
                report["maximal_scoped_candidate_closure"] = maximal
        if output_dir is not None:
            (output_dir / "link-audit-report.json").write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        return report
    finally:
        if managed_temp is not None:
            managed_temp.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path)
    parser.add_argument("--evb-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--clang")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(
            sdk_root=args.sdk_root, evb_root=args.evb_root,
            output_dir=args.output_dir, clang=args.clang,
        )
        if args.write_manifest is not None:
            if args.sdk_root is not None or args.evb_root is not None:
                raise AuditError("checked readiness manifest must not depend on an external SDK path")
            args.write_manifest.parent.mkdir(parents=True, exist_ok=True)
            args.write_manifest.write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    except (OSError, AuditError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 LVGL/Ambiq/Nema atomic-link readiness: FAIL-CLOSED")
        print(f"  local Cortex-M55 objects: {report['local_target_compile']['object_count']}")
        print(f"  direct Nema requirements: {report['direct_nema_requirement_count']}")
        print(f"  residual providers: {report['missing_provider_count']}")
        print("  hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

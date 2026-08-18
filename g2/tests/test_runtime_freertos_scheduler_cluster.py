from __future__ import annotations

import copy
import hashlib
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

RUN_BASE = 0x0043_8000
PREAMBLE_BYTES = 32
OVERLAY_RUNTIME_BASE = 0x0079_4324
OVERLAY_LIMIT = 0x007F_0000
OFFICIAL_SIZE = 3_523_396
OFFICIAL_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"

PORT_YIELD = "open_cfw_freertos_port_yield"
PORT_ENTER = "open_cfw_freertos_port_enter_critical"
PORT_EXIT = "open_cfw_freertos_port_exit_critical"
RESET_NEXT = "open_cfw_freertos_task_reset_next_task_unblock_time"
INCREMENT_TICK = "open_cfw_freertos_task_increment_tick"
RESUME_ALL = "open_cfw_freertos_task_resume_all"
MASK = "ulSetInterruptMask"
CLEAR_MASK = "vClearInterruptMask"

FUNCTIONS = [
    PORT_YIELD,
    PORT_ENTER,
    PORT_EXIT,
    RESET_NEXT,
    INCREMENT_TICK,
    RESUME_ALL,
]

SOURCES = {
    PORT_YIELD: (
        "research/candidates/freertos_scheduler_port_trio.c",
        5_437,
        "8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e",
    ),
    PORT_ENTER: (
        "research/candidates/freertos_scheduler_port_trio.c",
        5_437,
        "8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e",
    ),
    PORT_EXIT: (
        "research/candidates/freertos_scheduler_port_trio.c",
        5_437,
        "8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e",
    ),
    RESET_NEXT: (
        "components/shared/freertos/"
        "runtime_freertos_reset_next_task_unblock_time.c",
        2_544,
        "afaf50d27bf7fc9a106e15b9318d36f0afa6ff6ba35619269297f41e3ce867b8",
    ),
    INCREMENT_TICK: (
        "components/shared/freertos/runtime_freertos_task_increment_tick.c",
        6_927,
        "0fb59aba7fb8b8ab1f7fc2b2cc5095f9bb05334770d44790a42b33ad80369cb2",
    ),
    RESUME_ALL: (
        "components/shared/freertos/runtime_freertos_task_resume_all.c",
        6_262,
        "455b29e4eaec27451ad5ed24953583291659201b7fbd2da5c330f6e9da081dd5",
    ),
}

STOCK = {
    PORT_YIELD: (
        "replace_freertos_port_yield",
        0x0044_20BC,
        0x0044_20D0,
        "dd981b3e9196c6fd87bb79719c94628c89e564d5728b3fdd1ff08c397eccb397",
    ),
    PORT_ENTER: (
        "replace_freertos_port_enter_critical",
        0x0044_20D0,
        0x0044_20E8,
        "5809638c22f928d2b32cd21cc9b92a292fad24cd8b8008de4ad92b9faeaba0d4",
    ),
    PORT_EXIT: (
        "replace_freertos_port_exit_critical",
        0x0044_20E8,
        0x0044_2114,
        "bfd3ddb76c61ad634a3f58ed203260da3834895b646c9dffada546f9dc9d2a31",
    ),
    RESET_NEXT: (
        "replace_freertos_task_reset_next_task_unblock_time",
        0x0045_5876,
        0x0045_589C,
        "a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598",
    ),
    INCREMENT_TICK: (
        "replace_freertos_task_increment_tick",
        0x0045_504C,
        0x0045_519E,
        "438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050",
    ),
    RESUME_ALL: (
        "replace_freertos_task_resume_all",
        0x0045_4DCC,
        0x0045_4EFE,
        "548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09",
    ),
}

POST_SCHEDULER_STOCK = {
    "open_cfw_g2_easylogger_async_record_build_single_owner": (
        0x0044_8D4E,
        0x0044_8DD2,
        "9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17",
    ),
    "open_cfw_g2_easylogger_async_submit": (
        0x0044_AA80,
        0x0044_AA98,
        "787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356",
    ),
    "open_cfw_easylogger_output": (
        0x0043_D574,
        0x0043_D976,
        "d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c",
    ),
}

POST_SCHEDULER_SOURCE_PATCHES = (
    "open_cfw_freertos_queue_give_from_isr",
    "open_cfw_freertos_task_remove_from_event_list",
    "open_cfw_freertos_task_check_free_stack_space",
    "open_cfw_freertos_task_check_for_timeout",
    "open_cfw_freertos_queue_generic_reset",
    "open_cfw_freertos_task_remove_from_unordered_event_list",
    "open_cfw_easylogger_hexdump",
    "open_cfw_easylogger_hexdump_raw_submit",
    "open_cfw_g2_easylogger_async_record_build_level_less_single_owner",
    "open_cfw_freertos_cli_get_parameter",
    "open_cfw_freertos_cli_console_task",
    "open_cfw_freertos_queue_messages_waiting",
    "open_cfw_freertos_queue_messages_waiting_from_isr",
    "open_cfw_nanopb_decode_varint",
    "open_cfw_littlefs_file_size_private",
    "open_cfw_freertos_task_lists_initialize",
    "open_cfw_cmbacktrace_get_cur_thread_name",
    "open_cfw_littlefs_file_rewind_private",
    "open_cfw_littlefs_tag_type2",
    "open_cfw_littlefs_tag_isvalid",
    "open_cfw_littlefs_tag_type1",
    "open_cfw_littlefs_tag_type3",
    "open_cfw_littlefs_tag_id",
    "open_cfw_littlefs_tag_size",
    "open_cfw_nanopb_buf_read",
    "open_cfw_nanopb_readbyte",
    "open_cfw_nanopb_istream_from_buffer",
    "open_cfw_nanopb_decode_varint32_eof",
    "open_cfw_nanopb_decode_varint32",
    "open_cfw_littlefs_tag_chunk",
    "open_cfw_nanopb_make_string_substream",
    "open_cfw_nanopb_decode_bool",
    "open_cfw_nanopb_dec_bool",
    "open_cfw_nanopb_decode_tag",
    "open_cfw_nanopb_field_iter_begin",
    "open_cfw_nanopb_field_iter_begin_extension",
    "open_cfw_nanopb_field_iter_next",
    "open_cfw_nanopb_field_iter_find",
    "open_cfw_nanopb_field_iter_find_extension",
    "open_cfw_nanopb_field_iter_begin_const",
    "open_cfw_nanopb_field_iter_begin_extension_const",
    "open_cfw_nanopb_default_field_callback",
    "open_cfw_nanopb_decode_pointer_field",
    "open_cfw_ring_buffer_is_empty",
    "open_cfw_ring_buffer_is_full",
    "open_cfw_ring_buffer_init",
    "open_cfw_ring_buffer_queue",
    "open_cfw_ring_buffer_queue_arr",
    "open_cfw_ring_buffer_dequeue",
    "open_cfw_ring_buffer_dequeue_arr",
    "open_cfw_iar_memcpy_void",
    "open_cfw_iar_memcpy_aligned_void",
    "open_cfw_iar_memmove_void",
    "open_cfw_iar_sqrtf",
    "open_cfw_iar_domain_error",
    "open_cfw_iar_range_error",
    "open_cfw_iar_errno_address",
    "open_cfw_copy_advertised_name_pair_suffix",
    "open_cfw_cmsis_irq_context",
    "open_cfw_cmsis_kernel_get_tick_count",
    "open_cfw_cmsis_thread_get_id",
    "open_cfw_cmsis_message_queue_get_capacity",
    "open_cfw_cmsis_semaphore_get_count",
    "open_cfw_cmsis_message_queue_get_count",
    "open_cfw_cmsis_message_queue_delete",
    "open_cfw_cmsis_thread_yield",
    "open_cfw_cmsis_kernel_get_state",
    "open_cfw_cmsis_mutex_delete",
    "open_cfw_cmsis_timer_is_running",
    "open_cfw_cmsis_mutex_release",
    "open_cfw_cmsis_semaphore_release",
    "open_cfw_cmsis_timer_start",
    "open_cfw_cmsis_timer_stop",
    "open_cfw_cmsis_timer_delete",
    "open_cfw_cmsis_event_flags_new",
    "open_cfw_cmsis_event_flags_set",
    "open_cfw_cmsis_event_flags_clear",
    "open_cfw_cmsis_event_flags_wait",
    "open_cfw_cmsis_timer_new",
    "open_cfw_cmsis_memory_pool_new",
    "open_cfw_freertos_queue_copy_data_from_queue",
    "open_cfw_freertos_queue_receive_from_isr",
    "open_cfw_cmsis_memory_pool_create_block",
    "open_cfw_cmsis_memory_pool_alloc_block",
    "open_cfw_cmsis_memory_pool_free_block",
    "open_cfw_cmsis_memory_pool_free",
    "open_cfw_freertos_task_priority_disinherit",
    "open_cfw_freertos_queue_copy_data_to_queue",
    "open_cfw_freertos_queue_generic_send_from_isr",
    "open_cfw_cmsis_message_queue_put",
    "open_cfw_freertos_task_add_current_to_delayed_list",
    "open_cfw_freertos_task_place_on_event_list",
    "open_cfw_freertos_queue_unlock",
    "open_cfw_freertos_queue_receive",
    "open_cfw_cmsis_message_queue_get",
    "open_cfw_freertos_task_delay",
    "open_cfw_cmsis_delay",
    "open_cfw_freertos_task_priority_set",
    "open_cfw_cmsis_thread_set_priority",
    "open_cfw_freertos_task_get_state",
    "open_cfw_freertos_task_delete_tcb",
    "open_cfw_freertos_task_delete",
    "open_cfw_cmsis_thread_terminate",
    "open_cfw_freertos_task_notify_wait",
    "open_cfw_freertos_task_notify",
    "open_cfw_freertos_task_notify_from_isr",
    "open_cfw_cmsis_thread_flags_set",
    "open_cfw_cmsis_thread_flags_wait",
    "open_cfw_cmsis_thread_new",
    "open_cfw_cmsis_kernel_initialize",
    "open_cfw_cmsis_kernel_start",
    "TF_Init",
    "TF_Accept",
    "TF_AddTypeListener",
    "TF_Respond",
    "TF_Query_Multipart",
    "TF_Multipart_Payload",
    "TF_Multipart_Close",
    "TF_Tick",
)

COMMON_RELOCATIONS = {
    PORT_YIELD: [],
    PORT_ENTER: [(0x02, "R_ARM_THM_CALL", MASK)],
    PORT_EXIT: [
        (0x1C, "R_ARM_THM_JUMP24", CLEAR_MASK),
        (0x22, "R_ARM_THM_CALL", MASK),
    ],
    RESET_NEXT: [],
    RESUME_ALL: [
        (0x12, "R_ARM_THM_CALL", PORT_ENTER),
        (0x22, "R_ARM_THM_CALL", PORT_EXIT),
        (0x2E, "R_ARM_THM_CALL", MASK),
        (0xEE, "R_ARM_THM_CALL", RESET_NEXT),
        (0xFC, "R_ARM_THM_CALL", INCREMENT_TICK),
        (0x11C, "R_ARM_THM_CALL", PORT_YIELD),
    ],
}

PROFILES = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0",
        "overlay_size": 142_986,
        "overlay_sha256": (
            "1b0fc521cc8964da6525b7f7dce99060d07f5671f0038f37bcd998a56422a49f"
        ),
        "component_size": 3_666_382,
        "component_sha256": (
            "a4552ff210b6af33b7826a6b9aaefa6e01c7e6e976c9a852498570ededcf058f"
        ),
        "package_size": 4_444_468,
        "package_sha256": (
            "53b240df100153c5453697fb3ce8ac66663ca82484a1d69f88345e1e7c3cd3c6"
        ),
        "package_accounting": (143_245, 98_824, 4_202_399),
        # Builder reports exclude isolated/non-emitted registry categories.
        "function_count": 779,
        "patch_count": 720,
        "tail_growth": 782,
        "lz4_tail_growth": 1_758,
        "next_closure_tail_growth": 492,
        "timeout_tail_growth": 138,
        "easylogger_tail_growth": 2_094,
        "semaphore_tail_growth": 624,
        "reset_unordered_tail_growth": 388,
        "nanopb_close_tail_growth": 36,
        "littlefs_rewind_tail_growth": 16,
        "nanopb_fixed32_tail_growth": 50,
        "littlefs_tag_type2_tail_growth": 12,
        "littlefs_tag_chunk_tail_growth": 8,
        "littlefs_tag_type3_tail_growth": 8,
        "littlefs_tag_id_tail_growth": 8,
        "littlefs_tag_size_tail_growth": 8,
        "nanopb_fixed64_tail_growth": 30,
        "nanopb_read_tail_growth": 158,
        "nanopb_svarint_tail_growth": 54,
        "nanopb_varint32_tail_growth": 252,
        "nanopb_skip_string_tail_growth": 36,
        # Net tail trimmed by the rollback build: every post-milestone
        # admission retained in the legacy overlay that is not itemized
        # above (the nanopb decode wave and the iar float-exponent trio are
        # absent from the rollback overlay and are therefore not deleted
        # here).
        "current_rollback_net_tail_growth": 16_360,
        "later_tail_growth": 20_184,
        "legacy_reset_unordered_tail_growth": 388,
        # Active rollback build from the current production registry.
        "legacy_semaphore_layout": {
            "overlay_size": 138_106,
            "overlay_sha256": (
                "49aa7131b5f5c07c34441569beab22a5"
                "2e98cca2376788b0a35ace6428afb6ae"
            ),
            "component_size": 3_661_502,
            "component_sha256": (
                "cb13440dd758eac612d5d55b1ce37cdf"
                "bad251f656841975109dba475069e4b4"
            ),
            "function_count": 749,
            "patch_count": 691,
            "function_offset": 106_572,
            "function_size": 596,
            "patch_payload_offset": 40_036,
            "patch_target_address": 0x007A_E370,
            "patch_branch_hex": "6cf394bb",
            "patch_sha256": (
                "bf1b65c3cd7e87a4fc37e7482d6c9d73"
                "eb364f3a3aa6e53f0b5612b4b56c182d"
            ),
        },
        "legacy_primary_spans": {
            "open_cfw_evenhub_mode2_decompress": {
                "offset": 12_484,
                "size": 30,
            },
            "open_cfw_lz4_decompress_safe": {
                "offset": 12_516,
                "size": 696,
            },
        },
        "legacy_patch_replacements": {
            "open_cfw_evenhub_mode2_decompress": {
                "payload_offset": 691_244,
                "size": 40,
                "branch_hex": "b6f2ecbb",
            },
            "open_cfw_lz4_decompress_safe": {
                "payload_offset": 1_143_640,
                "size": 30,
                "branch_hex": "48f266b8",
            },
        },
        # Historical pre-cluster milestone.  The rollback still recreates its
        # exact 3,639,438-byte extent; the byte stream moved to
        # a2fa6903… after the campaign authenticated the previously
        # placeholder-pinned `open_cfw_transport_crc32_update` overlay byte
        # at offset 0 and clang 2100.3.30.1 refreshed retained copy-site
        # replacements.  The sha below authenticates the current fail-closed
        # reconstruction; the original recording was
        # 4e0a7f0604081d056f5e9c94142db2a4db5e3419f6e8a0cc98f82794eb37823c.
        "prior_component_size": 3_639_438,
        "prior_component_sha256": (
            "a2fa6903cf91b32ac843aab99c2dd5ba3bd4228f9d63d85c30504a88a09279c8"
        ),
        "provider_addresses": {MASK: 0x007A_FF08, CLEAR_MASK: 0x007A_FF1E},
        "accounting": {
            "source_owned_bytes": 143_168,
            "source_owned_in_place_bytes": 182,
            "generated_patch_site_bytes": 98_402,
            "replaced_stock_function_bytes": 98_580,
            "opaque_base_bytes": 3_424_328,
            "generated_wrapper_bytes": 32,
        },
        "leaves": {
            PORT_YIELD: (
                115_444, 0x007B_0618, 24, 2,
                "105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235",
                "105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235",
                "6ef3acba",
                "1d55099a69bdf6496ff9d396d08da47f010bb4e9e0a73d4c92b1def23cced7e8",
            ),
            PORT_ENTER: (
                115_468, 0x007B_0630, 30, 0,
                "c382397165ed32cec367e2ceb68f6af24ce748937cef326d825270741bafab7f",
                "18797972899b42b6333a1353a25820dc720a5e477d0275b3fb4f039cbc0ef158",
                "6ef3aeba",
                "eb5dfeebd33b75b7ea3bca9a69c1cd5735986fe73fd0d4921232cf94b6967de9",
            ),
            PORT_EXIT: (
                115_500, 0x007B_0650, 54, 2,
                "da3e6da9d2363ba358f7b6bbbd098a7cd7483807ec37477497db2d31632e4e9c",
                "1106c10ba143e84c0335da8c09658f88594e4578a8dfece201e73ee36f00900f",
                "6ef3b2ba",
                "5fe5effaeee03f15a59dcc3270d51ad891defcc094008e5e4d143550f0570d54",
            ),
            RESET_NEXT: (
                115_556, 0x007B_0688, 32, 2,
                "249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f",
                "249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f",
                "5af307bf",
                "154f3cce690424a0ea5293fc5af7f5a0170cc9d0e14fcb8ecaf0d1ec15586a7f",
            ),
            INCREMENT_TICK: (
                115_588, 0x007B_06A8, 344, 0,
                "1aec337b980ad1a9719f7bed519894ea3b7a8d2a0cecc239309a55729b40ecef",
                "453dd5addafa0fade84729e0f215668b067055eea7daf43cc089b9ee98e02888",
                "5bf32cbb",
                "bdd287666f3e2deda26222796d708ee60c86f5a9d4d437535a40340892155286",
            ),
            RESUME_ALL: (
                115_932, 0x007B_0800, 292, 0,
                "e608ef2a9725d183beb19220d7c864691b2affa85e64372cf62350d671badcdd",
                "8b8a8bde3a875d1b4f6b28d3aa0e4bedf2c80f80d0c0c380614e3e1a8c4216a3",
                "5bf318bd",
                "ce95bf86afb3cf055f642d98db1f9cde5d91a1b52f677b3d2c0044742b307881",
            ),
        },
        "tick_relocations": [
            (0x3C, "R_ARM_THM_CALL", MASK),
            (0x64, "R_ARM_THM_CALL", RESET_NEXT),
        ],
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "overlay_size": 144_266,
        "overlay_sha256": (
            "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9"
        ),
        "component_size": 3_667_662,
        "component_sha256": (
            "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6"
        ),
        "package_size": 4_446_156,
        "package_sha256": (
            "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3"
        ),
        "package_accounting": (145_147, 98_610, 4_202_399),
        "function_count": 664,
        "patch_count": 613,
        "tail_growth": 778,
        "lz4_tail_growth": 1_790,
        "next_closure_tail_growth": 492,
        "timeout_tail_growth": 138,
        "easylogger_tail_growth": 2_090,
        "semaphore_tail_growth": 622,
        "reset_unordered_tail_growth": 386,
        "nanopb_close_tail_growth": 36,
        "littlefs_rewind_tail_growth": 16,
        "nanopb_fixed32_tail_growth": 50,
        "littlefs_tag_type2_tail_growth": 12,
        "littlefs_tag_chunk_tail_growth": 8,
        "littlefs_tag_type3_tail_growth": 8,
        "littlefs_tag_id_tail_growth": 8,
        "littlefs_tag_size_tail_growth": 8,
        "nanopb_fixed64_tail_growth": 32,
        "nanopb_read_tail_growth": 160,
        "nanopb_svarint_tail_growth": 52,
        "nanopb_varint32_tail_growth": 252,
        "nanopb_skip_string_tail_growth": 36,
        "nanopb_varint32_patch_span": 256,
        "nanopb_skip_string_patch_span": 32,
        # Net tail retained by the active Linux rollback registry after the
        # removed read/svarint/skip-string closures are accounted for.
        "current_rollback_net_tail_growth": 208,
        "later_tail_growth": 2_834,
        "legacy_reset_unordered_tail_growth": 388,
        "legacy_semaphore_layout": {
            "overlay_size": 126_822,
            "overlay_sha256": (
                "3347ed7a8bfab677ebe7bb4dc4469a82"
                "20c80f0d44ebaab3d4882a9db0264338"
            ),
            "component_size": 3_650_218,
            "component_sha256": (
                "4f21a29b33633ce387a12ad55463bc86"
                "a2dff9dc43b4d528d317165fe326555b"
            ),
            "function_count": 660,
            "patch_count": 610,
            "function_offset": 107_124,
            "function_size": 606,
            "patch_payload_offset": 40_036,
            "patch_target_address": 0x007A_E598,
            "patch_branch_hex": "6cf3a8bc",
            "patch_sha256": (
                "48a52e283e718a6d27114540f47f20f1c"
                "8bbd85be025d1f5af12552521a2253d"
            ),
        },
        "legacy_primary_spans": {
            "open_cfw_evenhub_mode2_decompress": {
                "offset": 12_488,
                "size": 30,
            },
            "open_cfw_lz4_decompress_safe": {
                "offset": 12_520,
                "size": 650,
            },
        },
        "legacy_patch_replacements": {
            "open_cfw_evenhub_mode2_decompress": {
                "payload_offset": 691_244,
                "size": 40,
                "branch_hex": "b6f2eebb",
            },
            "open_cfw_lz4_decompress_safe": {
                "payload_offset": 1_143_640,
                "size": 30,
                "branch_hex": "48f268b8",
            },
        },
        "prior_component_size": 3_641_278,
        "prior_component_sha256": (
            "6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163"
        ),
        "provider_addresses": {MASK: 0x007B_054C, CLEAR_MASK: 0x007B_0562},
        "accounting": {
            "source_owned_bytes": 127_264,
            "source_owned_in_place_bytes": 182,
            "generated_patch_site_bytes": 86_914,
            "replaced_stock_function_bytes": 87_096,
            "opaque_base_bytes": 3_436_268,
            "generated_wrapper_bytes": 32,
        },
        "leaves": {
            PORT_YIELD: (
                117_276, 0x007B_0D40, 24, 2,
                "105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235",
                "105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235",
                "6ef340be",
                "690cd32bdefcd0df41370f85223cf083f470890522c8895a84bf4ecbe02160ab",
            ),
            PORT_ENTER: (
                117_300, 0x007B_0D58, 30, 0,
                "5b83770b60d27de697acae48b58eba3b27d55ab668c775c9d858c73f395877e4",
                "18797972899b42b6333a1353a25820dc720a5e477d0275b3fb4f039cbc0ef158",
                "6ef342be",
                "28592bb216a1816568710bca2954d9724d1ba9350452e146c0ad41b54b1f5f4b",
            ),
            PORT_EXIT: (
                117_332, 0x007B_0D78, 54, 2,
                "1e97f6015a84574113451a4da90c9bd1e22dbc2570f7b1db11ba9c0f6d9b5228",
                "1106c10ba143e84c0335da8c09658f88594e4578a8dfece201e73ee36f00900f",
                "6ef346be",
                "515877a3cd48e377e3435ed263c1a6514e964ffe47ccceb2f2f2864bbebe9572",
            ),
            RESET_NEXT: (
                117_388, 0x007B_0DB0, 32, 2,
                "249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f",
                "249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f",
                "5bf39bba",
                "3c5a648ae007a1d75497d98c5d8d0ff4ca0516d83a0b8a696f67bf7059b6e047",
            ),
            INCREMENT_TICK: (
                117_420, 0x007B_0DD0, 338, 0,
                "6fabcf5492fe4171cf7b27c225fc7a65730906cb9b57ca003c0539a4ddda3ea1",
                "889ae62e4116bbd1bd8c8db65612b779372dfe8a4f26e5c78e3a0828e1671c5a",
                "5bf3c0be",
                "3dcae69d5bb341f580867ffd3c4612834500b097e4caa9efe57703ed14e79cef",
            ),
            RESUME_ALL: (
                117_760, 0x007B_0F24, 292, 2,
                "43b18067bfa208746aff747013f4daf4d16f198474cc8891aebf4a0fedfc24d5",
                "7fb0e6bab36ed324d800362e1d1f85e29b8b7924e6cbe994600ebe998fe025a6",
                "5cf3aab8",
                "72eb44f51c4297cf241e9fa48d05ce2a9a9743f4dbbbfa5973c1cc0b8b11e380",
            ),
        },
        "tick_relocations": [
            (0x38, "R_ARM_THM_CALL", MASK),
            (0x60, "R_ARM_THM_CALL", RESET_NEXT),
        ],
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def artifact(report: dict, section: str) -> Path:
    return ROOT / report[section]["artifact"]


class RuntimeFreeRTOSSchedulerClusterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile_name = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE",
            "apple-clang" if sys.platform == "darwin" else "linux-clang",
        )
        if cls.profile_name not in PROFILES:
            raise AssertionError(
                f"unreviewed scheduler-cluster profile {cls.profile_name!r}"
            )
        cls.profile = PROFILES[cls.profile_name]
        cls.config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        cls.manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        cls.official = OFFICIAL.read_bytes()
        cls.application = cls.official[PREAMBLE_BYTES:]

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw
        cls.effective_manifest = open_cfw.load_manifest(CORE_SOURCE_MANIFEST)
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.reports = [
            apollo_overlay.build(
                root=ROOT,
                config_path=OVERLAY_CONFIG,
                output_dir=temporary / f"run-{index}",
                clang=cls.clang,
                toolchain_profile=cls.profile_name,
            )
            for index in (1, 2)
        ]
        cls.production = cls.reports[0]

        legacy_profile = (
            "legacy-apple-clang"
            if cls.profile_name == "apple-clang"
            else cls.profile_name
        )

        def load_legacy_config(_path: Path) -> dict:
            config = copy.deepcopy(cls.config)
            config["toolchain"]["flags"].append(
                "-DOPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE=1"
            )
            removed = {
                "open_cfw_freertos_queue_get_disinherit_priority_after_timeout",
                "open_cfw_freertos_queue_semaphore_take_upstream_candidate",
                "open_cfw_cmsis_memory_pool_alloc",
                "open_cfw_cmsis_mutex_acquire",
                "open_cfw_cmsis_semaphore_acquire",
                "open_cfw_nanopb_read",
                "open_cfw_nanopb_decode_svarint",
                "open_cfw_nanopb_skip_string",
                "open_cfw_nanopb_skip_field",
                "open_cfw_nanopb_skip_varint",
                "open_cfw_nanopb_close_string_substream",
                "open_cfw_nanopb_read_raw_value",
                "open_cfw_nanopb_dec_varint",
                "open_cfw_nanopb_dec_bytes",
                "open_cfw_nanopb_dec_string",
                "open_cfw_nanopb_dec_submessage",
                "open_cfw_nanopb_dec_fixed_length_bytes",
                "open_cfw_nanopb_decode_inner",
                "open_cfw_nanopb_decode_field",
                "open_cfw_nanopb_decode_basic_field",
                "open_cfw_nanopb_decode_static_field",
                "open_cfw_nanopb_decode_callback_field",
                "open_cfw_nanopb_decode_extension",
                "open_cfw_nanopb_decode_fixed32",
                "open_cfw_nanopb_decode_fixed64",
                "open_cfw_nanopb_default_extension_decoder",
                "open_cfw_nanopb_field_set_to_default",
                "open_cfw_nanopb_message_set_to_defaults",
            }
            config["functions"] = [
                function for function in config["functions"]
                if function not in removed
            ]
            insert_at = (
                config["functions"].index(
                    "open_cfw_freertos_queue_generic_send"
                )
                + 1
            )
            config["functions"].insert(
                insert_at,
                "open_cfw_freertos_queue_semaphore_take",
            )
            config["relocated_leaves"] = [
                leaf for leaf in config["relocated_leaves"]
                if leaf["function"] not in removed
            ]
            for patch in config["patch_sites"]:
                if patch.get("target_function") == (
                    "open_cfw_freertos_queue_semaphore_take_upstream_candidate"
                ):
                    patch["target_function"] = (
                        "open_cfw_freertos_queue_semaphore_take"
                    )
            config["patch_sites"] = [
                patch for patch in config["patch_sites"]
                if patch.get("target_function") not in removed
            ]
            if cls.profile_name == "apple-clang":
                config["toolchain_profiles"][legacy_profile] = {}
            return config

        original_load_config = apollo_overlay.load_config
        apollo_overlay.load_config = load_legacy_config
        try:
            cls.legacy_production = apollo_overlay.build(
                root=ROOT,
                config_path=OVERLAY_CONFIG,
                output_dir=temporary / "legacy-semaphore-layout",
                clang=cls.clang,
                toolchain_profile=legacy_profile,
                record_profile=True,
            )
        finally:
            apollo_overlay.load_config = original_load_config

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def profile_relocations(self, function: str):
        if function == INCREMENT_TICK:
            return self.profile["tick_relocations"]
        return COMMON_RELOCATIONS[function]

    def test_registration_order_source_pins_and_profile_contracts_are_exact(
        self,
    ) -> None:
        registered_functions = [
            function for function in self.config["functions"]
            if function in FUNCTIONS
        ]
        self.assertEqual(registered_functions, FUNCTIONS)
        self.assertEqual(
            [
                leaf["function"]
                for leaf in self.config["relocated_leaves"]
                if leaf["function"] in FUNCTIONS
            ],
            FUNCTIONS,
        )
        self.assertEqual(
            [
                patch["target_function"]
                for patch in self.config["patch_sites"]
                if patch["target_function"] in FUNCTIONS
            ],
            FUNCTIONS,
        )
        self.assertEqual(
            (len(self.config["functions"]), len(self.config["patch_sites"])),
            (783, 724),
        )

        for leaf in (
            item for item in self.config["relocated_leaves"]
            if item["function"] in FUNCTIONS
        ):
            function = leaf["function"]
            path, size, digest = SOURCES[function]
            with self.subTest(function=function):
                self.assertNotIn("profiles", leaf)
                self.assertEqual(
                    {
                        key: leaf["source"][key]
                        for key in ("path", "size", "sha256", "license", "upstream_commit")
                    },
                    {
                        "path": path,
                        "size": size,
                        "sha256": digest,
                        "license": "MIT",
                        "upstream_commit": UPSTREAM_COMMIT,
                    },
                )
                source = ROOT / path
                self.assertEqual(source.stat().st_size, size)
                self.assertEqual(sha256(source.read_bytes()), digest)

                effective = self.apollo_overlay.resolve_leaf_profile(
                    leaf,
                    self.profile_name,
                )
                (
                    offset,
                    _address,
                    output_size,
                    _padding,
                    relocated_sha,
                    unrelocated_sha,
                    _branch,
                    _replacement_sha,
                ) = self.profile["leaves"][function]
                self.assertEqual(
                    effective["expected"],
                    {
                        "size": output_size,
                        "sha256": relocated_sha,
                        "alignment": 4,
                        "offset": offset,
                        "unrelocated_sha256": unrelocated_sha,
                    },
                )
                self.assertEqual(
                    effective["relocations"],
                    [
                        {
                            "offset": relocation_offset,
                            "type": relocation_type,
                            "symbol": provider,
                            "target_function": provider,
                        }
                        for relocation_offset, relocation_type, provider
                        in self.profile_relocations(function)
                    ],
                )

    def test_all_stock_spans_and_complete_redirect_fills_are_authenticated(
        self,
    ) -> None:
        self.assertEqual(len(self.official), OFFICIAL_SIZE)
        self.assertEqual(sha256(self.official), OFFICIAL_SHA256)
        configured = {
            patch["target_function"]: patch
            for patch in self.config["patch_sites"]
            if patch["target_function"] in FUNCTIONS
        }
        reported = {
            patch["target_function"]: patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["target_function"] in FUNCTIONS
        }
        self.assertEqual(set(configured), set(FUNCTIONS))
        self.assertEqual(set(reported), set(FUNCTIONS))

        ranges = []
        for function in FUNCTIONS:
            name, start, end, stock_sha = STOCK[function]
            stock = self.application[start - RUN_BASE:end - RUN_BASE]
            target = self.profile["leaves"][function][1]
            branch_hex = self.profile["leaves"][function][6]
            replacement_sha = self.profile["leaves"][function][7]
            with self.subTest(function=function):
                self.assertEqual(len(stock), end - start)
                self.assertEqual(sha256(stock), stock_sha)
                self.assertEqual(
                    configured[function],
                    {
                        "name": name,
                        "runtime_address": start,
                        "expected_size": end - start,
                        "expected_sha256": stock_sha,
                        "branch": "b_w",
                        "target_function": function,
                    },
                )
                patch = reported[function]
                replacement = bytes.fromhex(patch["replacement_hex"])
                self.assertEqual(patch["target_address"], target)
                self.assertEqual(patch["payload_offset"], PREAMBLE_BYTES + start - RUN_BASE)
                self.assertEqual(len(replacement), end - start)
                self.assertEqual(replacement[:4].hex(), branch_hex)
                self.assertEqual(replacement[4:], b"\x00\xbf" * ((end - start - 4) // 2))
                self.assertEqual(sha256(replacement), replacement_sha)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        start,
                        replacement[:4],
                        link=False,
                    ),
                    target,
                )
            ranges.append((start, end, function))

        ranges.sort()
        self.assertEqual(sum(end - start for start, end, _ in ranges), 770)
        self.assertTrue(
            all(first[1] <= second[0] for first, second in zip(ranges, ranges[1:]))
        )

    def test_placements_named_dependencies_and_resolved_calls_are_exact(
        self,
    ) -> None:
        report_leaves = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] in FUNCTIONS
        }
        self.assertEqual(set(report_leaves), set(FUNCTIONS))
        functions = self.production["overlay"]["functions"]

        provider_addresses = dict(self.profile["provider_addresses"])
        provider_addresses.update(
            {
                function: values[1]
                for function, values in self.profile["leaves"].items()
            }
        )
        for provider, expected_address in provider_addresses.items():
            with self.subTest(provider=provider):
                self.assertIn(provider, functions)
                self.assertEqual(
                    OVERLAY_RUNTIME_BASE + functions[provider]["offset"],
                    expected_address,
                )

        leaf_ranges = []
        type_ids = {"R_ARM_THM_CALL": 10, "R_ARM_THM_JUMP24": 30}
        for function in FUNCTIONS:
            (
                offset,
                address,
                size,
                padding,
                relocated_sha,
                unrelocated_sha,
                _branch,
                _replacement_sha,
            ) = self.profile["leaves"][function]
            report = report_leaves[function]
            with self.subTest(function=function):
                self.assertEqual(
                    report["placement"],
                    {
                        "offset": offset,
                        "size": size,
                        "alignment": 4,
                        "padding_before": padding,
                        "runtime_address": address,
                        "runtime_address_hex": f"0x{address:08X}",
                    },
                )
                extraction = report["extraction"]
                self.assertEqual(
                    {
                        key: extraction[key]
                        for key in (
                            "function", "section", "runtime_address", "size",
                            "sha256", "unrelocated_sha256", "alignment",
                            "relocation_count",
                        )
                    },
                    {
                        "function": function,
                        "section": f".text.{function}",
                        "runtime_address": address,
                        "size": size,
                        "sha256": relocated_sha,
                        "unrelocated_sha256": unrelocated_sha,
                        "alignment": 4,
                        "relocation_count": len(self.profile_relocations(function)),
                    },
                )
                self.assertEqual(
                    [
                        {
                            key: relocation[key]
                            for key in (
                                "offset", "type", "type_id", "symbol",
                                "target_function", "runtime_address",
                                "target_address",
                            )
                        }
                        for relocation in extraction["relocations"]
                    ],
                    [
                        {
                            "offset": relocation_offset,
                            "type": relocation_type,
                            "type_id": type_ids[relocation_type],
                            "symbol": provider,
                            "target_function": provider,
                            "runtime_address": address + relocation_offset,
                            "target_address": provider_addresses[provider],
                        }
                        for relocation_offset, relocation_type, provider
                        in self.profile_relocations(function)
                    ],
                )
                for _relocation_offset, _relocation_type, provider in self.profile_relocations(function):
                    self.assertLess(
                        list(functions).index(provider),
                        list(functions).index(function),
                    )
            leaf_ranges.append((address, address + size, function))

        self.assertTrue(
            all(first[1] <= second[0] for first, second in zip(leaf_ranges, leaf_ranges[1:]))
        )
        final_end = leaf_ranges[-1][1]
        self.assertEqual(
            final_end,
            OVERLAY_RUNTIME_BASE
            + self.profile["overlay_size"]
            - self.profile["easylogger_tail_growth"]
            - self.profile["lz4_tail_growth"]
            - self.profile["next_closure_tail_growth"]
            - self.profile["timeout_tail_growth"]
            - self.profile["semaphore_tail_growth"]
            - self.profile["reset_unordered_tail_growth"]
            - self.profile["nanopb_close_tail_growth"]
            - self.profile["littlefs_rewind_tail_growth"]
            - self.profile["nanopb_fixed32_tail_growth"]
            - self.profile["littlefs_tag_type2_tail_growth"]
            - self.profile["littlefs_tag_chunk_tail_growth"]
            - self.profile["littlefs_tag_type3_tail_growth"]
            - self.profile.get("nanopb_varint32_tail_growth", 0)
            - self.profile.get("nanopb_skip_string_tail_growth", 0)
            - self.profile["littlefs_tag_id_tail_growth"]
            - self.profile["littlefs_tag_size_tail_growth"]
            - self.profile["nanopb_fixed64_tail_growth"]
            - self.profile["nanopb_read_tail_growth"]
            - self.profile["nanopb_svarint_tail_growth"]
            - self.profile["later_tail_growth"],
        )
        self.assertLessEqual(final_end, OVERLAY_LIMIT)
        self.assertEqual(OVERLAY_LIMIT - final_end, 259_804 if self.profile_name == "apple-clang" else 257_976)

    def test_component_accounting_equations_and_profile_pins_are_exact(
        self,
    ) -> None:
        expected_pins = (
            self.config["expected"]
            if self.profile_name == "apple-clang"
            else self.config["toolchain_profiles"][self.profile_name]["expected"]
        )
        component = self.production["component"]
        overlay = self.production["overlay"]
        accounting = self.profile["accounting"]
        self.assertEqual(
            self.production["toolchain"]["profile"],
            self.profile_name,
        )
        self.assertTrue(
            self.production["toolchain"]["version"].startswith(
                self.profile["version"]
            )
        )
        self.assertEqual(expected_pins["overlay_size"], self.profile["overlay_size"])
        self.assertEqual(expected_pins["component_size"], self.profile["component_size"])
        self.assertEqual(
            expected_pins["overlay_sha256"],
            self.profile["overlay_sha256"],
        )
        self.assertEqual(
            expected_pins["component_sha256"],
            self.profile["component_sha256"],
        )
        self.assertEqual(
            (overlay["size"], overlay["sha256"]),
            (expected_pins["overlay_size"], expected_pins["overlay_sha256"]),
        )
        self.assertEqual(
            (component["size"], component["sha256"]),
            (expected_pins["component_size"], expected_pins["component_sha256"]),
        )
        self.assertEqual(
            (len(overlay["functions"]), len(overlay["patched_sites"])),
            (self.profile["function_count"], self.profile["patch_count"]),
        )
        self.assertEqual(
            {key: component[key] for key in accounting},
            accounting,
        )
        if self.profile_name == "linux-clang":
            self.assertEqual(
                accounting["source_owned_bytes"],
                126_976
                + self.profile["nanopb_varint32_tail_growth"]
                + self.profile["nanopb_skip_string_tail_growth"],
            )
            self.assertEqual(
                accounting["generated_patch_site_bytes"],
                86_626
                + self.profile["nanopb_varint32_patch_span"]
                + self.profile["nanopb_skip_string_patch_span"],
            )
            self.assertEqual(
                accounting["replaced_stock_function_bytes"],
                86_808
                + self.profile["nanopb_varint32_patch_span"]
                + self.profile["nanopb_skip_string_patch_span"],
            )
            self.assertEqual(
                accounting["opaque_base_bytes"],
                3_436_556
                - self.profile["nanopb_varint32_patch_span"]
                - self.profile["nanopb_skip_string_patch_span"],
            )
        self.assertEqual(
            component["size"],
            accounting["opaque_base_bytes"]
            + accounting["source_owned_bytes"]
            + accounting["generated_patch_site_bytes"]
            + accounting["generated_wrapper_bytes"],
        )
        # The builder counts the 4-byte `bl` rewrite site
        # (`rewrite_g2_advertised_name_suffix`) in generated_patch_site_bytes
        # but not in replaced_stock_function_bytes, which only covers
        # b_w/copy replacements.
        bl_rewrite_bytes = 4
        self.assertEqual(
            accounting["replaced_stock_function_bytes"]
            + bl_rewrite_bytes,
            accounting["generated_patch_site_bytes"]
            + accounting["source_owned_in_place_bytes"],
        )
        self.assertEqual(
            accounting["opaque_base_bytes"]
            + accounting["replaced_stock_function_bytes"]
            + bl_rewrite_bytes
            + accounting["generated_wrapper_bytes"],
            OFFICIAL_SIZE,
        )

    def test_manifest_is_gap_free_and_owns_each_stock_and_source_span(self) -> None:
        main = self.manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertEqual(len(regions), 1256)
        self.assertEqual(main["source_appended_boundary"], OFFICIAL_SIZE)
        ordered = sorted(regions, key=lambda region: region["file_offset"])
        self.assertEqual(ordered[0]["file_offset"], 0)
        self.assertEqual(
            [region["file_offset"] + region["size"] for region in ordered[:-1]],
            [region["file_offset"] for region in ordered[1:]],
        )
        self.assertEqual(
            ordered[-1]["file_offset"] + ordered[-1]["size"],
            main["provider"]["size"],
        )

        for function in FUNCTIONS:
            _name, start, end, _stock_sha = STOCK[function]
            address = PROFILES["apple-clang"]["leaves"][function][1]
            size = PROFILES["apple-clang"]["leaves"][function][2]
            with self.subTest(function=function):
                replacement_regions = [
                        region
                        for region in regions
                        if region.get("target_address") == start
                        and region["size"] == end - start
                        and region["address_status"]
                        == "generated_source_entry_replacement"
                    ]
                self.assertEqual(len(replacement_regions), 1)
                source_regions = [
                    region
                    for region in regions
                    if region.get("target_address") == address
                    and region["size"] == size
                    and region["address_status"] == "source_compiled"
                ]
                self.assertEqual(len(source_regions), 1)
                self.assertEqual(
                    source_regions[0]["file_offset"],
                    PREAMBLE_BYTES + address - RUN_BASE,
                )

        alignment_spans = [
            (0x007B_0616, 2),
            (0x007B_064E, 2),
            (0x007B_0686, 2),
        ]
        self.assertEqual(
            sorted(
                (region["target_address"], region["size"])
                for region in regions
                if region["address_status"] == "generated_alignment"
                and 0x007B_0616
                <= region.get("target_address", 0)
                < 0x007B_0924
            ),
            alignment_spans,
        )

    def test_package_level_ownership_equation_and_provider_pins_are_exact(
        self,
    ) -> None:
        manifest = self.effective_manifest
        package = manifest["package"]
        package_profile = self.open_cfw.profile_pins(
            package,
            self.profile_name,
        )
        package_size = (
            package["expected_size"]
            if package_profile is None
            else package_profile["expected_size"]
        )
        package_sha256 = (
            package["expected_sha256"]
            if package_profile is None
            else package_profile["expected_sha256"]
        )
        self.assertEqual(package_size, self.profile["package_size"])
        self.assertEqual(package_sha256, self.profile["package_sha256"])

        component_sizes = {}
        effective_regions = {}
        for component in manifest["components"]:
            provider = component["provider"]
            provider_profile = self.open_cfw.profile_pins(
                provider,
                self.profile_name,
            )
            size = (
                provider["size"]
                if provider_profile is None
                else provider_profile["size"]
            )
            component_sizes[component["name"]] = size
            effective_regions[component["name"]] = (
                self.open_cfw.effective_component_regions(
                    component,
                    size,
                    self.profile_name,
                )
            )

        source_owned = sum(
            region["size"]
            for regions in effective_regions.values()
            for region in regions
            if region.get("target_address") is not None
            and region["address_status"] == "source_compiled"
        )
        generated_flash = sum(
            region["size"]
            for regions in effective_regions.values()
            for region in regions
            if region.get("target_address") is not None
            and region["address_status"].startswith("generated_")
        )
        package_envelope = package_size - sum(component_sizes.values())
        main_preamble = next(
            region["size"]
            for region in effective_regions["apollo_main"]
            if region["name"] == "ota_preamble"
        )
        generated = generated_flash + package_envelope + main_preamble
        opaque = package_size - source_owned - generated
        self.assertEqual(
            (source_owned, generated, opaque),
            self.profile["package_accounting"],
        )
        self.assertEqual(source_owned + generated + opaque, package_size)

    def test_two_builds_are_byte_deterministic_for_active_profile(self) -> None:
        first, second = self.reports
        for section in ("overlay", "component"):
            first_bytes = artifact(first, section).read_bytes()
            second_bytes = artifact(second, section).read_bytes()
            with self.subTest(section=section):
                self.assertEqual(first_bytes, second_bytes)
                self.assertEqual(sha256(first_bytes), first[section]["sha256"])
                self.assertEqual(sha256(second_bytes), second[section]["sha256"])

    def test_exact_stock_and_tail_rollback_recreates_prior_component(self) -> None:
        legacy_layout = self.profile["legacy_semaphore_layout"]
        legacy_overlay = artifact(
            self.legacy_production,
            "overlay",
        ).read_bytes()
        legacy_component = artifact(
            self.legacy_production,
            "component",
        ).read_bytes()
        self.assertEqual(
            (len(legacy_overlay), sha256(legacy_overlay)),
            (
                legacy_layout["overlay_size"],
                legacy_layout["overlay_sha256"],
            ),
        )
        self.assertEqual(
            (len(legacy_component), sha256(legacy_component)),
            (
                legacy_layout["component_size"],
                legacy_layout["component_sha256"],
            ),
        )
        self.assertEqual(
            (
                len(self.legacy_production["overlay"]["functions"]),
                len(self.legacy_production["overlay"]["patched_sites"]),
            ),
            (
                legacy_layout["function_count"],
                legacy_layout["patch_count"],
            ),
        )
        functions = dict(self.legacy_production["overlay"]["functions"])
        self.assertEqual(
            functions["open_cfw_freertos_queue_semaphore_take"],
            {
                "offset": legacy_layout["function_offset"],
                "size": legacy_layout["function_size"],
            },
        )
        legacy_primary = {
            "open_cfw_evenhub_mode2_decompress_legacy": (
                "open_cfw_evenhub_mode2_decompress",
                self.profile["legacy_primary_spans"][
                    "open_cfw_evenhub_mode2_decompress"
                ],
            ),
            "open_cfw_lz4_decompress_safe_legacy": (
                "open_cfw_lz4_decompress_safe",
                self.profile["legacy_primary_spans"][
                    "open_cfw_lz4_decompress_safe"
                ],
            ),
        }
        for legacy_name, (prior_name, expected_span) in legacy_primary.items():
            self.assertEqual(functions.pop(legacy_name), expected_span)
            functions[prior_name] = expected_span
        for appended_name in (
            "LZ4_decompress_safe",
            "open_cfw_lz4_decompress_safe",
            "open_cfw_evenhub_mode2_decompress",
        ):
            if appended_name not in {
                prior_name for prior_name, _span in legacy_primary.values()
            }:
                functions.pop(appended_name)
        self.assertNotIn("open_cfw_lz4_decompress_safe_legacy", functions)
        self.assertNotIn("open_cfw_evenhub_mode2_decompress_legacy", functions)
        self.assertEqual(
            functions["open_cfw_lz4_decompress_safe"],
            self.profile["legacy_primary_spans"][
                "open_cfw_lz4_decompress_safe"
            ],
        )
        self.assertEqual(
            functions["open_cfw_evenhub_mode2_decompress"],
            self.profile["legacy_primary_spans"][
                "open_cfw_evenhub_mode2_decompress"
            ],
        )

        rebuilt = bytearray(artifact(self.production, "component").read_bytes())
        current_patches = {
            patch["name"]: patch
            for patch in self.production["overlay"]["patched_sites"]
        }
        legacy_patches = {
            patch["name"]: patch
            for patch in self.legacy_production["overlay"]["patched_sites"]
        }
        semaphore_patch_name = "replace_freertos_queue_semaphore_take"
        current_semaphore_patch = current_patches[semaphore_patch_name]
        legacy_semaphore_patch = legacy_patches[semaphore_patch_name]
        legacy_replacement = bytes.fromhex(
            legacy_semaphore_patch["replacement_hex"]
        )
        self.assertEqual(
            legacy_semaphore_patch["payload_offset"],
            legacy_layout["patch_payload_offset"],
        )
        self.assertEqual(
            legacy_semaphore_patch["target_address"],
            legacy_layout["patch_target_address"],
        )
        self.assertEqual(
            legacy_replacement[:4].hex(),
            legacy_layout["patch_branch_hex"],
        )
        self.assertEqual(
            sha256(legacy_replacement),
            legacy_layout["patch_sha256"],
        )
        self.assertNotEqual(
            current_semaphore_patch["target_address"],
            legacy_semaphore_patch["target_address"],
        )
        removed_patch_names = {
            "replace_cmsis_memory_pool_alloc",
            "replace_cmsis_mutex_acquire",
            "replace_cmsis_semaphore_acquire",
            "replace_nanopb_close_string_substream",
            "replace_nanopb_dec_bytes",
            "replace_nanopb_dec_fixed_length_bytes",
            "replace_nanopb_dec_string",
            "replace_nanopb_dec_submessage",
            "replace_nanopb_dec_varint",
            "replace_nanopb_decode_basic_field",
            "replace_nanopb_decode_callback_field",
            "replace_nanopb_decode_extension",
            "replace_nanopb_decode_field",
            "replace_nanopb_decode_fixed32",
            "replace_nanopb_decode_fixed64",
            "replace_nanopb_decode_inner",
            "replace_nanopb_decode_static_field",
            "replace_nanopb_decode_svarint",
            "replace_nanopb_default_extension_decoder",
            "replace_nanopb_field_set_to_default",
            "replace_nanopb_message_set_to_defaults",
            "replace_nanopb_read",
            "replace_nanopb_read_raw_value",
            "replace_nanopb_skip_field",
            "replace_nanopb_skip_string",
            "replace_nanopb_skip_varint",
            # Profile-gated out of the legacy-apple-clang rollback build.
            "replace_iar_frexpf_bits",
            "replace_iar_frexpf",
            "replace_iar_ldexpf",
        }
        self.assertEqual(
            set(current_patches),
            set(legacy_patches) | removed_patch_names,
        )
        changed_redirects = []
        for name, legacy_patch in legacy_patches.items():
            current_patch = current_patches[name]
            current_replacement = bytes.fromhex(
                current_patch["replacement_hex"]
            )
            prior_replacement = bytes.fromhex(
                legacy_patch["replacement_hex"]
            )
            self.assertEqual(
                current_patch["payload_offset"],
                legacy_patch["payload_offset"],
            )
            self.assertEqual(len(current_replacement), len(prior_replacement))
            if current_replacement == prior_replacement:
                continue
            patch_offset = legacy_patch["payload_offset"]
            rebuilt[
                patch_offset:patch_offset + len(prior_replacement)
            ] = prior_replacement
            changed_redirects.append(name)
        self.assertIn(semaphore_patch_name, changed_redirects)
        for removed_patch_name in removed_patch_names:
            removed_patch = current_patches[removed_patch_name]
            removed_offset = removed_patch["payload_offset"]
            removed_stock = self.official[
                removed_offset:
                removed_offset + removed_patch["expected_size"]
            ]
            rebuilt[
                removed_offset:removed_offset + len(removed_stock)
            ] = removed_stock
        rebuilt[OFFICIAL_SIZE:] = legacy_overlay
        rebuilt[:8] = legacy_component[:8]
        self.assertEqual(
            (len(rebuilt), sha256(rebuilt)),
            (
                legacy_layout["component_size"],
                legacy_layout["component_sha256"],
            ),
        )
        for _function, (_name, start, end, _stock_sha) in STOCK.items():
            offset = PREAMBLE_BYTES + start - RUN_BASE
            rebuilt[offset:offset + end - start] = self.official[
                offset:offset + end - start
            ]
        patches = {
            patch["target_function"]: patch
            for patch in self.legacy_production["overlay"]["patched_sites"]
        }
        for function, (start, end, stock_sha) in POST_SCHEDULER_STOCK.items():
            offset = PREAMBLE_BYTES + start - RUN_BASE
            size = end - start
            stock = self.official[offset:offset + size]
            replacement = bytes.fromhex(patches[function]["replacement_hex"])
            with self.subTest(post_scheduler_function=function):
                self.assertEqual(patches[function]["runtime_address"], start)
                self.assertEqual(patches[function]["payload_offset"], offset)
                self.assertEqual(len(replacement), size)
                self.assertEqual(sha256(stock), stock_sha)
                self.assertEqual(rebuilt[offset:offset + size], replacement)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        start,
                        replacement[:4],
                        link=False,
                    ),
                    patches[function]["target_address"],
                )
            rebuilt[offset:offset + size] = stock
        rollback_source_patches = POST_SCHEDULER_SOURCE_PATCHES
        for function in rollback_source_patches:
            patch = patches[function]
            offset = patch["payload_offset"]
            if "expected_hex" in patch:
                stock = bytes.fromhex(patch["expected_hex"])
            else:
                stock = self.official[
                    offset:offset + patch["expected_size"]
                ]
            replacement = bytes.fromhex(patch["replacement_hex"])
            with self.subTest(post_scheduler_source_function=function):
                self.assertEqual(
                    offset,
                    PREAMBLE_BYTES + patch["runtime_address"] - RUN_BASE,
                )
                self.assertEqual(
                    self.official[offset:offset + len(stock)],
                    stock,
                )
                if "expected_size" in patch:
                    self.assertEqual(len(stock), patch["expected_size"])
                    self.assertEqual(
                        sha256(stock), patch["expected_sha256"]
                    )
                self.assertEqual(len(replacement), len(stock))
                self.assertEqual(
                    rebuilt[offset:offset + len(replacement)],
                    replacement,
                )
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        patch["runtime_address"],
                        replacement[:4],
                        link=patch.get("branch") == "bl",
                    ),
                    patch["target_address"],
                )
            rebuilt[offset:offset + len(stock)] = stock
        for function, site in self.profile[
            "legacy_patch_replacements"
        ].items():
            offset = site["payload_offset"]
            size = site["size"]
            branch = bytes.fromhex(site["branch_hex"])
            replacement = branch + b"\x00\xbf" * ((size - len(branch)) // 2)
            runtime_address = RUN_BASE + offset - PREAMBLE_BYTES
            target_address = (
                OVERLAY_RUNTIME_BASE
                + self.profile["legacy_primary_spans"][function]["offset"]
            )
            with self.subTest(legacy_patch_function=function):
                self.assertEqual(len(branch), 4)
                self.assertEqual(len(replacement), size)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        runtime_address,
                        branch,
                        link=False,
                    ),
                    target_address,
                )
            rebuilt[offset:offset + len(replacement)] = replacement
        del rebuilt[-(
            self.profile["easylogger_tail_growth"]
            + self.profile["legacy_reset_unordered_tail_growth"]
            + self.profile["timeout_tail_growth"]
            + self.profile["next_closure_tail_growth"]
            + self.profile["lz4_tail_growth"]
            + self.profile["tail_growth"]
            + self.profile["littlefs_rewind_tail_growth"]
            + self.profile["littlefs_tag_type2_tail_growth"]
            + self.profile["littlefs_tag_type3_tail_growth"]
            + self.profile["littlefs_tag_id_tail_growth"]
            + self.profile["littlefs_tag_size_tail_growth"]
            + self.profile.get("current_rollback_net_tail_growth", 0)
        ):]
        first_word = struct.unpack_from("<I", rebuilt, 0)[0]
        struct.pack_into(
            "<I",
            rebuilt,
            0,
            (first_word & 0xFF00_0000) | len(rebuilt),
        )
        struct.pack_into("<I", rebuilt, 4, zlib.crc32(rebuilt[8:]) & 0xFFFF_FFFF)
        self.assertEqual(len(rebuilt), self.profile["prior_component_size"])
        self.assertEqual(sha256(rebuilt), self.profile["prior_component_sha256"])

    def test_source_output_stock_and_aggregate_hash_drift_fail_closed(self) -> None:
        reset_leaf = next(
            leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] == RESET_NEXT
        )
        effective = self.apollo_overlay.resolve_leaf_profile(
            reset_leaf,
            self.profile_name,
        )
        target = self.profile["leaves"][RESET_NEXT][1]
        synthetic = {
            "function": RESET_NEXT,
            "runtime_address": target,
            "source": copy.deepcopy(effective["source"]),
            "toolchain": copy.deepcopy(effective["toolchain"]),
            "expected": {
                "size": effective["expected"]["size"],
                "sha256": effective["expected"]["sha256"],
            },
            "stock": {
                "size": effective["expected"]["size"],
                "sha256": effective["expected"]["sha256"],
            },
            "relocations": [],
        }
        bad_source = copy.deepcopy(synthetic)
        bad_source["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.apollo_overlay.BuildError,
            "source SHA-256 differs",
        ):
            self.apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=self.clang,
                leaf_config=bad_source,
                object_path=Path(self.temporary.name) / "bad-source.o",
                enforce_stock_fit=False,
            )

        bad_output = copy.deepcopy(synthetic)
        bad_output["expected"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.apollo_overlay.BuildError,
            "output differs from reviewed pins",
        ):
            self.apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=self.clang,
                leaf_config=bad_output,
                object_path=Path(self.temporary.name) / "bad-output.o",
                enforce_stock_fit=False,
            )

        functions = self.production["overlay"]["functions"]
        overlay = artifact(self.production, "overlay").read_bytes()
        bad_patch = self.apollo_overlay.filter_config_for_profile(
            copy.deepcopy(self.config),
            self.profile_name,
        )
        patch = next(
            patch
            for patch in bad_patch["patch_sites"]
            if patch["target_function"] == PORT_YIELD
        )
        patch["expected_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.apollo_overlay.BuildError,
            "replace_freertos_port_yield.*SHA-256",
        ):
            self.apollo_overlay.patch_component(
                base=self.official,
                overlay=overlay,
                functions=functions,
                config=bad_patch,
            )

        for label, actual_size, actual_digest in (
            (
                "overlay",
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
            ),
            (
                "component",
                self.production["component"]["size"],
                self.production["component"]["sha256"],
            ),
        ):
            with self.subTest(label=label), self.assertRaisesRegex(
                self.apollo_overlay.BuildError,
                "differs from reviewed",
            ):
                self.apollo_overlay.verify_expected(
                    label,
                    actual_size,
                    actual_digest,
                    actual_size,
                    "0" * 64,
                )


if __name__ == "__main__":
    unittest.main()

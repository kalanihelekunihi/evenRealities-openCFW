#!/usr/bin/env python3
"""Pin and source-route the final 53-function R1 ownership residue.

These are the last previously unclassified application entries: callerless or
orphan-record bodies, framework plumbing shared between blocked candidate
families, thunks, and small helpers. Every entry carries exact instruction-range
pins plus caller or registered-pointer evidence; remote continuation bytes of
noncontiguous bodies are recorded as omitted so inventory sizes still match.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int, size: int, ranges: tuple[tuple[int, int, str], ...],
    symbol: str, role: str, callers: tuple[tuple[int, str], ...],
    provider_family: str, source_disposition: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "size": size,
        "inventory": "ghidra_functions_csv",
        "ranges": ranges,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x0006F80C, 62, ((0x0006F80C, 0x0006F812, "c6668ea061fac5266c74045ac939416f5b3c0746c2f6d79ebbe032964a9eeb71"),),
        "r1_gxt310_temp_reg90_scaled_read", "argument-setting thunk: movs r0,#0x90; b.w 0x6F600 (temp-register read + float scale); destination builds on r1_temp_reg_read_thunk 0x6F640; all four callers are r1_product_specific temperature functions (r1_gxt310_temp_average_read, r1_temperature_pair_read_calibrated, r1_temperature_pair_reduce, r1_gxt310_temp_pair_read)",
        ((0x00050E2C, "BL"), (0x00050E64, "BL"), (0x00051134, "BL"), (0x00051274, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006623E, 30, ((0x0006623E, 0x0006625C, "491cfbb7b37867f7830f7fd41e24186e9cfb22ef3ffdec2738c6d4e4484e9300"),),
        "r1_fw_wtd_op_handler", "fw_wtd watchdog ops callback: op 0 -> r1_watchdog_op_18 (0x500FC, r1 product), op 1 -> *out = osKernelGetTickCount (0x7D28C); ROM pointer at 0x993D8 = ops-table slot in struct named \"fw_wtd\" (adjacent R1 AT-command strings AT^INFO/AT^CHARGE_VER/AT^RESET_RING)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00096A40, 8, ((0x00096A40, 0x00096A48, "626fa7d084aadb896d97e65ffc715ab280a31e48dbb466b9209071997c25245c"),),
        "r1_state_byte_nonzero_96a40", "bool normalize (x != 0) applied to product state bytes at +0x24 of R1 wear/motion state; sole caller r1_wear_motion_topic_callback (r1_product_specific high)",
        ((0x0003CD96, "BL"), (0x0003CDD4, "BL"), (0x0004C426, "BL"), (0x0004C51C, "BL"), (0x0004C53A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E8AE, 6, ((0x0003E8AE, 0x0003E8B4, "3d3da97d7504fb38dae88cfdd5a96ba432f9f298608674333fef8c1407fc50f4"),),
        "r1_queue_flush_bounded_true_entry", "alternate entry: movs r1,#1 then falls through into r1_queue_flush_bounded (0x3E8B4, r1_product_specific high) — the decompiler-attributed loop body belongs to 0x3E8B4; six call sites all from r1_bae8_hvx_serialized_send_adapter 0x3E7A8",
        ((0x0003E7FE, "BL"), (0x0003E80E, "BL"), (0x0003E824, "BL"), (0x0003E83C, "BL"), (0x0003E86A, "BL"), (0x0003E878, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

NORDIC_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x00093960, 60, ((0x00093960, 0x0009399C, "94fd5bb41708ac0c29fff62c7fdaa5b48b5da1aea60f1ecf67eebf5a1afe7d95"),),
        "twi_evt_handler", "exact function-local match to integration/nrfx/legacy/nrf_drv_twi.c::twi_evt_handler (identical source to twim_evt_handler): copies nrfx event fields into legacy nrf_drv_twi_evt_t on stack, calls m_handlers[inst_idx](&event, m_contexts[inst_idx]); installed by exact-matched nrf_drv_twi_init (literal 0x93961 loaded at 0x78A08, passed to 0x7B28C when event_handler != NULL); m_handlers table at 0x20007958 referenced from inside nrf_drv_twi_init",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
    _function(
        0x0005C034, 42, ((0x0005C034, 0x0005C05E, "af6f00949ea8e0e13909db3ccc52b042130756983e486fd066246d133a1c679b"),),
        "db_update_pending_handle", "exact function-local match to components/ble/peer_manager/gatt_cache_manager.c::db_update_pending_handle: nrf_mtx_trylock(&m_db_update_in_progress_mutex) = nrf_atomic_u32_fetch_store(ptr,1)==0 (0x780B0, exact-matched) + DMB, then exact-matched local_db_update_in_evt (0x75B20), on failure nrf_mtx_unlock (DMB + store 0); ROM pointer at 0x94AD4 = passed as iterator callback",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
    _function(
        0x00034A7C, 26, ((0x00034A7C, 0x00034A96, "fe6367a5f3058e59a05daad734f3fb1a118ca0c8650e707354764e91e06f53c6"),),
        "nrfx_wdt_irq_handler", "exact function-local match to modules/nrfx/drivers/src/nrfx_wdt.c::nrfx_wdt_irq_handler: nrf_wdt_event_check(TIMEOUT) reads EVENTS_TIMEOUT[0] at 0x40010100 (WDT base 0x40010000), calls installed handler (RAM 0x2000794C), then nrf_wdt_event_clear with readback artifact; vector-table slot 32 = IRQ 16 = WDT",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
    _function(
        0x00034410, 6, ((0x00034410, 0x00034416, "44ecd077aa57c4d953e0f4ece3cf17e3f1bf855d54c0bd7b174a1a632de3e920"),),
        "nrfx_prs_box_4_irq_handler", "exact function-local match to modules/nrfx/drivers/src/prs/nrfx_prs.c PRS_BOX_DEFINE handler: ldr r0,=m_prs_box_4 (0x20007940); ldr r0,[r0,#handler]; bx r0 with NRFX_ASSERT compiled out; vector-table slot 18 = IRQ 2 = UARTE0 (UARTE0 base 0x40002000 confirmed by sibling prs_box_get 0x84CD8, exact-matched high)",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
)

FREERTOS_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x0009566C, 6, ((0x0009566C, 0x00095672, "f9e9ed7deab97ba770020418c839a3824257d2e29c2f736e873b7a50a3efaeb8"),),
        "uxTaskGetNumberOfTasks", "FreeRTOS 10.5.1 tasks.c uxTaskGetNumberOfTasks: 6-byte uxCurrentNumberOfTasks getter used as the cTxLock/cRxLock bound by exact-matched queue FromISR functions",
        ((0x00097E2C, "BL"), (0x00097EC6, "BL"), (0x000980D2, "BL"),),
        "freertos_10_5_1_nordic_nrf52_port", "use_authenticated_upstream_snapshot_and_nordic_port",
    ),
)

GOMORE_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x0007260C, 68, ((0x0007260C, 0x00072650, "7a56820f1e05e2d028cb367f23900800ffedfd9d2c195e4a47386e99b7839339"),),
        "", "validate-then-store config pair into state (+0x138; backup +0x130/+0x134 when flags 0xB4/0xB8 clear); sole caller 0x8ED10, callee 0x72420; sits in GoMore audit-scope block",
        ((0x0008ED1E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00058CE8, 62, ((0x00058CE8, 0x00058D26, "ad0d62d64e258d4134a1a2a5bf5c2120f3db89acf17fc08d72de0ab35d96a4cb"),),
        "", "null-guarded 3-way buffer compare (0xFFFF on NULL, -1/0/+1); sole caller 0x57C44 = GoMore audit-scope candidate; GoMore-candidate neighbors",
        ((0x00057C52, "BL"), (0x00074D26, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004B560, 52, ((0x0004B560, 0x0004B594, "4df29f0bb268fad32e19e61746fd77ccc94d0726d8e321c0e7b0c552e5e5472a"),),
        "", "proximity dedup check: rejects value within 300 of any stored uint16 in state struct 0x2001E3DC (count at +0xA); callerless, no pointer hits; state struct also consumed by r1_temperature_* product code; GoMore-candidate neighbors both sides",
        ((0x0004B9CC, "BL"), (0x0004BCB2, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000295DE, 46, ((0x000295DE, 0x0002960C, "e300debfc64aa697b9059b351f56f40cfefbb738f59c4d235748879a9d110649"),),
        "", "all-bytes-are-space string check via __ctype accessor 0x275EC; sole caller 0x65028 (GoMore _sdkAuth_ field validator); identical twin of 0x2960C",
        ((0x0006503E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002960C, 46, ((0x0002960C, 0x0002963A, "371466666f3c0cee45756cba09c4bc50eaef34275a3ced81e9b41115c8bacd4c"),),
        "", "all-bytes-are-space string check via __ctype accessor 0x275EC; sole caller 0x57B38 = GoMore audit-scope candidate; identical twin of 0x295DE",
        ((0x00057B5E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00072420, 46, ((0x00072420, 0x0007244E, "2535e53a7146ac5eaff5fe27f1b00394a93c051e7648573e4bfdf22abe6d1b37"),),
        "", "4-field config range validator (int16 in [15,60], uint16 < 0xF1, two u8 <= 0x17); sole caller 0x7260C (see its evidence); r1_touch_cfg seam adjacency noted as fragility",
        ((0x00072616, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004AA98, 40, ((0x0004AA98, 0x0004AAC0, "0227681e50ad8d2bcc05a60d8cc28a98b3f9c3b2d8050e7cfd90503e75b27c5c"),),
        "", "piecewise curve map around 0x60 baseline (x0.5 below / x0.8 above), clamp [70,100]; callerless, no pointer hits; adjacent output-range validator 0x4AAC0 shares clamp constants; r1 sleep-vivo probe block context",
        ((0x0004AC76, "BL"), (0x0004AE2E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004FB44, 38, ((0x0004FB44, 0x0004FB6A, "8f6965240b7a0a677fba18cf66eb25b237d35a1e683d9c93c5ece317bfda0641"),),
        "", "decimal ASCII-to-int parse loop over safe-strlen 0x8F674 (GoMore-internal); sole caller 0x57C84 = GoMore audit-scope candidate",
        ((0x00057C8E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00058D26, 36, ((0x00058D26, 0x00058D4A, "be2dd47b1a02a368f44bdcc798ac0c617a12039e63e4066e77417f75cff31513"),),
        "", "null-safe strcmp returning byte difference (0 on NULL args); called 3x from 0x57B38 = GoMore audit-scope candidate; GoMore-candidate neighbors",
        ((0x00057B8A, "BL"), (0x00057B9C, "BL"), (0x00057BB8, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065028, 36, ((0x00065028, 0x0006504C, "217bfcf1efb45e93f9d37b4a8eea38abcf22eccc8a443d1f9b00c5b0329c8055"),),
        "", "GoMore sdkAuth token-field validator: rejects all-space names via 0x295DE, err 0xFFFFFC14; fn-ptr table slot at RAM 0x20007CFC consumed exclusively by GoMore _sdkAuth_ parser 0x8EA0C",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000327E4, 34, ((0x000327E4, 0x00032806, "eebcd0d37c7282c10ff158cd4577ae9c9359519e8f500974a8d72fdc8e39261e"),),
        "", "count occurrences of byte (comma 0x2C in practice) + 1 = field counter; callers 0x5D560 and GoMore _sdkAuth_ parser 0x8EA0C (both GoMore audit-scope)",
        ((0x0005D596, "BL"), (0x0008EB4A, "BL"), (0x0008EBB8, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065050, 32, ((0x00065050, 0x00065070, "a0f446723c772606d8ce900ba1c53190b107cd615c64afe27b209d3252c1fda8"),),
        "", "GoMore sdkAuth token-field validator: name memcmp mismatch -> err 0xFFFFFC13 (same code returned by parser 0x8EA0C itself); table slot RAM 0x20007CF8",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00033330, 28, ((0x00033330, 0x0003334C, "505003f2dac785b4ba9b458f423b3e60bfe79492b8c74bf8f3fe7d7d90650d2f"),),
        "", "packs 3 bytes into uint (bfi x3) and stores constant-tag word 0x35D13 alongside; callers 0x2874C and 0x2966C, both GoMore audit-scope candidates",
        ((0x0002894C, "BL"), (0x000289E0, "BL"), (0x00029852, "BL"), (0x000298E6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065070, 28, ((0x00065070, 0x0006508C, "b57375b02a5d8aeb6e43ff2f06adf9b802dcbd32d8485e15d89e6b76e9633fcd"),),
        "", "GoMore sdkAuth token-field validator: reserved name \"SU\" (constant at 0x6508C) -> err 0xFFFFFC11; table slot RAM 0x20007D00",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AAC0, 26, ((0x0006AAC0, 0x0006AADA, "99f4b31dbbe8a38b7e180d86d2acf738be080d3f76665f45ad60be944d30b597"),),
        "", "stores seed, srand (0x276B8) + rand (0x276A4), returns rand()%100+23; sole caller 0x5D31E = GoMore audit-scope candidate",
        ((0x0005D358, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004B598, 24, ((0x0004B598, 0x0004B5B0, "b97051e2ce6772c8127e0b6efa5fa4a45600a3bc42d81e917e06fc24d2a9c3de"),),
        "", "uint16 plausibility check: accepts value in [30048, 50048] (0x7500+0x30 .. +0x4E21); callerless, no pointer hits; pairs with 0x4B560 on same temperature-ish state; GoMore-candidate neighbors",
        ((0x0004B9C2, "BL"), (0x0004BCA8, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0008ED10, 22, ((0x0008ED10, 0x0008ED26, "4a13f5228d150a5f409eeb60d9d1f5649d624f2797aaf44c43fe24befa61f17c"),),
        "", "wrapper: calls 0x7260C(*gstate + 0x1130, param), returns 0; callerless in call graph, no pointer hits; embedded in GoMore audit-scope block (neighbors 0x8EA0C/0x8EC7C/0x8ECD8/0x8ED2C all GoMore candidates)",
        ((0x0008F71E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0008F674, 20, ((0x0008F674, 0x0008F688, "920b9d05633ed4746883bc971176bf6d5c7ffb8e3d48a583c9d4ac7d4fb9f30d"),),
        "", "NULL-guarded walk-to-NUL length (returns 0 on NULL -> NOT exact standard strlen semantics, so not toolchain runtime); all callers are GoMore audit-scope functions (0x4FB44's caller 0x57C84, 0x57B38, _sdkAuth_ parser 0x8EA0C x5); GoMore-candidate neighbors",
        ((0x0004FB5E, "BL"), (0x00057B56, "BL"), (0x00057B80, "BL"), (0x00057B92, "BL"), (0x00074D1C, "BL"), (0x0008EA78, "BL"), (0x0008EAC0, "BL"), (0x0008EAD6, "BL"), (0x0008EAF4, "BL"), (0x0008EBAC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004AAC0, 16, ((0x0004AAC0, 0x0004AAD0, "892b6d7d5dbbc8c77262b95d2f0017fcd43fad7e35d04fa34feb273d0295f062"),),
        "", "byte range validator [70,100] — shares clamp constants with adjacent 0x4AA98 mapper; callerless, no pointer hits",
        ((0x0004AC5E, "BL"), (0x0004AE14, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00072ACE, 4, ((0x00072ACE, 0x00072AD2, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),),
        "", "return-0 stub; adjacency to pinned Nordic nrfx_pwm irq_handler (0x72A32) rejected — both callers (0x57C84, 0x967C8) are GoMore audit-scope candidates",
        ((0x00057C9A, "BL"), (0x000967D0, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091080, 2, ((0x00091080, 0x00091082, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "", "2-byte empty body (bx lr); sole caller 0x4C37C = GoMore audit-scope reinit path; treated as GoMore no-op hook",
        ((0x0004C392, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x00034B08, 76, ((0x00034B08, 0x00034B54, "47f6f577a2cf956bc4645153645024f0f6bf96e0cca7dc811e91f415e7a151f2"),),
        "", "vtable-driven sensor register command/status poll (cmds 0xA6/0xAE, 0x140-tick timeout); callerless; ROM ops-table pointer at 0x31DC4; all classified neighbors Goodix high",
        (),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003E6B0, 68, ((0x0003E6B0, 0x0003E6C6, "40ff56660c7f59296d057c5af8100ca6ded078c411cc3b469c06c6a25cede02c"),),
        "", "algorithm-context destructor: frees sub-buffers (0x1C0/0x1DC/0x1F4/0x260) via sensor-algorithm heap free 0x2D460/0x36230, tail-branches to 0x29354; ROM ops-table pointer at 0xBCF78; Goodix-high neighbors both sides",
        (),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00043B30, 62, ((0x00043B30, 0x00043B6E, "0fc45ae6902d0018df660bf9e3572439a79268f8e672679d237ba8934754db0e"),),
        "", "per-slot elapsed-time accounting update (counters 0x1E0/0x1E4/0x1E8 from slot array at +0x238); classified Goodix thunk 0x99010 (thunk_FUN_00043b30, GH_SPO2/dlCom closed-callgraph boundary) targets it",
        ((0x00099010, "B.W"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00037574, 48, ((0x00037574, 0x0003757C, "e4489cd29e59fa994123e5446973511c7727252a43d342a216a65fe1d4281313"),),
        "", "Goodix helper; classified Goodix thunk 0x3754A (thunk_FUN_00037574, GH_SPO2/dlCom boundary) targets it",
        (),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00036BFA, 44, ((0x00036BFA, 0x00036C26, "b3713a82732d46def2a138a7352b03778cd8f45809d7b76ebe60ef0b46416e61"),),
        "", "context-buffer zeroing (three buffers at 0x1C0/0x1DC/0x1F4, lengths <<2) on mode==1; classified Goodix thunk 0x2F65C (thunk_FUN_00036bfa) targets it; Goodix-high neighbors",
        ((0x0002F65C, "B.W"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002ADD0, 40, ((0x0002ADD0, 0x0002ADD6, "e4ac8bd7466791613e56a3c03ef9709aaa8d80d47f19a20f6ec70ba1e26e184a"), (0x0002ADD8, 0x0002ADFA, "404bec7ecc58f5f229e0c05541fa2d8c322f40dd3c634b83fc677ca2af72400f"),),
        "", "in-place 16-bit byte-pair swap (endianness fixup) of sample buffer; callerless, no pointer/vector/init-table hits; contiguous Goodix-candidate neighbors",
        ((0x0002A6EE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00037B68, 24, ((0x00037B68, 0x00037B80, "7b80355b75df66f92a0479063f38a8e65a22a692c202108aa522c4cbe740142d"),),
        "", "int -> int8 clamp with -0x80 centering (unsigned-to-signed sample conversion); callerless, no pointer hits; Goodix-high neighbors on both sides",
        ((0x00086142, "BL"), (0x000862C4, "BL"), (0x0008636E, "BL"), (0x00086456, "BL"), (0x0008653A, "BL"), (0x00086566, "BL"), (0x0008659E, "BL"), (0x000865D4, "BL"), (0x000866DE, "BL"), (0x0008670E, "BL"), (0x00086742, "BL"), (0x00086770, "BL"), (0x000868B2, "BL"), (0x00086984, "BL"), (0x00086A8E, "BL"), (0x00086B12, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002A54C, 4, ((0x0002A54C, 0x0002A550, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),),
        "", "return-0 stub inside contiguous Goodix-candidate stub cluster (0x2A540/0x2A550/0x2A55C all Goodix candidate)",
        ((0x0006A4C2, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002A610, 4, ((0x0002A610, 0x0002A614, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),),
        "", "return-0 stub inside contiguous Goodix-candidate cluster (0x2A604/0x2A614/0x2A658)",
        ((0x0006A4BC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
)

DEVICE_REGISTRY_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x00050ABC, 30, ((0x00050ABC, 0x00050ADA, "01493f1cc6ee0eb2e44d322df92df3bb0e187529f198323f0deceac546295e39"),),
        "", "registry client op: registry device_operation_dispatch_slot_08 (0x85D1A) on DAT+4, conditional slot_20 (0x85D46,flag=1); callerless, no pointer hits; neighbors are r1_goodix_provider_adapter wrappers (adapter family not assignable this round)",
        ((0x00050B6E, "BL"), (0x00050B9C, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00087AF8, 30, ((0x00087AF8, 0x00087B16, "8509e07607294c4bd49a4433dfa558fa34908724a64ed53e9a49777998781745"),),
        "", "packs 3-word message into static buffer 0x2001E56C and posts via device_operation_dispatch_slot_10 (0x85D2C, registry candidate); RAM pointer-table hit at 0x200077EC; callerless in call graph",
        (),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0005D8CC, 26, ((0x0005D8CC, 0x0005D8E6, "83c735fdcbc9ed290714cd230d65fc66379ca691afa54dc735d986c546b126a3"),),
        "", "BKDR-style name hash (h = h*0x83 + byte) over buffer; callerless, no pointer hits; sits directly above the shared intrusive-list accessors 0x5D8E6/0x5D8EE/0x5D8F6 used by registry list insert/remove; 0x5D8xx-0x5DCxx list/registry region prior",
        ((0x000731FC, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0006F90E, 18, ((0x0006F90E, 0x0006F920, "0cfdd25c5a42688645f2744bf05dca0483d44bf68450d1a2d8b056fad26d5b53"),),
        "", "ops-table callback: reorders args, calls registry static_request_block_fill 0x509BC with op=0, returns 1; ROM ops-table hit at 0x2DB00 whose first slot is r1_goodix_board_line_prepare_thunk (Goodix device ops table)",
        (),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00077E30, 12, ((0x00077E30, 0x00077E3C, "5d706e51761318a467020a176c78df65e068d82e11acf2e5fc594438acb77339"),),
        "", "intrusive-list link store helper: if offset != 0, *(node + offset + 4) = value; called by registry-candidate list insert 0x5D94A, registry-candidate remove 0x5D998, and sensor-stream node allocate 0x5D90E",
        ((0x0005D92E, "BL"), (0x0005D960, "BL"), (0x0005D976, "BL"), (0x0005D9D6, "B.W"), (0x0005D9EE, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00077E3C, 10, ((0x00077E3C, 0x00077E46, "b7b4fc8d311ba35e4aaf7fa49703a4062558a0a9f8cf80a1660640eaa28dc8a8"),),
        "", "intrusive-list link store helper: if offset != 0, *(node + offset) = value; callers are the same registry-candidate list insert/remove pair 0x5D94A/0x5D998 plus sensor-stream node allocate 0x5D90E",
        ((0x0005D924, "BL"), (0x0005D93A, "BL"), (0x0005D96A, "BL"), (0x0005D9FC, "B.W"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0005D8E6, 8, ((0x0005D8E6, 0x0005D8EE, "0852648987107a62e4221fb31109e0d50dfc55c254528d5a5311b08a1a094c3f"),),
        "", "guarded node-field getter (NULL -> 0, else *(node+4)); callers: registry-candidate 0x5D998/0x5DB14 and sensor-stream-candidate 0x89B08/0x89D54/0x8A1E0/0x8A45C (shared list framework)",
        ((0x0005D99E, "BL"), (0x0005DA6A, "BL"), (0x0005DB32, "BL"), (0x00089BB6, "BL"), (0x00089C38, "BL"), (0x00089D62, "BL"), (0x0008A078, "BL"), (0x0008A260, "BL"), (0x0008A49E, "BL"), (0x0008A4CA, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0005D8EE, 8, ((0x0005D8EE, 0x0005D8F6, "e08000717aba4a99bd865d85b1b4e26170dd831851f6a5d5b9c05664d28c1020"),),
        "", "unguarded node-field getter *(node + offset + 4); same registry + sensor-stream caller set as 0x5D8E6",
        ((0x0005D9AA, "BL"), (0x0005D9E2, "BL"), (0x0005DA9C, "BL"), (0x0005DB54, "BL"), (0x00089BC2, "BL"), (0x00089C74, "BL"), (0x00089D76, "BL"), (0x0008A088, "BL"), (0x0008A2EA, "BL"), (0x0008A4AA, "BL"), (0x0008A4EE, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0005D8F6, 8, ((0x0005D8F6, 0x0005D8FE, "3ed21d493193ae519d2a98164490d5eb7124e824bfd4dff8fd774d7e0f847cfc"),),
        "", "guarded node-field getter (NULL -> 0, else *(node+8)); sole caller registry-candidate remove 0x5D998",
        ((0x0005D9BC, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00077214, 8, ((0x00077214, 0x0007721C, "0c7581b47a7677a260141079a54623b6555fe6e538d3d144fe4e142785701ee6"),),
        "", "pure branch thunk (b.w) to 0x85CBA = registry-candidate device_operation_dispatch_slot_0c with device handle *DAT_0007721C; inherits destination family/disposition",
        ((0x00042D30, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
)

QUANTIZED_RUNTIME_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x00029120, 34, ((0x00029120, 0x00029142, "bdec0f3376563581f2578e7e253ebd0d44f950cb7cffaf4fe0eac54aafafdead"),),
        "round_half_away_from_zero_29120", "float x -> int(x + copysign(0.5,x)) (vcvt.s32.f32); identical semantics to classified neighbor 0x290FE (round_half_away_from_zero_290fe, same family); callerless, no pointer hits",
        ((0x00085E2A, "BL"), (0x0008601E, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "investigate_before_implementing",
    ),
)

RTC_DEVICE_FRONTIER_FINAL53_FUNCTIONS = (
    _function(
        0x00050DAA, 12, ((0x00050DAA, 0x00050DB6, "7ed3839cbc121b8ce45a995ed1503c99126e28acc33936b2262f1671fb12d09a"),),
        "", "RTC-device ops-table slot 7 (ROM table at 0x99C8C): moves r3->r0, calls 0x50DE0, returns 1; table sits directly after days-in-month arrays and is referenced from time/calendar provider region 0x5A8AC-0x5A983",
        (),
        "unknown_rtc_device_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00050DE0, 12, ((0x00050DE0, 0x00050DEC, "51129a4a7988def880fc9ea1ea1a9ebd4572b7e8c134093cf8afe0aa52b33b91"),),
        "", "shared tail of 0x50DAA: tail-branches to registry device_operation_dispatch_slot_20 (0x85D46) with op=0 on a device handle; sole caller is the RTC-table slot 0x50DAA",
        ((0x00050DAE, "BL"),),
        "unknown_rtc_device_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00050DB6, 10, ((0x00050DB6, 0x00050DC0, "2e064ca1f0afdb9a53e8f599f8291b42f4e037b3df4152747b7ac292f84250d4"),),
        "", "RTC-device ops-table slot 4 (ROM table at 0x99C8C): calls registry static_request_block_fill 0x50DF0, returns 1",
        (),
        "unknown_rtc_device_provider_candidate", "investigate_before_implementing",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_FINAL53_FUNCTIONS
    + NORDIC_FRONTIER_FINAL53_FUNCTIONS
    + FREERTOS_FRONTIER_FINAL53_FUNCTIONS
    + GOMORE_FRONTIER_FINAL53_FUNCTIONS
    + GOODIX_FRONTIER_FINAL53_FUNCTIONS
    + DEVICE_REGISTRY_FRONTIER_FINAL53_FUNCTIONS
    + QUANTIZED_RUNTIME_FRONTIER_FINAL53_FUNCTIONS
    + RTC_DEVICE_FRONTIER_FINAL53_FUNCTIONS
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    rows = []
    for function in ALL_FUNCTIONS:
        entry = int(function["entry"])
        pinned = 0
        for start, end, want in function["ranges"]:
            body = image[start - LOAD_BASE:end - LOAD_BASE]
            if hashlib.sha256(body).hexdigest() != want:
                raise ValueError(f"frontier range changed: 0x{start:08x}..<0x{end:08x}")
            pinned += end - start
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if callers != function["callers"]:
            raise ValueError(f"frontier callers changed: 0x{entry:08x}")
        rows.append({
            **{k: v for k, v in function.items() if k != "ranges"},
            "entry": f"0x{entry:08x}",
            "pinned_bytes": pinned,
            "omitted_bytes": int(function["size"]) - pinned,
            "callers": [
                {"callsite": f"0x{callsite:08x}", "kind": kind}
                for callsite, kind in callers
            ],
        })
    return {
        "analysis": "final-53 ownership residue closure",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "pinned_bytes": sum(int(row["pinned_bytes"]) for row in rows),
        "omitted_bytes": sum(int(row["omitted_bytes"]) for row in rows),
        "r1_function_count": len(R1_FRONTIER_FINAL53_FUNCTIONS),
        "nordic_function_count": len(NORDIC_FRONTIER_FINAL53_FUNCTIONS),
        "freertos_function_count": len(FREERTOS_FRONTIER_FINAL53_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_FINAL53_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_FINAL53_FUNCTIONS),
        "device_registry_function_count": len(DEVICE_REGISTRY_FRONTIER_FINAL53_FUNCTIONS),
        "quantized_runtime_function_count": len(QUANTIZED_RUNTIME_FRONTIER_FINAL53_FUNCTIONS),
        "rtc_device_function_count": len(RTC_DEVICE_FRONTIER_FINAL53_FUNCTIONS),

        "functions": rows,
        "safety": {
            "biometric_or_health_algorithm_reimplemented": False,
            "yhm_wire_or_register_body_recreated": False,
            "unidentified_framework_recreated": False,
            "time_calendar_provider_recreated": False,
            "withheld_dispatch_surface_enabled": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

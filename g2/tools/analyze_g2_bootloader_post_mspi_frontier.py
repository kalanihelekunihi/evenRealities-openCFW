#!/usr/bin/env python3
"""Authenticate and classify the bootloader post-MSPI frontier.

The audit is software-only.  It compiles and relocates the admitted,
reviewable Thumb-2 realizations, checks their semantic provider
edges, checks the exhaustive byte ledger, and verifies production ownership
without probing, executing MMIO, flashing, signing, or assembling a release
package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apollo_overlay
from integrate_g2_bootloader_cmdq_services_427794 import (
    SERVICES as CMDQ_SERVICE_SPECS,
)
from integrate_g2_bootloader_float_math_427c90 import (
    FUNCTIONS as FLOAT_MATH_SPECS,
)


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_interrupt_power_426536.S"
MEMSET_WRAPPER_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memset_wrapper_426c10.c"
HFADJ_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_hfadj_enable_426c58.c"
HFADJ_CONFIG_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_hfadj_config_426c72.c"
HFADJ_DISABLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_hfadj_disable_426c7e.c"
DUAL_SWITCH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dual_switch_426c8c.c"
CLKGEN_CONFIG_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_config_426ccc.c"
CLKGEN_DISABLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_clkgen_disable_426d1e.c"
FLOAT_GCD_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_gcd_426d48.c"
FLOAT_RATIO_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_ratio_426db4.c"
FLOAT_MULTIPLIER_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_multiplier_426eac.c"
FLOAT_SELECT_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_encoding_select_426f6c.c"
SYSPLL_MIN_FVCO_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_min_fvco_427040.c"
SYSPLL_POSTDIV_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_postdiv_427160.c"
SYSPLL_INITIALIZE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_initialize_4272ac.c"
SYSPLL_DEINITIALIZE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_deinitialize_427310.c"
SYSPLL_ENABLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_enable_427360.c"
SYSPLL_DISABLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_disable_4273dc.c"
SYSPLL_CONFIGURE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_configure_42740c.c"
SYSPLL_LOCK_WAIT_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_syspll_lock_wait_427522.c"
QUEUE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_queue_4275ea.c"
MEMMOVE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memmove_4276bc.c"
CMDQ_UPDATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_update_indices_427754.c"
CMDQ_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_services_427794.c"
FLOAT_MATH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_math_427c90.c"
FLOAT_MATH_VENEERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_math_veneers_427c90.c"
SPOTMGR_TRANSITION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_transition_428378.c"
SPOTMGR_TRANSITION_7B_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_transition_7b_428a94.c"
SPOTMGR_FACTORY_TRIMS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_factory_trims_429da4.c"
SPOTMGR_FACTORY_ENSURE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_factory_trims_ensure_42a036.c"
SPOTMGR_TIMER_IRQ_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_timer_irq_service_42a04a.c"
SPOTMGR_BUCK_DEEPSLEEP_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_buck_deepsleep_state_42a08c.c"
SPOTMGR_INTERNAL_DOMAIN_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_internal_power_domain_42a19c.c"
SPOTMGR_POWER_TON_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_ton_adjust_42a1bc.c"
SPOTMGR_STATE_SEQUENCE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_state_transition_sequence_42a2b4.c"
SPOTMGR_TEMPERATURE_TRANSITION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_temperature_transition_separate_42a43a.c"
SPOTMGR_POWER_TRIMS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_trims_update_42a4bc.c"
SPOTMGR_POWER_STATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_determine_42a550.c"
SPOTMGR_UPDATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_update_42a878.c"
SPOTMGR_PROFILE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_profile_apply_42ab7c.c"
SPOTMGR_INIT_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_init_42abbc.c"
SPOTMGR_TEMPERATURE_INIT_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_temperature_init_42ac54.c"
SPOTMGR_TEMPERATURE_RANGE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_temperature_range_42ad40.c"
SPOTMGR_TRIM_HELPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_trim_helpers_42adb8.c"
SPOTMGR_TRIM_COMMIT_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_trim_commit_42ae9c.c"
SPOTMGR_BUCK_SCAN_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_buck_deepsleep_scan_42aef0.c"
SPOTMGR_STATE_EFFECTS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_state_transition_effects_42b014.c"
SPOTMGR_POWER_TRANSITION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_transition_trims_42b06c.c"
SPOTMGR_STATE_TRANSITION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_state_transition_42b294.c"
DIVIDER_HELPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_rounded_divider_power2_42c222.c"
HW_CLOCK_ENCODE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_clock_encode_42c26a.c"
STATE_RANGE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_state_range_dispatch_42cdf8.c"
STATE_EVENT_ZERO_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_state_event_zero_42cfe0.c"
STATE_EVENT_ONE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_state_event_one_value_42d104.c"
STATE_REGISTER_INITIALIZE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_state_register_initialize_42d3bc.c"
MISC_PRIMITIVES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_misc_primitives_42d84c.c"
DFU_IMAGE_CRC_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dfu_image_crc_check_42d890.c"
REGISTER_HELPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_register_helpers_42c034.c"
HW_EVENT_APPLY_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_event_apply_42c0b2.c"
CMDQ_ADAPTERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_adapters_42c3e2.c"
HW_DESCRIPTOR_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_descriptor_publish_42c45a.c"
HW_CONTEXT_CLAIM_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_context_claim_42c4c6.c"
HW_CONTEXT_ENABLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_context_enable_42c538.c"
HW_EVENT_SERVICE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_event_service_42c6f8.c"
HW_CONFIG_TRANSACTION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_transaction_42c988.c"
HW_INSTANCE_CONFIGURE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_instance_configure_42cc34.c"
HW_CONFIG_RETRY_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_retry_43048e.c"
PLATFORM_FINISH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_platform_finish_430502.c"
PLATFORM_BRINGUP_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_platform_bringup_430000.c"
DESCRIPTOR_REGISTER_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_descriptor_register_430280.c"
HW_STATE_COMPOSE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_state_compose_42bdf0.c"
HW_STATE_DECODE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_state_decode_42b6b8.c"
HW_PROFILE_APPLY_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_profile_apply_42ea68.c"
HW_REGISTER_PROFILE_RESTORE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_register_profile_restore_42f2fa.c"
EVENT_VALUE_PROFILE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_value_profile_42f204.c"
REGISTER_PROFILE_TRANSFER_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_register_profile_transfer_42f020.c"
CHUNKED_SOURCE_COMPARE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_chunked_source_compare_42da1e.c"
DFU_PAYLOAD_PROGRAM_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dfu_payload_program_42dae8.c"
MODE_APPLY_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mode_apply_42ff00.c"
CONTROL_WRAPPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_control_wrappers_42dd68.c"
CONTEXT_LIFECYCLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_context_lifecycle_42dd70.c"
EVENT_CONTROL_WRAPPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_control_wrappers_42e2ea.c"
EVENT_SETUP_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_setup_42e278.c"
EVENT_STATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_state_42e224.c"
SMALL_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_small_services_42cea4.c"
CONTROL_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_control_services_42bf54.c"
EVENT_SERVICE_LOOP_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_service_loop_42e2f8.c"
EVENT_RUNTIME_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_runtime_services_42e53c.c"
CONTROL_ORCHESTRATION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_control_orchestration_42dd14.c"
DFU_SERVICE_TASK_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_dfu_service_task_42de58.c"
CONTEXT_PUBLISH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_context_publish_42dca2.c"
LATE_WRAPPERS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_late_wrappers_42fff2.c"
NOOP_CALLBACKS_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_noop_callbacks_42dd98.c"
STARTUP_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_services_432910.c"
STARTUP_RUNTIME_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_runtime_43297c.c"
ALIGNMENT_DISPATCH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_alignment_dispatch_42e4f4.c"
GUARDED_CALL_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_guarded_call_cleanup_42e8a4.c"
HW_CONTEXT_INITIALIZE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_context_initialize_42e8d0.c"
EVENT_DISPATCH_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_dispatch_42f38e.c"
HW_HANDLE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_services_42ea32.c"
HW_COMMAND_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_command_42eff4.c"
CLKMGR_DIVIDER_SOURCE = ROOT / "components/shared/ambiq/runtime_clkmgr_divider_candidate.c"
HW_CHANNEL_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_channel_config_42eaf6.c"
HW_ACTIVATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_activate_42ed60.c"
HW_CONFIG_ENUMERATE_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_enumerate_42ec0c.c"
ORPHAN_SERVICES_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_orphan_services_430aec.c"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_REPORT = ROOT / "components/bootloader/core_overlay/build/build-report.json"
AMBIQ_SOURCE = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
AMBIQ_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.h"
AMBIQ_LICENSE = ROOT / "third_party/ambiqsuite-apollo510/LICENSE"
AMBIQ_PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
AMBIQ_QUEUE_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_queue.h"
AMBIQ_CMDQ_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_cmdq.h"

PINS = {
    BOOT: (148_599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"),
    MAIN: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    SOURCE: (44_692, "a1b9c4a5519a59329cb1c2a3bad6ab7eb973db56903a04fbed489c678a1f3d81"),
    CENSUS: (83_220, "6af54dfc96c888687b0687ac9b83d5ab427b0f2d4ecc9bb33c284c68cf29fd3e"),
    MEMSET_WRAPPER_SOURCE: (825, "bbcc17751db1eca6ac70b90948de4b12f2b96755cb86ad3b35886d57e88fe25a"),
    HFADJ_SOURCE: (909, "445c7a8cc57cb7aed3a4004ee060562ffb99b611d2b986442ed7547a9762503d"),
    HFADJ_CONFIG_SOURCE: (871, "3ba2f97833189778782e16d50165089dc737fc3fd75aee690a8f903ce18c983a"),
    HFADJ_DISABLE_SOURCE: (866, "78b97b8bfb29d85ca42333b5d91c9b865719112cbeafafbfaa8d463bbe6d7dc3"),
    DUAL_SWITCH_SOURCE: (2_578, "a4e62f01d25d5064d93006206c0574c5080b5a228c89803e62eab3251ee1e176"),
    CLKGEN_CONFIG_SOURCE: (2_674, "b93014f4591b61ee1accbf673f272a2e9d4321bf918f7adf863212ff3a4e3261"),
    CLKGEN_DISABLE_SOURCE: (810, "0d6d5eb220150a2b1aadb53f5d0392911612a4177a0b1ba378cc45f622e0bee1"),
    FLOAT_GCD_SOURCE: (1_158, "aa9f856ce58a8cb8cf8bdac4c72e9d3404bed80627dfcd10b7a3c90681ace9ce"),
    FLOAT_RATIO_SOURCE: (2_557, "e6c6fbf17f1102ec57d1cf8307e9d1f937e6bb510b8c919eefb4ed1e3fb356ae"),
    FLOAT_MULTIPLIER_SOURCE: (2_210, "4fc527028c045e6afd2578edf576a141c12b6b087f30e1ae1059e0cfb8a10263"),
    FLOAT_SELECT_SOURCE: (2_464, "fab1b8623c2b2af20e32a3130cb735ca4cec7f360cfe4b7a9bc24fff8077525b"),
    SYSPLL_MIN_FVCO_SOURCE: (3_963, "4dcfd9fad72a5884b3aa096f60fce1304fdfa716fe16cd4688ed7fc3280cf0e5"),
    SYSPLL_POSTDIV_SOURCE: (4_460, "8789ef668098ed26dfaafe2ac33424d0fd89a7d0ad3a5cc42a2b197a71ddb1d9"),
    SYSPLL_INITIALIZE_SOURCE: (2_362, "9cd928cb92202fd35a62738d0de91ff302a8e2e74376d1caacbeb7cf46d7fd49"),
    SYSPLL_DEINITIALIZE_SOURCE: (2_862, "965ced87505a307332e09a6812d11ff2dea40acbf490bf479fa541fa1a7210cc"),
    SYSPLL_ENABLE_SOURCE: (3_157, "48ede872ce7d8a77952cc256fb49f8677dbc93c2babc2870f4285709698674f8"),
    SYSPLL_DISABLE_SOURCE: (2_059, "b2a255ba82bfbc8655941104c21e2709a829e15d7a4201e1baef2549ab0d1933"),
    SYSPLL_CONFIGURE_SOURCE: (9_102, "5ff6984eb7f8ef5be6519f62d8e30da649c9c0619728da8eababc9f96ddc290f"),
    SYSPLL_LOCK_WAIT_SOURCE: (4_641, "6e7375a70491f95e31756934d18a121490f3cb7a4e6847eef2d8231c9a8db33a"),
    QUEUE_SOURCE: (4_549, "7cf282d9fca53ffe4170291cdc3fb17da8beecf4767e9ffbe3e5aa2044f1f4a9"),
    MEMMOVE_SOURCE: (1_108, "b63410af30e2432f3a8a4beb9527787b2662bc8404cf72cf125290e41004565d"),
    CMDQ_UPDATE_SOURCE: (3_441, "ac78bb01c0de433c911b537822e8c6637014d8180d3128b6288e6728b6008b32"),
    CMDQ_SERVICES_SOURCE: (16_145, "83df5464c59bd66d4f13b4b15abed30a721b9ff410bfb8ab4acbc93d4bf91188"),
    FLOAT_MATH_SOURCE: (6_767, "75a98dd043e4c39abb170a58b09ba8401de719ca535957b3afb1ca935142210c"),
    FLOAT_MATH_VENEERS_SOURCE: (3_196, "22a7a94c12817325377c25acfdc0c6e4acc074299f2e5467d3221b3f16a554ee"),
    SPOTMGR_TRANSITION_SOURCE: (3_512, "aa14e528718e5edc6a20103b951b289eb2c3c8564a330e0e403d149b3801644f"),
    SPOTMGR_TRANSITION_7B_SOURCE: (8_213, "be4c4617b3b664e1576aaa0156205d17bd2a552e5aaafd3f8a13c4f742dca947"),
    SPOTMGR_FACTORY_TRIMS_SOURCE: (2_490, "d20dde33ad27aefe7d14c36ffbbdb7dd038ae938d51dd80bfaa0dd214a1bbb6d"),
    SPOTMGR_FACTORY_ENSURE_SOURCE: (1_469, "c1151e210f9e1e11285d8b9b3bc74d8217370dbcffdb1b46e7fb9773b7d3160c"),
    SPOTMGR_TIMER_IRQ_SOURCE: (2_589, "13c2ca02ec9303e3a1c0506b76f489599b6131a9fd33421fa59723ab724483b6"),
    SPOTMGR_BUCK_DEEPSLEEP_SOURCE: (6_394, "45df23181652757089f6a69ff4a095ff8e68e392c627ed69db53f387feed9b72"),
    SPOTMGR_INTERNAL_DOMAIN_SOURCE: (1_377, "6a2d34cab44aa964ed5f203b3c5665b2d28a653611e02de6dec701fac09a423f"),
    SPOTMGR_POWER_TON_SOURCE: (5_798, "c3b397b5833bfbb9add45b3e44367974ab9cfee3871864ff67047ea8f77bd75a"),
    SPOTMGR_STATE_SEQUENCE_SOURCE: (11_291, "4741430855fd4a1344b48d5e5e7e6fc7b5ab1a6e2d389c52808d7c04492bf014"),
    SPOTMGR_TEMPERATURE_TRANSITION_SOURCE: (5_192, "4de53020af984d02bceb30519540dc7dda7633e2ecd998dac51c82ef31b96766"),
    SPOTMGR_POWER_TRIMS_SOURCE: (5_713, "e8d3daa5fec283f59153a52cfad2287a288e40882c1a920450bec9d6fe1cefb8"),
    SPOTMGR_POWER_STATE_SOURCE: (17_636, "4e201c6adb3a27bb59f5347a3b4679c3b642b1c4079a3aedfaff5b23432fc1b9"),
    SPOTMGR_UPDATE_SOURCE: (13_889, "748ea09bb3598a3ba045fda4c2c47dea74601faf85bc467966e9574534841859"),
    SPOTMGR_PROFILE_SOURCE: (2_229, "1d1a2d04a25e1fb86c2bbca2c70ed8c7cf0eb1b8a1e2976461ae85e182ec966d"),
    SPOTMGR_INIT_SOURCE: (3_818, "c52963c37e84313c830e60254df242b5619685ff71e1a80a7ade1b4136264361"),
    SPOTMGR_TEMPERATURE_INIT_SOURCE: (2_053, "c7ca1c2524bba42f8b264ddc676e5d568881ce1e8a0e209518b5d00cdf40c908"),
    SPOTMGR_TEMPERATURE_RANGE_SOURCE: (1_617, "b24cdcfa0cd68ddc6526780829a85c4e390bac7b108ce8aaff33f51601d4b61a"),
    SPOTMGR_TRIM_HELPERS_SOURCE: (4_349, "c4cbf548a28eb5ea192392ae0c48a6d6c671e18e9b1c53fe10a903699cb7b1d7"),
    SPOTMGR_TRIM_COMMIT_SOURCE: (1_468, "896fa6e31b957ff02a793b640012fe9b9a5d0c25ca98979273aa1957aea744e9"),
    SPOTMGR_BUCK_SCAN_SOURCE: (6_641, "dae1dc232e36f7d39a40655af73e547f1c7fcab8a86014e748f152396ec11dba"),
    SPOTMGR_STATE_EFFECTS_SOURCE: (2_638, "4e0c515dd2c0cce052ad1b42ef13c3db3a6aef7d1e57fb157ddd27595ae3cd9c"),
    SPOTMGR_POWER_TRANSITION_SOURCE: (11_845, "1daae8e352b04325e7a1e519111e4a9207042e8b5740e1b59692b8afc0004a27"),
    SPOTMGR_STATE_TRANSITION_SOURCE: (14_347, "858dc5a87b78e22b803f987645d573d364b024d354fcb230126f510498e599f0"),
    DIVIDER_HELPERS_SOURCE: (2_794, "be25364b30dff6d5acdd9695429b6280567a541a44856ef07935fd5d327ce4b8"),
    HW_CLOCK_ENCODE_SOURCE: (5_818, "3ecc609ac0bd37a2cc636df321644419b52d0cbc16939fc17133abf83fef7cf0"),
    STATE_RANGE_SOURCE: (12_765, "ccd29db6d561a2c57c49b11ede15576ee0de2dc633715b49785ff805cd28a095"),
    STATE_EVENT_ZERO_SOURCE: (3_987, "90321ad1e5150a4ddbd1a321638ad92f20cc81cd330f75e8ad3377c0b3c0eadc"),
    STATE_EVENT_ONE_SOURCE: (8_839, "43a5e400d060abd063b18ce00fac00a0c27f9c1d18a355973d8aa52e0ab4c7c8"),
    STATE_REGISTER_INITIALIZE_SOURCE: (6_296, "06b62fbf0e0828aa0d87134a022115973a5fe5b3541ec81d499ef48d3149e706"),
    MISC_PRIMITIVES_SOURCE: (4_007, "90d948a301d9d5ef34f8de6f9b0037f9a6abb7dc328868054520288e23b99deb"),
    DFU_IMAGE_CRC_SOURCE: (5_331, "95840f7a4cb540572823af27fa50429319749f424c7ffa6838f99f250390d511"),
    REGISTER_HELPERS_SOURCE: (7_511, "c27b18bf5dbf3ae160ce50463e3677c88e074a0bb718819898ce205ec3c7e5c0"),
    HW_EVENT_APPLY_SOURCE: (4_805, "9f70f0eb351205a28b85e53f96a4d51fa473ea7a4f6ced845082486234bb01bb"),
    CMDQ_ADAPTERS_SOURCE: (3_673, "f921a48a361f0d474781128b9ea4fe4b15a83727db472cb1178f78d66b954ff2"),
    HW_DESCRIPTOR_SOURCE: (1_650, "a3a8b458d92e6ad3e61861c7e44dfad202d5a50cd53afd70af47d60b5936365f"),
    HW_CONTEXT_CLAIM_SOURCE: (1_848, "3b46cad1c1a616d5503bfa4b592f30326f26f4fef368c138e295d3f01357c8fd"),
    HW_CONTEXT_ENABLE_SOURCE: (3_720, "4d85710f4613af13dfce38e85c2ff61e9bc94b2683573642116b0e17e2668ae2"),
    HW_EVENT_SERVICE_SOURCE: (8_225, "51c3bbd85505c2e89946ced24728ed528943a3ec02c38a0ea8c84e010fa87695"),
    HW_CONFIG_TRANSACTION_SOURCE: (7_095, "1e31cff5fb69b6256b7cb7081392364b3fd398402bad28bd30b058e902accbcf"),
    HW_INSTANCE_CONFIGURE_SOURCE: (5_381, "b5a353aff34adf56192017a1cb1f1ac0844476a69162e9725061f29217975eb9"),
    HW_CONFIG_RETRY_SOURCE: (2_454, "800e836227e6f754f325ef05134f1ffe184d5dc0f7d5175d178b212cb6a2e745"),
    PLATFORM_FINISH_SOURCE: (5_744, "03bb874a49921bcdaa6affb67930f6da9d21a433f2d93669d2629545df50f11b"),
    PLATFORM_BRINGUP_SOURCE: (5_712, "61e2cbda691e76ec07c778b09b4ecf9439e81a4c0f1df6a104e056e9773744e3"),
    DESCRIPTOR_REGISTER_SOURCE: (5_399, "fd135b632cc99651cef296f35b6e2c7ec1d8bf0dfebd6e63a2c9af05040d99c5"),
    HW_STATE_COMPOSE_SOURCE: (5_512, "7dc2091d350c71e142096fcf3b7f7c87f3b3bdd1df0be5d79f1f6bfb49288759"),
    HW_STATE_DECODE_SOURCE: (10_192, "67170ef4a1621e6a6bb564cb963fb981774fca0b906b14263bdeb755cc746ddb"),
    HW_PROFILE_APPLY_SOURCE: (2_511, "d998ef583e8df63483b3c005255b774eba898596acbcbf69fa3fc6d23bc2aa97"),
    HW_REGISTER_PROFILE_RESTORE_SOURCE: (2_930, "ced66ffb51c4ebc148e5ed32314117f89b84b4ba41d939b86412c1c0833ec35f"),
    EVENT_VALUE_PROFILE_SOURCE: (5_357, "fbe0f21e8279794d32b8b91958740ac9dc1753fc458ce3370c93a7cce19628bf"),
    REGISTER_PROFILE_TRANSFER_SOURCE: (5_748, "998df67af4570a50d2682a7b8186ba31b57a70725ca1723b08248c0fc75e18fc"),
    CHUNKED_SOURCE_COMPARE_SOURCE: (2_864, "41239ad9ae8bf2e12df17f7377ad09c38b0f70dde534f5f135838ce85852a724"),
    DFU_PAYLOAD_PROGRAM_SOURCE: (4_919, "05273a3b0cfce432b21527e377be9f8c2ac02cae862b28a00899da2f03c253f4"),
    MODE_APPLY_SOURCE: (4_417, "fe029db3a951fc9ff53e2c438560bd0df2c7716fcc238dc91fae355e56022f90"),
    CONTROL_WRAPPERS_SOURCE: (3_213, "4da52af0ccc849f743d3f2e298a33c6769b1776239faf84dbcb7d8ad2e32cd56"),
    CONTEXT_LIFECYCLE_SOURCE: (3_930, "e4b74c635f5f0e841b756900eb1d1ae9c20062a753b735a6fa6522725a2a766a"),
    EVENT_CONTROL_WRAPPERS_SOURCE: (2_109, "5f463bd5de40f968582e0198d1214125e63946ff5b128c8393eb2e4cf9ad0b0d"),
    EVENT_SETUP_SOURCE: (2_076, "f1f061f6c312116e123b3579243a79516303e092eabf32ed5ab3a883328bb170"),
    EVENT_STATE_SOURCE: (5_139, "e825a0580bf65be09b19827e8fcb43297689347d58fdbe8b769889c1ddb99b6b"),
    SMALL_SERVICES_SOURCE: (5_812, "1434af9c297fef8ae3bd4317723aa51d6fb5e7811f36da9a6919b46baef4ef71"),
    CONTROL_SERVICES_SOURCE: (5_976, "9dde955e64abee4a26392122fc0a85572791a5a3c7b09e17e00d7c97f298788b"),
    EVENT_SERVICE_LOOP_SOURCE: (3_318, "bf5d5e81f717225c2382254443964a2d4b50fa5bb8b41ce001bed83f92dca142"),
    EVENT_RUNTIME_SERVICES_SOURCE: (5_524, "9d427b3851f3680b514e5b9b02b9ed9e3cdb973b5aaf1a60dc8db4de2cdffc11"),
    CONTROL_ORCHESTRATION_SOURCE: (3_424, "96814607130a7fbac6b8c8c974b22302457c796715930fad6df4943b342f58cd"),
    DFU_SERVICE_TASK_SOURCE: (7_096, "2b34b8873824bbb361e4886933c7fc98781c150362c2fdf11c2072487d8bb3a4"),
    CONTEXT_PUBLISH_SOURCE: (1_752, "4915885eb4543890c828197dde035f13c0d987e11e9e19394391f4b9ed35d245"),
    LATE_WRAPPERS_SOURCE: (5_761, "fae82be6e3f01f260574240ffc4ad3892b3369f5e874319c5808d505cf458c5f"),
    NOOP_CALLBACKS_SOURCE: (939, "6f05f0addaef7c09b1cf28b951ad696d1ae895485b9ca1239c5e7fe60dcddd65"),
    STARTUP_SERVICES_SOURCE: (3_395, "c36332b66bfe3f4c2a0fbc064fe761896000fc674c45f63c08f7eadd5e0ebad6"),
    STARTUP_RUNTIME_SOURCE: (3_861, "ce14cbec8a9cf538be52f2c76cbd0255ae0c8ab94f179ebef9a1407c1ab3cea6"),
    ALIGNMENT_DISPATCH_SOURCE: (1_766, "018469bc245ed59ecd849971757531f0d9a5dd1125f2215f4b01f0d29fd4a0a2"),
    GUARDED_CALL_SOURCE: (2_504, "26c4cd2d2d2380931c4dc8f98ce3ef2177914f0cb92ec5f3a32e776ee433dc78"),
    HW_CONTEXT_INITIALIZE_SOURCE: (5_816, "89691e672633cd9590206a01475ebe2affd3b0c64ac886b6f606d8b3207b179b"),
    EVENT_DISPATCH_SOURCE: (3_328, "5f1102f84082416beaf905c89732103956a38e8b5776961cb836246237bda295"),
    HW_HANDLE_SOURCE: (4_839, "e4ca2c377c9fa4052ae2be95b13e1dc9acd362e9fd8ba18be05e596cc3d14649"),
    HW_COMMAND_SOURCE: (1_199, "660091c82acdcb71a8b384e0929c76e3229ad60b39957ceae3471941847cefa8"),
    CLKMGR_DIVIDER_SOURCE: (1_268, "090373ed2672073930edcf35783fc1fcd785a2a812ca10088f14d8261c8b7498"),
    HW_CHANNEL_SOURCE: (2_949, "139c7e866bc382b84b94271a24306d137fdf29dd56968fa05ecce758fc3d35a4"),
    HW_ACTIVATE_SOURCE: (1_439, "b75cff5fc5dbf72ba19ac32eabd897a2ebfaa5aa2f1e9e165b1d9b5d0ba21ab5"),
    HW_CONFIG_ENUMERATE_SOURCE: (16_137, "4bed46d7fc7a8008ef67b360d218d433a59e8df8a0a1e2d277b06899cd5b9cf6"),
    ORPHAN_SERVICES_SOURCE: (2_653, "692d609185272bb9ebc79d4342951766d02ac713f2bd8a727465e87ee5625dff"),
    AMBIQ_SOURCE: (168_473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    AMBIQ_HEADER: (36_982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    AMBIQ_LICENSE: (1_525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
    AMBIQ_PROVENANCE: (18_060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    AMBIQ_QUEUE_HEADER: (10_115, "eabc8d95b06f06c24cc160ca85e20bd2fca32d1e7b0d9c8d815b7b3f9dffd2db"),
    AMBIQ_CMDQ_HEADER: (10_496, "0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f"),
}

FUNCTIONS = {
    "open_cfw_bootloader_mspi_interrupt_service_426536": {
        "start": 0x00426536,
        "end": 0x004267FE,
        "sha256": "baf487db99da530690cd9100a3f10947ce5bbbca07dfc93cd76ff57bc87ad313",
        "upstream": "am_hal_mspi_interrupt_service",
        "main_start": 0x004C240E,
        "main_sha256": "8c43c0d8fd418e04cf808e80d00867981dc2a3eaefb23ee0227ed39538484164",
        "identical_bytes": 692,
        "difference_runs": 10,
        "callers": (0x0041FE22,),
        "provider_edges": (
            (0xEA, 0x0042403E), (0x136, 0x00422364),
            (0x16C, 0x00427A56), (0x224, 0x00423FAC),
            (0x26C, 0x00427B38), (0x278, 0x00423F8E),
            (0x288, 0x00423FAC), (0x2B8, 0x00422364),
        ),
    },
    "open_cfw_bootloader_mspi_power_control_426808": {
        "start": 0x00426808,
        "end": 0x00426BFE,
        "sha256": "80479d7c73fd0238da60b347069e233490562e35122272a235c35827f1e9084a",
        "upstream": "am_hal_mspi_power_control",
        "main_start": 0x004C26E0,
        "main_sha256": "4567f43c1d695764bc62c881fbf0bc9c3766c06e9d16d66454f1b87ec4b0ae5b",
        "identical_bytes": 985,
        "difference_runs": 15,
        "callers": (0x0041FE3E, 0x0041FE54, 0x004202AC),
        "provider_edges": (
            (0x4A, 0x0041BF84), (0x6C, 0x004222F0),
            (0x7E, 0x004249A0), (0x1EC, 0x00423F8E),
            (0x206, 0x004222F0), (0x216, 0x004249A0),
            (0x39E, 0x00423FAC), (0x3AE, 0x00426484),
            (0x3C6, 0x0041D1C0), (0x3D0, 0x0041C17A),
            (0x3DC, 0x004249A0), (0x3E6, 0x004223D8),
        ),
    },
}

POOLS = (
    (0x004267FE, 0x00426808, "f0ef1fedd08c40bdcdbac2afa7a8df77f7a1b6cebf3ccbe24145340afa295b16"),
    (0x00426BFE, 0x00426C10, "6d01aee7b0ea94693ad3e39e729d72dbdcf694fa0bb121442d026ca719b3d5c4"),
)

MEMSET_WRAPPER = {
    "function": "open_cfw_bootloader_memset_wrapper_426c10",
    "start": 0x00426C10,
    "source_end": 0x00426C22,
    "stock_end": 0x00426C24,
    "source_sha256": "1c4612755ef55e81387435e55bfbf79f2109770fae78aaf4614c4f846454ef16",
    "unrelocated_sha256": "766caf7569f0d310a934131ddd3af23500a17678c2cf6a0322421a49040e6fa5",
    "stock_prefix_sha256": "fb07be70e8d139355932bbbe2c71ca78530a5de811e775dc36b8858d91dbdec2",
    "tail_sha256": "d61f3ece088ca2fb6ebd3f47479ea5514bdbc39d0decd1f678f629b107878331",
    "callers": (0x00420014, 0x0042001E, 0x004201C4, 0x00420756,
                0x00420808, 0x0042E330, 0x0042E35A),
    "relocation_offset": 10,
    "provider": 0x0041560C,
}

HFADJ = {
    "function": "open_cfw_bootloader_clkgen_hfadj_enable_426c58",
    "start": 0x00426C58,
    "source_end": 0x00426C70,
    "stock_end": 0x00426C72,
    "source_sha256": "99885c04446f3fcda269491e2333194b1dd622219fd089f214ef80d90eab6d8b",
    "unrelocated_sha256": "99885c04446f3fcda269491e2333194b1dd622219fd089f214ef80d90eab6d8b",
    "stock_prefix_sha256": "5d37a30b859898aa9c5de9a9d41f97e12755878b88dcf8cf1a563eefa7ba1ca7",
    "tail_sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
    "callers": (0x00421DE2, 0x00421E18, 0x00421E7E),
    "register": 0x40004044,
}

HFADJ_CONFIG = {
    "function": "open_cfw_bootloader_clkgen_hfadj_config_426c72",
    "start": 0x00426C72,
    "end": 0x00426C7E,
    "cave_start": 0x00426C28,
    "cave_end": 0x00426C38,
    "source_sha256": "6b7094edd081661f3d3b8dbadef0e2e684b2bb3e22a31afcc992735020f54395",
    "stock_sha256": "2d973a6679b7557ee0db61ece3b5e87083256d7f60d653509001616459a23d5f",
    "generated_nop_sha256": "03931d66430ab23fe23dbc5aab43fd468a688b1cf0fc8a0cbaf64370e53da4d8",
    "callers": (0x0042176E, 0x0042177E, 0x00421DF6),
    "register": 0x40004020,
}

HFADJ_DISABLE = {
    "function": "open_cfw_bootloader_clkgen_hfadj_disable_426c7e",
    "start": 0x00426C7E,
    "end": 0x00426C8C,
    "cave_start": 0x00426C38,
    "cave_end": 0x00426C4C,
    "source_sha256": "9d601bd72990a9265dfb4d31794c6751e6ea0b84d1d647c5f6bbf7f1d18a8786",
    "stock_sha256": "f71be3e40ad49d191903a723ecf4416161e4f3be2aac50d1ee559eb19b73579e",
    "generated_nop_sha256": "e1debb332620b616da1501933af843054244f90e8f280da8d4a2db30c83064af",
    "callers": (0x00421764, 0x0042178E),
    "register": 0x40004020,
}

DUAL_SWITCH = {
    "function": "open_cfw_bootloader_dual_switch_426c8c",
    "start": 0x00426C8C,
    "source_end": 0x00426CC4,
    "stock_end": 0x00426CCC,
    "source_sha256": "877df9e6e2cba9faa0c6435ae1aea24d3b3162b3a0613947c1a81154a9059426",
    "unrelocated_sha256": "3a619bebf32afbd0f49259f3806b0d96b4024b70eab48eb36b621ef0d54def0f",
    "stock_prefix_sha256": "d5b82fd57ea541895d00b663f98123f4999e8a71c722a9392af2172cf31cd359",
    "tail_sha256": "d7d2a4025d26ea346c59aacce99c433ac393769f80658c1d6586235cda9af704",
    "callers": (0x00421FB4, 0x00421FDE, 0x004220A4),
    "register": 0x40004044,
    "status_register": 0x40004030,
    "poll_mask": 0x01000000,
    "relocation_offset": 36,
    "provider": 0x0041D246,
}

CLKGEN_CONFIG = {
    "function": "open_cfw_bootloader_clkgen_config_426ccc",
    "start": 0x00426CCC,
    "end": 0x00426D1E,
    "cave_start": 0x00415BFC,
    "cave_end": 0x00415C50,
    "source_sha256": "eca58d33f0d33fdefcc0b3f30c8988a2986c6ed4d713b4a081cacf9f9f7fc2d9",
    "stock_sha256": "c9ec02c292145c709613ed59045b804cbe0e697d86c83ed579bd2e3075a49b62",
    "generated_nop_sha256": "78680bf9577c12058eebdcfd3143188ebe75c9159a69de6bbc1f7c1e6af675a4",
    "callers": (0x00421928, 0x00421FC6),
    "control_register": 0x40004020,
    "mode_register": 0x4000404C,
    "divider_register": 0x40004048,
}

CLKGEN_DISABLE = {
    "function": "open_cfw_bootloader_clkgen_disable_426d1e",
    "start": 0x00426D1E,
    "end": 0x00426D2C,
    "cave_start": 0x00415C50,
    "cave_end": 0x00415C64,
    "source_sha256": "cbe1ab0d26505fa34fdac078e0935015001b2f3138109d8bad340acef1bbb48a",
    "stock_sha256": "b6e29296fa925d2ee116e96d5fa22e60265cdccedfe9072766a7adf69042a70e",
    "generated_nop_sha256": "e1debb332620b616da1501933af843054244f90e8f280da8d4a2db30c83064af",
    "callers": (0x0042191E, 0x00422082),
    "register": 0x40004050,
}

FLOAT_GCD = {
    "function": "open_cfw_bootloader_float_gcd_426d48",
    "start": 0x00426D48,
    "end": 0x00426DB2,
    "cave_start": 0x00415C64,
    "cave_end": 0x00415CC0,
    "source_sha256": "5f1d08b32b7c2291eabdff7d7ab4b17d63b265f827338acf974af4f67c082d5c",
    "unrelocated_sha256": "650ac1e603da47c895eecf060ce578e346835c18ae8c4720fe99a3aca4798b03",
    "stock_sha256": "f6d214ecce42adb7ca36928d8d457c2d6c18af45c10cc68da953d3252290eeed",
    "generated_nop_sha256": "1ada4421375156f3c85d8815147e5a5b537361f173f9bbe6d84fd8cf6dcf3612",
    "callers": (0x00426DCE, 0x0042706C),
    "provider": 0x00427C90,
    "stock_provider_offset": 0x2E,
    "relocation_offset": 54,
    "main_start": 0x0053937C,
    "main_sha256": "68ed00de682751c45f369fb4a471726617f8dd395cdbe31c583675f97d216a76",
    "identical_bytes": 102,
    "difference_runs": 1,
}

FLOAT_RATIO = {
    "function": "open_cfw_bootloader_float_ratio_426db4",
    "start": 0x00426DB4,
    "end": 0x00426EAC,
    "cave_start": 0x00415CD4,
    "cave_end": 0x00415DD0,
    "source_sha256": "cd5568ffb4b2c273bf85947cf4aa4fdf8441eba18c6a3b5d16e59b1340f086e3",
    "unrelocated_sha256": "da4c93662605a83943051f4f8385c2e2d767a0bcecfd5789eb732c0c3fb39156",
    "stock_sha256": "4082869f6c1884fe571d7d8335b2fc32ee6326cfb02b78d01f07c1da5bacc3dd",
    "generated_nop_sha256": "35115c6b08252d7d882dbd5c0d2a1bc15e6dd1fd73a933365788c57b10ff1142",
    "callers": (0x00426FC8,),
    "stock_provider_edges": (
        (0x1A, 0x00426D48),
        (0x44, 0x00427CCC),
        (0x56, 0x00427D98),
        (0x70, 0x00427D98),
        (0x84, 0x00427CCC),
        (0x96, 0x00427D98),
        (0xB0, 0x00427D98),
    ),
    "relocations": (
        (26, "open_cfw_bootloader_float_gcd_426d48", 0x00415C64),
        (60, "open_cfw_bootloader_fmodf_427ccc", 0x00427CCC),
        (82, "open_cfw_bootloader_roundf_427d98", 0x00427D98),
        (108, "open_cfw_bootloader_roundf_427d98", 0x00427D98),
        (124, "open_cfw_bootloader_fmodf_427ccc", 0x00427CCC),
        (142, "open_cfw_bootloader_roundf_427d98", 0x00427D98),
        (172, "open_cfw_bootloader_roundf_427d98", 0x00427D98),
    ),
    "main_start": 0x005393E8,
    "main_sha256": "c48f6d43d2baa55b03cec16a20fa64d487069e7dfda08354ee163b2024b91580",
    "identical_bytes": 230,
    "difference_runs": 12,
}

FLOAT_MULTIPLIER = {
    "function": "open_cfw_bootloader_float_multiplier_426eac",
    "start": 0x00426EAC,
    "end": 0x00426F6A,
    "cave_start": 0x00415DE4,
    "cave_end": 0x00415EA4,
    "source_sha256": "31c6cef0307e4b967a1528c06e5b9d8dc8d37be1dbf651f2cf76a6a9eed58004",
    "unrelocated_sha256": "3bed1abbdaa0269020d633558de15214c147f98916119dee54d1f1ea054d240a",
    "stock_sha256": "d289cc7f7ccd0c61ba49a4bf7c176573ceebe7d8725720ac00459716c6852cad",
    "generated_nop_sha256": "1f64c0965b2ea24234d91acb6bb5d2bc283f85a3afa7368f72fec6aa950cf104",
    "callers": (0x00426FE6,),
    "stock_provider_edges": (
        (0x2A, 0x00427DD0),
        (0x62, 0x00427CCC),
        (0x6E, 0x00427D98),
        (0x7A, 0x00427C90),
        (0x9E, 0x00427C90),
    ),
    "relocations": (
        (24, "open_cfw_bootloader_ceilf_427dd0", 0x00427DD0),
        (82, "open_cfw_bootloader_fmodf_427ccc", 0x00427CCC),
        (94, "open_cfw_bootloader_roundf_427d98", 0x00427D98),
        (106, "open_cfw_bootloader_floorf_427c90", 0x00427C90),
        (140, "open_cfw_bootloader_floorf_427c90", 0x00427C90),
    ),
    "main_start": 0x005394E0,
    "main_sha256": "5a1e7e7a8314532a36fd1b59a8f75d13d041bfbc1bb4fa75fa8c5949fac37562",
    "identical_bytes": 173,
    "difference_runs": 8,
}

FLOAT_SELECT = {
    "function": "open_cfw_bootloader_float_encoding_select_426f6c",
    "start": 0x00426F6C,
    "end": 0x00427032,
    "cave_start": 0x00415EA4,
    "cave_end": 0x00415F58,
    "source_sha256": "685316ba4585568c3b023923927fe0ef5a399ac92f00c44c8eaa3f3a24ac6b2b",
    "unrelocated_sha256": "f11042d808bd89e9c9d73ef6f277c6330927f2d9f29b05fdf699dfa2e74b24bd",
    "stock_sha256": "fabedc0c5c95c2523e6f867830085f0eb2c20e3f5798998b0e4aaa82bd57615d",
    "generated_nop_sha256": "3ea1e28dddc8cbb23a73a2ac2efe6d62bb3556cf709480255b307bb38bc4b7e4",
    "callers": (0x0042710C,),
    "stock_provider_edges": (
        (0x5C, 0x00426DB4),
        (0x7A, 0x00426EAC),
    ),
    "relocations": (
        (74, "open_cfw_bootloader_float_ratio_426db4", 0x00426DB4),
        (106, "open_cfw_bootloader_float_multiplier_426eac", 0x00426EAC),
    ),
    "main_start": 0x005395A0,
    "main_sha256": "fabedc0c5c95c2523e6f867830085f0eb2c20e3f5798998b0e4aaa82bd57615d",
    "identical_bytes": 198,
    "difference_runs": 0,
    "lower_literal": (0x0042715C, 0x42700000),
    "upper_literal": (0x0042703C, 0x44700001),
    "high_rate_literal": (0x00427308, 0x43700000),
}

SYSPLL_MIN_FVCO = {
    "function": "open_cfw_bootloader_syspll_min_fvco_427040",
    "start": 0x00427040,
    "end": 0x0042714C,
    "cave_start": 0x00427048,
    "apple_cave_end": 0x0042713C,
    "linux_cave_end": 0x00427140,
    "stock_sha256": "7fc066eeef20eeb8b3bf91c3746fdeac37b6eaabc66d004de1757ad005436422",
    "callers": (0x0042717C, 0x00427198),
    "stock_provider_edges": (
        (0x2C, 0x00426D48),
        (0xCC, 0x00426F6C),
    ),
    "table": (0x00431E70, 50,
              "eec288afd4c4718fd828dcd3fc872415da36c37a28fc073baec9d5694121a51c"),
    "main_start": 0x00539674,
    "main_sha256": "5201f63f7bae7d9edb540b6bb017305f736e690534eeb89ed90f356fcca31280",
    "identical_bytes": 260,
    "difference_runs": 4,
    "profiles": {
        "apple-clang": {
            "size": 244,
            "sha256": "2f01d112c0d1cdf4c0fa10048d434dd69d2331f84494f9949b6491a3dcff43f3",
            "unrelocated_sha256": "3d95c81f87d66151b4ba8996fec4cdeca127f507e5cc5f6fbc2ac400334f145a",
            "relocations": ((48, 0x00426D48), (164, 0x00426F6C)),
        },
        "linux-clang": {
            "size": 248,
            "sha256": "8f45b7a2175a9b9a1a99c07f96320b28ebacfa74b7a94e8bca19c876e50af358",
            "unrelocated_sha256": "c20352ecf0ad5176fb636545ed632981bea2c6ec35108b0c31a098fb1498b7f1",
            "relocations": ((52, 0x00426D48), (166, 0x00426F6C)),
        },
    },
}

SYSPLL_POSTDIV = {
    "function": "open_cfw_bootloader_syspll_postdiv_427160",
    "start": 0x00427160,
    "end": 0x004272AC,
    "cave_start": 0x00427168,
    "cave_end": 0x00427274,
    "stock_sha256": "7f3f9f3bbe5797d7db00b7ec229994ebd4a5e96e8a37889214e1d058de50558f",
    "callers": (0x004219AA,),
    "stock_provider_edges": ((0x1C, 0x00427040), (0x38, 0x00427040)),
    "interior_halfword_false_decodes": {
        0x0042716A: (0x00420132,),
        0x004271B8: (0x00420180,),
    },
    "tables": (
        (0x00433CB8, 16,
         "8dc1585615ae5ce6a2b8fe2fcde6d582d5b704c59382cc1d2b3bd953b8383d28"),
        (0x00433CC8, 16,
         "b71376a2c8f8bd0dde154022f58cb7e61872ce85a4622ac436b92c16cdf45930"),
    ),
    "main_start": 0x00539794,
    "main_sha256": "a436b072488dc3f19e2bab81b60a33b352b49f2ff86b5363337a98a7811ceffd",
    "identical_bytes": 316,
    "difference_runs": 8,
    "profiles": {
        "apple-clang": {
            "size": 268,
            "sha256": "37392e154a61d40029493ea8d68e384968a3923a95cfc5b20f7a8fcc33009a89",
            "unrelocated_sha256": "0e26e6e5e442d815f595decbef4f97d3c009e8b93f66a92ad8e95125e94991d4",
        },
        "linux-clang": {
            "size": 268,
            "sha256": "d006d16c7a05df73f368051d52c662ddd10fe15be369ee3b1a27de80bf308e1b",
            "unrelocated_sha256": "43f9f1b5016c186e3d7e02f32b2d212bcd690a2e92ea7f0ff9ab951c6c9a02aa",
        },
    },
    "relocations": ((20, 0x00427048), (38, 0x00427048)),
}

SYSPLL_INITIALIZE = {
    "function": "open_cfw_bootloader_row6_create_4272ac",
    "start": 0x004272AC,
    "end": 0x00427308,
    "cave_start": 0x004272B4,
    "cave_end": 0x004272F0,
    "stock_sha256": "3284295a51640dd35e9518837d69df3369ff537705ef07e88586fb2a0f8a1414",
    "callers": (0x0042215E,),
    "stock_provider_edges": ((0x4E, 0x0041CA5C),),
    "state_literal": (
        0x004275A4, 0x20027010,
        "f14031f7f4ab831f8796faf88fd60abc9862157144c8323dc0fc87344c564f5c",
    ),
    "magic_literal": (
        0x004275A8, 0x00504C30,
        "0316b8f8552e5da7138d905d0738f73b207f3bdf980ca5bcd3afbae0c653bc63",
    ),
    "main_start": 0x005398E0,
    "main_sha256": "344102274cb76e2a8e22e731aeb54f9905ff60611af472e0f2651fa87da23230",
    "identical_bytes": 86,
    "difference_runs": 4,
    "profiles": {
        "apple-clang": {
            "size": 60,
            "sha256": "14ec1958a36f051655ae9420ae0574fd83c9773848760f0592be766725004716",
            "unrelocated_sha256": "64d2229baba9bb087b18085b981384b12128878de3b8e3fae89769f5b9d4a444",
        },
        "linux-clang": {
            "size": 60,
            "sha256": "14ec1958a36f051655ae9420ae0574fd83c9773848760f0592be766725004716",
            "unrelocated_sha256": "64d2229baba9bb087b18085b981384b12128878de3b8e3fae89769f5b9d4a444",
        },
    },
    "relocations": ((34, 0x0041CA5C),),
}

SYSPLL_DEINITIALIZE = {
    "function": "open_cfw_bootloader_row6_destroy_427310",
    "start": 0x00427310,
    "end": 0x00427360,
    "stock_sha256": "1eba50a003fd2dbc10b692f916c95ac832659ee8245f1420e20cf06373631424",
    "callers": (0x00422198, 0x00422266),
    "stock_provider_edges": (
        (0x2C, 0x004273DC),
        (0x34, 0x0041CAE8),
        (0x40, 0x0041CAA2),
    ),
    "magic_literal": (
        0x004275AC, 0x01504C30,
        "c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e",
    ),
    "main_start": 0x00539944,
    "main_sha256": "15762cbfef691f5bc58b02426033212a57b18b62f4f594a1c40167790a83629c",
    "identical_bytes": 74,
    "difference_runs": 5,
    "profiles": {
        "apple-clang": {
            "size": 80,
            "sha256": "cadcef39ea58cdba4a2059dd41ca75ed8c569d6cc3edf941d8a321dc4a343189",
            "unrelocated_sha256": "613b87866651212d7ea0584e9fe70602aedce9203e096caa825b3f84d6538ddd",
        },
        "linux-clang": {
            "size": 80,
            "sha256": "cadcef39ea58cdba4a2059dd41ca75ed8c569d6cc3edf941d8a321dc4a343189",
            "unrelocated_sha256": "613b87866651212d7ea0584e9fe70602aedce9203e096caa825b3f84d6538ddd",
        },
    },
    "relocations": (
        (38, 0x004273DC),
        (48, 0x0041CAE8),
        (60, 0x0041CAA2),
    ),
}

SYSPLL_ENABLE = {
    "function": "open_cfw_bootloader_row6_start_427360",
    "start": 0x00427360,
    "end": 0x004273DC,
    "cave_start": 0x00427364,
    "stock_sha256": "0d2de1918fa403072986f15453ed612b3afd5383b89bdd95e8bf599ddb454280",
    "callers": (0x0042217E,),
    "literals": (
        (0x004275AC, 0x01504C30,
         "c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e"),
        (0x004275B0, 0x40020060,
         "9e716c73f2c165d5a9f66515fea66d1acfffac7b1bab8906b32675e252374fd3"),
        (0x004275B4, 0x400204D8,
         "8cba1aba74ea90d21f5c2640749a269f8d161506670ca249ce166a6080f8b8a5"),
    ),
    "main_start": 0x00539994,
    "main_sha256": "40618d8ed60a8a9e45079e8778a8e124d20fcfb5b317674574f21025b943963a",
    "identical_bytes": 118,
    "difference_runs": 3,
    "profiles": {
        "apple-clang": {
            "size": 84,
            "sha256": "b34095d709ec4b90846d9882ee05a2ce47a181166de1e90cba70998e23d1bebe",
            "unrelocated_sha256": "b34095d709ec4b90846d9882ee05a2ce47a181166de1e90cba70998e23d1bebe",
        },
        "linux-clang": {
            "size": 84,
            "sha256": "b34095d709ec4b90846d9882ee05a2ce47a181166de1e90cba70998e23d1bebe",
            "unrelocated_sha256": "b34095d709ec4b90846d9882ee05a2ce47a181166de1e90cba70998e23d1bebe",
        },
    },
}

SYSPLL_DISABLE = {
    "function": "open_cfw_bootloader_row6_stop_4273dc",
    "start": 0x004273DC,
    "end": 0x0042740C,
    "stock_sha256": "18fb22183427c03dff67cd845829f31b77a1cf974c0c91eda17e83308934dc73",
    "source_sha256": "6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb",
    "callers": (0x00422260, 0x0042733C),
    "literals": (
        (0x004275AC, 0x01504C30,
         "c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e"),
        (0x004275B4, 0x400204D8,
         "8cba1aba74ea90d21f5c2640749a269f8d161506670ca249ce166a6080f8b8a5"),
    ),
    "main_start": 0x00539A10,
    "main_sha256": "f45a5402b99d6dad3fc6f6549fbf6b229ecb2d30de69ac3e08e77b133d25e132",
    "identical_bytes": 44,
    "difference_runs": 2,
    "profiles": {
        "apple-clang": {
            "size": 48,
            "sha256": "6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb",
            "unrelocated_sha256": "6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb",
        },
        "linux-clang": {
            "size": 48,
            "sha256": "6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb",
            "unrelocated_sha256": "6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb",
        },
    },
}

SYSPLL_CONFIGURE = {
    "function": "open_cfw_bootloader_row6_configure_42740c",
    "start": 0x0042740C,
    "end": 0x00427522,
    "cave_start": 0x00427410,
    "stock_sha256": "61aad9e2393f589de90e10cd74396e589ee4aa1547947732738abb105a1ba2af",
    "callers": (0x00422170,),
    "stock_provider_edges": ((0xEE, 0x0041AC92),),
    "literals": (
        (0x004275AC, 0x01504C30,
         "c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e"),
        (0x004275B4, 0x400204D8,
         "8cba1aba74ea90d21f5c2640749a269f8d161506670ca249ce166a6080f8b8a5"),
        (0x004275B8, 0x400204DC,
         "ea88e026690dfd524de76bc2fd05aa0027dbeeb5ee1ddf72a5852ba1a7863101"),
        (0x004275BC, 0x400204E0,
         "a1fec26018410775e68659cdb3343b403d2846cd5f22f7c598cebfc25deabece"),
    ),
    "main_start": 0x00539A40,
    "main_sha256": "952498aa439122aadd5548d9bb261e5fcee1bae570e7b71931464f86c69ac010",
    "identical_bytes": 267,
    "difference_runs": 6,
    "profiles": {
        "apple-clang": {
            "size": 240,
            "sha256": "916771eadfbe45eb61d244376c14bb1354fe5bc7162003d6c5951189e8e8c876",
            "unrelocated_sha256": "127fc318fdac8cc7881027d87e146dd896ca99cbcbc66b081b78536454575f56",
        },
        "linux-clang": {
            "size": 240,
            "sha256": "d8ae9445de5140e0eaaf0015769ce6ad1cd6a5ad20bc2b5770b2932eabbf07f8",
            "unrelocated_sha256": "8aef5f3032b7f781231e9f640e9eeb701d50485d651bb54f3361127f4a564a7d",
        },
    },
}

SYSPLL_LOCK_WAIT = {
    "function": "open_cfw_bootloader_row6_lock_wait_427522",
    "start": 0x00427522,
    "end": 0x00427588,
    "cave_start": 0x00427528,
    "stock_sha256": "978d2a48a7b3971bfb7e0d4f2006836aeacb4c137467dfead90d41377316be3e",
    "callers": (0x00422202,),
    "stock_provider_edges": ((0x60, 0x0041D246),),
    "literals": (
        (0x004275AC, 0x01504C30,
         "c9767509276a128588c8373a4e0a1757b7e97633a7a1cc7cabbc92cd5f260a6e"),
        (0x004275B4, 0x400204D8,
         "8cba1aba74ea90d21f5c2640749a269f8d161506670ca249ce166a6080f8b8a5"),
        (0x004275BC, 0x400204E0,
         "a1fec26018410775e68659cdb3343b403d2846cd5f22f7c598cebfc25deabece"),
        (0x004275C0, 0x400204E4,
         "037d9b06ee7c4f7e0c0102835dccbc4cc27c27fb97d75b84012427195972f87e"),
    ),
    "main_start": 0x00539B56,
    "main_sha256": "e1998b485572e20fb3a2118c8c8f01427e112d268308baf41299ace6849d8a11",
    "identical_bytes": 96,
    "difference_runs": 6,
    "profiles": {
        "apple-clang": {
            "size": 88,
            "sha256": "9c751242434d7fd769e8e36600f944014899537ff9613fce57cdc500fc71d629",
            "unrelocated_sha256": "2fd5a60b6794c0bcb8836a1b80d858d8fc70e6c91a7e1e77180b3cd350790b9b",
        },
        "linux-clang": {
            "size": 88,
            "sha256": "9c751242434d7fd769e8e36600f944014899537ff9613fce57cdc500fc71d629",
            "unrelocated_sha256": "2fd5a60b6794c0bcb8836a1b80d858d8fc70e6c91a7e1e77180b3cd350790b9b",
        },
    },
}

QUEUE_FUNCTIONS = {
    "queue_init": {
        "function": "open_cfw_bootloader_queue_init_4275ea",
        "start": 0x004275EA,
        "end": 0x00427602,
        "cave_start": 0x004275F0,
        "stock_sha256": "142ce77e922601c4cf495ab896455263777d8088987c0f783477ea4aceff059f",
        "generated_nop_sha256": "bc918b52c356ecbb78652ef17d9bc3feb8cd8bdc97cd50648bd9ced7f9fbf066",
        "callers": (0x00422E04, 0x00422E20),
        "stock_provider_edges": (),
        "relocations": (),
        "main_start": 0x0053006C,
        "main_sha256": "142ce77e922601c4cf495ab896455263777d8088987c0f783477ea4aceff059f",
        "identical_bytes": 24,
        "difference_runs": 0,
        "profiles": {
            "apple-clang": {
                "size": 18,
                "sha256": "7c41f3e3bb6b211f6eb2e8f5d115063d1bd80f4541c0ed2d89e64dc89032d4b9",
                "unrelocated_sha256": "7c41f3e3bb6b211f6eb2e8f5d115063d1bd80f4541c0ed2d89e64dc89032d4b9",
            },
            "linux-clang": {
                "size": 18,
                "sha256": "0f1e402222fe9a765b68dd7f50e91dfaba7c0f4c9c2f67fe9bfb26429890d5a3",
                "unrelocated_sha256": "0f1e402222fe9a765b68dd7f50e91dfaba7c0f4c9c2f67fe9bfb26429890d5a3",
            },
        },
    },
    "queue_item_add": {
        "function": "open_cfw_bootloader_queue_item_add_427602",
        "start": 0x00427602,
        "end": 0x00427660,
        "cave_start": 0x00427608,
        "stock_sha256": "80fc90006d26902783880b56b7c04c351369282c1624a401c680e6bc66cde1e6",
        "generated_nop_sha256": "81985b95ea146b40ae726cfcda67d4438bf38661716a6c752848ded2b4495686",
        "callers": (0x00423378, 0x00423568),
        "stock_provider_edges": ((0x10, 0x0041B8EC),),
        "relocations": ((0x0E, 0x0041B8EC),),
        "main_start": 0x00530084,
        "main_sha256": "c6b8143eef5ee3a1a9d3b0cf063519996fc93975020a6797fe058e1b0d9851fb",
        "identical_bytes": 91,
        "difference_runs": 2,
        "profiles": {
            "apple-clang": {
                "size": 88,
                "sha256": "6d3eae77835f295febb980b300e6f66fcc62653214e517d9977561d390c6bdb8",
                "unrelocated_sha256": "6f9f119d3e32eab3d48671f33045e78bb57faea99366b9d71557965e7014ad7f",
            },
            "linux-clang": {
                "size": 88,
                "sha256": "6964d4faaf1d8c03d31fa51a259b7e56512f44f4d5ec6a72ca8c818e1e8d7840",
                "unrelocated_sha256": "680d4b0e62053340611e93ea3badf1e3d0f7da3f745b8c78f2ada66f3cffad98",
            },
        },
    },
    "queue_item_get": {
        "function": "open_cfw_bootloader_queue_item_get_427660",
        "start": 0x00427660,
        "end": 0x004276BA,
        "cave_start": 0x00427664,
        "stock_sha256": "6c63753c5d95abac9183eb00ec419aaf3240dceba70170b3a377e7e8ada137b2",
        "generated_nop_sha256": "998e9cb0986a0831d2a02119caf8ac4dd6e6b46f0e7017672dba2c2c0342c490",
        "callers": (0x004233BA, 0x00423656),
        "stock_provider_edges": ((0x10, 0x0041B8EC),),
        "relocations": ((0x0E, 0x0041B8EC),),
        "main_start": 0x005300E2,
        "main_sha256": "e2932949d162fdcd16af02aeccd6a5bdbab5c32a26ce9d3016c592a1a34c86a6",
        "identical_bytes": 87,
        "difference_runs": 2,
        "profiles": {
            "apple-clang": {
                "size": 86,
                "sha256": "c793d2e2dec7fbe5b17fbdb3539d719318faed1b971738295bb4d0d9724014f2",
                "unrelocated_sha256": "626394cf850e2a359004272a45ba1127f97a3f315a0d8f7895585bcc844a0c01",
            },
            "linux-clang": {
                "size": 86,
                "sha256": "721e19cdf487465342ba25c62bd2b99c3b657af073370d17b2d7ebf2851276d8",
                "unrelocated_sha256": "b5e30d611fc153d986b95cb557e877caa4368dc1dd5f95a53105b8473a680f24",
            },
        },
    },
}

QUEUE_UPSTREAM_SOURCE_SHA256 = "2ca55e34d5b9d4843e32ce0ab24e312bde580716c708c7f017adcd0a12dbd1e4"

MEMMOVE = {
    "function": "open_cfw_bootloader_memmove_4276bc",
    "start": 0x004276BC,
    "end": 0x00427752,
    "cave_start": 0x004276C0,
    "stock_sha256": "7ef3c825f46fa907a46b09880629b6ae49eace45319bd4beb74b9ff70d136137",
    "generated_nop_sha256": "7eeabd87f2596432c784ffa17a9032e823365584f2782f98ab91eb72d04c589e",
    "alignment_end": 0x00427754,
    "alignment_sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
    "callers": (0x0042395A,),
    "copy_provider_offset": 0x08,
    "copy_provider": 0x0041568C,
    "main_start": 0x00439710,
    "main_sha256": "31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28",
    "main_copy_provider": 0x00439BE4,
    "identical_bytes": 146,
    "difference_runs": 1,
    "profiles": {
        "apple-clang": {
            "size": 50,
            "sha256": "22a53bbac7dcb82baafe7b2907d4d94b2e4135eccb0395c9b83e37dbf79916db",
            "unrelocated_sha256": "22a53bbac7dcb82baafe7b2907d4d94b2e4135eccb0395c9b83e37dbf79916db",
        },
        "linux-clang": {
            "size": 50,
            "sha256": "22a53bbac7dcb82baafe7b2907d4d94b2e4135eccb0395c9b83e37dbf79916db",
            "unrelocated_sha256": "22a53bbac7dcb82baafe7b2907d4d94b2e4135eccb0395c9b83e37dbf79916db",
        },
    },
}

CMDQ_UPDATE = {
    "function": "open_cfw_bootloader_cmdq_update_indices_427754",
    "start": 0x00427754,
    "end": 0x00427794,
    "cave_start": 0x00427758,
    "stock_sha256": "8a2b2f4d159d6c4d3ec68b81c254a81c976d757dc1c9d57319649cacf6c65317",
    "generated_nop_sha256": "151a3e72535ae94b26470f02412dd0a1853bfc0ae551c4940c9e012ba4e3e30c",
    "generated_fill_sha256": "03931d66430ab23fe23dbc5aab43fd468a688b1cf0fc8a0cbaf64370e53da4d8",
    "callers": (0x00427944, 0x00427A7C, 0x00427AF2),
    "critical_provider_offset": 0x04,
    "critical_provider": 0x0041B8EC,
    "main_start": 0x00538D18,
    "main_sha256": "b509adac0c08c9239aabb77c270b559aa76cd2b797bc473f2d0d01a22e3c2837",
    "main_critical_provider": 0x00473940,
    "identical_bytes": 61,
    "difference_runs": 2,
    "upstream_source_sha256": "60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83",
    "upstream_source_blob": "0a286e565cad27cef801c389b5dedae826a2669a",
    "profiles": {
        "apple-clang": {
            "size": 44,
            "sha256": "e585f8d2fb16a83c80a7f76234bfe30e7ff3002e2837d8a7bb0475765cf4b160",
            "unrelocated_sha256": "539135b8807209605e2ff79f606b8a80b2d1780a4b629a32d00ed044a3396fce",
        },
        "linux-clang": {
            "size": 44,
            "sha256": "c8d7d16687b05815d24d6e0492e6ad500bb4845b9ce070db8c8063a294628911",
            "unrelocated_sha256": "aaad8061463e298db6d3dbf11a66957e34b3a49985d0980a51f0c73b4526ef2a",
        },
    },
}

CMDQ_SERVICES = {
    function: {
        "function": function,
        "start": start,
        "end": end,
        "stock_sha256": stock_sha256,
        "call_offset": call_offset,
        "profiles": {
            "apple-clang": {
                "size": apple[0],
                "sha256": apple[1],
                "unrelocated_sha256": apple[2],
                "stock_sha256": apple[3],
            },
            "linux-clang": {
                "size": linux[0],
                "sha256": linux[1],
                "unrelocated_sha256": linux[2],
                "stock_sha256": linux[3],
            },
        },
    }
    for function, start, end, stock_sha256, call_offset, apple, linux
    in CMDQ_SERVICE_SPECS
}

FLOAT_MATH = {
    function: {
        "function": function,
        "start": start,
        "end": end,
        "stock_sha256": stock_sha256,
        "source": source,
        "size": size,
        "sha256": linked_sha256,
        "unrelocated_sha256": unrelocated_sha256,
        "stock_prefix_sha256": stock_prefix_sha256,
        "target": target,
    }
    for (function, start, end, stock_sha256, source, size, linked_sha256,
         unrelocated_sha256, stock_prefix_sha256, target) in FLOAT_MATH_SPECS
}

FLOAT_MATH_CALLERS = {
    "open_cfw_bootloader_floorf_427c90": (0x00426D76, 0x00426F26, 0x00426F4A),
    "open_cfw_bootloader_floor_bits_427ca0": (0x00427C96,),
    "open_cfw_bootloader_fmodf_427ccc": (0x00426DF8, 0x00426E38, 0x00426F0E),
    "open_cfw_bootloader_fmod_bits_427cdc": (0x00427CD2,),
    "open_cfw_bootloader_roundf_427d98": (
        0x00426E0A, 0x00426E24, 0x00426E4A, 0x00426E64, 0x00426F1A,
    ),
    "open_cfw_bootloader_round_bits_427da8": (0x00427D9E,),
    "open_cfw_bootloader_ceilf_427dd0": (0x00426ED6,),
    "open_cfw_bootloader_ceil_bits_427de0": (0x00427DD6,),
    "open_cfw_bootloader_float_range_classify_427e0c": (0x0042A9E2,),
}

SPOTMGR_TRANSITION = {
    "function": "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378",
    "start": 0x00428378,
    "end": 0x004283E2,
    "sha256": "051e40c208a75b89a9826c46a5fcea7b9933f1de7c90f4acc01777ba1ed16866",
    "unrelocated_sha256": "35a3808a2b454603a347435c52e5e0c1e04e37e6101a6e9948e37fde60242a8f",
    "relocation_offset": 54,
    "provider": 0x0041D1C0,
    "callers": (0x0042A05C,),
    "shared_literals": (
        (0x00428A90, 0x200270B4), (0x00428BA8, 0x4002004C),
        (0x00428C84, 0x40020044), (0x00428C88, 0x2000055A),
        (0x00428C90, 0x200270B8), (0x00428C94, 0x200270BC),
        (0x00428C98, 0x200270B0), (0x00428C9C, 0x4002037C),
        (0x00428CA0, 0x40020080),
    ),
}

SPOTMGR_TRANSITION_7B = {
    "function": "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94",
    "start": 0x00428A94,
    "end": 0x00428BA8,
    "sha256": "1e0e7ddb0036670d692a97a50f6cc821d2a2358e741b72d502e943d31bb0b351",
    "unrelocated_sha256": "b9d0e8cfa43d1d1a1514e2ff0fda56c2b0d50511f816d53894b19f7feb3975d8",
    "callers": (0x0042A068,),
    "relocations": (
        (0x2E, "open_cfw_bootloader_delay_us_41d1c0", 0x0041D1C0),
        (0x64, "open_cfw_bootloader_delay_us_41d1c0", 0x0041D1C0),
        (0xB4, "open_cfw_bootloader_delay_us_41d1c0", 0x0041D1C0),
        (0xC6, "open_cfw_bootloader_delay_us_status_change_41d21c", 0x0041D21C),
        (0xEA, "open_cfw_bootloader_delay_us_41d1c0", 0x0041D1C0),
    ),
    "shared_literals": (
        (0x00428C84, 0x40020044), (0x00428C98, 0x200270B0),
        (0x00428CA0, 0x40020080), (0x00428C94, 0x200270BC),
        (0x00428C90, 0x200270B8), (0x00428BA8, 0x4002004C),
        (0x00429520, 0x200270B4), (0x004291E0, 0x40021000),
        (0x00428C9C, 0x4002037C), (0x004291E4, 0x40004044),
        (0x004291E8, 0x40004030), (0x00428C88, 0x2000055A),
    ),
}

SPOTMGR_FACTORY_TRIMS = {
    "function": "open_cfw_bootloader_spotmgr_load_factory_trims_429da4",
    "start": 0x00429DA4,
    "end": 0x00429DF6,
    "sha256": "a69ea6c52f959eba65684feebd9651d2068cdd0d91caf8eb45d74e52969c61a4",
    "main_start": 0x005A3E24,
    "callers": (0x0042A042,),
    "shared_literals": (
        (0x0042A548, 0x40020080),
        (0x0042A868, 0x20000150),
        (0x0042A084, 0x20026BA0),
        (0x0042A86C, 0x40020044),
        (0x0042A54C, 0x200271BC),
    ),
}

SPOTMGR_FACTORY_ENSURE = {
    "function": "open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036",
    "start": 0x0042A036,
    "end": 0x0042A04A,
    "sha256": "9c901638e2c0e882e9f92662df44aa585a49a2e160eb4f2a4c7b32b374ae7a06",
    "unrelocated_sha256": "9d3ed2e40906fd9e19c9edc7a48294cd8aaa624d34951606b435f7d7bca3c68c",
    "main_start": 0x005A40B6,
    "stored_pointer": 0x0041D15C,
    "relocation": (0x0C, "open_cfw_bootloader_spotmgr_load_factory_trims_429da4", 0x00429DA4),
    "shared_literals": ((0x0042A54C, 0x200271BC),),
}

SPOTMGR_TIMER_IRQ = {
    "function": "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a",
    "start": 0x0042A04A,
    "end": 0x0042A078,
    "sha256": "2ce0019a9c986275a9d5c9ea8d04c05e055c163e2802417c4ee68be2fd2b7fd4",
    "unrelocated_sha256": "fbeda6f0cc785f369e1ecc2da2a580a954b3c705058d8f32c3137dd609ae7e79",
    "stored_pointer": 0x0041D160,
    "callers": (
        0x00427F62, 0x00428106, 0x004282D8, 0x0042847A,
        0x0042859E, 0x0042870A, 0x004288D2, 0x004289B2,
        0x00428C48, 0x00428D3C, 0x00428E28, 0x00428F06,
        0x0042913A, 0x00429284, 0x004294DC, 0x004295B8,
        0x004296C4, 0x004297B4, 0x004298F0, 0x00429ACC,
        0x00429BE4, 0x00429CDE, 0x00429E92, 0x00429FFA,
    ),
    "relocations": (
        (0x02, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
        (0x12, "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378", 0x00428378),
        (0x1E, "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94", 0x00428A94),
        (0x22, "open_cfw_bootloader_spotmgr_timer_finish_41ccd6", 0x0041CCD6),
    ),
    "shared_literals": ((0x0042ABB4, 0x2000055A),),
}

SPOTMGR_BUCK_DEEPSLEEP = {
    "function": "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c",
    "start": 0x0042A08C,
    "end": 0x0042A19C,
    "sha256": "d6be1f893c0f78437db76208bb71ae7bf478411acb3ec307430709cd3dfe2e67",
    "unrelocated_sha256": "6e729b8c3c563a543f80219483d16ec5b38f5f31bb9afdf0d5869f7b3f70869c",
    "main_start": 0x005A410C,
    "main_sha256": "fd22420e52a17790ca72df5c495f4b121921462abadc775ed24df5ff3daf33f6",
    "identical_bytes": 253,
    "difference_runs": 9,
    "callers": (0x0042AA7A,),
    "relocation": (
        0x30, "open_cfw_bootloader_stimer_is_running_41f3f0", 0x0041F3F0,
    ),
    "shared_literals": (
        (0x0042A874, 0x400204D8),
        (0x0042AB70, 0x40008800),
        (0x0042AB74, 0x40008000),
        (0x0042AB78, 0x40008010),
        (0x0042ABB8, 0x200271C0),
    ),
}

SPOTMGR_INTERNAL_DOMAIN = {
    "function": "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c",
    "start": 0x0042A19C,
    "end": 0x0042A1B2,
    "sha256": "34664d76a6022980a70a926ac4c1108f43d33974584a9cb854f8faa59a8ebacf",
    "unrelocated_sha256": "34664d76a6022980a70a926ac4c1108f43d33974584a9cb854f8faa59a8ebacf",
    "main_start": 0x005A421C,
    "main_sha256": "db4fdac748e9f4483afbcd100a088101f823e080caa69c21eded210179a733c2",
    "identical_bytes": 20,
    "difference_runs": 1,
    "callers": (0x0042AAF4,),
    "shared_literals": ((0x0042ACA4, 0x200271B0),),
}

SPOTMGR_POWER_TON = {
    "function": "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
    "start": 0x0042A1BC,
    "end": 0x0042A2A4,
    "sha256": "8964efd235151acf974a0248acac460c57de14ed8effbb879293a54d97f6dfd0",
    "unrelocated_sha256": "8964efd235151acf974a0248acac460c57de14ed8effbb879293a54d97f6dfd0",
    "main_start": 0x005A423C,
    "main_sha256": "74a56bb748049d6b93486a461da7990e77314cfddd386045ed2fc4ddeca27124",
    "identical_bytes": 218,
    "difference_runs": 12,
    "callers": (
        0x00427F18, 0x00427F9E, 0x00428146, 0x00428314,
        0x004284B6, 0x0042861A, 0x004286C4, 0x00428742,
        0x00428916, 0x004289E2, 0x00428C7C, 0x00428D88,
        0x00428E62, 0x0042909A, 0x004292BE, 0x00429D20,
        0x00429F60, 0x0042A028, 0x0042A4DA,
    ),
    "shared_literals": (
        (0x0042AC50, 0x20026BA0),
        (0x0042ACA8, 0x40020344),
        (0x0042ACAC, 0x40020354),
        (0x0042ACB0, 0x40020358),
    ),
}

SPOTMGR_STATE_SEQUENCE = {
    "function": "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4",
    "start": 0x0042A2B4,
    "end": 0x0042A43A,
    "sha256": "c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f",
    "unrelocated_sha256": "e0fad5fe49ce4fde2b8a7371bc7a03824d8a273e9003c735317b3bb7075a7cf7",
    "main_start": 0x005A4334,
    "main_sha256": "f1b71cff0ba9b9fd7bb37d87bbfd1dcde7293361c5bf97e46bec825641bcc623",
    "identical_bytes": 384,
    "difference_runs": 2,
    "callers": (0x0042A462, 0x0042A492, 0x0042A524),
    "relocation": (
        0x12, "open_cfw_bootloader_memcpy_aligned_4156ac", 0x004156AC,
    ),
    "shared_literals": ((0x0042ACB4, 0x00433498),),
    "table_address": 0x00433498,
    "table_sha256": "d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8",
    "main_table_literal": 0x005A4E5C,
    "main_table_address": 0x00768BE0,
}

SPOTMGR_TEMPERATURE_TRANSITION = {
    "function": "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a",
    "start": 0x0042A43A,
    "end": 0x0042A4BC,
    "sha256": "1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107",
    "unrelocated_sha256": "066596bd21489fc692537d3fb5724af2ab6ba1eecb93d78b36ce35ea3a4d44cc",
    "main_start": 0x005A44BA,
    "main_sha256": "2f7a6cd1d785a53a4dd025c5f3c57703f7612efe5aa70263c943def71033c648",
    "identical_bytes": 126,
    "difference_runs": 2,
    "callers": (0x0042A4F2, 0x0042A518),
    "relocations": (
        (0x28, "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4", 0x0042A2B4),
        (0x58, "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4", 0x0042A2B4),
    ),
    "shared_literals": ((0x0042ACBC, 0x20000158),),
    "main_shared_literal": (0x005A4E60, 0x200002A8),
}

SPOTMGR_POWER_TRIMS = {
    "function": "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc",
    "start": 0x0042A4BC,
    "end": 0x0042A546,
    "sha256": "7bc6936adbff287072bfdcdac3b453214f98f9604c11239abef5a15f63b5e9bb",
    "unrelocated_sha256": "aed144230a794fe7b562c45bd45f9ba4afa02f2f1a9437c4635fd08402f60ec4",
    "main_start": 0x005A453C,
    "main_sha256": "2344f353caa315e0b9dbc75d759c181b2ae1dbf01f1f705e38b056e84c10c24f",
    "identical_bytes": 136,
    "difference_runs": 1,
    "callers": (0x0042AB52,),
    "relocations": (
        (0x1E, "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc", 0x0042A1BC),
        (0x36, "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a", 0x0042A43A),
        (0x5C, "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a", 0x0042A43A),
        (0x68, "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4", 0x0042A2B4),
    ),
    "shared_literals": ((0x0042ACBC, 0x20000158),),
    "main_shared_literal": (0x005A4E60, 0x200002A8),
}

SPOTMGR_POWER_STATE = {
    "function": "open_cfw_bootloader_spotmgr_power_state_determine_42a550",
    "start": 0x0042A550,
    "end": 0x0042A85E,
    "sha256": "73e2c284f4c3efc45c0cb02ad3d2d5c520c56ce136e4c185a4fbd56b815a0d87",
    "unrelocated_sha256": "73e2c284f4c3efc45c0cb02ad3d2d5c520c56ce136e4c185a4fbd56b815a0d87",
    "main_start": 0x005A45D0,
    "main_sha256": "d0d3ba15ffab7241ceeed1292ed98b98c9ca45c57921de74bfe4142004666e91",
    "identical_bytes": 750,
    "difference_runs": 16,
    "callers": (0x0042AB2A,),
    "shared_literals": (
        (0x0042ACC0, 0x00434168), (0x0042ACC4, 0x40021000),
        (0x0042ACC8, 0x00F00FFF), (0x0042ACCC, 0x000FFCFF),
        (0x0042ACD0, 0x2002708C), (0x0042ACD4, 0x000FF00F),
        (0x0042ACD8, 0x00011001), (0x0042ACDC, 0x00012001),
    ),
    "main_shared_literals": (
        (0x005A4E68, 0x0078EE58), (0x005A4E6C, 0x40021000),
        (0x005A4E70, 0x00F00FFF), (0x005A4E74, 0x000FFCFF),
        (0x005A4E78, 0x200742B0), (0x005A4E7C, 0x000FF00F),
        (0x005A4E80, 0x00011001), (0x005A4E84, 0x00012001),
    ),
}

SPOTMGR_UPDATE = {
    "function": "open_cfw_bootloader_spotmgr_power_state_update_42a878",
    "start": 0x0042A878, "end": 0x0042AB6E,
    "sha256": "83deb1cccedcf7dab0c986deaacc2f94baea6d1f74b7e7e387fbdb9f77527079",
    "unrelocated_sha256": "2939cbe9bff77ff31332559da4bf012f95b30ea65fd52954eba693168367e137",
    "dispatch_pointer": (0x0041D150, 0x0042A879),
    "relocations": (
        (0x38, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC),
        (0x16A, "open_cfw_bootloader_float_range_classify_427e0c", 0x00427E0C),
        (0x202, "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c", 0x0042A08C),
        (0x27C, "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c", 0x0042A19C),
        (0x2B2, "open_cfw_bootloader_spotmgr_power_state_determine_42a550", 0x0042A550),
        (0x2DA, "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc", 0x0042A4BC),
    ),
}

SPOTMGR_PROFILE = {
    "function": "open_cfw_bootloader_spotmgr_profile_apply_42ab7c",
    "start": 0x0042AB7C, "end": 0x0042ABB2,
    "sha256": "686b1225442297793c2d963c1903f0d2fa5dde214abdae1352ad5ade61c326f3",
    "unrelocated_sha256": "686b1225442297793c2d963c1903f0d2fa5dde214abdae1352ad5ade61c326f3",
    "dispatch_pointer": (0x0041D158, 0x0042AB7D),
    "relocations": (),
}

SPOTMGR_INIT = {
    "function": "open_cfw_bootloader_spotmgr_init_42abbc",
    "start": 0x0042ABBC, "end": 0x0042AC4E,
    "sha256": "1f0bfec6f59efe752ea106db7f7b7144fcd9b0df306919a7e03a7f2d550bca2d",
    "unrelocated_sha256": "d62bfd5f7ca5b79c01d63f55da969f21f422c5503ded4857cf20312f5cfc4a7a",
    "dispatch_pointer": (0x0041D14C, 0x0042ABBD),
    "relocations": (
        (0x3A, "open_cfw_bootloader_mram_read_421548", 0x00421548),
        (0x4C, "open_cfw_bootloader_mram_read_421548", 0x00421548),
        (0x72, "open_cfw_bootloader_mram_read_421548", 0x00421548),
        (0x88, "open_cfw_bootloader_spotmgr_runtime_init_41cc04", 0x0041CC04),
    ),
}

SPOTMGR_TEMPERATURE_INIT = {
    "function": "open_cfw_bootloader_spotmgr_temperature_init_42ac54",
    "start": 0x0042AC54, "end": 0x0042ACA4,
    "sha256": "4c910800d808fd71ce61510588a4bbe388e62974b65a756a73913bdf27482ea4",
    "unrelocated_sha256": "3636b7608940cd6452c1a6127ea5f177682849cc3740f5c98f9a4483a4794450",
    "dispatch_pointer": (0x0041D154, 0x0042AC55),
    "relocations": (
        (0x14, "open_cfw_bootloader_spotmgr_temperature_enable_41bf84", 0x0041BF84),
        (0x26, "open_cfw_bootloader_spotmgr_temperature_config_41ca2c", 0x0041CA2C),
        (0x38, "open_cfw_bootloader_delay_us_status_change_41d21c", 0x0041D21C),
    ),
}

SPOTMGR_TEMPERATURE_RANGE = {
    "function": "open_cfw_bootloader_spotmgr_temperature_range_42ad40",
    "start": 0x0042AD40, "end": 0x0042ADB8,
    "sha256": "89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d",
    "unrelocated_sha256": "89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d",
    "main_start": 0x005A0A70, "callers": (0x0042BB68,),
}

SPOTMGR_TRIM_HELPERS = (
    {"function": "open_cfw_bootloader_spotmgr_trim_enable_42adb8",
     "start": 0x0042ADB8, "end": 0x0042AE24,
     "sha256": "7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda",
     "unrelocated_sha256": "7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda",
     "main_start": 0x005A0AE8, "callers": (0x0042B4AE,)},
    {"function": "open_cfw_bootloader_spotmgr_profile_trim_42ae24",
     "start": 0x0042AE24, "end": 0x0042AE6C,
     "sha256": "73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538",
     "unrelocated_sha256": "73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538",
     "main_start": 0x005A0B54, "callers": (0x0042AEE0, 0x0042B694)},
    {"function": "open_cfw_bootloader_spotmgr_trim_restore_42ae6c",
     "start": 0x0042AE6C, "end": 0x0042AE9C,
     "sha256": "fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8",
     "unrelocated_sha256": "fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8",
     "main_start": 0x005A0B9C, "callers": (0x0042AEA4, 0x0042B68E)},
)

SPOTMGR_TRIM_COMMIT = {
    "function": "open_cfw_bootloader_spotmgr_trim_commit_42ae9c",
    "start": 0x0042AE9C, "end": 0x0042AEEC,
    "sha256": "62add64b9d5850045f7f332907406c01dc5f2ac1fbe500326b99a62d84a02904",
    "unrelocated_sha256": "0b2472da4b89f3dca0a6a8b877bcbb9f116587b6e8e9b4b18d609d218344a89e",
    "dispatch_pointer": (0x0041D17C, 0x0042AE9D),
    "relocations": (
        (0x02, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC),
        (0x08, "open_cfw_bootloader_spotmgr_trim_restore_42ae6c", 0x0042AE6C),
        (0x3E, "open_cfw_bootloader_spotmgr_trim_finalize_41ccd6", 0x0041CCD6),
        (0x44, "open_cfw_bootloader_spotmgr_profile_trim_42ae24", 0x0042AE24),
    ),
}

SPOTMGR_BUCK_SCAN = {
    "function": "open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0",
    "start": 0x0042AEF0, "end": 0x0042B010,
    "sha256": "7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b",
    "unrelocated_sha256": "040d93b977d325156b2ac09b6f01d68023fb2faf2bcf18e083a469afbb46e490",
    "main_start": 0x005A0C20,
    "main_sha256": "4e17431de023706b752a73b123eecbdbe0b8227ff331c6865dfc87376e194a99",
    "identical_bytes": 284, "difference_runs": 1,
    "callers": (0x0042BC08,),
    "relocation": (
        0x30, "open_cfw_bootloader_stimer_is_running_41f3f0", 0x0041F3F0,
    ),
    "shared_literals": (
        (0x0042B9D4, 0x400204D8),
        (0x0042B9D8, 0x200271C0),
        (0x0042B9DC, 0x40008800),
        (0x0042B9E0, 0x40008000),
        (0x0042B9E4, 0x40008010),
    ),
    "main_literals": (
        (0x005A1704, 0x400204D8),
        (0x005A1708, 0x20074F7B),
        (0x005A170C, 0x40008800),
        (0x005A1710, 0x40008000),
        (0x005A1714, 0x40008010),
    ),
}

SPOTMGR_STATE_EFFECTS = {
    "function": "open_cfw_bootloader_spotmgr_state_transition_effects_42b014",
    "start": 0x0042B014, "end": 0x0042B068,
    "sha256": "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88",
    "unrelocated_sha256": "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88",
    "main_start": 0x005A0D44,
    "callers": (0x0042BCB0, 0x0042BD26),
    "shared_literals": (
        (0x0042B9C8, 0x200271B2),
        (0x0042B9E8, 0x200271B0),
        (0x0042B9D0, 0x4002037C),
    ),
    "main_literals": (
        (0x005A16F8, 0x20074F6D),
        (0x005A1718, 0x20074F6B),
        (0x005A1700, 0x4002037C),
    ),
}

SPOTMGR_POWER_TRANSITION = {
    "function": "open_cfw_bootloader_spotmgr_power_transition_trims_42b06c",
    "start": 0x0042B06C, "end": 0x0042B294,
    "sha256": "44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377",
    "unrelocated_sha256": "35646af379886e8764cde56a2bf9bc6fb22e94f53ea178c5c60dd1727d190127",
    "main_start": 0x005A0D9C,
    "main_sha256": "a85df15a12dab48c2fd118dbde65dbb2f677f1f7782d93f03695442940e484b5",
    "identical_bytes": 540, "difference_runs": 4,
    "callers": (0x0042B2DA, 0x0042B348, 0x0042B65C),
    "relocations": (
        (0x76, "open_cfw_bootloader_delay_cycles_41d1c0", 0x0041D1C0),
        (0x90, "open_cfw_bootloader_delay_cycles_41d1c0", 0x0041D1C0),
    ),
    "shared_literals": (
        (0x0042B6A8, 0x40020080), (0x0042B6A0, 0x40020088),
        (0x0042B6A4, 0x20026BA0), (0x0042B9EC, 0x40020380),
        (0x0042B9F0, 0x40020344), (0x0042B9F4, 0x40020354),
        (0x0042B9F8, 0x40020358), (0x0042BDE4, 0x4002034C),
    ),
}

DIVIDER_HELPERS = (
    {
        "function": "open_cfw_bootloader_rounded_divider_42c222",
        "start": 0x0042C222, "end": 0x0042C256,
        "sha256": "84a7909276921edf87861325fa09f547e536659109a2de4eeb1fd171f7f57411",
        "unrelocated_sha256": "84a7909276921edf87861325fa09f547e536659109a2de4eeb1fd171f7f57411",
        "main_start": 0x0055BF1C, "callers": (0x0042C394, 0x0042C3C8),
        "host_cases": 100_000,
    },
    {
        "function": "open_cfw_bootloader_is_power_of_two_42c256",
        "start": 0x0042C256, "end": 0x0042C26A,
        "sha256": "c7c013df5ce01fcc66215af1337fed966a975393591a7bc7e17ebcf71bde8213",
        "unrelocated_sha256": "c7c013df5ce01fcc66215af1337fed966a975393591a7bc7e17ebcf71bde8213",
        "main_start": 0x0055BF50, "callers": (0x0042C3B2,),
        "host_cases": 100_009,
    },
)

HW_CLOCK_ENCODE = {
    "function": "open_cfw_bootloader_hw_clock_encode_42c26a",
    "start": 0x0042C26A, "end": 0x0042C3E2,
    "sha256": "23796b78366978bda2ee2db94e309c4f1cae4e92f5ffbc2072f75becca3ae9e8",
    "unrelocated_sha256": "1a25dd314239f7529ac9e4ea0d6dd690acda443e34cc35eb85fbb223baa349f5",
    "main_start": 0x0055BF64, "identical_main_bytes": 370,
    "callers": (0x0042CCB0,),
    "relocations": (
        (0x12A, "open_cfw_bootloader_rounded_divider_42c222", 0x0042C222),
        (0x148, "open_cfw_bootloader_is_power_of_two_42c256", 0x0042C256),
        (0x15E, "open_cfw_bootloader_rounded_divider_42c222", 0x0042C222),
    ),
}

HW_EVENT_APPLY = {
    "function": "open_cfw_bootloader_hw_event_apply_42c0b2",
    "start": 0x0042C0B2, "end": 0x0042C222,
    "sha256": "a3d5075b7f480a21b071c587bb343466ca39d411ed426927e82b22168591937e",
    "unrelocated_sha256": "d6834d461bd966d94e411a233499545d78421cec37e7901ba6e084eb4bbede2d",
    "main_start": 0x0055BDAC, "identical_main_bytes": 361,
    "callers": (0x0042C7D0, 0x0042C92A),
    "relocations": (
        (0x0C8, "open_cfw_bootloader_delay_cycles_41d1c0", 0x0041D1C0),
    ),
}

STATE_RANGE_SERVICES = (
    {"function": "open_cfw_bootloader_state_adjust_42cdf8",
     "start": 0x0042CDF8, "end": 0x0042CEA4,
     "sha256": "38a50cc07d40a0b1d447b195a21d977b7484f4d3151feead6e34dee388b59991",
     "unrelocated_sha256": "38a50cc07d40a0b1d447b195a21d977b7484f4d3151feead6e34dee388b59991",
     "main_start": 0x005A001C, "callers": (0x0042CECC, 0x0042D5E0),
     "stored_pointer": None, "relocations": (), "cases": 256 * 2 * 2},
    {"function": "open_cfw_bootloader_state_range_update_42ced8",
     "start": 0x0042CED8, "end": 0x0042CFE0,
     "sha256": "5cf1d6490be8e99cbc802900d5021f53a44fd49ab34fae01f67cc4308c11b5a0",
     "unrelocated_sha256": "7079a7b2881536c84b873867f4fcfe177d2164b023b3c536df80113790472752",
     "main_start": 0x005A00FC, "callers": (0x0042D5B0,), "stored_pointer": None,
     "relocations": ((0xA0, "open_cfw_bootloader_state_apply_42cea4", 0x0042CEA4, "STT_NOTYPE"),
                     (0xC8, "open_cfw_bootloader_state_apply_42cea4", 0x0042CEA4, "STT_NOTYPE"),
                     (0xEC, "open_cfw_bootloader_state_apply_42cea4", 0x0042CEA4, "STT_NOTYPE")),
     "cases": 8},
    {"function": "open_cfw_bootloader_state_event_dispatch_42d562",
     "start": 0x0042D562, "end": 0x0042D5C2,
     "sha256": "a060f2a726d07c0c67a1c00ada3aa671c805cfdab3a34e26239a7ebafc86eaa3",
     "unrelocated_sha256": "158ed49963d8dad49a00049283c61ebe50419c678e920125a47ad1d4f0073123",
     "main_start": 0x005A0786, "callers": (), "stored_pointer": 0x0041D184,
     "relocations": ((0x2A, "open_cfw_bootloader_state_event_zero_42cfe0", 0x0042CFE0, "STT_NOTYPE"),
                     (0x3A, "open_cfw_bootloader_state_event_one_zero_42d3bc", 0x0042D3BC, "STT_NOTYPE"),
                     (0x44, "open_cfw_bootloader_state_event_one_value_42d104", 0x0042D104, "STT_NOTYPE"),
                     (0x4E, "open_cfw_bootloader_state_range_update_42ced8", 0x0042CED8, "STT_FUNC")),
     "cases": 256},
)

STATE_EVENT_ZERO = {
    "function":"open_cfw_bootloader_state_event_zero_42cfe0",
    "start":0x0042CFE0,"end":0x0042D0F2,
    "sha256":"c03a0f379d7bbafb93e2c9074e4d754081699d39c63b4c2820765ffdab996624",
    "unrelocated_sha256":"01821e038de30d1a7e3cf1f0cb4e6124781b6860f1931800f3e89fe167b00e6a",
    "main_start":0x005A0204,"identical_main_bytes":271,"callers":(0x0042D58C,),
    "literals":((0x0042D7B8,0x200271B9),(0x0042D7C4,0x200271AC),(0x0042D7C8,0x200271C0),(0x0042D7D4,0x40008800),(0x0042D7D8,0x40008000),(0x0042D7DC,0x40008010)),
    "relocations":((0x022,"open_cfw_bootloader_state_probe_41f3f0",0x0041F3F0),),
}

STATE_EVENT_ONE = {
    "function":"open_cfw_bootloader_state_event_one_value_42d104",
    "start":0x0042D104,"end":0x0042D3BC,
    "sha256":"cf108ad5215cbb620832a3e19e1eede59c9a5726494715ae311b14c0ffa07994",
    "unrelocated_sha256":"1a14892f813bdf7509d0f4df3813866b5a77ab47ab377d72e592ed6cf4647480",
    "main_start":0x005A0328,"identical_main_bytes":684,"callers":(0x0042D5A6,),
    "literals":((0x0042D7A4,0x40021108),(0x0042D7AC,0x200271B4),(0x0042D7B4,0x4002004C),(0x0042D7E0,0x40020080),(0x0042D7E4,0x20027098),(0x0042D7E8,0x40020088),(0x0042D7EC,0x200270A0),(0x0042D7F0,0x2002709C),(0x0042D7F4,0x40020380),(0x0042D7F8,0x40020044),(0x0042D7FC,0x400201B0),(0x0042D800,0x40020344),(0x0042D804,0x4002034C),(0x0042D808,0x40020358),(0x0042D80C,0x40020354),(0x0042D810,0x200271B3)),
    "relocations":((0x0BA,"open_cfw_bootloader_delay_us_41d1c0",0x0041D1C0),(0x120,"open_cfw_bootloader_delay_us_41d1c0",0x0041D1C0),(0x2AE,"open_cfw_bootloader_delay_us_41d1c0",0x0041D1C0)),
}

MISC_PRIMITIVES = (
    {"function": "open_cfw_bootloader_stream_mode_42d84c",
     "start": 0x0042D84C, "end": 0x0042D88A,
     "sha256": "f477b0cb43f2f3074d2eeb48722f1045786679e4bc688fcf0440e842aeafa468",
     "unrelocated_sha256": "f477b0cb43f2f3074d2eeb48722f1045786679e4bc688fcf0440e842aeafa468",
     "callers": (0x0042D8A8, 0x0042DB2E, 0x0042DED8), "cases": 2_048},
    {"function": "open_cfw_bootloader_runtime_context_get_42d88a",
     "start": 0x0042D88A, "end": 0x0042D890,
     "sha256": "a38decb7c6c890f46354bc3a4b166bd89e4dac78108f0a6eb1e6123e61ad8087",
     "unrelocated_sha256": "a38decb7c6c890f46354bc3a4b166bd89e4dac78108f0a6eb1e6123e61ad8087",
     "callers": (0x0042DD6A,), "cases": 2},
    {"function": "open_cfw_bootloader_vector_handoff_42dc90",
     "start": 0x0042DC90, "end": 0x0042DCA2,
     "sha256": "71c5efb5c61ed7560ffa777e2f1ae2a3c65f0cace89f79de6e95b57f64673d6d",
     "unrelocated_sha256": "71c5efb5c61ed7560ffa777e2f1ae2a3c65f0cace89f79de6e95b57f64673d6d",
     "callers": (0x0042E08C, 0x0042E0F8), "cases": 2},
    {"function": "open_cfw_bootloader_crc32_table_42e1ec",
     "start": 0x0042E1EC, "end": 0x0042E220,
     "sha256": "b7d1a53f8d5f9e32fd1b27f48a14cf24bbfe5c7eb572950301fe0b32eff2f84a",
     "unrelocated_sha256": "b7d1a53f8d5f9e32fd1b27f48a14cf24bbfe5c7eb572950301fe0b32eff2f84a",
     "callers": (0x0042D936, 0x0042D99C), "cases": 2},
    {"function": "open_cfw_bootloader_terminal_mode_42e514",
     "start": 0x0042E514, "end": 0x0042E534,
     "sha256": "9c8ad2fd0e9722f5f6c902aee90dc63e6fbd7188827a02b16b6262421fa5107b",
     "unrelocated_sha256": "9c8ad2fd0e9722f5f6c902aee90dc63e6fbd7188827a02b16b6262421fa5107b",
     "callers": (0x0042DE50,), "cases": 256},
)

REGISTER_HELPERS = (
    {"function": "open_cfw_bootloader_hw_status_route_42c034",
     "start": 0x0042C034, "end": 0x0042C076,
     "sha256": "4748ace7dc077c4c00e8b22fb267ba5d64a0d28286c6b2d30868907e5ffa2005",
     "callers": (0x0042C570,), "cases": 24},
    {"function": "open_cfw_bootloader_hw_error_classify_42c076",
     "start": 0x0042C076, "end": 0x0042C0B2,
     "sha256": "ccdc2830f8d713ac41be3ffae702c125009eed11fc8b89d5f430e8c3a794af19",
     "callers": (0x0042C796, 0x0042C8CE), "cases": 65_536},
    {"function": "open_cfw_bootloader_hw_interrupt_enable_42c63a",
     "start": 0x0042C63A, "end": 0x0042C672,
     "sha256": "4bb8cd7875f57a46da8764a7c89f6058ce9f5aac52f707e5c86dc7a66c20d775",
     "callers": (0x004305CC,), "cases": 8},
    {"function": "open_cfw_bootloader_hw_interrupt_status_get_42c672",
     "start": 0x0042C672, "end": 0x0042C6B6,
     "sha256": "12a9d08495567647cb0d8416dfb736ee532845317b856b2b86e26b485510d347",
     "callers": (0x0043061C,), "cases": 8},
    {"function": "open_cfw_bootloader_hw_interrupt_clear_42c6b6",
     "start": 0x0042C6B6, "end": 0x0042C6E4,
     "sha256": "4a307af7da21ad92dbface1def9fb21fe550c8452a2c1a6b01755fdd0d7e2d4a",
     "callers": (0x0043062E,), "cases": 4},
    {"function": "open_cfw_bootloader_nvic_enable_bit_430240",
     "start": 0x00430240, "end": 0x0043025C,
     "sha256": "5f76b9bde6a1e386ed0ecb96e419aab2895f1cd30353dfac8bd7ef39b6fbd6c0",
     "callers": (0x0043036E,), "cases": 256},
    {"function": "open_cfw_bootloader_scb_priority_nibble_43025c",
     "start": 0x0043025C, "end": 0x00430280,
     "sha256": "ecf2bd6399d01eec88b38fd549bb5c511b6e5c06de2741cd54904269245e4f55",
     "callers": (0x0043035E,), "cases": 4_096},
    {"function": "open_cfw_bootloader_nvic_enable_bit_430470",
     "start": 0x00430470, "end": 0x0043048E,
     "sha256": "c71013637b644e67341b8f624db6831e06033c5a5323c421ef13a9f970883113",
     "callers": (0x004305D2,), "cases": 256},
)

CMDQ_ADAPTERS = (
    {"function": "open_cfw_bootloader_cmdq_adapter_init_42c3e2",
     "start": 0x0042C3E2, "end": 0x0042C420,
     "sha256": "1aa65df1cc920ea6fc753560e93e4967b36d8f0d49b1c37f9dd0b26295f84f02",
     "unrelocated_sha256": "7cb32beffb23a70bd84b37e9535483c46443570121bdf064f548ece05a7117cc",
     "callers": (0x0042C5D0,),
     "relocation": (0x2C, "open_cfw_bootloader_cmdq_init_427794", 0x00427794)},
    {"function": "open_cfw_bootloader_cmdq_adapter_enable_42c420",
     "start": 0x0042C420, "end": 0x0042C44E,
     "sha256": "1714c962c633337cdcde5ef6b032ac0bb3f10324ac0320e57fa8120c368bd4d3",
     "unrelocated_sha256": "66be604a116d307934ea0c3368c4c62c93ede52c84f494f3e25e844907eb4d4b",
     "callers": (0x0042C93E, 0x0042CAA4),
     "relocation": (0x28, "open_cfw_bootloader_cmdq_enable_427878", 0x00427878)},
    {"function": "open_cfw_bootloader_cmdq_adapter_disable_42c44e",
     "start": 0x0042C44E, "end": 0x0042C45A,
     "sha256": "d967623a77aff3dfbddc473422f508342a52aae0fa9b3e79c0215f3b62434157",
     "unrelocated_sha256": "e701bdc5d633faefd76b340e85ef86e0099177411ae4c6a202515a211c684fc1",
     "callers": (0x0042C94A, 0x0042CBE0),
     "relocation": (0x06, "open_cfw_bootloader_cmdq_disable_4278c8", 0x004278C8)},
)

HW_DESCRIPTOR_PUBLISH = {
    "function": "open_cfw_bootloader_hw_descriptor_publish_42c45a",
    "start": 0x0042C45A, "end": 0x0042C4C6,
    "sha256": "0deea2026365cb9c3471cdd81a7644c3fa519db2239154f3456da25ab88c5525",
    "callers": (0x0042C7EC,),
}

HW_CONTEXT_CLAIM = {
    "function": "open_cfw_bootloader_hw_context_claim_42c4c6",
    "start": 0x0042C4C6, "end": 0x0042C538,
    "sha256": "9727ea0e7e8786ddfab4618f79b101d91192e7291034937b15da4a9246d17db2",
    "main_start": 0x0055C2BC, "identical_main_bytes": 110,
    "callers": (0x00430514,),
}

HW_CONTEXT_ENABLE = {
    "function": "open_cfw_bootloader_hw_context_enable_42c538",
    "start": 0x0042C538, "end": 0x0042C63A,
    "sha256": "0183cf1cab1b0089fb0b49f71137bf868309198abd9319ca1e35f794ba430f2a",
    "unrelocated_sha256": "0541dca0e2b4a414177436b877cf5473f5b854a12b96d4d98724747ac1293da4",
    "main_start": 0x0055C32E, "identical_main_bytes": 246,
    "callers": (0x0043056C,),
    "relocations": (
        (0x38, "open_cfw_bootloader_hw_status_route_42c034", 0x0042C034),
        (0x98, "open_cfw_bootloader_cmdq_adapter_init_42c3e2", 0x0042C3E2),
        (0xC6, "open_cfw_bootloader_retained_status_check_41d246", 0x0041D246),
    ),
}

HW_EVENT_SERVICE = {
    "function": "open_cfw_bootloader_hw_event_service_42c6f8",
    "start": 0x0042C6F8, "end": 0x0042C980,
    "sha256": "7272867858e1c23f8ad5e5938ef7f5e02d59289de7c3c76eb6c7ea69fcec5958",
    "unrelocated_sha256": "68622fb39f74db4f8713335ee263e25dc024684d86d5e59bc43f600a11ee72b4",
    "main_start": 0x0055C558, "identical_main_bytes": 621,
    "callers": (0x00430636,),
    "relocations": (
        (0x09E, "open_cfw_bootloader_hw_error_classify_42c076", 0x0042C076),
        (0x0D8, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x0042C0B2),
        (0x0F4, "open_cfw_bootloader_hw_descriptor_publish_42c45a", 0x0042C45A),
        (0x13E, "open_cfw_bootloader_cmdq_get_status_427a56", 0x00427A56),
        (0x1D6, "open_cfw_bootloader_hw_error_classify_42c076", 0x0042C076),
        (0x232, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x0042C0B2),
        (0x23A, "open_cfw_bootloader_cmdq_error_resume_427b38", 0x00427B38),
        (0x246, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x0042C420),
        (0x252, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x0042C44E),
    ),
}

HW_CONFIG_TRANSACTION = {
    "function": "open_cfw_bootloader_hw_config_transaction_42c988",
    "start": 0x0042C988, "end": 0x0042CC34,
    "sha256": "1a89b00660cf0c54c66e781ac95f19dd764bb671587c36959ad2cd34fec53ae5",
    "unrelocated_sha256": "904ef19dffe0d14d032fbab68fc23a1902fc9eb9704230e52a4a29e5d302503f",
    "main_start": 0x0055C7E8, "identical_main_bytes": 657,
    "callers": (0x004304EC, 0x00430552),
    "relocations": (
        (0x04A, "open_cfw_bootloader_pwrctrl_periph_enable_41bf84", 0x0041BF84),
        (0x11C, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x0042C420),
        (0x140, "open_cfw_bootloader_retained_status_check_41d246", 0x0041D246),
        (0x152, "open_cfw_bootloader_mode_enable_route_4222f0", 0x004222F0),
        (0x258, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x0042C44E),
        (0x290, "open_cfw_bootloader_pwrctrl_periph_disable_41c17a", 0x0041C17A),
        (0x29C, "open_cfw_bootloader_mode_disable_route_422364", 0x00422364),
    ),
}

HW_INSTANCE_CONFIGURE = {
    "function": "open_cfw_bootloader_hw_instance_configure_42cc34",
    "start": 0x0042CC34, "end": 0x0042CDB0,
    "sha256": "d881da0882c4dcc9f1385402b877bcb3d8c379de014c78707c8db99f5b03aa93",
    "unrelocated_sha256": "cd9cd51d75de4bf4ffa5587acfeab18036746f59f4c60d9b5c2ce91edac3f631",
    "main_start": 0x0055CA94, "identical_main_bytes": 352,
    "callers": (0x00430562,),
    "relocations": (
        (0x07C, "open_cfw_bootloader_hw_clock_encode_42c26a", 0x0042C26A),
    ),
}

HW_CONFIG_RETRY = {
    "function": "open_cfw_bootloader_hw_config_retry_43048e",
    "start": 0x0043048E, "end": 0x00430502,
    "sha256": "6ba3fb6ddde5fa56fd43fc1f7f717bcc7cf201df2ae6af1b86d20bdde8404dbb",
    "unrelocated_sha256": "d38d571a4434f154b7f72b56d99123af55902ac5105c4202cc13087a0971b418",
    "main_start": 0x005041C6, "identical_main_bytes": 98,
    "callers": (0x00430576,),
    "relocations": (
        (0x024, "open_cfw_bootloader_callback_register_41d92c", 0x0041D92C),
        (0x036, "open_cfw_bootloader_callback_register_41d92c", 0x0041D92C),
        (0x040, "open_cfw_bootloader_delay_us_41f9d8", 0x0041F9D8),
        (0x05E, "open_cfw_bootloader_hw_config_transaction_42c988", 0x0042C988),
    ),
}

PLATFORM_FINISH = {
    "function":"open_cfw_bootloader_platform_finish_430502",
    "start":0x00430502,"end":0x00430610,
    "sha256":"f92c35acae4e7f10f79008020f00bb4607f39ff6b09545fbbbc93348b6873195",
    "unrelocated_sha256":"bad372fa5e2a442fcbf1d4e7a767aed113b369aeeaffb8d5cb4e3fd107da4b99",
    "main_start":0x0050423A,"identical_main_bytes":196,"callers":(0x004301EC,),
    "literals":((0x00430640,0x20000374),(0x00430648,0x20026ED8),(0x0043064C,0x20027104),(0x00430650,0x004322C8),(0x00430654,0x00433F74),(0x00430658,0x0043164C),(0x0043065C,0x004340A4)),
    "relocations":((0x012,"open_cfw_bootloader_hw_context_claim_42c4c6",0x0042C4C6),(0x026,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x03E,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x050,"open_cfw_bootloader_hw_config_transaction_42c988",0x0042C988),(0x060,"open_cfw_bootloader_hw_instance_configure_42cc34",0x0042CC34),(0x06A,"open_cfw_bootloader_hw_context_enable_42c538",0x0042C538),(0x074,"open_cfw_bootloader_hw_config_retry_43048e",0x0043048E),(0x0A6,"open_cfw_bootloader_event_object_create_416610",0x00416610),(0x0CA,"open_cfw_bootloader_hw_interrupt_enable_42c63a",0x0042C63A),(0x0D0,"open_cfw_bootloader_nvic_enable_bit_430470",0x00430470),(0x0DE,"open_cfw_bootloader_event_flags_create_416762",0x00416762),(0x104,"open_cfw_bootloader_log_4176ce",0x004176CE)),
}

PLATFORM_BRINGUP = {
    "function":"open_cfw_bootloader_platform_bringup_430000","start":0x00430000,"end":0x004301D6,
    "sha256":"c98f998d82e0cac0d01306057a759bbe3c360091397866e4e5999094a558879d","unrelocated_sha256":"62f91d410489b31b78356faa7ae9764b0b335fac5d2571074b3678e51cf251f0","callers":(0x004301E4,),
    "literals":((0x004301F8,0x00000000),(0x004301FC,0x44610001),(0x00430200,0x447A0000),(0x00430208,0x00434170),(0x0043020C,0x00431EA4),(0x00430210,0xC2F6E979),(0x00430214,0x004325F8),(0x00430218,0x00433140),(0x0043021C,0x0043402C),(0x00430220,0x00432C7C),(0x00430224,0x004329D4),(0x00430228,0x00433160),(0x0043022C,0x20027018),(0x00430230,0x40038038),(0x00430234,0x00431AB8),(0x00430238,0x00434174)),
    "relocations":((0x00E,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x016,"open_cfw_bootloader_hw_context_initialize_42e8d0",0x0042E8D0),(0x020,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x040,"open_cfw_bootloader_hw_config_enumerate_42ec0c",0x0042EC0C),(0x05E,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x068,"open_cfw_bootloader_register_profile_transfer_42f020",0x0042F020),(0x072,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x084,"open_cfw_bootloader_hw_profile_prepare_42eb74",0x0042EB74),(0x0B6,"open_cfw_bootloader_hw_profile_apply_42ea68",0x0042EA68),(0x0C0,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x0EC,"open_cfw_bootloader_hw_channel_config_42eaf6",0x0042EAF6),(0x0F6,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x0FC,"open_cfw_bootloader_hw_handle_activate_42ed60",0x0042ED60),(0x106,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x10C,"open_cfw_bootloader_hw_measurement_prepare_42ebaa",0x0042EBAA),(0x112,"open_cfw_bootloader_hw_handle_command_42eff4",0x0042EFF4),(0x142,"open_cfw_bootloader_hw_measurement_sample_42ee70",0x0042EE70),(0x150,"open_cfw_bootloader_hw_measurement_begin_42ebe2",0x0042EBE2),(0x156,"open_cfw_bootloader_hw_measurement_end_42eda0",0x0042EDA0),(0x1AA,"open_cfw_bootloader_message_emit_415fae",0x00415FAE),(0x1BE,"open_cfw_bootloader_register_profile_transfer_42f020",0x0042F020),(0x1C4,"open_cfw_bootloader_hw_handle_reset_42ea32",0x0042EA32),(0x1CE,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C)),
}

DESCRIPTOR_REGISTER = {
    "function":"open_cfw_bootloader_descriptor_register_430280",
    "start":0x00430280,"end":0x004303BC,
    "sha256":"41b2abc6111a25a5b0ee15e4c3e877aaa486b631855ca3dd75fb388d55dd1391",
    "unrelocated_sha256":"c9ef6ec35809b9ae523a8708c7db831ebb14f56991a1ba3f05b6e9fd7fcf4625",
    "main_start":0x0053A454,"identical_main_bytes":285,"callers":(0x004301DC,),
    "literals":((0x00430460,0x00434198),(0x00430464,0x00434194),(0x00430468,0x0043409C),(0x0043046C,0x00434190)),
    "relocations":((0x032,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x05E,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x086,"open_cfw_bootloader_memset_415ff4",0x00415FF4),(0x0A4,"open_cfw_bootloader_irq_mask_control_41dcca",0x0041DCCA),(0x0AC,"open_cfw_bootloader_irq_mask_apply_41de3c",0x0041DE3C),(0x0BE,"open_cfw_bootloader_irq_handler_bind_41e000",0x0041E000),(0x0C8,"open_cfw_bootloader_irq_state_publish_41da84",0x0041DA84),(0x0DE,"open_cfw_bootloader_scb_priority_nibble_43025c",0x0043025C),(0x0EE,"open_cfw_bootloader_nvic_enable_bit_430240",0x00430240),(0x110,"open_cfw_bootloader_callback_register_41d92c",0x0041D92C),(0x12E,"open_cfw_bootloader_boolean_route_41d9aa",0x0041D9AA)),
}

HW_STATE_COMPOSE = {
    "function":"open_cfw_bootloader_hw_state_compose_42bdf0",
    "start":0x0042BDF0,"end":0x0042BF4E,
    "sha256":"6abb107b7aebe13eaff37f34185f8865b71f27c756f8214d3646efa4f2304c1c",
    "unrelocated_sha256":"b58f55d554bf0421fd534e60ce347afec006da6d395801821ed11dbe26ff5f41",
    "main_start":0x005A1C18,"identical_main_bytes":313,"callers":(),
    "stored_pointer":0x0041D164,
    "literals":((0x0042BFCC,0x20026BA0),(0x0042BFD0,0x1F01600D),(0x0042BFD8,0x40021008),(0x0042C02C,0x400201BC)),
    "relocations":((0x03A,"open_cfw_bootloader_config_read_421548",0x00421548),(0x096,"open_cfw_bootloader_config_read_421548",0x00421548),(0x0B8,"open_cfw_bootloader_config_read_421548",0x00421548),(0x154,"open_cfw_bootloader_hw_state_commit_41cc04",0x0041CC04)),
}

HW_STATE_DECODE = {
    "function":"open_cfw_bootloader_hw_state_decode_42b6b8",
    "start":0x0042B6B8,"end":0x0042B9BA,
    "sha256":"74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1",
    "unrelocated_sha256":"74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1",
    "main_start":0x005A13E8,"identical_main_bytes":738,"callers":(0x0042BCEC,),
    "literals":((0x0042BFA8,0x00434164),(0x0042BFAC,0x40021000),(0x0042BFB0,0x00F00FFF),(0x0042BFB4,0x000FFCFF),(0x0042BFB8,0x2002708C),(0x0042BFBC,0x000FF00F),(0x0042BFC0,0x00011001),(0x0042BFC4,0x00012001)),
    "relocations":(),
}

SPOTMGR_STATE_TRANSITION = {
    "function":"open_cfw_bootloader_spotmgr_state_transition_42b294",
    "start":0x0042B294,"end":0x0042B69C,
    "sha256":"0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b",
    "unrelocated_sha256":"66cef2c5e94a5aefda464abf3c541bbd8103cf62e89ceb076811a6c3199b45a6",
    "main_start":0x005A0FC4,"identical_main_bytes":996,"callers":(0x0042BD14,),
    "literals":((0x0042B6A4,0x20026BA0),(0x0042B9FC,0x20000148),(0x0042BD9C,0x200000A4),(0x0042BDE8,0x200000F4),(0x0042B6B4,0x200270A8),(0x0042B9C4,0x200270AC),(0x0042B6A8,0x40020080),(0x0042BDEC,0x400083E0),(0x0042B9BC,0x200270A4),(0x0042B6AC,0x200271AE),(0x0042B6B0,0x40020044),(0x0042B9C0,0x4002004C),(0x0042BF50,0xE000ED14),(0x0042B9D0,0x4002037C),(0x0042B9C8,0x200271B2)),
    "relocations":((0x046,"open_cfw_bootloader_spotmgr_power_transition_trims_42b06c",0x0042B06C),(0x0B4,"open_cfw_bootloader_spotmgr_power_transition_trims_42b06c",0x0042B06C),(0x21A,"open_cfw_bootloader_spotmgr_trim_enable_42adb8",0x0042ADB8),(0x220,"open_cfw_bootloader_spotmgr_transition_start_41cc48",0x0041CC48),(0x22C,"open_cfw_bootloader_spotmgr_transition_wait_41cc92",0x0041CC92),(0x24A,"open_cfw_bootloader_spotmgr_irq_pause_41e22e",0x0041E22E),(0x268,"open_cfw_bootloader_delay_cycles_41d1c0",0x0041D1C0),(0x278,"open_cfw_bootloader_spotmgr_irq_resume_41e1e8",0x0041E1E8),(0x3C8,"open_cfw_bootloader_spotmgr_power_transition_trims_42b06c",0x0042B06C),(0x3F6,"open_cfw_bootloader_spotmgr_trim_finalize_41ccd6",0x0041CCD6),(0x3FA,"open_cfw_bootloader_spotmgr_trim_restore_42ae6c",0x0042AE6C),(0x400,"open_cfw_bootloader_spotmgr_profile_trim_42ae24",0x0042AE24)),
}

DFU_IMAGE_CRC = {
    "function":"open_cfw_bootloader_dfu_image_crc_check_42d890",
    "start":0x0042D890,"end":0x0042D9F0,
    "sha256":"b0ddd79ec823f1045ba1d689a2b9199a103a3c10afcd2d34cab9a66af914f82f",
    "unrelocated_sha256":"fce1f2d8b577fe200de04a0350123dcd15365db537253e93fcef3fec5a29ac0a",
    "callers":(0x0042DFF6,),
    "literals":((0x0042E108,0x004336E4),(0x0042E10C,0x00433BDC),(0x0042E110,0x004339AC),(0x0042E114,0x004310C4),(0x0042E118,0x00433FE0),(0x0042E11C,0x2001FDF0),(0x0042E120,0x00433E78),(0x0042E124,0x200004F0),(0x0042E128,0x00433BF0),(0x0042E12C,0x20026EF8),(0x0042E130,0x004339C4)),
    "relocations":((0x018,"open_cfw_bootloader_stream_mode_42d84c",0x0042D84C),(0x024,"open_cfw_bootloader_file_open_4153a4",0x004153A4),(0x04A,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x058,"open_cfw_bootloader_file_prepare_4154d2",0x004154D2),(0x070,"open_cfw_bootloader_file_read_415484",0x00415484),(0x098,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x0A6,"open_cfw_bootloader_crc32_table_42e1ec",0x0042E1EC),(0x0DE,"open_cfw_bootloader_file_read_415484",0x00415484),(0x102,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x10C,"open_cfw_bootloader_crc32_table_42e1ec",0x0042E1EC),(0x11A,"open_cfw_bootloader_file_close_415446",0x00415446),(0x146,"open_cfw_bootloader_log_4176ce",0x004176CE)),
}

DFU_PAYLOAD_PROGRAM = {
    "function":"open_cfw_bootloader_dfu_payload_program_42dae8",
    "start":0x0042DAE8,"end":0x0042DC90,
    "sha256":"8bec7ec7631e231c2c79d32f04f64eac3e12a99c3a80c879b441bbf6a62dfd82",
    "unrelocated_sha256":"3718f9c7011258ecc5e206c225615ab863b422edaef09bc6063fffe2490151c1",
    "callers":(0x0042E004,),
    "literals":((0x0042E108,0x004336E4),(0x0042E10C,0x00433BDC),(0x0042E114,0x004310C4),(0x0042E118,0x00433FE0),(0x0042E124,0x200004F0),(0x0042E128,0x00433BF0),(0x0042E13C,0x004320AC),(0x0042E140,0x004339DC),(0x0042E144,0x00433700),(0x0042E148,0x00433E88),(0x0042E14C,0x00433C18),(0x0042E150,0x2001EDE0),(0x0042E154,0x00433C2C)),
    "relocations":((0x018,"open_cfw_bootloader_chunked_indirect_visit_42d9f0",0x0042D9F0),(0x040,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x046,"open_cfw_bootloader_stream_mode_42d84c",0x0042D84C),(0x052,"open_cfw_bootloader_file_open_4153a4",0x004153A4),(0x07A,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x088,"open_cfw_bootloader_file_prepare_4154d2",0x004154D2),(0x0A0,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x0D8,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x100,"open_cfw_bootloader_file_read_415484",0x00415484),(0x122,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x142,"open_cfw_bootloader_chunked_source_compare_42da1e",0x0042DA1E),(0x164,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x180,"open_cfw_bootloader_file_close_415446",0x00415446),(0x19E,"open_cfw_bootloader_log_4176ce",0x004176CE)),
}

DFU_SERVICE_TASK = {
    "function":"open_cfw_bootloader_dfu_service_task_42de58","start":0x0042DE58,"end":0x0042E104,
    "sha256":"52e1f7a3ed50f4a8167463ae705cccee6ac690db1de524927a2eca9eb424557f","unrelocated_sha256":"759dc2f405b33a3e61e91d43484cc390e102b717c3e6a7c7d4729f1705b112b8","callers":(0x0042E1CC,),
    "literals":((0x0042E108,0x004336E4),(0x0042E10C,0x00433BDC),(0x0042E114,0x004310C4),(0x0042E118,0x00433FE0),(0x0042E12C,0x20026EF8),(0x0042E158,0x200004CC),(0x0042E18C,0x0043371C),(0x0042E190,0x00433C54),(0x0042E194,0x004333A0),(0x0042E198,0x20027174),(0x0042E19C,0x00433C68),(0x0042E1A0,0x00433EB8),(0x0042E1A4,0x00434004),(0x0042E1A8,0x00433C7C),(0x0042E1AC,0x00433A0C),(0x0042E1B0,0x00432834),(0x0042E1B4,0x0043306C),(0x0042E1B8,0x004333C0),(0x0042E1BC,0x00433A24),(0x0042E1C0,0x004333E0)),
    "relocations":((0x00E,"open_cfw_bootloader_memset_41560c",0x0041560C),(0x01C,"open_cfw_bootloader_file_close_415446",0x00415446),(0x03E,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x042,"open_cfw_bootloader_runtime_enable_42de0e",0x0042DE0E),(0x050,"open_cfw_bootloader_queue_receive_416920",0x00416920),(0x07A,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x080,"open_cfw_bootloader_stream_mode_42d84c",0x0042D84C),(0x08E,"open_cfw_bootloader_file_open_4153a4",0x004153A4),(0x0B0,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x0B4,"open_cfw_bootloader_runtime_enable_42de0e",0x0042DE0E),(0x0C6,"open_cfw_bootloader_file_read_415484",0x00415484),(0x0DA,"open_cfw_bootloader_file_close_415446",0x00415446),(0x108,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x128,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x144,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x16E,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x18A,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x19E,"open_cfw_bootloader_dfu_image_crc_check_42d890",0x0042D890),(0x1AC,"open_cfw_bootloader_dfu_payload_program_42dae8",0x0042DAE8),(0x1B2,"open_cfw_bootloader_runtime_enable_42de0e",0x0042DE0E),(0x1DC,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x208,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x22A,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x22E,"open_cfw_bootloader_runtime_disable_42ddf2",0x0042DDF2),(0x234,"open_cfw_bootloader_vector_handoff_42dc90",0x0042DC90),(0x274,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x296,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x29A,"open_cfw_bootloader_runtime_disable_42ddf2",0x0042DDF2),(0x2A0,"open_cfw_bootloader_vector_handoff_42dc90",0x0042DC90)),
}

STATE_REGISTER_INITIALIZE = {
    "function":"open_cfw_bootloader_state_register_initialize_42d3bc",
    "start":0x0042D3BC,"end":0x0042D562,
    "sha256":"28b119628520d11368f8517e23ba59254c17bb974684a59ead1266312f71e0c6",
    "unrelocated_sha256":"e9f07abd3d46704129114ec4e23d3a0702e9fab7d84c19b1b3376ea27e06af46",
    "main_start":0x005A05E0,"identical_main_bytes":414,"callers":(0x0042D59C,),
    "literals":((0x0042D7A4,0x40021108),(0x0042D7AC,0x200271B4),(0x0042D7B4,0x4002004C),(0x0042D7E0,0x40020080),(0x0042D7E4,0x20027098),(0x0042D7E8,0x40020088),(0x0042D7EC,0x200270A0),(0x0042D7F0,0x2002709C),(0x0042D7F4,0x40020380),(0x0042D7F8,0x40020044),(0x0042D7FC,0x400201B0),(0x0042D800,0x40020344),(0x0042D804,0x4002034C),(0x0042D808,0x40020358),(0x0042D80C,0x40020354),(0x0042D810,0x200271B3)),
    "relocations":((0x07C,"open_cfw_bootloader_delay_us_41d1c0",0x0041D1C0),(0x0A6,"open_cfw_bootloader_delay_us_41d1c0",0x0041D1C0)),
}

HW_CONTEXT_INITIALIZE = {
    "function":"open_cfw_bootloader_hw_context_initialize_42e8d0",
    "start":0x0042E8D0,"end":0x0042EA32,
    "sha256":"21eb4fbe548c1f7c1c16bbf7bf31671f7cdbf125ee784a96893efdef723f6fd8",
    "unrelocated_sha256":"b34fa81a3f580579a5260a539ef14f81e8b7bfdbbed0978e88dbba4c69e17c06",
    "main_start":0x0055D94C,"identical_main_bytes":339,"callers":(0x00430016,),
    "literals":((0x0042F150,0x20026DF0),(0x0042F154,0x2002702C),(0x0042F158,0x1F01600D),(0x0042F15C,0x200267F8),(0x0042F160,0x20026FC0),(0x0042F164,0x4395C000),(0x0042F168,0x3F839874),(0x0042F16C,0xBB8C47A1),(0x0042F170,0x20026FE0),(0x0042F174,0x4002010C),(0x0042F178,0x20027199)),
    "relocations":((0x094,"open_cfw_bootloader_config_read_421548",0x00421548),(0x0A4,"open_cfw_bootloader_config_read_421548",0x00421548),(0x0B6,"open_cfw_bootloader_config_read_421548",0x00421548),(0x116,"open_cfw_bootloader_config_read_421548",0x00421548),(0x126,"open_cfw_bootloader_config_read_421548",0x00421548)),
}

HW_PROFILE_APPLY = {
    "function": "open_cfw_bootloader_hw_profile_apply_42ea68",
    "start": 0x0042EA68, "end": 0x0042EAF6,
    "sha256": "1e62bb87b3abb1f8918525f1f3064c366982fc0afa075a018925d8f21376d686",
    "unrelocated_sha256": "2c8b1283be5ea34c8b2ca392315cea78f713d89ada1ebf6587dca17bdc7eab4e",
    "main_start": 0x0055DAE4, "identical_main_bytes": 140,
    "callers": (0x004300B6,),
    "relocations": (
        (0x02E, "open_cfw_bootloader_mode_enable_route_4222f0", 0x004222F0),
    ),
}

HW_REGISTER_PROFILE_RESTORE = {
    "function":"open_cfw_bootloader_hw_register_profile_restore_42f2fa",
    "start":0x0042F2FA,"end":0x0042F38E,
    "sha256":"b1b11b9cae5d09e8bd59aae4099ed288cbd5d1e55980dbdda910c89282b7af40",
    "unrelocated_sha256":"fbc38be724a162f01ab84627f97fa0843a969e4fedd792f00e1f2783fd13314a",
    "main_start":0x0059FCA2,"identical_main_bytes":144,"callers":(0x0042F3B8,),
    "relocations":((0x03C,"open_cfw_bootloader_register_power_toggle_42f1c8",0x0042F1C8),(0x084,"open_cfw_bootloader_register_power_toggle_42f1c8",0x0042F1C8),(0x08C,"open_cfw_bootloader_mode_finalize_41cde0",0x0041CDE0)),
}

EVENT_VALUE_PROFILE = {
    "function":"open_cfw_bootloader_event_value_provider_42f204",
    "start":0x0042F204,"end":0x0042F2FA,
    "sha256":"501f73cf98677984aeedc3b9d60df3775a99c7e68520f23d6bd11c8b0e342317",
    "unrelocated_sha256":"afc00b5ad826855d562f2c1f82f67b728ea5144b92754578cc319e35fcb10b0d",
    "main_start":0x0059FBAC,"identical_main_bytes":234,"callers":(0x0042F3C0,),
    "literals":((0x0042F5F4,0x40021108),(0x0042F5F8,0x40020080),(0x0042F5FC,0x20027090),(0x0042F600,0x40020088),(0x0042F604,0x20027094),(0x0042F608,0x200271A8),(0x0042F60C,0x2002704C),(0x0042F610,0x40020044),(0x0042F614,0x400201B0),(0x0042F618,0x20027050),(0x0042F61C,0x4002004C),(0x0042F620,0x40020374)),
    "relocations":((0x00C,"open_cfw_bootloader_mode_finalize_41cde0",0x0041CDE0),(0x064,"open_cfw_bootloader_register_power_toggle_42f1c8",0x0042F1C8),(0x0D0,"open_cfw_bootloader_register_power_toggle_42f1c8",0x0042F1C8),(0x0D6,"open_cfw_bootloader_delay_cycles_41d1c0",0x0041D1C0),(0x0EE,"open_cfw_bootloader_delay_cycles_41d1c0",0x0041D1C0)),
}

REGISTER_PROFILE_TRANSFER = {
    "function":"open_cfw_bootloader_register_profile_transfer_42f020",
    "start":0x0042F020,"end":0x0042F14E,
    "sha256":"2e6cca806f60cc19024673c46f635245eaea0c8e7aff23580b1a8cf15e487a73",
    "unrelocated_sha256":"7019743d54c61b4d148d591856d90a4c23d482770fc7938db8b4b374ef53278c",
    "main_start":0x0055E09C,"identical_main_bytes":292,"callers":(0x00430068,0x004301BE),
    "literals":((0x0042F17C,0x01AFAFAF),(0x0042F180,0x40038000),(0x0042F184,0x4003800C),(0x0042F188,0x40038040),(0x0042F18C,0x4003802C),(0x0042F190,0x40038030),(0x0042F1A0,0x40038200),(0x0042F1A4,0x4003803C),(0x0042F1A8,0x40038010),(0x0042F1AC,0x40038014),(0x0042F1B0,0x40038018),(0x0042F1B4,0x4003801C),(0x0042F1B8,0x40038020),(0x0042F1BC,0x40038024),(0x0042F1C0,0x40038028)),
    "relocations":((0x03E,"open_cfw_bootloader_mode_query_41bf84",0x0041BF84),(0x04C,"open_cfw_bootloader_mode_enable_route_4222f0",0x004222F0),(0x11E,"open_cfw_bootloader_clock_config_422364",0x00422364),(0x124,"open_cfw_bootloader_delay_status_41c17a",0x0041C17A)),
}

CHUNKED_SOURCE_COMPARE = {
    "function":"open_cfw_bootloader_chunked_source_compare_42da1e",
    "start":0x0042DA1E,"end":0x0042DAD0,
    "sha256":"4addc6bfb9023df944da168fed7deb268b2de24817dd19865719e37f4131216b",
    "unrelocated_sha256":"bb1588dad52910df21eed899b2baeca89620ce541261e8e511fecd04f539e471",
    "callers":(0x0042DC2A,),
    "relocations":((0x01A,"open_cfw_bootloader_compare_prepare_41e348",0x0041E348),(0x042,"open_cfw_bootloader_log_4176ce",0x004176CE),(0x07C,"open_cfw_bootloader_memory_compare_415758",0x00415758),(0x0A6,"open_cfw_bootloader_log_4176ce",0x004176CE)),
}

MODE_APPLY = {
    "function":"open_cfw_bootloader_mode_apply_42ff00",
    "start":0x0042FF00,"end":0x0042FFF2,
    "sha256":"2bf23ab0e4988009a2692db968a818ffeb5f010919982b1235db1b85d8735ae6",
    "unrelocated_sha256":"3f26b603da390864dd2be07c458566263a63400f78d428f98113b1540bc53d1d",
    "callers":(0x0042FFF8,),"state_literal":(0x00430204,0x200270D0),
    "relocations":((0x03C,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x052,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x068,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x07E,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x084,"open_cfw_bootloader_critical_enter_41b8ec",0x0041B8EC),(0x0C4,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x0CE,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC),(0x0EA,"open_cfw_bootloader_boolean_route_status_4303bc",0x004303BC)),
}

CONTROL_WRAPPERS = (
    {"function": "open_cfw_bootloader_runtime_context_wrapper_42dd68",
     "start": 0x0042DD68, "end": 0x0042DD70,
     "sha256": "86bf8be3cfef3a107d8691b1fb960ba63cc40d3ef6eb8ed906638e24001e1a84",
     "unrelocated_sha256": "c27d4a49b161be022ccdfdf92c47a4912090c2316b87ed52a61f20660f5f4dc3",
     "callers": (0x0042DD1E,),
     "relocations": ((0x02, "open_cfw_bootloader_runtime_context_get_42d88a", 0x0042D88A),)},
    {"function": "open_cfw_bootloader_control_one_wrapper_42dd9a",
     "start": 0x0042DD9A, "end": 0x0042DDA4,
     "sha256": "0ca6febf5ed7d28e9c024276b7e6b431494e53a1432d1cdf6993024364aa64de",
     "unrelocated_sha256": "2cb70dab61786bb8a0ca4c358e1158432893275d7ed07c6004ce79c7b711b906",
     "callers": (0x0042DD16,),
     "relocations": ((0x04, "open_cfw_bootloader_control_one_42e3e0", 0x0042E3E0),)},
    {"function": "open_cfw_bootloader_control_two_wrapper_42dda4",
     "start": 0x0042DDA4, "end": 0x0042DDAE,
     "sha256": "a02566589b66a631938391fbfa5c8e950eac62d5a45e037fbf7b94de93e95cb2",
     "unrelocated_sha256": "2cb70dab61786bb8a0ca4c358e1158432893275d7ed07c6004ce79c7b711b906",
     "callers": (0x0042DD26,),
     "relocations": ((0x04, "open_cfw_bootloader_control_two_42e412", 0x0042E412),)},
    {"function": "open_cfw_bootloader_control_bits_dispatch_42e1c4",
     "start": 0x0042E1C4, "end": 0x0042E1DA,
     "sha256": "8aa6ac1511e5e2da57a358e821a85859d7ffb97ef6e2b326f56f0eb276bae818",
     "unrelocated_sha256": "192c434907f6c4eb54fbe5790cd26c5ef9279e3417fe6bb3b4f29c25f0f639a9",
     "callers": (0x0042DD2C,),
     "relocations": ((0x08, "open_cfw_bootloader_control_fault_42de58", 0x0042DE58),
                     (0x10, "open_cfw_bootloader_control_terminal_loop_provider_42e1da", 0x0042E1DA))},
    {"function": "open_cfw_bootloader_control_terminal_loop_42e1da",
     "start": 0x0042E1DA, "end": 0x0042E1EC,
     "sha256": "52e02a7a6d3c381ed3daa583fb765a14e5b7610f3e9ff1ad3b259da0ce762ca3",
     "unrelocated_sha256": "08fbcbd480f53dd4e0516ed99b0ee572d3f850af576459f1ce1c7e53771a3c47",
     "callers": (0x0042E1D4,),
     "relocations": ((0x04, "open_cfw_bootloader_control_terminal_42e444", 0x0042E444),
                     (0x0C, "open_cfw_bootloader_runtime_notify_416378", 0x00416378))},
)

CONTEXT_LIFECYCLE = (
    {"function": "open_cfw_bootloader_runtime_queue_context_init_42dd70",
     "start": 0x0042DD70, "end": 0x0042DD98,
     "sha256": "b1a116c4a0b095a6b25414510fcd994e43043a3cb8048d6adecb0ccd4e62e9a7",
     "unrelocated_sha256": "73d3c112f75080f61acae6675511fc705a04b817e3c588408bd30042eaa5c47c",
     "callers": (0x0042DD1A,), "stored_pointer": None,
     "relocations": ((0x0C, "open_cfw_bootloader_runtime_queue_create_416816", 0x00416816),
                     (0x18, "open_cfw_bootloader_allocation_failure_41b2f8", 0x0041B2F8))},
    {"function": "open_cfw_bootloader_runtime_action_context_init_42ddae",
     "start": 0x0042DDAE, "end": 0x0042DDDA,
     "sha256": "380371eb1ff732482bbf5862d645eeb7e2198d5366513a326da54e1493fab666",
     "unrelocated_sha256": "d82b70ae5c6d7b9e075ac3ba24496e5eb54cb87365becdd9add92fc50bc8e574",
     "callers": (), "stored_pointer": 0x004343FE,
     "relocations": ((0x10, "open_cfw_bootloader_runtime_dispatch_4160fe", 0x004160FE),
                     (0x1C, "open_cfw_bootloader_allocation_failure_41b2f8", 0x0041B2F8))},
    {"function": "open_cfw_bootloader_runtime_action_context_deinit_42ddda",
     "start": 0x0042DDDA, "end": 0x0042DDF2,
     "sha256": "11df23f5964afb35c73937e9b03e8b010cce58ad1d840e5ea106b8b1abd1b6c1",
     "unrelocated_sha256": "dbd84048dbc1728d0fc7a7c13f4426b3bb37398349dc7bb813edbb70b9736448",
     "callers": (), "stored_pointer": 0x00434402,
     "relocations": ((0x0E, "open_cfw_bootloader_runtime_action_416200", 0x00416200),)},
    {"function": "open_cfw_bootloader_runtime_enable_sequence_42ddf2",
     "start": 0x0042DDF2, "end": 0x0042DE0E,
     "sha256": "2e690fb77d2d549104eaeb32851f8dfc94e079fb872890a5258604be9be8782c",
     "unrelocated_sha256": "f5c0449de46d42f24c63c3f558dc9aa63ca0b7123ee43e08ba92dc47e209f6d4",
     "callers": (0x0042E086, 0x0042E0F2), "stored_pointer": None,
     "relocations": ((0x02, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC),
                     (0x08, "open_cfw_bootloader_runtime_enable_41f8ba", 0x0041F8BA),
                     (0x12, "open_cfw_bootloader_runtime_mode_set_41ba80", 0x0041BA80),
                     (0x16, "open_cfw_bootloader_runtime_commit_41c990", 0x0041C990))},
)

EVENT_CONTROL_WRAPPERS = (
    {"function": "open_cfw_bootloader_event_wait_one_wrapper_42e2ea",
     "start": 0x0042E2EA, "end": 0x0042E2F8,
     "sha256": "755001d459d0d7af2b51fc148548078f44c848f2c6e735507029ffc337ba07f8",
     "unrelocated_sha256": "b2e9d3e4bd105ff8427fa2c89ebc03d29ea7c87a36cedac9f8299220f1d69b5e",
     "callers": (0x0042E30A,),
     "relocation": (0x08, "open_cfw_bootloader_event_wait_42e2a2", 0x0042E2A2)},
    {"function": "open_cfw_bootloader_guarded_context_teardown_42e3ca",
     "start": 0x0042E3CA, "end": 0x0042E3E0,
     "sha256": "544c355918dcd5b5ceb47a9c31bda9a753885aaf41bcd3ed957ae58e587fcf4f",
     "unrelocated_sha256": "74b4af3f060bbe60742d2e17e3f0001316738895cf91dc614049567d3f3185f2",
     "callers": (),
     "relocation": (0x0C, "open_cfw_bootloader_guarded_action_416200", 0x00416200)},
    {"function": "open_cfw_bootloader_event_bit_set_42e444",
     "start": 0x0042E444, "end": 0x0042E458,
     "sha256": "3099730c70327b1b039a6b0ea58e5a9b2a50f8eab76da2a4dac89a4fb4565c3c",
     "unrelocated_sha256": "fb42d9e8e3c1ce65bb07a5817d38fa5aac8cdf0cf983f39c72173f661e205013",
     "callers": (0x0042E1DE,),
     "relocation": (0x0E, "open_cfw_bootloader_event_bits_set_41652e", 0x0041652E)},
)

EVENT_SETUP_WRAPPERS = (
    {"function": "open_cfw_bootloader_event_runtime_setup_42e278",
     "start": 0x0042E278, "end": 0x0042E284,
     "sha256": "467af532a72d356addb9577ade72a626da8322be6ff7ed42015afb2f56b42741",
     "unrelocated_sha256": "4658dcdec39f0fc2e56a1cf1cff6e832accdd7f1553438b173a234bc9923629e",
     "callers": (0x0042E306,),
     "relocations": ((0x02, "open_cfw_bootloader_event_runtime_init_42e53c", 0x0042E53C),
                     (0x06, "open_cfw_bootloader_event_callback_dispatch_provider_42e284", 0x0042E284))},
    {"function": "open_cfw_bootloader_event_callback_dispatch_42e284",
     "start": 0x0042E284, "end": 0x0042E2A2,
     "sha256": "fd2c715cd5191d39eac7a7dee7b7a14d0a3f03f4caaca7fcae41bf32c8f72c67",
     "unrelocated_sha256": "7041c47adb8f1c02f7770e4d5d707bacfc44b02b77a5e5b053b40f2a711bf156",
     "callers": (0x0042E27E,),
     "relocations": ((0x02, "open_cfw_bootloader_runtime_value_4161c6", 0x004161C6),
                     (0x08, "open_cfw_bootloader_runtime_call_4161ce", 0x004161CE),
                     (0x12, "open_cfw_bootloader_runtime_value_4161c6", 0x004161C6),
                     (0x18, "open_cfw_bootloader_runtime_call_4161ce", 0x004161CE))},
)

EVENT_STATE_SERVICES = (
    {"function": "open_cfw_bootloader_retained_state_probe_42e224", "start": 0x0042E224, "end": 0x0042E254, "sha256": "cbb734736967e924c509fd7a235cc7be828b37a7f73ea981c52bd0f4438b4eec", "unrelocated_sha256": "46497ad8bd1d7e5ef5ee9c8605fcb19d93899052694d0315ab0341db032d744d", "callers": (0x0042E30E,), "stored_pointer": None, "relocations": ((0x1A, "open_cfw_bootloader_log_4176ce", 0x004176CE),)},
    {"function": "open_cfw_bootloader_event_flags_init_42e254", "start": 0x0042E254, "end": 0x0042E276, "sha256": "d5ddf3da1b0a6ad069d11bf5fa3f7cee7bb7b49da7f88f5f7fc41db45f3c8682", "unrelocated_sha256": "d09ea77084ebbcd63badf8f4cb17da34515b888b0461430076cef398e2014264", "callers": (0x0042E2FE,), "stored_pointer": None, "relocations": ((0x06, "open_cfw_bootloader_event_flags_create_4164da", 0x004164DA), (0x12, "open_cfw_bootloader_allocation_failure_41b2f8", 0x0041B2F8))},
    {"function": "open_cfw_bootloader_guard_context_init_42e39c", "start": 0x0042E39C, "end": 0x0042E3CA, "sha256": "1b39880e3d47e3da3e72511ef04e72f33ed5dbf7bb4bdc1e678cc1ec8e3346e2", "unrelocated_sha256": "6618177ec909d6f2574ce8a75118a613d8c9d1a2790a698458f6b40a1ed48724", "callers": (), "stored_pointer": 0x0043440E, "relocations": ((0x02, "open_cfw_bootloader_runtime_prepare_416058", 0x00416058), (0x0E, "open_cfw_bootloader_runtime_dispatch_4160fe", 0x004160FE), (0x1A, "open_cfw_bootloader_allocation_failure_41b2f8", 0x0041B2F8), (0x28, "open_cfw_bootloader_runtime_finalize_4160b0", 0x004160B0))},
    {"function": "open_cfw_bootloader_control_one_wait_42e3e0", "start": 0x0042E3E0, "end": 0x0042E412, "sha256": "2db659b64257eab40973463ed42d70b5bb519506294f949a56792e597ebae723", "unrelocated_sha256": "3908088fe1891671c347f922421e245639edd851ab3531ed42b17c05dc6917a8", "callers": (0x0042DD9E,), "stored_pointer": None, "relocations": ((0x0E, "open_cfw_bootloader_event_wait_4162c4", 0x004162C4), (0x2C, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
    {"function": "open_cfw_bootloader_control_two_publish_42e412", "start": 0x0042E412, "end": 0x0042E444, "sha256": "22dc8b8696ddc339b98a05705bbda6aa19bd401b7c9ee611bd51e4f42fe68cc9", "unrelocated_sha256": "e9ab8f7d865551e747a28b8032cbe2ddc27450afef8159d84aa5e7543ab92d98", "callers": (0x0042DDA8,), "stored_pointer": None, "relocations": ((0x1C, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x2C, "open_cfw_bootloader_event_bits_set_41652e", 0x0041652E))},
)

SMALL_RUNTIME_SERVICES = (
    {"function": "open_cfw_bootloader_state_update_critical_42cea4", "start": 0x0042CEA4, "end": 0x0042CED8, "sha256": "5e1f4567b244b4e447b9c7adefa7e1995a8994847c42da20da7cacf0269c17e1", "unrelocated_sha256": "f4e996fb208d73eaba0069e306a1306ba73bc28b9a5acf50b43695df8a86a49b", "callers": (0x0042CF78, 0x0042CFA0, 0x0042CFC4), "stored_pointer": None, "relocations": ((0x04, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC), (0x28, "open_cfw_bootloader_state_adjust_42cdf8", 0x0042CDF8))},
    {"function": "open_cfw_bootloader_chunked_indirect_visit_42d9f0", "start": 0x0042D9F0, "end": 0x0042DA1E, "sha256": "8094a3c36380823dea4b1d9e382fd01bfc1ada3907d83eba63f3e603f1230620", "unrelocated_sha256": "8094a3c36380823dea4b1d9e382fd01bfc1ada3907d83eba63f3e603f1230620", "callers": (0x0042DB00,), "stored_pointer": None, "relocations": ()},
    {"function": "open_cfw_bootloader_hardware_channel_normalize_42eda0", "start": 0x0042EDA0, "end": 0x0042EDF6, "sha256": "d8c726d50ce3b131a09fbd3baf26fa0be431dc76187560db65fe8e26b81e267e", "unrelocated_sha256": "90191c215f584a81ffca65fc2a302b2d878667c0169c12c97b1acf631afcfe55", "callers": (0x00430156,), "stored_pointer": None, "relocations": ((0x46, "open_cfw_bootloader_clock_config_422364", 0x00422364),)},
    {"function": "open_cfw_bootloader_platform_boot_sequence_4301d6", "start": 0x004301D6, "end": 0x004301F4, "sha256": "c1c946447d989615f057be7707475b14318dd6dc4f4db74fe603c662d579fd86", "unrelocated_sha256": "78f443c4dd221116c3a8cbd6acdc74c3038e22285eaabf79e44acd8bd84b3aef", "callers": (), "stored_pointer": 0x00433440, "relocations": ((0x06, "open_cfw_bootloader_scb_priority_nibble_430280", 0x00430280), (0x0A, "open_cfw_bootloader_mode_one_apply_42fff2", 0x0042FFF2), (0x0E, "open_cfw_bootloader_platform_stage_430000", 0x00430000), (0x12, "open_cfw_bootloader_platform_prepare_41f612", 0x0041F612), (0x16, "open_cfw_bootloader_platform_finish_430502", 0x00430502))},
    {"function": "open_cfw_bootloader_address_validate_430a60", "start": 0x00430A60, "end": 0x00430A9C, "sha256": "a4764c54fa357e914e1d59504315967881f056b4a078c086b0597de5c669896b", "unrelocated_sha256": "9ce9a927e722650fcc0ec7b8764a9be70b94f047c7c7c26afaab0404abcc8572", "callers": (0x00430AA8, 0x00430AD0, 0x00430AF4), "stored_pointer": None, "relocations": ((0x1A, "open_cfw_bootloader_address_limit_query_41d792", 0x0041D792),)},
)

RUNTIME_CONTROL_SERVICES = (
    {"function": "open_cfw_bootloader_hardware_readiness_gate_42bf54", "start": 0x0042BF54, "end": 0x0042BFA4, "sha256": "ea709a4b368ad40d8d1cc341d60deb5b3a84f33f0c7b080832f667538266c878", "unrelocated_sha256": "33f339eb82333f369613a9c61ca88edc397cd53acec61d1c5eccf06c8ef782fb", "callers": (), "stored_pointer": 0x0041D16C, "relocations": ((0x14, "open_cfw_bootloader_mode_query_41bf84", 0x0041BF84), (0x26, "open_cfw_bootloader_float_probe_41ca2c", 0x0041CA2C), (0x38, "open_cfw_bootloader_delay_status_change_41d21c", 0x0041D21C))},
    {"function": "open_cfw_bootloader_event_wait_mask_42e2a2", "start": 0x0042E2A2, "end": 0x0042E2EA, "sha256": "f7d5ce722b09295e04d5c2525cb58137a589a07472efd03673b559a8291cc085", "unrelocated_sha256": "4cb7aa4f0eee6a8f24c5b089cd03a53dd47fb0e07726c03696acb3ba3a73b007", "callers": (0x0042E2F2,), "stored_pointer": None, "relocations": ((0x0E, "open_cfw_bootloader_runtime_transfer_41623a", 0x0041623A), (0x1E, "open_cfw_bootloader_runtime_flags_wait_416590", 0x00416590), (0x40, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
    {"function": "open_cfw_bootloader_aligned_guarded_dispatch_42e4a0", "start": 0x0042E4A0, "end": 0x0042E4F4, "sha256": "d0924cd0559fc057d2a0eb2aa7558f1ef4a237b073daad60d1e80bab754b317e", "unrelocated_sha256": "9d909667005fac9e5860e1e3d64146fc43bfab6d21479ea9dbab8b24682eb0f2", "callers": (0x0042E508,), "stored_pointer": None, "relocations": ((0x1C, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC), (0x22, "open_cfw_bootloader_runtime_lock_41bd92", 0x0041BD92), (0x30, "open_cfw_bootloader_guarded_call_cleanup_42e8a4", 0x0042E8A4), (0x36, "open_cfw_bootloader_runtime_unlock_41bde4", 0x0041BDE4))},
    {"function": "open_cfw_bootloader_register_power_toggle_42f1c8", "start": 0x0042F1C8, "end": 0x0042F204, "sha256": "938e0f238204451a2aff50fd378808f5f3d2780c3627018935d2e382e94f9361", "unrelocated_sha256": "3a7d939562c4ed98e8b8a506ec3835ba2e13fe65fc0063caa9f5882347627696", "callers": (0x0042F268, 0x0042F2D4, 0x0042F336, 0x0042F37E), "stored_pointer": None, "relocations": ((0x16, "open_cfw_bootloader_delay_cycles_41d1c0", 0x0041D1C0), (0x1C, "open_cfw_bootloader_power_control_41c838", 0x0041C838), (0x24, "open_cfw_bootloader_power_control_41c838", 0x0041C838), (0x2A, "open_cfw_bootloader_delay_cycles_41d1c0", 0x0041D1C0))},
)

EVENT_SERVICE_LOOP = {
    "function": "open_cfw_bootloader_event_service_loop_42e2f8",
    "start": 0x0042E2F8, "end": 0x0042E39A,
    "sha256": "d735b2b537e7adbf8183b564920a0ccca1fbbeb67a10083476918e6e7d7a84f6",
    "unrelocated_sha256": "911313f6e17e0ad15a23b9773553ac00457107137008d941eb0e3a9db15be559",
    "callers": (), "stored_pointer": 0x0042E48C,
    "relocations": ((0x06, "open_cfw_bootloader_event_flags_init_42e254", 0x0042E254), (0x0A, "open_cfw_bootloader_noop_callback_42e276", 0x0042E276), (0x0E, "open_cfw_bootloader_event_runtime_setup_42e278", 0x0042E278), (0x12, "open_cfw_bootloader_event_wait_one_wrapper_42e2ea", 0x0042E2EA), (0x16, "open_cfw_bootloader_retained_state_probe_42e224", 0x0042E224), (0x2E, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x38, "open_cfw_bootloader_memset_wrapper_426c10", 0x00426C10), (0x42, "open_cfw_bootloader_runtime_context_create_42dca2", 0x0042DCA2), (0x58, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x62, "open_cfw_bootloader_memset_wrapper_426c10", 0x00426C10), (0x6C, "open_cfw_bootloader_runtime_context_create_42dca2", 0x0042DCA2), (0x74, "open_cfw_bootloader_noop_callback_42e39a", 0x0042E39A), (0x84, "open_cfw_bootloader_event_wait_4162c4", 0x004162C4), (0x8A, "open_cfw_bootloader_runtime_time_4160e8", 0x004160E8)),
}

EVENT_RUNTIME_SERVICES = (
    {"function": "open_cfw_bootloader_event_runtime_init_42e53c", "start": 0x0042E53C, "end": 0x0042E642, "sha256": "8cbbeffaffa2a5c06366020712b77d72be670a18d7ff3c319da22d4cc5bd60e1", "unrelocated_sha256": "d86265af7b562c0a4f2b77135c615aaf8a4ad4befd4fe80b48fd39c1f3cb1517", "callers": (0x0042E27A,), "relocations": ((0x14, "open_cfw_bootloader_queue_create_416816", 0x00416816), (0x38, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x54, "open_cfw_bootloader_named_object_create_4163b2", 0x004163B2), (0x78, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x8C, "open_cfw_bootloader_event_object_create_416610", 0x00416610), (0xB0, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0xC2, "open_cfw_bootloader_runtime_object_delete_416200", 0x00416200), (0xDA, "open_cfw_bootloader_runtime_task_create_4160fe", 0x004160FE), (0xFE, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
    {"function": "open_cfw_bootloader_event_callback_loop_42e644", "start": 0x0042E644, "end": 0x0042E686, "sha256": "12cee7c0ef1b572aab563a611afef44f7a04b723797499083ab338c6dc34d413", "unrelocated_sha256": "955ecd8eea75b567485ae7c243dc4ebe3e191c28f0a7acf5a35ca9d5c427c037", "callers": (), "relocations": ((0x1A, "open_cfw_bootloader_queue_receive_416920", 0x00416920), (0x3C, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
    {"function": "open_cfw_bootloader_event_callback_enqueue_42e686", "start": 0x0042E686, "end": 0x0042E6F2, "sha256": "8d2dc54d9c093c0c8ee2ef3c2b390c2719cb6b22fde97ccc7845cf180c960ed3", "unrelocated_sha256": "ec7c3afdd0a93421ade6491970da330e86857830703e57e3005e46e1aff4133f", "callers": (0x0042E79C,), "relocations": ((0x28, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x42, "open_cfw_bootloader_queue_send_4168a2", 0x004168A2), (0x64, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
)

CONTROL_ORCHESTRATION = (
    {"function": "open_cfw_bootloader_control_orchestrator_42dd14", "start": 0x0042DD14, "end": 0x0042DD68, "sha256": "bed813bc7b04b8ac8dffe02c444a4ac57d3d2d95af223d02cad46acde08ff524", "unrelocated_sha256": "c69f469c3ed42dd95b6493d1c3a0f97f7f0c47b0486c23219164169f7f453caa", "callers": (), "stored_pointer": 0x0042E174, "relocations": ((0x02, "open_cfw_bootloader_control_one_wrapper_42dd9a", 0x0042DD9A), (0x06, "open_cfw_bootloader_runtime_queue_context_init_42dd70", 0x0042DD70), (0x0A, "open_cfw_bootloader_runtime_context_wrapper_42dd68", 0x0042DD68), (0x0E, "open_cfw_bootloader_noop_callback_42dd98", 0x0042DD98), (0x12, "open_cfw_bootloader_control_two_wrapper_42dda4", 0x0042DDA4), (0x18, "open_cfw_bootloader_control_bits_dispatch_42e1c4", 0x0042E1C4), (0x26, "open_cfw_bootloader_event_wait_4162c4", 0x004162C4), (0x4E, "open_cfw_bootloader_log_4176ce", 0x004176CE))},
    {"function": "open_cfw_bootloader_critical_dispatch_transaction_42de0e", "start": 0x0042DE0E, "end": 0x0042DE58, "sha256": "ac57a9b6547160c8259307f2400e572680d610c2d7d8913fe30f29b21c1e28f0", "unrelocated_sha256": "df0a8dfa30390dd20818f35e9c91213538e151d35b97eaaf1a55e40049650524", "callers": (0x0042DE9A, 0x0042DF0C, 0x0042E00A), "stored_pointer": None, "relocations": ((0x16, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x1C, "open_cfw_bootloader_critical_enter_41b8ec", 0x0041B8EC), (0x28, "open_cfw_bootloader_memcpy_words_4156ac", 0x004156AC), (0x34, "open_cfw_bootloader_alignment_dispatch_42e4f4", 0x0042E4F4), (0x42, "open_cfw_bootloader_terminal_mode_42e514", 0x0042E514))},
)

CONTEXT_PUBLISH = {
    "function": "open_cfw_bootloader_runtime_context_publish_42dca2",
    "start": 0x0042DCA2, "end": 0x0042DD14,
    "sha256": "200d91da3673bb39591b488795b73a7de75ffcba3f22e666af257ddd45a08f5d",
    "unrelocated_sha256": "7203593c94d7fdf2b2075062728e5a981eaa73d282e3d7e06984b35aa55309bc",
    "callers": (0x0042E33A, 0x0042E364),
    "relocations": ((0x2A, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x38, "open_cfw_bootloader_queue_send_4168a2", 0x004168A2), (0x5A, "open_cfw_bootloader_log_4176ce", 0x004176CE), (0x68, "open_cfw_bootloader_runtime_transfer_41623a", 0x0041623A)),
}

LATE_WRAPPERS = (
    {"function": "open_cfw_bootloader_mode_one_apply_42fff2",
     "start": 0x0042FFF2, "end": 0x0042FFFE,
     "sha256": "75fb4f494d3b0844cdd83c4a29b56a600221b0c11cabe5a37da80055611739e5",
     "unrelocated_sha256": "5130a565487bf859f315758ff01bab0b9ba664d8c202f946fb7321f79f836b02",
     "callers": (0x004301E0,), "stored_pointer": None,
     "relocations": ((0x06, "open_cfw_bootloader_mode_apply_42ff00", 0x0042FF00),)},
    {"function": "open_cfw_bootloader_boolean_route_status_4303bc",
     "start": 0x004303BC, "end": 0x004303DE,
     "sha256": "c6f1ae52eca3aa5ea02a327560090a3b77b3603d70b8ef1db09ebf422b2495d1",
     "unrelocated_sha256": "20761cc03c65d94830c9f9ed045b754fed6db00929476daf9300f4e53475ede8",
     "callers": (0x0042FF3C, 0x0042FF52, 0x0042FF68, 0x0042FF7E,
                 0x0042FFC4, 0x0042FFCE, 0x0042FFEA), "stored_pointer": None,
     "relocations": ((0x10, "open_cfw_bootloader_boolean_route_41d9aa", 0x0041D9AA),)},
    {"function": "open_cfw_bootloader_validated_byte_copy_430a9c",
     "start": 0x00430A9C, "end": 0x00430AC4,
     "sha256": "227e07edede8d13c9bee39f2e4745468bb8290b3ae67e63d7af1b4546fb28ceb",
     "unrelocated_sha256": "f4365efc56e758fc3ac038c09d3e68afb1dc4f47ad7354c8bf6e94d21c22c466",
     "callers": (), "stored_pointer": None,
     "relocations": ((0x0C, "open_cfw_bootloader_address_validate_430a60", 0x00430A60),
                     (0x1A, "open_cfw_bootloader_byte_copy_41568c", 0x0041568C))},
    {"function": "open_cfw_bootloader_validated_word_transfer_430ac4",
     "start": 0x00430AC4, "end": 0x00430AEC,
     "sha256": "e868f672a76b215ca5f17a8cedca05ef0df0eddaac7a9b5e1dc024464a768512",
     "unrelocated_sha256": "b975f25f8af7dc30afb5984a14bb71e933b92d02dfba04cd233bd7202b7e43fe",
     "callers": (), "stored_pointer": None,
     "relocations": ((0x0C, "open_cfw_bootloader_address_validate_430a60", 0x00430A60),
                     (0x1A, "open_cfw_bootloader_word_transfer_provider_430b10", 0x00430B10))},
    {"function": "open_cfw_bootloader_word_transfer_critical_430b10",
     "start": 0x00430B10, "end": 0x00430B3C,
     "sha256": "2c87f99aa6b925741f616a9d79ff9fc3ccb3435fd812d87072f2946425dc6f91",
     "unrelocated_sha256": "fe3259e33c8cbb4cc0f524ffe128e948b6e2ff3371ae87859719334722c6dac3",
     "callers": (0x00430ADE,), "stored_pointer": None,
     "relocations": ((0x12, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
                     (0x20, "open_cfw_bootloader_alignment_dispatch_42e4f4", 0x0042E4F4))},
    {"function": "open_cfw_bootloader_platform_services_init_43194c",
     "start": 0x0043194C, "end": 0x0043198A,
     "sha256": "3d057acab6aa34a7443a18c5f1a7a63133a12944656603585df0f08982d41316",
     "unrelocated_sha256": "f20e6cf0468641fe0cccff820de74f1dfee0ce7a5197ccecc9d1dfc2e816d7d9",
     "callers": (), "stored_pointer": 0x00433448,
     "relocations": ((0x02, "open_cfw_bootloader_platform_init_41733c", 0x0041733C),
                     (0x0A, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x12, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x1A, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x22, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x2A, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x32, "open_cfw_bootloader_platform_route_4174a6", 0x004174A6),
                     (0x36, "open_cfw_bootloader_platform_finish_417392", 0x00417392))},
)

NOOP_CALLBACKS = (
    {"function": "open_cfw_bootloader_noop_callback_42dd98",
     "start": 0x0042DD98, "end": 0x0042DD9A, "callers": (0x0042DD22,),
     "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
     "unrelocated_sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"},
    {"function": "open_cfw_bootloader_noop_callback_42e276",
     "start": 0x0042E276, "end": 0x0042E278, "callers": (0x0042E302,),
     "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
     "unrelocated_sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"},
    {"function": "open_cfw_bootloader_noop_callback_42e39a",
     "start": 0x0042E39A, "end": 0x0042E39C, "callers": (0x0042E36C,),
     "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
     "unrelocated_sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"},
)
NOOP_CALLBACK_SHA = "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"

STARTUP_SERVICES = (
    {"function": "open_cfw_bootloader_vector_table_relocate_432910",
     "start": 0x00432910, "end": 0x0043291A,
     "sha256": "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c",
     "unrelocated_sha256": "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c",
     "main_start": 0x005E4228, "callers": (0x0043297C,), "stored_pointer": None,
     "relocations": (), "literals": ((0x0043292C, 0x00410000), (0x00432930, 0xE000ED08))},
    {"function": "open_cfw_bootloader_stack_limits_init_43291a",
     "start": 0x0043291A, "end": 0x0043292A,
     "sha256": "320ede47e52c2388957bf2ba938af992c2fb0cfa01e63bf1b6d6fea1f56b5980",
     "unrelocated_sha256": "8766f0e90be5027c2318484e7caf3d1e90b6c0dd518b1b44e840c11cf6b17753",
     "main_start": 0x005E4232, "callers": (), "stored_pointer": 0x00410004,
     "relocations": ((0x0A, "open_cfw_bootloader_process_stack_provider_43293c", 0x0043293C),),
     "literals": ((0x00432934, 0x2007D000),)},
    {"function": "open_cfw_bootloader_process_stack_init_43293c",
     "start": 0x0043293C, "end": 0x00432954,
     "sha256": "83b3b48d97503ec64f1922ffc3774a94e510616f7621abca62508fe9aa65d21a",
     "unrelocated_sha256": "6edb7912c020837b919c7f14c6750aec722f8b2f0abbc92a2e719a652d819731",
     "main_start": 0x005E4254, "callers": (0x00432924,), "stored_pointer": None,
     "relocations": ((0x10, "open_cfw_bootloader_fpu_provider_432958", 0x00432958),
                     (0x14, "open_cfw_bootloader_runtime_start_43297c", 0x0043297C)),
     "literals": ((0x00432954, 0xFEF5EDA5),)},
    {"function": "open_cfw_bootloader_fpu_enable_432958",
     "start": 0x00432958, "end": 0x0043297A,
     "sha256": "0a4d65c423e1840131ae14f4b432a592b8928d1dffeb7624edd12b5e483dd00a",
     "unrelocated_sha256": "0a4d65c423e1840131ae14f4b432a592b8928d1dffeb7624edd12b5e483dd00a",
     "main_start": 0x005E4270, "callers": (0x0043294C,), "stored_pointer": None,
     "relocations": (), "literals": ()},
)

STARTUP_RUNTIME = (
    {"function": "open_cfw_bootloader_runtime_start_43297c",
     "start": 0x0043297C, "end": 0x0043299A,
     "sha256": "0f697df14e7a3026cd502d19b3c2bbdd540389796647c301283e815b47a6be2d",
     "unrelocated_sha256": "a709d60bc609aa531644c3db7d80fff60277a16d425ef1f830569cc8afeb86a7",
     "main_start": 0x005E4294,
     "main_sha256": "6b05bad848e8a7ff78a6a2ba418f5e183a8bdd541fc89203d6c496c2e32778d6",
     "identical_bytes": 27, "difference_runs": 2, "callers": (0x00432950,),
     "relocations": ((0x00, "open_cfw_bootloader_vector_table_provider_432910", 0x00432910),
                     (0x08, "open_cfw_bootloader_init_array_provider_43299c", 0x0043299C),
                     (0x16, "open_cfw_bootloader_platform_init_provider_41b862", 0x0041B862),
                     (0x1A, "open_cfw_bootloader_terminal_loop_provider_4329c4", 0x004329C4))},
    {"function": "open_cfw_bootloader_init_array_run_43299c",
     "start": 0x0043299C, "end": 0x004329BC,
     "sha256": "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd",
     "unrelocated_sha256": "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd",
     "main_start": 0x005E42B4,
     "main_sha256": "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd",
     "identical_bytes": 32, "difference_runs": 0, "callers": (0x00432984,),
     "relocations": ()},
    {"function": "open_cfw_bootloader_terminal_loop_4329c4",
     "start": 0x004329C4, "end": 0x004329D2,
     "sha256": "bea26157ebbe31038bcf52f8a3233885515b034fd35636d6349e9b21370f26a2",
     "unrelocated_sha256": "e24a1349df6d186d6dbd5558a6e03f2e5bd58d8791f8a899b6be5e2ccbacf22f",
     "main_start": 0x005E42DC,
     "main_sha256": "e11450466f0c5c1ad25f3eb6a87eac6bae14c8acceb0edba3eaf243463cd9027",
     "identical_bytes": 11, "difference_runs": 2, "callers": (0x00432996,),
     "relocations": ((0x08, "open_cfw_bootloader_terminal_service_provider_41b298", 0x0041B298),)},
)
STARTUP_RUNTIME_LITERALS = (
    (0x004329BC, 0x0000071C), (0x004329C0, 0x00000760),
)
STARTUP_RUNTIME_MAIN_LITERALS = (
    (0x005E42D4, 0x001790F4), (0x005E42D8, 0x00179138),
)

ALIGNMENT_DISPATCH = {
    "function": "open_cfw_bootloader_alignment_dispatch_42e4f4",
    "start": 0x0042E4F4, "end": 0x0042E50E,
    "sha256": "b53569c4e9b718913c54a8e7137c6e1c91a6b6efd7374a4c043d8103fe4f423e",
    "unrelocated_sha256": "74321ec57a2083ec296094680e6c43aa481787040efa2b4442f56ca31dd1cfc3",
    "main_start": 0x004D0A2C, "callers": (0x0042DE42, 0x00430B30),
    "relocations": ((0x14, "open_cfw_bootloader_aligned_provider_42e4a0", 0x0042E4A0),),
    "literal": (0x0042E510, 0x08000140),
    "main_literal": (0x004D0A48, 0x08000140),
}

GUARDED_CALL = {
    "function": "open_cfw_bootloader_guarded_call_cleanup_42e8a4",
    "start": 0x0042E8A4, "end": 0x0042E8C2,
    "sha256": "c4d87e8f170f723eedb93c2fd52d09e6f176b9d41d75a0dba72b894fd9a42275",
    "unrelocated_sha256": "c4d87e8f170f723eedb93c2fd52d09e6f176b9d41d75a0dba72b894fd9a42275",
    "main_start": 0x00541B7C, "callers": (0x0042E4D0,),
    "literals": ((0x0042E8C8, 0x40014008), (0x0042E8CC, 0x40014024)),
    "main_literals": ((0x00541BA0, 0x40014008), (0x00541BA4, 0x40014024)),
}

EVENT_DISPATCH = {
    "function": "open_cfw_bootloader_event_dispatch_42f38e",
    "start": 0x0042F38E, "end": 0x0042F3DA,
    "sha256": "21de4d3df3c7a071b8ced878b814af7bdadfd59d5d1986104abb50bede8fb90a",
    "unrelocated_sha256": "cd4e930e11246ab861c5a68f3ef0bfbd03315e7f51d01633b961a9e81ad7f92b",
    "main_start": 0x0059FD36, "callers": (), "stored_pointer": 0x0041D1B4,
    "relocations": ((0x2A, "open_cfw_bootloader_event_zero_provider_42f2fa", 0x0042F2FA),
                    (0x32, "open_cfw_bootloader_event_value_provider_42f204", 0x0042F204)),
    "literals": ((0x0042F630, 0x447A0000), (0x0042F634, 0x2002705C)),
    "main_literals": ((0x0059FFD4, 0xC3888000), (0x0059FFD8, 0x447A0000)),
}

HW_HANDLE_SERVICES = (
    {"function": "open_cfw_bootloader_hw_handle_reset_42ea32",
     "start": 0x0042EA32, "end": 0x0042EA68,
     "sha256": "33eeb24b6b211f5d9920815c5ccc30b5c985bb5f094890a5e543b85e194c19b4",
     "unrelocated_sha256": "33eeb24b6b211f5d9920815c5ccc30b5c985bb5f094890a5e543b85e194c19b4",
     "main_start": 0x0055DAAE, "callers": (0x004301C4,)},
    {"function": "open_cfw_bootloader_hw_handle_configure_42eb74",
     "start": 0x0042EB74, "end": 0x0042EBAA,
     "sha256": "d227983f298102fc851a91454e4e48ffcaf57a43f050190e690a7cd6629f7fbb",
     "unrelocated_sha256": "d227983f298102fc851a91454e4e48ffcaf57a43f050190e690a7cd6629f7fbb",
     "main_start": 0x0055DBF0, "callers": (0x00430084,)},
    {"function": "open_cfw_bootloader_hw_handle_enable_42ebaa",
     "start": 0x0042EBAA, "end": 0x0042EBE2,
     "sha256": "052085424ed967f77d8f36303a119e299f4428fde2a6482b8a08f4686de151cd",
     "unrelocated_sha256": "052085424ed967f77d8f36303a119e299f4428fde2a6482b8a08f4686de151cd",
     "main_start": 0x0055DC26, "callers": (0x0043010C,)},
    {"function": "open_cfw_bootloader_hw_handle_disable_42ebe2",
     "start": 0x0042EBE2, "end": 0x0042EC0C,
     "sha256": "ebd287ea1a933ce89fb082d850d121c22baa5a0a765804e468539386133187d0",
     "unrelocated_sha256": "ebd287ea1a933ce89fb082d850d121c22baa5a0a765804e468539386133187d0",
     "main_start": 0x0055DC5E, "callers": (0x00430150,)},
)
HW_HANDLE_LITERALS = (
    (0x0042F17C, 0x01AFAFAF), (0x0042F180, 0x40038000),
    (0x0042F184, 0x4003800C), (0x0042F188, 0x40038040),
)
HW_HANDLE_MAIN_LITERALS = (
    (0x0055E1F8, 0x01AFAFAF), (0x0055E1FC, 0x40038000),
    (0x0055E204, 0x40038040),
)

HW_COMMAND = {
    "function": "open_cfw_bootloader_hw_handle_command_42eff4",
    "start": 0x0042EFF4, "end": 0x0042F014,
    "sha256": "ed0aedd4d0d69cedbcae932b154d2ed9f290d4c95bc0f3f06f8135539c19ec6f",
    "unrelocated_sha256": "ed0aedd4d0d69cedbcae932b154d2ed9f290d4c95bc0f3f06f8135539c19ec6f",
    "main_start": 0x0055E070, "callers": (0x00430112,),
    "literals": ((0x0042F17C, 0x01AFAFAF), (0x0042F1C4, 0x40038008)),
    "main_literals": ((0x0055E1F8, 0x01AFAFAF), (0x0055E240, 0x40038008)),
}

HW_CHANNEL_ACTIVATE = (
    {"function": "open_cfw_bootloader_hw_channel_config_42eaf6",
     "start": 0x0042EAF6, "end": 0x0042EB74,
     "sha256": "59424a9cdea76c34a98142a28944d1d1700758cc2412e7d1903be4757e1d3c04",
     "unrelocated_sha256": "59424a9cdea76c34a98142a28944d1d1700758cc2412e7d1903be4757e1d3c04",
     "source": HW_CHANNEL_SOURCE, "main_start": 0x0055DB72,
     "callers": (0x004300EC,), "cases": 256 * 8 * 2},
    {"function": "open_cfw_bootloader_hw_handle_activate_42ed60",
     "start": 0x0042ED60, "end": 0x0042EDA0,
     "sha256": "5603c205e322271c30b9c91be82538938549b50a35f8e6d1ad94de5d1bb7eb23",
     "unrelocated_sha256": "5603c205e322271c30b9c91be82538938549b50a35f8e6d1ad94de5d1bb7eb23",
     "source": HW_ACTIVATE_SOURCE, "main_start": 0x0055DDDC,
     "callers": (0x004300FC,), "cases": 4},
)

HW_CONFIG_ENUMERATE = (
    {"function": "open_cfw_bootloader_hw_config_dispatch_42ec0c",
     "start": 0x0042EC0C, "end": 0x0042ED60,
     "sha256": "b8b072619837474e9b6403d4097b20aedd8ce7f7ec8a458a1445c3574630fa83",
     "unrelocated_sha256": "b8b072619837474e9b6403d4097b20aedd8ce7f7ec8a458a1445c3574630fa83",
     "main_start": 0x0055DC88, "callers": (0x00430040,),
     "relocations": (), "cases": 16},
    {"function": "open_cfw_bootloader_hw_channel_normalize_42ee00",
     "start": 0x0042EE00, "end": 0x0042EE6C,
     "sha256": "8211026e1a7232d3cc7b527820d21a5bf55b843b9843e2db588c55777c909cb1",
     "unrelocated_sha256": "8211026e1a7232d3cc7b527820d21a5bf55b843b9843e2db588c55777c909cb1",
     "main_start": 0x0055DE7C, "callers": (0x0042EECA, 0x0042EFD0),
     "relocations": (), "cases": 4},
    {"function": "open_cfw_bootloader_hw_channel_enumerate_42ee70",
     "start": 0x0042EE70, "end": 0x0042EFF4,
     "sha256": "4051c15947e7cbab52ab6cc9a9a5993cddbd41ad9acf68b406fdee30066f5d9b",
     "unrelocated_sha256": "c69884c4fc9d791f76c2c7ef79eef74beafef2c7ae343162a99f7d1f9d91c655",
     "main_start": 0x0055DEEC, "callers": (0x00430142,),
     "relocations": ((0x5A, "open_cfw_bootloader_hw_channel_normalize_42ee00", 0x0042EE00, "STT_FUNC"),
                     (0x160, "open_cfw_bootloader_hw_channel_normalize_42ee00", 0x0042EE00, "STT_FUNC")),
     "cases": 16},
)

ORPHAN_SERVICES = (
    {"function": "open_cfw_bootloader_mode_four_wrapper_430aec",
     "start": 0x00430AEC, "end": 0x00430B0C,
     "sha256": "8b4d130ac1735011011fd8a65ded46b1c5892049315798e9c477e1745d031fb7",
     "unrelocated_sha256": "a9e49da54bb521ea38ca1a1260604be4c4dfa6a7a6d7287ff5bb6b1f7848e6a4",
     "main_start": 0x005A4F80,
     "relocations": ((0x08, "open_cfw_bootloader_mode_provider_430a60", 0x00430A60),)},
    {"function": "open_cfw_bootloader_zero_table_431e38",
     "start": 0x00431E38, "end": 0x00431E70,
     "sha256": "8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67",
     "unrelocated_sha256": "8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67",
     "main_start": 0x005FA01E, "relocations": ()},
)

CMDQ_SERVICE_MAIN_STARTS = {
    "open_cfw_bootloader_cmdq_init_427794": 0x00538D58,
    "open_cfw_bootloader_cmdq_enable_427878": 0x00538E3C,
    "open_cfw_bootloader_cmdq_disable_4278c8": 0x00538E8C,
    "open_cfw_bootloader_cmdq_alloc_block_42790a": 0x00538ECE,
    "open_cfw_bootloader_cmdq_release_block_4279be": 0x00538F82,
    "open_cfw_bootloader_cmdq_post_block_4279f0": 0x00538FB4,
    "open_cfw_bootloader_cmdq_get_status_427a56": 0x0053901A,
    "open_cfw_bootloader_cmdq_term_427ad6": 0x0053909A,
    "open_cfw_bootloader_cmdq_error_resume_427b38": 0x005390FC,
    "open_cfw_bootloader_cmdq_reset_427baa": 0x0053916E,
    "open_cfw_bootloader_cmdq_post_loop_block_427c12": 0x005391D6,
}

CMDQ_SERVICE_CALLERS = {
    "open_cfw_bootloader_cmdq_init_427794": (0x00423F4E, 0x0042C40E),
    "open_cfw_bootloader_cmdq_enable_427878": (0x00423FA6, 0x0042C448),
    "open_cfw_bootloader_cmdq_disable_4278c8": (0x00423FB2, 0x0042C454),
    "open_cfw_bootloader_cmdq_alloc_block_42790a": (0x00425D8A, 0x00425E26, 0x00425FDA),
    "open_cfw_bootloader_cmdq_release_block_4279be": (0x00425DE8, 0x00425EBA, 0x004260F0),
    "open_cfw_bootloader_cmdq_post_block_4279f0": (0x00425DD2, 0x00425EA6, 0x004260DC),
    "open_cfw_bootloader_cmdq_get_status_427a56": (0x004266A2, 0x0042C836),
    "open_cfw_bootloader_cmdq_term_427ad6": (0x00423F7A,),
    "open_cfw_bootloader_cmdq_error_resume_427b38": (0x004267A2, 0x0042C932),
    "open_cfw_bootloader_cmdq_reset_427baa": (0x00425CE4,),
    "open_cfw_bootloader_cmdq_post_loop_block_427c12": (0x00425E8C,),
}

FLOAT_AAPCS_VFP_WINDOWS = (
    (0x00426F6C, 0x00426F7E,
     "7bee97296dbe3708e41f5401aa1ec05017b4b5953280db616c82ecd8c9f50314",
     "encoding-selector pointer and s0/s1 hard-float entry capture"),
    (0x00426FBA, 0x00426FCC,
     "534893d0cff61a2667a7123582f5f242634c09fa7be24a8f6dcc3d7b8a4b0afa",
     "ratio caller pointer and s0/s1 argument setup"),
    (0x00426FD6, 0x00426FEA,
     "087c425648d2a968e431bab71da38a38b2ab457bbda2e8d5eda3e146f2d5fa1a",
     "multiplier caller pointer and s0/s1 argument setup"),
    (0x00427C90, 0x00427CA0,
     "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
     "floorf s0 argument/result veneer"),
    (0x00427CCC, 0x00427CDC,
     "85ee2ba6a57b18253f0503ab43d1a87345f4afd32574d6c2c51f037847868d38",
     "fmodf s0/s1 argument and s0 result veneer"),
    (0x00427D98, 0x00427DA8,
     "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b",
     "roundf s0 argument/result veneer"),
    (0x00427DD0, 0x00427DE0,
     "835331b3678ebbb1f451d5be4f41c76b348cbcabf12bcd1031cf7d774a6c5445",
     "ceilf s0 argument/result veneer"),
)

EXPECTED_ROWS = 272
EXPECTED_DISPOSITIONS = {
    "source_owned_production": (187, 26_720),
    "retained_typed_data": (2, 28),
    "retained_unreachable_tail": (16, 284),
    "typed_unresolved_executable": (0, 0),
    "typed_nonentry_mixed_or_data": (67, 30_121),
}

FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
)
PROFILES = {
    "apple-clang": (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
    "linux-clang": (Path("/opt/homebrew/opt/llvm@22/bin/clang"), "Homebrew clang version 22.1.8"),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def decode_thumb_bl(payload: bytes, address: int, base: int = BOOT_BASE) -> int | None:
    offset = address - base
    if offset < 0 or offset + 4 > len(payload):
        return None
    first, second = struct.unpack_from("<HH", payload, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def decode_thumb_b_w(payload: bytes, address: int, base: int = BOOT_BASE) -> int | None:
    """Decode the unconditional Thumb-2 B.W form used under the stock IT block."""
    offset = address - base
    if offset < 0 or offset + 4 > len(payload):
        return None
    first, second = struct.unpack_from("<HH", payload, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_callers(payload: bytes, target: int) -> tuple[int, ...]:
    return tuple(
        address
        for address in range(BOOT_BASE, BOOT_BASE + len(payload) - 3, 2)
        if decode_thumb_bl(payload, address) == target
    )


def difference_runs(left: bytes, right: bytes) -> int:
    indexes = [index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
    return sum(index == indexes[0] or index != indexes[pos - 1] + 1
               for pos, index in enumerate(indexes)) if indexes else 0


def extract_section(path: Path, name: str) -> tuple[bytes, int]:
    payload, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(sections, ".text." + name)
    body = payload[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    relocations = sum(
        int(item["size"]) // 8
        for item in sections
        if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
    )
    return body, relocations


def audit() -> dict:
    authenticated: dict[Path, bytes] = {}
    for path, expected in PINS.items():
        payload = path.read_bytes()
        require((len(payload), sha256(payload)) == expected, f"pin changed: {path.relative_to(ROOT)}")
        authenticated[path] = payload
    boot = authenticated[BOOT]
    main = authenticated[MAIN]

    rows = list(csv.DictReader(authenticated[CENSUS].decode().splitlines(), delimiter="\t"))
    require(len(rows) == EXPECTED_ROWS, "frontier row count changed")
    cursor = 0x00426536
    disposition_counts: dict[str, int] = {}
    disposition_bytes: dict[str, int] = {}
    for row in rows:
        start, end, size = int(row["start"], 16), int(row["end"], 16), int(row["size"])
        require(start == cursor and end > start and size == end - start, f"partition drift: {row['name']}")
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        require(sha256(body) == row["sha256"], f"span hash changed: {row['name']}")
        if row["disposition"] == "cross_image_exact_source_candidate":
            require(main.find(body) >= 0, f"cross-image candidate disappeared: {row['name']}")
        disposition_counts[row["disposition"]] = disposition_counts.get(row["disposition"], 0) + 1
        disposition_bytes[row["disposition"]] = disposition_bytes.get(row["disposition"], 0) + size
        cursor = end
    require(cursor == 0x00434477, "frontier partition no longer reaches stock EOF")
    require(sum(disposition_bytes.values()) == 57_153, "frontier byte conservation changed")
    require({key: (disposition_counts.get(key, 0), disposition_bytes.get(key, 0))
             for key in EXPECTED_DISPOSITIONS} == EXPECTED_DISPOSITIONS,
            "frontier classification changed")

    upstream = authenticated[AMBIQ_SOURCE].decode()
    mnemonic_source = authenticated[SOURCE].decode()
    memset_source = authenticated[MEMSET_WRAPPER_SOURCE].decode()
    hfadj_source = authenticated[HFADJ_SOURCE].decode()
    hfadj_config_source = authenticated[HFADJ_CONFIG_SOURCE].decode()
    hfadj_disable_source = authenticated[HFADJ_DISABLE_SOURCE].decode()
    dual_switch_source = authenticated[DUAL_SWITCH_SOURCE].decode()
    clkgen_config_source = authenticated[CLKGEN_CONFIG_SOURCE].decode()
    clkgen_disable_source = authenticated[CLKGEN_DISABLE_SOURCE].decode()
    float_gcd_source = authenticated[FLOAT_GCD_SOURCE].decode()
    float_ratio_source = authenticated[FLOAT_RATIO_SOURCE].decode()
    float_multiplier_source = authenticated[FLOAT_MULTIPLIER_SOURCE].decode()
    float_select_source = authenticated[FLOAT_SELECT_SOURCE].decode()
    syspll_min_fvco_source = authenticated[SYSPLL_MIN_FVCO_SOURCE].decode()
    syspll_postdiv_source = authenticated[SYSPLL_POSTDIV_SOURCE].decode()
    syspll_initialize_source = authenticated[SYSPLL_INITIALIZE_SOURCE].decode()
    syspll_deinitialize_source = authenticated[SYSPLL_DEINITIALIZE_SOURCE].decode()
    syspll_enable_source = authenticated[SYSPLL_ENABLE_SOURCE].decode()
    syspll_disable_source = authenticated[SYSPLL_DISABLE_SOURCE].decode()
    syspll_configure_source = authenticated[SYSPLL_CONFIGURE_SOURCE].decode()
    syspll_lock_wait_source = authenticated[SYSPLL_LOCK_WAIT_SOURCE].decode()
    queue_source = authenticated[QUEUE_SOURCE].decode()
    memmove_source = authenticated[MEMMOVE_SOURCE].decode()
    cmdq_update_source = authenticated[CMDQ_UPDATE_SOURCE].decode()
    cmdq_services_source = authenticated[CMDQ_SERVICES_SOURCE].decode()
    float_math_source = authenticated[FLOAT_MATH_SOURCE].decode()
    float_math_veneers_source = authenticated[FLOAT_MATH_VENEERS_SOURCE].decode()
    spotmgr_transition_source = authenticated[SPOTMGR_TRANSITION_SOURCE].decode()
    spotmgr_transition_7b_source = authenticated[SPOTMGR_TRANSITION_7B_SOURCE].decode()
    spotmgr_factory_trims_source = authenticated[SPOTMGR_FACTORY_TRIMS_SOURCE].decode()
    spotmgr_factory_ensure_source = authenticated[SPOTMGR_FACTORY_ENSURE_SOURCE].decode()
    spotmgr_timer_irq_source = authenticated[SPOTMGR_TIMER_IRQ_SOURCE].decode()
    spotmgr_buck_deepsleep_source = authenticated[SPOTMGR_BUCK_DEEPSLEEP_SOURCE].decode()
    spotmgr_internal_domain_source = authenticated[SPOTMGR_INTERNAL_DOMAIN_SOURCE].decode()
    spotmgr_power_ton_source = authenticated[SPOTMGR_POWER_TON_SOURCE].decode()
    spotmgr_state_sequence_source = authenticated[SPOTMGR_STATE_SEQUENCE_SOURCE].decode()
    spotmgr_temperature_transition_source = authenticated[SPOTMGR_TEMPERATURE_TRANSITION_SOURCE].decode()
    spotmgr_power_trims_source = authenticated[SPOTMGR_POWER_TRIMS_SOURCE].decode()
    spotmgr_power_state_source = authenticated[SPOTMGR_POWER_STATE_SOURCE].decode()
    spotmgr_update_source = authenticated[SPOTMGR_UPDATE_SOURCE].decode()
    spotmgr_profile_source = authenticated[SPOTMGR_PROFILE_SOURCE].decode()
    spotmgr_init_source = authenticated[SPOTMGR_INIT_SOURCE].decode()
    spotmgr_temperature_init_source = authenticated[SPOTMGR_TEMPERATURE_INIT_SOURCE].decode()
    spotmgr_temperature_range_source = authenticated[SPOTMGR_TEMPERATURE_RANGE_SOURCE].decode()
    spotmgr_trim_helpers_source = authenticated[SPOTMGR_TRIM_HELPERS_SOURCE].decode()
    spotmgr_trim_commit_source = authenticated[SPOTMGR_TRIM_COMMIT_SOURCE].decode()
    spotmgr_buck_scan_source = authenticated[SPOTMGR_BUCK_SCAN_SOURCE].decode()
    spotmgr_state_effects_source = authenticated[SPOTMGR_STATE_EFFECTS_SOURCE].decode()
    spotmgr_power_transition_source = authenticated[SPOTMGR_POWER_TRANSITION_SOURCE].decode()
    divider_helpers_source = authenticated[DIVIDER_HELPERS_SOURCE].decode()
    hw_clock_encode_source = authenticated[HW_CLOCK_ENCODE_SOURCE].decode()
    state_range_source = authenticated[STATE_RANGE_SOURCE].decode()
    misc_primitives_source = authenticated[MISC_PRIMITIVES_SOURCE].decode()
    register_helpers_source = authenticated[REGISTER_HELPERS_SOURCE].decode()
    hw_event_apply_source = authenticated[HW_EVENT_APPLY_SOURCE].decode()
    cmdq_adapters_source = authenticated[CMDQ_ADAPTERS_SOURCE].decode()
    hw_descriptor_source = authenticated[HW_DESCRIPTOR_SOURCE].decode()
    hw_context_claim_source = authenticated[HW_CONTEXT_CLAIM_SOURCE].decode()
    hw_context_enable_source = authenticated[HW_CONTEXT_ENABLE_SOURCE].decode()
    hw_event_service_source = authenticated[HW_EVENT_SERVICE_SOURCE].decode()
    hw_config_transaction_source = authenticated[HW_CONFIG_TRANSACTION_SOURCE].decode()
    hw_instance_configure_source = authenticated[HW_INSTANCE_CONFIGURE_SOURCE].decode()
    hw_config_retry_source = authenticated[HW_CONFIG_RETRY_SOURCE].decode()
    hw_profile_apply_source = authenticated[HW_PROFILE_APPLY_SOURCE].decode()
    control_wrappers_source = authenticated[CONTROL_WRAPPERS_SOURCE].decode()
    context_lifecycle_source = authenticated[CONTEXT_LIFECYCLE_SOURCE].decode()
    event_control_wrappers_source = authenticated[EVENT_CONTROL_WRAPPERS_SOURCE].decode()
    event_setup_source = authenticated[EVENT_SETUP_SOURCE].decode()
    event_state_source = authenticated[EVENT_STATE_SOURCE].decode()
    small_services_source = authenticated[SMALL_SERVICES_SOURCE].decode()
    control_services_source = authenticated[CONTROL_SERVICES_SOURCE].decode()
    event_service_loop_source = authenticated[EVENT_SERVICE_LOOP_SOURCE].decode()
    event_runtime_services_source = authenticated[EVENT_RUNTIME_SERVICES_SOURCE].decode()
    control_orchestration_source = authenticated[CONTROL_ORCHESTRATION_SOURCE].decode()
    context_publish_source = authenticated[CONTEXT_PUBLISH_SOURCE].decode()
    late_wrappers_source = authenticated[LATE_WRAPPERS_SOURCE].decode()
    noop_callbacks_source = authenticated[NOOP_CALLBACKS_SOURCE].decode()
    startup_services_source = authenticated[STARTUP_SERVICES_SOURCE].decode()
    startup_runtime_source = authenticated[STARTUP_RUNTIME_SOURCE].decode()
    alignment_dispatch_source = authenticated[ALIGNMENT_DISPATCH_SOURCE].decode()
    guarded_call_source = authenticated[GUARDED_CALL_SOURCE].decode()
    event_dispatch_source = authenticated[EVENT_DISPATCH_SOURCE].decode()
    hw_handle_source = authenticated[HW_HANDLE_SOURCE].decode()
    hw_command_source = authenticated[HW_COMMAND_SOURCE].decode()
    clkmgr_divider_source = authenticated[CLKMGR_DIVIDER_SOURCE].decode()
    hw_channel_source = authenticated[HW_CHANNEL_SOURCE].decode()
    hw_activate_source = authenticated[HW_ACTIVATE_SOURCE].decode()
    hw_config_enumerate_source = authenticated[HW_CONFIG_ENUMERATE_SOURCE].decode()
    orphan_services_source = authenticated[ORPHAN_SERVICES_SOURCE].decode()
    queue_header = authenticated[AMBIQ_QUEUE_HEADER].decode()
    cmdq_header = authenticated[AMBIQ_CMDQ_HEADER].decode()
    require("BSD 3-Clause License" in authenticated[AMBIQ_LICENSE].decode(), "Ambiq license changed")
    provenance = json.loads(authenticated[AMBIQ_PROVENANCE])
    require(provenance["upstream"]["selected_commit"] ==
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "Ambiq upstream commit changed")
    require(all(token not in mnemonic_source for token in (".byte", ".short", ".word")),
            "executable raw-encoding directive reintroduced")
    require(all(token not in cmdq_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "command-queue services reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_cmdq_init_427794",
        "open_cfw_bootloader_cmdq_alloc_block_42790a",
        "open_cfw_bootloader_cmdq_get_status_427a56",
        "open_cfw_bootloader_cmdq_error_resume_427b38",
        "open_cfw_bootloader_cmdq_post_loop_block_427c12",
        "OPEN_CFW_CMDQ_SSRAM_BASE",
        "open_cfw_bootloader_cmdq_update_indices_427754(queue)",
    ):
        require(token in cmdq_services_source,
                f"command-queue service source token missing: {token}")
    require(all(token not in float_math_source + float_math_veneers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "binary32 math source reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_floor_bits_427ca0",
        "open_cfw_bootloader_fmod_bits_427cdc",
        "__builtin_clz",
        "open_cfw_bootloader_float_range_classify_427e0c",
        "0x4FFEE92DU",
    ):
        require(token in float_math_source,
                f"binary32 math core source token missing: {token}")
    for token in (
        "open_cfw_bootloader_floorf_427c90",
        "open_cfw_bootloader_fmodf_427ccc",
        "open_cfw_bootloader_roundf_427d98",
        "open_cfw_bootloader_ceilf_427dd0",
        "pcs(\"aapcs-vfp\")",
    ):
        require(token in float_math_veneers_source,
                f"binary32 math veneer source token missing: {token}")
    require(all(token not in spotmgr_transition_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager transition reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378",
        "transition_sequence_2b", "bfi r2, r1, #10, #4",
        "bics r1, r1, #0x2000000", "last_delay_us = 5U",
        "ongoing_sequence = 26U",
    ):
        require(token in spotmgr_transition_source,
                f"SPOT-manager transition source token missing: {token}")
    require(all(token not in spotmgr_transition_7b_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager transition-7b reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94",
        "transition_sequence_7b", "index < 20U",
        "open_cfw_bootloader_delay_us_status_change_41d21c",
        "last_status_delay = 15U", "ongoing_sequence = 26U",
    ):
        require(token in spotmgr_transition_7b_source,
                f"SPOT-manager transition-7b source token missing: {token}")
    require(all(token not in spotmgr_factory_trims_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager factory-trim loader reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_load_factory_trims_429da4",
        "trim_words[state->trim_index + 1U]", "record >> 17",
        "record >> 7", "record >> 21", "state->ready = 0U",
    ):
        require(token in spotmgr_factory_trims_source,
                f"SPOT-manager factory-trim source token missing: {token}")
    require(all(token not in spotmgr_factory_ensure_source + spotmgr_timer_irq_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager wrapper/ISR reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036",
        "factory_trims_pending != 0U", "return 0U",
    ):
        require(token in spotmgr_factory_ensure_source,
                f"SPOT-manager readiness source token missing: {token}")
    for token in (
        "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a",
        "ongoing_sequence == 2U", "ongoing_sequence == 7U",
        "state->current_primask = token",
    ):
        require(token in spotmgr_timer_irq_source,
                f"SPOT-manager timer ISR source token missing: {token}")
    require(all(token not in spotmgr_buck_deepsleep_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager SIMOBUCK classifier reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c",
        "open_cfw_bootloader_stimer_is_running_41f3f0",
        "clock < 6U", "clock >= 19U", "clock < 0x1e0U",
        "state->force_buck_active = 0U",
    ):
        require(token in spotmgr_buck_deepsleep_source,
                f"SPOT-manager SIMOBUCK source token missing: {token}")
    require(all(token not in spotmgr_buck_scan_source
                for token in (".byte", ".short", ".word", ".inst")),
            "second SPOT-manager deep-sleep scan reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0",
        "open_cfw_bootloader_stimer_is_running_41f3f0",
        "clock < 6U", "clock >= 19U", "clock < 0x1e0U",
        "state->deep_sleep_blocked = 0U",
    ):
        require(token in spotmgr_buck_scan_source,
                f"second SPOT-manager deep-sleep source token missing: {token}")
    require(all(token not in spotmgr_state_effects_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager transition-effects leaf reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_state_transition_effects_42b014",
        "state->deep_sleep_entry_pending = 1U",
        "0x10000U | 0x08U | 0x40U",
        "state->hp_entry_pending = 0U",
    ):
        require(token in spotmgr_state_effects_source,
                f"SPOT-manager transition-effects source token missing: {token}")
    require(all(token not in spotmgr_power_transition_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager power-transition transaction reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_power_transition_trims_42b06c",
        "open_cfw_bootloader_delay_cycles_41d1c0",
        "core_delta = 14U", "flash_delta = 6U",
        "transition == 17U", "state->transition_control &= ~0x30000000U",
    ):
        require(token in spotmgr_power_transition_source,
                f"SPOT-manager power-transition source token missing: {token}")
    require(all(token not in divider_helpers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "rounded-divider helpers reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_rounded_divider_42c222",
        "open_cfw_bootloader_is_power_of_two_42c256",
        "numerator % denominator", "value & (value - 1U)",
    ):
        require(token in divider_helpers_source,
                f"rounded-divider helper source token missing: {token}")
    require(all(token not in hw_clock_encode_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-clock encoder reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_clock_encode_42c26a",
        "open_cfw_bootloader_hw_clock_encode_42c26a_portable",
        "open_cfw_bootloader_rounded_divider_42c222",
        "open_cfw_bootloader_is_power_of_two_42c256",
        "requested_hz<(source_hz>>14U)", "phase_select==1U",
        "actual%250000U==0U",
    ):
        require(token in hw_clock_encode_source,
                f"hardware-clock encoder source token missing: {token}")
    require(all(token not in state_range_source
                for token in (".byte", ".short", ".word", ".inst")),
            "state/range services reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_state_adjust_42cdf8",
        "open_cfw_bootloader_state_range_update_42ced8",
        "open_cfw_bootloader_state_event_dispatch_42d562",
        "value = value + reference >= 128U ? 127U",
        "state->sample >= -273.0f", "range == 2U",
    ):
        require(token in state_range_source,
                f"state/range source token missing: {token}")
    require(all(token not in misc_primitives_source
                for token in (".byte", ".short", ".word", ".inst")),
            "miscellaneous primitives reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_stream_mode_42d84c",
        "open_cfw_bootloader_runtime_context_get_42d88a",
        "open_cfw_bootloader_vector_handoff_42dc90",
        "open_cfw_bootloader_crc32_table_42e1ec",
        "open_cfw_bootloader_terminal_mode_42e514",
        "0xEDB88320U",
    ):
        require(token in misc_primitives_source,
                f"miscellaneous primitive source token missing: {token}")
    require(all(token not in register_helpers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "register helpers reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_status_route_42c034",
        "open_cfw_bootloader_hw_error_classify_42c076",
        "open_cfw_bootloader_hw_interrupt_enable_42c63a",
        "open_cfw_bootloader_hw_interrupt_status_get_42c672",
        "open_cfw_bootloader_hw_interrupt_clear_42c6b6",
        "open_cfw_bootloader_nvic_enable_bit_430240",
        "open_cfw_bootloader_scb_priority_nibble_43025c",
        "open_cfw_bootloader_nvic_enable_bit_430470",
        "OPEN_CFW_REG_HANDLE_MAGIC",
    ):
        require(token in register_helpers_source,
                f"register-helper source token missing: {token}")
    require(all(token not in hw_event_apply_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-event apply reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_event_apply_42c0b2",
        "open_cfw_bootloader_hw_event_apply_42c0b2_portable",
        "open_cfw_bootloader_delay_cycles_41d1c0",
        "events&0x800U", "events&0x210U",
        "state->register_10c=0x08000001U",
        "state->register_208=0xFFFFFFFFU",
    ):
        require(token in hw_event_apply_source,
                f"hardware-event apply source token missing: {token}")
    require(all(token not in cmdq_adapters_source
                for token in (".byte", ".short", ".word", ".inst")),
            "command-queue adapters reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_cmdq_adapter_init_42c3e2",
        "open_cfw_bootloader_cmdq_adapter_enable_42c420",
        "open_cfw_bootloader_cmdq_adapter_disable_42c44e",
        "open_cfw_bootloader_cmdq_init_427794",
        "open_cfw_bootloader_cmdq_enable_427878",
        "open_cfw_bootloader_cmdq_disable_4278c8",
        "byte_capacity>>1",
    ):
        require(token in cmdq_adapters_source,
                f"command-queue adapter source token missing: {token}")
    require(all(token not in hw_descriptor_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-descriptor publisher reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_descriptor_publish_42c45a",
        "open_cfw_bootloader_hw_descriptor_publish_42c45a_portable",
        "(producer_index+1U)%ring_size", "registers[2]=entry[4]",
    ):
        require(token in hw_descriptor_source,
                f"hardware-descriptor publisher source token missing: {token}")
    require(all(token not in hw_context_claim_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-context claim reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_context_claim_42c4c6",
        "open_cfw_bootloader_hw_context_claim_42c4c6_portable",
        "OPEN_CFW_HW_CLAIM_MAGIC", "OPEN_CFW_HW_CLAIM_STRIDE",
        "index>=8U", "output_present==0U",
    ):
        require(token in hw_context_claim_source,
                f"hardware-context claim source token missing: {token}")
    require(all(token not in hw_context_enable_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-context enable reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_context_enable_42c538",
        "open_cfw_bootloader_hw_context_enable_42c538_portable",
        "open_cfw_bootloader_hw_status_route_42c034",
        "open_cfw_bootloader_cmdq_adapter_init_42c3e2",
        "open_cfw_bootloader_retained_status_check_41d246",
        "context->register_11c&=~0x00000011U",
    ):
        require(token in hw_context_enable_source,
                f"hardware-context enable source token missing: {token}")
    require(all(token not in hw_event_service_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-event service reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_event_service_42c6f8",
        "open_cfw_bootloader_hw_event_service_42c6f8_portable",
        "open_cfw_bootloader_cmdq_get_status_427a56",
        "open_cfw_bootloader_cmdq_error_resume_427b38",
        "state->event_bits|=incoming_events",
        "state->register_200&=0xFFFFFBFEU",
    ):
        require(token in hw_event_service_source,
                f"hardware-event service source token missing: {token}")
    require(all(token not in hw_config_transaction_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-config transaction reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_config_transaction_42c988",
        "open_cfw_bootloader_hw_config_transaction_42c988_portable",
        "open_cfw_bootloader_pwrctrl_periph_enable_41bf84",
        "open_cfw_bootloader_mode_disable_route_422364",
        "state->saved_valid==0U", "state->registers[2]&=~0x11U",
    ):
        require(token in hw_config_transaction_source,
                f"hardware-config transaction source token missing: {token}")
    require(all(token not in hw_instance_configure_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-instance configurator reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_instance_configure_42cc34",
        "open_cfw_bootloader_hw_instance_configure_42cc34_portable",
        "open_cfw_bootloader_hw_clock_encode_42c26a",
        "state->control_280=flags&3U", "state->window>=257U",
        "0x773B2301U", "0x1D0E2301U", "0x0B052301U",
    ):
        require(token in hw_instance_configure_source,
                f"hardware-instance configurator source token missing: {token}")
    require(all(token not in hw_config_retry_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-config retry reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_config_retry_43048e",
        "open_cfw_bootloader_hw_config_retry_43048e_portable",
        "open_cfw_bootloader_callback_register_41d92c",
        "open_cfw_bootloader_hw_config_transaction_42c988",
        "attempt<1000U", "last_delay_us=10U",
    ):
        require(token in hw_config_retry_source,
                f"hardware-config retry source token missing: {token}")
    require(all(token not in hw_profile_apply_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-profile publisher reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_profile_apply_42ea68",
        "open_cfw_bootloader_hw_profile_apply_42ea68_portable",
        "open_cfw_bootloader_mode_enable_route_4222f0",
        "profile[0]!=2U", "state->published=value&~1U",
        "0x01AFAFAFU",
    ):
        require(token in hw_profile_apply_source,
                f"hardware-profile source token missing: {token}")
    require(all(token not in control_wrappers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "runtime control wrappers reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_runtime_context_wrapper_42dd68",
        "open_cfw_bootloader_control_one_wrapper_42dd9a",
        "open_cfw_bootloader_control_two_wrapper_42dda4",
        "open_cfw_bootloader_control_bits_dispatch_42e1c4",
        "open_cfw_bootloader_control_terminal_loop_42e1da",
        "flags&(1U<<22)", "flags&(1U<<23)", "notify(~0U)",
    ):
        require(token in control_wrappers_source,
                f"runtime control-wrapper source token missing: {token}")
    require(all(token not in context_lifecycle_source
                for token in (".byte", ".short", ".word", ".inst")),
            "runtime-context lifecycle reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_runtime_queue_context_init_42dd70",
        "open_cfw_bootloader_runtime_action_context_init_42ddae",
        "open_cfw_bootloader_runtime_action_context_deinit_42ddda",
        "open_cfw_bootloader_runtime_enable_sequence_42ddf2",
        "create(0x32U,0x28U,0U)", "action(*slot)", "set_mode(1U)",
    ):
        require(token in context_lifecycle_source,
                f"runtime-context lifecycle source token missing: {token}")
    require(all(token not in event_control_wrappers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "event-control wrappers reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_event_wait_one_wrapper_42e2ea",
        "open_cfw_bootloader_guarded_context_teardown_42e3ca",
        "open_cfw_bootloader_event_bit_set_42e444",
        "wait(handle,1U)", "*context=0U", "1U<<bit",
    ):
        require(token in event_control_wrappers_source,
                f"event-control wrapper source token missing: {token}")
    require(all(token not in event_setup_source
                for token in (".byte", ".short", ".word", ".inst")),
            "event-runtime setup wrappers reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_event_runtime_setup_42e278",
        "open_cfw_bootloader_event_callback_dispatch_42e284",
        "call(value(), 8U)", "call(value(), 0x30U)", "callback();",
    ):
        require(token in event_setup_source,
                f"event-runtime setup source token missing: {token}")
    require(all(token not in event_state_source
                for token in (".byte", ".short", ".word", ".inst")),
            "retained event-state services reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_retained_state_probe_42e224", "open_cfw_bootloader_event_flags_init_42e254", "open_cfw_bootloader_guard_context_init_42e39c", "open_cfw_bootloader_control_one_wait_42e3e0", "open_cfw_bootloader_control_two_publish_42e412", "value==0x55555555U", "wait(handle,1U,~0U)", "publish(handle,1U<<bit)"):
        require(token in event_state_source,
                f"retained event-state source token missing: {token}")
    require(all(token not in small_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "small runtime services reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_state_update_critical_42cea4", "open_cfw_bootloader_chunked_indirect_visit_42d9f0", "open_cfw_bootloader_hardware_channel_normalize_42eda0", "open_cfw_bootloader_platform_boot_sequence_4301d6", "open_cfw_bootloader_address_validate_430a60", "length-=chunk", "clock_config(4U,15U)", "address>=0x4000U&&length<limit"):
        require(token in small_services_source,
                f"small runtime service source token missing: {token}")
    require(all(token not in control_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "runtime control services reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_hardware_readiness_gate_42bf54", "open_cfw_bootloader_event_wait_mask_42e2a2", "open_cfw_bootloader_aligned_guarded_dispatch_42e4a0", "open_cfw_bootloader_register_power_toggle_42f1c8", "delay_result?4U:0U", "address&3U", "*control|=1U"):
        require(token in control_services_source,
                f"runtime control service source token missing: {token}")
    require(all(token not in event_service_loop_source
                for token in (".byte", ".short", ".word", ".inst")),
            "retained-event service loop reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_event_service_loop_42e2f8", "open_cfw_bootloader_event_service_context_42e2f8_portable", "wait_status<0x80000000U", "now-last<60000U"):
        require(token in event_service_loop_source,
                f"retained-event service-loop source token missing: {token}")
    require(all(token not in event_runtime_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "event runtime services reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_event_runtime_init_42e53c", "open_cfw_bootloader_event_callback_loop_42e644", "open_cfw_bootloader_event_callback_enqueue_42e686", "failures|=1U<<i", "receive_status==0U", "send_status!=0U?2U:0U"):
        require(token in event_runtime_services_source,
                f"event runtime-service source token missing: {token}")
    require(all(token not in control_orchestration_source
                for token in (".byte", ".short", ".word", ".inst")),
            "control orchestration reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_control_orchestrator_42dd14", "open_cfw_bootloader_critical_dispatch_transaction_42de0e", "wait_status<0x80000000U", "copy[i]=source[i]"):
        require(token in control_orchestration_source,
                f"control-orchestration source token missing: {token}")
    require(all(token not in context_publish_source
                for token in (".byte", ".short", ".word", ".inst")),
            "runtime-context publisher reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_runtime_context_publish_42dca2", "queue_ready==0U", "*event_mask|=0x00400000U"):
        require(token in context_publish_source,
                f"runtime-context publisher source token missing: {token}")
    require(all(token not in late_wrappers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "late runtime wrappers reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_mode_one_apply_42fff2",
        "open_cfw_bootloader_boolean_route_status_4303bc",
        "open_cfw_bootloader_validated_byte_copy_430a9c",
        "open_cfw_bootloader_validated_word_transfer_430ac4",
        "open_cfw_bootloader_word_transfer_critical_430b10",
        "open_cfw_bootloader_platform_services_init_43194c",
        "value==1U?1U:0U", "(byte_count+3U)>>2", "index<=5U",
    ):
        require(token in late_wrappers_source,
                f"late runtime-wrapper source token missing: {token}")
    require(all(token not in noop_callbacks_source
                for token in (".byte", ".short", ".word", ".inst")),
            "no-op callbacks reintroduced raw encoding")
    for facts in NOOP_CALLBACKS:
        require(facts["function"] in noop_callbacks_source,
                f"no-op callback source token missing: {facts['function']}")
    require(all(token not in startup_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "startup services reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_vector_table_relocate_432910",
        "open_cfw_bootloader_stack_limits_init_43291a",
        "open_cfw_bootloader_process_stack_init_43293c",
        "open_cfw_bootloader_fpu_enable_432958",
        "msr msplim", "msr psplim", "vmsr fpscr",
        "state->vector_table = 0x00410000U",
    ):
        require(token in startup_services_source,
                f"startup-service source token missing: {token}")
    require(all(token not in startup_runtime_source
                for token in (".byte", ".short", ".word", ".inst")),
            "startup runtime reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_runtime_start_43297c",
        "open_cfw_bootloader_init_array_run_43299c",
        "open_cfw_bootloader_terminal_loop_4329c4",
        "open_cfw_bootloader_platform_init_provider_41b862",
        "while (begin != end)", "while (bounded_iterations-- != 0U)",
    ):
        require(token in startup_runtime_source,
                f"startup-runtime source token missing: {token}")
    require(all(token not in alignment_dispatch_source
                for token in (".byte", ".short", ".word", ".inst")),
            "alignment dispatcher reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_alignment_dispatch_42e4f4",
        "open_cfw_bootloader_aligned_provider_42e4a0",
        "(length & 15U)", "(destination & 3U)",
        "OPEN_CFW_ALIGNMENT_ERROR",
    ):
        require(token in alignment_dispatch_source,
                f"alignment-dispatch source token missing: {token}")
    require(all(token not in guarded_call_source
                for token in (".byte", ".short", ".word", ".inst")),
            "guarded-call service reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_guarded_call_cleanup_42e8a4",
        "push {r2, r3, r4, lr}", "movs r2, #195",
        "open_cfw_guard_record(state, 28U, 0U)",
        "return result",
    ):
        require(token in guarded_call_source,
                f"guarded-call source token missing: {token}")
    require(all(token not in event_dispatch_source
                for token in (".byte", ".short", ".word", ".inst")),
            "event dispatcher reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_event_dispatch_42f38e",
        "open_cfw_bootloader_event_zero_provider_42f2fa",
        "open_cfw_bootloader_event_value_provider_42f204",
        "switch ((open_cfw_event_u8)event)", "case 1U:", "case 2U:",
    ):
        require(token in event_dispatch_source,
                f"event-dispatch source token missing: {token}")
    require(all(token not in hw_handle_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-handle services reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_handle_reset_42ea32",
        "open_cfw_bootloader_hw_handle_configure_42eb74",
        "open_cfw_bootloader_hw_handle_enable_42ebaa",
        "open_cfw_bootloader_hw_handle_disable_42ebe2",
        "OPEN_CFW_HW_HANDLE_MAGIC", "config->word4 & 0x3FFU",
        "registers->command |= 0x80000000U",
    ):
        require(token in hw_handle_source,
                f"hardware-handle source token missing: {token}")
    require(all(token not in hw_command_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware-handle command reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_handle_command_42eff4",
        "OPEN_CFW_COMMAND_HANDLE_MAGIC", "*command = 55U", "return 2U",
    ):
        require(token in hw_command_source,
                f"hardware-handle command source token missing: {token}")
    require(all(token not in clkmgr_divider_source
                for token in (".byte", ".short", ".word", ".inst")),
            "clock-manager divider source introduced raw executable encoding")
    for token in (
        "open_cfw_clkmgr_hfrc2_uq15_divider",
        "open_cfw_clkmgr_hfrc_integer_divider",
        "source_divider_exponent >= 32U",
        "requested_hz / source_hz",
    ):
        require(token in clkmgr_divider_source,
                f"clock-manager divider source token missing: {token}")
    require(all(token not in hw_channel_source + hw_activate_source
                for token in (".byte", ".short", ".word", ".inst")),
            "channel/activation services reintroduced raw executable encoding")
    for source_text, tokens, label in (
        (hw_channel_source,
         ("open_cfw_bootloader_hw_channel_config_42eaf6", "index >= 8U",
          "config->word4 < 32U", "registers->update_count += 1U"),
         "channel configuration"),
        (hw_activate_source,
         ("open_cfw_bootloader_hw_handle_activate_42ed60", "*control |= 1U",
          "handle->word0 |= 0x02000000U"), "handle activation"),
    ):
        for token in tokens:
            require(token in source_text, f"{label} source token missing: {token}")
    require(all(token not in hw_config_enumerate_source
                for token in (".byte", ".short", ".word", ".inst")),
            "hardware configuration/enumeration reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_hw_config_dispatch_42ec0c",
        "open_cfw_bootloader_hw_channel_normalize_42ee00",
        "open_cfw_bootloader_hw_channel_enumerate_42ee70",
        "config->word[1]>=0x100000U", "model->normalize_enabled==0U",
        "*count<limit",
    ):
        require(token in hw_config_enumerate_source,
                f"hardware configuration/enumeration source token missing: {token}")
    require(all(token not in orphan_services_source
                for token in (".byte", ".short", ".word", ".inst")),
            "unreferenced linked services reintroduced raw executable encoding")
    for token in (
        "open_cfw_bootloader_mode_four_wrapper_430aec",
        "open_cfw_bootloader_zero_table_431e38",
        "provider(handle, 4U, context)", "descriptor & 1U",
        "relative_base + descriptor - 1U",
    ):
        require(token in orphan_services_source,
                f"unreferenced linked-service source token missing: {token}")
    require(all(token not in spotmgr_internal_domain_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager internal-domain marker reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c",
        "prior_state == 1U", "requested_state == 2U",
        "state->hp_to_deep_sleep = 1U",
    ):
        require(token in spotmgr_internal_domain_source,
                f"SPOT-manager internal-domain source token missing: {token}")
    require(all(token not in spotmgr_power_ton_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager Ton selector reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
        "if (power_state == 8U)", "case 7U:",
        "vddc << 25", "vddf << 8",
    ):
        require(token in spotmgr_power_ton_source,
                f"SPOT-manager Ton source token missing: {token}")
    require(all(token not in spotmgr_state_sequence_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager state-sequence selector reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4",
        "open_cfw_bootloader_memcpy_aligned_4156ac",
        "open_cfw_spotmgr_transition_table[5][5]",
        "*sequence == 26U", "*sequence = 24U", "return 7U",
    ):
        require(token in spotmgr_state_sequence_source,
                f"SPOT-manager state-sequence source token missing: {token}")
    require(all(token not in spotmgr_temperature_transition_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager temperature dispatcher reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a",
        "starting_state < target_state", "starting_state > target_state",
        "status = observer(sequence", "sequence = 26U",
    ):
        require(token in spotmgr_temperature_transition_source,
                f"SPOT-manager temperature source token missing: {token}")
    require(all(token not in spotmgr_power_trims_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager power-trims router reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc",
        "target_state == current_state", "target_state >> 2",
        "middle_state", "status = sequence_hook(sequence",
    ):
        require(token in spotmgr_power_trims_source,
                f"SPOT-manager power-trims source token missing: {token}")
    require(all(token not in spotmgr_power_state_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager power-state classifier reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_power_state_determine_42a550",
        "power_descriptor = descriptor & 0x00F00FFFU",
        "ton_descriptor = descriptor & 0x000FF00FU",
        "status->device_power << 2", "collapse_profile ? 7U : 1U",
    ):
        require(token in spotmgr_power_state_source,
                f"SPOT-manager power-state source token missing: {token}")
    require(all(token not in spotmgr_update_source + spotmgr_profile_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager update/profile source reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_power_state_update_42a878",
        "open_cfw_bootloader_spotmgr_power_state_update_42a878_portable",
        "case 6U:", "open_cfw_bootloader_spotmgr_power_state_determine_42a550",
        "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc",
    ):
        require(token in spotmgr_update_source,
                f"SPOT-manager update source token missing: {token}")
    for token in (
        "open_cfw_bootloader_spotmgr_profile_apply_42ab7c",
        "state->magic == 0x1F01600DU", "state->profile_word_20 >> 7",
        "state->profile_word_68 >> 2",
    ):
        require(token in spotmgr_profile_source,
                f"SPOT-manager profile source token missing: {token}")
    require(all(token not in spotmgr_init_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager initializer reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_init_42abbc",
        "read_hook(1U, 0x25CU, 20U", "read_hook(1U, 0x270U, 5U",
        "state->words[0] = 0x1F01600DU", "init_hook(context)",
    ):
        require(token in spotmgr_init_source,
                f"SPOT-manager init source token missing: {token}")
    require(all(token not in spotmgr_temperature_init_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager temperature initializer reintroduced raw encoding")
    for token in (
        "open_cfw_bootloader_spotmgr_temperature_init_42ac54",
        "enable(29U,context)", "config(-40.0f,context)",
        "wait(2500U,0x400083E0U,context)",
    ):
        require(token in spotmgr_temperature_init_source,
                f"SPOT-manager temperature-init source token missing: {token}")
    require(all(token not in spotmgr_temperature_range_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager temperature range reintroduced raw encoding")
    for token in ("open_cfw_bootloader_spotmgr_temperature_range_42ad40",
                  "t>=-273.0f", "t<50.0f", "t<1000.0f"):
        require(token in spotmgr_temperature_range_source,
                f"SPOT-manager temperature-range source token missing: {token}")
    require(all(token not in spotmgr_trim_helpers_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager trim helpers reintroduced raw encoding")
    for token in ("open_cfw_bootloader_spotmgr_trim_enable_42adb8",
                  "open_cfw_bootloader_spotmgr_profile_trim_42ae24",
                  "open_cfw_bootloader_spotmgr_trim_restore_42ae6c",
                  "low+7U>=0x400U", "profile68>>14"):
        require(token in spotmgr_trim_helpers_source,
                f"SPOT-manager trim-helper source token missing: {token}")
    require(all(token not in spotmgr_trim_commit_source
                for token in (".byte", ".short", ".word", ".inst")),
            "SPOT-manager trim commit reintroduced raw encoding")
    for token in ("open_cfw_bootloader_spotmgr_trim_commit_42ae9c",
                  "power_state!=8U", "power_state!=12U", "*control|=0x48U"):
        require(token in spotmgr_trim_commit_source,
                f"SPOT-manager trim-commit source token missing: {token}")
    for token in (".syntax unified", ".thumb", ".cpu cortex-m55",
                  "ABI r0=pHandle", "am_hal_mspi_interrupt_service",
                  "am_hal_mspi_power_control"):
        require(token in mnemonic_source, f"mnemonic source proof token missing: {token}")
    require(all(token not in memset_source for token in (".byte", ".short", ".word", "__asm")),
            "memset wrapper reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_memset_wrapper_426c10",
                  "open_cfw_bootloader_retained_memset_41560c",
                  "return destination"):
        require(token in memset_source, f"memset wrapper source token missing: {token}")
    require(all(token not in hfadj_source for token in (".byte", ".short", ".word", "__asm")),
            "HFADJ leaf reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_clkgen_hfadj_enable_426c58",
                  "enable & 0xFFU", "0x40004044U", "value & ~1U"):
        require(token in hfadj_source, f"HFADJ source token missing: {token}")
    require(all(token not in hfadj_config_source
                for token in (".byte", ".short", ".word", "__asm")),
            "HFADJ configuration leaf reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_clkgen_hfadj_config_426c72",
                  "configuration | 1U", "0x40004020U"):
        require(token in hfadj_config_source,
                f"HFADJ configuration source token missing: {token}")
    require(all(token not in hfadj_disable_source
                for token in (".byte", ".short", ".word", "__asm")),
            "HFADJ disable leaf reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_clkgen_hfadj_disable_426c7e",
                  "value &= ~1U", "0x40004020U"):
        require(token in hfadj_disable_source,
                f"HFADJ disable source token missing: {token}")
    require(all(token not in dual_switch_source
                for token in (".byte", ".short", ".word", "__asm")),
            "dual-switch leaf reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_dual_switch_426c8c",
                  "0x40004044U", "0x40004030U", "0x01000000U",
                  "open_cfw_bootloader_retained_status_check_41d246"):
        require(token in dual_switch_source,
                f"dual-switch source token missing: {token}")
    require(all(token not in clkgen_config_source
                for token in (".byte", ".short", ".word", "__asm")),
            "CLKGEN configuration service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_clkgen_config_426ccc",
                  "0x40004020U", "0x4000404CU", "0x40004048U",
                  "clock_select : 2", "divider : 29",
                  "preserved_top_bit : 1"):
        require(token in clkgen_config_source,
                f"CLKGEN configuration source token missing: {token}")
    require(all(token not in clkgen_disable_source
                for token in (".byte", ".short", ".word", "__asm")),
            "CLKGEN disable service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_clkgen_disable_426d1e",
                  "0x40004050U", "value >>= 1", "value <<= 1"):
        require(token in clkgen_disable_source,
                f"CLKGEN disable source token missing: {token}")
    require(all(token not in float_gcd_source
                for token in (".byte", ".short", ".word", "__asm")),
            "floating common-divisor helper reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_float_gcd_426d48",
                  "open_cfw_bootloader_floorf_427c90",
                  "OPEN_CFW_AAPCS_VFP",
                  "0x1p-23f", "iteration >= 16U",
                  "large - quotient * small"):
        require(token in float_gcd_source,
                f"floating common-divisor source token missing: {token}")
    require(all(token not in float_ratio_source
                for token in (".byte", ".short", ".word", "__asm")),
            "floating ratio helper reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_float_ratio_426db4",
                  "open_cfw_bootloader_float_gcd_426d48(second, first)",
                  "OPEN_CFW_AAPCS_VFP",
                  "open_cfw_bootloader_fmodf_427ccc",
                  "open_cfw_bootloader_roundf_427d98",
                  "0x1.000002p-23f", "0x1.e00002p+9f",
                  "0x1.f80002p+5f", "second_count < 4U",
                  "second_count > 960U"):
        require(token in float_ratio_source,
                f"floating ratio source token missing: {token}")
    require(all(token not in float_multiplier_source
                for token in (".byte", ".short", ".word", "__asm")),
            "floating multiplier helper reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_float_multiplier_426eac",
                  "OPEN_CFW_AAPCS_VFP",
                  "open_cfw_bootloader_ceilf_427dd0",
                  "open_cfw_bootloader_fmodf_427ccc",
                  "open_cfw_bootloader_roundf_427d98",
                  "open_cfw_bootloader_floorf_427c90",
                  "0x1.f80002p+5f", "0x1p+24f",
                  "0x1.800002p+6f"):
        require(token in float_multiplier_source,
                f"floating multiplier source token missing: {token}")
    require(all(token not in float_select_source
                for token in (".byte", ".short", ".word", "__asm")),
            "floating encoding selector reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_float_encoding_select_426f6c",
                  "OPEN_CFW_AAPCS_VFP",
                  "open_cfw_bootloader_float_ratio_426db4",
                  "open_cfw_bootloader_float_multiplier_426eac",
                  "60.0f", "0x1.e00002p+9f", "240.0f",
                  "output->ratio_encoding", "output->fraction"):
        require(token in float_select_source,
                f"floating encoding-selector source token missing: {token}")
    require(all(token not in syspll_min_fvco_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL minimum-VCO service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_syspll_min_fvco_427040",
                  "open_cfw_bootloader_float_gcd_426d48",
                  "open_cfw_bootloader_float_encoding_select_426f6c",
                  "0x00431e70U", "10000000U", "1000000U",
                  "divider > 49U", "output->post_divider_1"):
        require(token in syspll_min_fvco_source,
                f"System PLL minimum-VCO source token missing: {token}")
    require(all(token not in syspll_postdiv_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL postdivider service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_syspll_postdiv_427160",
                  "open_cfw_bootloader_syspll_min_fvco_427040",
                  "0x00433cb8U", "0x00433cc8U", "60000000U",
                  "240000000U", "high_points > low_points",
                  "output->feedback_divider_fraction"):
        require(token in syspll_postdiv_source,
                f"System PLL postdivider source token missing: {token}")
    require(all(token not in syspll_initialize_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL initialization service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_create_4272ac",
                  "open_cfw_bootloader_pwrctrl_syspll_enable_41ca5c",
                  "0x20027010U", "0x01000000U", "0x00504c30U",
                  "prefix & 0xff000000U", "*output_handle = state"):
        require(token in syspll_initialize_source,
                f"System PLL initialization source token missing: {token}")
    require(all(token not in syspll_deinitialize_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL deinitialization service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_destroy_427310",
                  "open_cfw_bootloader_row6_stop_4273dc",
                  "open_cfw_bootloader_pwrctrl_syspll_enabled_41cae8",
                  "open_cfw_bootloader_pwrctrl_syspll_disable_41caa2",
                  "0x01ffffffU", "0x01504c30U", "0x01000000U",
                  "0x02000000U", "state->prefix &="):
        require(token in syspll_deinitialize_source,
                f"System PLL deinitialization source token missing: {token}")
    require(all(token not in syspll_enable_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL enable service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_start_427360",
                  "0x01ffffffU", "0x01504c30U", "0x02000000U",
                  "0x40020060U", "0x400204d8U", "1U << 29",
                  "OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ()"):
        require(token in syspll_enable_source,
                f"System PLL enable source token missing: {token}")
    require(all(token not in syspll_disable_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL disable service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_stop_4273dc",
                  "0x01ffffffU", "0x01504c30U", "0x02000000U",
                  "0x400204d8U", "1U << 29",
                  "OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_READ()"):
        require(token in syspll_disable_source,
                f"System PLL disable source token missing: {token}")
    require(all(token not in syspll_configure_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL configuration service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_configure_42740c",
                  "0x01ffffffU", "0x01504c30U", "0x02000000U",
                  "feedback < 4U", "feedback > 960U",
                  "feedback < 10U", "feedback > 96U",
                  "config->post_divider_2 > config->post_divider_1",
                  "0x400204d8U", "0x400204dcU", "0x400204e0U",
                  "open_cfw_bootloader_sysctrl_pll_fref_update_41ac92"):
        require(token in syspll_configure_source,
                f"System PLL configuration source token missing: {token}")
    require(all(token not in syspll_lock_wait_source
                for token in (".byte", ".short", ".word", "__asm")),
            "System PLL lock-wait service reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_row6_lock_wait_427522",
                  "0x01ffffffU", "0x01504c30U", "0x400204d8U",
                  "0x400204e0U", "0x400204e4U", "1000U", "1875U",
                  "OPEN_CFW_SYSPLL_LOCK_WAIT_CLOCK_SOURCE_MIN_MHZ - 1U",
                  "open_cfw_bootloader_delay_us_status_check_41d246"):
        require(token in syspll_lock_wait_source,
                f"System PLL lock-wait source token missing: {token}")
    require(all(token not in queue_source
                for token in (".byte", ".short", ".word", ".inst")),
            "queue family reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_queue_init_4275ea",
                  "open_cfw_bootloader_queue_item_add_427602",
                  "open_cfw_bootloader_queue_item_get_427660",
                  "open_cfw_bootloader_critical_save_41b8ec",
                  "msr primask, %0", "queue->capacity - queue->length",
                  "queue->length >= byte_count"):
        require(token in queue_source,
                f"queue source token missing: {token}")
    for token in ("uint32_t ui32WriteIndex", "uint32_t ui32ReadIndex",
                  "uint32_t ui32Length", "uint32_t ui32Capacity",
                  "uint32_t ui32ItemSize", "uint8_t *pui8Data"):
        require(token in queue_header,
                f"authenticated queue ABI token missing: {token}")
    require(all(token not in memmove_source
                for token in (".byte", ".short", ".word", ".inst", "__asm")),
            "memmove reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_memmove_4276bc",
                  "src_address < dst_address",
                  "dst_address < src_address +",
                  "dst[byte_count] = src[byte_count]",
                  "dst[index] = src[index]", "return destination"):
        require(token in memmove_source,
                f"memmove source token missing: {token}")
    require(all(token not in cmdq_update_source
                for token in (".byte", ".short", ".word", ".inst")),
            "command-queue index updater reintroduced raw executable encoding")
    for token in ("open_cfw_bootloader_cmdq_update_indices_427754",
                  "queue->end_index & ~0xFFU",
                  "queue->end_index - queue->current_index",
                  "queue->current_index -= 0x100U",
                  "*queue->registers->queue_address",
                  "msr primask, %0"):
        require(token in cmdq_update_source,
                f"command-queue index-update source token missing: {token}")
    for token in ("lastIdxProcessed", "lastIdxPosted", "lastIdxAllocated",
                  "am_hal_cmdq_get_status"):
        require(token in cmdq_header,
                f"authenticated command-queue API token missing: {token}")
    for start, end, expected, label in FLOAT_AAPCS_VFP_WINDOWS:
        require(sha256(boot[start - BOOT_BASE:end - BOOT_BASE]) == expected,
                f"hard-float ABI evidence changed: {label}")

    overlay = json.loads(OVERLAY.read_text())
    configured = {item["function"]: item for item in overlay["in_place_leaves"]}
    configured_caves = {item["function"]: item for item in overlay["cave_leaves"]}
    profiles: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-post-mspi-audit-") as directory:
        for profile, (compiler, version_prefix) in PROFILES.items():
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(version_prefix), f"{profile} compiler changed")
            for name, facts in FUNCTIONS.items():
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=configured[name],
                    object_path=Path(directory) / f"{profile}-{name}.o",
                    toolchain_profile=profile,
                )
                extraction = leaf_report["extraction"]
                stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
                require((len(body), sha256(body), extraction["relocation_count"]) ==
                        (facts["end"] - facts["start"], facts["sha256"],
                         len(facts["provider_edges"])),
                        f"{profile} compiled body changed: {name}")
                require(body == stock, f"{profile} body is not stock-exact: {name}")
            wrapper = configured[MEMSET_WRAPPER["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=wrapper,
                object_path=Path(directory) / f"{profile}-memset-wrapper.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (18, MEMSET_WRAPPER["source_sha256"],
                     MEMSET_WRAPPER["unrelocated_sha256"], 1),
                    f"{profile} memset wrapper output changed")
            hfadj = configured[HFADJ["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=hfadj,
                object_path=Path(directory) / f"{profile}-hfadj.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (24, HFADJ["source_sha256"], HFADJ["unrelocated_sha256"], 0),
                    f"{profile} HFADJ output changed")
            hfadj_config = configured_caves[HFADJ_CONFIG["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=hfadj_config,
                object_path=Path(directory) / f"{profile}-hfadj-config.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (16, HFADJ_CONFIG["source_sha256"],
                     HFADJ_CONFIG["source_sha256"], 0),
                    f"{profile} HFADJ configuration output changed")
            hfadj_disable = configured_caves[HFADJ_DISABLE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=hfadj_disable,
                object_path=Path(directory) / f"{profile}-hfadj-disable.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (20, HFADJ_DISABLE["source_sha256"],
                     HFADJ_DISABLE["source_sha256"], 0),
                    f"{profile} HFADJ disable output changed")
            dual_switch = configured[DUAL_SWITCH["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=dual_switch,
                object_path=Path(directory) / f"{profile}-dual-switch.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (56, DUAL_SWITCH["source_sha256"],
                     DUAL_SWITCH["unrelocated_sha256"], 1),
                    f"{profile} dual-switch output changed")
            clkgen_config = configured_caves[CLKGEN_CONFIG["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=clkgen_config,
                object_path=Path(directory) / f"{profile}-clkgen-config.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (84, CLKGEN_CONFIG["source_sha256"],
                     CLKGEN_CONFIG["source_sha256"], 0),
                    f"{profile} CLKGEN configuration output changed")
            clkgen_disable = configured_caves[CLKGEN_DISABLE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=clkgen_disable,
                object_path=Path(directory) / f"{profile}-clkgen-disable.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (20, CLKGEN_DISABLE["source_sha256"],
                     CLKGEN_DISABLE["source_sha256"], 0),
                    f"{profile} CLKGEN disable output changed")
            float_gcd = configured_caves[FLOAT_GCD["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=float_gcd,
                object_path=Path(directory) / f"{profile}-float-gcd.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (92, FLOAT_GCD["source_sha256"],
                     FLOAT_GCD["unrelocated_sha256"], 1),
                    f"{profile} floating common-divisor output changed")
            float_ratio = configured_caves[FLOAT_RATIO["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=float_ratio,
                object_path=Path(directory) / f"{profile}-float-ratio.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (252, FLOAT_RATIO["source_sha256"],
                     FLOAT_RATIO["unrelocated_sha256"], 7),
                    f"{profile} floating ratio output changed")
            float_multiplier = configured_caves[FLOAT_MULTIPLIER["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=float_multiplier,
                object_path=Path(directory) / f"{profile}-float-multiplier.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (192, FLOAT_MULTIPLIER["source_sha256"],
                     FLOAT_MULTIPLIER["unrelocated_sha256"], 5),
                    f"{profile} floating multiplier output changed")
            float_select = configured_caves[FLOAT_SELECT["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=float_select,
                object_path=Path(directory) / f"{profile}-float-select.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (180, FLOAT_SELECT["source_sha256"],
                     FLOAT_SELECT["unrelocated_sha256"], 2),
                    f"{profile} floating encoding-selector output changed")
            syspll = configured_caves[SYSPLL_MIN_FVCO["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=syspll,
                object_path=Path(directory) / f"{profile}-syspll-min-fvco.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_MIN_FVCO["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 2),
                    f"{profile} System PLL minimum-VCO output changed")
            postdiv = configured_caves[SYSPLL_POSTDIV["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=postdiv,
                object_path=Path(directory) / f"{profile}-syspll-postdiv.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_POSTDIV["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 2),
                    f"{profile} System PLL postdivider output changed")
            initialize = configured_caves[SYSPLL_INITIALIZE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=initialize,
                object_path=Path(directory) / f"{profile}-syspll-initialize.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_INITIALIZE["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 1),
                    f"{profile} System PLL initialization output changed")
            deinitialize = configured[SYSPLL_DEINITIALIZE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=deinitialize,
                object_path=Path(directory) / f"{profile}-syspll-deinitialize.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_DEINITIALIZE["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 3),
                    f"{profile} System PLL deinitialization output changed")
            enable = configured_caves[SYSPLL_ENABLE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=enable,
                object_path=Path(directory) / f"{profile}-syspll-enable.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_ENABLE["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 0),
                    f"{profile} System PLL enable output changed")
            disable = configured[SYSPLL_DISABLE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=disable,
                object_path=Path(directory) / f"{profile}-syspll-disable.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_DISABLE["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 0),
                    f"{profile} System PLL disable output changed")
            configure = configured_caves[SYSPLL_CONFIGURE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=configure,
                object_path=Path(directory) / f"{profile}-syspll-configure.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_CONFIGURE["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 1),
                    f"{profile} System PLL configuration output changed")
            lock_wait = configured_caves[SYSPLL_LOCK_WAIT["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=lock_wait,
                object_path=Path(directory) / f"{profile}-syspll-lock-wait.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = SYSPLL_LOCK_WAIT["profiles"][profile]
            require((len(body), sha256(body), extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 1),
                    f"{profile} System PLL lock-wait output changed")
            for queue_name, queue_facts in QUEUE_FUNCTIONS.items():
                queue_leaf = configured_caves[queue_facts["function"]]
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=queue_leaf,
                    object_path=Path(directory) / f"{profile}-{queue_name}.o",
                    toolchain_profile=profile,
                )
                extraction = leaf_report["extraction"]
                expected = queue_facts["profiles"][profile]
                require((len(body), sha256(body),
                         extraction["unrelocated_sha256"],
                         extraction["relocation_count"]) ==
                        (expected["size"], expected["sha256"],
                         expected["unrelocated_sha256"],
                         len(queue_facts["relocations"])),
                        f"{profile} {queue_name} output changed")
            memmove_leaf = configured_caves[MEMMOVE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=memmove_leaf,
                object_path=Path(directory) / f"{profile}-memmove.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = MEMMOVE["profiles"][profile]
            require((len(body), sha256(body),
                     extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 0),
                    f"{profile} memmove output changed")
            cmdq_update_leaf = configured_caves[CMDQ_UPDATE["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=cmdq_update_leaf,
                object_path=Path(directory) / f"{profile}-cmdq-update.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            expected = CMDQ_UPDATE["profiles"][profile]
            require((len(body), sha256(body),
                     extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (expected["size"], expected["sha256"],
                     expected["unrelocated_sha256"], 1),
                    f"{profile} command-queue index-update output changed")
            for service_name, service_facts in CMDQ_SERVICES.items():
                service_leaf = configured[service_name]
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=service_leaf,
                    object_path=(Path(directory) /
                                 f"{profile}-{service_name}.o"),
                    toolchain_profile=profile,
                )
                extraction = leaf_report["extraction"]
                expected = service_facts["profiles"][profile]
                require((len(body), sha256(body),
                         extraction["unrelocated_sha256"],
                         extraction["relocation_count"]) ==
                        (expected["size"], expected["sha256"],
                         expected["unrelocated_sha256"],
                         1 if service_facts["call_offset"] is not None else 0),
                        f"{profile} {service_name} output changed")
            for math_name, math_facts in FLOAT_MATH.items():
                math_leaf = configured[math_name]
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=math_leaf,
                    object_path=(Path(directory) /
                                 f"{profile}-{math_name}.o"),
                    toolchain_profile=profile,
                )
                extraction = leaf_report["extraction"]
                require((len(body), sha256(body),
                         extraction["unrelocated_sha256"],
                         extraction["relocation_count"]) ==
                        (math_facts["size"], math_facts["sha256"],
                         math_facts["unrelocated_sha256"],
                         1 if math_facts["target"] is not None else 0),
                        f"{profile} {math_name} output changed")
            spotmgr_leaf = configured[SPOTMGR_TRANSITION["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=spotmgr_leaf,
                object_path=Path(directory) / f"{profile}-spotmgr-transition.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body),
                     extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (SPOTMGR_TRANSITION["end"] - SPOTMGR_TRANSITION["start"],
                     SPOTMGR_TRANSITION["sha256"],
                     SPOTMGR_TRANSITION["unrelocated_sha256"], 1),
                    f"{profile} SPOT-manager transition output changed")
            spotmgr_7b_leaf = configured[SPOTMGR_TRANSITION_7B["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=spotmgr_7b_leaf,
                object_path=Path(directory) / f"{profile}-spotmgr-transition-7b.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body),
                     extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (SPOTMGR_TRANSITION_7B["end"] -
                     SPOTMGR_TRANSITION_7B["start"],
                     SPOTMGR_TRANSITION_7B["sha256"],
                     SPOTMGR_TRANSITION_7B["unrelocated_sha256"], 5),
                    f"{profile} SPOT-manager transition-7b output changed")
            factory_trims_leaf = configured[SPOTMGR_FACTORY_TRIMS["function"]]
            body, leaf_report = apollo_overlay.compile_in_place_leaf(
                root=ROOT,
                clang=str(compiler),
                leaf_config=factory_trims_leaf,
                object_path=Path(directory) / f"{profile}-spotmgr-factory-trims.o",
                toolchain_profile=profile,
            )
            extraction = leaf_report["extraction"]
            require((len(body), sha256(body),
                     extraction["unrelocated_sha256"],
                     extraction["relocation_count"]) ==
                    (SPOTMGR_FACTORY_TRIMS["end"] -
                     SPOTMGR_FACTORY_TRIMS["start"],
                     SPOTMGR_FACTORY_TRIMS["sha256"],
                     SPOTMGR_FACTORY_TRIMS["sha256"], 0),
                    f"{profile} SPOT-manager factory-trim output changed")
            for suffix, facts, relocations in (
                ("factory-ensure", SPOTMGR_FACTORY_ENSURE, 1),
                ("timer-irq", SPOTMGR_TIMER_IRQ, 4),
                ("buck-deepsleep", SPOTMGR_BUCK_DEEPSLEEP, 1),
                ("internal-domain", SPOTMGR_INTERNAL_DOMAIN, 0),
                ("power-ton", SPOTMGR_POWER_TON, 0),
                ("state-sequence", SPOTMGR_STATE_SEQUENCE, 1),
                ("temperature-transition", SPOTMGR_TEMPERATURE_TRANSITION, 2),
                ("power-trims", SPOTMGR_POWER_TRIMS, 4),
                ("power-state", SPOTMGR_POWER_STATE, 0),
                ("power-update", SPOTMGR_UPDATE, 6),
                ("profile-apply", SPOTMGR_PROFILE, 0),
                ("init", SPOTMGR_INIT, 4),
                ("temperature-init", SPOTMGR_TEMPERATURE_INIT, 3),
                ("temperature-range", SPOTMGR_TEMPERATURE_RANGE, 0),
                ("trim-enable", SPOTMGR_TRIM_HELPERS[0], 0),
                ("profile-trim", SPOTMGR_TRIM_HELPERS[1], 0),
                ("trim-restore", SPOTMGR_TRIM_HELPERS[2], 0),
                ("trim-commit", SPOTMGR_TRIM_COMMIT, 4),
                ("buck-deepsleep-scan", SPOTMGR_BUCK_SCAN, 1),
                ("state-transition-effects", SPOTMGR_STATE_EFFECTS, 0),
                ("power-transition-trims", SPOTMGR_POWER_TRANSITION, 2),
                ("rounded-divider", DIVIDER_HELPERS[0], 0),
                ("is-power-of-two", DIVIDER_HELPERS[1], 0),
                ("state-adjust", STATE_RANGE_SERVICES[0], 0),
                ("state-range-update", STATE_RANGE_SERVICES[1], 3),
                ("state-event-dispatch", STATE_RANGE_SERVICES[2], 4),
                ("stream-mode", MISC_PRIMITIVES[0], 0),
                ("runtime-context", MISC_PRIMITIVES[1], 0),
                ("vector-handoff", MISC_PRIMITIVES[2], 0),
                ("crc32-table", MISC_PRIMITIVES[3], 0),
                ("terminal-mode", MISC_PRIMITIVES[4], 0),
                ("noop-42dd98", NOOP_CALLBACKS[0], 0),
                ("noop-42e276", NOOP_CALLBACKS[1], 0),
                ("noop-42e39a", NOOP_CALLBACKS[2], 0),
                ("startup-vector", STARTUP_SERVICES[0], 0),
                ("startup-limits", STARTUP_SERVICES[1], 1),
                ("startup-process", STARTUP_SERVICES[2], 2),
                ("startup-fpu", STARTUP_SERVICES[3], 0),
                ("startup-runtime", STARTUP_RUNTIME[0], 4),
                ("startup-init-array", STARTUP_RUNTIME[1], 0),
                ("startup-terminal", STARTUP_RUNTIME[2], 1),
                ("alignment-dispatch", ALIGNMENT_DISPATCH, 1),
                ("guarded-call", GUARDED_CALL, 0),
                ("event-dispatch", EVENT_DISPATCH, 2),
                ("hw-handle-reset", HW_HANDLE_SERVICES[0], 0),
                ("hw-handle-configure", HW_HANDLE_SERVICES[1], 0),
                ("hw-handle-enable", HW_HANDLE_SERVICES[2], 0),
                ("hw-handle-disable", HW_HANDLE_SERVICES[3], 0),
                ("hw-handle-command", HW_COMMAND, 0),
                ("hw-channel-config", HW_CHANNEL_ACTIVATE[0], 0),
                ("hw-handle-activate", HW_CHANNEL_ACTIVATE[1], 0),
                ("hw-config-dispatch", HW_CONFIG_ENUMERATE[0], 0),
                ("hw-channel-normalize", HW_CONFIG_ENUMERATE[1], 0),
                ("hw-channel-enumerate", HW_CONFIG_ENUMERATE[2], 2),
                ("orphan-mode-four", ORPHAN_SERVICES[0], 1),
                ("orphan-zero-table", ORPHAN_SERVICES[1], 0),
            ):
                leaf = configured[facts["function"]]
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=leaf,
                    object_path=Path(directory) / f"{profile}-spotmgr-{suffix}.o",
                    toolchain_profile=profile,
                    allowed_defined_relocation_targets=frozenset(
                        item["symbol"] for item in leaf.get("relocations", [])
                        if isinstance(item.get("symbol"), str)
                    ),
                )
                extraction = leaf_report["extraction"]
                require((len(body), sha256(body),
                         extraction["unrelocated_sha256"],
                         extraction["relocation_count"]) ==
                        (facts["end"] - facts["start"], facts["sha256"],
                         facts["unrelocated_sha256"], relocations),
                        f"{profile} SPOT-manager {suffix} output changed")
            profiles[profile] = version

    wrapper = configured[MEMSET_WRAPPER["function"]]
    require((wrapper["runtime_address"], wrapper["expected"]["size"],
             wrapper["expected"]["sha256"],
             wrapper["expected"]["unrelocated_sha256"],
             wrapper["stock"]["sha256"], wrapper["source"]["license"]) ==
            (MEMSET_WRAPPER["start"], 18, MEMSET_WRAPPER["source_sha256"],
             MEMSET_WRAPPER["unrelocated_sha256"],
             MEMSET_WRAPPER["stock_prefix_sha256"], "MIT"),
            "memset wrapper production registration changed")
    relocation = wrapper["relocations"]
    require(len(relocation) == 1 and
            (relocation[0]["offset"], relocation[0]["type"],
             relocation[0]["symbol"], relocation[0]["symbol_type"],
             relocation[0]["target_address"]) ==
            (MEMSET_WRAPPER["relocation_offset"], "R_ARM_THM_CALL",
             "open_cfw_bootloader_retained_memset_41560c", "STT_NOTYPE",
             MEMSET_WRAPPER["provider"]),
            "memset wrapper relocation contract changed")
    stock_prefix = boot[MEMSET_WRAPPER["start"] - BOOT_BASE:
                        MEMSET_WRAPPER["source_end"] - BOOT_BASE]
    tail = boot[MEMSET_WRAPPER["source_end"] - BOOT_BASE:
                MEMSET_WRAPPER["stock_end"] - BOOT_BASE]
    require(sha256(stock_prefix) == MEMSET_WRAPPER["stock_prefix_sha256"] and
            sha256(tail) == MEMSET_WRAPPER["tail_sha256"],
            "memset wrapper stock boundary changed")
    require(direct_callers(boot, MEMSET_WRAPPER["start"]) ==
            MEMSET_WRAPPER["callers"], "memset wrapper caller topology changed")
    require(direct_callers(boot, MEMSET_WRAPPER["source_end"]) == (),
            "memset wrapper unreachable tail gained a direct caller")
    require(struct.pack("<I", MEMSET_WRAPPER["source_end"] | 1) not in boot,
            "memset wrapper unreachable tail gained a stored entry pointer")

    hfadj = configured[HFADJ["function"]]
    require((hfadj["runtime_address"], hfadj["expected"]["size"],
             hfadj["expected"]["sha256"],
             hfadj["expected"]["unrelocated_sha256"],
             hfadj["stock"]["sha256"], hfadj["source"]["license"],
             hfadj["relocations"]) ==
            (HFADJ["start"], 24, HFADJ["source_sha256"],
             HFADJ["unrelocated_sha256"], HFADJ["stock_prefix_sha256"],
             "MIT", []),
            "HFADJ production registration changed")
    hfadj_stock = boot[HFADJ["start"] - BOOT_BASE:HFADJ["source_end"] - BOOT_BASE]
    hfadj_tail = boot[HFADJ["source_end"] - BOOT_BASE:HFADJ["stock_end"] - BOOT_BASE]
    require(sha256(hfadj_stock) == HFADJ["stock_prefix_sha256"] and
            sha256(hfadj_tail) == HFADJ["tail_sha256"],
            "HFADJ stock boundary changed")
    require(boot[0x00426D30 - BOOT_BASE:0x00426D34 - BOOT_BASE] ==
            struct.pack("<I", HFADJ["register"]),
            "HFADJ stock register literal changed")
    require(direct_callers(boot, HFADJ["start"]) == HFADJ["callers"],
            "HFADJ caller topology changed")
    require(direct_callers(boot, HFADJ["source_end"]) == (),
            "HFADJ unreachable tail gained a direct caller")
    require(struct.pack("<I", HFADJ["source_end"] | 1) not in boot,
            "HFADJ unreachable tail gained a stored entry pointer")

    hfadj_config = configured_caves[HFADJ_CONFIG["function"]]
    require((hfadj_config["runtime_address"], hfadj_config["expected"]["size"],
             hfadj_config["expected"]["sha256"],
             hfadj_config["stock"]["sha256"],
             hfadj_config["source"]["license"], hfadj_config["relocations"]) ==
            (HFADJ_CONFIG["cave_start"], 16, HFADJ_CONFIG["source_sha256"],
             HFADJ_CONFIG["generated_nop_sha256"], "MIT", []),
            "HFADJ configuration cave registration changed")
    stock_config = boot[HFADJ_CONFIG["start"] - BOOT_BASE:
                        HFADJ_CONFIG["end"] - BOOT_BASE]
    require(sha256(stock_config) == HFADJ_CONFIG["stock_sha256"],
            "HFADJ configuration stock body changed")
    require(boot[0x00426D34 - BOOT_BASE:0x00426D38 - BOOT_BASE] ==
            struct.pack("<I", HFADJ_CONFIG["register"]),
            "HFADJ configuration stock register literal changed")
    require(direct_callers(boot, HFADJ_CONFIG["start"]) ==
            HFADJ_CONFIG["callers"],
            "HFADJ configuration caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(HFADJ_CONFIG["start"] + 2,
                                     HFADJ_CONFIG["end"], 2)),
            "HFADJ configuration interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(HFADJ_CONFIG["start"] + 2,
                                     HFADJ_CONFIG["end"], 2)),
            "HFADJ configuration interior gained a stored entry pointer")
    patch = next(item for item in overlay["patch_sites"]
                 if item["name"] ==
                 "replace_bootloader_clkgen_hfadj_config_426c72")
    require((patch["runtime_address"], patch["expected_size"],
             patch["expected_sha256"], patch["target_function"]) ==
            (HFADJ_CONFIG["start"], 12, HFADJ_CONFIG["stock_sha256"],
             HFADJ_CONFIG["function"]),
            "HFADJ configuration redirect contract changed")

    hfadj_disable = configured_caves[HFADJ_DISABLE["function"]]
    require((hfadj_disable["runtime_address"], hfadj_disable["expected"]["size"],
             hfadj_disable["expected"]["sha256"],
             hfadj_disable["stock"]["sha256"],
             hfadj_disable["source"]["license"], hfadj_disable["relocations"]) ==
            (HFADJ_DISABLE["cave_start"], 20, HFADJ_DISABLE["source_sha256"],
             HFADJ_DISABLE["generated_nop_sha256"], "MIT", []),
            "HFADJ disable cave registration changed")
    stock_disable = boot[HFADJ_DISABLE["start"] - BOOT_BASE:
                         HFADJ_DISABLE["end"] - BOOT_BASE]
    require(sha256(stock_disable) == HFADJ_DISABLE["stock_sha256"],
            "HFADJ disable stock body changed")
    require(boot[0x00426D34 - BOOT_BASE:0x00426D38 - BOOT_BASE] ==
            struct.pack("<I", HFADJ_DISABLE["register"]),
            "HFADJ disable stock register literal changed")
    require(direct_callers(boot, HFADJ_DISABLE["start"]) ==
            HFADJ_DISABLE["callers"],
            "HFADJ disable caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(HFADJ_DISABLE["start"] + 2,
                                     HFADJ_DISABLE["end"], 2)),
            "HFADJ disable interior gained a direct caller")
    disable_patch = next(item for item in overlay["patch_sites"]
                         if item["name"] ==
                         "replace_bootloader_clkgen_hfadj_disable_426c7e")
    require((disable_patch["runtime_address"],
             disable_patch["expected_size"],
             disable_patch["expected_sha256"],
             disable_patch["target_function"]) ==
            (HFADJ_DISABLE["start"], 14, HFADJ_DISABLE["stock_sha256"],
             HFADJ_DISABLE["function"]),
            "HFADJ disable redirect contract changed")

    dual_switch = configured[DUAL_SWITCH["function"]]
    require((dual_switch["runtime_address"], dual_switch["expected"]["size"],
             dual_switch["expected"]["sha256"],
             dual_switch["expected"]["unrelocated_sha256"],
             dual_switch["stock"]["sha256"],
             dual_switch["source"]["license"]) ==
            (DUAL_SWITCH["start"], 56, DUAL_SWITCH["source_sha256"],
             DUAL_SWITCH["unrelocated_sha256"],
             DUAL_SWITCH["stock_prefix_sha256"], "MIT"),
            "dual-switch production registration changed")
    relocation = dual_switch["relocations"]
    require(len(relocation) == 1 and
            (relocation[0]["offset"], relocation[0]["type"],
             relocation[0]["symbol"], relocation[0]["symbol_type"],
             relocation[0]["target_address"]) ==
            (DUAL_SWITCH["relocation_offset"], "R_ARM_THM_CALL",
             "open_cfw_bootloader_retained_status_check_41d246", "STT_NOTYPE",
             DUAL_SWITCH["provider"]),
            "dual-switch relocation contract changed")
    dual_stock = boot[DUAL_SWITCH["start"] - BOOT_BASE:
                      DUAL_SWITCH["source_end"] - BOOT_BASE]
    dual_tail = boot[DUAL_SWITCH["source_end"] - BOOT_BASE:
                     DUAL_SWITCH["stock_end"] - BOOT_BASE]
    require(sha256(dual_stock) == DUAL_SWITCH["stock_prefix_sha256"] and
            sha256(dual_tail) == DUAL_SWITCH["tail_sha256"],
            "dual-switch stock boundary changed")
    require(boot[0x00426D30 - BOOT_BASE:0x00426D34 - BOOT_BASE] ==
            struct.pack("<I", DUAL_SWITCH["register"]),
            "dual-switch control-register literal changed")
    require(boot[0x00426D38 - BOOT_BASE:0x00426D3C - BOOT_BASE] ==
            struct.pack("<I", DUAL_SWITCH["status_register"]),
            "dual-switch status-register literal changed")
    require(direct_callers(boot, DUAL_SWITCH["start"]) == DUAL_SWITCH["callers"],
            "dual-switch caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(DUAL_SWITCH["start"] + 2,
                                     DUAL_SWITCH["source_end"], 2)),
            "dual-switch interior gained a direct caller")
    require(direct_callers(boot, DUAL_SWITCH["source_end"]) == (),
            "dual-switch unreachable tail gained a direct caller")
    require(struct.pack("<I", DUAL_SWITCH["source_end"] | 1) not in boot,
            "dual-switch unreachable tail gained a stored entry pointer")

    clkgen_config = configured_caves[CLKGEN_CONFIG["function"]]
    require((clkgen_config["runtime_address"],
             clkgen_config["expected"]["size"],
             clkgen_config["expected"]["sha256"],
             clkgen_config["expected"]["unrelocated_sha256"],
             clkgen_config["stock"]["sha256"],
             clkgen_config["source"]["license"],
             clkgen_config["relocations"]) ==
            (CLKGEN_CONFIG["cave_start"], 84,
             CLKGEN_CONFIG["source_sha256"],
             CLKGEN_CONFIG["source_sha256"],
             CLKGEN_CONFIG["generated_nop_sha256"], "MIT", []),
            "CLKGEN configuration cave registration changed")
    clkgen_stock = boot[CLKGEN_CONFIG["start"] - BOOT_BASE:
                         CLKGEN_CONFIG["end"] - BOOT_BASE]
    require(sha256(clkgen_stock) == CLKGEN_CONFIG["stock_sha256"],
            "CLKGEN configuration stock body changed")
    for literal_address, register, label in (
        (0x00426D34, CLKGEN_CONFIG["control_register"], "control"),
        (0x00426D3C, CLKGEN_CONFIG["mode_register"], "mode"),
        (0x00426D40, CLKGEN_CONFIG["divider_register"], "divider"),
    ):
        require(boot[literal_address - BOOT_BASE:
                     literal_address - BOOT_BASE + 4] ==
                struct.pack("<I", register),
                f"CLKGEN configuration {label}-register literal changed")
    require(direct_callers(boot, CLKGEN_CONFIG["start"]) ==
            CLKGEN_CONFIG["callers"],
            "CLKGEN configuration caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(CLKGEN_CONFIG["start"] + 2,
                                     CLKGEN_CONFIG["end"], 2)),
            "CLKGEN configuration interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(CLKGEN_CONFIG["start"] + 2,
                                     CLKGEN_CONFIG["end"], 2)),
            "CLKGEN configuration interior gained a stored entry pointer")
    clkgen_patch = next(item for item in overlay["patch_sites"]
                        if item["name"] ==
                        "replace_bootloader_clkgen_config_426ccc")
    require((clkgen_patch["runtime_address"],
             clkgen_patch["expected_size"],
             clkgen_patch["expected_sha256"],
             clkgen_patch["target_function"]) ==
            (CLKGEN_CONFIG["start"], 82,
             CLKGEN_CONFIG["stock_sha256"], CLKGEN_CONFIG["function"]),
            "CLKGEN configuration redirect contract changed")

    clkgen_disable = configured_caves[CLKGEN_DISABLE["function"]]
    require((clkgen_disable["runtime_address"],
             clkgen_disable["expected"]["size"],
             clkgen_disable["expected"]["sha256"],
             clkgen_disable["expected"]["unrelocated_sha256"],
             clkgen_disable["stock"]["sha256"],
             clkgen_disable["source"]["license"],
             clkgen_disable["relocations"]) ==
            (CLKGEN_DISABLE["cave_start"], 20,
             CLKGEN_DISABLE["source_sha256"],
             CLKGEN_DISABLE["source_sha256"],
             CLKGEN_DISABLE["generated_nop_sha256"], "MIT", []),
            "CLKGEN disable cave registration changed")
    clkgen_disable_stock = boot[CLKGEN_DISABLE["start"] - BOOT_BASE:
                                CLKGEN_DISABLE["end"] - BOOT_BASE]
    require(sha256(clkgen_disable_stock) == CLKGEN_DISABLE["stock_sha256"],
            "CLKGEN disable stock body changed")
    require(boot[0x00426D44 - BOOT_BASE:0x00426D48 - BOOT_BASE] ==
            struct.pack("<I", CLKGEN_DISABLE["register"]),
            "CLKGEN disable register literal changed")
    require(direct_callers(boot, CLKGEN_DISABLE["start"]) ==
            CLKGEN_DISABLE["callers"],
            "CLKGEN disable caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(CLKGEN_DISABLE["start"] + 2,
                                     CLKGEN_DISABLE["end"], 2)),
            "CLKGEN disable interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(CLKGEN_DISABLE["start"] + 2,
                                     CLKGEN_DISABLE["end"], 2)),
            "CLKGEN disable interior gained a stored entry pointer")
    clkgen_disable_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_clkgen_disable_426d1e")
    require((clkgen_disable_patch["runtime_address"],
             clkgen_disable_patch["expected_size"],
             clkgen_disable_patch["expected_sha256"],
             clkgen_disable_patch["target_function"]) ==
            (CLKGEN_DISABLE["start"], 14,
             CLKGEN_DISABLE["stock_sha256"], CLKGEN_DISABLE["function"]),
            "CLKGEN disable redirect contract changed")

    float_gcd = configured_caves[FLOAT_GCD["function"]]
    require((float_gcd["runtime_address"],
             float_gcd["expected"]["size"],
             float_gcd["expected"]["sha256"],
             float_gcd["expected"]["unrelocated_sha256"],
             float_gcd["stock"]["sha256"],
             float_gcd["source"]["license"]) ==
            (FLOAT_GCD["cave_start"], 92,
             FLOAT_GCD["source_sha256"],
             FLOAT_GCD["unrelocated_sha256"],
             FLOAT_GCD["generated_nop_sha256"], "MIT"),
            "floating common-divisor cave registration changed")
    relocation = float_gcd["relocations"]
    require(len(relocation) == 1 and
            (relocation[0]["offset"], relocation[0]["type"],
             relocation[0]["symbol"], relocation[0]["symbol_type"],
             relocation[0]["target_address"]) ==
            (FLOAT_GCD["relocation_offset"], "R_ARM_THM_CALL",
             "open_cfw_bootloader_floorf_427c90", "STT_NOTYPE",
             FLOAT_GCD["provider"]),
            "floating common-divisor relocation contract changed")
    float_gcd_stock = boot[FLOAT_GCD["start"] - BOOT_BASE:
                           FLOAT_GCD["end"] - BOOT_BASE]
    require(sha256(float_gcd_stock) == FLOAT_GCD["stock_sha256"],
            "floating common-divisor stock body changed")
    require(decode_thumb_bl(boot,
                            FLOAT_GCD["start"] +
                            FLOAT_GCD["stock_provider_offset"]) ==
            FLOAT_GCD["provider"],
            "floating common-divisor stock floorf edge changed")
    require(direct_callers(boot, FLOAT_GCD["start"]) ==
            FLOAT_GCD["callers"],
            "floating common-divisor caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(FLOAT_GCD["start"] + 2,
                                     FLOAT_GCD["end"], 2)),
            "floating common-divisor interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(FLOAT_GCD["start"] + 2,
                                     FLOAT_GCD["end"], 2)),
            "floating common-divisor interior gained a stored entry pointer")
    main_float_gcd = main[FLOAT_GCD["main_start"] - MAIN_BASE:
                          FLOAT_GCD["main_start"] - MAIN_BASE +
                          len(float_gcd_stock)]
    require(sha256(main_float_gcd) == FLOAT_GCD["main_sha256"],
            "floating common-divisor main analogue changed")
    require(sum(left == right for left, right in
                zip(float_gcd_stock, main_float_gcd)) ==
            FLOAT_GCD["identical_bytes"],
            "floating common-divisor cross-image identity count changed")
    require(difference_runs(float_gcd_stock, main_float_gcd) ==
            FLOAT_GCD["difference_runs"],
            "floating common-divisor difference topology changed")
    float_gcd_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_float_gcd_426d48")
    require((float_gcd_patch["runtime_address"],
             float_gcd_patch["expected_size"],
             float_gcd_patch["expected_sha256"],
             float_gcd_patch["target_function"]) ==
            (FLOAT_GCD["start"], 106,
             FLOAT_GCD["stock_sha256"], FLOAT_GCD["function"]),
            "floating common-divisor redirect contract changed")

    float_ratio = configured_caves[FLOAT_RATIO["function"]]
    require((float_ratio["runtime_address"],
             float_ratio["expected"]["size"],
             float_ratio["expected"]["sha256"],
             float_ratio["expected"]["unrelocated_sha256"],
             float_ratio["stock"]["sha256"],
             float_ratio["source"]["license"]) ==
            (FLOAT_RATIO["cave_start"], 252,
             FLOAT_RATIO["source_sha256"],
             FLOAT_RATIO["unrelocated_sha256"],
             FLOAT_RATIO["generated_nop_sha256"], "MIT"),
            "floating ratio cave registration changed")
    relocation = float_ratio["relocations"]
    require(len(relocation) == len(FLOAT_RATIO["relocations"]),
            "floating ratio relocation count changed")
    require(tuple((item["offset"], item["symbol"], item["target_address"])
                  for item in relocation) == FLOAT_RATIO["relocations"],
            "floating ratio relocation targets changed")
    require(all(item["type"] == "R_ARM_THM_CALL" and
                item["symbol_type"] == "STT_NOTYPE"
                for item in relocation),
            "floating ratio relocation kinds changed")
    float_ratio_stock = boot[FLOAT_RATIO["start"] - BOOT_BASE:
                             FLOAT_RATIO["end"] - BOOT_BASE]
    require(sha256(float_ratio_stock) == FLOAT_RATIO["stock_sha256"],
            "floating ratio stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, FLOAT_RATIO["start"] + offset))
                  for offset, _target in FLOAT_RATIO["stock_provider_edges"]) ==
            FLOAT_RATIO["stock_provider_edges"],
            "floating ratio stock provider edges changed")
    require(direct_callers(boot, FLOAT_RATIO["start"]) ==
            FLOAT_RATIO["callers"],
            "floating ratio caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(FLOAT_RATIO["start"] + 2,
                                     FLOAT_RATIO["end"], 2)),
            "floating ratio interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(FLOAT_RATIO["start"] + 2,
                                     FLOAT_RATIO["end"], 2)),
            "floating ratio interior gained a stored entry pointer")
    main_float_ratio = main[FLOAT_RATIO["main_start"] - MAIN_BASE:
                            FLOAT_RATIO["main_start"] - MAIN_BASE +
                            len(float_ratio_stock)]
    require(sha256(main_float_ratio) == FLOAT_RATIO["main_sha256"],
            "floating ratio main analogue changed")
    require(sum(left == right for left, right in
                zip(float_ratio_stock, main_float_ratio)) ==
            FLOAT_RATIO["identical_bytes"],
            "floating ratio cross-image identity count changed")
    require(difference_runs(float_ratio_stock, main_float_ratio) ==
            FLOAT_RATIO["difference_runs"],
            "floating ratio difference topology changed")
    float_ratio_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_float_ratio_426db4")
    require((float_ratio_patch["runtime_address"],
             float_ratio_patch["expected_size"],
             float_ratio_patch["expected_sha256"],
             float_ratio_patch["target_function"]) ==
            (FLOAT_RATIO["start"], 248,
             FLOAT_RATIO["stock_sha256"], FLOAT_RATIO["function"]),
            "floating ratio redirect contract changed")

    float_multiplier = configured_caves[FLOAT_MULTIPLIER["function"]]
    require((float_multiplier["runtime_address"],
             float_multiplier["expected"]["size"],
             float_multiplier["expected"]["sha256"],
             float_multiplier["expected"]["unrelocated_sha256"],
             float_multiplier["stock"]["sha256"],
             float_multiplier["source"]["license"]) ==
            (FLOAT_MULTIPLIER["cave_start"], 192,
             FLOAT_MULTIPLIER["source_sha256"],
             FLOAT_MULTIPLIER["unrelocated_sha256"],
             FLOAT_MULTIPLIER["generated_nop_sha256"], "MIT"),
            "floating multiplier cave registration changed")
    relocation = float_multiplier["relocations"]
    require(len(relocation) == len(FLOAT_MULTIPLIER["relocations"]),
            "floating multiplier relocation count changed")
    require(tuple((item["offset"], item["symbol"], item["target_address"])
                  for item in relocation) == FLOAT_MULTIPLIER["relocations"],
            "floating multiplier relocation targets changed")
    require(all(item["type"] == "R_ARM_THM_CALL" and
                item["symbol_type"] == "STT_NOTYPE"
                for item in relocation),
            "floating multiplier relocation kinds changed")
    float_multiplier_stock = boot[
        FLOAT_MULTIPLIER["start"] - BOOT_BASE:
        FLOAT_MULTIPLIER["end"] - BOOT_BASE]
    require(sha256(float_multiplier_stock) ==
            FLOAT_MULTIPLIER["stock_sha256"],
            "floating multiplier stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, FLOAT_MULTIPLIER["start"] + offset))
                  for offset, _target in
                  FLOAT_MULTIPLIER["stock_provider_edges"]) ==
            FLOAT_MULTIPLIER["stock_provider_edges"],
            "floating multiplier stock provider edges changed")
    require(direct_callers(boot, FLOAT_MULTIPLIER["start"]) ==
            FLOAT_MULTIPLIER["callers"],
            "floating multiplier caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(FLOAT_MULTIPLIER["start"] + 2,
                                     FLOAT_MULTIPLIER["end"], 2)),
            "floating multiplier interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(FLOAT_MULTIPLIER["start"] + 2,
                                     FLOAT_MULTIPLIER["end"], 2)),
            "floating multiplier interior gained a stored entry pointer")
    main_float_multiplier = main[
        FLOAT_MULTIPLIER["main_start"] - MAIN_BASE:
        FLOAT_MULTIPLIER["main_start"] - MAIN_BASE +
        len(float_multiplier_stock)]
    require(sha256(main_float_multiplier) == FLOAT_MULTIPLIER["main_sha256"],
            "floating multiplier main analogue changed")
    require(sum(left == right for left, right in
                zip(float_multiplier_stock, main_float_multiplier)) ==
            FLOAT_MULTIPLIER["identical_bytes"],
            "floating multiplier cross-image identity count changed")
    require(difference_runs(float_multiplier_stock, main_float_multiplier) ==
            FLOAT_MULTIPLIER["difference_runs"],
            "floating multiplier difference topology changed")
    float_multiplier_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_float_multiplier_426eac")
    require((float_multiplier_patch["runtime_address"],
             float_multiplier_patch["expected_size"],
             float_multiplier_patch["expected_sha256"],
             float_multiplier_patch["target_function"]) ==
            (FLOAT_MULTIPLIER["start"], 190,
             FLOAT_MULTIPLIER["stock_sha256"],
             FLOAT_MULTIPLIER["function"]),
            "floating multiplier redirect contract changed")

    float_select = configured_caves[FLOAT_SELECT["function"]]
    require((float_select["runtime_address"],
             float_select["expected"]["size"],
             float_select["expected"]["sha256"],
             float_select["expected"]["unrelocated_sha256"],
             float_select["stock"]["sha256"],
             float_select["source"]["license"]) ==
            (FLOAT_SELECT["cave_start"], 180,
             FLOAT_SELECT["source_sha256"],
             FLOAT_SELECT["unrelocated_sha256"],
             FLOAT_SELECT["generated_nop_sha256"], "MIT"),
            "floating encoding-selector cave registration changed")
    relocation = float_select["relocations"]
    require(tuple((item["offset"], item["symbol"], item["target_address"])
                  for item in relocation) == FLOAT_SELECT["relocations"],
            "floating encoding-selector relocation targets changed")
    require(all(item["type"] == "R_ARM_THM_CALL" and
                item["symbol_type"] == "STT_NOTYPE"
                for item in relocation),
            "floating encoding-selector relocation kinds changed")
    float_select_stock = boot[
        FLOAT_SELECT["start"] - BOOT_BASE:FLOAT_SELECT["end"] - BOOT_BASE]
    require(sha256(float_select_stock) == FLOAT_SELECT["stock_sha256"],
            "floating encoding-selector stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, FLOAT_SELECT["start"] + offset))
                  for offset, _target in FLOAT_SELECT["stock_provider_edges"]) ==
            FLOAT_SELECT["stock_provider_edges"],
            "floating encoding-selector stock provider edges changed")
    require(direct_callers(boot, FLOAT_SELECT["start"]) ==
            FLOAT_SELECT["callers"],
            "floating encoding-selector caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(FLOAT_SELECT["start"] + 2,
                                     FLOAT_SELECT["end"], 2)),
            "floating encoding-selector interior gained a direct caller")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(FLOAT_SELECT["start"] + 2,
                                     FLOAT_SELECT["end"], 2)),
            "floating encoding-selector interior gained a stored entry pointer")
    for address, value in (
        FLOAT_SELECT["lower_literal"], FLOAT_SELECT["upper_literal"],
        FLOAT_SELECT["high_rate_literal"],
    ):
        require(boot[address - BOOT_BASE:address - BOOT_BASE + 4] ==
                struct.pack("<I", value),
                "floating encoding-selector literal changed")
    main_float_select = main[
        FLOAT_SELECT["main_start"] - MAIN_BASE:
        FLOAT_SELECT["main_start"] - MAIN_BASE + len(float_select_stock)]
    require(sha256(main_float_select) == FLOAT_SELECT["main_sha256"],
            "floating encoding-selector main analogue changed")
    require(sum(left == right for left, right in
                zip(float_select_stock, main_float_select)) ==
            FLOAT_SELECT["identical_bytes"],
            "floating encoding-selector cross-image identity count changed")
    require(difference_runs(float_select_stock, main_float_select) ==
            FLOAT_SELECT["difference_runs"],
            "floating encoding-selector difference topology changed")
    float_select_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_float_encoding_select_426f6c")
    require((float_select_patch["runtime_address"],
             float_select_patch["expected_size"],
             float_select_patch["expected_sha256"],
             float_select_patch["target_function"]) ==
            (FLOAT_SELECT["start"], 198, FLOAT_SELECT["stock_sha256"],
             FLOAT_SELECT["function"]),
            "floating encoding-selector redirect contract changed")

    syspll = configured_caves[SYSPLL_MIN_FVCO["function"]]
    require((syspll["runtime_address"], syspll["expected"]["size"],
             syspll["expected"]["sha256"],
             syspll["expected"]["unrelocated_sha256"],
             syspll["stock"]["sha256"], syspll["source"]["license"],
             syspll["source"]["upstream_commit"]) ==
            (SYSPLL_MIN_FVCO["cave_start"], 244,
             SYSPLL_MIN_FVCO["profiles"]["apple-clang"]["sha256"],
             SYSPLL_MIN_FVCO["profiles"]["apple-clang"]["unrelocated_sha256"],
             "ebce7d0464d5c8bf66d4df5e7cb70d277645342bedaf359b875177a5eab1aa64",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL minimum-VCO cave registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in syspll["relocations"]) ==
            SYSPLL_MIN_FVCO["profiles"]["apple-clang"]["relocations"],
            "System PLL minimum-VCO canonical relocations changed")
    linux_syspll = syspll["toolchain_profiles"]["linux-clang"]
    require((linux_syspll["expected"]["size"],
             linux_syspll["expected"]["sha256"],
             linux_syspll["expected"]["unrelocated_sha256"],
             linux_syspll["stock"]["size"], linux_syspll["stock"]["sha256"],
             tuple((item["offset"], item["target_address"])
                   for item in linux_syspll["relocations"])) ==
            (248, SYSPLL_MIN_FVCO["profiles"]["linux-clang"]["sha256"],
             SYSPLL_MIN_FVCO["profiles"]["linux-clang"]["unrelocated_sha256"],
             248, "57049ff9959ef20da010f368054b493107162e8e8f258b0bba82dd459bfecf33",
             SYSPLL_MIN_FVCO["profiles"]["linux-clang"]["relocations"]),
            "System PLL minimum-VCO Linux profile contract changed")
    syspll_stock = boot[
        SYSPLL_MIN_FVCO["start"] - BOOT_BASE:
        SYSPLL_MIN_FVCO["end"] - BOOT_BASE]
    require(sha256(syspll_stock) == SYSPLL_MIN_FVCO["stock_sha256"],
            "System PLL minimum-VCO stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_MIN_FVCO["start"] + offset))
                  for offset, _target in SYSPLL_MIN_FVCO["stock_provider_edges"]) ==
            SYSPLL_MIN_FVCO["stock_provider_edges"],
            "System PLL minimum-VCO provider topology changed")
    require(direct_callers(boot, SYSPLL_MIN_FVCO["start"]) ==
            SYSPLL_MIN_FVCO["callers"],
            "System PLL minimum-VCO caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_MIN_FVCO["start"] + 2,
                                     SYSPLL_MIN_FVCO["end"], 2)),
            "System PLL minimum-VCO interior gained a direct caller")
    table_address, table_size, table_sha256 = SYSPLL_MIN_FVCO["table"]
    require(sha256(boot[table_address - BOOT_BASE:
                        table_address - BOOT_BASE + table_size]) == table_sha256,
            "System PLL post-divider table changed")
    main_syspll = main[
        SYSPLL_MIN_FVCO["main_start"] - MAIN_BASE:
        SYSPLL_MIN_FVCO["main_start"] - MAIN_BASE + len(syspll_stock)]
    require(sha256(main_syspll) == SYSPLL_MIN_FVCO["main_sha256"],
            "System PLL minimum-VCO main analogue changed")
    require(sum(left == right for left, right in zip(syspll_stock, main_syspll)) ==
            SYSPLL_MIN_FVCO["identical_bytes"],
            "System PLL minimum-VCO cross-image identity count changed")
    require(difference_runs(syspll_stock, main_syspll) ==
            SYSPLL_MIN_FVCO["difference_runs"],
            "System PLL minimum-VCO difference topology changed")
    syspll_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_min_fvco_427040")
    require((syspll_patch["runtime_address"], syspll_patch["expected_size"],
             syspll_patch["expected_sha256"], syspll_patch["target_function"]) ==
            (SYSPLL_MIN_FVCO["start"], 268,
             SYSPLL_MIN_FVCO["stock_sha256"], SYSPLL_MIN_FVCO["function"]),
            "System PLL minimum-VCO redirect contract changed")

    postdiv = configured_caves[SYSPLL_POSTDIV["function"]]
    require((postdiv["runtime_address"], postdiv["expected"]["size"],
             postdiv["expected"]["sha256"],
             postdiv["expected"]["unrelocated_sha256"],
             postdiv["stock"]["sha256"], postdiv["source"]["license"],
             postdiv["source"]["upstream_commit"]) ==
            (SYSPLL_POSTDIV["cave_start"], 268,
             SYSPLL_POSTDIV["profiles"]["apple-clang"]["sha256"],
             SYSPLL_POSTDIV["profiles"]["apple-clang"]["unrelocated_sha256"],
             "03233c44272fa01b604132abcc16315602a5151d9f3e5db2a6074095dd035bf6",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL postdivider cave registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in postdiv["relocations"]) ==
            SYSPLL_POSTDIV["relocations"],
            "System PLL postdivider canonical relocations changed")
    linux_postdiv = postdiv["toolchain_profiles"]["linux-clang"]
    require((linux_postdiv["expected"]["size"],
             linux_postdiv["expected"]["sha256"],
             linux_postdiv["expected"]["unrelocated_sha256"]) ==
            (268, SYSPLL_POSTDIV["profiles"]["linux-clang"]["sha256"],
             SYSPLL_POSTDIV["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL postdivider Linux profile contract changed")
    postdiv_stock = boot[
        SYSPLL_POSTDIV["start"] - BOOT_BASE:
        SYSPLL_POSTDIV["end"] - BOOT_BASE]
    require(sha256(postdiv_stock) == SYSPLL_POSTDIV["stock_sha256"],
            "System PLL postdivider stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_POSTDIV["start"] + offset))
                  for offset, _target in SYSPLL_POSTDIV["stock_provider_edges"]) ==
            SYSPLL_POSTDIV["stock_provider_edges"],
            "System PLL postdivider provider topology changed")
    require(direct_callers(boot, SYSPLL_POSTDIV["start"]) ==
            SYSPLL_POSTDIV["callers"],
            "System PLL postdivider caller topology changed")
    interior_decodes = {
        address: callers
        for address in range(SYSPLL_POSTDIV["start"] + 2,
                             SYSPLL_POSTDIV["end"], 2)
        if (callers := direct_callers(boot, address))
    }
    require(interior_decodes == SYSPLL_POSTDIV["interior_halfword_false_decodes"],
            "System PLL postdivider interior halfword decode topology changed")
    for table_address, table_size, table_sha256 in SYSPLL_POSTDIV["tables"]:
        require(sha256(boot[table_address - BOOT_BASE:
                            table_address - BOOT_BASE + table_size]) ==
                table_sha256, "System PLL PTS table changed")
    main_postdiv = main[
        SYSPLL_POSTDIV["main_start"] - MAIN_BASE:
        SYSPLL_POSTDIV["main_start"] - MAIN_BASE + len(postdiv_stock)]
    require(sha256(main_postdiv) == SYSPLL_POSTDIV["main_sha256"],
            "System PLL postdivider main analogue changed")
    require(sum(left == right for left, right in
                zip(postdiv_stock, main_postdiv)) ==
            SYSPLL_POSTDIV["identical_bytes"],
            "System PLL postdivider cross-image identity count changed")
    require(difference_runs(postdiv_stock, main_postdiv) ==
            SYSPLL_POSTDIV["difference_runs"],
            "System PLL postdivider difference topology changed")
    postdiv_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_postdiv_427160")
    require((postdiv_patch["runtime_address"], postdiv_patch["expected_size"],
             postdiv_patch["expected_sha256"],
             postdiv_patch["target_function"]) ==
            (SYSPLL_POSTDIV["start"], 332,
             SYSPLL_POSTDIV["stock_sha256"], SYSPLL_POSTDIV["function"]),
            "System PLL postdivider redirect contract changed")

    initialize = configured_caves[SYSPLL_INITIALIZE["function"]]
    require((initialize["runtime_address"], initialize["expected"]["size"],
             initialize["expected"]["sha256"],
             initialize["expected"]["unrelocated_sha256"],
             initialize["stock"]["sha256"], initialize["source"]["license"],
             initialize["source"]["upstream_commit"]) ==
            (SYSPLL_INITIALIZE["cave_start"], 60,
             SYSPLL_INITIALIZE["profiles"]["apple-clang"]["sha256"],
             SYSPLL_INITIALIZE["profiles"]["apple-clang"]["unrelocated_sha256"],
             "63fd82bc7c6b56fa45121d1605db9aeac6928cdb9123b347db41b8a8e56f4de0",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL initialization cave registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in initialize["relocations"]) ==
            SYSPLL_INITIALIZE["relocations"],
            "System PLL initialization canonical relocations changed")
    linux_initialize = initialize["toolchain_profiles"]["linux-clang"]
    require((linux_initialize["expected"]["size"],
             linux_initialize["expected"]["sha256"],
             linux_initialize["expected"]["unrelocated_sha256"]) ==
            (60, SYSPLL_INITIALIZE["profiles"]["linux-clang"]["sha256"],
             SYSPLL_INITIALIZE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL initialization Linux profile contract changed")
    initialize_stock = boot[
        SYSPLL_INITIALIZE["start"] - BOOT_BASE:
        SYSPLL_INITIALIZE["end"] - BOOT_BASE]
    require(sha256(initialize_stock) == SYSPLL_INITIALIZE["stock_sha256"],
            "System PLL initialization stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_INITIALIZE["start"] + offset))
                  for offset, _target in SYSPLL_INITIALIZE["stock_provider_edges"]) ==
            SYSPLL_INITIALIZE["stock_provider_edges"],
            "System PLL initialization provider topology changed")
    require(direct_callers(boot, SYSPLL_INITIALIZE["start"]) ==
            SYSPLL_INITIALIZE["callers"],
            "System PLL initialization caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_INITIALIZE["start"] + 2,
                                     SYSPLL_INITIALIZE["end"], 2)),
            "System PLL initialization interior gained a direct caller")
    for literal_name in ("state_literal", "magic_literal"):
        address, value, digest = SYSPLL_INITIALIZE[literal_name]
        body = boot[address - BOOT_BASE:address - BOOT_BASE + 4]
        require((struct.unpack("<I", body)[0], sha256(body)) == (value, digest),
                f"System PLL initialization {literal_name} changed")
    main_initialize = main[
        SYSPLL_INITIALIZE["main_start"] - MAIN_BASE:
        SYSPLL_INITIALIZE["main_start"] - MAIN_BASE + len(initialize_stock)]
    require(sha256(main_initialize) == SYSPLL_INITIALIZE["main_sha256"],
            "System PLL initialization main analogue changed")
    require(sum(left == right for left, right in
                zip(initialize_stock, main_initialize)) ==
            SYSPLL_INITIALIZE["identical_bytes"],
            "System PLL initialization cross-image identity count changed")
    require(difference_runs(initialize_stock, main_initialize) ==
            SYSPLL_INITIALIZE["difference_runs"],
            "System PLL initialization difference topology changed")
    initialize_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_initialize_4272ac")
    require((initialize_patch["runtime_address"],
             initialize_patch["expected_size"],
             initialize_patch["expected_sha256"],
             initialize_patch["target_function"]) ==
            (SYSPLL_INITIALIZE["start"], 92,
             SYSPLL_INITIALIZE["stock_sha256"], SYSPLL_INITIALIZE["function"]),
            "System PLL initialization redirect contract changed")

    deinitialize = configured[SYSPLL_DEINITIALIZE["function"]]
    require((deinitialize["runtime_address"],
             deinitialize["expected"]["size"],
             deinitialize["expected"]["sha256"],
             deinitialize["expected"]["unrelocated_sha256"],
             deinitialize["stock"]["sha256"],
             deinitialize["source"]["license"],
             deinitialize["source"]["upstream_commit"]) ==
            (SYSPLL_DEINITIALIZE["start"], 80,
             SYSPLL_DEINITIALIZE["profiles"]["apple-clang"]["sha256"],
             SYSPLL_DEINITIALIZE["profiles"]["apple-clang"]["unrelocated_sha256"],
             SYSPLL_DEINITIALIZE["stock_sha256"], "BSD-3-Clause",
             "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL deinitialization in-place registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in deinitialize["relocations"]) ==
            SYSPLL_DEINITIALIZE["relocations"],
            "System PLL deinitialization canonical relocations changed")
    linux_deinitialize = deinitialize["toolchain_profiles"]["linux-clang"]
    require((linux_deinitialize["expected"]["size"],
             linux_deinitialize["expected"]["sha256"],
             linux_deinitialize["expected"]["unrelocated_sha256"]) ==
            (80, SYSPLL_DEINITIALIZE["profiles"]["linux-clang"]["sha256"],
             SYSPLL_DEINITIALIZE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL deinitialization Linux profile contract changed")
    deinitialize_stock = boot[
        SYSPLL_DEINITIALIZE["start"] - BOOT_BASE:
        SYSPLL_DEINITIALIZE["end"] - BOOT_BASE]
    require(sha256(deinitialize_stock) == SYSPLL_DEINITIALIZE["stock_sha256"],
            "System PLL deinitialization stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_DEINITIALIZE["start"] + offset))
                  for offset, _target in
                  SYSPLL_DEINITIALIZE["stock_provider_edges"]) ==
            SYSPLL_DEINITIALIZE["stock_provider_edges"],
            "System PLL deinitialization provider topology changed")
    require(direct_callers(boot, SYSPLL_DEINITIALIZE["start"]) ==
            SYSPLL_DEINITIALIZE["callers"],
            "System PLL deinitialization caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_DEINITIALIZE["start"] + 2,
                                     SYSPLL_DEINITIALIZE["end"], 2)),
            "System PLL deinitialization interior gained a direct caller")
    literal_address, literal_value, literal_digest = (
        SYSPLL_DEINITIALIZE["magic_literal"]
    )
    literal = boot[literal_address - BOOT_BASE:
                   literal_address - BOOT_BASE + 4]
    require((struct.unpack("<I", literal)[0], sha256(literal)) ==
            (literal_value, literal_digest),
            "System PLL deinitialization handle literal changed")
    main_deinitialize = main[
        SYSPLL_DEINITIALIZE["main_start"] - MAIN_BASE:
        SYSPLL_DEINITIALIZE["main_start"] - MAIN_BASE + len(deinitialize_stock)]
    require(sha256(main_deinitialize) == SYSPLL_DEINITIALIZE["main_sha256"],
            "System PLL deinitialization main analogue changed")
    require(sum(left == right for left, right in
                zip(deinitialize_stock, main_deinitialize)) ==
            SYSPLL_DEINITIALIZE["identical_bytes"],
            "System PLL deinitialization cross-image identity count changed")
    require(difference_runs(deinitialize_stock, main_deinitialize) ==
            SYSPLL_DEINITIALIZE["difference_runs"],
            "System PLL deinitialization difference topology changed")

    enable = configured_caves[SYSPLL_ENABLE["function"]]
    require((enable["runtime_address"], enable["expected"]["size"],
             enable["expected"]["sha256"],
             enable["expected"]["unrelocated_sha256"],
             enable["stock"]["sha256"], enable["source"]["license"],
             enable["source"]["upstream_commit"], enable["relocations"]) ==
            (SYSPLL_ENABLE["cave_start"], 84,
             SYSPLL_ENABLE["profiles"]["apple-clang"]["sha256"],
             SYSPLL_ENABLE["profiles"]["apple-clang"]["unrelocated_sha256"],
             "78680bf9577c12058eebdcfd3143188ebe75c9159a69de6bbc1f7c1e6af675a4",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b", []),
            "System PLL enable cave registration changed")
    linux_enable = enable["toolchain_profiles"]["linux-clang"]
    require((linux_enable["expected"]["size"],
             linux_enable["expected"]["sha256"],
             linux_enable["expected"]["unrelocated_sha256"]) ==
            (84, SYSPLL_ENABLE["profiles"]["linux-clang"]["sha256"],
             SYSPLL_ENABLE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL enable Linux profile contract changed")
    enable_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_enable_427360")
    require((enable_patch["runtime_address"], enable_patch["expected_size"],
             enable_patch["expected_sha256"], enable_patch["target_function"]) ==
            (SYSPLL_ENABLE["start"], 124, SYSPLL_ENABLE["stock_sha256"],
             SYSPLL_ENABLE["function"]),
            "System PLL enable redirect contract changed")
    enable_stock = boot[
        SYSPLL_ENABLE["start"] - BOOT_BASE:SYSPLL_ENABLE["end"] - BOOT_BASE]
    require(sha256(enable_stock) == SYSPLL_ENABLE["stock_sha256"],
            "System PLL enable stock body changed")
    require(direct_callers(boot, SYSPLL_ENABLE["start"]) ==
            SYSPLL_ENABLE["callers"],
            "System PLL enable caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_ENABLE["start"] + 2,
                                     SYSPLL_ENABLE["end"], 2)),
            "System PLL enable interior gained a direct caller")
    for address, value, digest in SYSPLL_ENABLE["literals"]:
        literal = boot[address - BOOT_BASE:address - BOOT_BASE + 4]
        require((struct.unpack("<I", literal)[0], sha256(literal)) ==
                (value, digest),
                "System PLL enable literal contract changed")
    main_enable = main[
        SYSPLL_ENABLE["main_start"] - MAIN_BASE:
        SYSPLL_ENABLE["main_start"] - MAIN_BASE + len(enable_stock)]
    require(sha256(main_enable) == SYSPLL_ENABLE["main_sha256"],
            "System PLL enable main analogue changed")
    require(sum(left == right for left, right in zip(enable_stock, main_enable)) ==
            SYSPLL_ENABLE["identical_bytes"],
            "System PLL enable cross-image identity count changed")
    require(difference_runs(enable_stock, main_enable) ==
            SYSPLL_ENABLE["difference_runs"],
            "System PLL enable difference topology changed")

    disable = configured[SYSPLL_DISABLE["function"]]
    require((disable["runtime_address"], disable["expected"]["size"],
             disable["expected"]["sha256"],
             disable["expected"]["unrelocated_sha256"],
             disable["stock"]["sha256"], disable["source"]["license"],
             disable["source"]["upstream_commit"], disable["relocations"]) ==
            (SYSPLL_DISABLE["start"], 48,
             SYSPLL_DISABLE["profiles"]["apple-clang"]["sha256"],
             SYSPLL_DISABLE["profiles"]["apple-clang"]["unrelocated_sha256"],
             SYSPLL_DISABLE["stock_sha256"], "BSD-3-Clause",
             "e8baebd44008dfec7197d40d53c8a62f3a36b38b", []),
            "System PLL disable in-place registration changed")
    linux_disable = disable["toolchain_profiles"]["linux-clang"]
    require((linux_disable["expected"]["size"],
             linux_disable["expected"]["sha256"],
             linux_disable["expected"]["unrelocated_sha256"]) ==
            (48, SYSPLL_DISABLE["profiles"]["linux-clang"]["sha256"],
             SYSPLL_DISABLE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL disable Linux profile contract changed")
    disable_stock = boot[
        SYSPLL_DISABLE["start"] - BOOT_BASE:SYSPLL_DISABLE["end"] - BOOT_BASE]
    require(sha256(disable_stock) == SYSPLL_DISABLE["stock_sha256"],
            "System PLL disable stock body changed")
    require(direct_callers(boot, SYSPLL_DISABLE["start"]) ==
            SYSPLL_DISABLE["callers"],
            "System PLL disable caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_DISABLE["start"] + 2,
                                     SYSPLL_DISABLE["end"], 2)),
            "System PLL disable interior gained a direct caller")
    for address, value, digest in SYSPLL_DISABLE["literals"]:
        literal = boot[address - BOOT_BASE:address - BOOT_BASE + 4]
        require((struct.unpack("<I", literal)[0], sha256(literal)) ==
                (value, digest),
                "System PLL disable literal contract changed")
    main_disable = main[
        SYSPLL_DISABLE["main_start"] - MAIN_BASE:
        SYSPLL_DISABLE["main_start"] - MAIN_BASE + len(disable_stock)]
    require(sha256(main_disable) == SYSPLL_DISABLE["main_sha256"],
            "System PLL disable main analogue changed")
    require(sum(left == right for left, right in
                zip(disable_stock, main_disable)) ==
            SYSPLL_DISABLE["identical_bytes"],
            "System PLL disable cross-image identity count changed")
    require(difference_runs(disable_stock, main_disable) ==
            SYSPLL_DISABLE["difference_runs"],
            "System PLL disable difference topology changed")

    configure = configured_caves[SYSPLL_CONFIGURE["function"]]
    require((configure["runtime_address"], configure["expected"]["size"],
             configure["expected"]["sha256"],
             configure["expected"]["unrelocated_sha256"],
             configure["stock"]["sha256"], configure["source"]["license"],
             configure["source"]["upstream_commit"]) ==
            (SYSPLL_CONFIGURE["cave_start"], 240,
             SYSPLL_CONFIGURE["profiles"]["apple-clang"]["sha256"],
             SYSPLL_CONFIGURE["profiles"]["apple-clang"]["unrelocated_sha256"],
             "5c2d381a5e07efff52e2d350e57f00d5f01b62e2b7d9747cf0d1cb75aa5befef",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL configuration cave registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in configure["relocations"]) ==
            ((192, 0x0041AC92),),
            "System PLL configuration provider relocation changed")
    linux_configure = configure["toolchain_profiles"]["linux-clang"]
    require((linux_configure["expected"]["size"],
             linux_configure["expected"]["sha256"],
             linux_configure["expected"]["unrelocated_sha256"]) ==
            (240, SYSPLL_CONFIGURE["profiles"]["linux-clang"]["sha256"],
             SYSPLL_CONFIGURE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL configuration Linux profile contract changed")
    configure_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_configure_42740c")
    require((configure_patch["runtime_address"],
             configure_patch["expected_size"],
             configure_patch["expected_sha256"],
             configure_patch["target_function"]) ==
            (SYSPLL_CONFIGURE["start"], 278,
             SYSPLL_CONFIGURE["stock_sha256"], SYSPLL_CONFIGURE["function"]),
            "System PLL configuration redirect contract changed")
    configure_stock = boot[
        SYSPLL_CONFIGURE["start"] - BOOT_BASE:
        SYSPLL_CONFIGURE["end"] - BOOT_BASE]
    require(sha256(configure_stock) == SYSPLL_CONFIGURE["stock_sha256"],
            "System PLL configuration stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_CONFIGURE["start"] + offset))
                  for offset, _target in
                  SYSPLL_CONFIGURE["stock_provider_edges"]) ==
            SYSPLL_CONFIGURE["stock_provider_edges"],
            "System PLL configuration stock provider edge changed")
    require(direct_callers(boot, SYSPLL_CONFIGURE["start"]) ==
            SYSPLL_CONFIGURE["callers"],
            "System PLL configuration caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_CONFIGURE["start"] + 2,
                                     SYSPLL_CONFIGURE["end"], 2)),
            "System PLL configuration interior gained a direct caller")
    for address, value, digest in SYSPLL_CONFIGURE["literals"]:
        literal = boot[address - BOOT_BASE:address - BOOT_BASE + 4]
        require((struct.unpack("<I", literal)[0], sha256(literal)) ==
                (value, digest),
                "System PLL configuration literal contract changed")
    main_configure = main[
        SYSPLL_CONFIGURE["main_start"] - MAIN_BASE:
        SYSPLL_CONFIGURE["main_start"] - MAIN_BASE + len(configure_stock)]
    require(sha256(main_configure) == SYSPLL_CONFIGURE["main_sha256"],
            "System PLL configuration main analogue changed")
    require(sum(left == right for left, right in
                zip(configure_stock, main_configure)) ==
            SYSPLL_CONFIGURE["identical_bytes"],
            "System PLL configuration cross-image identity count changed")
    require(difference_runs(configure_stock, main_configure) ==
            SYSPLL_CONFIGURE["difference_runs"],
            "System PLL configuration difference topology changed")

    lock_wait = configured_caves[SYSPLL_LOCK_WAIT["function"]]
    require((lock_wait["runtime_address"], lock_wait["expected"]["size"],
             lock_wait["expected"]["sha256"],
             lock_wait["expected"]["unrelocated_sha256"],
             lock_wait["stock"]["sha256"], lock_wait["source"]["license"],
             lock_wait["source"]["upstream_commit"]) ==
            (SYSPLL_LOCK_WAIT["cave_start"], 88,
             SYSPLL_LOCK_WAIT["profiles"]["apple-clang"]["sha256"],
             SYSPLL_LOCK_WAIT["profiles"]["apple-clang"]["unrelocated_sha256"],
             "81985b95ea146b40ae726cfcda67d4438bf38661716a6c752848ded2b4495686",
             "BSD-3-Clause", "e8baebd44008dfec7197d40d53c8a62f3a36b38b"),
            "System PLL lock-wait cave registration changed")
    require(tuple((item["offset"], item["target_address"])
                  for item in lock_wait["relocations"]) ==
            ((70, 0x0041D246),),
            "System PLL lock-wait provider relocation changed")
    linux_lock_wait = lock_wait["toolchain_profiles"]["linux-clang"]
    require((linux_lock_wait["expected"]["size"],
             linux_lock_wait["expected"]["sha256"],
             linux_lock_wait["expected"]["unrelocated_sha256"]) ==
            (88, SYSPLL_LOCK_WAIT["profiles"]["linux-clang"]["sha256"],
             SYSPLL_LOCK_WAIT["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "System PLL lock-wait Linux profile contract changed")
    lock_wait_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_syspll_lock_wait_427522")
    require((lock_wait_patch["runtime_address"],
             lock_wait_patch["expected_size"],
             lock_wait_patch["expected_sha256"],
             lock_wait_patch["target_function"]) ==
            (SYSPLL_LOCK_WAIT["start"], 102,
             SYSPLL_LOCK_WAIT["stock_sha256"], SYSPLL_LOCK_WAIT["function"]),
            "System PLL lock-wait redirect contract changed")
    lock_wait_stock = boot[
        SYSPLL_LOCK_WAIT["start"] - BOOT_BASE:
        SYSPLL_LOCK_WAIT["end"] - BOOT_BASE]
    require(sha256(lock_wait_stock) == SYSPLL_LOCK_WAIT["stock_sha256"],
            "System PLL lock-wait stock body changed")
    require(tuple((offset, decode_thumb_bl(
                      boot, SYSPLL_LOCK_WAIT["start"] + offset))
                  for offset, _target in
                  SYSPLL_LOCK_WAIT["stock_provider_edges"]) ==
            SYSPLL_LOCK_WAIT["stock_provider_edges"],
            "System PLL lock-wait stock provider edge changed")
    require(direct_callers(boot, SYSPLL_LOCK_WAIT["start"]) ==
            SYSPLL_LOCK_WAIT["callers"],
            "System PLL lock-wait caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SYSPLL_LOCK_WAIT["start"] + 2,
                                     SYSPLL_LOCK_WAIT["end"], 2)),
            "System PLL lock-wait interior gained a direct caller")
    for address, value, digest in SYSPLL_LOCK_WAIT["literals"]:
        literal = boot[address - BOOT_BASE:address - BOOT_BASE + 4]
        require((struct.unpack("<I", literal)[0], sha256(literal)) ==
                (value, digest),
                "System PLL lock-wait literal contract changed")
    main_lock_wait = main[
        SYSPLL_LOCK_WAIT["main_start"] - MAIN_BASE:
        SYSPLL_LOCK_WAIT["main_start"] - MAIN_BASE + len(lock_wait_stock)]
    require(sha256(main_lock_wait) == SYSPLL_LOCK_WAIT["main_sha256"],
            "System PLL lock-wait main analogue changed")
    require(sum(left == right for left, right in
                zip(lock_wait_stock, main_lock_wait)) ==
            SYSPLL_LOCK_WAIT["identical_bytes"],
            "System PLL lock-wait cross-image identity count changed")
    require(difference_runs(lock_wait_stock, main_lock_wait) ==
            SYSPLL_LOCK_WAIT["difference_runs"],
            "System PLL lock-wait difference topology changed")

    queue_results = {}
    for queue_name, facts in QUEUE_FUNCTIONS.items():
        item = configured_caves[facts["function"]]
        apple = facts["profiles"]["apple-clang"]
        require((item["runtime_address"], item["expected"]["size"],
                 item["expected"]["sha256"],
                 item["expected"]["unrelocated_sha256"],
                 item["stock"]["sha256"], item["source"]["license"],
                 item["source"]["upstream_commit"]) ==
                (facts["cave_start"], apple["size"], apple["sha256"],
                 apple["unrelocated_sha256"], facts["generated_nop_sha256"],
                 "BSD-3-Clause", provenance["upstream"]["selected_commit"]),
                f"{queue_name} cave registration changed")
        require(tuple((entry["offset"], entry["target_address"])
                      for entry in item["relocations"]) ==
                facts["relocations"],
                f"{queue_name} provider relocation changed")
        require(all(entry["type"] == "R_ARM_THM_CALL" and
                    entry["symbol_type"] == "STT_NOTYPE" and
                    entry["symbol"] ==
                    "open_cfw_bootloader_critical_save_41b8ec"
                    for entry in item["relocations"]),
                f"{queue_name} relocation kind changed")
        patch = next(entry for entry in overlay["patch_sites"]
                     if entry["name"] ==
                     f"replace_bootloader_{queue_name}_" +
                     f"{facts['start']:x}"[-6:])
        require((patch["runtime_address"], patch["expected_size"],
                 patch["expected_sha256"], patch["target_function"]) ==
                (facts["start"], facts["end"] - facts["start"],
                 facts["stock_sha256"], facts["function"]),
                f"{queue_name} redirect contract changed")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        require(sha256(stock) == facts["stock_sha256"],
                f"{queue_name} stock body changed")
        require(tuple((offset, decode_thumb_bl(boot, facts["start"] + offset))
                      for offset, _target in facts["stock_provider_edges"]) ==
                facts["stock_provider_edges"],
                f"{queue_name} stock provider edge changed")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"{queue_name} caller topology changed")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2,
                                         facts["end"], 2)),
                f"{queue_name} interior gained a direct caller")
        main_body = main[facts["main_start"] - MAIN_BASE:
                         facts["main_start"] - MAIN_BASE + len(stock)]
        require(sha256(main_body) == facts["main_sha256"],
                f"{queue_name} main analogue changed")
        require(sum(left == right for left, right in zip(stock, main_body)) ==
                facts["identical_bytes"],
                f"{queue_name} cross-image identity count changed")
        require(difference_runs(stock, main_body) == facts["difference_runs"],
                f"{queue_name} cross-image difference topology changed")
        queue_results[queue_name] = {
            "function": facts["function"],
            "start": facts["start"],
            "end_exclusive": facts["end"],
            "stock_bytes": len(stock),
            "source_cave_start": facts["cave_start"],
            "source_cave_bytes_by_profile": {
                name: profile_facts["size"]
                for name, profile_facts in facts["profiles"].items()
            },
            "direct_call_sites": list(facts["callers"]),
            "main_analogue": facts["main_start"],
            "identical_bytes": facts["identical_bytes"],
        }

    memmove_leaf = configured_caves[MEMMOVE["function"]]
    apple_memmove = MEMMOVE["profiles"]["apple-clang"]
    require((memmove_leaf["runtime_address"],
             memmove_leaf["expected"]["size"],
             memmove_leaf["expected"]["sha256"],
             memmove_leaf["expected"]["unrelocated_sha256"],
             memmove_leaf["stock"]["sha256"],
             memmove_leaf["source"]["license"],
             memmove_leaf["relocations"]) ==
            (MEMMOVE["cave_start"], apple_memmove["size"],
             apple_memmove["sha256"], apple_memmove["unrelocated_sha256"],
             MEMMOVE["generated_nop_sha256"], "MIT", []),
            "memmove cave registration changed")
    linux_memmove = memmove_leaf["toolchain_profiles"]["linux-clang"]
    require((linux_memmove["expected"]["size"],
             linux_memmove["expected"]["sha256"],
             linux_memmove["expected"]["unrelocated_sha256"]) ==
            (MEMMOVE["profiles"]["linux-clang"]["size"],
             MEMMOVE["profiles"]["linux-clang"]["sha256"],
             MEMMOVE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "memmove Linux profile contract changed")
    memmove_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_memmove_4276bc")
    require((memmove_patch["runtime_address"],
             memmove_patch["expected_size"],
             memmove_patch["expected_sha256"],
             memmove_patch["target_function"]) ==
            (MEMMOVE["start"], MEMMOVE["end"] - MEMMOVE["start"],
             MEMMOVE["stock_sha256"], MEMMOVE["function"]),
            "memmove redirect contract changed")
    memmove_stock = boot[
        MEMMOVE["start"] - BOOT_BASE:MEMMOVE["end"] - BOOT_BASE]
    require(sha256(memmove_stock) == MEMMOVE["stock_sha256"],
            "memmove stock body changed")
    require(decode_thumb_b_w(
                boot, MEMMOVE["start"] + MEMMOVE["copy_provider_offset"]) ==
            MEMMOVE["copy_provider"],
            "memmove forward-copy provider edge changed")
    require(direct_callers(boot, MEMMOVE["start"]) == MEMMOVE["callers"],
            "memmove caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(MEMMOVE["start"] + 2,
                                     MEMMOVE["end"], 2)),
            "memmove interior gained a direct caller")
    require(struct.pack("<I", MEMMOVE["start"] | 1) not in boot,
            "memmove gained a stored entry pointer")
    alignment = boot[
        MEMMOVE["end"] - BOOT_BASE:MEMMOVE["alignment_end"] - BOOT_BASE]
    require(sha256(alignment) == MEMMOVE["alignment_sha256"],
            "memmove alignment changed")
    main_memmove = main[
        MEMMOVE["main_start"] - MAIN_BASE:
        MEMMOVE["main_start"] - MAIN_BASE + len(memmove_stock)]
    require(sha256(main_memmove) == MEMMOVE["main_sha256"],
            "memmove main analogue changed")
    require(decode_thumb_b_w(
                main, MEMMOVE["main_start"] + MEMMOVE["copy_provider_offset"],
                MAIN_BASE) == MEMMOVE["main_copy_provider"],
            "memmove main forward-copy provider edge changed")
    require(sum(left == right for left, right in
                zip(memmove_stock, main_memmove)) == MEMMOVE["identical_bytes"],
            "memmove cross-image identity count changed")
    require(difference_runs(memmove_stock, main_memmove) ==
            MEMMOVE["difference_runs"],
            "memmove cross-image difference topology changed")
    memmove_result = {
        "function": MEMMOVE["function"],
        "start": MEMMOVE["start"],
        "end_exclusive": MEMMOVE["end"],
        "stock_bytes": len(memmove_stock),
        "source_cave_start": MEMMOVE["cave_start"],
        "source_cave_bytes_by_profile": {
            name: facts["size"]
            for name, facts in MEMMOVE["profiles"].items()
        },
        "direct_call_sites": list(MEMMOVE["callers"]),
        "copy_provider": MEMMOVE["copy_provider"],
        "main_analogue": MEMMOVE["main_start"],
        "identical_bytes": MEMMOVE["identical_bytes"],
        "alignment_bytes": len(alignment),
    }

    cmdq_update_leaf = configured_caves[CMDQ_UPDATE["function"]]
    apple_cmdq_update = CMDQ_UPDATE["profiles"]["apple-clang"]
    require((cmdq_update_leaf["runtime_address"],
             cmdq_update_leaf["expected"]["size"],
             cmdq_update_leaf["expected"]["sha256"],
             cmdq_update_leaf["expected"]["unrelocated_sha256"],
             cmdq_update_leaf["stock"]["sha256"],
             cmdq_update_leaf["source"]["license"],
             cmdq_update_leaf["source"]["upstream_commit"]) ==
            (CMDQ_UPDATE["cave_start"], apple_cmdq_update["size"],
             apple_cmdq_update["sha256"],
             apple_cmdq_update["unrelocated_sha256"],
             CMDQ_UPDATE["generated_nop_sha256"], "BSD-3-Clause",
             provenance["upstream"]["selected_commit"]),
            "command-queue index-update cave registration changed")
    require(tuple((item["offset"], item["type"], item["symbol"],
                   item["symbol_type"], item["target_address"])
                  for item in cmdq_update_leaf["relocations"]) ==
            ((4, "R_ARM_THM_CALL",
              "open_cfw_bootloader_critical_save_41b8ec", "STT_NOTYPE",
              CMDQ_UPDATE["critical_provider"]),),
            "command-queue index-update relocation changed")
    linux_cmdq_update = cmdq_update_leaf["toolchain_profiles"]["linux-clang"]
    require((linux_cmdq_update["expected"]["size"],
             linux_cmdq_update["expected"]["sha256"],
             linux_cmdq_update["expected"]["unrelocated_sha256"]) ==
            (CMDQ_UPDATE["profiles"]["linux-clang"]["size"],
             CMDQ_UPDATE["profiles"]["linux-clang"]["sha256"],
             CMDQ_UPDATE["profiles"]["linux-clang"]["unrelocated_sha256"]),
            "command-queue index-update Linux profile contract changed")
    cmdq_update_patch = next(
        item for item in overlay["patch_sites"]
        if item["name"] == "replace_bootloader_cmdq_update_indices_427754")
    require((cmdq_update_patch["runtime_address"],
             cmdq_update_patch["expected_size"],
             cmdq_update_patch["expected_sha256"],
             cmdq_update_patch["target_function"]) ==
            (CMDQ_UPDATE["start"], CMDQ_UPDATE["end"] - CMDQ_UPDATE["start"],
             CMDQ_UPDATE["stock_sha256"], CMDQ_UPDATE["function"]),
            "command-queue index-update redirect contract changed")
    cmdq_update_stock = boot[
        CMDQ_UPDATE["start"] - BOOT_BASE:CMDQ_UPDATE["end"] - BOOT_BASE]
    require(sha256(cmdq_update_stock) == CMDQ_UPDATE["stock_sha256"],
            "command-queue index-update stock body changed")
    require(decode_thumb_bl(
                boot,
                CMDQ_UPDATE["start"] + CMDQ_UPDATE["critical_provider_offset"]) ==
            CMDQ_UPDATE["critical_provider"],
            "command-queue index-update critical provider changed")
    require(direct_callers(boot, CMDQ_UPDATE["start"]) == CMDQ_UPDATE["callers"],
            "command-queue index-update caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(CMDQ_UPDATE["start"] + 2,
                                     CMDQ_UPDATE["end"], 2)),
            "command-queue index-update interior gained a direct caller")
    require(struct.pack("<I", CMDQ_UPDATE["start"] | 1) not in boot,
            "command-queue index-update gained a stored entry pointer")
    main_cmdq_update = main[
        CMDQ_UPDATE["main_start"] - MAIN_BASE:
        CMDQ_UPDATE["main_start"] - MAIN_BASE + len(cmdq_update_stock)]
    require(sha256(main_cmdq_update) == CMDQ_UPDATE["main_sha256"],
            "command-queue index-update main analogue changed")
    require(decode_thumb_bl(
                main,
                CMDQ_UPDATE["main_start"] +
                CMDQ_UPDATE["critical_provider_offset"], MAIN_BASE) ==
            CMDQ_UPDATE["main_critical_provider"],
            "command-queue index-update main critical provider changed")
    require(sum(left == right for left, right in
                zip(cmdq_update_stock, main_cmdq_update)) ==
            CMDQ_UPDATE["identical_bytes"],
            "command-queue index-update cross-image identity count changed")
    require(difference_runs(cmdq_update_stock, main_cmdq_update) ==
            CMDQ_UPDATE["difference_runs"],
            "command-queue index-update cross-image difference topology changed")
    cmdq_update_result = {
        "function": CMDQ_UPDATE["function"],
        "start": CMDQ_UPDATE["start"],
        "end_exclusive": CMDQ_UPDATE["end"],
        "stock_bytes": len(cmdq_update_stock),
        "source_cave_start": CMDQ_UPDATE["cave_start"],
        "source_cave_bytes_by_profile": {
            name: facts["size"]
            for name, facts in CMDQ_UPDATE["profiles"].items()
        },
        "direct_call_sites": list(CMDQ_UPDATE["callers"]),
        "critical_provider": CMDQ_UPDATE["critical_provider"],
        "main_analogue": CMDQ_UPDATE["main_start"],
        "identical_bytes": CMDQ_UPDATE["identical_bytes"],
        "upstream_source_sha256": CMDQ_UPDATE["upstream_source_sha256"],
        "upstream_source_blob": CMDQ_UPDATE["upstream_source_blob"],
    }

    cmdq_service_results = []
    for service_name, service_facts in CMDQ_SERVICES.items():
        leaf = configured[service_name]
        apple = service_facts["profiles"]["apple-clang"]
        linux = service_facts["profiles"]["linux-clang"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 leaf["source"]["upstream_commit"]) ==
                (service_facts["start"], apple["size"], apple["sha256"],
                 apple["unrelocated_sha256"], apple["stock_sha256"],
                 "BSD-3-Clause", provenance["upstream"]["selected_commit"]),
                f"{service_name} Apple registration changed")
        linux_leaf = leaf["toolchain_profiles"]["linux-clang"]
        require((linux_leaf["expected"]["size"],
                 linux_leaf["expected"]["sha256"],
                 linux_leaf["expected"]["unrelocated_sha256"],
                 linux_leaf["stock"]["sha256"]) ==
                (linux["size"], linux["sha256"],
                 linux["unrelocated_sha256"], linux["stock_sha256"]),
                f"{service_name} Linux registration changed")
        expected_relocations = () if service_facts["call_offset"] is None else (
            (service_facts["call_offset"], "R_ARM_THM_CALL",
             CMDQ_UPDATE["function"], "STT_NOTYPE", CMDQ_UPDATE["start"]),
        )
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in leaf["relocations"]) == expected_relocations,
                f"{service_name} relocation contract changed")
        stock_body = boot[
            service_facts["start"] - BOOT_BASE:
            service_facts["end"] - BOOT_BASE]
        require(sha256(stock_body) == service_facts["stock_sha256"],
                f"{service_name} stock body changed")
        main_start = CMDQ_SERVICE_MAIN_STARTS[service_name]
        main_body = main[
            main_start - MAIN_BASE:main_start - MAIN_BASE + len(stock_body)]
        require(main_body == stock_body,
                f"{service_name} exact Apollo-main analogue changed")
        require(direct_callers(boot, service_facts["start"]) ==
                CMDQ_SERVICE_CALLERS[service_name],
                f"{service_name} direct caller topology changed")
        require(all(direct_callers(boot, address) == ()
                    for address in range(service_facts["start"] + 2,
                                         service_facts["end"], 2)),
                f"{service_name} interior gained direct ingress")
        require(all(struct.pack("<I", address | 1) not in boot
                    for address in range(service_facts["start"] + 2,
                                         service_facts["end"], 2)),
                f"{service_name} interior gained a stored entry pointer")
        cmdq_service_results.append({
            "function": service_name,
            "start": service_facts["start"],
            "stock_end_exclusive": service_facts["end"],
            "source_end_exclusive": service_facts["start"] + apple["size"],
            "source_bytes_by_profile": {
                "apple-clang": apple["size"],
                "linux-clang": linux["size"],
            },
            "retained_unreachable_tail_bytes": (
                service_facts["end"] - service_facts["start"] -
                apple["size"]
            ),
            "direct_call_sites": list(CMDQ_SERVICE_CALLERS[service_name]),
            "main_analogue": main_start,
        })

    float_math_results = []
    for math_name, math_facts in FLOAT_MATH.items():
        leaf = configured[math_name]
        linux_leaf = leaf["toolchain_profiles"]["linux-clang"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"]) ==
                (math_facts["start"], math_facts["size"],
                 math_facts["sha256"], math_facts["unrelocated_sha256"],
                 math_facts["stock_prefix_sha256"], "MIT",
                 math_facts["source"]),
                f"{math_name} Apple registration changed")
        require((linux_leaf["expected"]["size"],
                 linux_leaf["expected"]["sha256"],
                 linux_leaf["expected"]["unrelocated_sha256"],
                 linux_leaf["stock"]["sha256"]) ==
                (math_facts["size"], math_facts["sha256"],
                 math_facts["unrelocated_sha256"],
                 math_facts["stock_prefix_sha256"]),
                f"{math_name} Linux registration changed")
        expected_relocations = ()
        if math_facts["target"] is not None:
            expected_relocations = ((
                6, "R_ARM_THM_CALL", math_facts["target"][0],
                "STT_NOTYPE", math_facts["target"][1],
            ),)
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in leaf["relocations"]) == expected_relocations,
                f"{math_name} relocation contract changed")
        stock_body = boot[
            math_facts["start"] - BOOT_BASE:
            math_facts["end"] - BOOT_BASE]
        require(sha256(stock_body) == math_facts["stock_sha256"],
                f"{math_name} stock body changed")
        require(direct_callers(boot, math_facts["start"]) ==
                FLOAT_MATH_CALLERS[math_name],
                f"{math_name} direct caller topology changed")
        require(all(direct_callers(boot, address) == ()
                    for address in range(math_facts["start"] + 2,
                                         math_facts["end"], 2)),
                f"{math_name} interior gained direct ingress")
        require(all(struct.pack("<I", address | 1) not in boot
                    for address in range(math_facts["start"],
                                         math_facts["end"], 2)),
                f"{math_name} gained a stored entry pointer")
        float_math_results.append({
            "function": math_name,
            "start": math_facts["start"],
            "stock_end_exclusive": math_facts["end"],
            "source_end_exclusive": math_facts["start"] + math_facts["size"],
            "source_bytes_by_profile": {
                "apple-clang": math_facts["size"],
                "linux-clang": math_facts["size"],
            },
            "retained_unreachable_tail_bytes": (
                math_facts["end"] - math_facts["start"] - math_facts["size"]
            ),
            "direct_call_sites": list(FLOAT_MATH_CALLERS[math_name]),
        })

    spotmgr_leaf = configured[SPOTMGR_TRANSITION["function"]]
    spotmgr_linux = spotmgr_leaf["toolchain_profiles"]["linux-clang"]
    spotmgr_relocation = ((
        SPOTMGR_TRANSITION["relocation_offset"], "R_ARM_THM_CALL",
        "open_cfw_bootloader_delay_us_41d1c0", "STT_NOTYPE",
        SPOTMGR_TRANSITION["provider"],
    ),)
    require((spotmgr_leaf["runtime_address"], spotmgr_leaf["expected"]["size"],
             spotmgr_leaf["expected"]["sha256"],
             spotmgr_leaf["expected"]["unrelocated_sha256"],
             spotmgr_leaf["stock"]["sha256"],
             spotmgr_leaf["source"]["license"],
             ROOT / spotmgr_leaf["source"]["path"]) ==
            (SPOTMGR_TRANSITION["start"],
             SPOTMGR_TRANSITION["end"] - SPOTMGR_TRANSITION["start"],
             SPOTMGR_TRANSITION["sha256"],
             SPOTMGR_TRANSITION["unrelocated_sha256"],
             SPOTMGR_TRANSITION["sha256"], "BSD-3-Clause",
             SPOTMGR_TRANSITION_SOURCE),
            "SPOT-manager Apple registration changed")
    require((spotmgr_linux["expected"]["size"],
             spotmgr_linux["expected"]["sha256"],
             spotmgr_linux["expected"]["unrelocated_sha256"],
             spotmgr_linux["stock"]["sha256"]) ==
            (SPOTMGR_TRANSITION["end"] - SPOTMGR_TRANSITION["start"],
             SPOTMGR_TRANSITION["sha256"],
             SPOTMGR_TRANSITION["unrelocated_sha256"],
             SPOTMGR_TRANSITION["sha256"]),
            "SPOT-manager Linux registration changed")
    for row in (spotmgr_leaf, spotmgr_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) == spotmgr_relocation,
                "SPOT-manager relocation contract changed")
    spotmgr_stock = boot[
        SPOTMGR_TRANSITION["start"] - BOOT_BASE:
        SPOTMGR_TRANSITION["end"] - BOOT_BASE]
    require(sha256(spotmgr_stock) == SPOTMGR_TRANSITION["sha256"],
            "SPOT-manager stock body changed")
    require(direct_callers(boot, SPOTMGR_TRANSITION["start"]) ==
            SPOTMGR_TRANSITION["callers"],
            "SPOT-manager transition direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_TRANSITION["start"] + 2,
                                     SPOTMGR_TRANSITION["end"], 2)),
            "SPOT-manager transition interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_TRANSITION["start"],
                                     SPOTMGR_TRANSITION["end"], 2)),
            "SPOT-manager transition gained a stored entry pointer")
    for address, value in SPOTMGR_TRANSITION["shared_literals"]:
        offset = address - BOOT_BASE
        require(struct.unpack_from("<I", boot, offset)[0] == value,
                f"SPOT-manager shared literal changed at 0x{address:08X}")
    spotmgr_result = {
        "function": SPOTMGR_TRANSITION["function"],
        "start": SPOTMGR_TRANSITION["start"],
        "end_exclusive": SPOTMGR_TRANSITION["end"],
        "source_bytes_by_profile": {"apple-clang": 106, "linux-clang": 106},
        "direct_call_sites": list(SPOTMGR_TRANSITION["callers"]),
        "provider": SPOTMGR_TRANSITION["provider"],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_TRANSITION["shared_literals"]
        ],
    }

    spotmgr_7b_leaf = configured[SPOTMGR_TRANSITION_7B["function"]]
    spotmgr_7b_linux = spotmgr_7b_leaf["toolchain_profiles"]["linux-clang"]
    spotmgr_7b_relocations = tuple(
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in SPOTMGR_TRANSITION_7B["relocations"]
    )
    require((spotmgr_7b_leaf["runtime_address"],
             spotmgr_7b_leaf["expected"]["size"],
             spotmgr_7b_leaf["expected"]["sha256"],
             spotmgr_7b_leaf["expected"]["unrelocated_sha256"],
             spotmgr_7b_leaf["stock"]["sha256"],
             spotmgr_7b_leaf["source"]["license"],
             ROOT / spotmgr_7b_leaf["source"]["path"]) ==
            (SPOTMGR_TRANSITION_7B["start"],
             SPOTMGR_TRANSITION_7B["end"] - SPOTMGR_TRANSITION_7B["start"],
             SPOTMGR_TRANSITION_7B["sha256"],
             SPOTMGR_TRANSITION_7B["unrelocated_sha256"],
             SPOTMGR_TRANSITION_7B["sha256"], "BSD-3-Clause",
             SPOTMGR_TRANSITION_7B_SOURCE),
            "SPOT-manager transition-7b Apple registration changed")
    require((spotmgr_7b_linux["expected"]["size"],
             spotmgr_7b_linux["expected"]["sha256"],
             spotmgr_7b_linux["expected"]["unrelocated_sha256"],
             spotmgr_7b_linux["stock"]["sha256"]) ==
            (SPOTMGR_TRANSITION_7B["end"] - SPOTMGR_TRANSITION_7B["start"],
             SPOTMGR_TRANSITION_7B["sha256"],
             SPOTMGR_TRANSITION_7B["unrelocated_sha256"],
             SPOTMGR_TRANSITION_7B["sha256"]),
            "SPOT-manager transition-7b Linux registration changed")
    for row in (spotmgr_7b_leaf, spotmgr_7b_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) ==
                spotmgr_7b_relocations,
                "SPOT-manager transition-7b relocation contract changed")
    spotmgr_7b_stock = boot[
        SPOTMGR_TRANSITION_7B["start"] - BOOT_BASE:
        SPOTMGR_TRANSITION_7B["end"] - BOOT_BASE]
    require(sha256(spotmgr_7b_stock) == SPOTMGR_TRANSITION_7B["sha256"],
            "SPOT-manager transition-7b stock body changed")
    require(direct_callers(boot, SPOTMGR_TRANSITION_7B["start"]) ==
            SPOTMGR_TRANSITION_7B["callers"],
            "SPOT-manager transition-7b direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_TRANSITION_7B["start"] + 2,
                                     SPOTMGR_TRANSITION_7B["end"], 2)),
            "SPOT-manager transition-7b interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_TRANSITION_7B["start"],
                                     SPOTMGR_TRANSITION_7B["end"], 2)),
            "SPOT-manager transition-7b gained a stored entry pointer")
    for address, value in SPOTMGR_TRANSITION_7B["shared_literals"]:
        offset = address - BOOT_BASE
        require(struct.unpack_from("<I", boot, offset)[0] == value,
                f"SPOT-manager transition-7b shared literal changed at "
                f"0x{address:08X}")
    spotmgr_7b_result = {
        "function": SPOTMGR_TRANSITION_7B["function"],
        "start": SPOTMGR_TRANSITION_7B["start"],
        "end_exclusive": SPOTMGR_TRANSITION_7B["end"],
        "source_bytes_by_profile": {"apple-clang": 276, "linux-clang": 276},
        "direct_call_sites": list(SPOTMGR_TRANSITION_7B["callers"]),
        "provider_edges": [
            {"offset": offset, "symbol": symbol, "target_address": target}
            for offset, symbol, target in SPOTMGR_TRANSITION_7B["relocations"]
        ],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_TRANSITION_7B["shared_literals"]
        ],
        "poll_limit_us": 20,
    }

    factory_leaf = configured[SPOTMGR_FACTORY_TRIMS["function"]]
    factory_linux = factory_leaf["toolchain_profiles"]["linux-clang"]
    require((factory_leaf["runtime_address"], factory_leaf["expected"]["size"],
             factory_leaf["expected"]["sha256"],
             factory_leaf["expected"]["unrelocated_sha256"],
             factory_leaf["stock"]["sha256"],
             factory_leaf["source"]["license"],
             ROOT / factory_leaf["source"]["path"]) ==
            (SPOTMGR_FACTORY_TRIMS["start"],
             SPOTMGR_FACTORY_TRIMS["end"] - SPOTMGR_FACTORY_TRIMS["start"],
             SPOTMGR_FACTORY_TRIMS["sha256"],
             SPOTMGR_FACTORY_TRIMS["sha256"],
             SPOTMGR_FACTORY_TRIMS["sha256"], "MIT",
             SPOTMGR_FACTORY_TRIMS_SOURCE),
            "SPOT-manager factory-trim Apple registration changed")
    require((factory_linux["expected"]["size"],
             factory_linux["expected"]["sha256"],
             factory_linux["expected"]["unrelocated_sha256"],
             factory_linux["stock"]["sha256"],
             factory_leaf["relocations"], factory_linux["relocations"]) ==
            (82, SPOTMGR_FACTORY_TRIMS["sha256"],
             SPOTMGR_FACTORY_TRIMS["sha256"],
             SPOTMGR_FACTORY_TRIMS["sha256"], [], []),
            "SPOT-manager factory-trim Linux registration changed")
    factory_stock = boot[
        SPOTMGR_FACTORY_TRIMS["start"] - BOOT_BASE:
        SPOTMGR_FACTORY_TRIMS["end"] - BOOT_BASE]
    require(sha256(factory_stock) == SPOTMGR_FACTORY_TRIMS["sha256"],
            "SPOT-manager factory-trim stock body changed")
    main_factory = main[
        SPOTMGR_FACTORY_TRIMS["main_start"] - MAIN_BASE:
        SPOTMGR_FACTORY_TRIMS["main_start"] - MAIN_BASE + len(factory_stock)]
    require(main_factory == factory_stock,
            "SPOT-manager factory-trim exact Apollo-main analogue changed")
    require(direct_callers(boot, SPOTMGR_FACTORY_TRIMS["start"]) ==
            SPOTMGR_FACTORY_TRIMS["callers"],
            "SPOT-manager factory-trim direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_FACTORY_TRIMS["start"] + 2,
                                     SPOTMGR_FACTORY_TRIMS["end"], 2)),
            "SPOT-manager factory-trim interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_FACTORY_TRIMS["start"],
                                     SPOTMGR_FACTORY_TRIMS["end"], 2)),
            "SPOT-manager factory-trim gained a stored entry pointer")
    for address, value in SPOTMGR_FACTORY_TRIMS["shared_literals"]:
        offset = address - BOOT_BASE
        require(struct.unpack_from("<I", boot, offset)[0] == value,
                f"SPOT-manager factory-trim shared literal changed at "
                f"0x{address:08X}")
    factory_trim_result = {
        "function": SPOTMGR_FACTORY_TRIMS["function"],
        "start": SPOTMGR_FACTORY_TRIMS["start"],
        "end_exclusive": SPOTMGR_FACTORY_TRIMS["end"],
        "source_bytes_by_profile": {"apple-clang": 82, "linux-clang": 82},
        "direct_call_sites": list(SPOTMGR_FACTORY_TRIMS["callers"]),
        "main_analogue": SPOTMGR_FACTORY_TRIMS["main_start"],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_FACTORY_TRIMS["shared_literals"]
        ],
    }

    ensure_leaf = configured[SPOTMGR_FACTORY_ENSURE["function"]]
    ensure_linux = ensure_leaf["toolchain_profiles"]["linux-clang"]
    ensure_relocation = ((
        SPOTMGR_FACTORY_ENSURE["relocation"][0], "R_ARM_THM_CALL",
        SPOTMGR_FACTORY_ENSURE["relocation"][1], "STT_NOTYPE",
        SPOTMGR_FACTORY_ENSURE["relocation"][2],
    ),)
    require((ensure_leaf["runtime_address"], ensure_leaf["expected"]["size"],
             ensure_leaf["expected"]["sha256"],
             ensure_leaf["expected"]["unrelocated_sha256"],
             ensure_leaf["stock"]["sha256"], ensure_leaf["source"]["license"],
             ROOT / ensure_leaf["source"]["path"]) ==
            (SPOTMGR_FACTORY_ENSURE["start"], 20,
             SPOTMGR_FACTORY_ENSURE["sha256"],
             SPOTMGR_FACTORY_ENSURE["unrelocated_sha256"],
             SPOTMGR_FACTORY_ENSURE["sha256"], "MIT",
             SPOTMGR_FACTORY_ENSURE_SOURCE),
            "SPOT-manager readiness Apple registration changed")
    require((ensure_linux["expected"]["size"],
             ensure_linux["expected"]["sha256"],
             ensure_linux["expected"]["unrelocated_sha256"],
             ensure_linux["stock"]["sha256"]) ==
            (20, SPOTMGR_FACTORY_ENSURE["sha256"],
             SPOTMGR_FACTORY_ENSURE["unrelocated_sha256"],
             SPOTMGR_FACTORY_ENSURE["sha256"]),
            "SPOT-manager readiness Linux registration changed")
    for row in (ensure_leaf, ensure_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) == ensure_relocation,
                "SPOT-manager readiness relocation contract changed")
    ensure_stock = boot[
        SPOTMGR_FACTORY_ENSURE["start"] - BOOT_BASE:
        SPOTMGR_FACTORY_ENSURE["end"] - BOOT_BASE]
    require(sha256(ensure_stock) == SPOTMGR_FACTORY_ENSURE["sha256"],
            "SPOT-manager readiness stock body changed")
    ensure_main = main[
        SPOTMGR_FACTORY_ENSURE["main_start"] - MAIN_BASE:
        SPOTMGR_FACTORY_ENSURE["main_start"] - MAIN_BASE + len(ensure_stock)]
    require(ensure_main == ensure_stock,
            "SPOT-manager readiness exact Apollo-main analogue changed")
    require(direct_callers(boot, SPOTMGR_FACTORY_ENSURE["start"]) == (),
            "SPOT-manager readiness gained direct ingress")
    require(boot.find(struct.pack("<I", SPOTMGR_FACTORY_ENSURE["start"] | 1)) ==
            SPOTMGR_FACTORY_ENSURE["stored_pointer"] - BOOT_BASE,
            "SPOT-manager readiness stored ingress changed")
    for address, value in SPOTMGR_FACTORY_ENSURE["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager readiness shared literal changed")
    ensure_result = {
        "function": SPOTMGR_FACTORY_ENSURE["function"],
        "start": SPOTMGR_FACTORY_ENSURE["start"],
        "end_exclusive": SPOTMGR_FACTORY_ENSURE["end"],
        "source_bytes_by_profile": {"apple-clang": 20, "linux-clang": 20},
        "stored_entry_pointer": SPOTMGR_FACTORY_ENSURE["stored_pointer"],
        "provider": SPOTMGR_FACTORY_ENSURE["relocation"][2],
        "main_analogue": SPOTMGR_FACTORY_ENSURE["main_start"],
    }

    timer_leaf = configured[SPOTMGR_TIMER_IRQ["function"]]
    timer_linux = timer_leaf["toolchain_profiles"]["linux-clang"]
    timer_relocations = tuple(
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in SPOTMGR_TIMER_IRQ["relocations"]
    )
    require((timer_leaf["runtime_address"], timer_leaf["expected"]["size"],
             timer_leaf["expected"]["sha256"],
             timer_leaf["expected"]["unrelocated_sha256"],
             timer_leaf["stock"]["sha256"], timer_leaf["source"]["license"],
             ROOT / timer_leaf["source"]["path"]) ==
            (SPOTMGR_TIMER_IRQ["start"], 46, SPOTMGR_TIMER_IRQ["sha256"],
             SPOTMGR_TIMER_IRQ["unrelocated_sha256"],
             SPOTMGR_TIMER_IRQ["sha256"], "BSD-3-Clause",
             SPOTMGR_TIMER_IRQ_SOURCE),
            "SPOT-manager timer ISR Apple registration changed")
    require((timer_linux["expected"]["size"],
             timer_linux["expected"]["sha256"],
             timer_linux["expected"]["unrelocated_sha256"],
             timer_linux["stock"]["sha256"]) ==
            (46, SPOTMGR_TIMER_IRQ["sha256"],
             SPOTMGR_TIMER_IRQ["unrelocated_sha256"],
             SPOTMGR_TIMER_IRQ["sha256"]),
            "SPOT-manager timer ISR Linux registration changed")
    for row in (timer_leaf, timer_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) == timer_relocations,
                "SPOT-manager timer ISR relocation contract changed")
    timer_stock = boot[
        SPOTMGR_TIMER_IRQ["start"] - BOOT_BASE:
        SPOTMGR_TIMER_IRQ["end"] - BOOT_BASE]
    require(sha256(timer_stock) == SPOTMGR_TIMER_IRQ["sha256"],
            "SPOT-manager timer ISR stock body changed")
    require(direct_callers(boot, SPOTMGR_TIMER_IRQ["start"]) ==
            SPOTMGR_TIMER_IRQ["callers"],
            "SPOT-manager timer ISR caller topology changed")
    require(boot.find(struct.pack("<I", SPOTMGR_TIMER_IRQ["start"] | 1)) ==
            SPOTMGR_TIMER_IRQ["stored_pointer"] - BOOT_BASE,
            "SPOT-manager timer ISR stored ingress changed")
    for address, value in SPOTMGR_TIMER_IRQ["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager timer ISR shared literal changed")
    timer_irq_result = {
        "function": SPOTMGR_TIMER_IRQ["function"],
        "start": SPOTMGR_TIMER_IRQ["start"],
        "end_exclusive": SPOTMGR_TIMER_IRQ["end"],
        "source_bytes_by_profile": {"apple-clang": 46, "linux-clang": 46},
        "direct_call_sites": list(SPOTMGR_TIMER_IRQ["callers"]),
        "stored_entry_pointer": SPOTMGR_TIMER_IRQ["stored_pointer"],
        "provider_edges": [
            {"offset": offset, "symbol": symbol, "target_address": target}
            for offset, symbol, target in SPOTMGR_TIMER_IRQ["relocations"]
        ],
        "corrected_prior_end_exclusive": 0x0042A074,
    }

    buck_leaf = configured[SPOTMGR_BUCK_DEEPSLEEP["function"]]
    buck_linux = buck_leaf["toolchain_profiles"]["linux-clang"]
    buck_relocation = ((
        SPOTMGR_BUCK_DEEPSLEEP["relocation"][0], "R_ARM_THM_CALL",
        SPOTMGR_BUCK_DEEPSLEEP["relocation"][1], "STT_NOTYPE",
        SPOTMGR_BUCK_DEEPSLEEP["relocation"][2],
    ),)
    require((buck_leaf["runtime_address"], buck_leaf["expected"]["size"],
             buck_leaf["expected"]["sha256"],
             buck_leaf["expected"]["unrelocated_sha256"],
             buck_leaf["stock"]["sha256"], buck_leaf["source"]["license"],
             ROOT / buck_leaf["source"]["path"]) ==
            (SPOTMGR_BUCK_DEEPSLEEP["start"], 272,
             SPOTMGR_BUCK_DEEPSLEEP["sha256"],
             SPOTMGR_BUCK_DEEPSLEEP["unrelocated_sha256"],
             SPOTMGR_BUCK_DEEPSLEEP["sha256"], "BSD-3-Clause",
             SPOTMGR_BUCK_DEEPSLEEP_SOURCE),
            "SPOT-manager SIMOBUCK Apple registration changed")
    require((buck_linux["expected"]["size"],
             buck_linux["expected"]["sha256"],
             buck_linux["expected"]["unrelocated_sha256"],
             buck_linux["stock"]["sha256"]) ==
            (272, SPOTMGR_BUCK_DEEPSLEEP["sha256"],
             SPOTMGR_BUCK_DEEPSLEEP["unrelocated_sha256"],
             SPOTMGR_BUCK_DEEPSLEEP["sha256"]),
            "SPOT-manager SIMOBUCK Linux registration changed")
    for row in (buck_leaf, buck_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) == buck_relocation,
                "SPOT-manager SIMOBUCK relocation contract changed")
    buck_stock = boot[
        SPOTMGR_BUCK_DEEPSLEEP["start"] - BOOT_BASE:
        SPOTMGR_BUCK_DEEPSLEEP["end"] - BOOT_BASE]
    require(sha256(buck_stock) == SPOTMGR_BUCK_DEEPSLEEP["sha256"],
            "SPOT-manager SIMOBUCK stock body changed")
    buck_main = main[
        SPOTMGR_BUCK_DEEPSLEEP["main_start"] - MAIN_BASE:
        SPOTMGR_BUCK_DEEPSLEEP["main_start"] - MAIN_BASE + len(buck_stock)]
    require(sha256(buck_main) == SPOTMGR_BUCK_DEEPSLEEP["main_sha256"],
            "SPOT-manager SIMOBUCK Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(buck_stock, buck_main)) ==
            SPOTMGR_BUCK_DEEPSLEEP["identical_bytes"],
            "SPOT-manager SIMOBUCK cross-image identity changed")
    require(difference_runs(buck_stock, buck_main) ==
            SPOTMGR_BUCK_DEEPSLEEP["difference_runs"],
            "SPOT-manager SIMOBUCK cross-image difference topology changed")
    require(direct_callers(boot, SPOTMGR_BUCK_DEEPSLEEP["start"]) ==
            SPOTMGR_BUCK_DEEPSLEEP["callers"],
            "SPOT-manager SIMOBUCK caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_BUCK_DEEPSLEEP["start"] + 2,
                                     SPOTMGR_BUCK_DEEPSLEEP["end"], 2)),
            "SPOT-manager SIMOBUCK interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_BUCK_DEEPSLEEP["start"],
                                     SPOTMGR_BUCK_DEEPSLEEP["end"], 2)),
            "SPOT-manager SIMOBUCK gained a stored entry pointer")
    for address, value in SPOTMGR_BUCK_DEEPSLEEP["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager SIMOBUCK shared literal changed")
    buck_deepsleep_result = {
        "function": SPOTMGR_BUCK_DEEPSLEEP["function"],
        "start": SPOTMGR_BUCK_DEEPSLEEP["start"],
        "end_exclusive": SPOTMGR_BUCK_DEEPSLEEP["end"],
        "source_bytes_by_profile": {"apple-clang": 272, "linux-clang": 272},
        "direct_call_sites": list(SPOTMGR_BUCK_DEEPSLEEP["callers"]),
        "provider": SPOTMGR_BUCK_DEEPSLEEP["relocation"][2],
        "main_analogue": SPOTMGR_BUCK_DEEPSLEEP["main_start"],
        "identical_main_bytes": SPOTMGR_BUCK_DEEPSLEEP["identical_bytes"],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_BUCK_DEEPSLEEP["shared_literals"]
        ],
        "timer_count": 16,
        "timer_clock_ranges": [[0, 6], [19, 25], [0x100, 0x1E0]],
    }

    scan_leaf = configured[SPOTMGR_BUCK_SCAN["function"]]
    scan_linux = scan_leaf["toolchain_profiles"]["linux-clang"]
    scan_relocation = ((
        SPOTMGR_BUCK_SCAN["relocation"][0], "R_ARM_THM_CALL",
        SPOTMGR_BUCK_SCAN["relocation"][1], "STT_NOTYPE",
        SPOTMGR_BUCK_SCAN["relocation"][2],
    ),)
    require((scan_leaf["runtime_address"], scan_leaf["expected"]["size"],
             scan_leaf["expected"]["sha256"],
             scan_leaf["expected"]["unrelocated_sha256"],
             scan_leaf["stock"]["sha256"], scan_leaf["source"]["license"],
             ROOT / scan_leaf["source"]["path"]) ==
            (SPOTMGR_BUCK_SCAN["start"], 288,
             SPOTMGR_BUCK_SCAN["sha256"],
             SPOTMGR_BUCK_SCAN["unrelocated_sha256"],
             SPOTMGR_BUCK_SCAN["sha256"], "BSD-3-Clause",
             SPOTMGR_BUCK_SCAN_SOURCE),
            "second SPOT-manager deep-sleep Apple registration changed")
    require((scan_linux["expected"]["size"],
             scan_linux["expected"]["sha256"],
             scan_linux["expected"]["unrelocated_sha256"],
             scan_linux["stock"]["sha256"]) ==
            (288, SPOTMGR_BUCK_SCAN["sha256"],
             SPOTMGR_BUCK_SCAN["unrelocated_sha256"],
             SPOTMGR_BUCK_SCAN["sha256"]),
            "second SPOT-manager deep-sleep Linux registration changed")
    for row in (scan_leaf, scan_linux):
        require(tuple((item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in row["relocations"]) == scan_relocation,
                "second SPOT-manager deep-sleep relocation contract changed")
    scan_stock = boot[SPOTMGR_BUCK_SCAN["start"] - BOOT_BASE:
                      SPOTMGR_BUCK_SCAN["end"] - BOOT_BASE]
    scan_main = main[SPOTMGR_BUCK_SCAN["main_start"] - MAIN_BASE:
                     SPOTMGR_BUCK_SCAN["main_start"] - MAIN_BASE + 288]
    require(sha256(scan_stock) == SPOTMGR_BUCK_SCAN["sha256"] and
            sha256(scan_main) == SPOTMGR_BUCK_SCAN["main_sha256"],
            "second SPOT-manager deep-sleep cross-image body changed")
    require(sum(left == right for left, right in zip(scan_stock, scan_main)) ==
            SPOTMGR_BUCK_SCAN["identical_bytes"] and
            difference_runs(scan_stock, scan_main) ==
            SPOTMGR_BUCK_SCAN["difference_runs"],
            "second SPOT-manager deep-sleep identity topology changed")
    require(direct_callers(boot, SPOTMGR_BUCK_SCAN["start"]) ==
            SPOTMGR_BUCK_SCAN["callers"],
            "second SPOT-manager deep-sleep caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_BUCK_SCAN["start"] + 2,
                                     SPOTMGR_BUCK_SCAN["end"], 2)),
            "second SPOT-manager deep-sleep interior gained direct ingress")
    require(struct.pack("<I", SPOTMGR_BUCK_SCAN["start"] | 1) not in boot,
            "second SPOT-manager deep-sleep gained stored ingress")
    for address, value in SPOTMGR_BUCK_SCAN["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "second SPOT-manager deep-sleep boot literal changed")
    for address, value in SPOTMGR_BUCK_SCAN["main_literals"]:
        require(struct.unpack_from("<I", main, address - MAIN_BASE)[0] == value,
                "second SPOT-manager deep-sleep main literal changed")
    buck_scan_result = {
        "function": SPOTMGR_BUCK_SCAN["function"],
        "start": SPOTMGR_BUCK_SCAN["start"],
        "end_exclusive": SPOTMGR_BUCK_SCAN["end"],
        "source_bytes_by_profile": {"apple-clang": 288, "linux-clang": 288},
        "direct_call_sites": list(SPOTMGR_BUCK_SCAN["callers"]),
        "provider": SPOTMGR_BUCK_SCAN["relocation"][2],
        "main_analogue": SPOTMGR_BUCK_SCAN["main_start"],
        "identical_main_bytes": SPOTMGR_BUCK_SCAN["identical_bytes"],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_BUCK_SCAN["shared_literals"]
        ],
        "host_cases_tested": 100_000,
    }

    effects_leaf = configured[SPOTMGR_STATE_EFFECTS["function"]]
    effects_linux = effects_leaf["toolchain_profiles"]["linux-clang"]
    for profile, leaf in (("Apple", effects_leaf), ("Linux", effects_linux)):
        require((leaf["expected"]["size"], leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["relocations"]) ==
                (84, SPOTMGR_STATE_EFFECTS["sha256"],
                 SPOTMGR_STATE_EFFECTS["sha256"],
                 SPOTMGR_STATE_EFFECTS["sha256"], []),
                f"SPOT-manager transition-effects {profile} registration changed")
    require((effects_leaf["runtime_address"],
             effects_leaf["source"]["license"],
             ROOT / effects_leaf["source"]["path"]) ==
            (SPOTMGR_STATE_EFFECTS["start"], "BSD-3-Clause",
             SPOTMGR_STATE_EFFECTS_SOURCE),
            "SPOT-manager transition-effects source registration changed")
    effects_stock = boot[SPOTMGR_STATE_EFFECTS["start"] - BOOT_BASE:
                         SPOTMGR_STATE_EFFECTS["end"] - BOOT_BASE]
    effects_main = main[SPOTMGR_STATE_EFFECTS["main_start"] - MAIN_BASE:
                        SPOTMGR_STATE_EFFECTS["main_start"] - MAIN_BASE + 84]
    require(effects_stock == effects_main and
            sha256(effects_stock) == SPOTMGR_STATE_EFFECTS["sha256"],
            "SPOT-manager transition-effects cross-image body changed")
    require(direct_callers(boot, SPOTMGR_STATE_EFFECTS["start"]) ==
            SPOTMGR_STATE_EFFECTS["callers"],
            "SPOT-manager transition-effects caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_STATE_EFFECTS["start"] + 2,
                                     SPOTMGR_STATE_EFFECTS["end"], 2)),
            "SPOT-manager transition-effects interior gained ingress")
    require(struct.pack("<I", SPOTMGR_STATE_EFFECTS["start"] | 1) not in boot,
            "SPOT-manager transition-effects gained stored ingress")
    for address, value in SPOTMGR_STATE_EFFECTS["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager transition-effects boot literal changed")
    for address, value in SPOTMGR_STATE_EFFECTS["main_literals"]:
        require(struct.unpack_from("<I", main, address - MAIN_BASE)[0] == value,
                "SPOT-manager transition-effects main literal changed")
    state_effects_result = {
        "function": SPOTMGR_STATE_EFFECTS["function"],
        "start": SPOTMGR_STATE_EFFECTS["start"],
        "end_exclusive": SPOTMGR_STATE_EFFECTS["end"],
        "source_bytes_by_profile": {"apple-clang": 84, "linux-clang": 84},
        "direct_call_sites": list(SPOTMGR_STATE_EFFECTS["callers"]),
        "main_analogue": SPOTMGR_STATE_EFFECTS["main_start"],
        "exact_main_bytes": 84,
        "cleared_power_control_mask": 0x10048,
        "state_pairs_tested": 65_536,
    }

    pt_leaf = configured[SPOTMGR_POWER_TRANSITION["function"]]
    pt_linux = pt_leaf["toolchain_profiles"]["linux-clang"]
    pt_relocations = [{
        "offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
        "symbol_type": "STT_NOTYPE", "target_address": target,
    } for offset, symbol, target in SPOTMGR_POWER_TRANSITION["relocations"]]
    require((pt_leaf["runtime_address"], pt_leaf["expected"]["size"],
             pt_leaf["expected"]["sha256"],
             pt_leaf["expected"]["unrelocated_sha256"],
             pt_leaf["stock"]["sha256"], pt_leaf["source"]["license"],
             ROOT / pt_leaf["source"]["path"], pt_leaf["relocations"]) ==
            (SPOTMGR_POWER_TRANSITION["start"], 552,
             SPOTMGR_POWER_TRANSITION["sha256"],
             SPOTMGR_POWER_TRANSITION["unrelocated_sha256"],
             SPOTMGR_POWER_TRANSITION["sha256"], "BSD-3-Clause",
             SPOTMGR_POWER_TRANSITION_SOURCE, pt_relocations),
            "SPOT-manager power-transition Apple registration changed")
    require((pt_linux["expected"]["size"], pt_linux["expected"]["sha256"],
             pt_linux["expected"]["unrelocated_sha256"],
             pt_linux["stock"]["sha256"], pt_linux["relocations"]) ==
            (552, SPOTMGR_POWER_TRANSITION["sha256"],
             SPOTMGR_POWER_TRANSITION["unrelocated_sha256"],
             SPOTMGR_POWER_TRANSITION["sha256"], pt_relocations),
            "SPOT-manager power-transition Linux registration changed")
    pt_stock = boot[SPOTMGR_POWER_TRANSITION["start"] - BOOT_BASE:
                    SPOTMGR_POWER_TRANSITION["end"] - BOOT_BASE]
    pt_main = main[SPOTMGR_POWER_TRANSITION["main_start"] - MAIN_BASE:
                   SPOTMGR_POWER_TRANSITION["main_start"] - MAIN_BASE + 552]
    require(sha256(pt_stock) == SPOTMGR_POWER_TRANSITION["sha256"] and
            sha256(pt_main) == SPOTMGR_POWER_TRANSITION["main_sha256"],
            "SPOT-manager power-transition cross-image body changed")
    require(sum(left == right for left, right in zip(pt_stock, pt_main)) ==
            SPOTMGR_POWER_TRANSITION["identical_bytes"] and
            difference_runs(pt_stock, pt_main) ==
            SPOTMGR_POWER_TRANSITION["difference_runs"],
            "SPOT-manager power-transition difference topology changed")
    require(direct_callers(boot, SPOTMGR_POWER_TRANSITION["start"]) ==
            SPOTMGR_POWER_TRANSITION["callers"],
            "SPOT-manager power-transition caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_POWER_TRANSITION["start"] + 2,
                                     SPOTMGR_POWER_TRANSITION["end"], 2)),
            "SPOT-manager power-transition interior gained ingress")
    require(struct.pack("<I", SPOTMGR_POWER_TRANSITION["start"] | 1) not in boot,
            "SPOT-manager power-transition gained stored ingress")
    for address, value in SPOTMGR_POWER_TRANSITION["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager power-transition shared literal changed")
    power_transition_result = {
        "function": SPOTMGR_POWER_TRANSITION["function"],
        "start": SPOTMGR_POWER_TRANSITION["start"],
        "end_exclusive": SPOTMGR_POWER_TRANSITION["end"],
        "source_bytes_by_profile": {"apple-clang": 552, "linux-clang": 552},
        "direct_call_sites": list(SPOTMGR_POWER_TRANSITION["callers"]),
        "provider_edges": [{"offset": offset, "target_address": target}
                           for offset, _symbol, target in
                           SPOTMGR_POWER_TRANSITION["relocations"]],
        "main_analogue": SPOTMGR_POWER_TRANSITION["main_start"],
        "identical_main_bytes": SPOTMGR_POWER_TRANSITION["identical_bytes"],
        "route_cases_tested": 10_500,
        "temporary_trim_widths": [10, 6],
    }

    divider_results = []
    for facts in DIVIDER_HELPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"], leaf["stock"]["sha256"],
                 leaf["source"]["license"], ROOT / leaf["source"]["path"],
                 leaf["relocations"]) ==
                (facts["start"], size, facts["sha256"], facts["sha256"],
                 "MIT", DIVIDER_HELPERS_SOURCE, []),
                f"rounded-divider Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (size, facts["sha256"], facts["sha256"], []),
                f"rounded-divider Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"rounded-divider main analogue changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"rounded-divider caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"rounded-divider interior gained ingress: {facts['function']}")
        divider_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "main_analogue": facts["main_start"],
            "exact_main_bytes": size, "host_cases_tested": facts["host_cases"],
        })

    facts = HW_EVENT_APPLY
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [(offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
                            for offset, symbol, target in facts["relocations"]]
    observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"])
                for x in leaf["relocations"]]
    linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"])
                      for x in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"],
             leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], "MIT", HW_EVENT_APPLY_SOURCE, expected_relocations),
            "hardware-event apply Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"],
             linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"],
                                  facts["sha256"], expected_relocations),
            "hardware-event apply Linux registration changed")
    stock = boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    analogue = main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock) == facts["sha256"], "hardware-event apply stock changed")
    require(sum(a == b for a, b in zip(stock, analogue)) == facts["identical_main_bytes"],
            "hardware-event apply main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-event apply callers changed")
    require(all(direct_callers(boot, a) == () for a in range(facts["start"]+2,facts["end"],2)),
            "hardware-event apply interior gained ingress")
    require(struct.pack("<I",facts["start"]|1) not in boot,
            "hardware-event apply gained stored ingress")
    require(struct.unpack_from("<II",boot,0x42C6E8-BOOT_BASE) ==
            (0x40050000,0x08000001), "hardware-event apply literals changed")
    hw_event_apply_result = {"function":facts["function"],"start":facts["start"],
        "end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},
        "direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],
        "identical_main_bytes":facts["identical_main_bytes"],
        "provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],
        "drain_event_mask":0x800,"pulse_event_mask":0x210,
        "hardware_validation":"blocked by unavailable physical evidence"}

    facts = HW_CLOCK_ENCODE
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in facts["relocations"]
    ]
    observed = [(item["offset"], item["type"], item["symbol"],
                 item["symbol_type"], item["target_address"])
                for item in leaf["relocations"]]
    linux_observed = [(item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"],
             facts["unrelocated_sha256"], facts["sha256"], "MIT",
             HW_CLOCK_ENCODE_SOURCE, expected_relocations),
            "hardware-clock encoder Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], expected_relocations),
            "hardware-clock encoder Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-clock encoder stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-clock encoder main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-clock encoder caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-clock encoder interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-clock encoder gained stored ingress")
    require(struct.unpack_from("<II", boot, 0x42C980 - BOOT_BASE) ==
            (96_000_000, 250_000), "hardware-clock encoder literals changed")
    hw_clock_encode_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "provider_edges": [{"offset": offset, "target_address": target}
                           for offset, _symbol, target in facts["relocations"]],
        "source_clock_hz": 96_000_000, "maximum_exponent": 7,
        "host_cases_tested": 10_032,
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    state_range_results = []
    for facts in STATE_RANGE_SERVICES:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        relocations = tuple(
            (offset, "R_ARM_THM_CALL", symbol, symbol_type, target)
            for offset, symbol, target, symbol_type in facts["relocations"]
        )
        observed = tuple((item["offset"], item["type"], item["symbol"],
                          item["symbol_type"], item["target_address"])
                         for item in leaf["relocations"])
        linux_observed = tuple((item["offset"], item["type"], item["symbol"],
                                item["symbol_type"], item["target_address"])
                               for item in linux["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 STATE_RANGE_SOURCE, relocations),
                f"state/range Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], relocations),
                f"state/range Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"state/range Apollo-main body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"state/range caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"state/range interior gained ingress: {facts['function']}")
        if facts["stored_pointer"] is not None:
            require(struct.unpack_from("<I", boot,
                    facts["stored_pointer"] - BOOT_BASE)[0] == facts["start"] | 1,
                    f"state/range stored ingress changed: {facts['function']}")
        state_range_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "stored_pointer": facts["stored_pointer"],
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target, _type in facts["relocations"]],
            "main_analogue": facts["main_start"], "portable_cases": facts["cases"],
        })

    facts=STATE_EVENT_ZERO;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",STATE_EVENT_ZERO_SOURCE,expected_relocations),"state-event classifier Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"state-event classifier Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"state-event classifier cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"state-event classifier ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"state-event classifier gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"state-event classifier literals changed")
    state_event_zero_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"channel_count":16,"classified_ranges":[[0,6],[19,25],[256,480]],"hardware_validation":"blocked by unavailable physical evidence"}

    facts=STATE_EVENT_ONE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",STATE_EVENT_ONE_SOURCE,expected_relocations),"state-one Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"state-one Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"state-one cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"state-one ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"state-one gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"state-one literals changed")
    state_event_one_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"delay_sequences_us":{"active":[5,10],"nonactive":[15]},"power_mask":0xF0000000,"hardware_validation":"blocked by unavailable physical evidence"}

    misc_primitive_results = []
    for facts in MISC_PRIMITIVES:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], leaf["relocations"]) ==
                (facts["start"], size, facts["sha256"], facts["sha256"],
                 facts["sha256"], "MIT", MISC_PRIMITIVES_SOURCE, []),
                f"miscellaneous primitive Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
                f"miscellaneous primitive Linux registration changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"miscellaneous primitive caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"miscellaneous primitive interior gained ingress: {facts['function']}")
        misc_primitive_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "portable_cases": facts["cases"],
            "hardware_validation": ("blocked by unavailable physical evidence"
                                    if facts["function"].endswith(("42dc90", "42e514")) else None),
        })

    register_helper_results = []
    for facts in REGISTER_HELPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], leaf["relocations"]) ==
                (facts["start"], size, facts["sha256"], facts["sha256"],
                 facts["sha256"], "MIT", REGISTER_HELPERS_SOURCE, []),
                f"register-helper Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
                f"register-helper Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        require(sha256(stock) == facts["sha256"],
                f"register-helper stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"register-helper caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"register-helper interior gained ingress: {facts['function']}")
        require(struct.pack("<I", facts["start"] | 1) not in boot,
                f"register-helper gained stored ingress: {facts['function']}")
        register_helper_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "portable_cases": facts["cases"],
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    cmdq_adapter_results = []
    for facts in CMDQ_ADAPTERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        offset, symbol, target = facts["relocation"]
        expected_relocation = [(offset, "R_ARM_THM_CALL", symbol,
                                "STT_NOTYPE", target)]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 CMDQ_ADAPTERS_SOURCE, expected_relocation),
                f"command-queue adapter Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocation),
                f"command-queue adapter Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"command-queue adapter stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"command-queue adapter caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"command-queue adapter interior gained ingress: {facts['function']}")
        cmdq_adapter_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edge": {"offset": offset, "target_address": target},
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    facts = HW_DESCRIPTOR_PUBLISH
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], leaf["relocations"]) ==
            (facts["start"], size, facts["sha256"], facts["sha256"],
             facts["sha256"], "MIT", HW_DESCRIPTOR_SOURCE, []),
            "hardware-descriptor Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux["relocations"]) ==
            (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
            "hardware-descriptor Linux registration changed")
    require(sha256(boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]) ==
            facts["sha256"], "hardware-descriptor stock body changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-descriptor direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-descriptor interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-descriptor gained stored ingress")
    hw_descriptor_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "descriptor_stride": 32,
        "published_field_order": [0, 1, 4, 2, 3, 5],
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_CONTEXT_CLAIM
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], leaf["relocations"]) ==
            (facts["start"], size, facts["sha256"], facts["sha256"],
             facts["sha256"], "MIT", HW_CONTEXT_CLAIM_SOURCE, []),
            "hardware-context claim Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux["relocations"]) ==
            (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
            "hardware-context claim Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-context claim stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-context claim main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-context claim direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-context claim interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-context claim gained stored ingress")
    hw_context_claim_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "handle_magic": 0x00123456, "context_stride": 0x8A8,
        "status_codes": {"success": 0, "index": 5, "output": 6, "claimed": 7},
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_CONTEXT_ENABLE
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in facts["relocations"]
    ]
    observed = [(item["offset"], item["type"], item["symbol"],
                 item["symbol_type"], item["target_address"])
                for item in leaf["relocations"]]
    linux_observed = [(item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"],
             facts["unrelocated_sha256"], facts["sha256"], "MIT",
             HW_CONTEXT_ENABLE_SOURCE, expected_relocations),
            "hardware-context enable Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], expected_relocations),
            "hardware-context enable Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-context enable stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-context enable main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-context enable direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-context enable interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-context enable gained stored ingress")
    hw_context_enable_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in facts["relocations"]
        ],
        "active_flag": 0x02000000, "rollback_mask": 0x00000011,
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_EVENT_SERVICE
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in facts["relocations"]
    ]
    observed = [(item["offset"], item["type"], item["symbol"],
                 item["symbol_type"], item["target_address"])
                for item in leaf["relocations"]]
    linux_observed = [(item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"],
             facts["unrelocated_sha256"], facts["sha256"], "MIT",
             HW_EVENT_SERVICE_SOURCE, expected_relocations),
            "hardware-event service Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], expected_relocations),
            "hardware-event service Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-event service stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-event service main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-event service direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-event service interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-event service gained stored ingress")
    hw_event_service_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in facts["relocations"]
        ],
        "descriptor_stride": 32, "event_apply_mask": 0x00004A7C,
        "register_200_mask": 0xFFFFFBFE,
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_CONFIG_TRANSACTION
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in facts["relocations"]
    ]
    observed = [(item["offset"], item["type"], item["symbol"],
                 item["symbol_type"], item["target_address"])
                for item in leaf["relocations"]]
    linux_observed = [(item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"],
             facts["unrelocated_sha256"], facts["sha256"], "MIT",
             HW_CONFIG_TRANSACTION_SOURCE, expected_relocations),
            "hardware-config transaction Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], expected_relocations),
            "hardware-config transaction Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-config transaction stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-config transaction main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-config transaction direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-config transaction interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-config transaction gained stored ingress")
    hw_config_transaction_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in facts["relocations"]
        ],
        "snapshot_register_count": 13, "supported_modes": [0, 1, 2],
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_INSTANCE_CONFIGURE
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in facts["relocations"]
    ]
    observed = [(item["offset"], item["type"], item["symbol"],
                 item["symbol_type"], item["target_address"])
                for item in leaf["relocations"]]
    linux_observed = [(item["offset"], item["type"], item["symbol"],
                       item["symbol_type"], item["target_address"])
                      for item in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"],
             facts["unrelocated_sha256"], facts["sha256"], "MIT",
             HW_INSTANCE_CONFIGURE_SOURCE, expected_relocations),
            "hardware-instance configurator Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], expected_relocations),
            "hardware-instance configurator Linux registration changed")
    stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
    analogue = main[facts["main_start"] - MAIN_BASE:
                    facts["main_start"] - MAIN_BASE + size]
    require(sha256(stock) == facts["sha256"],
            "hardware-instance configurator stock body changed")
    require(sum(left == right for left, right in zip(stock, analogue)) ==
            facts["identical_main_bytes"],
            "hardware-instance configurator main analogue changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"],
            "hardware-instance configurator direct ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(facts["start"] + 2, facts["end"], 2)),
            "hardware-instance configurator interior gained ingress")
    require(struct.pack("<I", facts["start"] | 1) not in boot,
            "hardware-instance configurator gained stored ingress")
    hw_instance_configure_result = {
        "function": facts["function"], "start": facts["start"],
        "end_exclusive": facts["end"],
        "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
        "direct_call_sites": list(facts["callers"]),
        "main_analogue": facts["main_start"],
        "identical_main_bytes": facts["identical_main_bytes"],
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in facts["relocations"]
        ],
        "supported_modes": [0, 1],
        "fixed_rates_hz": [100_000, 400_000, 1_000_000],
        "maximum_instances": 8, "slot_count": 4,
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    facts = HW_CONFIG_RETRY
    leaf = configured[facts["function"]]
    linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [(o, "R_ARM_THM_CALL", n, "STT_NOTYPE", t)
                            for o, n, t in facts["relocations"]]
    observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"])
                for x in leaf["relocations"]]
    linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"])
                      for x in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"],
             leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) ==
            (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"],
             facts["sha256"], "MIT", HW_CONFIG_RETRY_SOURCE, expected_relocations),
            "hardware-config retry Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) ==
            (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations),
            "hardware-config retry Linux registration changed")
    stock = boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    analogue = main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock) == facts["sha256"], "hardware-config retry stock changed")
    require(sum(a == b for a,b in zip(stock,analogue)) == facts["identical_main_bytes"],
            "hardware-config retry main analogue changed")
    require(direct_callers(boot,facts["start"]) == facts["callers"],
            "hardware-config retry callers changed")
    require(all(direct_callers(boot,a) == () for a in range(facts["start"]+2,facts["end"],2)),
            "hardware-config retry interior gained ingress")
    require(struct.pack("<I",facts["start"]|1) not in boot,
            "hardware-config retry gained stored ingress")
    require(struct.unpack_from("<II",boot,0x430640-BOOT_BASE) == (0x20000374,0x00434158),
            "hardware-config retry literals changed")
    hw_config_retry_result = {"function":facts["function"],"start":facts["start"],
        "end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},
        "direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],
        "identical_main_bytes":facts["identical_main_bytes"],
        "provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],
        "maximum_attempts":1000,"retry_delay_us":10,"timeout_status":4,
        "hardware_validation":"blocked by unavailable physical evidence"}

    facts=PLATFORM_FINISH;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",PLATFORM_FINISH_SOURCE,expected_relocations),"platform-finalizer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"platform-finalizer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"platform-finalizer cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"platform-finalizer ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"platform-finalizer gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"platform-finalizer literals changed")
    platform_finish_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"slot_count":8,"interrupt_number":10,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=PLATFORM_BRINGUP;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]];observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",PLATFORM_BRINGUP_SOURCE,expected_relocations),"platform bring-up Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"platform bring-up Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];require(sha256(stock)==facts["sha256"],"platform bring-up stock changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"platform bring-up ingress changed");require(struct.pack("<I",facts["start"]|1)not in boot,"platform bring-up gained stored ingress");require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"platform bring-up literals changed")
    platform_bringup_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"measurement_attempts":3,"measurement_scale_numerator":0x4A6,"measurement_scale_shift":12,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=DESCRIPTOR_REGISTER;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",DESCRIPTOR_REGISTER_SOURCE,expected_relocations),"descriptor registrar Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"descriptor registrar Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"descriptor registrar cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"descriptor registrar ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"descriptor registrar gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"descriptor registrar literals changed")
    descriptor_register_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"descriptor_stride":12,"supported_types":[1,2,4],"interrupt_mask_words":7,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=HW_STATE_COMPOSE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",HW_STATE_COMPOSE_SOURCE,expected_relocations),"hardware-state composer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"hardware-state composer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"hardware-state composer cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"hardware-state composer direct ingress changed")
    require(struct.unpack_from("<I",boot,facts["stored_pointer"]-BOOT_BASE)[0]==facts["start"]|1,"hardware-state composer stored ingress changed")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"hardware-state composer literals changed")
    hw_state_compose_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"stored_pointer":facts["stored_pointer"],"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"config_read_count":3,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=HW_STATE_DECODE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",HW_STATE_DECODE_SOURCE,[]),"hardware-state decoder Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],[]),"hardware-state decoder Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"hardware-state decoder cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"hardware-state decoder ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"hardware-state decoder gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"hardware-state decoder literals changed")
    hw_state_decode_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"portable_cases":16384,"primary_values":24,"secondary_values":12,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=SPOTMGR_STATE_TRANSITION;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",SPOTMGR_STATE_TRANSITION_SOURCE,expected_relocations),"SPOT-manager state-transition Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"SPOT-manager state-transition Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"SPOT-manager state-transition cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"SPOT-manager state-transition ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"SPOT-manager state-transition gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"SPOT-manager state-transition literals changed")
    spotmgr_state_transition_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"transition_delays":[50,200,2000],"special_states":[1,5,8,12,14,15,17],"hardware_validation":"blocked by unavailable physical evidence"}

    facts=DFU_IMAGE_CRC;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",DFU_IMAGE_CRC_SOURCE,expected_relocations),"DFU image CRC Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"DFU image CRC Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    require(sha256(stock)==facts["sha256"],"DFU image CRC stock changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"DFU image CRC ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"DFU image CRC gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"DFU image CRC literals changed")
    dfu_image_crc_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"header_bytes_skipped":8,"payload_size_mask":0x00FFFFFF,"short_reads_are_logged":True,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=DFU_PAYLOAD_PROGRAM;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",DFU_PAYLOAD_PROGRAM_SOURCE,expected_relocations),"DFU payload programmer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"DFU payload programmer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    require(sha256(stock)==facts["sha256"],"DFU payload programmer stock changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"DFU payload programmer ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"DFU payload programmer gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"DFU payload programmer literals changed")
    dfu_payload_program_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"header_bytes_skipped":32,"payload_size_mask":0x00FFFFFF,"indirect_program_callback":True,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=DFU_SERVICE_TASK;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]];observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",DFU_SERVICE_TASK_SOURCE,expected_relocations),"DFU service Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"DFU service Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];require(sha256(stock)==facts["sha256"],"DFU service stock changed");require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"DFU service ingress changed");require(struct.pack("<I",facts["start"]|1)not in boot,"DFU service gained stored ingress");require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"DFU service literals changed")
    dfu_service_task_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"header_bytes":32,"queue_command":1,"vector_ready_mask":0x20000000,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=STATE_REGISTER_INITIALIZE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",STATE_REGISTER_INITIALIZE_SOURCE,expected_relocations),"state-register initializer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"state-register initializer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"state-register initializer cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"state-register initializer ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"state-register initializer gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"state-register initializer literals changed")
    state_register_initialize_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"delay_sequence_us":[5,10],"power_mask":0xF0000000,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=HW_CONTEXT_INITIALIZE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",HW_CONTEXT_INITIALIZE_SOURCE,expected_relocations),"hardware-context initializer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"hardware-context initializer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"hardware-context initializer cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"hardware-context initializer ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"hardware-context initializer gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"hardware-context initializer literals changed")
    hw_context_initialize_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"slot_stride":72,"primary_profile_words":3,"secondary_profile_words":2,"hardware_validation":"blocked by unavailable physical evidence"}

    facts = HW_PROFILE_APPLY
    leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]]
    linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",HW_PROFILE_APPLY_SOURCE,expected_relocations),"hardware-profile Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"hardware-profile Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"],"hardware-profile stock changed")
    require(sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"hardware-profile main analogue changed")
    require(direct_callers(boot,facts["start"])==facts["callers"],"hardware-profile callers changed")
    require(all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"hardware-profile interior gained ingress")
    require(struct.pack("<I",facts["start"]|1)not in boot,"hardware-profile gained stored ingress")
    require(struct.unpack_from("<II",boot,0x42F17C-BOOT_BASE)==(0x01AFAFAF,0x40038000),"hardware-profile literals changed")
    hw_profile_apply_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"profile_fields":7,"published_register":0x40038000,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=REGISTER_PROFILE_TRANSFER;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",REGISTER_PROFILE_TRANSFER_SOURCE,expected_relocations),"register-profile transfer Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"register-profile transfer Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"register-profile transfer cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"register-profile transfer ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"register-profile transfer gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"register-profile transfer literals changed")
    register_profile_transfer_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"profile_words":13,"supported_operations":[0,1,2],"hardware_validation":"blocked by unavailable physical evidence"}

    facts=EVENT_VALUE_PROFILE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",EVENT_VALUE_PROFILE_SOURCE,expected_relocations),"event-value profile Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"event-value profile Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"event-value profile cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"event-value profile ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"event-value profile gained stored ingress")
    require(all(struct.unpack_from("<I",boot,a-BOOT_BASE)[0]==v for a,v in facts["literals"]),"event-value profile literals changed")
    event_value_profile_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"shared_literals":[{"address":a,"value":v}for a,v in facts["literals"]],"settle_delay_cycles":15,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=HW_REGISTER_PROFILE_RESTORE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",HW_REGISTER_PROFILE_RESTORE_SOURCE,expected_relocations),"register-profile restore Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"register-profile restore Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE];analogue=main[facts["main_start"]-MAIN_BASE:facts["main_start"]-MAIN_BASE+size]
    require(sha256(stock)==facts["sha256"] and sum(a==b for a,b in zip(stock,analogue))==facts["identical_main_bytes"],"register-profile restore cross-image body changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"register-profile restore ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"register-profile restore gained stored ingress")
    hw_register_profile_restore_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"main_analogue":facts["main_start"],"identical_main_bytes":facts["identical_main_bytes"],"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"hardware_validation":"blocked by unavailable physical evidence"}

    facts=CHUNKED_SOURCE_COMPARE;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",CHUNKED_SOURCE_COMPARE_SOURCE,expected_relocations),"chunked source-comparison Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"chunked source-comparison Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    require(sha256(stock)==facts["sha256"],"chunked source-comparison stock changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"chunked source-comparison ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"chunked source-comparison gained stored ingress")
    chunked_source_compare_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"chunk_bytes":4096,"hardware_validation":"blocked by unavailable physical evidence"}

    facts=MODE_APPLY;leaf=configured[facts["function"]];linux=leaf["toolchain_profiles"]["linux-clang"];size=facts["end"]-facts["start"]
    expected_relocations=[(o,"R_ARM_THM_CALL",n,"STT_NOTYPE",t)for o,n,t in facts["relocations"]]
    observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in leaf["relocations"]];linux_observed=[(x["offset"],x["type"],x["symbol"],x["symbol_type"],x["target_address"])for x in linux["relocations"]]
    require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["stock"]["sha256"],leaf["source"]["license"],ROOT/leaf["source"]["path"],observed)==(facts["start"],size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],"MIT",MODE_APPLY_SOURCE,expected_relocations),"mode-apply Apple registration changed")
    require((linux["expected"]["size"],linux["expected"]["sha256"],linux["expected"]["unrelocated_sha256"],linux["stock"]["sha256"],linux_observed)==(size,facts["sha256"],facts["unrelocated_sha256"],facts["sha256"],expected_relocations),"mode-apply Linux registration changed")
    stock=boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]
    require(sha256(stock)==facts["sha256"],"mode-apply stock changed")
    require(direct_callers(boot,facts["start"])==facts["callers"] and all(direct_callers(boot,a)==()for a in range(facts["start"]+2,facts["end"],2)),"mode-apply ingress changed")
    require(struct.pack("<I",facts["start"]|1)not in boot,"mode-apply gained stored ingress")
    literal_address,literal_value=facts["state_literal"]
    require(struct.unpack_from("<I",boot,literal_address-BOOT_BASE)[0]==literal_value,"mode-apply shared state literal changed")
    mode_apply_result={"function":facts["function"],"start":facts["start"],"end_exclusive":facts["end"],"source_bytes_by_profile":{"apple-clang":size,"linux-clang":size},"direct_call_sites":list(facts["callers"]),"provider_edges":[{"offset":o,"target_address":t}for o,_n,t in facts["relocations"]],"state_address":literal_value,"direct_service_routes":{"1":0x81,"2":0x7D,"3":0x80,"4":0x8E,"8":0x92},"aggregate_modes":[6,7,9],"hardware_validation":"blocked by unavailable physical evidence"}

    control_wrapper_results = []
    for facts in CONTROL_WRAPPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"]
        ]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 CONTROL_WRAPPERS_SOURCE, expected_relocations),
                f"control-wrapper Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"control-wrapper Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"control-wrapper stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"control-wrapper caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"control-wrapper interior gained ingress: {facts['function']}")
        control_wrapper_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    context_lifecycle_results = []
    for facts in CONTEXT_LIFECYCLE:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"]
        ]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 CONTEXT_LIFECYCLE_SOURCE, expected_relocations),
                f"context-lifecycle Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"context-lifecycle Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"context-lifecycle stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"context-lifecycle caller topology changed: {facts['function']}")
        pointer = facts["stored_pointer"]
        if pointer is not None:
            require(boot[pointer - BOOT_BASE:pointer - BOOT_BASE + 4] ==
                    struct.pack("<I", facts["start"] | 1),
                    f"context-lifecycle stored ingress changed: {facts['function']}")
        context_lifecycle_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "stored_pointer": pointer,
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    event_control_wrapper_results = []
    for facts in EVENT_CONTROL_WRAPPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        offset, symbol, target = facts["relocation"]
        expected_relocation = [(offset, "R_ARM_THM_CALL", symbol,
                                "STT_NOTYPE", target)]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 EVENT_CONTROL_WRAPPERS_SOURCE, expected_relocation),
                f"event-control wrapper Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocation),
                f"event-control wrapper Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"event-control wrapper stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"event-control wrapper caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"event-control wrapper interior gained ingress: {facts['function']}")
        event_control_wrapper_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edge": {"offset": offset, "target_address": target},
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    event_setup_results = []
    for facts in EVENT_SETUP_WRAPPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"]
        ]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 EVENT_SETUP_SOURCE, expected_relocations),
                f"event-runtime setup Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"event-runtime setup Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"event-runtime setup stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"event-runtime setup caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"event-runtime setup interior gained ingress: {facts['function']}")
        event_setup_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    event_state_results = []
    for facts in EVENT_STATE_SERVICES:
        leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
        observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
        linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", EVENT_STATE_SOURCE, expected_relocations), f"event-state Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), f"event-state Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], f"event-state stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"], f"event-state caller topology changed: {facts['function']}")
        pointer = facts["stored_pointer"]
        if pointer is not None:
            require(boot[pointer-BOOT_BASE:pointer-BOOT_BASE+4] == struct.pack("<I", facts["start"] | 1), f"event-state stored ingress changed: {facts['function']}")
        event_state_results.append({"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "stored_pointer": pointer, "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "hardware_validation": "blocked by unavailable physical evidence"})

    small_service_results = []
    for facts in SMALL_RUNTIME_SERVICES:
        leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
        observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
        linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", SMALL_SERVICES_SOURCE, expected_relocations), f"small-service Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), f"small-service Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], f"small-service stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"], f"small-service caller topology changed: {facts['function']}")
        pointer = facts["stored_pointer"]
        if pointer is not None:
            require(boot[pointer-BOOT_BASE:pointer-BOOT_BASE+4] == struct.pack("<I", facts["start"] | 1), f"small-service stored ingress changed: {facts['function']}")
        small_service_results.append({"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "stored_pointer": pointer, "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "hardware_validation": "blocked by unavailable physical evidence"})

    runtime_control_service_results = []
    for facts in RUNTIME_CONTROL_SERVICES:
        leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
        observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
        linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", CONTROL_SERVICES_SOURCE, expected_relocations), f"runtime control-service Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), f"runtime control-service Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], f"runtime control-service stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"], f"runtime control-service caller topology changed: {facts['function']}")
        pointer = facts["stored_pointer"]
        if pointer is not None:
            require(boot[pointer-BOOT_BASE:pointer-BOOT_BASE+4] == struct.pack("<I", facts["start"] | 1), f"runtime control-service stored ingress changed: {facts['function']}")
        runtime_control_service_results.append({"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "stored_pointer": pointer, "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "hardware_validation": "blocked by unavailable physical evidence"})

    facts = EVENT_SERVICE_LOOP; leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
    observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
    linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", EVENT_SERVICE_LOOP_SOURCE, expected_relocations), "event service-loop Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), "event service-loop Linux registration changed")
    require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], "event service-loop stock body changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"], "event service-loop direct ingress changed")
    pointer = facts["stored_pointer"]
    require(boot[pointer-BOOT_BASE:pointer-BOOT_BASE+4] == struct.pack("<I", facts["start"] | 1), "event service-loop stored ingress changed")
    event_service_loop_result = {"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "stored_pointer": pointer, "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "wait_timeout": 60_000, "hardware_validation": "blocked by unavailable physical evidence"}

    event_runtime_service_results = []
    for facts in EVENT_RUNTIME_SERVICES:
        leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
        observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
        linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", EVENT_RUNTIME_SERVICES_SOURCE, expected_relocations), f"event runtime-service Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), f"event runtime-service Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], f"event runtime-service stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"], f"event runtime-service direct ingress changed: {facts['function']}")
        event_runtime_service_results.append({"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "hardware_validation": "blocked by unavailable physical evidence"})

    control_orchestration_results = []
    for facts in CONTROL_ORCHESTRATION:
        leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
        observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
        linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", CONTROL_ORCHESTRATION_SOURCE, expected_relocations), f"control-orchestration Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), f"control-orchestration Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], f"control-orchestration stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"], f"control-orchestration direct ingress changed: {facts['function']}")
        pointer = facts["stored_pointer"]
        if pointer is not None: require(boot[pointer-BOOT_BASE:pointer-BOOT_BASE+4] == struct.pack("<I", facts["start"] | 1), f"control-orchestration stored ingress changed: {facts['function']}")
        control_orchestration_results.append({"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "stored_pointer": pointer, "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "hardware_validation": "blocked by unavailable physical evidence"})

    facts = CONTEXT_PUBLISH; leaf = configured[facts["function"]]; linux = leaf["toolchain_profiles"]["linux-clang"]
    size = facts["end"] - facts["start"]
    expected_relocations = [(o, "R_ARM_THM_CALL", s, "STT_NOTYPE", t) for o, s, t in facts["relocations"]]
    observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in leaf["relocations"]]
    linux_observed = [(x["offset"], x["type"], x["symbol"], x["symbol_type"], x["target_address"]) for x in linux["relocations"]]
    require((leaf["runtime_address"], leaf["expected"]["size"], leaf["expected"]["sha256"], leaf["expected"]["unrelocated_sha256"], leaf["stock"]["sha256"], leaf["source"]["license"], ROOT / leaf["source"]["path"], observed) == (facts["start"], size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], "MIT", CONTEXT_PUBLISH_SOURCE, expected_relocations), "runtime-context publisher Apple registration changed")
    require((linux["expected"]["size"], linux["expected"]["sha256"], linux["expected"]["unrelocated_sha256"], linux["stock"]["sha256"], linux_observed) == (size, facts["sha256"], facts["unrelocated_sha256"], facts["sha256"], expected_relocations), "runtime-context publisher Linux registration changed")
    require(sha256(boot[facts["start"]-BOOT_BASE:facts["end"]-BOOT_BASE]) == facts["sha256"], "runtime-context publisher stock body changed")
    require(direct_callers(boot, facts["start"]) == facts["callers"], "runtime-context publisher direct ingress changed")
    context_publish_result = {"function": facts["function"], "start": facts["start"], "end_exclusive": facts["end"], "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size}, "direct_call_sites": list(facts["callers"]), "provider_edges": [{"offset": o, "target_address": t} for o, _s, t in facts["relocations"]], "event_mask": 0x00400000, "hardware_validation": "blocked by unavailable physical evidence"}

    late_wrapper_results = []
    for facts in LATE_WRAPPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = [
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"]
        ]
        observed = [(item["offset"], item["type"], item["symbol"],
                     item["symbol_type"], item["target_address"])
                    for item in leaf["relocations"]]
        linux_observed = [(item["offset"], item["type"], item["symbol"],
                           item["symbol_type"], item["target_address"])
                          for item in linux["relocations"]]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 LATE_WRAPPERS_SOURCE, expected_relocations),
                f"late-wrapper Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"late-wrapper Linux registration changed: {facts['function']}")
        require(sha256(boot[facts["start"] - BOOT_BASE:
                            facts["end"] - BOOT_BASE]) == facts["sha256"],
                f"late-wrapper stock body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"late-wrapper caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"late-wrapper interior gained ingress: {facts['function']}")
        if facts["stored_pointer"] is not None:
            require(struct.unpack_from("<I", boot,
                    facts["stored_pointer"] - BOOT_BASE)[0] == facts["start"] | 1,
                    f"late-wrapper stored ingress changed: {facts['function']}")
        late_wrapper_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "stored_pointer": facts["stored_pointer"],
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "hardware_validation": "blocked by unavailable physical evidence",
        })

    noop_results = []
    for facts in NOOP_CALLBACKS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"], leaf["stock"]["sha256"],
                 leaf["source"]["license"], ROOT / leaf["source"]["path"],
                 leaf["relocations"]) ==
                (facts["start"], 2, NOOP_CALLBACK_SHA, NOOP_CALLBACK_SHA,
                 "MIT", NOOP_CALLBACKS_SOURCE, []),
                f"no-op callback Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (2, NOOP_CALLBACK_SHA, NOOP_CALLBACK_SHA, []),
                f"no-op callback Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        require(stock == b"\x70\x47" and sha256(stock) == NOOP_CALLBACK_SHA,
                f"no-op callback body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"no-op callback caller topology changed: {facts['function']}")
        require(struct.pack("<I", facts["start"] | 1) not in boot,
                f"no-op callback gained stored ingress: {facts['function']}")
        noop_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": 2, "linux-clang": 2},
            "direct_call_sites": list(facts["callers"]),
            "semantic_effect": "none",
        })

    alignment_leaf = configured[ALIGNMENT_DISPATCH["function"]]
    alignment_linux = alignment_leaf["toolchain_profiles"]["linux-clang"]
    alignment_relocations = tuple(
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in ALIGNMENT_DISPATCH["relocations"])
    require((alignment_leaf["runtime_address"],
             alignment_leaf["expected"]["size"],
             alignment_leaf["expected"]["sha256"],
             alignment_leaf["expected"]["unrelocated_sha256"],
             alignment_leaf["stock"]["sha256"],
             alignment_leaf["source"]["license"],
             ROOT / alignment_leaf["source"]["path"],
             tuple((item["offset"], item["type"], item["symbol"],
                    item["symbol_type"], item["target_address"])
                   for item in alignment_leaf["relocations"])) ==
            (ALIGNMENT_DISPATCH["start"], 26, ALIGNMENT_DISPATCH["sha256"],
             ALIGNMENT_DISPATCH["unrelocated_sha256"],
             ALIGNMENT_DISPATCH["sha256"], "MIT", ALIGNMENT_DISPATCH_SOURCE,
             alignment_relocations),
            "alignment-dispatch Apple registration changed")
    require((alignment_linux["expected"]["size"],
             alignment_linux["expected"]["sha256"],
             alignment_linux["expected"]["unrelocated_sha256"],
             alignment_linux["stock"]["sha256"],
             tuple((item["offset"], item["type"], item["symbol"],
                    item["symbol_type"], item["target_address"])
                   for item in alignment_linux["relocations"])) ==
            (26, ALIGNMENT_DISPATCH["sha256"],
             ALIGNMENT_DISPATCH["unrelocated_sha256"],
             ALIGNMENT_DISPATCH["sha256"], alignment_relocations),
            "alignment-dispatch Linux registration changed")
    alignment_stock = boot[
        ALIGNMENT_DISPATCH["start"] - BOOT_BASE:
        ALIGNMENT_DISPATCH["end"] - BOOT_BASE]
    alignment_main = main[
        ALIGNMENT_DISPATCH["main_start"] - MAIN_BASE:
        ALIGNMENT_DISPATCH["main_start"] - MAIN_BASE + len(alignment_stock)]
    require(alignment_stock == alignment_main and
            sha256(alignment_stock) == ALIGNMENT_DISPATCH["sha256"],
            "alignment-dispatch Apollo-main body changed")
    require(direct_callers(boot, ALIGNMENT_DISPATCH["start"]) ==
            ALIGNMENT_DISPATCH["callers"],
            "alignment-dispatch caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(ALIGNMENT_DISPATCH["start"] + 2,
                                     ALIGNMENT_DISPATCH["end"], 2)),
            "alignment-dispatch interior gained ingress")
    require(struct.pack("<I", ALIGNMENT_DISPATCH["start"] | 1) not in boot,
            "alignment-dispatch gained stored ingress")
    for payload, base, (address, value) in (
        (boot, BOOT_BASE, ALIGNMENT_DISPATCH["literal"]),
        (main, MAIN_BASE, ALIGNMENT_DISPATCH["main_literal"]),
    ):
        require(struct.unpack_from("<I", payload, address - base)[0] == value,
                f"alignment-dispatch literal changed at {address:#x}")
    alignment_dispatch_result = {
        "function": ALIGNMENT_DISPATCH["function"],
        "start": ALIGNMENT_DISPATCH["start"],
        "end_exclusive": ALIGNMENT_DISPATCH["end"],
        "source_bytes_by_profile": {"apple-clang": 26, "linux-clang": 26},
        "direct_call_sites": list(ALIGNMENT_DISPATCH["callers"]),
        "provider_edges": [{"offset": offset, "target_address": target}
                           for offset, _symbol, target in
                           ALIGNMENT_DISPATCH["relocations"]],
        "main_analogue": ALIGNMENT_DISPATCH["main_start"],
        "error_code": ALIGNMENT_DISPATCH["literal"][1],
        "required_length_alignment": 16,
        "required_destination_alignment": 4,
        "portable_rejection_classes": 63,
    }

    guarded_leaf = configured[GUARDED_CALL["function"]]
    guarded_linux = guarded_leaf["toolchain_profiles"]["linux-clang"]
    require((guarded_leaf["runtime_address"], guarded_leaf["expected"]["size"],
             guarded_leaf["expected"]["sha256"],
             guarded_leaf["expected"]["unrelocated_sha256"],
             guarded_leaf["stock"]["sha256"],
             guarded_leaf["source"]["license"],
             ROOT / guarded_leaf["source"]["path"], guarded_leaf["relocations"]) ==
            (GUARDED_CALL["start"], 30, GUARDED_CALL["sha256"],
             GUARDED_CALL["unrelocated_sha256"], GUARDED_CALL["sha256"],
             "MIT", GUARDED_CALL_SOURCE, []),
            "guarded-call Apple registration changed")
    require((guarded_linux["expected"]["size"],
             guarded_linux["expected"]["sha256"],
             guarded_linux["expected"]["unrelocated_sha256"],
             guarded_linux["stock"]["sha256"], guarded_linux["relocations"]) ==
            (30, GUARDED_CALL["sha256"], GUARDED_CALL["unrelocated_sha256"],
             GUARDED_CALL["sha256"], []),
            "guarded-call Linux registration changed")
    guarded_stock = boot[GUARDED_CALL["start"] - BOOT_BASE:
                         GUARDED_CALL["end"] - BOOT_BASE]
    guarded_main = main[GUARDED_CALL["main_start"] - MAIN_BASE:
                        GUARDED_CALL["main_start"] - MAIN_BASE + len(guarded_stock)]
    require(guarded_stock == guarded_main and
            sha256(guarded_stock) == GUARDED_CALL["sha256"],
            "guarded-call Apollo-main body changed")
    require(direct_callers(boot, GUARDED_CALL["start"]) == GUARDED_CALL["callers"],
            "guarded-call caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(GUARDED_CALL["start"] + 2,
                                     GUARDED_CALL["end"], 2)),
            "guarded-call interior gained ingress")
    require(struct.pack("<I", GUARDED_CALL["start"] | 1) not in boot,
            "guarded-call gained stored ingress")
    for payload, base, literals in (
        (boot, BOOT_BASE, GUARDED_CALL["literals"]),
        (main, MAIN_BASE, GUARDED_CALL["main_literals"]),
    ):
        for address, value in literals:
            require(struct.unpack_from("<I", payload, address - base)[0] == value,
                    f"guarded-call literal changed at {address:#x}")
    guarded_call_result = {
        "function": GUARDED_CALL["function"], "start": GUARDED_CALL["start"],
        "end_exclusive": GUARDED_CALL["end"],
        "source_bytes_by_profile": {"apple-clang": 30, "linux-clang": 30},
        "direct_call_sites": list(GUARDED_CALL["callers"]),
        "main_analogue": GUARDED_CALL["main_start"],
        "control_base": GUARDED_CALL["literals"][0][1],
        "status_address": GUARDED_CALL["literals"][1][1],
        "ordered_cleanup_writes": [
            {"offset": 0, "value": 0xC3},
            {"offset": 0x1C, "value": 0},
            {"offset": 0, "value": 0},
        ],
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    event_leaf = configured[EVENT_DISPATCH["function"]]
    event_linux = event_leaf["toolchain_profiles"]["linux-clang"]
    event_relocations = tuple(
        (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
        for offset, symbol, target in EVENT_DISPATCH["relocations"])
    require((event_leaf["runtime_address"], event_leaf["expected"]["size"],
             event_leaf["expected"]["sha256"],
             event_leaf["expected"]["unrelocated_sha256"],
             event_leaf["stock"]["sha256"], event_leaf["source"]["license"],
             ROOT / event_leaf["source"]["path"],
             tuple((item["offset"], item["type"], item["symbol"],
                    item["symbol_type"], item["target_address"])
                   for item in event_leaf["relocations"])) ==
            (EVENT_DISPATCH["start"], 76, EVENT_DISPATCH["sha256"],
             EVENT_DISPATCH["unrelocated_sha256"], EVENT_DISPATCH["sha256"],
             "MIT", EVENT_DISPATCH_SOURCE, event_relocations),
            "event-dispatch Apple registration changed")
    require((event_linux["expected"]["size"], event_linux["expected"]["sha256"],
             event_linux["expected"]["unrelocated_sha256"],
             event_linux["stock"]["sha256"],
             tuple((item["offset"], item["type"], item["symbol"],
                    item["symbol_type"], item["target_address"])
                   for item in event_linux["relocations"])) ==
            (76, EVENT_DISPATCH["sha256"],
             EVENT_DISPATCH["unrelocated_sha256"], EVENT_DISPATCH["sha256"],
             event_relocations),
            "event-dispatch Linux registration changed")
    event_stock = boot[EVENT_DISPATCH["start"] - BOOT_BASE:
                       EVENT_DISPATCH["end"] - BOOT_BASE]
    event_main = main[EVENT_DISPATCH["main_start"] - MAIN_BASE:
                      EVENT_DISPATCH["main_start"] - MAIN_BASE + len(event_stock)]
    require(event_stock == event_main and sha256(event_stock) == EVENT_DISPATCH["sha256"],
            "event-dispatch Apollo-main body changed")
    require(direct_callers(boot, EVENT_DISPATCH["start"]) == (),
            "event-dispatch gained direct ingress")
    require(struct.unpack_from("<I", boot,
                               EVENT_DISPATCH["stored_pointer"] - BOOT_BASE)[0] ==
            EVENT_DISPATCH["start"] | 1,
            "event-dispatch stored ingress changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(EVENT_DISPATCH["start"] + 2,
                                     EVENT_DISPATCH["end"], 2)),
            "event-dispatch interior gained ingress")
    for payload, base, literals in (
        (boot, BOOT_BASE, EVENT_DISPATCH["literals"]),
        (main, MAIN_BASE, EVENT_DISPATCH["main_literals"]),
    ):
        for address, value in literals:
            require(struct.unpack_from("<I", payload, address - base)[0] == value,
                    f"event-dispatch literal changed at {address:#x}")
    event_dispatch_result = {
        "function": EVENT_DISPATCH["function"], "start": EVENT_DISPATCH["start"],
        "end_exclusive": EVENT_DISPATCH["end"],
        "source_bytes_by_profile": {"apple-clang": 76, "linux-clang": 76},
        "stored_entry_pointer": EVENT_DISPATCH["stored_pointer"],
        "provider_edges": [{"offset": offset, "target_address": target}
                           for offset, _symbol, target in EVENT_DISPATCH["relocations"]],
        "main_analogue": EVENT_DISPATCH["main_start"],
        "event_values_tested": 256, "event_selector_width_bits": 8,
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    hw_handle_results = []
    for facts in HW_HANDLE_SERVICES:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], leaf["relocations"]) ==
                (facts["start"], size, facts["sha256"], facts["sha256"],
                 facts["sha256"], "MIT", HW_HANDLE_SOURCE, []),
                f"hardware-handle Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
                f"hardware-handle Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"hardware-handle Apollo-main body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"hardware-handle caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"hardware-handle interior gained ingress: {facts['function']}")
        require(struct.pack("<I", facts["start"] | 1) not in boot,
                f"hardware-handle gained stored ingress: {facts['function']}")
        hw_handle_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "main_analogue": facts["main_start"],
        })
    for payload, base, literals in (
        (boot, BOOT_BASE, HW_HANDLE_LITERALS),
        (main, MAIN_BASE, HW_HANDLE_MAIN_LITERALS),
    ):
        for address, value in literals:
            require(struct.unpack_from("<I", payload, address - base)[0] == value,
                    f"hardware-handle literal changed at {address:#x}")

    command_leaf = configured[HW_COMMAND["function"]]
    command_linux = command_leaf["toolchain_profiles"]["linux-clang"]
    require((command_leaf["runtime_address"], command_leaf["expected"]["size"],
             command_leaf["expected"]["sha256"],
             command_leaf["expected"]["unrelocated_sha256"],
             command_leaf["stock"]["sha256"], command_leaf["source"]["license"],
             ROOT / command_leaf["source"]["path"], command_leaf["relocations"]) ==
            (HW_COMMAND["start"], 32, HW_COMMAND["sha256"], HW_COMMAND["sha256"],
             HW_COMMAND["sha256"], "MIT", HW_COMMAND_SOURCE, []),
            "hardware-handle command Apple registration changed")
    require((command_linux["expected"]["size"],
             command_linux["expected"]["sha256"],
             command_linux["expected"]["unrelocated_sha256"],
             command_linux["stock"]["sha256"], command_linux["relocations"]) ==
            (32, HW_COMMAND["sha256"], HW_COMMAND["sha256"],
             HW_COMMAND["sha256"], []),
            "hardware-handle command Linux registration changed")
    command_stock = boot[HW_COMMAND["start"] - BOOT_BASE:
                         HW_COMMAND["end"] - BOOT_BASE]
    command_main = main[HW_COMMAND["main_start"] - MAIN_BASE:
                        HW_COMMAND["main_start"] - MAIN_BASE + 32]
    require(command_stock == command_main and
            sha256(command_stock) == HW_COMMAND["sha256"],
            "hardware-handle command Apollo-main body changed")
    require(direct_callers(boot, HW_COMMAND["start"]) == HW_COMMAND["callers"],
            "hardware-handle command caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(HW_COMMAND["start"] + 2, HW_COMMAND["end"], 2)),
            "hardware-handle command interior gained ingress")
    for payload, base, literals in (
        (boot, BOOT_BASE, HW_COMMAND["literals"]),
        (main, MAIN_BASE, HW_COMMAND["main_literals"]),
    ):
        for address, value in literals:
            require(struct.unpack_from("<I", payload, address - base)[0] == value,
                    f"hardware-handle command literal changed at {address:#x}")
    hw_command_result = {
        "function": HW_COMMAND["function"], "start": HW_COMMAND["start"],
        "end_exclusive": HW_COMMAND["end"],
        "source_bytes_by_profile": {"apple-clang": 32, "linux-clang": 32},
        "direct_call_sites": list(HW_COMMAND["callers"]),
        "main_analogue": HW_COMMAND["main_start"], "command_value": 55,
        "command_address": HW_COMMAND["literals"][1][1],
        "hardware_validation": "blocked by unavailable physical evidence",
    }

    hw_channel_activate_results = []
    for facts in HW_CHANNEL_ACTIVATE:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], leaf["relocations"]) ==
                (facts["start"], size, facts["sha256"], facts["sha256"],
                 facts["sha256"], "MIT", facts["source"], []),
                f"channel/activation Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux["relocations"]) ==
                (size, facts["sha256"], facts["sha256"], facts["sha256"], []),
                f"channel/activation Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"channel/activation Apollo-main body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"channel/activation caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"channel/activation interior gained ingress: {facts['function']}")
        hw_channel_activate_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "main_analogue": facts["main_start"],
            "portable_cases": facts["cases"],
            "hardware_validation": "blocked by unavailable physical evidence",
        })
    for payload, base, literals in (
        (boot, BOOT_BASE, ((0x0042F154, 0x2002702C), (0x0042F17C, 0x01AFAFAF),
                          (0x0042F180, 0x40038000), (0x0042F184, 0x4003800C))),
        (main, MAIN_BASE, ((0x0055E1D0, 0x20074248), (0x0055E1F8, 0x01AFAFAF),
                          (0x0055E1FC, 0x40038000), (0x0055E200, 0x4003800C))),
    ):
        for address, value in literals:
            require(struct.unpack_from("<I", payload, address - base)[0] == value,
                    f"channel/activation literal changed at {address:#x}")

    hw_config_enumerate_results = []
    for facts in HW_CONFIG_ENUMERATE:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        relocations = tuple(
            (offset, "R_ARM_THM_CALL", symbol, symbol_type, target)
            for offset, symbol, target, symbol_type in facts["relocations"]
        )
        observed = tuple((item["offset"], item["type"], item["symbol"],
                          item["symbol_type"], item["target_address"])
                         for item in leaf["relocations"])
        linux_observed = tuple((item["offset"], item["type"], item["symbol"],
                                item["symbol_type"], item["target_address"])
                               for item in linux["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"], observed) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 HW_CONFIG_ENUMERATE_SOURCE, relocations),
                f"hardware configuration/enumeration Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"], linux_observed) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], relocations),
                f"hardware configuration/enumeration Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"hardware configuration/enumeration main body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"hardware configuration/enumeration caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"hardware configuration/enumeration interior gained ingress: {facts['function']}")
        hw_config_enumerate_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target, _type in facts["relocations"]],
            "main_analogue": facts["main_start"], "portable_cases": facts["cases"],
            "hardware_validation": "blocked by unavailable physical evidence",
        })
    for address, value in (
        (0x0042F17C, 0x01AFAFAF), (0x0042F18C, 0x4003802C),
        (0x0042F190, 0x40038030), (0x0042F194, 0x40038034),
        (0x0042F184, 0x4003800C), (0x0042F1A4, 0x4003803C),
    ):
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                f"hardware configuration/enumeration literal changed at {address:#x}")

    orphan_results = []
    for facts in ORPHAN_SERVICES:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        relocations = tuple((offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
                            for offset, symbol, target in facts["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in leaf["relocations"])) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 ORPHAN_SERVICES_SOURCE, relocations),
                f"unreferenced linked-service Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in linux["relocations"])) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], relocations),
                f"unreferenced linked-service Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"unreferenced linked-service main body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == () and
                struct.pack("<I", facts["start"] | 1) not in boot,
                f"unreferenced linked-service gained ingress: {facts['function']}")
        orphan_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "main_analogue": facts["main_start"], "authenticated_ingress": False,
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
        })

    startup_results = []
    for facts in STARTUP_SERVICES:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = tuple(
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in leaf["relocations"])) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 STARTUP_SERVICES_SOURCE, expected_relocations),
                f"startup-service Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in linux["relocations"])) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"startup-service Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"startup-service main analogue changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"startup-service caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"startup-service interior gained ingress: {facts['function']}")
        pointer = struct.pack("<I", facts["start"] | 1)
        if facts["stored_pointer"] is None:
            require(pointer not in boot,
                    f"startup-service gained stored ingress: {facts['function']}")
        else:
            require(struct.unpack_from(
                "<I", boot, facts["stored_pointer"] - BOOT_BASE)[0] ==
                    facts["start"] | 1,
                    f"startup-service stored ingress changed: {facts['function']}")
        for address, value in facts["literals"]:
            require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                    f"startup-service literal changed at {address:#x}")
        startup_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "stored_entry_pointer": facts["stored_pointer"],
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "main_analogue": facts["main_start"], "exact_main_bytes": size,
            "shared_literals": [{"address": address, "value": value}
                                for address, value in facts["literals"]],
        })

    startup_runtime_results = []
    for facts in STARTUP_RUNTIME:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        expected_relocations = tuple(
            (offset, "R_ARM_THM_CALL", symbol, "STT_NOTYPE", target)
            for offset, symbol, target in facts["relocations"])
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"],
                 leaf["expected"]["unrelocated_sha256"],
                 leaf["stock"]["sha256"], leaf["source"]["license"],
                 ROOT / leaf["source"]["path"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in leaf["relocations"])) ==
                (facts["start"], size, facts["sha256"],
                 facts["unrelocated_sha256"], facts["sha256"], "MIT",
                 STARTUP_RUNTIME_SOURCE, expected_relocations),
                f"startup-runtime Apple registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["expected"]["unrelocated_sha256"],
                 linux["stock"]["sha256"],
                 tuple((item["offset"], item["type"], item["symbol"],
                        item["symbol_type"], item["target_address"])
                       for item in linux["relocations"])) ==
                (size, facts["sha256"], facts["unrelocated_sha256"],
                 facts["sha256"], expected_relocations),
                f"startup-runtime Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(sha256(stock) == facts["sha256"] and
                sha256(analogue) == facts["main_sha256"],
                f"startup-runtime body changed: {facts['function']}")
        require(sum(left == right for left, right in zip(stock, analogue)) ==
                facts["identical_bytes"] and
                difference_runs(stock, analogue) == facts["difference_runs"],
                f"startup-runtime main topology changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"startup-runtime caller topology changed: {facts['function']}")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"startup-runtime interior gained ingress: {facts['function']}")
        require(struct.pack("<I", facts["start"] | 1) not in boot,
                f"startup-runtime gained stored ingress: {facts['function']}")
        startup_runtime_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "main_analogue": facts["main_start"],
            "identical_main_bytes": facts["identical_bytes"],
        })
    for address, value in STARTUP_RUNTIME_LITERALS:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                f"startup-runtime literal changed at {address:#x}")
    for address, value in STARTUP_RUNTIME_MAIN_LITERALS:
        require(struct.unpack_from("<I", main, address - MAIN_BASE)[0] == value,
                f"startup-runtime main literal changed at {address:#x}")

    domain_leaf = configured[SPOTMGR_INTERNAL_DOMAIN["function"]]
    domain_linux = domain_leaf["toolchain_profiles"]["linux-clang"]
    require((domain_leaf["runtime_address"], domain_leaf["expected"]["size"],
             domain_leaf["expected"]["sha256"],
             domain_leaf["expected"]["unrelocated_sha256"],
             domain_leaf["stock"]["sha256"], domain_leaf["source"]["license"],
             ROOT / domain_leaf["source"]["path"], domain_leaf["relocations"]) ==
            (SPOTMGR_INTERNAL_DOMAIN["start"], 22,
             SPOTMGR_INTERNAL_DOMAIN["sha256"],
             SPOTMGR_INTERNAL_DOMAIN["sha256"],
             SPOTMGR_INTERNAL_DOMAIN["sha256"], "BSD-3-Clause",
             SPOTMGR_INTERNAL_DOMAIN_SOURCE, []),
            "SPOT-manager internal-domain Apple registration changed")
    require((domain_linux["expected"]["size"],
             domain_linux["expected"]["sha256"],
             domain_linux["expected"]["unrelocated_sha256"],
             domain_linux["stock"]["sha256"], domain_linux["relocations"]) ==
            (22, SPOTMGR_INTERNAL_DOMAIN["sha256"],
             SPOTMGR_INTERNAL_DOMAIN["sha256"],
             SPOTMGR_INTERNAL_DOMAIN["sha256"], []),
            "SPOT-manager internal-domain Linux registration changed")
    domain_stock = boot[
        SPOTMGR_INTERNAL_DOMAIN["start"] - BOOT_BASE:
        SPOTMGR_INTERNAL_DOMAIN["end"] - BOOT_BASE]
    require(sha256(domain_stock) == SPOTMGR_INTERNAL_DOMAIN["sha256"],
            "SPOT-manager internal-domain stock body changed")
    domain_main = main[
        SPOTMGR_INTERNAL_DOMAIN["main_start"] - MAIN_BASE:
        SPOTMGR_INTERNAL_DOMAIN["main_start"] - MAIN_BASE + len(domain_stock)]
    require(sha256(domain_main) == SPOTMGR_INTERNAL_DOMAIN["main_sha256"],
            "SPOT-manager internal-domain Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(domain_stock, domain_main)) ==
            SPOTMGR_INTERNAL_DOMAIN["identical_bytes"],
            "SPOT-manager internal-domain cross-image identity changed")
    require(difference_runs(domain_stock, domain_main) ==
            SPOTMGR_INTERNAL_DOMAIN["difference_runs"],
            "SPOT-manager internal-domain difference topology changed")
    require(direct_callers(boot, SPOTMGR_INTERNAL_DOMAIN["start"]) ==
            SPOTMGR_INTERNAL_DOMAIN["callers"],
            "SPOT-manager internal-domain caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_INTERNAL_DOMAIN["start"] + 2,
                                     SPOTMGR_INTERNAL_DOMAIN["end"], 2)),
            "SPOT-manager internal-domain interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_INTERNAL_DOMAIN["start"],
                                     SPOTMGR_INTERNAL_DOMAIN["end"], 2)),
            "SPOT-manager internal-domain gained a stored entry pointer")
    for address, value in SPOTMGR_INTERNAL_DOMAIN["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager internal-domain shared literal changed")
    internal_domain_result = {
        "function": SPOTMGR_INTERNAL_DOMAIN["function"],
        "start": SPOTMGR_INTERNAL_DOMAIN["start"],
        "end_exclusive": SPOTMGR_INTERNAL_DOMAIN["end"],
        "source_bytes_by_profile": {"apple-clang": 22, "linux-clang": 22},
        "direct_call_sites": list(SPOTMGR_INTERNAL_DOMAIN["callers"]),
        "main_analogue": SPOTMGR_INTERNAL_DOMAIN["main_start"],
        "shared_flag": SPOTMGR_INTERNAL_DOMAIN["shared_literals"][0][1],
        "requested_deep_sleep_state": 2,
        "prior_high_performance_state": 1,
    }

    ton_leaf = configured[SPOTMGR_POWER_TON["function"]]
    ton_linux = ton_leaf["toolchain_profiles"]["linux-clang"]
    require((ton_leaf["runtime_address"], ton_leaf["expected"]["size"],
             ton_leaf["expected"]["sha256"],
             ton_leaf["expected"]["unrelocated_sha256"],
             ton_leaf["stock"]["sha256"], ton_leaf["source"]["license"],
             ROOT / ton_leaf["source"]["path"], ton_leaf["relocations"]) ==
            (SPOTMGR_POWER_TON["start"], 232, SPOTMGR_POWER_TON["sha256"],
             SPOTMGR_POWER_TON["sha256"], SPOTMGR_POWER_TON["sha256"],
             "BSD-3-Clause", SPOTMGR_POWER_TON_SOURCE, []),
            "SPOT-manager Ton Apple registration changed")
    require((ton_linux["expected"]["size"],
             ton_linux["expected"]["sha256"],
             ton_linux["expected"]["unrelocated_sha256"],
             ton_linux["stock"]["sha256"], ton_linux["relocations"]) ==
            (232, SPOTMGR_POWER_TON["sha256"],
             SPOTMGR_POWER_TON["sha256"],
             SPOTMGR_POWER_TON["sha256"], []),
            "SPOT-manager Ton Linux registration changed")
    ton_stock = boot[SPOTMGR_POWER_TON["start"] - BOOT_BASE:
                     SPOTMGR_POWER_TON["end"] - BOOT_BASE]
    require(sha256(ton_stock) == SPOTMGR_POWER_TON["sha256"],
            "SPOT-manager Ton stock body changed")
    ton_main = main[SPOTMGR_POWER_TON["main_start"] - MAIN_BASE:
                    SPOTMGR_POWER_TON["main_start"] - MAIN_BASE + len(ton_stock)]
    require(sha256(ton_main) == SPOTMGR_POWER_TON["main_sha256"],
            "SPOT-manager Ton Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(ton_stock, ton_main)) ==
            SPOTMGR_POWER_TON["identical_bytes"],
            "SPOT-manager Ton cross-image identity changed")
    require(difference_runs(ton_stock, ton_main) ==
            SPOTMGR_POWER_TON["difference_runs"],
            "SPOT-manager Ton cross-image topology changed")
    require(direct_callers(boot, SPOTMGR_POWER_TON["start"]) ==
            SPOTMGR_POWER_TON["callers"],
            "SPOT-manager Ton caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_POWER_TON["start"] + 2,
                                     SPOTMGR_POWER_TON["end"], 2)),
            "SPOT-manager Ton interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_POWER_TON["start"],
                                     SPOTMGR_POWER_TON["end"], 2)),
            "SPOT-manager Ton gained a stored entry pointer")
    for address, value in SPOTMGR_POWER_TON["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager Ton shared literal changed")
    power_ton_result = {
        "function": SPOTMGR_POWER_TON["function"],
        "start": SPOTMGR_POWER_TON["start"],
        "end_exclusive": SPOTMGR_POWER_TON["end"],
        "source_bytes_by_profile": {"apple-clang": 232, "linux-clang": 232},
        "direct_call_sites": list(SPOTMGR_POWER_TON["callers"]),
        "main_analogue": SPOTMGR_POWER_TON["main_start"],
        "identical_main_bytes": SPOTMGR_POWER_TON["identical_bytes"],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_POWER_TON["shared_literals"]
        ],
        "power_state_8_forced_ton_state": 7,
        "vddc_output_bit_offset": 25,
        "vddf_output_bit_offset": 8,
    }

    sequence_leaf = configured[SPOTMGR_STATE_SEQUENCE["function"]]
    sequence_linux = sequence_leaf["toolchain_profiles"]["linux-clang"]
    sequence_relocation = {
        "offset": SPOTMGR_STATE_SEQUENCE["relocation"][0],
        "type": "R_ARM_THM_CALL",
        "symbol": SPOTMGR_STATE_SEQUENCE["relocation"][1],
        "symbol_type": "STT_NOTYPE",
        "target_address": SPOTMGR_STATE_SEQUENCE["relocation"][2],
    }
    require(
        (sequence_leaf["runtime_address"], sequence_leaf["expected"]["size"],
         sequence_leaf["expected"]["sha256"],
         sequence_leaf["expected"]["unrelocated_sha256"],
         sequence_leaf["stock"]["sha256"], sequence_leaf["source"]["license"],
         ROOT / sequence_leaf["source"]["path"], sequence_leaf["relocations"])
        == (SPOTMGR_STATE_SEQUENCE["start"], 390,
            SPOTMGR_STATE_SEQUENCE["sha256"],
            SPOTMGR_STATE_SEQUENCE["unrelocated_sha256"],
            SPOTMGR_STATE_SEQUENCE["sha256"], "BSD-3-Clause",
            SPOTMGR_STATE_SEQUENCE_SOURCE, [sequence_relocation]),
        "SPOT-manager state-sequence Apple registration changed",
    )
    require(
        (sequence_linux["expected"]["size"],
         sequence_linux["expected"]["sha256"],
         sequence_linux["expected"]["unrelocated_sha256"],
         sequence_linux["stock"]["sha256"], sequence_linux["relocations"])
        == (390, SPOTMGR_STATE_SEQUENCE["sha256"],
            SPOTMGR_STATE_SEQUENCE["unrelocated_sha256"],
            SPOTMGR_STATE_SEQUENCE["sha256"], [sequence_relocation]),
        "SPOT-manager state-sequence Linux registration changed",
    )
    sequence_stock = boot[
        SPOTMGR_STATE_SEQUENCE["start"] - BOOT_BASE:
        SPOTMGR_STATE_SEQUENCE["end"] - BOOT_BASE
    ]
    require(sha256(sequence_stock) == SPOTMGR_STATE_SEQUENCE["sha256"],
            "SPOT-manager state-sequence stock body changed")
    sequence_main = main[
        SPOTMGR_STATE_SEQUENCE["main_start"] - MAIN_BASE:
        SPOTMGR_STATE_SEQUENCE["main_start"] - MAIN_BASE + len(sequence_stock)
    ]
    require(sha256(sequence_main) == SPOTMGR_STATE_SEQUENCE["main_sha256"],
            "SPOT-manager state-sequence Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(sequence_stock, sequence_main)) ==
            SPOTMGR_STATE_SEQUENCE["identical_bytes"],
            "SPOT-manager state-sequence cross-image identity changed")
    require(difference_runs(sequence_stock, sequence_main) ==
            SPOTMGR_STATE_SEQUENCE["difference_runs"],
            "SPOT-manager state-sequence difference topology changed")
    require(direct_callers(boot, SPOTMGR_STATE_SEQUENCE["start"]) ==
            SPOTMGR_STATE_SEQUENCE["callers"],
            "SPOT-manager state-sequence caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_STATE_SEQUENCE["start"] + 2,
                                     SPOTMGR_STATE_SEQUENCE["end"], 2)),
            "SPOT-manager state-sequence interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_STATE_SEQUENCE["start"],
                                     SPOTMGR_STATE_SEQUENCE["end"], 2)),
            "SPOT-manager state-sequence gained a stored entry pointer")
    for address, value in SPOTMGR_STATE_SEQUENCE["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager state-sequence shared literal changed")
    sequence_table = boot[
        SPOTMGR_STATE_SEQUENCE["table_address"] - BOOT_BASE:
        SPOTMGR_STATE_SEQUENCE["table_address"] - BOOT_BASE + 28
    ]
    require(sha256(sequence_table) == SPOTMGR_STATE_SEQUENCE["table_sha256"],
            "SPOT-manager state-sequence table changed")
    require(struct.unpack_from(
        "<I", main,
        SPOTMGR_STATE_SEQUENCE["main_table_literal"] - MAIN_BASE
    )[0] == SPOTMGR_STATE_SEQUENCE["main_table_address"],
            "SPOT-manager state-sequence main table pointer changed")
    main_sequence_table = main[
        SPOTMGR_STATE_SEQUENCE["main_table_address"] - MAIN_BASE:
        SPOTMGR_STATE_SEQUENCE["main_table_address"] - MAIN_BASE + 28
    ]
    require(main_sequence_table == sequence_table,
            "SPOT-manager state-sequence cross-image table changed")
    state_sequence_result = {
        "function": SPOTMGR_STATE_SEQUENCE["function"],
        "start": SPOTMGR_STATE_SEQUENCE["start"],
        "end_exclusive": SPOTMGR_STATE_SEQUENCE["end"],
        "source_bytes_by_profile": {"apple-clang": 390, "linux-clang": 390},
        "direct_call_sites": list(SPOTMGR_STATE_SEQUENCE["callers"]),
        "provider_edge": {
            "offset": SPOTMGR_STATE_SEQUENCE["relocation"][0],
            "target_address": SPOTMGR_STATE_SEQUENCE["relocation"][2],
        },
        "main_analogue": SPOTMGR_STATE_SEQUENCE["main_start"],
        "identical_main_bytes": SPOTMGR_STATE_SEQUENCE["identical_bytes"],
        "transition_table_address": SPOTMGR_STATE_SEQUENCE["table_address"],
        "transition_table_sha256": SPOTMGR_STATE_SEQUENCE["table_sha256"],
        "valid_state_pairs_tested": 400,
    }

    temperature_leaf = configured[SPOTMGR_TEMPERATURE_TRANSITION["function"]]
    temperature_linux = temperature_leaf["toolchain_profiles"]["linux-clang"]
    temperature_relocations = [{
        "offset": offset,
        "type": "R_ARM_THM_CALL",
        "symbol": symbol,
        "symbol_type": "STT_NOTYPE",
        "target_address": target,
    } for offset, symbol, target in SPOTMGR_TEMPERATURE_TRANSITION["relocations"]]
    require(
        (temperature_leaf["runtime_address"], temperature_leaf["expected"]["size"],
         temperature_leaf["expected"]["sha256"],
         temperature_leaf["expected"]["unrelocated_sha256"],
         temperature_leaf["stock"]["sha256"],
         temperature_leaf["source"]["license"],
         ROOT / temperature_leaf["source"]["path"],
         temperature_leaf["relocations"])
        == (SPOTMGR_TEMPERATURE_TRANSITION["start"], 130,
            SPOTMGR_TEMPERATURE_TRANSITION["sha256"],
            SPOTMGR_TEMPERATURE_TRANSITION["unrelocated_sha256"],
            SPOTMGR_TEMPERATURE_TRANSITION["sha256"], "BSD-3-Clause",
            SPOTMGR_TEMPERATURE_TRANSITION_SOURCE, temperature_relocations),
        "SPOT-manager temperature Apple registration changed",
    )
    require(
        (temperature_linux["expected"]["size"],
         temperature_linux["expected"]["sha256"],
         temperature_linux["expected"]["unrelocated_sha256"],
         temperature_linux["stock"]["sha256"],
         temperature_linux["relocations"])
        == (130, SPOTMGR_TEMPERATURE_TRANSITION["sha256"],
            SPOTMGR_TEMPERATURE_TRANSITION["unrelocated_sha256"],
            SPOTMGR_TEMPERATURE_TRANSITION["sha256"], temperature_relocations),
        "SPOT-manager temperature Linux registration changed",
    )
    temperature_stock = boot[
        SPOTMGR_TEMPERATURE_TRANSITION["start"] - BOOT_BASE:
        SPOTMGR_TEMPERATURE_TRANSITION["end"] - BOOT_BASE
    ]
    require(sha256(temperature_stock) == SPOTMGR_TEMPERATURE_TRANSITION["sha256"],
            "SPOT-manager temperature stock body changed")
    temperature_main = main[
        SPOTMGR_TEMPERATURE_TRANSITION["main_start"] - MAIN_BASE:
        SPOTMGR_TEMPERATURE_TRANSITION["main_start"] - MAIN_BASE + len(temperature_stock)
    ]
    require(sha256(temperature_main) == SPOTMGR_TEMPERATURE_TRANSITION["main_sha256"],
            "SPOT-manager temperature Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(temperature_stock, temperature_main)) ==
            SPOTMGR_TEMPERATURE_TRANSITION["identical_bytes"],
            "SPOT-manager temperature cross-image identity changed")
    require(difference_runs(temperature_stock, temperature_main) ==
            SPOTMGR_TEMPERATURE_TRANSITION["difference_runs"],
            "SPOT-manager temperature difference topology changed")
    require(direct_callers(boot, SPOTMGR_TEMPERATURE_TRANSITION["start"]) ==
            SPOTMGR_TEMPERATURE_TRANSITION["callers"],
            "SPOT-manager temperature caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_TEMPERATURE_TRANSITION["start"] + 2,
                                     SPOTMGR_TEMPERATURE_TRANSITION["end"], 2)),
            "SPOT-manager temperature interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_TEMPERATURE_TRANSITION["start"],
                                     SPOTMGR_TEMPERATURE_TRANSITION["end"], 2)),
            "SPOT-manager temperature gained a stored entry pointer")
    for address, value in SPOTMGR_TEMPERATURE_TRANSITION["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager temperature shared literal changed")
    main_literal_address, main_literal_value = \
        SPOTMGR_TEMPERATURE_TRANSITION["main_shared_literal"]
    require(struct.unpack_from("<I", main, main_literal_address - MAIN_BASE)[0]
            == main_literal_value,
            "SPOT-manager temperature main shared literal changed")
    temperature_transition_result = {
        "function": SPOTMGR_TEMPERATURE_TRANSITION["function"],
        "start": SPOTMGR_TEMPERATURE_TRANSITION["start"],
        "end_exclusive": SPOTMGR_TEMPERATURE_TRANSITION["end"],
        "source_bytes_by_profile": {"apple-clang": 130, "linux-clang": 130},
        "direct_call_sites": list(SPOTMGR_TEMPERATURE_TRANSITION["callers"]),
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in
            SPOTMGR_TEMPERATURE_TRANSITION["relocations"]
        ],
        "callback_table_pointer": SPOTMGR_TEMPERATURE_TRANSITION["shared_literals"][0][1],
        "main_analogue": SPOTMGR_TEMPERATURE_TRANSITION["main_start"],
        "identical_main_bytes": SPOTMGR_TEMPERATURE_TRANSITION["identical_bytes"],
        "valid_state_pairs_tested": 400,
    }

    trims_leaf = configured[SPOTMGR_POWER_TRIMS["function"]]
    trims_linux = trims_leaf["toolchain_profiles"]["linux-clang"]
    trims_relocations = [{
        "offset": offset,
        "type": "R_ARM_THM_CALL",
        "symbol": symbol,
        "symbol_type": "STT_NOTYPE",
        "target_address": target,
    } for offset, symbol, target in SPOTMGR_POWER_TRIMS["relocations"]]
    require(
        (trims_leaf["runtime_address"], trims_leaf["expected"]["size"],
         trims_leaf["expected"]["sha256"],
         trims_leaf["expected"]["unrelocated_sha256"],
         trims_leaf["stock"]["sha256"], trims_leaf["source"]["license"],
         ROOT / trims_leaf["source"]["path"], trims_leaf["relocations"])
        == (SPOTMGR_POWER_TRIMS["start"], 138, SPOTMGR_POWER_TRIMS["sha256"],
            SPOTMGR_POWER_TRIMS["unrelocated_sha256"],
            SPOTMGR_POWER_TRIMS["sha256"], "BSD-3-Clause",
            SPOTMGR_POWER_TRIMS_SOURCE, trims_relocations),
        "SPOT-manager power-trims Apple registration changed",
    )
    require(
        (trims_linux["expected"]["size"], trims_linux["expected"]["sha256"],
         trims_linux["expected"]["unrelocated_sha256"],
         trims_linux["stock"]["sha256"], trims_linux["relocations"])
        == (138, SPOTMGR_POWER_TRIMS["sha256"],
            SPOTMGR_POWER_TRIMS["unrelocated_sha256"],
            SPOTMGR_POWER_TRIMS["sha256"], trims_relocations),
        "SPOT-manager power-trims Linux registration changed",
    )
    trims_stock = boot[
        SPOTMGR_POWER_TRIMS["start"] - BOOT_BASE:
        SPOTMGR_POWER_TRIMS["end"] - BOOT_BASE
    ]
    require(sha256(trims_stock) == SPOTMGR_POWER_TRIMS["sha256"],
            "SPOT-manager power-trims stock body changed")
    trims_main = main[
        SPOTMGR_POWER_TRIMS["main_start"] - MAIN_BASE:
        SPOTMGR_POWER_TRIMS["main_start"] - MAIN_BASE + len(trims_stock)
    ]
    require(sha256(trims_main) == SPOTMGR_POWER_TRIMS["main_sha256"],
            "SPOT-manager power-trims Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(trims_stock, trims_main)) ==
            SPOTMGR_POWER_TRIMS["identical_bytes"],
            "SPOT-manager power-trims cross-image identity changed")
    require(difference_runs(trims_stock, trims_main) ==
            SPOTMGR_POWER_TRIMS["difference_runs"],
            "SPOT-manager power-trims difference topology changed")
    require(direct_callers(boot, SPOTMGR_POWER_TRIMS["start"]) ==
            SPOTMGR_POWER_TRIMS["callers"],
            "SPOT-manager power-trims caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_POWER_TRIMS["start"] + 2,
                                     SPOTMGR_POWER_TRIMS["end"], 2)),
            "SPOT-manager power-trims interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_POWER_TRIMS["start"],
                                     SPOTMGR_POWER_TRIMS["end"], 2)),
            "SPOT-manager power-trims gained a stored entry pointer")
    for address, value in SPOTMGR_POWER_TRIMS["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager power-trims shared literal changed")
    trims_main_literal_address, trims_main_literal_value = \
        SPOTMGR_POWER_TRIMS["main_shared_literal"]
    require(struct.unpack_from(
        "<I", main, trims_main_literal_address - MAIN_BASE
    )[0] == trims_main_literal_value,
            "SPOT-manager power-trims main shared literal changed")
    power_trims_result = {
        "function": SPOTMGR_POWER_TRIMS["function"],
        "start": SPOTMGR_POWER_TRIMS["start"],
        "end_exclusive": SPOTMGR_POWER_TRIMS["end"],
        "source_bytes_by_profile": {"apple-clang": 138, "linux-clang": 138},
        "direct_call_sites": list(SPOTMGR_POWER_TRIMS["callers"]),
        "provider_edges": [
            {"offset": offset, "target_address": target}
            for offset, _symbol, target in SPOTMGR_POWER_TRIMS["relocations"]
        ],
        "callback_table_pointer": SPOTMGR_POWER_TRIMS["shared_literals"][0][1],
        "main_analogue": SPOTMGR_POWER_TRIMS["main_start"],
        "identical_main_bytes": SPOTMGR_POWER_TRIMS["identical_bytes"],
        "routes_tested": 800,
    }

    state_leaf = configured[SPOTMGR_POWER_STATE["function"]]
    state_linux = state_leaf["toolchain_profiles"]["linux-clang"]
    require(
        (state_leaf["runtime_address"], state_leaf["expected"]["size"],
         state_leaf["expected"]["sha256"],
         state_leaf["expected"]["unrelocated_sha256"],
         state_leaf["stock"]["sha256"], state_leaf["source"]["license"],
         ROOT / state_leaf["source"]["path"], state_leaf["relocations"])
        == (SPOTMGR_POWER_STATE["start"], 782,
            SPOTMGR_POWER_STATE["sha256"],
            SPOTMGR_POWER_STATE["unrelocated_sha256"],
            SPOTMGR_POWER_STATE["sha256"], "BSD-3-Clause",
            SPOTMGR_POWER_STATE_SOURCE, []),
        "SPOT-manager power-state Apple registration changed",
    )
    require(
        (state_linux["expected"]["size"], state_linux["expected"]["sha256"],
         state_linux["expected"]["unrelocated_sha256"],
         state_linux["stock"]["sha256"], state_linux["relocations"])
        == (782, SPOTMGR_POWER_STATE["sha256"],
            SPOTMGR_POWER_STATE["unrelocated_sha256"],
            SPOTMGR_POWER_STATE["sha256"], []),
        "SPOT-manager power-state Linux registration changed",
    )
    state_stock = boot[
        SPOTMGR_POWER_STATE["start"] - BOOT_BASE:
        SPOTMGR_POWER_STATE["end"] - BOOT_BASE
    ]
    require(sha256(state_stock) == SPOTMGR_POWER_STATE["sha256"],
            "SPOT-manager power-state stock body changed")
    state_main = main[
        SPOTMGR_POWER_STATE["main_start"] - MAIN_BASE:
        SPOTMGR_POWER_STATE["main_start"] - MAIN_BASE + len(state_stock)
    ]
    require(sha256(state_main) == SPOTMGR_POWER_STATE["main_sha256"],
            "SPOT-manager power-state Apollo-main analogue changed")
    require(sum(left == right for left, right in zip(state_stock, state_main)) ==
            SPOTMGR_POWER_STATE["identical_bytes"],
            "SPOT-manager power-state cross-image identity changed")
    require(difference_runs(state_stock, state_main) ==
            SPOTMGR_POWER_STATE["difference_runs"],
            "SPOT-manager power-state difference topology changed")
    require(direct_callers(boot, SPOTMGR_POWER_STATE["start"]) ==
            SPOTMGR_POWER_STATE["callers"],
            "SPOT-manager power-state caller topology changed")
    require(all(direct_callers(boot, address) == ()
                for address in range(SPOTMGR_POWER_STATE["start"] + 2,
                                     SPOTMGR_POWER_STATE["end"], 2)),
            "SPOT-manager power-state interior gained direct ingress")
    require(all(struct.pack("<I", address | 1) not in boot
                for address in range(SPOTMGR_POWER_STATE["start"],
                                     SPOTMGR_POWER_STATE["end"], 2)),
            "SPOT-manager power-state gained a stored entry pointer")
    for address, value in SPOTMGR_POWER_STATE["shared_literals"]:
        require(struct.unpack_from("<I", boot, address - BOOT_BASE)[0] == value,
                "SPOT-manager power-state shared literal changed")
    for address, value in SPOTMGR_POWER_STATE["main_shared_literals"]:
        require(struct.unpack_from("<I", main, address - MAIN_BASE)[0] == value,
                "SPOT-manager power-state main shared literal changed")
    power_state_result = {
        "function": SPOTMGR_POWER_STATE["function"],
        "start": SPOTMGR_POWER_STATE["start"],
        "end_exclusive": SPOTMGR_POWER_STATE["end"],
        "source_bytes_by_profile": {"apple-clang": 782, "linux-clang": 782},
        "direct_call_sites": list(SPOTMGR_POWER_STATE["callers"]),
        "provider_edges": [],
        "shared_literals": [
            {"address": address, "value": value}
            for address, value in SPOTMGR_POWER_STATE["shared_literals"]
        ],
        "main_analogue": SPOTMGR_POWER_STATE["main_start"],
        "identical_main_bytes": SPOTMGR_POWER_STATE["identical_bytes"],
        "host_cases_tested": 40_960,
    }

    update_profile_results = {}
    for label, facts, source_path, host_cases in (
        ("power_state_update", SPOTMGR_UPDATE, SPOTMGR_UPDATE_SOURCE, 23),
        ("profile_apply", SPOTMGR_PROFILE, SPOTMGR_PROFILE_SOURCE, 2),
        ("init", SPOTMGR_INIT, SPOTMGR_INIT_SOURCE, 3),
        ("temperature_init", SPOTMGR_TEMPERATURE_INIT,
         SPOTMGR_TEMPERATURE_INIT_SOURCE, 6),
        ("trim_commit", SPOTMGR_TRIM_COMMIT, SPOTMGR_TRIM_COMMIT_SOURCE, 4),
    ):
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        relocations = [{
            "offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
            "symbol_type": "STT_NOTYPE", "target_address": target,
        } for offset, symbol, target in facts["relocations"]]
        size = facts["end"] - facts["start"]
        require(
            (leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"],
             leaf["expected"]["unrelocated_sha256"],
             leaf["stock"]["sha256"], leaf["source"]["license"],
             ROOT / leaf["source"]["path"], leaf["relocations"])
            == (facts["start"], size, facts["sha256"],
                facts["unrelocated_sha256"], facts["sha256"],
                "BSD-3-Clause", source_path, relocations),
            f"SPOT-manager {label} Apple registration changed",
        )
        require(
            (linux["expected"]["size"], linux["expected"]["sha256"],
             linux["expected"]["unrelocated_sha256"],
             linux["stock"]["sha256"], linux["relocations"])
            == (size, facts["sha256"], facts["unrelocated_sha256"],
                facts["sha256"], relocations),
            f"SPOT-manager {label} Linux registration changed",
        )
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        require(sha256(stock) == facts["sha256"],
                f"SPOT-manager {label} stock body changed")
        require(direct_callers(boot, facts["start"]) == (),
                f"SPOT-manager {label} gained direct BL ingress")
        require(all(direct_callers(boot, address) == ()
                    for address in range(facts["start"] + 2, facts["end"], 2)),
                f"SPOT-manager {label} interior gained direct ingress")
        pointer_site, pointer_value = facts["dispatch_pointer"]
        require(struct.unpack_from("<I", boot, pointer_site - BOOT_BASE)[0] ==
                pointer_value,
                f"SPOT-manager {label} dispatch pointer changed")
        require(boot.count(struct.pack("<I", pointer_value)) == 1,
                f"SPOT-manager {label} dispatch ingress multiplicity changed")
        update_profile_results[label] = {
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size,
                                        "linux-clang": size},
            "dispatch_pointer_site": pointer_site,
            "provider_edges": [{"offset": offset, "target_address": target}
                               for offset, _symbol, target in facts["relocations"]],
            "host_route_classes_tested": host_cases,
        }

    range_leaf = configured[SPOTMGR_TEMPERATURE_RANGE["function"]]
    range_linux = range_leaf["toolchain_profiles"]["linux-clang"]
    require(
        (range_leaf["runtime_address"], range_leaf["expected"]["size"],
         range_leaf["expected"]["sha256"],
         range_leaf["expected"]["unrelocated_sha256"],
         range_leaf["stock"]["sha256"], range_leaf["source"]["license"],
         ROOT / range_leaf["source"]["path"], range_leaf["relocations"])
        == (SPOTMGR_TEMPERATURE_RANGE["start"], 120,
            SPOTMGR_TEMPERATURE_RANGE["sha256"],
            SPOTMGR_TEMPERATURE_RANGE["sha256"],
            SPOTMGR_TEMPERATURE_RANGE["sha256"], "BSD-3-Clause",
            SPOTMGR_TEMPERATURE_RANGE_SOURCE, []),
        "SPOT-manager temperature-range Apple registration changed",
    )
    require((range_linux["expected"]["size"],
             range_linux["expected"]["sha256"], range_linux["relocations"])
            == (120, SPOTMGR_TEMPERATURE_RANGE["sha256"], []),
            "SPOT-manager temperature-range Linux registration changed")
    range_stock = boot[SPOTMGR_TEMPERATURE_RANGE["start"] - BOOT_BASE:
                       SPOTMGR_TEMPERATURE_RANGE["end"] - BOOT_BASE]
    range_main = main[SPOTMGR_TEMPERATURE_RANGE["main_start"] - MAIN_BASE:
                      SPOTMGR_TEMPERATURE_RANGE["main_start"] - MAIN_BASE + 120]
    require(range_stock == range_main and
            sha256(range_stock) == SPOTMGR_TEMPERATURE_RANGE["sha256"],
            "SPOT-manager temperature-range cross-image body changed")
    require(direct_callers(boot, SPOTMGR_TEMPERATURE_RANGE["start"]) ==
            SPOTMGR_TEMPERATURE_RANGE["callers"],
            "SPOT-manager temperature-range caller topology changed")
    temperature_range_result = {
        "function": SPOTMGR_TEMPERATURE_RANGE["function"],
        "start": SPOTMGR_TEMPERATURE_RANGE["start"],
        "end_exclusive": SPOTMGR_TEMPERATURE_RANGE["end"],
        "source_bytes_by_profile": {"apple-clang": 120, "linux-clang": 120},
        "direct_call_sites": list(SPOTMGR_TEMPERATURE_RANGE["callers"]),
        "main_analogue": SPOTMGR_TEMPERATURE_RANGE["main_start"],
        "boundary_classes_tested": 13,
    }

    trim_helper_results = []
    for facts in SPOTMGR_TRIM_HELPERS:
        leaf = configured[facts["function"]]
        linux = leaf["toolchain_profiles"]["linux-clang"]
        size = facts["end"] - facts["start"]
        require((leaf["runtime_address"], leaf["expected"]["size"],
                 leaf["expected"]["sha256"], leaf["relocations"],
                 leaf["source"]["license"], ROOT / leaf["source"]["path"])
                == (facts["start"], size, facts["sha256"], [],
                    "BSD-3-Clause", SPOTMGR_TRIM_HELPERS_SOURCE),
                f"SPOT-manager trim registration changed: {facts['function']}")
        require((linux["expected"]["size"], linux["expected"]["sha256"],
                 linux["relocations"]) == (size, facts["sha256"], []),
                f"SPOT-manager trim Linux registration changed: {facts['function']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        analogue = main[facts["main_start"] - MAIN_BASE:
                        facts["main_start"] - MAIN_BASE + size]
        require(stock == analogue and sha256(stock) == facts["sha256"],
                f"SPOT-manager trim cross-image body changed: {facts['function']}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"SPOT-manager trim caller topology changed: {facts['function']}")
        trim_helper_results.append({
            "function": facts["function"], "start": facts["start"],
            "end_exclusive": facts["end"],
            "source_bytes_by_profile": {"apple-clang": size, "linux-clang": size},
            "direct_call_sites": list(facts["callers"]),
            "main_analogue": facts["main_start"],
        })

    function_results = {}
    for name, facts in FUNCTIONS.items():
        require(facts["upstream"] + "(" in upstream, f"upstream function disappeared: {facts['upstream']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        main_body = main[facts["main_start"] - MAIN_BASE:
                         facts["main_start"] - MAIN_BASE + len(stock)]
        require(sha256(stock) == facts["sha256"], f"stock body changed: {name}")
        require(sha256(main_body) == facts["main_sha256"], f"main analogue changed: {name}")
        require(sum(a == b for a, b in zip(stock, main_body)) == facts["identical_bytes"],
                f"cross-image identity count changed: {name}")
        require(difference_runs(stock, main_body) == facts["difference_runs"],
                f"cross-image difference topology changed: {name}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"caller topology changed: {name}")
        function_results[name] = {
            "start": facts["start"], "end_exclusive": facts["end"],
            "bytes": len(stock), "sha256": facts["sha256"],
            "upstream": facts["upstream"], "main_analogue": facts["main_start"],
            "identical_bytes": facts["identical_bytes"],
            "address_coupled_difference_bytes": len(stock) - facts["identical_bytes"],
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [
                {"offset": offset, "target_address": target}
                for offset, target in facts["provider_edges"]
            ],
        }
    for start, end, expected in POOLS:
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        require(sha256(body) == expected, f"literal pool changed: {start:#x}")
        require(struct.pack("<I", start | 1) not in boot, f"pool gained stored entry pointer: {start:#x}")

    for name, facts in FUNCTIONS.items():
        item = configured[name]
        require((item["runtime_address"], item["expected"]["size"],
                 item["expected"]["sha256"], item["source"]["license"]) ==
                (facts["start"], facts["end"] - facts["start"], facts["sha256"], "BSD-3-Clause"),
                f"production overlay registration changed: {name}")
        require(tuple((entry["offset"], entry["target_address"])
                      for entry in item["relocations"]) == facts["provider_edges"],
                f"semantic provider-edge contract changed: {name}")

    manifest = json.loads(MANIFEST.read_text())
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {item["name"]: item for item in regions}
    expected_regions = {
        "bootloader_mspi_interrupt_service_426536_source_in_place": (0x00426536, 712, "source_compiled"),
        "bootloader_mspi_interrupt_service_literal_pool_4267fe_opaque": (0x004267FE, 10, "official_blob"),
        "bootloader_mspi_power_control_426808_source_in_place": (0x00426808, 1014, "source_compiled"),
        "bootloader_mspi_power_control_literal_pool_426bfe_426c10_official": (0x00426BFE, 18, "official_blob"),
        "bootloader_memset_wrapper_426c10_source_in_place": (0x00426C10, 18, "source_compiled"),
        "bootloader_memset_wrapper_unreachable_tail_426c22_426c24_official": (0x00426C22, 2, "official_blob"),
        "bootloader_clkmgr_hfrc2_uq15_divider_source_redirect": (0x00426C24, 4, "generated_source_entry_replacement"),
        "bootloader_clkgen_hfadj_config_426c72_source_cave": (0x00426C28, 16, "source_compiled"),
        "bootloader_clkgen_hfadj_disable_426c7e_source_cave": (0x00426C38, 20, "source_compiled"),
        "bootloader_clkmgr_hfrc2_uq15_divider_generated_fill_after_hfadj_caves": (0x00426C4C, 2, "generated_source_entry_replacement"),
        "bootloader_clkmgr_hfrc_integer_divider_source_redirect": (0x00426C4E, 10, "generated_source_entry_replacement"),
        "bootloader_clkgen_hfadj_enable_426c58_source_in_place": (0x00426C58, 24, "source_compiled"),
        "bootloader_clkgen_hfadj_enable_unreachable_tail_426c70_426c72_official": (0x00426C70, 2, "official_blob"),
        "bootloader_clkgen_hfadj_config_426c72_source_redirect": (0x00426C72, 12, "generated_source_entry_replacement"),
        "bootloader_clkgen_hfadj_disable_426c7e_source_redirect": (0x00426C7E, 14, "generated_source_entry_replacement"),
        "bootloader_dual_switch_426c8c_source_in_place": (0x00426C8C, 56, "source_compiled"),
        "bootloader_dual_switch_unreachable_tail_426cc4_426ccc_official": (0x00426CC4, 8, "official_blob"),
        "bootloader_clkgen_config_426ccc_source_redirect": (0x00426CCC, 82, "generated_source_entry_replacement"),
        "bootloader_clkgen_disable_426d1e_source_redirect": (0x00426D1E, 14, "generated_source_entry_replacement"),
        "bootloader_clkgen_gap_426d2c_426d48_official": (0x00426D2C, 28, "official_blob"),
        "bootloader_float_gcd_426d48_source_redirect": (0x00426D48, 106, "generated_source_entry_replacement"),
        "bootloader_float_gap_426db2_426db4_official": (0x00426DB2, 2, "official_blob"),
        "bootloader_float_ratio_426db4_source_redirect": (0x00426DB4, 248, "generated_source_entry_replacement"),
        "bootloader_float_multiplier_426eac_source_redirect": (0x00426EAC, 190, "generated_source_entry_replacement"),
        "bootloader_float_gap_426f6a_426f6c_official": (0x00426F6A, 2, "official_blob"),
        "bootloader_float_encoding_select_426f6c_source_redirect": (0x00426F6C, 198, "generated_source_entry_replacement"),
        "bootloader_float_select_syspll_gap_427032_427040_official": (0x00427032, 14, "official_blob"),
        "bootloader_syspll_min_fvco_427040_source_redirect": (0x00427040, 8, "generated_source_entry_replacement"),
        "bootloader_syspll_min_fvco_427040_source_cave": (0x00427048, 244, "source_compiled"),
        "bootloader_syspll_min_fvco_427040_generated_fill_after_cave": (0x0042713C, 16, "generated_source_entry_replacement"),
        "bootloader_syspll_gap_42714c_427160_official": (0x0042714C, 20, "official_blob"),
        "bootloader_syspll_postdiv_427160_source_redirect": (0x00427160, 8, "generated_source_entry_replacement"),
        "bootloader_syspll_postdiv_427160_source_cave": (0x00427168, 268, "source_compiled"),
        "bootloader_syspll_postdiv_427160_generated_fill_after_cave": (0x00427274, 56, "generated_source_entry_replacement"),
        "bootloader_syspll_initialize_4272ac_source_redirect": (0x004272AC, 8, "generated_source_entry_replacement"),
        "bootloader_syspll_initialize_4272ac_source_cave": (0x004272B4, 60, "source_compiled"),
        "bootloader_syspll_initialize_4272ac_generated_fill_after_cave": (0x004272F0, 24, "generated_source_entry_replacement"),
        "bootloader_syspll_deinitialize_gap_427308_427310_official": (0x00427308, 8, "official_blob"),
        "bootloader_syspll_deinitialize_427310_source_in_place": (0x00427310, 80, "source_compiled"),
        "bootloader_syspll_enable_427360_source_redirect": (0x00427360, 4, "generated_source_entry_replacement"),
        "bootloader_syspll_enable_427360_source_cave": (0x00427364, 84, "source_compiled"),
        "bootloader_syspll_enable_427360_generated_fill_after_cave": (0x004273B8, 36, "generated_source_entry_replacement"),
        "bootloader_syspll_disable_4273dc_source_in_place": (0x004273DC, 48, "source_compiled"),
        "bootloader_syspll_configure_42740c_source_redirect": (0x0042740C, 4, "generated_source_entry_replacement"),
        "bootloader_syspll_configure_42740c_source_cave": (0x00427410, 240, "source_compiled"),
        "bootloader_syspll_configure_42740c_generated_fill_after_cave": (0x00427500, 34, "generated_source_entry_replacement"),
        "bootloader_syspll_lock_wait_427522_source_redirect": (0x00427522, 6, "generated_source_entry_replacement"),
        "bootloader_syspll_lock_wait_427522_source_cave": (0x00427528, 88, "source_compiled"),
        "bootloader_syspll_lock_wait_427522_generated_fill_after_cave": (0x00427580, 8, "generated_source_entry_replacement"),
        "bootloader_syspll_queue_gap_427588_4275ea_official": (0x00427588, 98, "official_blob"),
        "bootloader_queue_init_4275ea_source_redirect": (0x004275EA, 6, "generated_source_entry_replacement"),
        "bootloader_queue_init_4275ea_source_cave": (0x004275F0, 18, "source_compiled"),
        "bootloader_queue_item_add_427602_source_redirect": (0x00427602, 6, "generated_source_entry_replacement"),
        "bootloader_queue_item_add_427602_source_cave": (0x00427608, 88, "source_compiled"),
        "bootloader_queue_item_get_427660_source_redirect": (0x00427660, 4, "generated_source_entry_replacement"),
        "bootloader_queue_item_get_427660_source_cave": (0x00427664, 86, "source_compiled"),
        "bootloader_queue_memmove_alignment_4276ba_4276bc_official": (0x004276BA, 2, "official_blob"),
        "bootloader_memmove_4276bc_source_redirect": (0x004276BC, 4, "generated_source_entry_replacement"),
        "bootloader_memmove_4276bc_source_cave": (0x004276C0, 50, "source_compiled"),
        "bootloader_memmove_4276bc_generated_fill_after_cave": (0x004276F2, 96, "generated_source_entry_replacement"),
        "bootloader_memmove_cmdq_alignment_427752_427754_official": (0x00427752, 2, "official_blob"),
        "bootloader_cmdq_update_indices_427754_source_redirect": (0x00427754, 4, "generated_source_entry_replacement"),
        "bootloader_cmdq_update_indices_427754_source_cave": (0x00427758, 44, "source_compiled"),
        "bootloader_cmdq_update_indices_427754_generated_fill_after_cave": (0x00427784, 16, "generated_source_entry_replacement"),
        "bootloader_cmdq_init_427794_source_in_place": (0x00427794, 184, "source_compiled"),
        "bootloader_cmdq_init_427794_unreachable_tail": (0x0042784C, 44, "official_blob"),
        "bootloader_cmdq_enable_427878_source_in_place": (0x00427878, 68, "source_compiled"),
        "bootloader_cmdq_enable_427878_unreachable_tail": (0x004278BC, 12, "official_blob"),
        "bootloader_cmdq_disable_4278c8_source_in_place": (0x004278C8, 52, "source_compiled"),
        "bootloader_cmdq_disable_4278c8_unreachable_tail": (0x004278FC, 14, "official_blob"),
        "bootloader_cmdq_alloc_block_42790a_source_in_place": (0x0042790A, 148, "source_compiled"),
        "bootloader_cmdq_alloc_block_42790a_unreachable_tail": (0x0042799E, 32, "official_blob"),
        "bootloader_cmdq_release_block_4279be_source_in_place": (0x004279BE, 48, "source_compiled"),
        "bootloader_cmdq_release_block_4279be_unreachable_tail": (0x004279EE, 2, "official_blob"),
        "bootloader_cmdq_post_block_4279f0_source_in_place": (0x004279F0, 92, "source_compiled"),
        "bootloader_cmdq_post_block_4279f0_unreachable_tail": (0x00427A4C, 10, "official_blob"),
        "bootloader_cmdq_get_status_427a56_source_in_place": (0x00427A56, 104, "source_compiled"),
        "bootloader_cmdq_get_status_427a56_unreachable_tail": (0x00427ABE, 24, "official_blob"),
        "bootloader_cmdq_term_427ad6_source_in_place": (0x00427AD6, 88, "source_compiled"),
        "bootloader_cmdq_term_427ad6_unreachable_tail": (0x00427B2E, 10, "official_blob"),
        "bootloader_cmdq_error_resume_427b38_source_in_place": (0x00427B38, 88, "source_compiled"),
        "bootloader_cmdq_error_resume_427b38_unreachable_tail": (0x00427B90, 26, "official_blob"),
        "bootloader_cmdq_reset_427baa_source_in_place": (0x00427BAA, 88, "source_compiled"),
        "bootloader_cmdq_reset_427baa_unreachable_tail": (0x00427C02, 16, "official_blob"),
        "bootloader_cmdq_post_loop_block_427c12_source_in_place": (0x00427C12, 96, "source_compiled"),
        "bootloader_cmdq_tail_and_float_math_gap_427c72_427c90": (0x00427C72, 30, "official_blob"),
        "bootloader_floorf_427c90_source_in_place": (0x00427C90, 16, "source_compiled"),
        "bootloader_floor_bits_427ca0_source_in_place": (0x00427CA0, 44, "source_compiled"),
        "bootloader_fmodf_427ccc_source_in_place": (0x00427CCC, 16, "source_compiled"),
        "bootloader_fmod_bits_427cdc_source_in_place": (0x00427CDC, 168, "source_compiled"),
        "bootloader_fmod_bits_427cdc_unreachable_tail": (0x00427D84, 20, "official_blob"),
        "bootloader_roundf_427d98_source_in_place": (0x00427D98, 16, "source_compiled"),
        "bootloader_round_bits_427da8_source_in_place": (0x00427DA8, 40, "source_compiled"),
        "bootloader_ceilf_427dd0_source_in_place": (0x00427DD0, 16, "source_compiled"),
        "bootloader_ceil_bits_427de0_source_in_place": (0x00427DE0, 44, "source_compiled"),
        "bootloader_float_range_classify_427e0c_source_in_place": (0x00427E0C, 72, "source_compiled"),
        "bootloader_opaque_between_float_math_and_spotmgr_427e54_428378": (0x00427E54, 1_316, "official_blob"),
        "bootloader_spotmgr_transition_sequence_2b_428378_source_in_place": (0x00428378, 106, "source_compiled"),
        "bootloader_opaque_between_spotmgr_transitions_4283e2_428a94": (0x004283E2, 1_714, "official_blob"),
        "bootloader_spotmgr_transition_sequence_7b_428a94_source_in_place": (0x00428A94, 276, "source_compiled"),
        "bootloader_opaque_between_spotmgr_transition_7b_and_factory_trims_428ba8_429da4": (0x00428BA8, 4_604, "official_blob"),
        "bootloader_spotmgr_load_factory_trims_429da4_source_in_place": (0x00429DA4, 82, "source_compiled"),
        "bootloader_opaque_between_factory_trims_and_ensure_429df6_42a036": (0x00429DF6, 576, "official_blob"),
        "bootloader_spotmgr_ensure_factory_trims_42a036_source_in_place": (0x0042A036, 20, "source_compiled"),
        "bootloader_spotmgr_timer_irq_service_42a04a_source_in_place": (0x0042A04A, 46, "source_compiled"),
        "bootloader_opaque_between_spotmgr_timer_irq_and_buck_classifier_42a078_42a08c": (0x0042A078, 20, "official_blob"),
        "bootloader_spotmgr_buck_deepsleep_state_42a08c_source_in_place": (0x0042A08C, 272, "source_compiled"),
        "bootloader_spotmgr_internal_power_domain_42a19c_source_in_place": (0x0042A19C, 22, "source_compiled"),
        "bootloader_opaque_between_spotmgr_internal_domain_and_ton_adjust_42a1b2_42a1bc": (0x0042A1B2, 10, "official_blob"),
        "bootloader_spotmgr_power_ton_adjust_42a1bc_source_in_place": (0x0042A1BC, 232, "source_compiled"),
        "bootloader_opaque_between_spotmgr_ton_adjust_and_state_sequence_42a2a4_42a2b4": (0x0042A2A4, 16, "official_blob"),
        "bootloader_spotmgr_state_transition_sequence_42a2b4_source_in_place": (0x0042A2B4, 390, "source_compiled"),
        "bootloader_spotmgr_temperature_transition_separate_42a43a_source_in_place": (0x0042A43A, 130, "source_compiled"),
        "bootloader_spotmgr_power_trims_update_42a4bc_source_in_place": (0x0042A4BC, 138, "source_compiled"),
        "bootloader_opaque_between_spotmgr_power_trims_and_power_state_42a546_42a550": (0x0042A546, 10, "official_blob"),
        "bootloader_spotmgr_power_state_determine_42a550_source_in_place": (0x0042A550, 782, "source_compiled"),
        "bootloader_opaque_between_spotmgr_power_state_classifier_and_update_42a85e_42a878": (0x0042A85E, 26, "official_blob"),
        "bootloader_spotmgr_power_state_update_42a878_source_in_place": (0x0042A878, 758, "source_compiled"),
        "bootloader_opaque_between_spotmgr_update_and_profile_apply_42ab6e_42ab7c": (0x0042AB6E, 14, "official_blob"),
        "bootloader_spotmgr_profile_apply_42ab7c_source_in_place": (0x0042AB7C, 54, "source_compiled"),
        "bootloader_opaque_between_spotmgr_profile_apply_and_init_42abb2_42abbc": (0x0042ABB2, 10, "official_blob"),
        "bootloader_spotmgr_init_42abbc_source_in_place": (0x0042ABBC, 146, "source_compiled"),
        "bootloader_opaque_between_spotmgr_init_and_temperature_init_42ac4e_42ac54": (0x0042AC4E, 6, "official_blob"),
        "bootloader_spotmgr_temperature_init_42ac54_source_in_place": (0x0042AC54, 80, "source_compiled"),
        "bootloader_opaque_between_spotmgr_temperature_init_and_range_42aca4_42ad40": (0x0042ACA4, 156, "official_blob"),
        "bootloader_spotmgr_temperature_range_42ad40_source_in_place": (0x0042AD40, 120, "source_compiled"),
        "bootloader_spotmgr_trim_enable_42adb8_source_in_place": (0x0042ADB8, 108, "source_compiled"),
        "bootloader_spotmgr_profile_trim_42ae24_source_in_place": (0x0042AE24, 72, "source_compiled"),
        "bootloader_spotmgr_trim_restore_42ae6c_source_in_place": (0x0042AE6C, 48, "source_compiled"),
        "bootloader_spotmgr_trim_commit_42ae9c_source_in_place": (0x0042AE9C, 80, "source_compiled"),
        "bootloader_spotmgr_trim_commit_scan_gap_42aeec_42aef0": (0x0042AEEC, 4, "official_blob"),
        "bootloader_spotmgr_buck_deepsleep_scan_42aef0_source_in_place": (0x0042AEF0, 288, "source_compiled"),
        "bootloader_spotmgr_buck_scan_transition_effects_gap_42b010_42b014": (0x0042B010, 4, "official_blob"),
        "bootloader_spotmgr_state_transition_effects_42b014_source_in_place": (0x0042B014, 84, "source_compiled"),
        "bootloader_spotmgr_transition_effects_power_trim_gap_42b068_42b06c": (0x0042B068, 4, "official_blob"),
        "bootloader_spotmgr_power_transition_trims_42b06c_source_in_place": (0x0042B06C, 552, "source_compiled"),
        "bootloader_spotmgr_state_transition_42b294_source_in_place": (0x0042B294, 1_032, "source_compiled"),
        "bootloader_spotmgr_state_transition_decode_gap_42b69c_42b6b8": (0x0042B69C, 28, "official_blob"),
        "bootloader_hw_state_decode_42b6b8_source_in_place": (0x0042B6B8, 770, "source_compiled"),
        "bootloader_opaque_between_hw_state_decode_and_compose_42b9ba_42bdf0": (0x0042B9BA, 1_078, "official_blob"),
        "bootloader_hw_state_compose_42bdf0_source_in_place": (0x0042BDF0, 350, "source_compiled"),
        "bootloader_hw_state_compose_readiness_gap_42bf4e_42bf54": (0x0042BF4E, 6, "official_blob"),
        "bootloader_hardware_readiness_gate_42bf54_source_in_place": (0x0042BF54, 80, "source_compiled"),
        "bootloader_opaque_between_readiness_gate_and_hw_status_route_42bfa4_42c034": (0x0042BFA4, 144, "official_blob"),
        "bootloader_hw_status_route_42c034_source_in_place": (0x0042C034, 66, "source_compiled"),
        "bootloader_hw_error_classify_42c076_source_in_place": (0x0042C076, 60, "source_compiled"),
        "bootloader_hw_event_apply_42c0b2_source_in_place": (0x0042C0B2, 368, "source_compiled"),
        "bootloader_rounded_divider_42c222_source_in_place": (0x0042C222, 52, "source_compiled"),
        "bootloader_is_power_of_two_42c256_source_in_place": (0x0042C256, 20, "source_compiled"),
        "bootloader_hw_clock_encode_42c26a_source_in_place": (0x0042C26A, 376, "source_compiled"),
        "bootloader_cmdq_adapter_init_42c3e2_source_in_place": (0x0042C3E2, 62, "source_compiled"),
        "bootloader_cmdq_adapter_enable_42c420_source_in_place": (0x0042C420, 46, "source_compiled"),
        "bootloader_cmdq_adapter_disable_42c44e_source_in_place": (0x0042C44E, 12, "source_compiled"),
        "bootloader_hw_descriptor_publish_42c45a_source_in_place": (0x0042C45A, 108, "source_compiled"),
        "bootloader_hw_context_claim_42c4c6_source_in_place": (0x0042C4C6, 114, "source_compiled"),
        "bootloader_hw_context_enable_42c538_source_in_place": (0x0042C538, 258, "source_compiled"),
        "bootloader_hw_interrupt_enable_42c63a_source_in_place": (0x0042C63A, 56, "source_compiled"),
        "bootloader_hw_interrupt_status_get_42c672_source_in_place": (0x0042C672, 68, "source_compiled"),
        "bootloader_hw_interrupt_clear_42c6b6_source_in_place": (0x0042C6B6, 46, "source_compiled"),
        "bootloader_opaque_between_interrupt_clear_and_event_service_42c6e4_42c6f8": (0x0042C6E4, 20, "official_blob"),
        "bootloader_hw_event_service_42c6f8_source_in_place": (0x0042C6F8, 648, "source_compiled"),
        "bootloader_opaque_between_event_service_and_config_transaction_42c980_42c988": (0x0042C980, 8, "official_blob"),
        "bootloader_hw_config_transaction_42c988_source_in_place": (0x0042C988, 684, "source_compiled"),
        "bootloader_hw_instance_configure_42cc34_source_in_place": (0x0042CC34, 380, "source_compiled"),
        "bootloader_opaque_between_instance_configure_and_state_adjust_42cdb0_42cdf8": (0x0042CDB0, 72, "official_blob"),
        "bootloader_state_adjust_42cdf8_source_in_place": (0x0042CDF8, 172, "source_compiled"),
        "bootloader_state_update_critical_42cea4_source_in_place": (0x0042CEA4, 52, "source_compiled"),
        "bootloader_state_range_update_42ced8_source_in_place": (0x0042CED8, 264, "source_compiled"),
        "bootloader_state_event_zero_42cfe0_source_in_place": (0x0042CFE0, 274, "source_compiled"),
        "bootloader_state_event_zero_state_one_gap_42d0f2_42d104": (0x0042D0F2, 18, "official_blob"),
        "bootloader_state_event_one_value_42d104_source_in_place": (0x0042D104, 696, "source_compiled"),
        "bootloader_state_register_initialize_42d3bc_source_in_place": (0x0042D3BC, 422, "source_compiled"),
        "bootloader_state_event_dispatch_42d562_source_in_place": (0x0042D562, 96, "source_compiled"),
        "bootloader_opaque_between_state_dispatch_and_stream_mode_42d5c2_42d84c": (0x0042D5C2, 650, "official_blob"),
        "bootloader_stream_mode_42d84c_source_in_place": (0x0042D84C, 62, "source_compiled"),
        "bootloader_runtime_context_get_42d88a_source_in_place": (0x0042D88A, 6, "source_compiled"),
        "bootloader_dfu_image_crc_check_42d890_source_in_place": (0x0042D890, 352, "source_compiled"),
        "bootloader_chunked_indirect_visit_42d9f0_source_in_place": (0x0042D9F0, 46, "source_compiled"),
        "bootloader_chunked_source_compare_42da1e_source_in_place": (0x0042DA1E, 178, "source_compiled"),
        "bootloader_chunk_compare_payload_program_gap_42dad0_42dae8": (0x0042DAD0, 24, "official_blob"),
        "bootloader_dfu_payload_program_42dae8_source_in_place": (0x0042DAE8, 424, "source_compiled"),
        "bootloader_vector_handoff_42dc90_source_in_place": (0x0042DC90, 18, "source_compiled"),
        "bootloader_runtime_context_publish_42dca2_source_in_place": (0x0042DCA2, 114, "source_compiled"),
        "bootloader_control_orchestrator_42dd14_source_in_place": (0x0042DD14, 84, "source_compiled"),
        "bootloader_runtime_context_wrapper_42dd68_source_in_place": (0x0042DD68, 8, "source_compiled"),
        "bootloader_runtime_queue_context_init_42dd70_source_in_place": (0x0042DD70, 40, "source_compiled"),
        "bootloader_noop_callback_42dd98_source_in_place": (0x0042DD98, 2, "source_compiled"),
        "bootloader_control_one_wrapper_42dd9a_source_in_place": (0x0042DD9A, 10, "source_compiled"),
        "bootloader_control_two_wrapper_42dda4_source_in_place": (0x0042DDA4, 10, "source_compiled"),
        "bootloader_runtime_action_context_init_42ddae_source_in_place": (0x0042DDAE, 44, "source_compiled"),
        "bootloader_runtime_action_context_deinit_42ddda_source_in_place": (0x0042DDDA, 24, "source_compiled"),
        "bootloader_runtime_enable_sequence_42ddf2_source_in_place": (0x0042DDF2, 28, "source_compiled"),
        "bootloader_critical_dispatch_transaction_42de0e_source_in_place": (0x0042DE0E, 74, "source_compiled"),
        "bootloader_dfu_service_task_42de58_source_in_place": (0x0042DE58, 684, "source_compiled"),
        "bootloader_dfu_service_control_bits_gap_42e104_42e1c4": (0x0042E104, 192, "official_blob"),
        "bootloader_control_bits_dispatch_42e1c4_source_in_place": (0x0042E1C4, 22, "source_compiled"),
        "bootloader_control_terminal_loop_42e1da_source_in_place": (0x0042E1DA, 18, "source_compiled"),
        "bootloader_crc32_table_42e1ec_source_in_place": (0x0042E1EC, 52, "source_compiled"),
        "bootloader_crc32_state_probe_gap_42e220_42e224": (0x0042E220, 4, "official_blob"),
        "bootloader_retained_state_probe_42e224_source_in_place": (0x0042E224, 48, "source_compiled"),
        "bootloader_event_flags_init_42e254_source_in_place": (0x0042E254, 34, "source_compiled"),
        "bootloader_noop_callback_42e276_source_in_place": (0x0042E276, 2, "source_compiled"),
        "bootloader_event_runtime_setup_42e278_source_in_place": (0x0042E278, 12, "source_compiled"),
        "bootloader_event_callback_dispatch_42e284_source_in_place": (0x0042E284, 30, "source_compiled"),
        "bootloader_event_wait_mask_42e2a2_source_in_place": (0x0042E2A2, 72, "source_compiled"),
        "bootloader_event_wait_one_wrapper_42e2ea_source_in_place": (0x0042E2EA, 14, "source_compiled"),
        "bootloader_event_service_loop_42e2f8_source_in_place": (0x0042E2F8, 162, "source_compiled"),
        "bootloader_noop_callback_42e39a_source_in_place": (0x0042E39A, 2, "source_compiled"),
        "bootloader_guard_context_init_42e39c_source_in_place": (0x0042E39C, 46, "source_compiled"),
        "bootloader_guarded_context_teardown_42e3ca_source_in_place": (0x0042E3CA, 22, "source_compiled"),
        "bootloader_control_one_wait_42e3e0_source_in_place": (0x0042E3E0, 50, "source_compiled"),
        "bootloader_control_two_publish_42e412_source_in_place": (0x0042E412, 50, "source_compiled"),
        "bootloader_event_bit_set_42e444_source_in_place": (0x0042E444, 20, "source_compiled"),
        "bootloader_opaque_between_event_bit_and_guarded_dispatch_42e458_42e4a0": (0x0042E458, 72, "official_blob"),
        "bootloader_aligned_guarded_dispatch_42e4a0_source_in_place": (0x0042E4A0, 84, "source_compiled"),
        "bootloader_alignment_dispatch_42e4f4_source_in_place": (0x0042E4F4, 26, "source_compiled"),
        "bootloader_alignment_dispatch_terminal_mode_gap_42e50e_42e514": (0x0042E50E, 6, "official_blob"),
        "bootloader_terminal_mode_42e514_source_in_place": (0x0042E514, 32, "source_compiled"),
        "bootloader_terminal_mode_event_runtime_gap_42e534_42e53c": (0x0042E534, 8, "official_blob"),
        "bootloader_event_runtime_init_42e53c_source_in_place": (0x0042E53C, 262, "source_compiled"),
        "bootloader_event_runtime_callback_loop_gap_42e642_42e644": (0x0042E642, 2, "official_blob"),
        "bootloader_event_callback_loop_42e644_source_in_place": (0x0042E644, 66, "source_compiled"),
        "bootloader_event_callback_enqueue_42e686_source_in_place": (0x0042E686, 108, "source_compiled"),
        "bootloader_opaque_between_event_enqueue_and_guarded_call_42e6f2_42e8a4": (0x0042E6F2, 434, "official_blob"),
        "bootloader_guarded_call_cleanup_42e8a4_source_in_place": (0x0042E8A4, 30, "source_compiled"),
        "bootloader_guarded_call_context_initialize_gap_42e8c2_42e8d0": (0x0042E8C2, 14, "official_blob"),
        "bootloader_hw_context_initialize_42e8d0_source_in_place": (0x0042E8D0, 354, "source_compiled"),
        "bootloader_hw_handle_reset_42ea32_source_in_place": (0x0042EA32, 54, "source_compiled"),
        "bootloader_hw_profile_apply_42ea68_source_in_place": (0x0042EA68, 142, "source_compiled"),
        "bootloader_hw_channel_config_42eaf6_source_in_place": (0x0042EAF6, 126, "source_compiled"),
        "bootloader_hw_handle_configure_42eb74_source_in_place": (0x0042EB74, 54, "source_compiled"),
        "bootloader_hw_handle_enable_42ebaa_source_in_place": (0x0042EBAA, 56, "source_compiled"),
        "bootloader_hw_handle_disable_42ebe2_source_in_place": (0x0042EBE2, 42, "source_compiled"),
        "bootloader_hw_config_dispatch_42ec0c_source_in_place": (0x0042EC0C, 340, "source_compiled"),
        "bootloader_hw_handle_activate_42ed60_source_in_place": (0x0042ED60, 64, "source_compiled"),
        "bootloader_hardware_channel_normalize_42eda0_source_in_place": (0x0042EDA0, 86, "source_compiled"),
        "bootloader_hardware_channel_normalize_gap_42edf6_42ee00": (0x0042EDF6, 10, "official_blob"),
        "bootloader_hw_channel_normalize_42ee00_source_in_place": (0x0042EE00, 108, "source_compiled"),
        "bootloader_channel_normalize_enumerate_gap_42ee6c_42ee70": (0x0042EE6C, 4, "official_blob"),
        "bootloader_hw_channel_enumerate_42ee70_source_in_place": (0x0042EE70, 388, "source_compiled"),
        "bootloader_hw_handle_command_42eff4_source_in_place": (0x0042EFF4, 32, "source_compiled"),
        "bootloader_hw_command_profile_transfer_gap_42f014_42f020": (0x0042F014, 12, "official_blob"),
        "bootloader_register_profile_transfer_42f020_source_in_place": (0x0042F020, 302, "source_compiled"),
        "bootloader_profile_transfer_power_toggle_gap_42f14e_42f1c8": (0x0042F14E, 122, "official_blob"),
        "bootloader_register_power_toggle_42f1c8_source_in_place": (0x0042F1C8, 60, "source_compiled"),
        "bootloader_event_value_profile_42f204_source_in_place": (0x0042F204, 246, "source_compiled"),
        "bootloader_hw_register_profile_restore_42f2fa_source_in_place": (0x0042F2FA, 148, "source_compiled"),
        "bootloader_event_dispatch_42f38e_source_in_place": (0x0042F38E, 76, "source_compiled"),
        "bootloader_opaque_between_event_dispatch_and_mode_apply_42f3da_42ff00": (0x0042F3DA, 2_854, "official_blob"),
        "bootloader_mode_apply_42ff00_source_in_place": (0x0042FF00, 242, "source_compiled"),
        "bootloader_mode_one_apply_42fff2_source_in_place": (0x0042FFF2, 12, "source_compiled"),
        "bootloader_mode_one_platform_bringup_gap_42fffe_430000": (0x0042FFFE, 2, "official_blob"),
        "bootloader_platform_bringup_430000_source_in_place": (0x00430000, 470, "source_compiled"),
        "bootloader_platform_boot_sequence_4301d6_source_in_place": (0x004301D6, 30, "source_compiled"),
        "bootloader_platform_boot_nvic_gap_4301f4_430240": (0x004301F4, 76, "official_blob"),
        "bootloader_nvic_enable_bit_430240_source_in_place": (0x00430240, 28, "source_compiled"),
        "bootloader_scb_priority_nibble_43025c_source_in_place": (0x0043025C, 36, "source_compiled"),
        "bootloader_descriptor_register_430280_source_in_place": (0x00430280, 316, "source_compiled"),
        "bootloader_boolean_route_status_4303bc_source_in_place": (0x004303BC, 34, "source_compiled"),
        "bootloader_opaque_between_boolean_route_and_nvic_enable_4303de_430470": (0x004303DE, 146, "official_blob"),
        "bootloader_nvic_enable_bit_430470_source_in_place": (0x00430470, 30, "source_compiled"),
        "bootloader_hw_config_retry_43048e_source_in_place": (0x0043048E, 116, "source_compiled"),
        "bootloader_platform_finish_430502_source_in_place": (0x00430502, 270, "source_compiled"),
        "bootloader_opaque_between_platform_finish_and_address_validate_430610_430a60": (0x00430610, 1_104, "official_blob"),
        "bootloader_address_validate_430a60_source_in_place": (0x00430A60, 60, "source_compiled"),
        "bootloader_validated_byte_copy_430a9c_source_in_place": (0x00430A9C, 40, "source_compiled"),
        "bootloader_validated_word_transfer_430ac4_source_in_place": (0x00430AC4, 40, "source_compiled"),
        "bootloader_mode_four_wrapper_430aec_source_in_place": (0x00430AEC, 32, "source_compiled"),
        "bootloader_mode_wrapper_word_transfer_gap_430b0c_430b10": (0x00430B0C, 4, "official_blob"),
        "bootloader_word_transfer_critical_430b10_source_in_place": (0x00430B10, 44, "source_compiled"),
        "bootloader_opaque_between_word_transfer_and_platform_init_430b3c_43194c": (0x00430B3C, 3_600, "official_blob"),
        "bootloader_platform_services_init_43194c_source_in_place": (0x0043194C, 62, "source_compiled"),
        "bootloader_opaque_between_platform_init_and_zero_table_43198a_431e38": (0x0043198A, 1_198, "official_blob"),
        "bootloader_zero_table_431e38_source_in_place": (0x00431E38, 56, "source_compiled"),
        "bootloader_opaque_between_zero_table_and_startup_431e70_432910": (0x00431E70, 2_720, "official_blob"),
        "bootloader_vector_table_relocate_432910_source_in_place": (0x00432910, 10, "source_compiled"),
        "bootloader_stack_limits_init_43291a_source_in_place": (0x0043291A, 16, "source_compiled"),
        "bootloader_startup_literals_43292a_43293c": (0x0043292A, 18, "official_blob"),
        "bootloader_process_stack_init_43293c_source_in_place": (0x0043293C, 24, "source_compiled"),
        "bootloader_process_stack_literal_432954_432958": (0x00432954, 4, "official_blob"),
        "bootloader_fpu_enable_432958_source_in_place": (0x00432958, 34, "source_compiled"),
        "bootloader_startup_runtime_alignment_43297a_43297c": (0x0043297A, 2, "official_blob"),
        "bootloader_runtime_start_43297c_source_in_place": (0x0043297C, 30, "source_compiled"),
        "bootloader_runtime_start_alignment_43299a_43299c": (0x0043299A, 2, "official_blob"),
        "bootloader_init_array_run_43299c_source_in_place": (0x0043299C, 32, "source_compiled"),
        "bootloader_init_array_literals_4329bc_4329c4": (0x004329BC, 8, "official_blob"),
        "bootloader_terminal_loop_4329c4_source_in_place": (0x004329C4, 14, "source_compiled"),
        "bootloader_opaque_after_terminal_loop_4329d2": (0x004329D2, 6_821, "official_blob"),
        "bootloader_clkgen_config_426ccc_source_cave": (0x00415BFC, 84, "source_compiled"),
        "bootloader_clkgen_disable_426d1e_source_cave": (0x00415C50, 20, "source_compiled"),
        "bootloader_float_gcd_426d48_source_cave": (0x00415C64, 92, "source_compiled"),
        "bootloader_format_core_generated_fill_between_float_gcd_ratio_caves": (0x00415CC0, 20, "generated_source_entry_replacement"),
        "bootloader_float_ratio_426db4_source_cave": (0x00415CD4, 252, "source_compiled"),
        "bootloader_format_core_generated_fill_between_float_ratio_multiplier_caves": (0x00415DD0, 20, "generated_source_entry_replacement"),
        "bootloader_float_multiplier_426eac_source_cave": (0x00415DE4, 192, "source_compiled"),
        "bootloader_float_encoding_select_426f6c_source_cave": (0x00415EA4, 180, "source_compiled"),
        "bootloader_format_core_generated_fill_after_clkgen_float_gcd_ratio_multiplier_select_caves": (0x00415F58, 86, "generated_source_entry_replacement"),
    }
    for name, expected in expected_regions.items():
        item = by_name[name]
        require((item["target_address"], item["size"], item["address_status"]) == expected,
                f"core manifest region changed: {name}")

    report = json.loads(BUILD_REPORT.read_text())
    component = report["component"]
    require((component["size"], component["sha256"]) ==
            (163_840, "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"),
            "canonical boot provider identity changed")
    require((component["source_owned_bytes"], component["opaque_base_bytes"],
             component["source_owned_cave_bytes"],
             component["source_owned_in_place_bytes"],
            component["generated_patch_site_bytes"]) ==
            (59_009, 87_985, 2_594, 41_190, 16_830),
            "live source/official accounting changed")
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] +
            component["generated_alignment_bytes"] == 147_010,
            "boot source/official conservation changed")

    return {
        "component": "G2 Apollo bootloader post-MSPI frontier",
        "status": "classification-complete / 187 production source admissions / zero unresolved executable spans / hardware validation blocked by unavailable physical evidence",
        "frontier": {"start": 0x00426536, "end_exclusive": 0x00434477, "bytes": 57_153},
        "classification": {
            "exhaustive": True, "unclassified_bytes": 0,
            "row_count": len(rows),
            "by_disposition": {key: {"spans": value[0], "bytes": value[1]}
                               for key, value in EXPECTED_DISPOSITIONS.items()},
        },
        "admission": {
            "license": "BSD-3-Clause", "production_routed": True,
            "upstream_commit": provenance["upstream"]["selected_commit"],
            "instruction_representation": "reviewable Thumb-2 mnemonics; no raw encoding directives",
            "source_owned_bytes": 26_720, "retained_literal_pool_bytes": 28,
            "retained_unreachable_tail_bytes": 284,
            "memset_wrapper": {
                "function": MEMSET_WRAPPER["function"],
                "start": MEMSET_WRAPPER["start"],
                "source_end_exclusive": MEMSET_WRAPPER["source_end"],
                "stock_end_exclusive": MEMSET_WRAPPER["stock_end"],
                "source_bytes": 18,
                "retained_unreachable_tail_bytes": 2,
                "direct_call_sites": list(MEMSET_WRAPPER["callers"]),
                "provider": MEMSET_WRAPPER["provider"],
            },
            "clkgen_hfadj_enable": {
                "function": HFADJ["function"],
                "start": HFADJ["start"],
                "source_end_exclusive": HFADJ["source_end"],
                "stock_end_exclusive": HFADJ["stock_end"],
                "source_bytes": 24,
                "retained_unreachable_tail_bytes": 2,
                "direct_call_sites": list(HFADJ["callers"]),
                "register": HFADJ["register"],
            },
            "clkgen_hfadj_config": {
                "function": HFADJ_CONFIG["function"],
                "start": HFADJ_CONFIG["start"],
                "end_exclusive": HFADJ_CONFIG["end"],
                "stock_bytes": 12,
                "source_cave_start": HFADJ_CONFIG["cave_start"],
                "source_cave_bytes": 16,
                "direct_call_sites": list(HFADJ_CONFIG["callers"]),
                "register": HFADJ_CONFIG["register"],
            },
            "clkgen_hfadj_disable": {
                "function": HFADJ_DISABLE["function"],
                "start": HFADJ_DISABLE["start"],
                "end_exclusive": HFADJ_DISABLE["end"],
                "stock_bytes": 14,
                "source_cave_start": HFADJ_DISABLE["cave_start"],
                "source_cave_bytes": 20,
                "direct_call_sites": list(HFADJ_DISABLE["callers"]),
                "register": HFADJ_DISABLE["register"],
            },
            "dual_switch": {
                "function": DUAL_SWITCH["function"],
                "start": DUAL_SWITCH["start"],
                "source_end_exclusive": DUAL_SWITCH["source_end"],
                "stock_end_exclusive": DUAL_SWITCH["stock_end"],
                "source_bytes": 56,
                "retained_unreachable_tail_bytes": 8,
                "direct_call_sites": list(DUAL_SWITCH["callers"]),
                "register": DUAL_SWITCH["register"],
                "status_register": DUAL_SWITCH["status_register"],
                "poll_mask": DUAL_SWITCH["poll_mask"],
                "provider": DUAL_SWITCH["provider"],
            },
            "clkgen_config": {
                "function": CLKGEN_CONFIG["function"],
                "start": CLKGEN_CONFIG["start"],
                "end_exclusive": CLKGEN_CONFIG["end"],
                "stock_bytes": 82,
                "source_cave_start": CLKGEN_CONFIG["cave_start"],
                "source_cave_bytes": 84,
                "direct_call_sites": list(CLKGEN_CONFIG["callers"]),
                "control_register": CLKGEN_CONFIG["control_register"],
                "mode_register": CLKGEN_CONFIG["mode_register"],
                "divider_register": CLKGEN_CONFIG["divider_register"],
            },
            "clkgen_disable": {
                "function": CLKGEN_DISABLE["function"],
                "start": CLKGEN_DISABLE["start"],
                "end_exclusive": CLKGEN_DISABLE["end"],
                "stock_bytes": 14,
                "source_cave_start": CLKGEN_DISABLE["cave_start"],
                "source_cave_bytes": 20,
                "direct_call_sites": list(CLKGEN_DISABLE["callers"]),
                "register": CLKGEN_DISABLE["register"],
            },
            "float_gcd": {
                "function": FLOAT_GCD["function"],
                "start": FLOAT_GCD["start"],
                "end_exclusive": FLOAT_GCD["end"],
                "stock_bytes": 106,
                "source_cave_start": FLOAT_GCD["cave_start"],
                "source_cave_bytes": 92,
                "direct_call_sites": list(FLOAT_GCD["callers"]),
                "provider": FLOAT_GCD["provider"],
                "main_analogue": FLOAT_GCD["main_start"],
                "identical_bytes": FLOAT_GCD["identical_bytes"],
            },
            "float_ratio": {
                "function": FLOAT_RATIO["function"],
                "start": FLOAT_RATIO["start"],
                "end_exclusive": FLOAT_RATIO["end"],
                "stock_bytes": 248,
                "source_cave_start": FLOAT_RATIO["cave_start"],
                "source_cave_bytes": 252,
                "direct_call_sites": list(FLOAT_RATIO["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in FLOAT_RATIO["stock_provider_edges"]
                ],
                "main_analogue": FLOAT_RATIO["main_start"],
                "identical_bytes": FLOAT_RATIO["identical_bytes"],
            },
            "float_multiplier": {
                "function": FLOAT_MULTIPLIER["function"],
                "start": FLOAT_MULTIPLIER["start"],
                "end_exclusive": FLOAT_MULTIPLIER["end"],
                "stock_bytes": 190,
                "source_cave_start": FLOAT_MULTIPLIER["cave_start"],
                "source_cave_bytes": 192,
                "direct_call_sites": list(FLOAT_MULTIPLIER["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in
                    FLOAT_MULTIPLIER["stock_provider_edges"]
                ],
                "main_analogue": FLOAT_MULTIPLIER["main_start"],
                "identical_bytes": FLOAT_MULTIPLIER["identical_bytes"],
            },
            "float_encoding_select": {
                "function": FLOAT_SELECT["function"],
                "start": FLOAT_SELECT["start"],
                "end_exclusive": FLOAT_SELECT["end"],
                "stock_bytes": 198,
                "source_cave_start": FLOAT_SELECT["cave_start"],
                "source_cave_bytes": 180,
                "direct_call_sites": list(FLOAT_SELECT["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in FLOAT_SELECT["stock_provider_edges"]
                ],
                "main_analogue": FLOAT_SELECT["main_start"],
                "identical_bytes": FLOAT_SELECT["identical_bytes"],
            },
            "syspll_min_fvco": {
                "function": SYSPLL_MIN_FVCO["function"],
                "start": SYSPLL_MIN_FVCO["start"],
                "end_exclusive": SYSPLL_MIN_FVCO["end"],
                "stock_bytes": 268,
                "source_cave_start": SYSPLL_MIN_FVCO["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_MIN_FVCO["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_MIN_FVCO["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in SYSPLL_MIN_FVCO["stock_provider_edges"]
                ],
                "postdivider_table_address": SYSPLL_MIN_FVCO["table"][0],
                "main_analogue": SYSPLL_MIN_FVCO["main_start"],
                "identical_bytes": SYSPLL_MIN_FVCO["identical_bytes"],
            },
            "syspll_postdiv": {
                "function": SYSPLL_POSTDIV["function"],
                "start": SYSPLL_POSTDIV["start"],
                "end_exclusive": SYSPLL_POSTDIV["end"],
                "stock_bytes": 332,
                "source_cave_start": SYSPLL_POSTDIV["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_POSTDIV["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_POSTDIV["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in SYSPLL_POSTDIV["stock_provider_edges"]
                ],
                "pts_table_addresses": [
                    table[0] for table in SYSPLL_POSTDIV["tables"]
                ],
                "main_analogue": SYSPLL_POSTDIV["main_start"],
                "identical_bytes": SYSPLL_POSTDIV["identical_bytes"],
            },
            "syspll_initialize": {
                "function": SYSPLL_INITIALIZE["function"],
                "start": SYSPLL_INITIALIZE["start"],
                "end_exclusive": SYSPLL_INITIALIZE["end"],
                "stock_bytes": 92,
                "source_cave_start": SYSPLL_INITIALIZE["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_INITIALIZE["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_INITIALIZE["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in SYSPLL_INITIALIZE["stock_provider_edges"]
                ],
                "state_address": SYSPLL_INITIALIZE["state_literal"][1],
                "handle_magic": SYSPLL_INITIALIZE["magic_literal"][1],
                "main_analogue": SYSPLL_INITIALIZE["main_start"],
                "identical_bytes": SYSPLL_INITIALIZE["identical_bytes"],
            },
            "syspll_deinitialize": {
                "function": SYSPLL_DEINITIALIZE["function"],
                "start": SYSPLL_DEINITIALIZE["start"],
                "end_exclusive": SYSPLL_DEINITIALIZE["end"],
                "stock_bytes": 80,
                "source_in_place_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_DEINITIALIZE["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_DEINITIALIZE["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in
                    SYSPLL_DEINITIALIZE["stock_provider_edges"]
                ],
                "handle_magic": SYSPLL_DEINITIALIZE["magic_literal"][1],
                "main_analogue": SYSPLL_DEINITIALIZE["main_start"],
                "identical_bytes": SYSPLL_DEINITIALIZE["identical_bytes"],
            },
            "syspll_enable": {
                "function": SYSPLL_ENABLE["function"],
                "start": SYSPLL_ENABLE["start"],
                "end_exclusive": SYSPLL_ENABLE["end"],
                "stock_bytes": 124,
                "source_cave_start": SYSPLL_ENABLE["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_ENABLE["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_ENABLE["callers"]),
                "handle_magic": SYSPLL_ENABLE["literals"][0][1],
                "vrctrl_address": SYSPLL_ENABLE["literals"][1][1],
                "pllctl0_address": SYSPLL_ENABLE["literals"][2][1],
                "main_analogue": SYSPLL_ENABLE["main_start"],
                "identical_bytes": SYSPLL_ENABLE["identical_bytes"],
            },
            "syspll_disable": {
                "function": SYSPLL_DISABLE["function"],
                "start": SYSPLL_DISABLE["start"],
                "end_exclusive": SYSPLL_DISABLE["end"],
                "stock_bytes": 48,
                "source_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_DISABLE["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_DISABLE["callers"]),
                "handle_magic": SYSPLL_DISABLE["literals"][0][1],
                "pllctl0_address": SYSPLL_DISABLE["literals"][1][1],
                "main_analogue": SYSPLL_DISABLE["main_start"],
                "identical_bytes": SYSPLL_DISABLE["identical_bytes"],
            },
            "syspll_configure": {
                "function": SYSPLL_CONFIGURE["function"],
                "start": SYSPLL_CONFIGURE["start"],
                "end_exclusive": SYSPLL_CONFIGURE["end"],
                "stock_bytes": 278,
                "source_cave_start": SYSPLL_CONFIGURE["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_CONFIGURE["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_CONFIGURE["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in
                    SYSPLL_CONFIGURE["stock_provider_edges"]
                ],
                "handle_magic": SYSPLL_CONFIGURE["literals"][0][1],
                "pllctl0_address": SYSPLL_CONFIGURE["literals"][1][1],
                "plldiv0_address": SYSPLL_CONFIGURE["literals"][2][1],
                "plldiv1_address": SYSPLL_CONFIGURE["literals"][3][1],
                "main_analogue": SYSPLL_CONFIGURE["main_start"],
                "identical_bytes": SYSPLL_CONFIGURE["identical_bytes"],
            },
            "syspll_lock_wait": {
                "function": SYSPLL_LOCK_WAIT["function"],
                "start": SYSPLL_LOCK_WAIT["start"],
                "end_exclusive": SYSPLL_LOCK_WAIT["end"],
                "stock_bytes": 102,
                "source_cave_start": SYSPLL_LOCK_WAIT["cave_start"],
                "source_cave_bytes_by_profile": {
                    name: facts["size"]
                    for name, facts in SYSPLL_LOCK_WAIT["profiles"].items()
                },
                "direct_call_sites": list(SYSPLL_LOCK_WAIT["callers"]),
                "provider_edges": [
                    {"offset": offset, "target_address": target}
                    for offset, target in
                    SYSPLL_LOCK_WAIT["stock_provider_edges"]
                ],
                "handle_magic": SYSPLL_LOCK_WAIT["literals"][0][1],
                "pllctl0_address": SYSPLL_LOCK_WAIT["literals"][1][1],
                "plldiv1_address": SYSPLL_LOCK_WAIT["literals"][2][1],
                "pllstat_address": SYSPLL_LOCK_WAIT["literals"][3][1],
                "main_analogue": SYSPLL_LOCK_WAIT["main_start"],
                "identical_bytes": SYSPLL_LOCK_WAIT["identical_bytes"],
            },
            "queue_family": {
                "upstream_source_sha256": QUEUE_UPSTREAM_SOURCE_SHA256,
                "upstream_commit": provenance["upstream"]["selected_commit"],
                "abi_bytes": 24,
                "critical_provider": 0x0041B8EC,
                "functions": queue_results,
            },
            "memmove": memmove_result,
            "cmdq_update_indices": cmdq_update_result,
            "cmdq_public_services": cmdq_service_results,
            "float_math_runtime": float_math_results,
            "spotmgr_transition_sequence_2b": spotmgr_result,
            "spotmgr_transition_sequence_7b": spotmgr_7b_result,
            "spotmgr_factory_trim_loader": factory_trim_result,
            "spotmgr_factory_trim_readiness": ensure_result,
            "spotmgr_timer_irq_service": timer_irq_result,
            "spotmgr_buck_deepsleep_classifier": buck_deepsleep_result,
            "spotmgr_internal_power_domain": internal_domain_result,
            "spotmgr_power_ton_adjust": power_ton_result,
            "spotmgr_state_transition_sequence": state_sequence_result,
            "spotmgr_temperature_transition_separate": temperature_transition_result,
            "spotmgr_power_trims_update": power_trims_result,
            "spotmgr_power_state_determine": power_state_result,
            "spotmgr_power_state_update": update_profile_results["power_state_update"],
            "spotmgr_profile_apply": update_profile_results["profile_apply"],
            "spotmgr_init": update_profile_results["init"],
            "spotmgr_temperature_init": update_profile_results["temperature_init"],
            "spotmgr_temperature_range": temperature_range_result,
            "spotmgr_trim_helpers": trim_helper_results,
            "spotmgr_trim_commit": update_profile_results["trim_commit"],
            "spotmgr_buck_deepsleep_scan": buck_scan_result,
            "spotmgr_state_transition_effects": state_effects_result,
            "spotmgr_power_transition_trims": power_transition_result,
            "rounded_divider_helpers": divider_results,
            "hardware_clock_encode": hw_clock_encode_result,
            "hardware_event_apply": hw_event_apply_result,
            "state_range_services": state_range_results,
            "state_event_zero": state_event_zero_result,
            "miscellaneous_primitives": misc_primitive_results,
            "register_helpers": register_helper_results,
            "command_queue_adapters": cmdq_adapter_results,
            "hardware_descriptor_publish": hw_descriptor_result,
            "hardware_context_claim": hw_context_claim_result,
            "hardware_context_enable": hw_context_enable_result,
            "hardware_event_service": hw_event_service_result,
            "hardware_config_transaction": hw_config_transaction_result,
            "hardware_instance_configure": hw_instance_configure_result,
            "hardware_config_retry": hw_config_retry_result,
            "platform_finish": platform_finish_result,
            "platform_bringup": platform_bringup_result,
            "descriptor_register": descriptor_register_result,
            "hardware_state_compose": hw_state_compose_result,
            "hardware_state_decode": hw_state_decode_result,
            "spotmgr_state_transition": spotmgr_state_transition_result,
            "dfu_image_crc_check": dfu_image_crc_result,
            "dfu_payload_program": dfu_payload_program_result,
            "dfu_service_task": dfu_service_task_result,
            "state_event_one_value": state_event_one_result,
            "state_register_initialize": state_register_initialize_result,
            "hardware_context_initialize": hw_context_initialize_result,
            "hardware_profile_apply": hw_profile_apply_result,
            "register_profile_transfer": register_profile_transfer_result,
            "event_value_profile": event_value_profile_result,
            "hardware_register_profile_restore": hw_register_profile_restore_result,
            "chunked_source_compare": chunked_source_compare_result,
            "mode_apply": mode_apply_result,
            "runtime_control_wrappers": control_wrapper_results,
            "runtime_context_lifecycle": context_lifecycle_results,
            "event_control_wrappers": event_control_wrapper_results,
            "event_runtime_setup_wrappers": event_setup_results,
            "retained_event_state_services": event_state_results,
            "small_runtime_services": small_service_results,
            "runtime_control_services": runtime_control_service_results,
            "event_service_loop": event_service_loop_result,
            "event_runtime_services": event_runtime_service_results,
            "control_orchestration": control_orchestration_results,
            "runtime_context_publish": context_publish_result,
            "late_runtime_wrappers": late_wrapper_results,
            "noop_callbacks": noop_results,
            "alignment_dispatch": alignment_dispatch_result,
            "guarded_call_cleanup": guarded_call_result,
            "event_dispatch": event_dispatch_result,
            "hardware_handle_services": hw_handle_results,
            "hardware_handle_command": hw_command_result,
            "clock_manager_dividers": {
                "source": str(CLKMGR_DIVIDER_SOURCE.relative_to(ROOT)),
                "license": "MIT", "production_routed": True,
                "stock_entries": [0x00426C24, 0x00426C4E],
                "routing": "authenticated entry redirects to compiled source caves",
            },
            "hardware_channel_activation": hw_channel_activate_results,
            "hardware_configuration_enumeration": hw_config_enumerate_results,
            "unreferenced_linked_services": orphan_results,
            "startup_services": startup_results,
            "startup_runtime": startup_runtime_results,
            "functions": function_results,
        },
        "profiles": profiles,
        "boot_component": component,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Post-MSPI frontier: 57,153 bytes exhaustively classified; 26,720 bytes production source; 0 unresolved executable bytes")
        print("  hardware validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"post-MSPI frontier audit failed: {error}") from error

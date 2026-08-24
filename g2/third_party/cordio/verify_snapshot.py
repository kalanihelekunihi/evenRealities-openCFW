#!/usr/bin/env python3
"""Fail-closed offline verification for the Packetcraft Cordio source oracle."""

from __future__ import annotations

import hashlib
import json
import stat
import struct
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE = HERE / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 20246
EXPECTED_PROVENANCE_SHA256 = "1fffca2937f4ec8f0937f947e0d6e0c14110ea36c561826be21b67d0c7bab07a"
EXPECTED_RECORDS_SHA256 = "2d9ba02bd31e3784789af3ddb3f2bbcaa9e7187f12eb76506b4b2d14a2d55d9a"
EXPECTED_COMMIT = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
EXPECTED_TREE = "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97"
EXPECTED_PARENT = "eb4282c7abe78dad8fb3984791b9c193fe904052"
EXPECTED_COMMIT_SIZE = 222
EXPECTED_COMMIT_SHA256 = "5dab57d27af0548331378a1b5fcda9bf89724aeecd1b3b92a8df19b516c24c80"
EXPECTED_TREE_CLOSURE_SIZE = 46490
EXPECTED_TREE_CLOSURE_SHA256 = "ff5cfc9516ad240bef69c72df42486dfa82fa54eaa4e5e4dca74cc62917ae5da"
EXPECTED_TREE_OBJECTS = {
    "062769d651f2ff9b740e585d8bcd90dc85dcabef",
    "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97",
    "150eedefa037805a45d7b2c4d3dc40739d2ff994",
    "17786ee74a20a3b90587dd41b013d8468361a1cd",
    "2023fdd8a1aa3f1a49745a4f61a1af0eff0dee2b",
    "376629d79339e79f8152b290a4c966c0c6b15ce4",
    "52851063425147d1f978963a674e92ac674e8043",
    "67a37e3efcd969375f88f782a5cc40c5eced0b43",
    "93d955317dc6b9afda3c5bdde913e8b1a7698173",
    "9cb897dafee585110af7a8f35483337354260d3d",
    "ae95b912d20ab7793467d3c4c329438d80b6b8b9",
    "aea4d8618dfeb509a3db4d8283721e37f66cee04",
    "b05f619801e343c8e026104f763fc7323d1358a1",
    "bfdb7ba37213ccac8046849c7109442268156e07",
    "c3b7f6ec6fd91d0bccef246629db3a3036e833c0",
    "c5faf0c6732ca1a36ad6db3c1b55c1b16668fc47",
    "c8670c6fdf6008807fe22675330928ceb4d8b51c",
    "ecb4b2024b69e629ae83d0abaecb3043b657e3be",
    "ee1818e85ace6a3d730168d36db01d5341acf09a",
    "fc02ee8c9544694cfa5c1da0b29d279928d674c1",
    "fdc54d7b8ae3aed3fa409a74c4b64334b250b80c",
}
EXPECTED_CONFIG_SIZE = 574
EXPECTED_CONFIG_SHA256 = "a908d4d003392c4fa2cfceef0e5d000bb448a67dbb4cf94fcb431c14366e68a2"
EXPECTED_IMAGE_SIZE = 3_523_396
EXPECTED_IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0

EXPECTED_SOURCE_PATHS = [
    "LICENSE.md",
    "ble-host/include/att_api.h",
    "ble-host/include/att_defs.h",
    "ble-host/include/att_uuid.h",
    "ble-host/include/dm_api.h",
    "ble-host/include/hci_api.h",
    "ble-host/include/l2c_api.h",
    "ble-host/include/l2c_defs.h",
    "ble-host/include/sec_api.h",
    "ble-host/include/smp_api.h",
    "ble-host/include/smp_defs.h",
    "ble-host/sources/stack/att/att_main.h",
    "ble-host/sources/stack/att/atts_csf.c",
    "ble-host/sources/stack/att/atts_main.h",
    "ble-host/sources/stack/cfg/cfg_stack.h",
    "ble-host/sources/stack/dm/dm_conn.h",
    "ble-host/sources/stack/dm/dm_conn_sm.c",
    "ble-host/sources/stack/dm/dm_main.h",
    "ble-host/sources/stack/smp/smp_db.c",
    "ble-host/sources/stack/smp/smp_main.h",
    "ble-profiles/include/app_api.h",
    "ble-profiles/include/app_cfg.h",
    "ble-profiles/include/app_db.h",
    "ble-profiles/sources/af/app_main.h",
    "ble-profiles/sources/af/common/app_db.c",
    "ble-profiles/sources/services/svc_core.h",
    "wsf/include/hci_defs.h",
    "wsf/include/util/bda.h",
    "wsf/include/util/bstream.h",
    "wsf/include/wsf_assert.h",
    "wsf/include/wsf_buf.h",
    "wsf/include/wsf_cs.h",
    "wsf/include/wsf_heap.h",
    "wsf/include/wsf_math.h",
    "wsf/include/wsf_nvm.h",
    "wsf/include/wsf_os.h",
    "wsf/include/wsf_queue.h",
    "wsf/include/wsf_timer.h",
    "wsf/include/wsf_trace.h",
    "wsf/include/wsf_types.h",
    "wsf/sources/targets/baremetal/wsf_buf.c",
]
ROOT_SOURCE_PATHS = [
    "ble-host/sources/stack/att/atts_csf.c",
    "ble-host/sources/stack/dm/dm_conn_sm.c",
    "ble-host/sources/stack/smp/smp_db.c",
    "ble-profiles/sources/af/common/app_db.c",
    "wsf/sources/targets/baremetal/wsf_buf.c",
]
METADATA_PATHS = {
    ".gitattributes",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
    "g2-config/cordio_recovered_config.h",
    "g2-patches/smp_main-ambiq-aes-queue-cleanup.patch",
    f"upstream/{EXPECTED_COMMIT}.commit",
    "upstream/trees.json",
}
EXPECTED_RELEASES = {
    "r20.05": {
        "commit": "eeb34839755da1c19cc85b8795cc863483c16ef0",
        "tree": "906eb9beaf5e8c3b39ab445f6522f7febeda38b5",
    },
    "r20.05a": {
        "commit": "5e21ee596a80a3dc75ae5ef0938712a6042b2ac3",
        "tree": "5001d075e93220d66ae1340208046c0526b0dc3a",
    },
    "r20.05b": {
        "commit": "eb4282c7abe78dad8fb3984791b9c193fe904052",
        "tree": "c8204fcb39847aa6d3cae3ec49772a70f6097765",
    },
    "r20.05c": {
        "commit": EXPECTED_COMMIT,
        "tree": EXPECTED_TREE,
    },
}
EXPECTED_ORACLE_BLOBS = {
    "ble-host/sources/stack/att/atts_csf.c": "ed4f051194b77827ec991f0d5c0c38969ea7548a",
    "ble-host/sources/stack/dm/dm_conn_sm.c": "58c5c6e1e4df5744c9a41902634cdd23a1aef906",
    "ble-host/sources/stack/smp/smp_db.c": "cbd056aaab32eab0838b2bd9bbaac872012ca06b",
    "ble-profiles/sources/af/common/app_db.c": "789f4c9bac29a5b7eb92c2cb22a221cdd720fe83",
    "wsf/sources/targets/baremetal/wsf_buf.c": "be2ab9cfc03b65390ba25d8d97321fa2d304fc64",
}
EXPECTED_CODE_SPANS = {
    "AttsCsfSetClientChangeAwareState": (
        0x0052D090,
        0x0052D0DC,
        "3d8ce46d70a13f0a62d6693355310733d09cf623fa61018f825956a8feb56070",
    ),
    "AttsCsfWriteFeatures_core": (
        0x0052D628,
        0x0052D674,
        "2e11f9d1dfa9b76ebfd7d92902439df111292ba781151196eca08280184d5bd9",
    ),
    "AttsCsfWriteFeatures_callback_tail": (
        0x0052D79E,
        0x0052D7B6,
        "27aa2fb64353776ed629c906e6c6466d6fdcf0ae9d5f02efa1a5650229afa124",
    ),
    "dmConnSmExecute_event_table_core": (
        0x00534024,
        0x005340A0,
        "decb00baeedd9291a19c1746fb58d8114c979e3f622c78567143f19b515d89b1",
    ),
    "dmConnSmExecute_dispatch_tail": (
        0x005344FA,
        0x00534532,
        "80294c9e8e8462f412813b8fb7711f795d654d9dd6344b2cda45e8c88e145dd1",
    ),
    "WsfBufAlloc": (
        0x00530446,
        0x005304D4,
        "307ff7ddc2830031087eff4c703949a9974deb2e81efe9cd4334b06c35d57d48",
    ),
    "WsfBufFree": (
        0x005304D4,
        0x00530512,
        "6148f827458d86f257dc4ac8eab53f4eeb9372912249d1181fc835861b5a058f",
    ),
}

EXPECTED_BOUNDED_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_dm_sec_lesc_message_handler",
    "open_cfw_cordio_dm_sec_generate_ecc_key_request",
    "open_cfw_cordio_dm_sec_set_ecc_key",
    "open_cfw_cordio_dm_sec_get_ecc_key",
    "open_cfw_cordio_dm_sec_compare_response",
    "open_cfw_cordio_dm_sec_get_compare_value",
    "open_cfw_cordio_dm_sec_lesc_init",
}
EXPECTED_BOUNDED_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_dm_sec_lesc.c",
    "size": 5696,
    "sha256": "df7f4a7c643703ce6363f18810a01b50de86853a254abab2e3d50b8a4cf2ffe8",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c dm_sec_lesc.c linked surface",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-dm-sec-lesc-source-recovery.md",
}
EXPECTED_DM_SEC_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_dm_sec_hci_handler",
    "open_cfw_cordio_dm_sec_message_handler",
    "open_cfw_cordio_dm_sec_smp_callback_execute",
    "open_cfw_cordio_dm_sec_auth_response",
    "open_cfw_cordio_dm_sec_init",
    "open_cfw_cordio_dm_sec_get_local_csrk",
    "open_cfw_cordio_dm_sec_get_local_irk",
    "open_cfw_cordio_dm_sec_reset",
}
EXPECTED_DM_SEC_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_dm_sec.c",
    "size": 9140,
    "sha256": "4198e5030e71becbc8de4697984172a6730c140ecbd165183451dc6260e928d9",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c dm_sec.c linked surface",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-dm-sec-source-recovery.md",
}
EXPECTED_DM_SEC_SLAVE_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_dm_sec_slave_pair_response",
    "open_cfw_cordio_dm_sec_slave_request",
    "open_cfw_cordio_dm_sec_slave_ltk_response",
}
EXPECTED_DM_SEC_MASTER_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_dm_sec_master_smp_encrypt_request",
    "open_cfw_cordio_dm_sec_master_pair_request",
    "open_cfw_cordio_dm_sec_master_encrypt_request",
}
EXPECTED_DM_SEC_ROLES_SOURCE_BASE = {
    "path": "components/apollo_main/core_overlay/cordio_dm_sec_roles.c",
    "size": 5640,
    "sha256": "95636a5ef5a28805aef2467868c3e0551d1da6c7d889c11d01fe32c3255810ad",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c dm_sec_slave.c and dm_sec_master.c linked surfaces",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
}
EXPECTED_DM_SEC_SLAVE_PRODUCTION_SOURCE = {
    **EXPECTED_DM_SEC_ROLES_SOURCE_BASE,
    "evidence": "docs/research/cordio-dm-sec-slave-source-recovery.md",
}
EXPECTED_DM_SEC_MASTER_PRODUCTION_SOURCE = {
    **EXPECTED_DM_SEC_ROLES_SOURCE_BASE,
    "evidence": "docs/research/cordio-dm-sec-master-source-recovery.md",
}
EXPECTED_SMP_DB_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smp_db_start_service_timer",
    "open_cfw_cordio_smp_db_record_in_use",
    "open_cfw_cordio_smp_db_add_device",
    "open_cfw_cordio_smp_db_get_record",
    "open_cfw_cordio_smp_db_init",
    "open_cfw_cordio_smp_db_get_pairing_disabled_time",
    "open_cfw_cordio_smp_db_set_failure_count",
    "open_cfw_cordio_smp_db_get_failure_count",
    "open_cfw_cordio_smp_db_max_attempt_reached",
    "open_cfw_cordio_smp_db_pairing_failed",
    "open_cfw_cordio_smp_db_service",
}
EXPECTED_SMP_DB_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_db.c",
    "size": 11087,
    "sha256": "e103f1e933f1d7bff5939c2e013162de68bace7298320d879bddd5f5859c5cb5",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smp_db.c linked surface",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-db-source-recovery.md",
}
EXPECTED_SMP_MAIN_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smp_main_packet_length",
    "open_cfw_cordio_smp_main_ccb_by_connection_id",
    "open_cfw_cordio_smp_main_ccb_by_handle",
    "open_cfw_cordio_smp_main_state_idle",
    "open_cfw_cordio_smp_main_send_packet",
    "open_cfw_cordio_smp_main_l2c_data_callback",
    "open_cfw_cordio_smp_main_l2c_control_callback",
    "open_cfw_cordio_smp_main_resume_attempts",
    "open_cfw_cordio_smp_main_dm_connection_callback",
    "open_cfw_cordio_smp_main_calculate_c1_part1",
    "open_cfw_cordio_smp_main_calculate_c1_part2",
    "open_cfw_cordio_smp_main_calculate_s1",
    "open_cfw_cordio_smp_main_generate_ltk",
    "open_cfw_cordio_smp_main_message_allocate",
    "open_cfw_cordio_smp_main_dm_message_send",
    "open_cfw_cordio_smp_main_get_sc_security_level",
    "open_cfw_cordio_smp_main_dm_lesc_enabled",
    "open_cfw_cordio_smp_main_dm_get_stk",
    "open_cfw_cordio_smp_main_handler",
    "open_cfw_cordio_smp_main_dm_encrypt_indication",
    "open_cfw_cordio_smp_main_handler_init",
}
EXPECTED_SMP_MAIN_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_main.c",
    "size": 29363,
    "sha256": "ea5f2e24d9eb9ab36365a41280464e825dd03049acf5e634b5b13385b4178c70",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smp_main.c linked surface with the Ambiq stale-AES queue fix",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-main-source-recovery.md",
}
EXPECTED_SMP_SC_MAIN_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smp_sc_allocate_scratch_buffers",
    "open_cfw_cordio_smp_sc_free_scratch_buffers",
    "open_cfw_cordio_smp_sc_cmac",
    "open_cfw_cordio_smp_sc_allocate",
    "open_cfw_cordio_smp_sc_calculate_f4",
    "open_cfw_cordio_smp_sc_init",
    "open_cfw_cordio_smp_sc_cat",
    "open_cfw_cordio_smp_sc_cat128",
    "open_cfw_cordio_smp_sc_send_public_key",
    "open_cfw_cordio_smp_sc_send_dh_key_check",
    "open_cfw_cordio_smp_sc_send_random",
    "open_cfw_cordio_smp_sc_send_pairing_confirm",
    "open_cfw_cordio_smp_sc_get_passkey_bit",
    "open_cfw_cordio_smp_sc_cancel_with_reattempt",
    "open_cfw_cordio_smp_sc_fail_with_reattempt",
    "open_cfw_cordio_smp_sc_event_string",
    "open_cfw_cordio_smp_sc_state_string",
    "open_cfw_cordio_smp_sc_log_byte_array",
}
EXPECTED_SMP_SC_MAIN_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_sc_main.c",
    "size": 22793,
    "sha256": "14b8afa598b7a0053b23312db689ba36a259dad542f568af607e1d89eb5404ef",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smp_sc_main.c linked surface with a bounded short-line trace fix",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-sc-main-source-recovery.md",
}
EXPECTED_SMP_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smp_act_start_response_timer",
    "open_cfw_cordio_smp_act_none",
    "open_cfw_cordio_smp_act_cleanup_core",
    "open_cfw_cordio_smp_act_cleanup",
    "open_cfw_cordio_smp_act_send_pairing_failed",
    "open_cfw_cordio_smp_act_pairing_failed",
    "open_cfw_cordio_smp_act_security_request_timeout",
    "open_cfw_cordio_smp_act_pairing_cancel",
    "open_cfw_cordio_smp_act_store_pin",
    "open_cfw_cordio_smp_act_process_pairing",
    "open_cfw_cordio_smp_act_authentication_request",
    "open_cfw_cordio_smp_act_confirm_calculate_one",
    "open_cfw_cordio_smp_act_confirm_calculate_two",
    "open_cfw_cordio_smp_act_send_confirm",
    "open_cfw_cordio_smp_act_verify_calculate_one",
    "open_cfw_cordio_smp_act_verify_calculate_two",
    "open_cfw_cordio_smp_act_send_key",
    "open_cfw_cordio_smp_act_receive_key",
    "open_cfw_cordio_smp_act_max_attempts",
    "open_cfw_cordio_smp_act_attempt_received",
    "open_cfw_cordio_smp_act_notify_attempts_failure",
    "open_cfw_cordio_smp_act_notify_timeout_failure",
    "open_cfw_cordio_smp_act_check_attempts",
    "open_cfw_cordio_smp_act_pairing_complete",
    "open_cfw_cordio_smp_act_execute",
}
EXPECTED_SMP_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_act.c",
    "size": 35811,
    "sha256": "f73e9d76970e3e66009d82c75bf07b3e2c8a2c1602ad76f52af024af40014bde",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smp_act.c linked surface",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-act-source-recovery.md",
}
EXPECTED_SMP_SC_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smp_sc_act_cat_initiator_address",
    "open_cfw_cordio_smp_sc_act_cat_responder_address",
    "open_cfw_cordio_smp_sc_act_process_pairing",
    "open_cfw_cordio_smp_sc_act_authentication_request",
    "open_cfw_cordio_smp_sc_act_cleanup",
    "open_cfw_cordio_smp_sc_act_pairing_failed",
    "open_cfw_cordio_smp_sc_act_pairing_cancel",
    "open_cfw_cordio_smp_sc_act_authentication_select",
    "open_cfw_cordio_smp_sc_act_passkey_setup",
    "open_cfw_cordio_smp_sc_act_jwnc_calculate_f4",
    "open_cfw_cordio_smp_sc_act_jwnc_calculate_g2",
    "open_cfw_cordio_smp_sc_act_jwnc_display",
    "open_cfw_cordio_smp_sc_act_passkey_receive",
    "open_cfw_cordio_smp_sc_act_passkey_send",
    "open_cfw_cordio_smp_sc_act_calculate_shared_secret",
    "open_cfw_cordio_smp_sc_act_calculate_f5_t",
    "open_cfw_cordio_smp_sc_act_calculate_f5_mac",
    "open_cfw_cordio_smp_sc_act_calculate_f5_ltk",
    "open_cfw_cordio_smp_sc_act_calculate_f6_ea",
    "open_cfw_cordio_smp_sc_act_calculate_f6_eb",
}
EXPECTED_SMP_SC_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_sc_act.c",
    "size": 39464,
    "sha256": "2b7977d36ee69f70159a51538dc41b9c447bf572a0e7f4932a5f2965454396cf",
    "license": "Apache-2.0",
    "origin": (
        "production adapter of the authenticated AmbiqSuite R4.4.1 "
        "Packetcraft Cordio smp_sc_act.c linked surface, preserving the "
        "stock G2 R4/r19 no-I/O branch"
    ),
    "upstream": "third_party/cordio",
    "upstream_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
    "evidence": "docs/research/cordio-smp-sc-act-source-recovery.md",
}
EXPECTED_SMPI_SC_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpi_sc_authentication_select",
    "open_cfw_cordio_smpi_sc_send_public_key",
    "open_cfw_cordio_smpi_sc_jwnc_setup",
    "open_cfw_cordio_smpi_sc_jwnc_send_random",
    "open_cfw_cordio_smpi_sc_jwnc_calculate_f4",
    "open_cfw_cordio_smpi_sc_jwnc_calculate_g2",
    "open_cfw_cordio_smpi_sc_passkey_calculate_ca",
    "open_cfw_cordio_smpi_sc_passkey_calculate_cb",
    "open_cfw_cordio_smpi_sc_passkey_send_confirm",
    "open_cfw_cordio_smpi_sc_passkey_send_random",
    "open_cfw_cordio_smpi_sc_passkey_check",
    "open_cfw_cordio_smpi_sc_oob_calculate_cb",
    "open_cfw_cordio_smpi_sc_oob_send_random",
    "open_cfw_cordio_smpi_sc_oob_process_random",
    "open_cfw_cordio_smpi_sc_dh_key_check_send",
    "open_cfw_cordio_smpi_sc_dh_key_check_verify",
}
EXPECTED_SMPI_SC_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smpi_sc_act.c",
    "size": 18850,
    "sha256": "f7ba436496256178a0b6c49fa2dfcfaba8a48984a13282063e1d997ddff2dac8",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smpi_sc_act.c linked surface with the stock r20/R4 keyReady transition",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smpi-sc-act-source-recovery.md",
}
EXPECTED_SMPR_SC_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpr_sc_store_pin",
    "open_cfw_cordio_smpr_sc_send_public_key",
    "open_cfw_cordio_smpr_sc_jwnc_setup",
    "open_cfw_cordio_smpr_sc_jwnc_send_confirm",
    "open_cfw_cordio_smpr_sc_jwnc_calculate_g2",
    "open_cfw_cordio_smpr_sc_jwnc_display",
    "open_cfw_cordio_smpr_sc_passkey_store_confirm",
    "open_cfw_cordio_smpr_sc_passkey_calculate_cb",
    "open_cfw_cordio_smpr_sc_passkey_store_confirm_and_calculate_cb",
    "open_cfw_cordio_smpr_sc_passkey_store_pin_and_calculate_cb",
    "open_cfw_cordio_smpr_sc_passkey_send_confirm",
    "open_cfw_cordio_smpr_sc_passkey_calculate_ca",
    "open_cfw_cordio_smpr_sc_passkey_send_random",
    "open_cfw_cordio_smpr_sc_oob_setup",
    "open_cfw_cordio_smpr_sc_oob_calculate_ca",
    "open_cfw_cordio_smpr_sc_oob_send_random",
    "open_cfw_cordio_smpr_sc_store_dh_key_check",
    "open_cfw_cordio_smpr_sc_wait_dh_key_check",
    "open_cfw_cordio_smpr_sc_calculate_dh_key",
    "open_cfw_cordio_smpr_sc_dh_key_check_send",
}
EXPECTED_SMPR_SC_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smpr_sc_act.c",
    "size": 17715,
    "sha256": "9aeeb7deca5ddba366291e2b19daeb4c06f8d1feb4915dc863b50b5dd1d82c26",
    "license": "Apache-2.0",
    "origin": "production adapter of the authenticated Packetcraft Cordio r20.05c smpr_sc_act.c linked surface with the stock r20/R4 keyReady transition",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smpr-sc-act-source-recovery.md",
}
EXPECTED_SMPI_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpi_pair_request",
    "open_cfw_cordio_smpi_check_security_request",
    "open_cfw_cordio_smpi_process_security_request",
    "open_cfw_cordio_smpi_process_pair_response",
    "open_cfw_cordio_smpi_process_pair_confirm",
    "open_cfw_cordio_smpi_confirm_verify",
    "open_cfw_cordio_smpi_stk_encrypt",
    "open_cfw_cordio_smpi_setup_key_distribution",
    "open_cfw_cordio_smpi_receive_key",
    "open_cfw_cordio_smpi_send_key",
}
EXPECTED_SMPI_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smpi_act.c",
    "size": 16690,
    "sha256": "0a19fb3adddd4ae6b9a71a4b012b2dea23cc3999938e3e6be1f8da4772a538df",
    "license": "Apache-2.0",
    "origin": "production adapter of authenticated Packetcraft Cordio r20.05c smpi_act.c linked legacy pairing actions with the stock r20/R4 keyReady transition",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smpi-act-source-recovery.md",
}
EXPECTED_SMPR_ACT_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpr_send_security_request",
    "open_cfw_cordio_smpr_process_pair_request",
    "open_cfw_cordio_smpr_send_pair_response",
    "open_cfw_cordio_smpr_process_pair_confirm",
    "open_cfw_cordio_smpr_process_pair_confirm_calculate",
    "open_cfw_cordio_smpr_confirm_verify",
    "open_cfw_cordio_smpr_send_pair_random",
    "open_cfw_cordio_smpr_send_key",
    "open_cfw_cordio_smpr_setup_key_distribution",
    "open_cfw_cordio_smpr_receive_key",
}
EXPECTED_SMPR_ACT_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smpr_act.c",
    "size": 16630,
    "sha256": "f01027a9e7bc6e6af2bf4add1838cf873e1e90b6c2ee57e419e3a82f02dac5ed",
    "license": "Apache-2.0",
    "origin": "production adapter of authenticated Packetcraft Cordio r20.05c smpr_act.c linked legacy pairing actions with the stock r20/R4 keyReady transition",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smpr-act-source-recovery.md",
}
EXPECTED_SMP_SC_SM_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpi_sc_initialize",
    "open_cfw_cordio_smpi_sc_state_string",
    "open_cfw_cordio_smpr_sc_initialize",
    "open_cfw_cordio_smpr_sc_state_string",
}
EXPECTED_SMP_SC_SM_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_sc_sm.c",
    "size": 16284,
    "sha256": "6bc75e8320b1ceabff762f64ba655b12f5a18c8539a5258a5c8d61f08d2a8739",
    "license": "Apache-2.0",
    "origin": "production C reconstruction of Packetcraft Cordio r20.05c smpi_sc_sm.c and smpr_sc_sm.c linked state-machine interfaces and dispatch ABI",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-sc-state-machines-source-recovery.md",
}
EXPECTED_SMP_LEGACY_SM_PRODUCTION_FUNCTIONS = {
    "open_cfw_cordio_smpi_initialize",
    "open_cfw_cordio_smpr_initialize",
}
EXPECTED_SMP_LEGACY_SM_PRODUCTION_SOURCE = {
    "path": "components/apollo_main/core_overlay/cordio_smp_legacy_sm.c",
    "size": 8797,
    "sha256": "9a90b81d01f83ca8daa21cf645594188a6e7feb61a40f61b2afee089063d5c01",
    "license": "Apache-2.0",
    "origin": "production C reconstruction of Packetcraft Cordio r20.05c smpi_sm.c and smpr_sm.c linked legacy state-machine interfaces and dispatch ABI",
    "upstream": "third_party/cordio",
    "upstream_commit": EXPECTED_COMMIT,
    "evidence": "docs/research/cordio-smp-legacy-state-machines-source-recovery.md",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_object_sha1(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Cordio snapshot verification failed: {message}")


def image_slice(image: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    require(0 <= first < last <= len(image), "G2 run span is outside the image")
    return image[first:last]


def verify_provenance() -> dict[str, Any]:
    raw = PROVENANCE.read_bytes()
    require(len(raw) == EXPECTED_PROVENANCE_SIZE, "provenance size changed")
    require(sha256(raw) == EXPECTED_PROVENANCE_SHA256, "provenance bytes changed")
    value = json.loads(raw)
    require(
        set(value) == {"schema_version", "component", "license", "upstream", "selection", "g2_boundary", "files"},
        "provenance schema changed",
    )
    require(value["schema_version"] == 1, "schema version changed")
    require(value["component"] == "Packetcraft Cordio", "component changed")
    require(value["license"] == "Apache-2.0", "license changed")

    upstream = value["upstream"]
    require(upstream["selected_release"] == "r20.05c", "release choice changed")
    require(upstream["selected_ref"] == EXPECTED_COMMIT, "selected ref changed")
    require(upstream["tag_object"] is None, "unsupported tag-object claim")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(upstream["parent_commit"] == EXPECTED_PARENT, "parent changed")
    require(upstream["commit_subject"] == "r20.05c", "release subject changed")
    require(upstream["commit_signature"]["present"] is False, "unsupported signature claim")
    require(upstream["tree_closure_path"] == "upstream/trees.json", "tree closure path changed")
    require(upstream["tree_closure_size"] == EXPECTED_TREE_CLOSURE_SIZE, "stored tree closure size changed")
    require(upstream["tree_closure_sha256"] == EXPECTED_TREE_CLOSURE_SHA256, "stored tree closure digest changed")
    require(upstream["tree_object_count"] == len(EXPECTED_TREE_OBJECTS), "tree object count changed")

    selection = value["selection"]
    require(selection["exact_g2_checkout_proven"] is False, "unsupported whole-tree claim")
    require(selection["selected_file_count"] == 41, "selected file count changed")
    require(selection["selected_c_source_count"] == 5, "source count changed")
    require(selection["selected_header_count"] == 35, "header count changed")
    require(selection["selected_license_count"] == 1, "license count changed")
    require(selection["root_source_paths"] == ROOT_SOURCE_PATHS, "root source set changed")
    require(selection["source_records_sha256"] == EXPECTED_RECORDS_SHA256, "stored records digest changed")
    require(selection["integration_status"] == "authenticated and verified offline; no production registration", "integration boundary changed")
    exclusions = "\n".join(selection["excluded_features"])
    for phrase in ("Ambiq FreeRTOS", "Even platform/ble", "controller and radio"):
        require(phrase in exclusions, f"required exclusion missing: {phrase}")

    boundary = value["g2_boundary"]
    require(boundary["whole_stack_identity"] == "unresolved", "whole-stack identity overclaimed")
    require(boundary["bounded_equivalence_interval"]["releases"] == EXPECTED_RELEASES, "release interval changed")
    require("complete G2 Cordio vendor tree" in boundary["bounded_equivalence_interval"]["not_an_upper_bound_for"], "interval qualification changed")
    port = boundary["port_boundary"]
    require(port["g2_source_path"] == "wsf/sources/port/freertos/wsf_buf.c", "G2 WSF port changed")
    require(port["vendored_comparator"] == "wsf/sources/targets/baremetal/wsf_buf.c", "WSF comparator changed")
    require(port["ambiq_hci_port"] == "excluded and unresolved", "Ambiq HCI boundary changed")
    require(port["even_mram_platform_glue"] == "excluded and unresolved", "Even glue boundary changed")
    return value


def verify_commit_object(provenance: dict[str, Any]) -> None:
    record = provenance["upstream"]
    payload = (HERE / record["commit_object_payload_path"]).read_bytes()
    require(len(payload) == EXPECTED_COMMIT_SIZE, "commit payload size changed")
    require(sha256(payload) == EXPECTED_COMMIT_SHA256, "commit payload changed")
    require(git_object_sha1("commit", payload) == EXPECTED_COMMIT, "commit object ID changed")
    require(payload.startswith(f"tree {EXPECTED_TREE}\nparent {EXPECTED_PARENT}\n".encode()), "commit tree/parent chain changed")
    require(payload.endswith(b"\n\nr20.05c\n"), "commit subject changed")
    require(b"\ngpgsig " not in payload, "unexpected signature appeared")


def verify_tree_closure(
    provenance: dict[str, Any], closure: dict[str, Any] | None = None
) -> None:
    """Rebuild required Git trees and prove every selected path membership."""
    if closure is None:
        record = provenance["upstream"]
        raw = (HERE / record["tree_closure_path"]).read_bytes()
        require(len(raw) == EXPECTED_TREE_CLOSURE_SIZE, "tree closure size changed")
        require(sha256(raw) == EXPECTED_TREE_CLOSURE_SHA256, "tree closure bytes changed")
        closure = json.loads(raw)

    require(set(closure) == {"schema_version", "root_tree", "trees"}, "tree closure schema changed")
    require(closure["schema_version"] == 1, "tree closure schema version changed")
    require(closure["root_tree"] == EXPECTED_TREE, "tree closure root changed")

    trees: dict[str, list[dict[str, str]]] = {}
    for tree in closure["trees"]:
        require(set(tree) == {"oid", "entries"}, "tree record schema changed")
        oid = tree["oid"]
        require(isinstance(oid, str) and len(oid) == 40, "invalid tree object ID")
        require(oid not in trees, f"duplicate tree object {oid}")
        payload = bytearray()
        names: set[str] = set()
        for entry in tree["entries"]:
            require(set(entry) == {"mode", "type", "oid", "name"}, f"tree entry schema changed in {oid}")
            mode = entry["mode"]
            kind = entry["type"]
            child_oid = entry["oid"]
            name = entry["name"]
            require((mode, kind) in {("040000", "tree"), ("100644", "blob")}, f"unsupported tree entry kind in {oid}")
            require(isinstance(child_oid, str) and len(child_oid) == 40 and all(ch in "0123456789abcdef" for ch in child_oid), f"invalid child object ID in {oid}")
            require(isinstance(name, str) and name and "/" not in name and "\0" not in name, f"invalid tree entry name in {oid}")
            require(name not in names, f"duplicate tree entry {name!r} in {oid}")
            names.add(name)
            raw_mode = "40000" if mode == "040000" else mode
            payload.extend(f"{raw_mode} {name}".encode("utf-8"))
            payload.append(0)
            payload.extend(bytes.fromhex(child_oid))
        require(git_object_sha1("tree", bytes(payload)) == oid, f"tree object ID mismatch: {oid}")
        trees[oid] = tree["entries"]

    require(set(trees) == EXPECTED_TREE_OBJECTS, "required tree object set changed")
    for source in provenance["files"]:
        tree_oid = EXPECTED_TREE
        parts = source["upstream_path"].split("/")
        for index, part in enumerate(parts):
            matches = [entry for entry in trees[tree_oid] if entry["name"] == part]
            require(len(matches) == 1, f"path is absent from commit tree: {source['upstream_path']}")
            entry = matches[0]
            if index < len(parts) - 1:
                require(entry["type"] == "tree", f"non-tree path component: {source['upstream_path']}")
                require(entry["oid"] in trees, f"missing path tree object: {source['upstream_path']}")
                tree_oid = entry["oid"]
            else:
                require(entry["type"] == "blob", f"selected path is not a blob: {source['upstream_path']}")
                require(entry["mode"] == source["git_mode"], f"tree mode mismatch: {source['upstream_path']}")
                require(entry["oid"] == source["git_blob_sha1"], f"tree blob mismatch: {source['upstream_path']}")


def verify_source_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require([item["local_path"] for item in records] == EXPECTED_SOURCE_PATHS, "source order/path set changed")
    require(canonical_sha256(records) == EXPECTED_RECORDS_SHA256, "source records changed")
    by_path = {item["local_path"]: item for item in records}
    require({path: by_path[path]["git_blob_sha1"] for path in ROOT_SOURCE_PATHS} == EXPECTED_ORACLE_BLOBS, "source-oracle blob set changed")
    for item in records:
        require(set(item) == {"local_path", "upstream_path", "git_mode", "size", "sha256", "git_blob_sha1"}, f"record schema changed for {item['local_path']}")
        require(item["local_path"] == item["upstream_path"], f"path remapping changed for {item['local_path']}")
        require(item["git_mode"] == "100644", f"Git mode changed for {item['local_path']}")
        path = HERE / item["local_path"]
        require(path.is_file(), f"source file missing: {item['local_path']}")
        data = path.read_bytes()
        require(not (path.stat().st_mode & stat.S_IXUSR), f"source became executable: {item['local_path']}")
        require(len(data) == item["size"], f"size changed: {item['local_path']}")
        require(sha256(data) == item["sha256"], f"SHA-256 changed: {item['local_path']}")
        require(git_object_sha1("blob", data) == item["git_blob_sha1"], f"Git blob changed: {item['local_path']}")

    license_record = by_path["LICENSE.md"]
    require(license_record["size"] == 562, "license size changed")
    require(license_record["sha256"] == "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd", "license SHA-256 changed")
    require(license_record["git_blob_sha1"] == "5fe50d5491f1166292380f46c8beae44ca83cadb", "license Git blob changed")

    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual == set(EXPECTED_SOURCE_PATHS) | METADATA_PATHS, "snapshot file set changed")
    require((HERE / ".gitattributes").read_bytes() == b"* -text whitespace=-trailing-space\n", "snapshot byte/whitespace attributes changed")


def verify_configuration_and_firmware(provenance: dict[str, Any]) -> None:
    boundary = provenance["g2_boundary"]
    config = (HERE / boundary["recovered_config_header"]).read_bytes()
    require(len(config) == EXPECTED_CONFIG_SIZE, "G2 config size changed")
    require(sha256(config) == EXPECTED_CONFIG_SHA256, "G2 config changed")
    for macro in (
        b"#define DM_CONN_MAX 3\n",
        b"#define WSF_BUF_FREE_CHECK_ASSERT 1\n",
        b"#define WSF_BUF_STATS 0\n",
        b"#define WSF_BUF_STATS_HIST 0\n",
        b"#define WSF_OS_DIAG 0\n",
    ):
        require(config.count(macro) == 1, f"missing exact config macro {macro!r}")

    cfg = boundary["proven_configuration"]
    require(cfg["DM_CONN_MAX"] == 3 and cfg["DM_CONN_ID_NONE"] == 0, "DM connection config changed")
    require(cfg["ATT_client_record_stride"] == 2, "ATT client record layout changed")
    require(cfg["WSF_BUF_FREE_CHECK_ASSERT"] is True, "WSF free check changed")
    require(cfg["WSF_BUF_STATS"] is False and cfg["WSF_BUF_STATS_HIST"] is False, "WSF stats config changed")
    require(cfg["WSF_OS_DIAG"] is False, "WSF diagnostic config changed")
    require(cfg["WSF_buffer_pool_descriptor_bytes"] == 12, "WSF descriptor layout changed")
    require(cfg["WSF_buffer_free_list_pointer_offset"] == 8, "WSF free-list offset changed")
    require(cfg["WSF_buffer_free_marker"] == "0xFAABD00D", "WSF free marker changed")

    require(b"#define DM_CONN_MAX              3\n" in (HERE / "ble-host/sources/stack/cfg/cfg_stack.h").read_bytes(), "upstream DM_CONN_MAX template changed")
    require(b"#define APP_DB_NUM_RECS 3\n" in (HERE / "ble-profiles/include/app_cfg.h").read_bytes(), "upstream app DB template changed")
    require(b"#define WSF_BUF_FREE_CHECK_ASSERT TRUE\n" in (HERE / "wsf/include/wsf_buf.h").read_bytes(), "upstream WSF free-check template changed")
    require(b"#define WSF_BUF_STATS FALSE\n" in (HERE / "wsf/include/wsf_buf.h").read_bytes(), "upstream WSF stats template changed")
    require(b"#define WSF_OS_DIAG                             FALSE\n" in (HERE / "wsf/include/wsf_os.h").read_bytes(), "upstream WSF OS template changed")

    image = IMAGE.read_bytes()
    require(len(image) == EXPECTED_IMAGE_SIZE, "official G2 image size changed")
    require(sha256(image) == EXPECTED_IMAGE_SHA256, "official G2 image identity changed")
    for label, (start, end, expected) in EXPECTED_CODE_SPANS.items():
        require(sha256(image_slice(image, start, end)) == expected, f"{label} firmware evidence changed")
    marker = struct.unpack("<I", image_slice(image, 0x00530534, 0x00530538))[0]
    require(marker == 0xFAABD00D, "WsfBufFree marker evidence changed")
    require(image_slice(image, 0x0053049C, 0x005304A0) == bytes.fromhex("40f24110"), "WsfBufAlloc source-line evidence changed")


def generated_build_path(path: Path, root: Path) -> bool:
    """Return whether ``path`` is generated component output, not configuration."""
    relative = path.relative_to(root)
    return any(part == "build" or part.startswith("build-") for part in relative.parts)


def verify_bounded_production_adapter(overlay_path: Path) -> None:
    """Permit only the pinned local Cordio adapters to cite this oracle."""
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    records = [
        record
        for record in (
            overlay.get("relocated_leaves", []) + overlay.get("in_place_leaves", [])
        )
        if record.get("source", {}).get("upstream") == "third_party/cordio"
    ]
    require(
        {record.get("function") for record in records}
        == EXPECTED_BOUNDED_PRODUCTION_FUNCTIONS
        | EXPECTED_DM_SEC_PRODUCTION_FUNCTIONS
        | EXPECTED_DM_SEC_SLAVE_PRODUCTION_FUNCTIONS
        | EXPECTED_DM_SEC_MASTER_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_DB_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_MAIN_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_SC_MAIN_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_SC_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMPI_SC_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMPR_SC_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMPI_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMPR_ACT_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_SC_SM_PRODUCTION_FUNCTIONS
        | EXPECTED_SMP_LEGACY_SM_PRODUCTION_FUNCTIONS,
        "snapshot is production-configured outside the bounded Cordio adapter",
    )
    require(len(records) == 178, "bounded Cordio production function count changed")
    for record in records:
        function = record.get("function")
        if function in EXPECTED_BOUNDED_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_BOUNDED_PRODUCTION_SOURCE
        elif function in EXPECTED_DM_SEC_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_DM_SEC_PRODUCTION_SOURCE
        elif function in EXPECTED_DM_SEC_SLAVE_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_DM_SEC_SLAVE_PRODUCTION_SOURCE
        elif function in EXPECTED_DM_SEC_MASTER_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_DM_SEC_MASTER_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_DB_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_DB_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_MAIN_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_MAIN_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_SC_MAIN_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_SC_MAIN_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_SC_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_SC_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMPI_SC_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMPI_SC_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMPR_SC_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMPR_SC_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMPI_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMPI_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMPR_ACT_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMPR_ACT_PRODUCTION_SOURCE
        elif function in EXPECTED_SMP_SC_SM_PRODUCTION_FUNCTIONS:
            expected_source = EXPECTED_SMP_SC_SM_PRODUCTION_SOURCE
        else:
            expected_source = EXPECTED_SMP_LEGACY_SM_PRODUCTION_SOURCE
        require(
            record.get("source") == expected_source,
            f"bounded Cordio source contract changed: {record.get('function')}",
        )

    for expected_source in (
        EXPECTED_BOUNDED_PRODUCTION_SOURCE,
        EXPECTED_DM_SEC_PRODUCTION_SOURCE,
        EXPECTED_DM_SEC_SLAVE_PRODUCTION_SOURCE,
        EXPECTED_DM_SEC_MASTER_PRODUCTION_SOURCE,
        EXPECTED_SMP_DB_PRODUCTION_SOURCE,
        EXPECTED_SMP_MAIN_PRODUCTION_SOURCE,
        EXPECTED_SMP_SC_MAIN_PRODUCTION_SOURCE,
        EXPECTED_SMP_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMP_SC_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMPI_SC_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMPR_SC_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMPI_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMPR_ACT_PRODUCTION_SOURCE,
        EXPECTED_SMP_SC_SM_PRODUCTION_SOURCE,
        EXPECTED_SMP_LEGACY_SM_PRODUCTION_SOURCE,
    ):
        source_path = ROOT / expected_source["path"]
        require(source_path.is_file(), "bounded Cordio production source is missing")
        source = source_path.read_bytes()
        require(
            len(source) == expected_source["size"],
            "bounded Cordio production source size changed",
        )
        require(
            sha256(source) == expected_source["sha256"],
            "bounded Cordio production source hash changed",
        )


def verify_production_exclusion() -> None:
    """Reject snapshot compilation; allow one pinned local source adaptation."""
    reference_tokens = (
        "third_party/cordio",
        "CORDIO_DIR",
        "atts_csf.c",
        "dm_conn_sm.c",
        "smp_db.c",
        "app_db.c",
        "wsf_buf.c",
    )

    # Verification-only registration is permitted.  Keep it exact so any use
    # of the snapshot directory or its source-oracle leaves by a compiler,
    # linker, component, or firmware recipe still fails closed.
    makefile = ROOT / "Makefile"
    if makefile.is_file():
        allowed_makefile_references = {
            "CORDIO_DIR := third_party/cordio",
            "\t$(PYTHON) $(CORDIO_DIR)/verify_snapshot.py",
        }
        for line_number, line in enumerate(
            makefile.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if any(token in line for token in reference_tokens):
                require(
                    line in allowed_makefile_references,
                    f"snapshot is production-configured by Makefile:{line_number}",
                )

    configured: set[Path] = set()
    manifests = ROOT / "manifests"
    if manifests.is_dir():
        configured.update(
            path
            for path in manifests.rglob("*")
            if path.is_file() and not generated_build_path(path, manifests)
        )

    component_suffixes = {
        ".asm",
        ".c",
        ".h",
        ".json",
        ".ld",
        ".lds",
        ".mk",
        ".py",
        ".s",
    }
    components = ROOT / "components"
    if components.is_dir():
        configured.update(
            path
            for path in components.rglob("*")
            if path.is_file()
            and not generated_build_path(path, components)
            and (path.suffix.lower() in component_suffixes or path.name == "Makefile")
        )

    configured.update(
        {
            ROOT / "tools" / "apollo_overlay.py",
            ROOT / "tools" / "open_cfw.py",
        }
    )
    overlay_path = ROOT / "components/apollo_main/core_overlay/overlay.json"
    bounded_source_paths = {
        ROOT / source["path"] for source in (
            EXPECTED_BOUNDED_PRODUCTION_SOURCE,
            EXPECTED_DM_SEC_PRODUCTION_SOURCE,
            EXPECTED_DM_SEC_SLAVE_PRODUCTION_SOURCE,
            EXPECTED_DM_SEC_MASTER_PRODUCTION_SOURCE,
            EXPECTED_SMP_DB_PRODUCTION_SOURCE,
            EXPECTED_SMP_MAIN_PRODUCTION_SOURCE,
            EXPECTED_SMP_SC_MAIN_PRODUCTION_SOURCE,
            EXPECTED_SMP_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMP_SC_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMPI_SC_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMPR_SC_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMPI_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMPR_ACT_PRODUCTION_SOURCE,
            EXPECTED_SMP_SC_SM_PRODUCTION_SOURCE,
            EXPECTED_SMP_LEGACY_SM_PRODUCTION_SOURCE,
        )
    }
    for path in sorted(configured):
        if not path.is_file():
            continue
        if path == overlay_path:
            verify_bounded_production_adapter(overlay_path)
            continue
        if path in bounded_source_paths:
            continue
        content = path.read_text(encoding="utf-8")
        require(
            not any(token in content for token in reference_tokens),
            f"snapshot is production-configured by {path.relative_to(ROOT)}",
        )


def main() -> int:
    provenance = verify_provenance()
    verify_commit_object(provenance)
    verify_tree_closure(provenance)
    verify_source_files(provenance)
    verify_configuration_and_firmware(provenance)
    verify_production_exclusion()
    print("Packetcraft Cordio r20.05c source-oracle snapshot verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

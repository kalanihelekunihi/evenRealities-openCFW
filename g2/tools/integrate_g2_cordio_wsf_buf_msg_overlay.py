#!/usr/bin/env python3
"""Promote the reviewed G2 Cordio WSF buffer and message leaves."""

import argparse
import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_wsf_buf_msg_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)


def linked_selectors_from_map(path: Path, selector_prefix: str) -> tuple:
    """Build deterministic selectors from an already-pinned function ledger."""
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return tuple(
        (
            f"{selector_prefix}_{int(row['source_order']):02d}",
            row["function"],
            int(row["stock_start"], 0),
            int(row["stock_end_exclusive"], 0),
        )
        for row in rows
        if row["stock_status"] == "linked"
    )


HCI_EVT_SELECTORS = linked_selectors_from_map(
    ROOT / "tools/manifests/ambiq-cordio-hci-evt-function-map.tsv", "LINKED"
)
HCI_EVT_INTERNAL_PROVIDERS = {
    function: function for _selector, function, _start, _end in HCI_EVT_SELECTORS
}


MODULES = {
    "buf": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wsf_buf_candidate.c",
        "recorder": "apple-cordio-wsf-buf-record",
        "define": "OPEN_CFW_WSF_BUF_",
        "patch": "replace_cordio_wsf_buf_",
        "region": "cordio_wsf_buf_",
        "evidence": "docs/research/cordio-wsf-buffer-message-source-recovery.md",
        "origin": (
            "clean-room G2 Cordio/Ambiq FreeRTOS WSF buffer implementation over "
            "the authenticated AmbiqSuite 2.5.1 behavior family and retained ABI"
        ),
        "license": "GPL-3.0-only",
        "flag": "-DOPEN_CFW_WSF_BUF_PRODUCTION=1",
        "selectors": (
            ("INIT", "open_cfw_cordio_wsf_buffer_init_candidate", 0x00530364, 0x00530446),
            ("ALLOCATE", "open_cfw_cordio_wsf_buffer_allocate_candidate", 0x00530446, 0x005304D4),
            ("FREE", "open_cfw_cordio_wsf_buffer_free_candidate", 0x005304D4, 0x00530512),
        ),
        "providers": {
            "open_cfw_cordio_wsf_cs_enter_candidate": 0x0052B8A4,
            "open_cfw_cordio_wsf_cs_exit_candidate": 0x0052B8B6,
        },
    },
    "msg": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wsf_msg_candidate.c",
        "recorder": "apple-cordio-wsf-msg-record",
        "define": "OPEN_CFW_WSF_MSG_",
        "patch": "replace_cordio_wsf_msg_",
        "region": "cordio_wsf_msg_",
        "evidence": "docs/research/cordio-wsf-buffer-message-source-recovery.md",
        "origin": (
            "Packetcraft r19.02 Apache-2.0 G2 Cordio WSF message implementation "
            "over the retained WSF queue, task, and promoted buffer ABIs"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_WSF_MSG_PRODUCTION=1",
        "selectors": (
            ("DATA_ALLOCATE", "open_cfw_cordio_wsf_message_data_allocate_candidate", 0x004BF990, 0x004BF99E),
            ("ALLOCATE", "open_cfw_cordio_wsf_message_allocate_candidate", 0x004BF99E, 0x004BF9B0),
            ("FREE", "open_cfw_cordio_wsf_message_free_candidate", 0x004BF9B0, 0x004BF9BA),
            ("SEND", "open_cfw_cordio_wsf_message_send_candidate", 0x004BF9BA, 0x004BF9DE),
            ("ENQUEUE", "open_cfw_cordio_wsf_message_enqueue_candidate", 0x004BF9DE, 0x004BF9EC),
            ("DEQUEUE", "open_cfw_cordio_wsf_message_dequeue_candidate", 0x004BF9EC, 0x004BFA00),
            ("PEEK", "open_cfw_cordio_wsf_message_peek_candidate", 0x004BFA00, 0x004BFA0E),
        ),
        "providers": {
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_wsf_buffer_free_candidate":
                "open_cfw_cordio_wsf_buffer_free_candidate",
            "open_cfw_cordio_wsf_task_message_queue_candidate": 0x0052B97C,
            "open_cfw_cordio_wsf_task_set_ready_candidate": 0x0052B95E,
            "open_cfw_cordio_wsf_queue_enqueue_candidate": 0x00538C24,
            "open_cfw_cordio_wsf_queue_dequeue_candidate": 0x00538C4A,
        },
    },
    "queue": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wsf_queue_candidate.c",
        "recorder": "apple-cordio-wsf-queue-record",
        "define": "OPEN_CFW_WSF_QUEUE_",
        "patch": "replace_cordio_wsf_queue_",
        "region": "cordio_wsf_queue_",
        "evidence": "docs/research/cordio-wsf-os-queue-source-recovery.md",
        "origin": (
            "clean-room G2 Cordio WSF intrusive queue implementation over the "
            "authenticated AmbiqSuite 2.5.1 behavior family"
        ),
        "license": "GPL-3.0-only",
        "flag": "-DOPEN_CFW_WSF_QUEUE_PRODUCTION=1",
        "selectors": (
            ("ENQUEUE", "open_cfw_cordio_wsf_queue_enqueue_candidate", 0x00538C24, 0x00538C4A),
            ("DEQUEUE", "open_cfw_cordio_wsf_queue_dequeue_candidate", 0x00538C4A, 0x00538C6E),
            ("PUSH", "open_cfw_cordio_wsf_queue_push_candidate", 0x00538C6E, 0x00538C8C),
            ("INSERT", "open_cfw_cordio_wsf_queue_insert_candidate", 0x00538C8C, 0x00538CC8),
            ("REMOVE", "open_cfw_cordio_wsf_queue_remove_candidate", 0x00538CC8, 0x00538CF6),
            ("COUNT", "open_cfw_cordio_wsf_queue_count_candidate", 0x00538CF6, 0x00538D16),
        ),
        "providers": {
            "open_cfw_cordio_wsf_cs_enter_candidate":
                "open_cfw_cordio_wsf_cs_enter_candidate",
            "open_cfw_cordio_wsf_cs_exit_candidate":
                "open_cfw_cordio_wsf_cs_exit_candidate",
            "open_cfw_cordio_wsf_queue_enqueue_candidate":
                "open_cfw_cordio_wsf_queue_enqueue_candidate",
            "open_cfw_cordio_wsf_queue_push_candidate":
                "open_cfw_cordio_wsf_queue_push_candidate",
        },
    },
    "os": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wsf_os_candidate.c",
        "recorder": "apple-cordio-wsf-os-record",
        "define": "OPEN_CFW_WSF_OS_",
        "patch": "replace_cordio_wsf_os_",
        "region": "cordio_wsf_os_",
        "evidence": "docs/research/cordio-wsf-os-queue-source-recovery.md",
        "origin": (
            "clean-room G2 Cordio/Ambiq FreeRTOS WSF OS implementation over "
            "the authenticated AmbiqSuite 2.5.1 behavior family and stock ABI"
        ),
        "license": "GPL-3.0-only",
        "flag": "-DOPEN_CFW_WSF_OS_PRODUCTION=1",
        "selectors": (
            ("CS_ENTER", "open_cfw_cordio_wsf_cs_enter_candidate", 0x0052B8A4, 0x0052B8B6),
            ("CS_EXIT", "open_cfw_cordio_wsf_cs_exit_candidate", 0x0052B8B6, 0x0052B8C8),
            ("TASK_LOCK", "open_cfw_cordio_wsf_task_lock_candidate", 0x0052B8C8, 0x0052B8D0),
            ("TASK_UNLOCK", "open_cfw_cordio_wsf_task_unlock_candidate", 0x0052B8D0, 0x0052B8D8),
            ("SET_OS_EVENT", "open_cfw_cordio_wsf_set_os_specific_event_candidate", 0x0052B8D8, 0x0052B91E),
            ("SET_EVENT", "open_cfw_cordio_wsf_set_event_candidate", 0x0052B91E, 0x0052B95E),
            ("TASK_READY", "open_cfw_cordio_wsf_task_set_ready_candidate", 0x0052B95E, 0x0052B97C),
            ("TASK_QUEUE", "open_cfw_cordio_wsf_task_message_queue_candidate", 0x0052B97C, 0x0052B980),
            ("NEXT_HANDLER", "open_cfw_cordio_wsf_os_set_next_handler_candidate", 0x0052B980, 0x0052B99E),
            ("READY_SLEEP", "open_cfw_cordio_wsf_os_ready_to_sleep_candidate", 0x0052B99E, 0x0052B9B2),
            ("INIT", "open_cfw_cordio_wsf_os_init_candidate", 0x0052B9B2, 0x0052B9D0),
            ("DISPATCHER", "open_cfw_cordio_wsf_os_dispatcher_candidate", 0x0052B9D0, 0x0052BAB8),
        ),
        "providers": {
            "open_cfw_cordio_wsf_cs_enter_candidate":
                "open_cfw_cordio_wsf_cs_enter_candidate",
            "open_cfw_cordio_wsf_cs_exit_candidate":
                "open_cfw_cordio_wsf_cs_exit_candidate",
            "open_cfw_cordio_wsf_set_os_specific_event_candidate":
                "open_cfw_cordio_wsf_set_os_specific_event_candidate",
            "open_cfw_cordio_wsf_os_ready_to_sleep_candidate":
                "open_cfw_cordio_wsf_os_ready_to_sleep_candidate",
            "open_cfw_cordio_wsf_port_is_inside_interrupt_candidate": 0x00442228,
            "open_cfw_cordio_wsf_event_group_set_bits_from_isr_candidate": 0x0047EE4A,
            "open_cfw_cordio_wsf_event_group_set_bits_candidate": 0x0047ED76,
            "open_cfw_cordio_wsf_yield_candidate": 0x004420BC,
            "open_cfw_cordio_wsf_event_group_create_candidate": 0x0047EBD8,
            "open_cfw_cordio_wsf_event_group_wait_bits_candidate": 0x0047EBF8,
            "open_cfw_cordio_wsf_message_dequeue_candidate":
                "open_cfw_cordio_wsf_message_dequeue_candidate",
            "open_cfw_cordio_wsf_message_free_candidate":
                "open_cfw_cordio_wsf_message_free_candidate",
            "open_cfw_cordio_wsf_timer_update_ticks_candidate":
                "open_cfw_cordio_wsf_timer_update_ticks_candidate",
            "open_cfw_cordio_wsf_timer_service_expired_candidate":
                "open_cfw_cordio_wsf_timer_service_expired_candidate",
        },
    },
    "wstr": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wstr_candidate.c",
        "recorder": "apple-cordio-wstr-record",
        "define": "OPEN_CFW_WSTR_",
        "patch": "replace_cordio_wstr_",
        "region": "cordio_wstr_",
        "evidence": "docs/research/cordio-wstr-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 WSF reverse-copy and in-place reverse "
            "definitions retained from r19.02 through r20.05c"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_WSTR_PRODUCTION=1",
        "selectors": (
            ("REVERSE_COPY", "open_cfw_cordio_wstr_reverse_copy_candidate", 0x0056D8C4, 0x0056D8F0),
            ("REVERSE", "open_cfw_cordio_wstr_reverse_candidate", 0x0056D8F0, 0x0056D93A),
        ),
        "providers": {},
    },
    "assert_trace": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.c",
        "recorder": "apple-cordio-wsf-assert-trace-record",
        "define": "OPEN_CFW_WSF_ASSERT_TRACE_",
        "patch": "replace_cordio_wsf_assert_trace_",
        "region": "cordio_wsf_assert_trace_",
        "evidence": "docs/research/cordio-wsf-assert-trace-source-recovery.md",
        "origin": (
            "clean-room G2 Cordio WSF assert/trace implementation over the "
            "authenticated AmbiqSuite behavior family and retained debug ABI"
        ),
        "license": "GPL-3.0-only",
        "flag": "-DOPEN_CFW_WSF_ASSERT_TRACE_PRODUCTION=1",
        "selectors": (
            ("TRACE", "open_cfw_cordio_wsf_trace_candidate", 0x0052A63C, 0x0052A672),
            ("ASSERT", "open_cfw_cordio_wsf_assert_candidate", 0x00569A44, 0x00569ADE),
        ),
        "providers": {
            "open_cfw_cordio_wsf_trace_vsprintf_candidate": 0x00473036,
            "open_cfw_cordio_wsf_trace_debug_printf_candidate": 0x004733EE,
            "open_cfw_cordio_wsf_assert_candidate":
                "open_cfw_cordio_wsf_assert_candidate",
            "open_cfw_cordio_wsf_assert_reset_candidate": 0x0044B0AE,
        },
    },
    "atts_csf": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_csf.c",
        "recorder": "apple-cordio-atts-csf-record",
        "define": "OPEN_CFW_ATTS_CSF_",
        "patch": "replace_cordio_atts_csf_",
        "region": "cordio_atts_csf_",
        "evidence": "docs/research/cordio-atts-csf-source-recovery.md",
        "origin": (
            "Packetcraft r20.05--r20.05c Apache-2.0 ATT client-supported-"
            "features implementation over the recovered three-connection G2 ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_CSF_PRODUCTION=1",
        "selectors": (
            ("SET_HASH", "open_cfw_cordio_atts_csf_set_hash_update_status", 0x0052C6C0, 0x0052C914),
            ("GET_HASH", "open_cfw_cordio_atts_csf_get_hash_update_status", 0x0052C914, 0x0052C91C),
            ("IS_AWARE", "open_cfw_cordio_atts_csf_is_client_change_aware", 0x0052C928, 0x0052CA9C),
            ("ACT_STATE", "open_cfw_cordio_atts_csf_act_client_state", 0x0052CAA8, 0x0052D06E),
            ("SET_STATE", "open_cfw_cordio_atts_csf_set_clients_change_awareness_state", 0x0052D090, 0x0052D35A),
            ("CONN_OPEN", "open_cfw_cordio_atts_csf_connection_open", 0x0052D370, 0x0052D4E0),
            ("REGISTER", "open_cfw_cordio_atts_csf_register", 0x0052D4E0, 0x0052D4E8),
            ("WRITE", "open_cfw_cordio_atts_csf_write_features", 0x0052D508, 0x0052D7B6),
            ("GET_FEATURES", "open_cfw_cordio_atts_csf_get_features", 0x0052D7C4, 0x0052D8EE),
            ("GET_STATE", "open_cfw_cordio_atts_csf_get_change_aware_state", 0x0052D8EE, 0x0052DA0C),
        ),
        "providers": {
            "open_cfw_cordio_atts_check_pending_database_hash_read_response": 0x00534DD8,
        },
    },
    "atts_ccc": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_ccc.c",
        "recorder": "apple-cordio-atts-ccc-record",
        "define": "OPEN_CFW_ATTS_CCC_",
        "patch": "replace_cordio_atts_ccc_",
        "region": "cordio_atts_ccc_",
        "evidence": "docs/research/cordio-atts-ccc-source-recovery.md",
        "origin": (
            "Packetcraft r20.05--r20.05c Apache-2.0 ATT client-"
            "characteristic-configuration implementation with recovered G2 guards"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_CCC_PRODUCTION=1",
        "selectors": (
            ("CALLBACK", "open_cfw_cordio_atts_ccc_callback", 0x0052BB64, 0x0052BB8A),
            ("ALLOCATE", "open_cfw_cordio_atts_ccc_allocate_table", 0x0052BB8A, 0x0052BCEA),
            ("GET_TABLE", "open_cfw_cordio_atts_ccc_get_table", 0x0052BCEA, 0x0052BE26),
            ("FREE", "open_cfw_cordio_atts_ccc_free_table", 0x0052BE34, 0x0052BF8E),
            ("READ", "open_cfw_cordio_atts_ccc_read_value", 0x0052BF8E, 0x0052BFF0),
            ("WRITE", "open_cfw_cordio_atts_ccc_write_value", 0x0052BFF0, 0x0052C09E),
            ("MAIN", "open_cfw_cordio_atts_ccc_main_callback", 0x0052C0AC, 0x0052C224),
            ("REGISTER", "open_cfw_cordio_atts_ccc_register", 0x0052C224, 0x0052C23C),
            ("INITIALIZE", "open_cfw_cordio_atts_ccc_initialize_table", 0x0052C244, 0x0052C3C4),
            ("CLEAR", "open_cfw_cordio_atts_ccc_clear_table", 0x0052C3D0, 0x0052C5F2),
            ("GET", "open_cfw_cordio_atts_ccc_get", 0x0052C5F2, 0x0052C60E),
            ("SET", "open_cfw_cordio_atts_ccc_set", 0x0052C60E, 0x0052C628),
            ("ENABLED", "open_cfw_cordio_atts_ccc_enabled", 0x0052C628, 0x0052C660),
            ("LENGTH", "open_cfw_cordio_atts_ccc_table_length", 0x0052C664, 0x0052C66A),
        ),
        "providers": {
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_wsf_buffer_free_candidate":
                "open_cfw_cordio_wsf_buffer_free_candidate",
            "open_cfw_cordio_dm_connection_security_level": 0x004B71B2,
            "open_cfw_cordio_atts_ccc_callback":
                "open_cfw_cordio_atts_ccc_callback",
            "open_cfw_cordio_atts_ccc_allocate_table":
                "open_cfw_cordio_atts_ccc_allocate_table",
            "open_cfw_cordio_atts_ccc_get_table":
                "open_cfw_cordio_atts_ccc_get_table",
            "open_cfw_cordio_atts_ccc_free_table":
                "open_cfw_cordio_atts_ccc_free_table",
            "open_cfw_cordio_atts_ccc_read_value":
                "open_cfw_cordio_atts_ccc_read_value",
            "open_cfw_cordio_atts_ccc_write_value":
                "open_cfw_cordio_atts_ccc_write_value",
            "open_cfw_cordio_atts_ccc_get":
                "open_cfw_cordio_atts_ccc_get",
        },
    },
    "atts_write": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_write.c",
        "recorder": "apple-cordio-atts-write-record",
        "define": "OPEN_CFW_ATTS_WRITE_",
        "patch": "replace_cordio_atts_write_",
        "region": "cordio_atts_write_",
        "evidence": "docs/research/cordio-atts-write-source-recovery.md",
        "origin": (
            "Packetcraft r20.05--r20.05c Apache-2.0 ATT server write "
            "processors over the recovered G2 EATT and fixed-SRAM ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_WRITE_PRODUCTION=1",
        "selectors": (
            ("EXECUTE", "open_cfw_cordio_atts_execute_prepared_write", 0x005A5D94, 0x005A5E3A),
            ("PROCESS", "open_cfw_cordio_atts_process_write", 0x005A5E3A, 0x005A5FC2),
            ("PREPARE", "open_cfw_cordio_atts_process_prepare_write_request", 0x005A5FC2, 0x005A6170),
            ("EXECUTE_REQUEST", "open_cfw_cordio_atts_process_execute_write_request", 0x005A6170, 0x005A6258),
        ),
        "providers": {
            "open_cfw_cordio_atts_find_by_handle": 0x0056C5D4,
            "open_cfw_cordio_atts_permissions": 0x0056C66A,
            "open_cfw_cordio_atts_error_response": 0x00534C9A,
            "open_cfw_cordio_atts_clear_prepared_writes": 0x00534CDE,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_wsf_buffer_free_candidate":
                "open_cfw_cordio_wsf_buffer_free_candidate",
            "open_cfw_cordio_wsf_queue_enqueue_candidate":
                "open_cfw_cordio_wsf_queue_enqueue_candidate",
            "open_cfw_cordio_wsf_queue_dequeue_candidate":
                "open_cfw_cordio_wsf_queue_dequeue_candidate",
            "open_cfw_cordio_wsf_queue_count_candidate":
                "open_cfw_cordio_wsf_queue_count_candidate",
            "open_cfw_cordio_atts_execute_prepared_write":
                "open_cfw_cordio_atts_execute_prepared_write",
        },
    },
    "atts_proc": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_proc.c",
        "recorder": "apple-cordio-atts-proc-record",
        "define": "OPEN_CFW_ATTS_PROC_",
        "patch": "replace_cordio_atts_proc_",
        "region": "cordio_atts_proc_",
        "evidence": "docs/research/cordio-atts-proc-source-recovery.md",
        "origin": (
            "Packetcraft r20.05--r20.05c Apache-2.0 common ATT server "
            "processors with the authenticated G2 247-byte MTU floor"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_PROC_PRODUCTION=1",
        "selectors": (
            ("UUID", "open_cfw_cordio_atts_uuid_compare", 0x0056C550, 0x0056C5AA),
            ("UUID16", "open_cfw_cordio_atts_uuid16_compare", 0x0056C5AA, 0x0056C5D4),
            ("FIND_HANDLE", "open_cfw_cordio_atts_find_by_handle", 0x0056C5D4, 0x0056C610),
            ("FIND_RANGE", "open_cfw_cordio_atts_find_in_range", 0x0056C610, 0x0056C66A),
            ("PERMISSIONS", "open_cfw_cordio_atts_permissions", 0x0056C66A, 0x0056C6FC),
            ("MTU", "open_cfw_cordio_atts_process_mtu_request", 0x0056C6FC, 0x0056C924),
            ("FIND_INFO", "open_cfw_cordio_atts_process_find_information_request", 0x0056C930, 0x0056CAA8),
            ("READ", "open_cfw_cordio_atts_process_read_request", 0x0056CAA8, 0x0056CBCA),
            ("READ_MULTI_VAR", "open_cfw_cordio_atts_process_read_multiple_variable_request", 0x0056CBCA, 0x0056CD96),
        ),
        "providers": {
            "open_cfw_cordio_att_uuid_compare_16_to_128": 0x004B5014,
            "open_cfw_cordio_dm_connection_security_level": 0x004B71B2,
            "open_cfw_cordio_atts_csf_get_features":
                "open_cfw_cordio_atts_csf_get_features",
            "open_cfw_cordio_hci_get_maximum_receive_acl_length": 0x00530D4C,
            "open_cfw_cordio_att_set_mtu": 0x004B503C,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_atts_error_response": 0x00534C9A,
            "open_cfw_cordio_atts_discovery_busy": 0x00534D06,
            "open_cfw_cordio_wsf_message_free": 0x004BF9B0,
            "open_cfw_cordio_att_message_free": 0x004B5210,
            "open_cfw_cordio_atts_uuid_compare":
                "open_cfw_cordio_atts_uuid_compare",
            "open_cfw_cordio_atts_uuid16_compare":
                "open_cfw_cordio_atts_uuid16_compare",
            "open_cfw_cordio_atts_find_by_handle":
                "open_cfw_cordio_atts_find_by_handle",
            "open_cfw_cordio_atts_find_in_range":
                "open_cfw_cordio_atts_find_in_range",
            "open_cfw_cordio_atts_permissions":
                "open_cfw_cordio_atts_permissions",
        },
    },
    "atts_ind": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_ind.c",
        "recorder": "apple-cordio-atts-ind-record",
        "define": "OPEN_CFW_ATTS_IND_",
        "patch": "replace_cordio_atts_ind_",
        "region": "cordio_atts_ind_",
        "evidence": "docs/research/cordio-atts-ind-source-recovery.md",
        "origin": (
            "Packetcraft r20.05--r20.05c Apache-2.0 ATT server indication "
            "and notification implementation with authenticated G2 ABI deltas"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_IND_PRODUCTION=1",
        "selectors": (
            ("PENDING", "open_cfw_cordio_atts_ind_pending", 0x005338AC, 0x0053390E),
            ("SET_PENDING", "open_cfw_cordio_atts_ind_set_pending_notification", 0x0053390E, 0x00533934),
            ("EXEC_CALLBACK", "open_cfw_cordio_atts_ind_execute_callback", 0x00533934, 0x0053394C),
            ("NOTIFICATION_CALLBACK", "open_cfw_cordio_atts_ind_notification_callback", 0x0053394C, 0x005339AC),
            ("SETUP", "open_cfw_cordio_atts_ind_setup_message", 0x005339AC, 0x00533A40),
            ("CONNECTION_CALLBACK", "open_cfw_cordio_atts_ind_connection_callback", 0x00533A40, 0x00533BC6),
            ("MESSAGE_CALLBACK", "open_cfw_cordio_atts_ind_message_callback", 0x00533BCC, 0x00533C4C),
            ("CONTROL_CALLBACK", "open_cfw_cordio_atts_ind_control_callback", 0x00533C4C, 0x00533C6C),
            ("HANDLE", "open_cfw_cordio_atts_handle_value_indication_notification", 0x00533C6C, 0x00533DD2),
            ("CONFIRM", "open_cfw_cordio_atts_process_value_confirmation", 0x00533DD8, 0x00533E40),
            ("INITIALIZE", "open_cfw_cordio_atts_ind_initialize", 0x00533E40, 0x00533E90),
            ("INDICATION", "open_cfw_cordio_atts_handle_value_indication", 0x00533EBC, 0x00533ED8),
            ("NOTIFICATION", "open_cfw_cordio_atts_handle_value_notification", 0x00533ED8, 0x00533EF4),
        ),
        "providers": {
            "open_cfw_cordio_att_execute_callback": 0x004B5074,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_att_message_parameter": 0x004B50F0,
            "open_cfw_cordio_att_decode_message_parameter": 0x004B50FE,
            "open_cfw_cordio_wsf_timer_start_seconds": 0x0052A4B8,
            "open_cfw_cordio_wsf_timer_stop": 0x0052A4D2,
            "open_cfw_cordio_atts_ind_connection_by_id": 0x00534F14,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
            "open_cfw_cordio_wsf_message_allocate": 0x004BF99E,
            "open_cfw_cordio_wsf_message_send": 0x004BF9BA,
            "open_cfw_cordio_wsf_message_free": 0x004BF9B0,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_message_free": 0x004B5210,
            "open_cfw_cordio_atts_csf_is_client_change_aware":
                "open_cfw_cordio_atts_csf_is_client_change_aware",
            "open_cfw_cordio_atts_csf_get_change_aware_state":
                "open_cfw_cordio_atts_csf_get_change_aware_state",
            "open_cfw_cordio_atts_csf_set_clients_change_awareness_state":
                "open_cfw_cordio_atts_csf_set_clients_change_awareness_state",
            "open_cfw_cordio_atts_find_by_handle":
                "open_cfw_cordio_atts_find_by_handle",
            "open_cfw_cordio_atts_ind_pending":
                "open_cfw_cordio_atts_ind_pending",
            "open_cfw_cordio_atts_ind_set_pending_notification":
                "open_cfw_cordio_atts_ind_set_pending_notification",
            "open_cfw_cordio_atts_ind_execute_callback":
                "open_cfw_cordio_atts_ind_execute_callback",
            "open_cfw_cordio_atts_ind_notification_callback":
                "open_cfw_cordio_atts_ind_notification_callback",
            "open_cfw_cordio_atts_ind_setup_message":
                "open_cfw_cordio_atts_ind_setup_message",
            "open_cfw_cordio_atts_handle_value_indication_notification":
                "open_cfw_cordio_atts_handle_value_indication_notification",
        },
    },
    "atts_read": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_read.c",
        "recorder": "apple-cordio-atts-read-record",
        "define": "OPEN_CFW_ATTS_READ_",
        "patch": "replace_cordio_atts_read_",
        "region": "cordio_atts_read_",
        "evidence": "docs/research/cordio-atts-read-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 ATT optional server read processors from "
            "the authenticated AmbiqSuite R4.4.1 behavioral oracle"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_READ_PRODUCTION=1",
        "selectors": (
            ("FIND_UUID", "open_cfw_cordio_atts_find_uuid_in_range", 0x0056D93C, 0x0056D9EC),
            ("FIND_SERVICE_END", "open_cfw_cordio_atts_find_service_group_end", 0x0056D9EC, 0x0056DA9E),
            ("BLOB", "open_cfw_cordio_atts_process_read_blob_request", 0x0056DA9E, 0x0056DC04),
            ("FIND_TYPE", "open_cfw_cordio_atts_process_find_type_request", 0x0056DC04, 0x0056DD9C),
            ("TYPE", "open_cfw_cordio_atts_process_read_type_request", 0x0056DD9C, 0x0056E0DE),
            ("MULTIPLE", "open_cfw_cordio_atts_process_read_multiple_request", 0x0056E0DE, 0x0056E26C),
            ("GROUP_TYPE", "open_cfw_cordio_atts_process_read_group_type_request", 0x0056E26C, 0x0056E4E4),
        ),
        "providers": {
            "open_cfw_cordio_atts_uuid_compare":
                "open_cfw_cordio_atts_uuid_compare",
            "open_cfw_cordio_atts_uuid16_compare":
                "open_cfw_cordio_atts_uuid16_compare",
            "open_cfw_cordio_atts_find_by_handle":
                "open_cfw_cordio_atts_find_by_handle",
            "open_cfw_cordio_atts_permissions":
                "open_cfw_cordio_atts_permissions",
            "open_cfw_cordio_atts_csf_get_hash_update_status":
                "open_cfw_cordio_atts_csf_get_hash_update_status",
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_atts_error_response": 0x00534C9A,
            "open_cfw_cordio_atts_discovery_busy": 0x00534D06,
            "open_cfw_cordio_wsf_message_free": 0x004BF9B0,
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_atts_find_uuid_in_range":
                "open_cfw_cordio_atts_find_uuid_in_range",
            "open_cfw_cordio_atts_find_service_group_end":
                "open_cfw_cordio_atts_find_service_group_end",
        },
    },
    "atts_main": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_atts_main.c",
        "recorder": "apple-cordio-atts-main-record",
        "define": "OPEN_CFW_ATTS_MAIN_",
        "patch": "replace_cordio_atts_main_",
        "region": "cordio_atts_main_",
        "evidence": "docs/research/cordio-atts-main-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 ATT server owner/dispatcher from the "
            "authenticated AmbiqSuite R4.4.1 hardened behavioral oracle"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTS_MAIN_PRODUCTION=1",
        "selectors": (
            ("DATA", "open_cfw_cordio_atts_data_callback", 0x0053498C, 0x00534ABA),
            ("CONNECTION", "open_cfw_cordio_atts_connection_callback", 0x00534ABA, 0x00534C42),
            ("MESSAGE", "open_cfw_cordio_atts_message_callback", 0x00534C42, 0x00534C8A),
            ("CONTROL", "open_cfw_cordio_atts_l2c_control_callback", 0x00534C8A, 0x00534C9A),
            ("ERROR_RESPONSE", "open_cfw_cordio_atts_error_response", 0x00534C9A, 0x00534CDE),
            ("CLEAR_WRITES", "open_cfw_cordio_atts_clear_prepared_writes", 0x00534CDE, 0x00534D06),
            ("DISCOVERY_BUSY", "open_cfw_cordio_atts_discovery_busy", 0x00534D06, 0x00534D46),
            ("PROCESS_HASH", "open_cfw_cordio_atts_process_database_hash_update", 0x00534D46, 0x00534DD0),
            ("CHECK_HASH", "open_cfw_cordio_atts_check_pending_database_hash_read_response", 0x00534DD8, 0x00534EA8),
            ("HASHABLE", "open_cfw_cordio_atts_is_hashable_attribute", 0x00534EA8, 0x00534F0E),
            ("CCB_ID", "open_cfw_cordio_atts_ind_connection_by_id", 0x00534F14, 0x005351A8),
            ("CCB_HANDLE", "open_cfw_cordio_atts_ind_connection_by_handle", 0x005351A8, 0x005351D6),
            ("INITIALIZE", "open_cfw_cordio_atts_initialize", 0x005351DC, 0x00535258),
            ("HASH_STRING", "open_cfw_cordio_atts_hash_database_string", 0x0053525C, 0x00535276),
            ("CALCULATE_HASH", "open_cfw_cordio_atts_calculate_database_hash", 0x0053527C, 0x005353AE),
            ("ADD_GROUP", "open_cfw_cordio_atts_add_group", 0x005353AE, 0x005353E8),
            ("REMOVE_GROUP", "open_cfw_cordio_atts_remove_group", 0x005353E8, 0x00535440),
        ),
        "providers": {
            "open_cfw_cordio_atts_csf_act_client_state":
                "open_cfw_cordio_atts_csf_act_client_state",
            "open_cfw_cordio_atts_csf_set_hash_update_status":
                "open_cfw_cordio_atts_csf_set_hash_update_status",
            "open_cfw_cordio_atts_find_by_handle":
                "open_cfw_cordio_atts_find_by_handle",
            "open_cfw_cordio_atts_find_uuid_in_range":
                "open_cfw_cordio_atts_find_uuid_in_range",
            "open_cfw_cordio_dm_connection_in_use": 0x004B6EC6,
            "open_cfw_cordio_dm_connection_id_by_handle": 0x004B6E96,
            "open_cfw_cordio_dm_connection_check_idle": 0x004B73A2,
            "open_cfw_cordio_dm_connection_set_idle": 0x004B71DC,
            "open_cfw_cordio_security_cmac": 0x0053665C,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_wsf_buffer_free_candidate":
                "open_cfw_cordio_wsf_buffer_free_candidate",
            "open_cfw_cordio_wsf_queue_dequeue_candidate":
                "open_cfw_cordio_wsf_queue_dequeue_candidate",
            "open_cfw_cordio_wsf_queue_insert_candidate":
                "open_cfw_cordio_wsf_queue_insert_candidate",
            "open_cfw_cordio_wsf_queue_remove_candidate":
                "open_cfw_cordio_wsf_queue_remove_candidate",
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
            "open_cfw_cordio_wsf_timer_start_seconds": 0x0052A4B8,
            "open_cfw_cordio_wsf_timer_stop": 0x0052A4D2,
            "open_cfw_cordio_wsf_assert_candidate":
                "open_cfw_cordio_wsf_assert_candidate",
            "open_cfw_cordio_atts_ind_connection_by_handle":
                "open_cfw_cordio_atts_ind_connection_by_handle",
            "open_cfw_cordio_atts_error_response":
                "open_cfw_cordio_atts_error_response",
            "open_cfw_cordio_atts_clear_prepared_writes":
                "open_cfw_cordio_atts_clear_prepared_writes",
            "open_cfw_cordio_atts_process_database_hash_update":
                "open_cfw_cordio_atts_process_database_hash_update",
            "open_cfw_cordio_atts_is_hashable_attribute":
                "open_cfw_cordio_atts_is_hashable_attribute",
            "open_cfw_cordio_atts_hash_database_string":
                "open_cfw_cordio_atts_hash_database_string",
        },
    },
    "attc_write": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_attc_write.c",
        "recorder": "apple-cordio-attc-write-record",
        "define": "OPEN_CFW_ATTC_WRITE_",
        "patch": "replace_cordio_attc_write_",
        "region": "cordio_attc_write_",
        "evidence": "docs/research/cordio-attc-write-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 ATT client optional-write definitions "
            "retained through r20.05c and the official AmbiqSuite R4.4.1 import"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTC_WRITE_PRODUCTION=1",
        "selectors": (
            (
                "PROCESS_PREP_RSP",
                "open_cfw_cordio_attc_process_prepare_write_response",
                0x00539DCC,
                0x00539DEA,
            ),
            (
                "COMMAND",
                "open_cfw_cordio_attc_write_command",
                0x00539DEA,
                0x00539E48,
            ),
        ),
        "providers": {
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_attc_send_message": 0x004B5640,
        },
    },
    "attc_read": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_attc_read.c",
        "recorder": "apple-cordio-attc-read-record",
        "define": "OPEN_CFW_ATTC_READ_",
        "patch": "replace_cordio_attc_read_",
        "region": "cordio_attc_read_",
        "evidence": "docs/research/cordio-attc-read-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 ATT client optional-read definitions "
            "from r20.05c and the byte-identical AmbiqSuite R4.4.1 import"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTC_READ_PRODUCTION=1",
        "selectors": (
            (
                "FIND_TYPE_RESPONSE",
                "open_cfw_cordio_attc_process_find_by_type_response",
                0x0056C3B0,
                0x0056C454,
            ),
            (
                "LONG_RESPONSE",
                "open_cfw_cordio_attc_process_read_long_response",
                0x0056C454,
                0x0056C47E,
            ),
            (
                "FIND_TYPE_REQUEST",
                "open_cfw_cordio_attc_find_by_type_value_request",
                0x0056C47E,
                0x0056C4EE,
            ),
            (
                "TYPE_REQUEST",
                "open_cfw_cordio_attc_read_by_type_request",
                0x0056C4EE,
                0x0056C54E,
            ),
        ),
        "providers": {
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_attc_send_message": 0x004B5640,
        },
    },
    "attc_proc": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_attc_proc.c",
        "recorder": "apple-cordio-attc-proc-record",
        "define": "OPEN_CFW_ATTC_PROC_",
        "patch": "replace_cordio_attc_proc_",
        "region": "cordio_attc_proc_",
        "evidence": "docs/research/cordio-attc-proc-source-recovery.md",
        "origin": "Packetcraft Apache-2.0 r20 ATT client PDU processor with bounded R4 table hardening",
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTC_PROC_PRODUCTION=1",
        "copy_selectors": {"READ_RESPONSE", "READ_MULTI_VAR_RESPONSE"},
        "selectors": (
            ("ERROR_RESPONSE", "open_cfw_cordio_attc_process_error_response", 0x004B5230, 0x004B527A),
            ("MTU_RESPONSE", "open_cfw_cordio_attc_process_mtu_response", 0x004B527A, 0x004B52C2),
            ("FIND_READ_RESPONSE", "open_cfw_cordio_attc_process_find_or_read_response", 0x004B52C2, 0x004B53DA),
            ("READ_RESPONSE", "open_cfw_cordio_attc_process_read_response", 0x004B53DA, 0x004B53DC),
            ("WRITE_RESPONSE", "open_cfw_cordio_attc_process_write_response", 0x004B53DC, 0x004B53E2),
            ("READ_MULTI_VAR_RESPONSE", "open_cfw_cordio_attc_process_read_multiple_variable_response", 0x004B53E2, 0x004B53E4),
            ("MULTI_VAR_NOTIFICATION", "open_cfw_cordio_attc_process_multiple_variable_notification", 0x004B53E4, 0x004B5448),
            ("RESPONSE", "open_cfw_cordio_attc_process_response", 0x004B5448, 0x004B557A),
            ("INDICATION", "open_cfw_cordio_attc_process_indication_notification", 0x004B557A, 0x004B5640),
            ("SEND_MESSAGE", "open_cfw_cordio_attc_send_message", 0x004B5640, 0x004B571E),
            ("FIND_INFO_REQUEST", "open_cfw_cordio_attc_find_information_request", 0x004B571E, 0x004B575A),
            ("READ_REQUEST", "open_cfw_cordio_attc_read_request", 0x004B575A, 0x004B579C),
            ("WRITE_REQUEST", "open_cfw_cordio_attc_write_request", 0x004B579C, 0x004B57FA),
            ("MTU_REQUEST", "open_cfw_cordio_attc_mtu_request", 0x004B57FA, 0x004B5838),
            ("INDICATION_CONFIRM", "open_cfw_cordio_attc_indication_confirm", 0x004B5838, 0x004B598C),
        ),
        "providers": {
            "open_cfw_cordio_att_set_mtu": 0x004B503C,
            "open_cfw_cordio_hci_get_max_rx_acl_length": 0x00530D4C,
            "open_cfw_cordio_wsf_timer_stop_candidate": "open_cfw_cordio_wsf_timer_stop_candidate",
            "open_cfw_cordio_attc_free_packet": 0x00531AC0,
            "open_cfw_cordio_attc_send_request": 0x00531144,
            "open_cfw_cordio_attc_setup_request": 0x00531160,
            "open_cfw_cordio_wsf_task_lock_candidate": "open_cfw_cordio_wsf_task_lock_candidate",
            "open_cfw_cordio_wsf_task_unlock_candidate": "open_cfw_cordio_wsf_task_unlock_candidate",
            "open_cfw_cordio_attc_connection_by_id": 0x00531820,
            "open_cfw_cordio_attc_connection_by_handle": 0x00531A7C,
            "open_cfw_cordio_attc_execute_callback": 0x00531AD6,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_wsf_message_allocate_candidate": "open_cfw_cordio_wsf_message_allocate_candidate",
            "open_cfw_cordio_wsf_message_free_candidate": "open_cfw_cordio_wsf_message_free_candidate",
            "open_cfw_cordio_wsf_message_send_candidate": "open_cfw_cordio_wsf_message_send_candidate",
            "open_cfw_cordio_attc_process_find_by_type_response": "open_cfw_cordio_attc_process_find_by_type_response",
            "open_cfw_cordio_attc_process_read_long_response": "open_cfw_cordio_attc_process_read_long_response",
            "open_cfw_cordio_attc_process_prepare_write_response": "open_cfw_cordio_attc_process_prepare_write_response",
        },
    },
    "attc_main": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_attc_main.c",
        "recorder": "apple-cordio-attc-main-record",
        "define": "OPEN_CFW_ATTC_MAIN_",
        "patch": "replace_cordio_attc_main_",
        "region": "cordio_attc_main_",
        "evidence": "docs/research/cordio-attc-main-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 r20/R4 ATT client core with bounded "
            "G2 connection, bearer, timer, and on-deck hardening"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTC_MAIN_PRODUCTION=1",
        "selectors": (
            ("PEND_WRITE", "open_cfw_cordio_attc_pending_write_command", 0x00530D74, 0x00530DBE),
            ("SET_PEND_WRITE", "open_cfw_cordio_attc_set_pending_write_command", 0x00530DBE, 0x00530DE6),
            ("WRITE_CALLBACK", "open_cfw_cordio_attc_write_command_callback", 0x00530DE6, 0x00530E30),
            ("SIMPLE_REQ", "open_cfw_cordio_attc_send_simple_request", 0x00530E30, 0x00530E64),
            ("CONTINUING_REQ", "open_cfw_cordio_attc_send_continuing_request", 0x00530E64, 0x00530F08),
            ("MTU_REQ", "open_cfw_cordio_attc_send_mtu_request", 0x00530F08, 0x00531054),
            ("WRITE_CMD", "open_cfw_cordio_attc_send_write_command", 0x00531054, 0x00531088),
            ("PREP_WRITE_REQ", "open_cfw_cordio_attc_send_prepare_write_request", 0x00531088, 0x00531144),
            ("SEND_REQ", "open_cfw_cordio_attc_send_request", 0x00531144, 0x00531154),
            ("SETUP_REQ", "open_cfw_cordio_attc_setup_request", 0x00531160, 0x0053119C),
            ("DATA_CALLBACK", "open_cfw_cordio_attc_data_callback", 0x0053119C, 0x00531326),
            ("CONTROL_CALLBACK", "open_cfw_cordio_attc_control_callback", 0x00531330, 0x0053135A),
            ("CONNECTION_CALLBACK", "open_cfw_cordio_attc_connection_callback", 0x0053135A, 0x005315A8),
            ("MESSAGE_CALLBACK", "open_cfw_cordio_attc_message_callback", 0x005315B4, 0x00531816),
            ("CCB_BY_ID", "open_cfw_cordio_attc_connection_by_id", 0x00531820, 0x00531A7C),
            ("CCB_BY_HANDLE", "open_cfw_cordio_attc_connection_by_handle", 0x00531A7C, 0x00531AAA),
            ("FREE_PACKET", "open_cfw_cordio_attc_free_packet", 0x00531AC0, 0x00531AD6),
            ("EXEC_CALLBACK", "open_cfw_cordio_attc_execute_callback", 0x00531AD6, 0x00531AF2),
            ("REQUEST_CLEAR", "open_cfw_cordio_attc_request_clear", 0x00531AF2, 0x00531B16),
            ("INITIALIZE", "open_cfw_cordio_attc_initialize", 0x00531B1C, 0x00531B90),
        ),
        "providers": {
            "open_cfw_cordio_attc_pending_write_command": "open_cfw_cordio_attc_pending_write_command",
            "open_cfw_cordio_attc_set_pending_write_command": "open_cfw_cordio_attc_set_pending_write_command",
            "open_cfw_cordio_attc_write_command_callback": "open_cfw_cordio_attc_write_command_callback",
            "open_cfw_cordio_attc_send_simple_request": "open_cfw_cordio_attc_send_simple_request",
            "open_cfw_cordio_attc_send_continuing_request": "open_cfw_cordio_attc_send_continuing_request",
            "open_cfw_cordio_attc_send_mtu_request": "open_cfw_cordio_attc_send_mtu_request",
            "open_cfw_cordio_attc_send_write_command": "open_cfw_cordio_attc_send_write_command",
            "open_cfw_cordio_attc_send_prepare_write_request": "open_cfw_cordio_attc_send_prepare_write_request",
            "open_cfw_cordio_attc_send_request": "open_cfw_cordio_attc_send_request",
            "open_cfw_cordio_attc_setup_request": "open_cfw_cordio_attc_setup_request",
            "open_cfw_cordio_attc_connection_by_id": "open_cfw_cordio_attc_connection_by_id",
            "open_cfw_cordio_attc_connection_by_handle": "open_cfw_cordio_attc_connection_by_handle",
            "open_cfw_cordio_attc_free_packet": "open_cfw_cordio_attc_free_packet",
            "open_cfw_cordio_attc_execute_callback": "open_cfw_cordio_attc_execute_callback",
            "open_cfw_cordio_attc_request_clear": "open_cfw_cordio_attc_request_clear",
            "open_cfw_cordio_attc_process_response": "open_cfw_cordio_attc_process_response",
            "open_cfw_cordio_attc_process_indication_notification": "open_cfw_cordio_attc_process_indication_notification",
            "open_cfw_cordio_attc_process_multiple_variable_notification": "open_cfw_cordio_attc_process_multiple_variable_notification",
            "open_cfw_cordio_attc_mtu_request": "open_cfw_cordio_attc_mtu_request",
            "open_cfw_cordio_attc_indication_confirm": "open_cfw_cordio_attc_indication_confirm",
            "open_cfw_cordio_dm_connection_in_use": 0x004B6EC6,
            "open_cfw_cordio_dm_connection_id_by_handle": 0x004B6E96,
            "open_cfw_cordio_dm_connection_role": 0x004B73C4,
            "open_cfw_cordio_att_execute_callback": 0x004B5074,
            "open_cfw_cordio_hci_get_max_rx_acl_length": 0x00530D4C,
            "open_cfw_cordio_att_message_allocate": 0x004B50AE,
            "open_cfw_cordio_att_l2c_data_request": 0x004B50BA,
            "open_cfw_cordio_wsf_timer_start_sec_candidate": "open_cfw_cordio_wsf_timer_start_sec_candidate",
            "open_cfw_cordio_wsf_timer_stop_candidate": "open_cfw_cordio_wsf_timer_stop_candidate",
            "open_cfw_cordio_wsf_message_free_candidate": "open_cfw_cordio_wsf_message_free_candidate",
        },
    },
    "ancc_profile": {
        "source": ROOT / "components/shared/cordio/runtime_ancc_profile.c",
        "recorder": "apple-ambiqsuite-ancc-profile-record",
        "define": "OPEN_CFW_ANCC_PROFILE_",
        "patch": "replace_ambiqsuite_ancc_profile_",
        "region": "ambiqsuite_ancc_profile_",
        "evidence": "docs/research/ambiqsuite-ancc-profile-source-recovery.md",
        "origin": (
            "AmbiqSuite 2.5.1 BSD-3-Clause ANCS client with the recovered "
            "G2 product ABI, fragmented-parser hardening, and notification policy"
        ),
        "license": "BSD-3-Clause",
        "flag": "-DOPEN_CFW_ANCC_PROFILE_PRODUCTION=1",
        "selectors": (
            ("CONN_OPEN", "open_cfw_ancc_connection_open_adapter", 0x004BEA04, 0x004BEA14),
            ("CONN_CLOSE", "open_cfw_ancc_connection_close_adapter", 0x004BEA14, 0x004BEA24),
            ("NO_CONNECTION", "open_cfw_ancc_no_connection_adapter", 0x004BEA24, 0x004BEA36),
            ("POP", "open_cfw_ancc_action_list_pop_adapter", 0x004BEA36, 0x004BEA7A),
            ("GET_NEXT", "open_cfw_ancc_get_next_notification_handler", 0x004BEA7A, 0x004BEAE8),
            ("GET_NOTIFICATION", "open_cfw_ancc_get_notification_attributes", 0x004BEAE8, 0x004BEB82),
            ("ACTION", "open_cfw_ancc_perform_notification_action", 0x004BEB82, 0x004BEBC4),
            ("GET_APP", "open_cfw_ancc_get_app_attributes", 0x004BEBC4, 0x004BEC20),
            ("PUSH", "open_cfw_ancc_action_list_push_adapter", 0x004BEC20, 0x004BED0E),
            ("SYNC_CALLBACK", "open_cfw_ancc_rx_sync_event_callback", 0x004BED0E, 0x004BEDAC),
            ("COMPLETE", "open_cfw_ancc_send_complete_notification", 0x004BEDAC, 0x004BEE0A),
            ("REMOVE", "open_cfw_ancc_notification_remove_callback", 0x004BEE0A, 0x004BEE5A),
            ("VALUE_UPDATE", "open_cfw_ancc_notification_value_update", 0x004BEE5A, 0x004BEFCE),
            ("VALUE_GATE", "open_cfw_ancc_value_update_gate", 0x004BEFCE, 0x004BF06C),
            ("ATTRIBUTE_CALLBACK", "open_cfw_ancc_attribute_callback_adapter", 0x004BF06C, 0x004BF214),
            ("DISPATCH", "open_cfw_ancc_dispatch", 0x004BF228, 0x004BF6BE),
            ("RESET", "open_cfw_ancc_reset_state_machine", 0x004BF6C4, 0x004BF742),
            ("INIT", "open_cfw_ancc_profile_initialize", 0x004BF742, 0x004BF780),
            ("PROCESS_MESSAGE", "open_cfw_ancc_profile_process_message", 0x004BF780, 0x004BF81A),
            ("DISCOVER", "open_cfw_ancc_service_discover", 0x004BF82C, 0x004BF8AC),
            ("GET_ACTIVE", "open_cfw_ancc_get_active_notification", 0x004BF8AC, 0x004BF8B0),
        ),
        "providers": {
            "open_cfw_ancc_dispatch": "open_cfw_ancc_dispatch",
            "open_cfw_ancc_get_next_notification_handler":
                "open_cfw_ancc_get_next_notification_handler",
            "open_cfw_ancc_rx_sync_event_callback":
                "open_cfw_ancc_rx_sync_event_callback",
            "open_cfw_cordio_attc_write_request":
                "open_cfw_cordio_attc_write_request",
            "open_cfw_cordio_wsf_message_allocate_candidate":
                "open_cfw_cordio_wsf_message_allocate_candidate",
            "open_cfw_cordio_wsf_message_send_candidate":
                "open_cfw_cordio_wsf_message_send_candidate",
            "open_cfw_event_loop_push_delayed": "open_cfw_event_loop_push_delayed",
            "open_cfw_event_loop_remove_delayed": "open_cfw_event_loop_remove_delayed",
            "open_cfw_ancc_sync_send": 0x00464D1C,
            "open_cfw_cordio_dm_connection_role": 0x004B73C4,
            "open_cfw_ancc_product_role": 0x0045A568,
            "open_cfw_ancc_service_enabled": 0x004972A2,
            "open_cfw_ancc_ota_active": 0x004487AC,
            "open_cfw_ancc_efs_active": 0x00458C1E,
            "open_cfw_cmsis_kernel_get_tick_count":
                "open_cfw_cmsis_kernel_get_tick_count",
            "open_cfw_ancc_connection_epoch": 0x004B8204,
            "open_cfw_ancc_whitelist_result": 0x004D67B8,
            "open_cfw_ancc_report_unlisted_app": 0x004D71BC,
            "open_cfw_ancc_discover_service": 0x005332B4,
        },
    },
    "app_legacy": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_app_legacy.c",
        "recorder": "apple-ambiqsuite-cordio-app-legacy-record",
        "define": "OPEN_CFW_CORDIO_APP_LEGACY_",
        "patch": "replace_ambiqsuite_cordio_app_legacy_",
        "region": "ambiqsuite_cordio_app_legacy_",
        "evidence": "docs/research/ambiqsuite-cordio-app-framework-source-recovery.md",
        "origin": (
            "AmbiqSuite 2.5.1 Apache-2.0 legacy master/slave application "
            "framework adapted to the recovered G2 state/configuration ABI "
            "and G2 extended-advertising retry policy"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_CORDIO_APP_LEGACY_PRODUCTION=1",
        "selectors": (
            ("MASTER_MODE", "open_cfw_app_master_scan_mode", 0x00503298, 0x0050337C),
            ("SCAN_START", "open_cfw_app_scan_start", 0x0050337C, 0x005033B2),
            ("SCAN_STOP", "open_cfw_app_scan_stop", 0x005033B2, 0x005033CA),
            ("CONNECTION_OPEN", "open_cfw_app_connection_open", 0x005033CA, 0x0050345E),
            ("ADV_START_INTERNAL", "open_cfw_app_slave_legacy_advertising_start", 0x004B2A04, 0x004B2A92),
            ("ADV_TYPE_CHANGED", "open_cfw_app_slave_legacy_advertising_type_changed", 0x004B2A92, 0x004B2AAA),
            ("ADV_NEXT_STATE", "open_cfw_app_slave_legacy_advertising_next_state", 0x004B2AAA, 0x004B2AFE),
            ("ADV_STOP_CALLBACK", "open_cfw_app_slave_legacy_advertising_stop", 0x004B2AFE, 0x004B2B90),
            ("ADV_RESTART_CALLBACK", "open_cfw_app_slave_legacy_advertising_restart", 0x004B2B90, 0x004B2BDE),
            ("ADV_MODE", "open_cfw_app_slave_legacy_advertising_mode", 0x004B2BDE, 0x004B2CEC),
            ("ADV_SET_DATA", "open_cfw_app_advertising_set_data", 0x004B2CEC, 0x004B2D22),
            ("ADV_START", "open_cfw_app_advertising_start", 0x004B2D22, 0x004B2D62),
            ("ADV_STOP", "open_cfw_app_advertising_stop", 0x004B2D62, 0x004B2D7C),
            ("ADV_SET_TYPE", "open_cfw_app_advertising_set_type", 0x004B2D7C, 0x004B2DBC),
        ),
        "providers": {
            "open_cfw_app_master_scan_mode": "open_cfw_app_master_scan_mode",
            "open_cfw_app_slave_legacy_advertising_start":
                "open_cfw_app_slave_legacy_advertising_start",
            "open_cfw_app_slave_legacy_advertising_type_changed":
                "open_cfw_app_slave_legacy_advertising_type_changed",
            "open_cfw_app_slave_legacy_advertising_next_state":
                "open_cfw_app_slave_legacy_advertising_next_state",
            "open_cfw_app_slave_legacy_advertising_mode":
                "open_cfw_app_slave_legacy_advertising_mode",
            "open_cfw_cordio_dm_scan_set_interval": 0x0055BB68,
            "open_cfw_cordio_dm_scan_start": 0x0055BAAE,
            "open_cfw_cordio_dm_scan_stop": 0x0055BB1E,
            "open_cfw_app_connection_open_internal": 0x00503D1E,
            "open_cfw_cordio_dm_advertising_extended_mode": 0x004BAC4E,
            "open_cfw_app_advertising_start_internal": 0x004B42F0,
            "open_cfw_app_slave_advertising_start_internal": 0x004B446A,
            "open_cfw_app_advertising_stop_internal": 0x004B43FC,
            "open_cfw_app_advertising_set_data_internal": 0x004B4240,
            "open_cfw_app_advertising_set_type_internal": 0x004B4510,
            "open_cfw_cordio_wsf_timer_start_ms": 0x0052A4C4,
            "open_cfw_cordio_wsf_timer_stop": 0x0052A4D2,
        },
    },
    "app_core": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_app_core.c",
        "recorder": "apple-ambiqsuite-cordio-app-core-record",
        "define": "OPEN_CFW_CORDIO_APP_CORE_",
        "patch": "replace_ambiqsuite_cordio_app_core_",
        "region": "ambiqsuite_cordio_app_core_",
        "evidence": "docs/research/ambiqsuite-cordio-app-framework-source-recovery.md",
        "origin": (
            "AmbiqSuite/Packetcraft Apache-2.0 application UI, connection, "
            "privacy, timer, and ATT database-hash behavior adapted to the "
            "recovered G2 application-framework ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_CORDIO_APP_CORE_PRODUCTION=1",
        "selectors": (
            ("UI_ACTION", "open_cfw_app_ui_action", 0x004BD054, 0x004BD7FA),
            ("UI_PASSKEY", "open_cfw_app_ui_display_passkey", 0x004BD7FA, 0x004BD91E),
            ("UI_CONFIRM", "open_cfw_app_ui_display_confirm_value", 0x004BD91E, 0x004BDA24),
            ("CHECK_BONDED", "open_cfw_app_check_bonded", 0x004BAD26, 0x004BAE66),
            ("ADD_RESOLVING", "open_cfw_app_add_device_to_resolving_list", 0x004BB098, 0x004BB210),
            ("UPDATE_TIMER", "open_cfw_app_connection_update_timer_start", 0x004BB25C, 0x004BB394),
            ("SERVER_HASH", "open_cfw_app_server_handle_database_hash_update", 0x005346E4, 0x0053480C),
        ),
        "providers": {
            "open_cfw_cordio_hci_ll_privacy_supported": 0x00530D54,
            "open_cfw_app_database_get_key": 0x0047AE78,
            "open_cfw_cordio_dm_security_get_local_irk": 0x004D2524,
            "open_cfw_cordio_dm_priv_add_device_to_resolving_list": 0x004D282E,
            "open_cfw_cordio_wsf_timer_start_ms": 0x0052A4C4,
            "open_cfw_app_database_hash_get": 0x0047B45A,
            "open_cfw_app_database_hash_set": 0x0047B468,
            "open_cfw_app_database_set_clients_change_aware_state": 0x0047B438,
            "open_cfw_cordio_atts_set_clients_change_awareness_state": 0x0052D090,
            "open_cfw_cordio_gatt_send_service_changed_indication": 0x004B5A44,
        },
    },
    "app_master": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_app_master.c",
        "recorder": "apple-ambiqsuite-cordio-app-master-record",
        "define": "OPEN_CFW_CORDIO_APP_MASTER_",
        "patch": "replace_ambiqsuite_cordio_app_master_",
        "region": "ambiqsuite_cordio_app_master_",
        "evidence": "docs/research/ambiqsuite-cordio-app-framework-source-recovery.md",
        "origin": (
            "AmbiqSuite/Packetcraft Apache-2.0 master application framework "
            "adapted to the recovered G2 MRAM database and connection ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_CORDIO_APP_MASTER_PRODUCTION=1",
        "selectors": (
            ("SCAN_STOP", "open_cfw_app_master_scan_stop_event", 0x0050367C, 0x005037BC),
            ("RESOLVED_ADDRESS", "open_cfw_app_master_resolved_address_event", 0x0050393E, 0x00503B24),
            ("CONNECTION_OPEN", "open_cfw_app_master_connection_open", 0x00503D1E, 0x00503EA2),
            ("SECURITY_REQUEST", "open_cfw_app_master_security_request", 0x00503EA8, 0x00503FF0),
        ),
        "providers": {
            "open_cfw_cordio_dm_connection_open": 0x0055BCC0,
            "open_cfw_app_database_record_in_use": 0x0047A5D0,
            "open_cfw_app_database_find_by_address": 0x0047AD74,
            "open_cfw_mram_handle_resolved_address":
                "open_cfw_mram_handle_resolved_address",
            "open_cfw_cordio_dm_connection_security_level": 0x004B71B2,
            "open_cfw_app_master_initiate_security_internal": 0x00503498,
        },
    },
    "app_slave": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_app_slave.c",
        "recorder": "apple-ambiqsuite-cordio-app-slave-record",
        "define": "OPEN_CFW_CORDIO_APP_SLAVE_",
        "patch": "replace_ambiqsuite_cordio_app_slave_",
        "region": "ambiqsuite_cordio_app_slave_",
        "evidence": "docs/research/ambiqsuite-cordio-app-framework-source-recovery.md",
        "origin": (
            "AmbiqSuite/Packetcraft Apache-2.0 slave application framework "
            "adapted to the recovered G2 MRAM, ATT cache, and DM dispatch ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION=1",
        "selectors": (
            ("RESOLVE_ADDRESS", "open_cfw_app_slave_resolve_address", 0x004B3606, 0x004B36B2),
            ("RESOLVED_EVENT", "open_cfw_app_slave_resolved_address_event", 0x004B3792, 0x004B38F2),
            ("PROCESS_DM", "open_cfw_app_slave_process_dm_message", 0x004B3CA4, 0x004B4230),
        ),
        "providers": {
            "open_cfw_mram_sync_records": "open_cfw_mram_sync_records",
            "open_cfw_app_database_get_next_record": 0x0047A630,
            "open_cfw_app_slave_database_get_key": 0x0047AE78,
            "open_cfw_cordio_dm_connection_peer_address": 0x004B6EEA,
            "open_cfw_cordio_dm_priv_resolve_address": 0x004D27F6,
            "open_cfw_cordio_atts_ccc_initialize_table": 0x0052C244,
            "open_cfw_app_database_get_csf_record": 0x0047B40C,
            "open_cfw_cordio_atts_csf_connection_open": 0x0052D370,
            "open_cfw_cordio_gatt_send_service_changed_indication": 0x004B5A44,
            "open_cfw_cordio_atts_set_csrk": 0x0052DBB8,
            "open_cfw_cordio_atts_set_sign_counter": 0x0052DBD6,
            "open_cfw_app_slave_security_respond_ltk_internal": 0x004B36B2,
            "open_cfw_app_slave_reset_event_internal": 0x004B32D4,
            "open_cfw_app_slave_connection_open_event_internal": 0x004B36FC,
            "open_cfw_app_slave_connection_close_event_internal": 0x004B3720,
            "open_cfw_app_slave_remote_parameter_event_internal": 0x004B38F2,
            "open_cfw_app_slave_reset_extension_internal": 0x004B48A6,
            "open_cfw_app_slave_advertising_reset_internal": 0x004B3026,
        },
    },
    "app_discovery": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_app_discovery.c",
        "recorder": "apple-ambiqsuite-cordio-app-discovery-record",
        "define": "OPEN_CFW_CORDIO_APP_DISC_",
        "patch": "replace_ambiqsuite_cordio_app_discovery_",
        "region": "ambiqsuite_cordio_app_discovery_",
        "evidence": "docs/research/ambiqsuite-cordio-app-framework-source-recovery.md",
        "origin": (
            "AmbiqSuite/Packetcraft Apache-2.0 application discovery and "
            "configuration state machine adapted to the recovered G2 cached-"
            "database-hash and MRAM record ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_CORDIO_APP_DISC_PRODUCTION=1",
        "selectors": (
            ("CFG_START", "open_cfw_app_disc_configuration_start", 0x00531BD4, 0x00531D58),
            ("START", "open_cfw_app_disc_start", 0x00531D60, 0x00531F12),
            ("RESTART", "open_cfw_app_disc_restart", 0x00531F20, 0x005320C2),
            ("PARSE_READ_TYPE", "open_cfw_app_disc_parse_read_by_type", 0x005322F6, 0x00532624),
            ("PARSE_FIND_INFO", "open_cfw_app_disc_parse_find_information", 0x00532644, 0x0053290A),
            ("PROCESS_ATT", "open_cfw_app_disc_process_att_message", 0x00532924, 0x00532E52),
            ("SET_HANDLE_LIST", "open_cfw_app_disc_set_handle_list", 0x00532EB4, 0x00532FEE),
            ("COMPLETE", "open_cfw_app_disc_complete", 0x0053303C, 0x00533280),
            ("FIND_SERVICE", "open_cfw_app_disc_find_service", 0x005332B4, 0x00533452),
            ("CONFIGURE", "open_cfw_app_disc_configure", 0x00533474, 0x00533622),
            ("READ_HASH", "open_cfw_app_disc_read_database_hash", 0x005336E0, 0x00533846),
        ),
        "providers": {
            "open_cfw_app_disc_database_handle": 0x004BB07C,
            "open_cfw_app_disc_database_new_record": 0x0047A71C,
            "open_cfw_cordio_dm_connection_role": 0x004B73C4,
            "open_cfw_cordio_dm_connection_peer_address": 0x004B6EEA,
            "open_cfw_cordio_dm_connection_peer_address_type": 0x004B6ED8,
            "open_cfw_app_disc_database_set_peer_hash": 0x0047B3AE,
            "open_cfw_app_disc_database_set_cache_by_hash": 0x0047B3CC,
            "open_cfw_app_disc_database_set_status": 0x0047B488,
            "open_cfw_app_disc_database_set_handle_list": 0x0047B48E,
            "open_cfw_app_check_bonded": "open_cfw_app_check_bonded",
            "open_cfw_cordio_dm_connection_set_idle": 0x004B71DC,
            "open_cfw_cordio_wsf_buffer_allocate_candidate":
                "open_cfw_cordio_wsf_buffer_allocate_candidate",
            "open_cfw_cordio_wsf_buffer_free_candidate":
                "open_cfw_cordio_wsf_buffer_free_candidate",
            "open_cfw_cordio_attc_discovery_service_complete": 0x0056BF32,
            "open_cfw_cordio_attc_discovery_characteristic_start": 0x0056C1B8,
            "open_cfw_cordio_attc_discovery_characteristic_complete": 0x0056C1F8,
            "open_cfw_cordio_attc_discovery_configuration_complete": 0x0056C396,
            "open_cfw_cordio_attc_discover_service": 0x0056BF12,
            "open_cfw_cordio_attc_start_configuration": 0x0056C388,
            "open_cfw_cordio_attc_read_by_type_request": 0x0056C4EE,
            "open_cfw_cordio_dm_connection_security_level": 0x004B71B2,
            "open_cfw_app_disc_configuration_start":
                "open_cfw_app_disc_configuration_start",
            "open_cfw_app_disc_start": "open_cfw_app_disc_start",
            "open_cfw_app_disc_restart": "open_cfw_app_disc_restart",
            "open_cfw_app_disc_parse_read_by_type":
                "open_cfw_app_disc_parse_read_by_type",
            "open_cfw_app_disc_parse_find_information":
                "open_cfw_app_disc_parse_find_information",
        },
    },
    "attc_disc": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_attc_disc.c",
        "recorder": "apple-cordio-attc-disc-record",
        "define": "OPEN_CFW_ATTC_DISC_",
        "patch": "replace_cordio_attc_disc_",
        "region": "cordio_attc_disc_",
        "evidence": "docs/research/cordio-attc-disc-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 r20 ATT client discovery with bounded "
            "response-shape, index, handle, and configuration hardening"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_ATTC_DISC_PRODUCTION=1",
        "selectors": (
            ("UUID_COMPARE", "open_cfw_cordio_attc_discovery_uuid_compare", 0x0056B7EC, 0x0056B834),
            ("VERIFY", "open_cfw_cordio_attc_discovery_verify", 0x0056B834, 0x0056B86A),
            ("DESCRIPTORS", "open_cfw_cordio_attc_discovery_descriptors", 0x0056B86A, 0x0056B8FA),
            ("DESCRIPTOR_PAIR", "open_cfw_cordio_attc_discovery_process_descriptor_pair", 0x0056B8FA, 0x0056BA82),
            ("DESCRIPTOR", "open_cfw_cordio_attc_discovery_process_descriptor", 0x0056BA82, 0x0056BB1A),
            ("CHAR_DECL", "open_cfw_cordio_attc_discovery_process_characteristic_declaration", 0x0056BB1C, 0x0056BE24),
            ("CHARACTERISTIC", "open_cfw_cordio_attc_discovery_process_characteristic", 0x0056BE30, 0x0056BEB6),
            ("CONFIG_NEXT", "open_cfw_cordio_attc_discovery_configuration_next", 0x0056BEB6, 0x0056BF12),
            ("SERVICE_START", "open_cfw_cordio_attc_discover_service", 0x0056BF12, 0x0056BF32),
            ("SERVICE_COMPLETE", "open_cfw_cordio_attc_complete_service_discovery", 0x0056BF32, 0x0056C1B8),
            ("CHAR_START", "open_cfw_cordio_attc_start_characteristic_discovery", 0x0056C1B8, 0x0056C1DA),
            ("CHAR_COMPLETE", "open_cfw_cordio_attc_complete_characteristic_discovery", 0x0056C1F8, 0x0056C34C),
            ("CONFIG_START", "open_cfw_cordio_attc_start_configuration", 0x0056C388, 0x0056C396),
            ("CONFIG_COMPLETE", "open_cfw_cordio_attc_complete_configuration", 0x0056C396, 0x0056C3A6),
            ("CONFIG_RESUME", "open_cfw_cordio_attc_resume_configuration", 0x0056C3A6, 0x0056C3B0),
        ),
        "providers": {
            "open_cfw_cordio_attc_discovery_uuid_compare": "open_cfw_cordio_attc_discovery_uuid_compare",
            "open_cfw_cordio_attc_discovery_verify": "open_cfw_cordio_attc_discovery_verify",
            "open_cfw_cordio_attc_discovery_descriptors": "open_cfw_cordio_attc_discovery_descriptors",
            "open_cfw_cordio_attc_discovery_process_descriptor_pair": "open_cfw_cordio_attc_discovery_process_descriptor_pair",
            "open_cfw_cordio_attc_discovery_process_descriptor": "open_cfw_cordio_attc_discovery_process_descriptor",
            "open_cfw_cordio_attc_discovery_process_characteristic_declaration": "open_cfw_cordio_attc_discovery_process_characteristic_declaration",
            "open_cfw_cordio_attc_discovery_process_characteristic": "open_cfw_cordio_attc_discovery_process_characteristic",
            "open_cfw_cordio_attc_discovery_configuration_next": "open_cfw_cordio_attc_discovery_configuration_next",
            "open_cfw_cordio_att_uuid_compare_16_to_128": 0x004B5014,
            "open_cfw_cordio_attc_find_information_request": "open_cfw_cordio_attc_find_information_request",
            "open_cfw_cordio_attc_find_by_type_value_request": "open_cfw_cordio_attc_find_by_type_value_request",
            "open_cfw_cordio_attc_read_by_type_request": "open_cfw_cordio_attc_read_by_type_request",
            "open_cfw_cordio_attc_read_request": "open_cfw_cordio_attc_read_request",
            "open_cfw_cordio_attc_write_request": "open_cfw_cordio_attc_write_request",
        },
    },
    "dm_adv": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_adv.c",
        "recorder": "apple-cordio-dm-adv-record",
        "define": "OPEN_CFW_DM_ADV_",
        "patch": "replace_cordio_dm_adv_",
        "region": "cordio_dm_adv_",
        "evidence": "docs/research/cordio-dm-adv-source-recovery.md",
        "origin": (
            "AmbiqSuite 2.5.1 Apache-2.0 Cordio common advertising "
            "implementation with authenticated inline-payload ABI and "
            "fail-closed handle, pointer, message, and advertising-data bounds"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_ADV_PRODUCTION=1",
        "selectors": (
            ("CB_INIT", "open_cfw_cordio_dm_adv_control_block_initialize", 0x004B3098, 0x004B30E4),
            ("INIT", "open_cfw_cordio_dm_adv_initialize", 0x004B30E4, 0x004B310A),
            ("CONN_COMPLETE", "open_cfw_cordio_dm_adv_generate_connection_complete", 0x004B310A, 0x004B3166),
            ("CONFIGURE", "open_cfw_cordio_dm_adv_configure", 0x004B3166, 0x004B319E),
            ("SET_DATA", "open_cfw_cordio_dm_adv_set_data", 0x004B319E, 0x004B31EA),
            ("START", "open_cfw_cordio_dm_adv_start", 0x004B31EA, 0x004B3250),
            ("STOP", "open_cfw_cordio_dm_adv_stop", 0x004B3250, 0x004B3292),
            ("SET_INTERVAL", "open_cfw_cordio_dm_adv_set_interval", 0x004B3292, 0x004B32B8),
            ("SET_ADDRESS_TYPE", "open_cfw_cordio_dm_adv_set_address_type", 0x004B32B8, 0x004B32CA),
        ),
        "providers": {
            "open_cfw_cordio_dm_adv_control_block_initialize": "open_cfw_cordio_dm_adv_control_block_initialize",
            "open_cfw_cordio_wsf_message_allocate_candidate": "open_cfw_cordio_wsf_message_allocate_candidate",
            "open_cfw_cordio_wsf_message_send_candidate": "open_cfw_cordio_wsf_message_send_candidate",
            "open_cfw_cordio_wsf_task_lock_candidate": "open_cfw_cordio_wsf_task_lock_candidate",
            "open_cfw_cordio_wsf_task_unlock_candidate": "open_cfw_cordio_wsf_task_unlock_candidate",
            "open_cfw_cordio_dm_device_pass_hci_event_to_connection": 0x004D29C2,
        },
    },
    "dm_adv_leg": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_adv_leg.c",
        "recorder": "apple-cordio-dm-adv-leg-record",
        "define": "OPEN_CFW_DM_ADV_LEG_",
        "patch": "replace_cordio_dm_adv_leg_",
        "region": "cordio_dm_adv_leg_",
        "evidence": "docs/research/cordio-dm-adv-leg-source-recovery.md",
        "origin": (
            "AmbiqSuite 2.5.1 Apache-2.0 Cordio legacy advertising state "
            "machine with authenticated flexible-array message ABI and "
            "fail-closed message, handle, data-length, and pointer bounds"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_ADV_LEG_PRODUCTION=1",
        "selectors": (
            ("CONFIG_PARAMETERS", "open_cfw_cordio_dm_adv_legacy_configure_parameters", 0x004B9A80, 0x004B9AC0),
            ("ACTION_CONFIGURE", "open_cfw_cordio_dm_adv_legacy_action_configure", 0x004B9AC0, 0x004B9D1A),
            ("ACTION_SET_DATA", "open_cfw_cordio_dm_adv_legacy_action_set_data", 0x004B9D24, 0x004B9E7A),
            ("ACTION_START", "open_cfw_cordio_dm_adv_legacy_action_start", 0x004B9E88, 0x004BA0E6),
            ("ACTION_STOP", "open_cfw_cordio_dm_adv_legacy_action_stop", 0x004BA0F4, 0x004BA332),
            ("ACTION_REMOVE", "open_cfw_cordio_dm_adv_legacy_action_remove_set", 0x004BA33C, 0x004BA33E),
            ("ACTION_CLEAR", "open_cfw_cordio_dm_adv_legacy_action_clear_sets", 0x004BA33E, 0x004BA340),
            ("ACTION_SET_RANDOM", "open_cfw_cordio_dm_adv_legacy_action_set_random_address", 0x004BA340, 0x004BA342),
            ("ACTION_TIMEOUT", "open_cfw_cordio_dm_adv_legacy_action_timeout", 0x004BA342, 0x004BA456),
            ("RESET", "open_cfw_cordio_dm_adv_legacy_reset", 0x004BA45C, 0x004BA490),
            ("HCI_HANDLER", "open_cfw_cordio_dm_adv_legacy_hci_handler", 0x004BA4B0, 0x004BA6AC),
            ("MESSAGE_HANDLER", "open_cfw_cordio_dm_adv_legacy_message_handler", 0x004BA6AC, 0x004BA6C0),
            ("START_DIRECTED", "open_cfw_cordio_dm_adv_legacy_start_directed", 0x004BA6D4, 0x004BA848),
            ("STOP_DIRECTED", "open_cfw_cordio_dm_adv_legacy_stop_directed", 0x004BA864, 0x004BA9C8),
            ("CONNECTED", "open_cfw_cordio_dm_adv_legacy_connected", 0x004BA9D4, 0x004BAAF8),
            ("CONNECT_FAILED", "open_cfw_cordio_dm_adv_legacy_connect_failed", 0x004BAB04, 0x004BAC28),
            ("INITIALIZE", "open_cfw_cordio_dm_adv_legacy_initialize", 0x004BAC2C, 0x004BAC4E),
        ),
        "copy_selectors": {"ACTION_REMOVE", "ACTION_CLEAR", "ACTION_SET_RANDOM"},
        "providers": {
            "open_cfw_cordio_dm_legacy_link_layer_address_type": 0x004D2A84,
            "open_cfw_cordio_hci_set_legacy_advertising_parameters": 0x0052B420,
            "open_cfw_cordio_hci_set_legacy_advertising_data": 0x0052B3D2,
            "open_cfw_cordio_hci_set_legacy_scan_response_data": 0x0052B554,
            "open_cfw_cordio_hci_set_legacy_advertising_enable": 0x0052B3B0,
            "open_cfw_cordio_wsf_timer_start_ms": 0x0052A4C4,
            "open_cfw_cordio_wsf_timer_stop": 0x0052A4D2,
            "open_cfw_cordio_dm_device_pass_private_event": 0x004B2EA6,
            "open_cfw_cordio_dm_adv_legacy_configure_parameters": "open_cfw_cordio_dm_adv_legacy_configure_parameters",
            "open_cfw_cordio_dm_adv_legacy_action_configure": "open_cfw_cordio_dm_adv_legacy_action_configure",
            "open_cfw_cordio_dm_adv_legacy_action_set_data": "open_cfw_cordio_dm_adv_legacy_action_set_data",
            "open_cfw_cordio_dm_adv_legacy_action_start": "open_cfw_cordio_dm_adv_legacy_action_start",
            "open_cfw_cordio_dm_adv_legacy_action_stop": "open_cfw_cordio_dm_adv_legacy_action_stop",
            "open_cfw_cordio_dm_adv_legacy_action_remove_set": "open_cfw_cordio_dm_adv_legacy_action_remove_set",
            "open_cfw_cordio_dm_adv_legacy_action_clear_sets": "open_cfw_cordio_dm_adv_legacy_action_clear_sets",
            "open_cfw_cordio_dm_adv_legacy_action_set_random_address": "open_cfw_cordio_dm_adv_legacy_action_set_random_address",
            "open_cfw_cordio_dm_adv_legacy_action_timeout": "open_cfw_cordio_dm_adv_legacy_action_timeout",
            "open_cfw_cordio_dm_adv_legacy_reset": "open_cfw_cordio_dm_adv_legacy_reset",
            "open_cfw_cordio_dm_adv_legacy_hci_handler": "open_cfw_cordio_dm_adv_legacy_hci_handler",
            "open_cfw_cordio_dm_adv_legacy_message_handler": "open_cfw_cordio_dm_adv_legacy_message_handler",
            "open_cfw_cordio_dm_adv_initialize": "open_cfw_cordio_dm_adv_initialize",
            "open_cfw_cordio_dm_adv_generate_connection_complete": "open_cfw_cordio_dm_adv_generate_connection_complete",
            "open_cfw_cordio_wsf_task_lock_candidate": "open_cfw_cordio_wsf_task_lock_candidate",
            "open_cfw_cordio_wsf_task_unlock_candidate": "open_cfw_cordio_wsf_task_unlock_candidate",
        },
    },
    "hci_cmd_phy": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_cmd_phy.c",
        "recorder": "apple-cordio-hci-cmd-phy-record",
        "define": "OPEN_CFW_HCI_CMD_PHY_",
        "patch": "replace_cordio_hci_cmd_phy_",
        "region": "cordio_hci_cmd_phy_",
        "evidence": "docs/research/cordio-hci-cmd-phy-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 HCI PHY command wrappers with "
            "explicit little-endian serialization"
        ),
        "license": "Apache-2.0",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_CMD_PHY_PRODUCTION=1",
        "selectors": (
            ("SET_PHY", "HciLeSetPhyCmd", 0x00539E48, 0x00539E92),
        ),
        "providers": {
            "hciCmdAlloc": 0x0052AE38,
            "hciCmdSend": 0x0052AE5E,
        },
    },
    "hci_tr": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_tr.c",
        "recorder": "apple-cordio-hci-tr-record",
        "define": "OPEN_CFW_HCI_TR_",
        "patch": "replace_cordio_hci_tr_",
        "region": "cordio_hci_tr_",
        "evidence": "docs/research/cordio-hci-tr-source-recovery.md",
        "origin": (
            "Clean-room Ambiq Cordio HCI byte transport reconstructed from "
            "authenticated G2 machine-code behavior and public HCI/WSF ABIs, "
            "with atomic fail-closed receive-state reset"
        ),
        "license": "project-original-clean-room",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_TR_PRODUCTION=1",
        "selectors": (
            ("SEND_ACL", "hciTrSendAclData", 0x0053013C, 0x00530166),
            ("SEND_CMD", "hciTrSendCmd", 0x00530166, 0x00530186),
            ("SERIAL_RX", "hciTrSerialRxIncoming", 0x00530186, 0x00530348),
        ),
        "providers": {
            "HciDrvWrite": 0x004B4A02,
            "HciGetMaxRxAclLen": 0x00530D4C,
            "hciCoreRecv": 0x00530C88,
            "WsfMsgDataAlloc": 0x004BF990,
            "WsfMsgAlloc": 0x004BF99E,
        },
    },
    "hci_core_ps": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_core_ps.c",
        "recorder": "apple-cordio-hci-core-ps-record",
        "define": "OPEN_CFW_HCI_CORE_PS_",
        "patch": "replace_cordio_hci_core_ps_",
        "region": "cordio_hci_core_ps_",
        "evidence": "docs/research/cordio-hci-core-ps-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 dual-chip HCI platform behavior "
            "adapted to the authenticated G2 control-block ABI, with "
            "completed-count saturation and fail-closed unknown RX types"
        ),
        "license": "Apache-2.0",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_CORE_PS_PRODUCTION=1",
        "selectors": (
            ("CORE_INIT", "hciCoreInit", 0x00530C00, 0x00530C08),
            ("NUM_COMPLETE", "hciCoreNumCmplPkts", 0x00530C08, 0x00530C88),
            ("CORE_RECV", "hciCoreRecv", 0x00530C88, 0x00530CB2),
            ("CORE_HANDLER", "HciCoreHandler", 0x00530CB2, 0x00530D30),
            ("GET_BD_ADDR", "HciGetBdAddr", 0x00530D30, 0x00530D34),
            ("GET_BUF_SIZE", "HciGetBufSize", 0x00530D34, 0x00530D3C),
            ("GET_LE_FEATURES", "HciGetLeSupFeat", 0x00530D3C, 0x00530D4C),
            ("GET_MAX_RX_ACL", "HciGetMaxRxAclLen", 0x00530D4C, 0x00530D54),
            ("ADV_EXT_SUPPORTED", "HciLeAdvExtSupported", 0x00530D54, 0x00530D68),
        ),
        "providers": {
            "hciCmdInit": 0x0052AEC6,
            "hciCoreConnByHandle": 0x0052A704,
            "hciCoreTxReady": 0x0052A79E,
            "hciCmdTimeout": 0x0052AEE6,
            "hciEvtProcessMsg": 0x0056B390,
            "hciCoreResetSequence": 0x00569B56,
            "hciCoreAclReassembly": 0x0052A962,
            "WsfMsgEnq": 0x004BF9DE,
            "WsfMsgDeq": 0x004BF9EC,
            "WsfMsgFree": 0x004BF9B0,
            "WsfSetEvent": 0x0052B91E,
        },
    },
    "hci_core": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_core.c",
        "recorder": "apple-cordio-hci-core-record",
        "define": "OPEN_CFW_HCI_CORE_",
        "patch": "replace_cordio_hci_core_",
        "region": "cordio_hci_core_",
        "evidence": "docs/research/cordio-hci-core-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 common HCI ACL core adapted to "
            "the authenticated G2 three-connection/six-CIS ABI, return-aware "
            "transport, bounded fragmentation, and hardened reassembly"
        ),
        "license": "Apache-2.0",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_CORE_PRODUCTION=1",
        "selectors": (
            ("CONN_ALLOC", "hciCoreConnAlloc", 0x0052A67C, 0x0052A6B0),
            ("CONN_FREE", "hciCoreConnFree", 0x0052A6B0, 0x0052A704),
            ("CONN_BY_HANDLE", "hciCoreConnByHandle", 0x0052A704, 0x0052A72E),
            ("NEXT_FRAGMENT", "hciCoreNextConnFragment", 0x0052A72E, 0x0052A758),
            ("CONN_OPEN", "hciCoreConnOpen", 0x0052A758, 0x0052A762),
            ("CONN_CLOSE", "hciCoreConnClose", 0x0052A762, 0x0052A76C),
            ("SEND_ACL_CORE", "hciCoreSendAclData", 0x0052A76C, 0x0052A79E),
            ("TX_READY", "hciCoreTxReady", 0x0052A79E, 0x0052A850),
            ("TX_START", "hciCoreTxAclStart", 0x0052A850, 0x0052A8B0),
            ("TX_CONTINUE", "hciCoreTxAclContinue", 0x0052A8B0, 0x0052A936),
            ("TX_COMPLETE", "hciCoreTxAclComplete", 0x0052A936, 0x0052A962),
            ("RX_REASSEMBLY", "hciCoreAclReassembly", 0x0052A962, 0x0052AC02),
            ("PUBLIC_INIT", "HciCoreInit", 0x0052AC02, 0x0052AC6A),
            ("RESET_SEQUENCE", "HciResetSequence", 0x0052AC6A, 0x0052ACCE),
            ("SET_MAX_RX", "HciSetMaxRxAclLen", 0x0052ACCE, 0x0052ACD6),
            ("SET_LE_FEATURE", "HciSetLeSupFeat", 0x0052ACD6, 0x0052AD04),
            ("PUBLIC_SEND_ACL", "HciSendAclData", 0x0052AD04, 0x0052AD9C),
            ("CIS_ALLOC", "hciCoreCisAlloc", 0x0052AD9C, 0x0052ADC2),
            ("CIS_FREE", "hciCoreCisFree", 0x0052ADC2, 0x0052ADEC),
            ("CIS_BY_HANDLE", "hciCoreCisByHandle", 0x0052ADEC, 0x0052AE14),
            ("CIS_OPEN", "hciCoreCisOpen", 0x0052AE24, 0x0052AE2E),
            ("CIS_CLOSE", "hciCoreCisClose", 0x0052AE2E, 0x0052AE38),
        ),
        "providers": {
            "hciTrSendAclData": 0x0053013C,
            "HciGetBufSize": 0x00530D34,
            "hciCoreInit": 0x00530C00,
            "hciCoreResetStart": 0x00569B4A,
            "WsfMsgDataAlloc": 0x004BF990,
            "WsfMsgFree": 0x004BF9B0,
            "WsfMsgEnq": 0x004BF9DE,
            "WsfMsgDeq": 0x004BF9EC,
        },
    },
    "hci_vs": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_vs.c",
        "recorder": "apple-cordio-hci-vs-record",
        "define": "OPEN_CFW_HCI_VS_",
        "patch": "replace_cordio_hci_vs_",
        "region": "cordio_hci_vs_",
        "evidence": "docs/research/cordio-hci-vs-reset-sequence-recovery.md",
        "origin": (
            "clean-room G2 Apollo3/Cooper hybrid HCI reset sequence over "
            "authenticated command/provider ABIs with fail-closed event parsing"
        ),
        "license": "GPL-3.0-only",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_VS_PRODUCTION=1",
        "selectors": (
            ("READ_RESOLVING", "hciCoreReadResolvingListSize", 0x00569B04, 0x00569B2A),
            ("READ_MAX_DATA", "hciCoreReadMaxDataLen", 0x00569B2A, 0x00569B4A),
            ("RESET_START", "hciCoreResetStart", 0x00569B4A, 0x00569B56),
            ("RESET_SEQUENCE", "hciCoreResetSequence", 0x00569B56, 0x00569D26),
        ),
        "providers": {
            "HciLeReadResolvingListSize": 0x0052B7DC,
            "HciLeReadMaxDataLen": 0x0052B24C,
            "HciLeRandCmd": 0x0052B304,
            "HciResetCmd": 0x0052B682,
            "HciVscUpdateBDAddress": 0x004B4D08,
            "HciVscUpdateNvdsParam": 0x004B4C8A,
            "HciVscSetRfPowerLevelEx": 0x004B4CB2,
            "HciSetEventMaskCmd": 0x0052B6BC,
            "HciLeSetEventMaskCmd": 0x0052B492,
            "HciSetEventMaskPage2Cmd": 0x0052B6E4,
            "HciReadBdAddrCmd": 0x0052B606,
            "HciLeReadBufSizeCmd": 0x0052B31E,
            "HciLeReadSupStatesCmd": 0x0052B37C,
            "HciLeReadWhiteListSizeCmd": 0x0052B396,
            "HciLeReadLocalSupFeatCmd": 0x0052B338,
            "HciLeWriteDefDataLen": 0x0052B1BC,
            "hciCoreReadResolvingListSize": "hciCoreReadResolvingListSize",
            "hciCoreReadMaxDataLen": "hciCoreReadMaxDataLen",
        },
    },
    "hci_cmd_core": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_cmd.c",
        "recorder": "apple-cordio-hci-cmd-core-record",
        "define": "OPEN_CFW_HCI_CMD_CORE_",
        "patch": "replace_cordio_hci_cmd_core_",
        "region": "cordio_hci_cmd_core_",
        "evidence": "docs/research/cordio-hci-cmd-source-recovery.md",
        "origin": (
            "clean-room Cordio HCI command queue, timeout, completion, and "
            "reset ownership over the authenticated G2 control-block ABI"
        ),
        "license": "GPL-3.0-only",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_CMD_PRODUCTION=1",
        "selectors": (
            ("ALLOC", "hciCmdAlloc", 0x0052AE38, 0x0052AE5E),
            ("SEND", "hciCmdSend", 0x0052AE5E, 0x0052AEC6),
            ("INIT", "hciCmdInit", 0x0052AEC6, 0x0052AEE6),
            ("TIMEOUT", "hciCmdTimeout", 0x0052AEE6, 0x0052AEF8),
            ("COMPLETE", "hciCmdRecvCmpl", 0x0052AEF8, 0x0052AF10),
            ("ENC_01", "HciDisconnectCmd", 0x0052AF10, 0x0052AF40),
            ("ENC_02", "HciLeConnUpdateCmd", 0x0052AF40, 0x0052AFCC),
            ("ENC_03", "HciLeCreateConnCmd", 0x0052AFCC, 0x0052B0A4),
            ("ENC_04", "HciLeCreateConnCancelCmd", 0x0052B0A4, 0x0052B0BE),
            ("ENC_05", "HciLeRemoteConnParamReqReply", 0x0052B0BE, 0x0052B146),
            ("ENC_06", "HciLeRemoteConnParamReqNegReply", 0x0052B146, 0x0052B176),
            ("ENC_07", "HciLeSetDataLen", 0x0052B176, 0x0052B1BC),
            ("ENC_08", "HciLeWriteDefDataLen", 0x0052B1BC, 0x0052B1F4),
            ("ENC_09", "HciLeReadLocalP256PubKey", 0x0052B1F4, 0x0052B20E),
            ("ENC_10", "HciLeGenerateDHKey", 0x0052B20E, 0x0052B24C),
            ("ENC_11", "HciLeReadMaxDataLen", 0x0052B24C, 0x0052B266),
            ("ENC_12", "HciLeEncryptCmd", 0x0052B266, 0x0052B2A4),
            ("ENC_13", "HciLeLtkReqNegReplCmd", 0x0052B2A4, 0x0052B2CE),
            ("ENC_14", "HciLeLtkReqReplCmd", 0x0052B2CE, 0x0052B304),
            ("ENC_15", "HciLeRandCmd", 0x0052B304, 0x0052B31E),
            ("ENC_16", "HciLeReadBufSizeCmd", 0x0052B31E, 0x0052B338),
            ("ENC_17", "HciLeReadLocalSupFeatCmd", 0x0052B338, 0x0052B352),
            ("ENC_18", "HciLeReadRemoteFeatCmd", 0x0052B352, 0x0052B37C),
            ("ENC_19", "HciLeReadSupStatesCmd", 0x0052B37C, 0x0052B396),
            ("ENC_20", "HciLeReadWhiteListSizeCmd", 0x0052B396, 0x0052B3B0),
            ("ENC_21", "HciLeSetAdvEnableCmd", 0x0052B3B0, 0x0052B3D2),
            ("ENC_22", "HciLeSetAdvDataCmd", 0x0052B3D2, 0x0052B420),
            ("ENC_23", "HciLeSetAdvParamCmd", 0x0052B420, 0x0052B492),
            ("ENC_24", "HciLeSetEventMaskCmd", 0x0052B492, 0x0052B4BA),
            ("ENC_25", "HciLeSetRandAddrCmd", 0x0052B4BA, 0x0052B4E2),
            ("ENC_26", "HciLeSetScanEnableCmd", 0x0052B4E2, 0x0052B50A),
            ("ENC_27", "HciLeSetScanParamCmd", 0x0052B50A, 0x0052B554),
            ("ENC_28", "HciLeSetScanRespDataCmd", 0x0052B554, 0x0052B5A2),
            ("ENC_29", "HciLeStartEncryptionCmd", 0x0052B5A2, 0x0052B606),
            ("ENC_30", "HciReadBdAddrCmd", 0x0052B606, 0x0052B620),
            ("ENC_31", "HciReadBufSizeCmd", 0x0052B620, 0x0052B63A),
            ("ENC_32", "HciReadRssiCmd", 0x0052B63A, 0x0052B664),
            ("CLEAR", "hciClearCmdQueue", 0x0052B664, 0x0052B682),
            ("RESET", "HciResetCmd", 0x0052B682, 0x0052B6AE),
            ("ENC_33", "HciSetEventMaskCmd", 0x0052B6BC, 0x0052B6E4),
            ("ENC_34", "HciSetEventMaskPage2Cmd", 0x0052B6E4, 0x0052B70C),
            ("ENC_35", "HciWriteAuthPayloadTimeout", 0x0052B70C, 0x0052B744),
            ("ENC_36", "HciLeAddDeviceToResolvingListCmd", 0x0052B744, 0x0052B794),
            ("ENC_37", "HciLeRemoveDeviceFromResolvingList", 0x0052B794, 0x0052B7C2),
            ("ENC_38", "HciLeClearResolvingList", 0x0052B7C2, 0x0052B7DC),
            ("ENC_39", "HciLeReadResolvingListSize", 0x0052B7DC, 0x0052B7F6),
            ("ENC_40", "HciLeSetAddrResolutionEnable", 0x0052B7F6, 0x0052B818),
            ("ENC_41", "HciLeSetPrivacyModeCmd", 0x0052B818, 0x0052B84C),
            ("ENC_42", "HciVendorSpecificCmd", 0x0052B84C, 0x0052B87A),
            ("ENC_43", "HciLeRequestPeerScaCmd", 0x0052B87A, 0x0052B8A4),
        ),
        "providers": {
            "WsfMsgAlloc": 0x004BF99E,
            "WsfMsgFree": 0x004BF9B0,
            "WsfMsgEnq": 0x004BF9DE,
            "WsfMsgDeq": 0x004BF9EC,
            "WsfMsgPeek": 0x004BFA00,
            "WsfTimerStartSec": 0x0052A4B8,
            "WsfTimerStop": 0x0052A4D2,
            "hciTrSendCmd": "hciTrSendCmd",
            "HciDrvShutdown": 0x004B49CE,
            "HciDrvRadioBoot": 0x004B48A6,
            "DmDevReset": 0x004B3026,
            "hciCmdAlloc": "hciCmdAlloc",
            "hciCmdSend": "hciCmdSend",
            "hciClearCmdQueue": "hciClearCmdQueue",
            "memcpy": 0x00439BE4,
            "__aeabi_memcpy": 0x00439BE4,
            "__aeabi_memcpy4": 0x00439BE4,
        },
    },
    "hci_driver": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_driver.c",
        "recorder": "apple-cordio-hci-driver-record",
        "define": "OPEN_CFW_HCI_DRIVER_",
        "patch": "replace_cordio_hci_driver_",
        "region": "cordio_hci_driver_",
        "evidence": "docs/research/cordio-hci-driver-source-recovery.md",
        "origin": (
            "clean-room G2 Apollo HCI driver state, transmit queue, WSF "
            "scheduler, and vendor-command implementation over the authenticated ABI"
        ),
        "license": "GPL-3.0-only",
        "whole_translation_unit": True,
        "flag": "-DOPEN_CFW_HCI_DRIVER_PRODUCTION=1",
        # Radio boot/shutdown and the BLEIF transfer handler remain stock in
        # the deliverable while hardware validation is deferred by project
        # direction. Future qualification requires authorized G2 hardware and
        # either a component-specific controller/IRQ fixture or an authenticated
        # golden capture of the blocking read/write bridge.
        "selectors": (
            ("ERROR", "error_check", 0x004B47AE, 0x004B47CC),
            ("WRITE", "hciDrvWrite", 0x004B4A02, 0x004B4A7C),
            ("HANDLER_INIT", "HciDrvHandlerInit", 0x004B4A7C, 0x004B4A98),
            ("INT_SERVICE", "HciDrvIntService", 0x004B4A98, 0x004B4AB2),
            ("NVDS", "HciVscUpdateNvdsParam", 0x004B4C8A, 0x004B4CB2),
            ("RF_POWER", "HciVscSetRfPowerLevelEx", 0x004B4CB2, 0x004B4CD2),
            ("CUSTOM_ADDRESS", "HciVscSetCustom_BDAddr", 0x004B4CD2, 0x004B4D08),
            ("UPDATE_ADDRESS", "HciVscUpdateBDAddress", 0x004B4D08, 0x004B4D18),
            ("EMPTY_QUEUE", "HciDrvEmptyWriteQueue", 0x004B4D18, 0x004B4D2C),
        ),
        "providers": {
            "WsfSetEvent": 0x0052B91E,
            "HciVendorSpecificCmd": "HciVendorSpecificCmd",
            "open_cfw_hci_driver_queue_init": 0x0053006C,
            "open_cfw_hci_driver_queue_add": 0x00530084,
            "open_cfw_hci_driver_queue_remove": 0x005300E2,
        },
    },
    "hci_evt": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_hci_evt.c",
        "recorder": "apple-cordio-hci-evt-record",
        "define": "OPEN_CFW_HCI_EVT_",
        "patch": "replace_cordio_hci_evt_",
        "region": "cordio_hci_evt_",
        "evidence": "docs/research/cordio-hci-evt-source-recovery.md",
        "origin": (
            "clean-room Bluetooth HCI event decoder over the authenticated G2 "
            "Cordio callback ABI and fail-closed wire-length validation"
        ),
        "license": "GPL-3.0-only",
        "whole_translation_unit": True,
        "copy_selectors": {"LINKED_45"},
        "flag": "-DOPEN_CFW_HCI_EVT_PRODUCTION=1",
        "include_dirs": [
            "components/shared/cordio",
            "third_party/cordio/wsf/include",
            "third_party/cordio/ble-host/include",
            "third_party/cordio/ble-host/sources/stack/cfg",
        ],
        "selectors": HCI_EVT_SELECTORS,
        "providers": {
            **HCI_EVT_INTERNAL_PROVIDERS,
            "hciCmdRecvCmpl": "hciCmdRecvCmpl",
            "hciCoreNumCmplPkts": "hciCoreNumCmplPkts",
            "hciCoreConnOpen": "hciCoreConnOpen",
            "hciCoreConnClose": "hciCoreConnClose",
            "hciCoreCisByHandle": "hciCoreCisByHandle",
            "hciCoreCisOpen": "hciCoreCisOpen",
            "hciCoreCisClose": "hciCoreCisClose",
        },
    },
    "dm_conn": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn.c",
        "recorder": "apple-cordio-dm-conn-record",
        "define": "OPEN_CFW_DM_CONN_",
        "patch": "replace_cordio_dm_conn_core_",
        "region": "cordio_dm_conn_core_",
        "evidence": "docs/research/cordio-dm-conn-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 DM connection manager adapted to "
            "the authenticated three-connection G2 ABI, retained tables, and "
            "fail-closed connection, client, callback, and action bounds"
        ),
        "license": "Apache-2.0",
        # Packetcraft's public dm_conn.c is maintained as one translation unit.
        # Each function still has its own section and relocation contract; the
        # recorder deliberately discards the other independently extracted
        # function sections (plus their CANTUNWIND companions) for each leaf.
        "whole_translation_unit": True,
        "copy_selectors": {"LINKED_10", "LINKED_16"},
        "flags": (
            "-DOPEN_CFW_DM_CONN_PRODUCTION=1",
            "-DDM_CONN_MAX=3",
            "-DDM_NUM_ADV_SETS=1",
            "-DDM_NUM_PHYS=2",
            "-Wno-unused-parameter",
        ),
        "include_dirs": [
            "components/shared/cordio",
            "third_party/cordio/wsf/include",
            "third_party/cordio/ble-host/include",
            "third_party/cordio/ble-host/sources/stack/cfg",
            "third_party/cordio/ble-host/sources/stack/dm",
        ],
        "selectors": (
            ("LINKED_01", "dmConnCmplStates", 0x004B5B24, 0x004B5C78),
            ("LINKED_02", "dmConnCcbAlloc", 0x004B5C78, 0x004B5EEA),
            ("LINKED_03", "dmConnCcbDealloc", 0x004B5EF0, 0x004B6012),
            ("LINKED_04", "dmConnCcbByHandle", 0x004B601C, 0x004B6166),
            ("LINKED_05", "dmConnCcbByBdAddr", 0x004B6170, 0x004B62A8),
            ("LINKED_06", "dmConnCcbById", 0x004B62A8, 0x004B62CA),
            ("LINKED_07", "dmConnNum", 0x004B62CA, 0x004B62EA),
            ("LINKED_08", "dmConnExecCback", 0x004B62EA, 0x004B6320),
            ("LINKED_09", "dmConnOpenAccept", 0x004B6324, 0x004B63CA),
            ("LINKED_10", "dmConnSmActNone", 0x004B63CA, 0x004B63CC),
            ("LINKED_11", "dmConnSmActClose", 0x004B63CC, 0x004B63D8),
            ("LINKED_12", "dmConnSmActConnOpened", 0x004B63D8, 0x004B6484),
            ("LINKED_13", "dmConnSmActConnFailed", 0x004B6488, 0x004B64CE),
            ("LINKED_14", "dmConnSmActConnClosed", 0x004B64CE, 0x004B6508),
            ("LINKED_15", "dmConnSmActHciUpdated", 0x004B6508, 0x004B651A),
            ("LINKED_16", "dmConnUpdActNone", 0x004B6530, 0x004B6532),
            ("LINKED_17", "dmConnUpdExecute", 0x004B6532, 0x004B67CA),
            ("LINKED_18", "dmConnReset", 0x004B67EC, 0x004B687E),
            ("LINKED_19", "dmConnMsgHandler", 0x004B6888, 0x004B68A4),
            ("LINKED_20", "dmConnHciHandler", 0x004B68A4, 0x004B6914),
            ("LINKED_21", "dmConn2MsgHandler", 0x004B6914, 0x004B6990),
            ("LINKED_22", "dmConn2HciHandler", 0x004B6990, 0x004B6A16),
            ("LINKED_23", "dmConnUpdMsgHandler", 0x004B6A16, 0x004B6A38),
            ("LINKED_24", "dmConn2ActRssiRead", 0x004B6A38, 0x004B6A6E),
            ("LINKED_25", "dmConn2ActRemoteConnParamReq", 0x004B6A6E, 0x004B6AB0),
            ("LINKED_26", "dmConn2ActDataLenChange", 0x004B6AB8, 0x004B6AFA),
            ("LINKED_27", "dmConn2ActWriteAuthToCmpl", 0x004B6AFA, 0x004B6B28),
            ("LINKED_28", "dmConn2ActAuthToExpired", 0x004B6B28, 0x004B6B50),
            ("LINKED_29", "dmConn2ActReadRemoteFeaturesCmpl", 0x004B6B50, 0x004B6BA6),
            ("LINKED_30", "dmConn2ActReadRemoteVerInfoCmpl", 0x004B6BAC, 0x004B6BEE),
            ("LINKED_31", "dmConn2ActReqPeerSca", 0x004B6BEE, 0x004B6C24),
            ("LINKED_32", "DmConnInit", 0x004B6C28, 0x004B6C5E),
            ("LINKED_33", "DmConnRegister", 0x004B6C64, 0x004B6C82),
            ("LINKED_34", "DmConnClose", 0x004B6C82, 0x004B6CB0),
            ("LINKED_35", "DmReadRemoteFeatures", 0x004B6CB0, 0x004B6D26),
            ("LINKED_36", "DmConnUpdate", 0x004B6D26, 0x004B6D68),
            ("LINKED_37", "dmConnSetConnSpec", 0x004B6D68, 0x004B6D96),
            ("LINKED_38", "dmConnSetScanInterval", 0x004B6D96, 0x004B6DCA),
            ("LINKED_39", "DmConnSetScanInterval", 0x004B6DD4, 0x004B6DE6),
            ("LINKED_40", "DmConnSetConnSpec", 0x004B6DE6, 0x004B6DF2),
            ("LINKED_41", "DmConnReadRssi", 0x004B6DF2, 0x004B6E14),
            ("LINKED_42", "DmRemoteConnParamReqReply", 0x004B6E14, 0x004B6E46),
            ("LINKED_43", "DmRemoteConnParamReqNegReply", 0x004B6E46, 0x004B6E6C),
            ("LINKED_44", "DmConnSetDataLen", 0x004B6E6C, 0x004B6E96),
            ("LINKED_45", "DmConnIdByHandle", 0x004B6E96, 0x004B6EC6),
            ("LINKED_46", "DmConnInUse", 0x004B6EC6, 0x004B6ED8),
            ("LINKED_47", "DmConnPeerAddrType", 0x004B6ED8, 0x004B6EEA),
            ("LINKED_48", "DmConnPeerAddr", 0x004B6EEA, 0x004B6EFA),
            ("LINKED_49", "DmConnLocalAddrType", 0x004B6EFA, 0x004B6F0C),
            ("LINKED_50", "DmConnLocalAddr", 0x004B6F0C, 0x004B6F1C),
            ("LINKED_51", "DmConnPeerRpa", 0x004B6F28, 0x004B706E),
            ("LINKED_52", "DmConnLocalRpa", 0x004B707C, 0x004B71B2),
            ("LINKED_53", "DmConnSecLevel", 0x004B71B2, 0x004B71C2),
            ("LINKED_54", "DmConnSetIdle", 0x004B71DC, 0x004B73A2),
            ("LINKED_55", "DmConnCheckIdle", 0x004B73A2, 0x004B73C4),
            ("LINKED_56", "DmConnRole", 0x004B73C4, 0x004B73E8),
            ("LINKED_57", "vendorCcbInitLike", 0x004B73E8, 0x004B7426),
        ),
        "providers": {
            "memset": 0x0043C0E4,
            "memcpy": 0x00439BE4,
            "__aeabi_memcpy": 0x00439BE4,
            "BdaCpy": 0x004D293C,
            "BdaCmp": 0x004D294A,
            "WsfTaskLock": 0x0052B8C8,
            "WsfTaskUnlock": 0x0052B8D0,
            "WsfMsgAlloc": 0x004BF99E,
            "WsfMsgSend": 0x004BF9BA,
            "HciDisconnectCmd": 0x0052AF10,
            "DmHostAddrType": 0x004D2AA8,
            "HciGetBdAddr": 0x00530D30,
            "dmDevPassEvtToDevPriv": 0x004B2EA6,
            "dmDevPassEvtToConnCte": 0x004B3008,
            "dmConnSmExecute": 0x00533EF4,
            "HciLeRemoteConnParamReqNegReply": 0x0052B146,
            "HciLeRequestPeerScaCmd": 0x0052B87A,
            "HciReadRssiCmd": 0x0052B63A,
            "HciLeSetDataLen": 0x0052B176,
            "HciLeRemoteConnParamReqReply": 0x0052B0BE,
            "HciWriteAuthPayloadTimeout": 0x0052B70C,
            "HciLeReadRemoteFeatCmd": 0x0052B352,
            "DmInitPhyToIdx": 0x004D2B8A,
        },
    },
    "dm_conn_sm": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn_sm.c",
        "recorder": "apple-cordio-dm-conn-sm-record",
        "define": "OPEN_CFW_DM_CONN_SM_",
        "patch": "replace_cordio_dm_conn_sm_",
        "region": "cordio_dm_conn_sm_",
        "evidence": "docs/research/cordio-dm-conn-sm-source-recovery.md",
        "origin": (
            "Packetcraft Apache-2.0 r20.05 connection state machine with "
            "authenticated five-state/eight-event G2 table and fail-closed "
            "CCB, action-set, and action-pointer bounds"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_CONN_SM_PRODUCTION=1",
        "selectors": (
            ("EXECUTE", "open_cfw_cordio_dm_connection_state_machine_execute",
             0x00533EF4, 0x00534532),
        ),
        "providers": {
            "open_cfw_cordio_dm_connection_action_none": 0x0044B610,
        },
    },
    "dm_dev": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_dev.c",
        "recorder": "apple-cordio-dm-dev-record",
        "define": "OPEN_CFW_DM_DEV_",
        "patch": "replace_cordio_dm_dev_",
        "region": "cordio_dm_dev_",
        "evidence": "docs/research/cordio-dm-dev-source-recovery.md",
        "origin": (
            "AmbiqSuite R4.4.1 Apache-2.0 Cordio local-device management "
            "with authenticated G2 component/message ABI and fail-closed "
            "message, component, callback, address, and filter-policy bounds"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_DEV_PRODUCTION=1",
        "selectors": (
            ("ACTION_RESET", "open_cfw_cordio_dm_device_action_reset", 0x004B2DF8, 0x004B2E28),
            ("HCI_RESET", "open_cfw_cordio_dm_device_hci_reset_complete", 0x004B2E28, 0x004B2E3A),
            ("HCI_VENDOR_COMMAND", "open_cfw_cordio_dm_device_hci_vendor_command_complete", 0x004B2E3A, 0x004B2E48),
            ("HCI_VENDOR_EVENT", "open_cfw_cordio_dm_device_hci_vendor_event", 0x004B2E48, 0x004B2E56),
            ("HCI_HARDWARE_ERROR", "open_cfw_cordio_dm_device_hci_hardware_error", 0x004B2E56, 0x004B2E64),
            ("HCI_HANDLER", "open_cfw_cordio_dm_device_hci_handler", 0x004B2E64, 0x004B2E94),
            ("MESSAGE_HANDLER", "open_cfw_cordio_dm_device_message_handler", 0x004B2E94, 0x004B2EA6),
            ("PASS_PRIVACY", "open_cfw_cordio_dm_device_pass_event_to_privacy", 0x004B2EA6, 0x004B3008),
            ("PASS_CTE", "open_cfw_cordio_dm_device_pass_event_to_connection_cte", 0x004B3008, 0x004B3026),
            ("RESET", "open_cfw_cordio_dm_device_reset", 0x004B3026, 0x004B304C),
            ("SET_RANDOM", "open_cfw_cordio_dm_device_set_random_address", 0x004B304C, 0x004B3060),
            ("VENDOR_INIT", "open_cfw_cordio_dm_device_vendor_initialize", 0x004B308C, 0x004B3096),
        ),
        "providers": {
            "open_cfw_cordio_hci_reset_sequence": 0x0052AC6A,
            "open_cfw_cordio_hci_set_random_address": 0x0052B4BA,
            "open_cfw_cordio_wsf_message_allocate_candidate":
                "open_cfw_cordio_wsf_message_allocate_candidate",
            "open_cfw_cordio_wsf_message_send_candidate":
                "open_cfw_cordio_wsf_message_send_candidate",
            "open_cfw_cordio_dm_device_action_reset":
                "open_cfw_cordio_dm_device_action_reset",
            "open_cfw_cordio_dm_device_hci_reset_complete":
                "open_cfw_cordio_dm_device_hci_reset_complete",
            "open_cfw_cordio_dm_device_hci_vendor_command_complete":
                "open_cfw_cordio_dm_device_hci_vendor_command_complete",
            "open_cfw_cordio_dm_device_hci_vendor_event":
                "open_cfw_cordio_dm_device_hci_vendor_event",
            "open_cfw_cordio_dm_device_hci_hardware_error":
                "open_cfw_cordio_dm_device_hci_hardware_error",
        },
    },
    "dm_main": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_main.c",
        "recorder": "apple-cordio-dm-main-record",
        "define": "OPEN_CFW_DM_MAIN_",
        "patch": "replace_cordio_dm_main_",
        "region": "cordio_dm_main_",
        "evidence": "docs/research/cordio-dm-main-source-recovery.md",
        "origin": (
            "AmbiqSuite R4.4.1 Apache-2.0 Cordio device-manager router "
            "with authenticated G2 route/event-size tables and fail-closed "
            "event, component, callback, advertising-data, and PHY bounds"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_MAIN_PRODUCTION=1",
        "copy_selectors": {"EMPTY_RESET", "EMPTY_HANDLER"},
        "selectors": (
            ("HCI_CALLBACK", "open_cfw_cordio_dm_hci_event_callback", 0x004D299C, 0x004D29BE),
            ("EMPTY_RESET", "open_cfw_cordio_dm_empty_reset", 0x004D29BE, 0x004D29C0),
            ("EMPTY_HANDLER", "open_cfw_cordio_dm_empty_handler", 0x004D29C0, 0x004D29C2),
            ("PASS_CONNECTION", "open_cfw_cordio_dm_pass_hci_event_to_connection", 0x004D29C2, 0x004D29CE),
            ("REGISTER", "open_cfw_cordio_dm_register_callback", 0x004D29CE, 0x004D2A06),
            ("FIND_AD_TYPE", "open_cfw_cordio_dm_find_advertising_type", 0x004D2A06, 0x004D2A46),
            ("HANDLER_INIT", "open_cfw_cordio_dm_handler_initialize", 0x004D2A46, 0x004D2A5C),
            ("HANDLER", "open_cfw_cordio_dm_handler", 0x004D2A5C, 0x004D2A7E),
            ("LL_PRIVACY", "open_cfw_cordio_dm_link_layer_privacy_enabled", 0x004D2A7E, 0x004D2A84),
            ("LL_ADDRESS", "open_cfw_cordio_dm_link_layer_address_type", 0x004D2A84, 0x004D2AA8),
            ("HOST_ADDRESS", "open_cfw_cordio_dm_host_address_type", 0x004D2AA8, 0x004D2ACC),
            ("SIZE_EVENT", "open_cfw_cordio_dm_size_of_event", 0x004D2ACC, 0x004D2AE8),
            ("SCAN_INTERNAL", "open_cfw_cordio_dm_scan_phy_to_index_internal", 0x004D2B00, 0x004D2B3E),
            ("SCAN", "open_cfw_cordio_dm_scan_phy_to_index", 0x004D2B3E, 0x004D2B4C),
            ("INIT_INTERNAL", "open_cfw_cordio_dm_initiator_phy_to_index_internal", 0x004D2B4C, 0x004D2B8A),
            ("INIT", "open_cfw_cordio_dm_initiator_phy_to_index", 0x004D2B8A, 0x004D2B98),
        ),
        "providers": {
            "open_cfw_cordio_hci_get_maximum_receive_acl_length": 0x00530D4C,
            "open_cfw_cordio_hci_event_register": 0x005367E4,
            "open_cfw_cordio_dm_hci_event_callback": 0x004D299C,
            "open_cfw_cordio_dm_scan_phy_to_index_internal": 0x004D2B00,
            "open_cfw_cordio_dm_initiator_phy_to_index_internal": 0x004D2B4C,
        },
    },
    "dm_phy": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_phy.c",
        "recorder": "apple-cordio-dm-phy-record",
        "define": "OPEN_CFW_DM_PHY_",
        "patch": "replace_cordio_dm_phy_",
        "region": "cordio_dm_phy_",
        "evidence": "docs/research/cordio-dm-phy-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c and byte-identical AmbiqSuite R4.4.1 "
            "Apache-2.0 Cordio PHY manager with authenticated G2 connection, "
            "event, component, callback, and widened feature-mask ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_PHY_PRODUCTION=1",
        "selectors": (
            ("HCI", "open_cfw_cordio_dm_phy_hci_handler", 0x004C5734, 0x004C5774),
            ("ACTION_READ", "open_cfw_cordio_dm_phy_action_read", 0x004C5774, 0x004C57AE),
            ("ACTION_DEFAULT", "open_cfw_cordio_dm_phy_action_default", 0x004C57AE, 0x004C57D6),
            ("ACTION_UPDATE", "open_cfw_cordio_dm_phy_action_update", 0x004C57D6, 0x004C5810),
            ("SET", "open_cfw_cordio_dm_phy_set", 0x004C5810, 0x004C584A),
            ("INIT", "open_cfw_cordio_dm_phy_initialize", 0x004C584A, 0x004C5868),
        ),
        "providers": {
            "open_cfw_cordio_dm_connection_control_by_handle": 0x004B601C,
            "open_cfw_cordio_dm_connection_control_by_id": 0x004B62A8,
            "open_cfw_cordio_hci_set_phy": 0x00539E48,
            "open_cfw_cordio_hci_set_supported_features": 0x0052ACD6,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
            "open_cfw_cordio_dm_phy_action_read":
                "open_cfw_cordio_dm_phy_action_read",
            "open_cfw_cordio_dm_phy_action_default":
                "open_cfw_cordio_dm_phy_action_default",
            "open_cfw_cordio_dm_phy_action_update":
                "open_cfw_cordio_dm_phy_action_update",
        },
    },
    "dm_conn_master_leg": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn_master_leg.c",
        "recorder": "apple-cordio-dm-conn-master-leg-record",
        "define": "OPEN_CFW_DM_CONN_MASTER_LEG_",
        "patch": "replace_cordio_dm_conn_master_leg_",
        "region": "cordio_dm_conn_master_leg_",
        "evidence": "docs/research/cordio-dm-conn-master-leg-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 legacy master connection manager "
            "with authenticated G2 control-block, message, and split action-table ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_CONN_MASTER_LEG_PRODUCTION=1",
        "selectors": (
            ("OPEN", "open_cfw_cordio_dm_connection_master_legacy_open", 0x00536A28, 0x00536A86),
            ("ACTION_OPEN", "open_cfw_cordio_dm_connection_master_legacy_action_open", 0x00536A86, 0x00536A98),
            ("INIT", "open_cfw_cordio_dm_connection_master_legacy_initialize", 0x00536A98, 0x00536AB0),
        ),
        "providers": {
            "open_cfw_cordio_dm_scan_phy_to_index": 0x004D2B3E,
            "open_cfw_cordio_dm_link_layer_address_type": 0x004D2A84,
            "open_cfw_cordio_hci_create_connection": 0x0052AFCC,
            "open_cfw_cordio_dm_device_pass_event_to_privacy": 0x004B2EA6,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
            "open_cfw_cordio_dm_connection_master_legacy_open":
                "open_cfw_cordio_dm_connection_master_legacy_open",
        },
    },
    "dm_conn_master": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn_master.c",
        "recorder": "apple-cordio-dm-conn-master-record",
        "define": "OPEN_CFW_DM_CONN_MASTER_",
        "patch": "replace_cordio_dm_conn_master_core_",
        "region": "cordio_dm_conn_master_core_",
        "evidence": "docs/research/cordio-dm-conn-master-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 master connection-update and "
            "L2CAP bridge logic over the authenticated G2 CCB/message ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_CONN_MASTER_PRODUCTION=1",
        "selectors": (
            ("CANCEL", "open_cfw_cordio_dm_connection_master_action_cancel", 0x0055BC5C, 0x0055BC70),
            ("UPDATE", "open_cfw_cordio_dm_connection_master_action_update", 0x0055BC70, 0x0055BC7C),
            ("L2C_ACTION", "open_cfw_cordio_dm_connection_master_action_l2c_indication", 0x0055BC7C, 0x0055BC96),
            ("L2C_INDICATION", "open_cfw_cordio_dm_connection_master_l2c_indication", 0x0055BC96, 0x0055BCC0),
            ("OPEN", "open_cfw_cordio_dm_connection_master_open", 0x0055BCC0, 0x0055BCE6),
        ),
        "providers": {
            "open_cfw_cordio_hci_create_connection_cancel": 0x0052B0A4,
            "open_cfw_cordio_dm_device_pass_event_to_privacy": 0x004B2EA6,
            "open_cfw_cordio_hci_connection_update": 0x0052AF40,
            "open_cfw_cordio_l2c_connection_update_response": 0x00537230,
            "open_cfw_cordio_dm_connection_control_by_handle": 0x004B601C,
            "open_cfw_cordio_dm_connection_update_execute": 0x004B6532,
            "open_cfw_cordio_dm_connection_open_accept": 0x004B6324,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
        },
    },
    "dm_conn_slave_leg": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn_slave_leg.c",
        "recorder": "apple-cordio-dm-conn-slave-leg-record",
        "define": "OPEN_CFW_DM_CONN_SLAVE_LEG_",
        "patch": "replace_cordio_dm_conn_slave_leg_",
        "region": "cordio_dm_conn_slave_leg_",
        "evidence": "docs/research/cordio-dm-conn-slave-leg-source-recovery.md",
        "origin": "Packetcraft r20.05c Apache-2.0 legacy slave connection actions over authenticated G2 split tables",
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_CONN_SLAVE_LEG_PRODUCTION=1",
        "selectors": (
            ("ACCEPT", "open_cfw_cordio_dm_connection_slave_legacy_action_accept", 0x00536AC8, 0x00536ADC),
            ("CANCEL", "open_cfw_cordio_dm_connection_slave_legacy_action_cancel", 0x00536ADC, 0x00536AF0),
            ("ACCEPTED", "open_cfw_cordio_dm_connection_slave_legacy_action_accepted", 0x00536AF0, 0x00536B04),
            ("FAILED", "open_cfw_cordio_dm_connection_slave_legacy_action_failed", 0x00536B04, 0x00536B18),
            ("INIT", "open_cfw_cordio_dm_connection_slave_legacy_initialize", 0x00536B18, 0x00536B30),
        ),
        "providers": {
            "open_cfw_cordio_dm_advertising_start_directed": 0x004BA6D4,
            "open_cfw_cordio_dm_advertising_stop_directed": 0x004BA864,
            "open_cfw_cordio_dm_advertising_connected": 0x004BA9D4,
            "open_cfw_cordio_dm_advertising_connect_failed": 0x004BAB04,
            "open_cfw_cordio_dm_connection_action_opened": 0x004B63D8,
            "open_cfw_cordio_dm_connection_action_failed": 0x004B6488,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
        },
    },
    "dm_conn_slave": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_conn_slave.c",
        "recorder": "apple-cordio-dm-conn-slave-record",
        "define": "OPEN_CFW_DM_CONN_SLAVE_",
        "patch": "replace_cordio_dm_conn_slave_core_",
        "region": "cordio_dm_conn_slave_core_",
        "evidence": "docs/research/cordio-dm-conn-slave-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 slave connection-update and "
            "L2CAP bridge logic over the authenticated G2 CCB/message ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_CONN_SLAVE_PRODUCTION=1",
        "selectors": (
            ("CALLBACK", "open_cfw_cordio_dm_connection_slave_update_callback", 0x0056E4F8, 0x0056E526),
            ("UPDATE", "open_cfw_cordio_dm_connection_slave_action_update", 0x0056E526, 0x0056E564),
            ("CONFIRM", "open_cfw_cordio_dm_connection_slave_action_l2c_confirm", 0x0056E564, 0x0056E580),
            ("L2C_CONFIRM", "open_cfw_cordio_dm_connection_slave_l2c_confirm", 0x0056E580, 0x0056E5A4),
            ("L2C_REJECT", "open_cfw_cordio_dm_connection_slave_l2c_reject", 0x0056E5A4, 0x0056E5C6),
        ),
        "providers": {
            "open_cfw_cordio_hci_get_supported_features": 0x00530D3C,
            "open_cfw_cordio_hci_connection_update": 0x0052AF40,
            "open_cfw_cordio_l2c_connection_update_request": 0x00536EA4,
            "open_cfw_cordio_dm_connection_control_by_handle": 0x004B601C,
            "open_cfw_cordio_dm_connection_update_execute": 0x004B6532,
            "open_cfw_cordio_dm_connection_open_accept": 0x004B6324,
            "open_cfw_cordio_dm_connection_slave_update_callback":
                "open_cfw_cordio_dm_connection_slave_update_callback",
        },
    },
    "dm_priv": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_dm_priv.c",
        "recorder": "apple-cordio-dm-priv-record",
        "define": "OPEN_CFW_DM_PRIV_",
        "patch": "replace_cordio_dm_priv_core_",
        "region": "cordio_dm_priv_core_",
        "evidence": "docs/research/cordio-dm-priv-source-recovery.md",
        "origin": (
            "Packetcraft r20.05c Apache-2.0 privacy manager with authenticated "
            "G2 control-block, message, event, interface, and action-table ABI"
        ),
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_DM_PRIV_PRODUCTION=1",
        "selectors": (
            ("RESOLVE_ACTION", "open_cfw_cordio_dm_privacy_action_resolve", 0x004D254C, 0x004D25BA),
            ("RESOLVE_AES", "open_cfw_cordio_dm_privacy_aes_resolve_complete", 0x004D25BA, 0x004D25F2),
            ("ADD_ACTION", "open_cfw_cordio_dm_privacy_action_add", 0x004D25F2, 0x004D2616),
            ("REMOVE_ACTION", "open_cfw_cordio_dm_privacy_action_remove", 0x004D2616, 0x004D262C),
            ("CLEAR_ACTION", "open_cfw_cordio_dm_privacy_action_clear", 0x004D262C, 0x004D2634),
            ("ENABLE_ACTION", "open_cfw_cordio_dm_privacy_action_enable", 0x004D2634, 0x004D263E),
            ("MODE_ACTION", "open_cfw_cordio_dm_privacy_action_mode", 0x004D263E, 0x004D264C),
            ("GENERATE_ACTION", "open_cfw_cordio_dm_privacy_action_generate", 0x004D264C, 0x004D26AC),
            ("GENERATE_AES", "open_cfw_cordio_dm_privacy_aes_generate_complete", 0x004D26AC, 0x004D26E8),
            ("HCI", "open_cfw_cordio_dm_privacy_hci_handler", 0x004D26E8, 0x004D27A0),
            ("SET_ENABLE", "open_cfw_cordio_dm_privacy_set_address_resolution", 0x004D27A0, 0x004D27AE),
            ("MESSAGE", "open_cfw_cordio_dm_privacy_message_handler", 0x004D27AE, 0x004D27C0),
            ("RESET", "open_cfw_cordio_dm_privacy_reset", 0x004D27C0, 0x004D27CE),
            ("AES_MESSAGE", "open_cfw_cordio_dm_privacy_aes_message_handler", 0x004D27CE, 0x004D27E0),
            ("INIT", "open_cfw_cordio_dm_privacy_initialize", 0x004D27E0, 0x004D27F6),
            ("RESOLVE", "open_cfw_cordio_dm_privacy_resolve", 0x004D27F6, 0x004D282E),
            ("ADD", "open_cfw_cordio_dm_privacy_add", 0x004D282E, 0x004D2880),
            ("REMOVE", "open_cfw_cordio_dm_privacy_remove", 0x004D2880, 0x004D28B0),
            ("CLEAR", "open_cfw_cordio_dm_privacy_clear", 0x004D28B0, 0x004D28CC),
            ("ENABLE", "open_cfw_cordio_dm_privacy_enable", 0x004D28CC, 0x004D28F0),
            ("MODE", "open_cfw_cordio_dm_privacy_mode", 0x004D28F0, 0x004D2920),
        ),
        "providers": {
            "open_cfw_cordio_security_aes": 0x00536426,
            "open_cfw_cordio_security_random": 0x0053634E,
            "open_cfw_cordio_hci_add_resolving": 0x0052B744,
            "open_cfw_cordio_hci_remove_resolving": 0x0052B794,
            "open_cfw_cordio_hci_clear_resolving": 0x0052B7C2,
            "open_cfw_cordio_hci_set_address_resolution": 0x0052B7F6,
            "open_cfw_cordio_hci_set_privacy_mode": 0x0052B818,
            "open_cfw_cordio_dm_device_pass_event_to_privacy": 0x004B2EA6,
            "open_cfw_cordio_wsf_message_allocate": 0x004BF99E,
            "open_cfw_cordio_wsf_message_send": 0x004BF9BA,
            "open_cfw_cordio_wsf_task_lock": 0x0052B8C8,
            "open_cfw_cordio_wsf_task_unlock": 0x0052B8D0,
            "open_cfw_cordio_dm_privacy_set_address_resolution":
                "open_cfw_cordio_dm_privacy_set_address_resolution",
        },
    },
    "l2c_main": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_l2c_main.c",
        "recorder": "apple-cordio-l2c-main-record",
        "define": "OPEN_CFW_L2C_MAIN_",
        "patch": "replace_cordio_l2c_main_",
        "region": "cordio_l2c_main_",
        "evidence": "docs/research/cordio-l2c-main-source-recovery.md",
        "origin": "Packetcraft Apache-2.0 r20 L2CAP core with fail-closed packet and registration bounds",
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_L2C_PRODUCTION=1",
        "copy_selectors": {"DEFAULT_CONTROL"},
        "selectors": (
            ("DEFAULT_DATA", "open_cfw_cordio_l2c_default_data_callback", 0x00530538, 0x00530640),
            ("DEFAULT_CID_DATA", "open_cfw_cordio_l2c_default_cid_data_callback", 0x00530640, 0x0053075E),
            ("DEFAULT_CONTROL", "open_cfw_cordio_l2c_default_control_callback", 0x0053076C, 0x0053076E),
            ("SIGNALING", "open_cfw_cordio_l2c_receive_signaling_packet", 0x0053076E, 0x005308E6),
            ("ACL", "open_cfw_cordio_l2c_hci_acl_callback", 0x005308E6, 0x00530A9C),
            ("FLOW", "open_cfw_cordio_l2c_hci_flow_callback", 0x00530AA4, 0x00530ADC),
            ("REJECT", "open_cfw_cordio_l2c_send_command_reject", 0x00530AE0, 0x00530B28),
            ("ALLOCATE", "open_cfw_cordio_l2c_message_allocate", 0x00530B28, 0x00530B34),
            ("INITIALIZE", "open_cfw_cordio_l2c_initialize", 0x00530B34, 0x00530B5E),
            ("REGISTER", "open_cfw_cordio_l2c_register", 0x00530B5E, 0x00530B74),
            ("DATA_REQUEST", "open_cfw_cordio_l2c_data_request", 0x00530BBC, 0x00530BFE),
        ),
        "providers": {
            "open_cfw_cordio_dm_connection_id_by_handle": 0x004B6E96,
            "open_cfw_cordio_dm_connection_role": 0x004B73C4,
            "open_cfw_cordio_hci_acl_register": 0x005367F0,
            "open_cfw_cordio_hci_send_acl_data": 0x0052AD04,
            "open_cfw_cordio_wsf_message_data_allocate_candidate": "open_cfw_cordio_wsf_message_data_allocate_candidate",
            "open_cfw_cordio_wsf_message_free_candidate": "open_cfw_cordio_wsf_message_free_candidate",
            "open_cfw_cordio_l2c_default_data_callback": "open_cfw_cordio_l2c_default_data_callback",
            "open_cfw_cordio_l2c_default_cid_data_callback": "open_cfw_cordio_l2c_default_cid_data_callback",
            "open_cfw_cordio_l2c_default_control_callback": "open_cfw_cordio_l2c_default_control_callback",
            "open_cfw_cordio_l2c_receive_signaling_packet": "open_cfw_cordio_l2c_receive_signaling_packet",
            "open_cfw_cordio_l2c_hci_acl_callback": "open_cfw_cordio_l2c_hci_acl_callback",
            "open_cfw_cordio_l2c_hci_flow_callback": "open_cfw_cordio_l2c_hci_flow_callback",
            "open_cfw_cordio_l2c_message_allocate": "open_cfw_cordio_l2c_message_allocate",
            "open_cfw_cordio_l2c_data_request": "open_cfw_cordio_l2c_data_request",
        },
    },
    "l2c_master": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_l2c_master.c",
        "recorder": "apple-cordio-l2c-master-record",
        "define": "OPEN_CFW_L2C_MASTER_",
        "patch": "replace_cordio_l2c_master_",
        "region": "cordio_l2c_master_",
        "evidence": "docs/research/cordio-l2c-master-source-recovery.md",
        "origin": "Packetcraft Apache-2.0 r20 L2CAP master connection-parameter signaling",
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_L2C_PRODUCTION=1",
        "selectors": (
            ("RECEIVE", "open_cfw_cordio_l2c_master_receive_signaling_packet", 0x00536FBC, 0x005371FE),
            ("INITIALIZE", "open_cfw_cordio_l2c_master_initialize", 0x00537200, 0x00537208),
            ("RESPONSE", "open_cfw_cordio_l2c_connection_update_response", 0x00537230, 0x00537278),
        ),
        "providers": {
            "open_cfw_cordio_l2c_send_command_reject": "open_cfw_cordio_l2c_send_command_reject",
            "open_cfw_cordio_l2c_connection_update_response": "open_cfw_cordio_l2c_connection_update_response",
            "open_cfw_cordio_dm_l2c_connection_update_indication": 0x0055BC96,
            "open_cfw_cordio_l2c_master_receive_signaling_packet": "open_cfw_cordio_l2c_master_receive_signaling_packet",
            "open_cfw_cordio_l2c_message_allocate": "open_cfw_cordio_l2c_message_allocate",
            "open_cfw_cordio_l2c_data_request": "open_cfw_cordio_l2c_data_request",
        },
    },
    "l2c_slave": {
        "source": ROOT / "components/shared/cordio/runtime_cordio_l2c_slave.c",
        "recorder": "apple-cordio-l2c-slave-record",
        "define": "OPEN_CFW_L2C_SLAVE_",
        "patch": "replace_cordio_l2c_slave_",
        "region": "cordio_l2c_slave_",
        "evidence": "docs/research/cordio-l2c-slave-source-recovery.md",
        "origin": "Packetcraft Apache-2.0 r20 L2CAP slave signaling with one-based connection bounds",
        "license": "Apache-2.0",
        "flag": "-DOPEN_CFW_L2C_PRODUCTION=1",
        "selectors": (
            ("TIMEOUT", "open_cfw_cordio_l2c_slave_request_timeout", 0x00536B40, 0x00536C52),
            ("RECEIVE", "open_cfw_cordio_l2c_slave_receive_signaling_packet", 0x00536C5C, 0x00536E76),
            ("INITIALIZE", "open_cfw_cordio_l2c_slave_initialize", 0x00536E78, 0x00536E9A),
            ("UPDATE_REQUEST", "open_cfw_cordio_l2c_connection_update_request", 0x00536EA4, 0x00536F6A),
            ("HANDLER_INIT", "open_cfw_cordio_l2c_slave_handler_initialize", 0x00536F6A, 0x00536F76),
            ("HANDLER", "open_cfw_cordio_l2c_slave_handler", 0x00536FA4, 0x00536FBA),
        ),
        "providers": {
            "open_cfw_cordio_dm_connection_id_by_handle": 0x004B6E96,
            "open_cfw_cordio_dm_l2c_connection_update_confirmation": 0x0056E580,
            "open_cfw_cordio_dm_l2c_command_reject_indication": 0x0056E5A4,
            "open_cfw_cordio_wsf_timer_start_sec_candidate": "open_cfw_cordio_wsf_timer_start_sec_candidate",
            "open_cfw_cordio_wsf_timer_stop_candidate": "open_cfw_cordio_wsf_timer_stop_candidate",
            "open_cfw_cordio_l2c_send_command_reject": "open_cfw_cordio_l2c_send_command_reject",
            "open_cfw_cordio_l2c_message_allocate": "open_cfw_cordio_l2c_message_allocate",
            "open_cfw_cordio_l2c_data_request": "open_cfw_cordio_l2c_data_request",
            "open_cfw_cordio_l2c_slave_receive_signaling_packet": "open_cfw_cordio_l2c_slave_receive_signaling_packet",
            "open_cfw_cordio_l2c_slave_request_timeout": "open_cfw_cordio_l2c_slave_request_timeout",
        },
    },
}


def configure(module: str) -> dict:
    item = MODULES[module]
    base.SOURCE = item["source"]
    base.RECORDER = item["recorder"]
    base.LEAF_DEFINE_PREFIX = item["define"]
    base.PATCH_PREFIX = item["patch"]
    base.EVIDENCE = item["evidence"]
    base.ORIGIN = item["origin"]
    base.LICENSE = item["license"]
    module_flags = item["flags"] if "flags" in item else (item["flag"],)
    base.FLAGS = [*base.FLAGS, *module_flags]
    base.INCLUDE_DIRS = item.get(
        "include_dirs", ["components/shared/cordio"]
    )
    base.SELECTORS = item["selectors"]
    base.PROVIDERS = item["providers"]
    return item


def patch_prefix_owner(name: str):
    """Return the most-specific registered patch prefix for *name*."""
    return next(
        (
            prefix for prefix in sorted(
                (module["patch"] for module in MODULES.values()),
                key=len,
                reverse=True,
            )
            if name.startswith(prefix)
        ),
        None,
    )


def prepare_preserving_nested_routes(item: dict) -> None:
    """Prepare one module without dropping a longer-prefix sibling's routes."""
    config = json.loads(base.CONFIG.read_text())
    prefix = item["patch"]
    preserved = [
        row for row in config.get("patch_sites", [])
        if row.get("name", "").startswith(prefix)
        and patch_prefix_owner(row.get("name", "")) != prefix
    ]
    base.prepare()
    if not preserved:
        return
    config = json.loads(base.CONFIG.read_text())
    present = {row["name"] for row in config.get("patch_sites", [])}
    for row in preserved:
        profiles = row.setdefault("profiles", ["apple-clang"])
        if base.RECORDER not in profiles:
            profiles.append(base.RECORDER)
        if row["name"] not in present:
            config["patch_sites"].append(row)
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def apply_copy_selectors(item: dict) -> None:
    selectors = item.get("copy_selectors", set())
    if not selectors:
        return
    config = json.loads(base.CONFIG.read_text())
    for index, (selector, _function, _start, _end) in enumerate(
        item["selectors"], 1
    ):
        if selector not in selectors:
            continue
        name = f"{base.PATCH_PREFIX}{index:02d}"
        site = next(row for row in config["patch_sites"] if row["name"] == name)
        site["branch"] = "copy"
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def apply_translation_unit_policy(item: dict) -> None:
    if not item.get("whole_translation_unit"):
        return
    config = json.loads(base.CONFIG.read_text())
    source_path = item["source"].relative_to(ROOT).as_posix()
    names = {function for _selector, function, _start, _end in item["selectors"]}
    for row in config.get("relocated_leaves", []):
        if row.get("function") in names and row.get("source", {}).get("path") == source_path:
            row["strict_relocation_contract"] = True
            row["allow_discarded_alloc_sections"] = True
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def drop_module() -> None:
    config = json.loads(base.CONFIG.read_text())
    names = {function for _selector, function, _start, _end in base.SELECTORS}
    config["functions"] = [row for row in config["functions"] if row not in names]
    config["relocated_leaves"] = [
        row for row in config["relocated_leaves"]
        if row.get("function") not in names
    ]
    config["patch_sites"] = [
        row for row in config["patch_sites"]
        if patch_prefix_owner(row.get("name", "")) != base.PATCH_PREFIX
    ]
    config.get("toolchain_profiles", {}).pop(base.RECORDER, None)
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves", "patch_sites"):
        for row in config.get(key, []):
            profiles = row.get("profiles")
            if isinstance(profiles, list):
                row["profiles"] = [profile for profile in profiles if profile != base.RECORDER]
            records = row.get("toolchain_profiles")
            if isinstance(records, dict):
                records.pop(base.RECORDER, None)
                if not records:
                    row.pop("toolchain_profiles", None)
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def record_current_profile() -> None:
    """Attach the module recorder to the current complete placement order.

    This is intentionally non-mutating with respect to functions, leaves, and
    patch routes.  It is used when two independently promoted module names had
    a historical prefix collision and the retained module needs fresh pins for
    the already-reviewed combined order without being removed and re-appended.
    """
    config = json.loads(base.CONFIG.read_text())
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves", "patch_sites"):
        for row in config.get(key, []):
            records = row.get("toolchain_profiles")
            if isinstance(records, dict):
                records.pop(base.RECORDER, None)
                if not records:
                    row.pop("toolchain_profiles", None)
            profiles = row.get("profiles")
            if isinstance(profiles, list) and "apple-clang" in profiles \
                    and base.RECORDER not in profiles:
                profiles.append(base.RECORDER)
    config.setdefault("toolchain_profiles", {})[base.RECORDER] = {}
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def promote_current_or_prepared_profile(item: dict) -> None:
    """Promote a recorder build even when unchanged leaves omit duplicate pins."""
    config = json.loads(base.CONFIG.read_text())
    names = {function for _selector, function, _start, _end in item["selectors"]}
    for row in config.get("relocated_leaves", []):
        if row.get("function") not in names:
            continue
        recorded = row.setdefault("toolchain_profiles", {}).setdefault(
            base.RECORDER, {}
        )
        # The profile recorder deliberately omits byte-identical leaf pins.
        # base.promote() requires an explicit expected block, so carry forward
        # the already-reviewed canonical leaf contract in that case.
        recorded.setdefault("expected", row["expected"])
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")
    base.promote()


def sync_manifest(item: dict) -> None:
    manifest = json.loads(base.MANIFEST.read_text())
    report = json.loads(base.REPORT.read_text())
    run_base = json.loads(base.CONFIG.read_text())["run_base"]
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    provider_path = ROOT / provider["path"]
    provider["size"] = provider_path.stat().st_size
    provider["sha256"] = base.sha(provider_path.read_bytes())
    override["function"] = (
        "Even Apollo510B main firmware with maintained source overlays including "
        "clean-room display, sensor, health, RTOS, case-UART, and Cordio WSF/ATT policy"
    )
    prefix = item["region"]
    # Region prefixes intentionally mirror module names.  Some modules are a
    # strict prefix of another module (for example ``cordio_hci_core_`` and
    # ``cordio_hci_core_ps_``), so a plain startswith() would delete the more
    # specific module's appended regions while syncing the parent.  Attribute
    # each row to the longest registered prefix before deciding ownership.
    region_prefixes = tuple(
        sorted(
            (module["region"] for module in MODULES.values()),
            key=len,
            reverse=True,
        )
    )

    def owned_by_prefix(row: dict, wanted: str) -> bool:
        name = row["name"]
        owner = next((candidate for candidate in region_prefixes if name.startswith(candidate)), None)
        return owner == wanted

    existing_routes = any(
        owned_by_prefix(row, prefix)
        and row.get("address_status") == "generated_source_entry_replacement"
        for row in override["regions"]
    )
    if existing_routes:
        # Rebuilding an already-promoted module changes only the appended
        # compiled leaves.  Preserve its in-place redirect/gap partition so
        # repeated syncs do not require reconstructing the original opaque
        # owner that the first sync deliberately split.
        regions = [
            row for row in override["regions"]
            if not (
                owned_by_prefix(row, prefix)
                and row.get("address_status") in {
                    "source_compiled", "generated_alignment"
                }
            )
        ]
    else:
        regions = [
            row for row in override["regions"]
            if not owned_by_prefix(row, prefix)
        ]
    stock = sorted(item["selectors"], key=lambda row: row[2])
    numbered = list(enumerate(stock, 1))
    groups = []
    for numbered_row in numbered:
        if groups and groups[-1][-1][1][3] == numbered_row[1][2]:
            groups[-1].append(numbered_row)
        else:
            groups.append([numbered_row])
    for group in (() if existing_routes else reversed(groups)):
        first_start, last_end = group[0][1][2], group[-1][1][3]
        owner_index = next(
            index for index, row in enumerate(regions)
            if row.get("address_status") == "official_blob"
            and row.get("target_address", 0) <= first_start
            and row.get("target_address", 0) + row["size"] >= last_end
        )
        owner = regions[owner_index]
        owner_start = owner["target_address"]
        owner_end = owner_start + owner["size"]
        split = []
        if owner_start < first_start:
            before = dict(owner)
            before["size"] = first_start - owner_start
            split.append(before)
        cursor = first_start
        for index, (_selector, function, start, end) in group:
            if cursor < start:
                split.append(base.region(
                    f"{prefix}retained_gap_{index:02d}",
                    "Official WSF compatibility bytes", "official_blob",
                    32 + cursor - run_base, start - cursor, cursor,
                    f"apollo510b/main-opaque-{prefix}gap-0x{cursor:08x}.bin",
                ))
            split.append(base.region(
                f"{prefix}{index:02d}_source_replacement",
                f"Generated guarded redirect replacing {function}",
                "generated_source_entry_replacement", 32 + start - run_base,
                end - start, start,
                f"apollo510b/main-generated-{prefix}{index:02d}-0x{start:08x}.bin",
            ))
            cursor = end
        if cursor < owner_end:
            split.append(base.region(
                f"opaque_after_{prefix.rstrip('_')}_{group[0][0]:02d}",
                "Official Apollo bytes after the source-replaced WSF module",
                "official_blob", 32 + cursor - run_base,
                owner_end - cursor, cursor,
                f"apollo510b/main-opaque-0x{cursor:08x}.bin",
            ))
        regions[owner_index:owner_index + 1] = split

    source_name = item["source"].name
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path", "").endswith(source_name)
    ]
    for row in leaves:
        extraction, placement = row["extraction"], row["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_cordio_wsf_").removesuffix(
            "_candidate"
        ).replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"{prefix}{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-{prefix}{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"{prefix}{slug}_source_text",
            f"Cordio WSF leaf ({function}) compiled from maintained C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-{prefix}{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda row: row["file_offset"])
    final = max(row["file_offset"] + row["size"] for row in regions)
    if final != provider["size"]:
        raise SystemExit(f"manifest tiling ends at {final}, provider has {provider['size']} bytes")
    override["regions"] = regions
    manifest["package"]["expected_size"] = None
    manifest["package"]["expected_sha256"] = None
    base.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", choices=tuple(MODULES))
    parser.add_argument(
        "action",
        choices=("prepare", "record-current", "promote", "drop", "sync-manifest", "pin-package"),
    )
    args = parser.parse_args()
    item = configure(args.module)
    if args.action == "prepare":
        prepare_preserving_nested_routes(item)
        apply_copy_selectors(item)
        apply_translation_unit_policy(item)
    elif args.action == "record-current":
        record_current_profile()
    elif args.action == "promote":
        promote_current_or_prepared_profile(item)
    elif args.action == "drop":
        drop_module()
    elif args.action == "sync-manifest":
        sync_manifest(item)
    else:
        base.pin_package()


if __name__ == "__main__":
    main()

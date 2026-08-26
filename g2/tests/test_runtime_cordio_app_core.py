#!/usr/bin/env python3
"""Exercise the recovered G2 Cordio application-framework core ABI."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_app_core.c"


class RuntimeCordioAppCoreTests(unittest.TestCase):
    def test_host_ui_connection_privacy_timer_and_database_hash(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_app_core.c"

            volatile uint8_t open_cfw_app_core_connection_state[3U * 0x30U];
            volatile uint8_t open_cfw_app_core_handler_id;
            open_cfw_app_ui_callback_t open_cfw_app_core_ui_callback;

            static unsigned ui_calls, key_gets, add_calls, timer_starts;
            static unsigned hash_gets, hash_sets, db_awareness_sets;
            static unsigned att_awareness_sets, service_changed_calls;
            static uint8_t last_ui_event, last_addr_type, last_enable;
            static uint8_t last_db_state, last_att_state;
            static uint16_t last_parameter, last_start, last_end;
            static uint32_t last_ui_value, last_timer_ms, last_handle;
            static void *last_timer;
            static uint8_t peer_key[23], local_irk[16];
            static uint8_t stored_hash[16], replacement_hash[16];
            static uint8_t *hash_result;
            static int privacy_supported = 1;

            static void write32(volatile uint8_t *p, uint32_t v) {
                p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
                p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
            }
            static uint16_t read16(const volatile uint8_t *p) {
                return (uint16_t)p[0]|(uint16_t)((uint16_t)p[1]<<8);
            }
            static void ui_callback(uint8_t event, uint32_t value) {
                last_ui_event=event;last_ui_value=value;ui_calls++;
            }
            int open_cfw_cordio_hci_ll_privacy_supported(void) {
                return privacy_supported;
            }
            uint8_t *open_cfw_app_database_get_key(
                uint32_t handle, uint8_t type, uint8_t *length
            ) {
                assert(handle==0x12345678U&&type==4U&&length==0);
                last_handle=handle;key_gets++;return peer_key;
            }
            uint8_t *open_cfw_cordio_dm_security_get_local_irk(void) {
                return local_irk;
            }
            void open_cfw_cordio_dm_priv_add_device_to_resolving_list(
                uint8_t addr_type, uint8_t *address, uint8_t *key,
                uint8_t *local, uint8_t enable, uint16_t parameter
            ) {
                assert(address==peer_key+16&&key==peer_key&&local==local_irk);
                last_addr_type=addr_type;last_enable=enable;
                last_parameter=parameter;add_calls++;
            }
            void open_cfw_cordio_wsf_timer_start_ms(void *timer, uint32_t ms) {
                last_timer=timer;last_timer_ms=ms;timer_starts++;
            }
            uint8_t *open_cfw_app_database_hash_get(void) {
                hash_gets++;return hash_result;
            }
            void open_cfw_app_database_hash_set(uint8_t *hash) {
                assert(hash==replacement_hash);hash_sets++;
            }
            void open_cfw_app_database_set_clients_change_aware_state(
                uint32_t handle, uint8_t state
            ) {
                assert(handle==0U);last_db_state=state;db_awareness_sets++;
            }
            void open_cfw_cordio_atts_set_clients_change_awareness_state(
                uint8_t connection, uint8_t state
            ) {
                assert(connection==0U);last_att_state=state;att_awareness_sets++;
            }
            void open_cfw_cordio_gatt_send_service_changed_indication(
                uint8_t connection, uint16_t start, uint16_t end
            ) {
                assert(connection==0U);last_start=start;last_end=end;
                service_changed_calls++;
            }

            int main(void) {
                uint8_t event_header[4]={0x34U,0x12U,0U,0U};
                open_cfw_app_server_event_t server_event={0};
                memset((void *)open_cfw_app_core_connection_state,0,
                       sizeof(open_cfw_app_core_connection_state));
                open_cfw_app_core_ui_callback=ui_callback;
                open_cfw_app_ui_action(7U);
                assert(ui_calls==1U&&last_ui_event==7U&&last_ui_value==0U);
                open_cfw_app_ui_display_passkey(654321U);
                assert(ui_calls==2U&&last_ui_event==15U&&last_ui_value==654321U);
                open_cfw_app_ui_display_confirm_value(123456U);
                assert(ui_calls==3U&&last_ui_event==16U&&last_ui_value==123456U);
                open_cfw_app_core_ui_callback=0;
                open_cfw_app_ui_action(1U);assert(ui_calls==3U);

                open_cfw_app_core_connection_state[5]=1U;
                assert(open_cfw_app_check_bonded(1U)==1);
                assert(open_cfw_app_check_bonded(0U)==0);
                assert(open_cfw_app_check_bonded(4U)==0);
                write32(open_cfw_app_core_connection_state,0x12345678U);
                peer_key[0x16]=2U;
                open_cfw_app_add_device_to_resolving_list(event_header,1U);
                assert(key_gets==1U&&add_calls==1U&&last_handle==0x12345678U);
                assert(last_addr_type==2U&&last_enable==1U);
                assert(last_parameter==0x1234U);
                privacy_supported=0;
                open_cfw_app_add_device_to_resolving_list(event_header,1U);
                assert(key_gets==1U&&add_calls==1U);
                privacy_supported=1;
                open_cfw_app_add_device_to_resolving_list(0,1U);
                open_cfw_app_add_device_to_resolving_list(event_header,0U);
                assert(add_calls==1U);

                open_cfw_app_core_handler_id=9U;
                open_cfw_app_connection_update_timer_start(1U);
                assert(timer_starts==1U&&last_timer_ms==30U);
                assert(last_timer==(void *)(open_cfw_app_core_connection_state+0x20));
                assert(read16(open_cfw_app_core_connection_state+0x28)==1U);
                assert(open_cfw_app_core_connection_state[0x2A]==2U);
                assert(open_cfw_app_core_connection_state[0x2C]==9U);
                open_cfw_app_connection_update_timer_start(0U);
                assert(timer_starts==1U);

                memcpy(stored_hash,replacement_hash,16U);
                hash_result=stored_hash;server_event.value=replacement_hash;
                open_cfw_app_server_handle_database_hash_update(&server_event);
                assert(hash_gets==1U&&hash_sets==0U&&service_changed_calls==0U);
                replacement_hash[7]=0xA5U;
                open_cfw_app_server_handle_database_hash_update(&server_event);
                assert(hash_sets==1U&&db_awareness_sets==1U);
                assert(att_awareness_sets==1U&&service_changed_calls==1U);
                assert(last_db_state==3U&&last_att_state==3U);
                assert(last_start==1U&&last_end==0xFFFFU);
                hash_result=0;
                open_cfw_app_server_handle_database_hash_update(&server_event);
                assert(hash_sets==2U&&service_changed_calls==2U);
                server_event.value=0;
                open_cfw_app_server_handle_database_hash_update(&server_event);
                assert(hash_sets==2U);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "cordio-app-core-test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(harness_path), "-o", str(executable)],
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        selectors = [
            "UI_ACTION", "UI_PASSKEY", "UI_CONFIRM", "CHECK_BONDED",
            "ADD_RESOLVING", "UPDATE_TIMER", "SERVER_HASH",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run(
                    ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                     "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                     "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                     "-Wall", "-Wextra", "-Werror",
                     "-DOPEN_CFW_CORDIO_APP_CORE_PRODUCTION=1",
                     f"-DOPEN_CFW_CORDIO_APP_CORE_{selector}_ONLY=1",
                     "-c", str(SOURCE), "-o",
                     str(Path(directory) / f"{selector}.o")],
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()

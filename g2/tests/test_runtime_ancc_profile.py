#!/usr/bin/env python3
"""Exercise the complete G2 ANCC ABI adapter and its isolated target leaves."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_ancc_profile.c"


class RuntimeAnccProfileTests(unittest.TestCase):
    def test_host_adapter_commands_parser_policy_and_dispatch(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_ancc_profile.c"

            struct open_cfw_ancc_state open_cfw_ancc_profile_state;
            struct open_cfw_ancc_product_notification
                open_cfw_ancc_product_notification;
            void *open_cfw_ancc_profile_context;
            void *open_cfw_ancc_profile_argument;
            open_cfw_ancc_u16 *open_cfw_ancc_handle_list;

            static unsigned writes, sends, schedules, removes, syncs;
            static unsigned reports, discoveries;
            static uint8_t write_value[80];
            static uint16_t write_length, write_handle;
            static uint8_t write_connection, scheduled_event;
            static uint32_t scheduled_delay;
            static uint8_t role = 1U, whitelist;
            static uint32_t tick = 7000U, epoch = 1000U;
            static void (*scheduled_callback)(uint8_t);
            static uint16_t *discovered_handles;

            void open_cfw_cordio_attc_write_request(
                uint8_t connection, uint16_t handle, uint16_t length,
                const uint8_t *value
            ) {
                writes++; write_connection=connection; write_handle=handle;
                write_length=length; assert(length<=sizeof(write_value));
                memcpy(write_value,value,length);
            }
            void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t n) {
                static uint8_t message[16]; assert(n<=sizeof(message));
                memset(message,0,sizeof(message)); return message;
            }
            void open_cfw_cordio_wsf_message_send_candidate(
                uint8_t handler, void *message
            ) { assert(handler==9U&&message!=NULL); sends++; }
            void open_cfw_event_loop_push_delayed(
                void (*callback)(uint8_t), uint32_t event, uint32_t delay
            ) { schedules++; scheduled_callback=callback;
                scheduled_event=(uint8_t)event; scheduled_delay=delay; }
            void open_cfw_event_loop_remove_delayed(void (*callback)(uint8_t)) {
                assert(callback==open_cfw_ancc_get_next_notification_handler);
                removes++;
            }
            void open_cfw_ancc_sync_send(
                uint16_t service, const void *value, uint16_t length,
                int (*callback)(int)
            ) { assert(service==0x101U&&value==&open_cfw_ancc_product_notification);
                assert(length==0x2FCU&&callback(37)==37); syncs++; }
            uint8_t open_cfw_cordio_dm_connection_role(uint8_t id) {
                assert(id==7U); return 1U;
            }
            uint8_t open_cfw_ancc_product_role(void) { return role; }
            uint8_t open_cfw_ancc_service_enabled(void) { return 1U; }
            uint8_t open_cfw_ancc_ota_active(void) { return 0U; }
            uint8_t open_cfw_ancc_efs_active(void) { return 0U; }
            uint32_t open_cfw_cmsis_kernel_get_tick_count(void) { return tick; }
            uint32_t open_cfw_ancc_connection_epoch(void) { return epoch; }
            uint8_t open_cfw_ancc_whitelist_result(const uint8_t *app_id) {
                assert(strcmp((const char *)app_id,"com.test") == 0);
                return whitelist;
            }
            void open_cfw_ancc_report_unlisted_app(
                const uint8_t *app_id, const uint8_t *name
            ) { assert(strcmp((const char *)app_id,"com.test")==0);
                assert(strcmp((const char *)name,"Test App")==0); reports++; }
            void open_cfw_ancc_discover_service(
                uint8_t connection, uint8_t uuid_length, const uint8_t *uuid,
                uint8_t count, const void *characteristics, uint16_t *handles
            ) { assert(connection==7U&&uuid_length==16U&&count==5U);
                assert((uintptr_t)uuid==0x00787FC0U);
                assert((uintptr_t)characteristics==0x200030BCU);
                discoveries++; discovered_handles=handles; }

            static uint16_t append_attribute(
                uint8_t *output, uint16_t index, uint8_t id,
                const uint8_t *value, uint16_t length
            ) {
                output[index++]=id; output[index++]=(uint8_t)length;
                output[index++]=(uint8_t)(length>>8);
                memcpy(output+index,value,length);
                return (uint16_t)(index+length);
            }

            int main(void) {
                uint8_t context[0x40]={0};
                uint16_t *handles=(uint16_t *)(context+0x30);
                struct open_cfw_ancc_att_event event={0};
                uint8_t notification[8]={0U,0x18U,4U,1U,0x44U,0x33U,0x22U,0x11U};
                uint8_t response[256]; uint16_t length=0U;
                handles[0]=0x101U;handles[2]=0x103U;handles[3]=0x104U;

                open_cfw_ancc_profile_initialize(9U,context,(void *)0x1234U);
                assert(open_cfw_ancc_handle_list==handles);
                open_cfw_ancc_connection_open_adapter(7U,handles);
                assert(!open_cfw_ancc_no_connection_adapter());
                open_cfw_ancc_get_notification_attributes(handles,0x12345678U);
                assert(writes==1U&&write_connection==7U&&write_handle==0x103U);
                assert(write_length==19U&&write_value[0]==0U);
                assert(write_value[1]==0x78U&&write_value[4]==0x12U);
                open_cfw_ancc_perform_notification_action(handles,0xA1B2C3D4U,1U);
                assert(write_length==6U&&write_value[0]==2U&&write_value[5]==1U);
                open_cfw_ancc_get_app_attributes(handles,(const uint8_t *)"com.test");
                assert(write_value[0]==1U&&write_length==11U);

                event.value=notification;event.value_length=8U;event.handle=handles[0];
                open_cfw_ancc_notification_value_update(handles,&event,0xA2U);
                assert(schedules==1U&&scheduled_event==0xA2U&&scheduled_delay==200U);
                assert(scheduled_callback==open_cfw_ancc_get_next_notification_handler);
                scheduled_callback(scheduled_event); assert(sends==1U);
                { struct open_cfw_ancc_att_event timer={.parameter=7U,.event=0xA2U};
                  open_cfw_ancc_profile_process_message(NULL,&timer); }
                assert(write_value[0]==0U&&write_length==19U);

                response[length++]=0U;response[length++]=0x44U;
                response[length++]=0x33U;response[length++]=0x22U;
                response[length++]=0x11U;
                length=append_attribute(response,length,0U,
                    (const uint8_t *)"com.test",9U);
                length=append_attribute(response,length,1U,
                    (const uint8_t *)"Title",5U);
                length=append_attribute(response,length,2U,
                    (const uint8_t *)"Sub",3U);
                length=append_attribute(response,length,3U,
                    (const uint8_t *)"Message",7U);
                length=append_attribute(response,length,4U,
                    (const uint8_t *)"1",1U);
                length=append_attribute(response,length,5U,
                    (const uint8_t *)"20260826",8U);
                length=append_attribute(response,length,6U,
                    (const uint8_t *)"Open",4U);
                length=append_attribute(response,length,7U,
                    (const uint8_t *)"Dismiss",7U);
                event.value=response;event.value_length=4U;event.handle=handles[3];
                open_cfw_ancc_notification_value_update(handles,&event,0U);
                event.value=response+4U;event.value_length=(uint16_t)(length-4U);
                open_cfw_ancc_notification_value_update(handles,&event,0U);
                assert(strcmp((char *)open_cfw_ancc_product_notification.app_id,
                    "com.test")==0);
                assert(strcmp((char *)open_cfw_ancc_product_notification.title,
                    "Title")==0);
                assert(strcmp((char *)open_cfw_ancc_product_notification.message,
                    "Message")==0);
                assert(write_value[0]==2U&&write_value[5]==1U);

                length=0U;response[length++]=1U;
                memcpy(response+length,"com.test",9U);length+=9U;
                length=append_attribute(response,length,0U,
                    (const uint8_t *)"Test App",8U);
                event.value=response;event.value_length=3U;
                open_cfw_ancc_notification_value_update(handles,&event,0U);
                event.value=response+3U;event.value_length=(uint16_t)(length-3U);
                open_cfw_ancc_notification_value_update(handles,&event,0U);
                assert(syncs==1U&&reports==0U);
                assert(strcmp((char *)open_cfw_ancc_product_notification.app_name,
                    "Test App")==0);

                whitelist=1U; open_cfw_ancc_reset_state_machine();
                event.value=response;event.value_length=length;
                open_cfw_ancc_notification_value_update(handles,&event,0U);
                assert(reports==1U&&syncs==1U);

                role=0U;assert(!open_cfw_ancc_service_discover(7U,handles));
                role=1U;assert(open_cfw_ancc_service_discover(7U,handles));
                assert(discoveries==1U&&discovered_handles==handles);
                assert(open_cfw_ancc_get_active_notification()==
                    &open_cfw_ancc_product_notification);
                open_cfw_ancc_connection_close_adapter();
                assert(open_cfw_ancc_no_connection_adapter());
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "ancc-adapter-test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(harness_path), "-o", str(executable)],
                check=True
            )
            subprocess.run([str(executable)], check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        selectors = [
            "CONN_OPEN", "CONN_CLOSE", "NO_CONNECTION", "POP", "GET_NEXT",
            "GET_NOTIFICATION", "ACTION", "GET_APP", "PUSH", "SYNC_CALLBACK",
            "COMPLETE", "REMOVE", "VALUE_UPDATE", "VALUE_GATE",
            "ATTRIBUTE_CALLBACK", "DISPATCH", "RESET", "INIT",
            "PROCESS_MESSAGE", "DISCOVER", "GET_ACTIVE",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run(
                    ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                     "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                     "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                     "-Wall", "-Wextra", "-Werror",
                     "-DOPEN_CFW_ANCC_PROFILE_PRODUCTION=1",
                     f"-DOPEN_CFW_ANCC_PROFILE_{selector}_ONLY=1",
                     "-I", str(SOURCE_DIR), "-c", str(SOURCE), "-o",
                     str(Path(directory) / f"{selector}.o")], check=True
                )


if __name__ == "__main__":
    unittest.main()

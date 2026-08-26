import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_dev.c"


class CordioDmDeviceSourceTests(unittest.TestCase):
    def test_reset_dispatch_bridges_address_and_filter_policy(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_dm_dev.h"

            struct open_cfw_cordio_dm_device_main_control
                open_cfw_cordio_dm_device_main_control;
            uintptr_t open_cfw_cordio_dm_device_function_interfaces[21];
            static struct open_cfw_cordio_dm_device_function_interface interfaces[21];
            static unsigned reset_calls, reset_sequences, callbacks, sends;
            static unsigned set_random_calls, add_calls, remove_calls, clear_calls;
            static unsigned privacy_calls, cte_calls;
            static uint8_t allocated[4], sent_handler, random_address[6];
            static uint8_t last_callback_event;
            static struct open_cfw_cordio_dm_device_privacy_message privacy_message;
            static struct open_cfw_cordio_dm_device_message_header cte_message;
            static uint8_t allocation_enabled=1U;

            static void component_reset(void) { reset_calls++; }
            static void callback(void *p) { callbacks++; last_callback_event=
                ((struct open_cfw_cordio_dm_device_message_header *)p)->event; }
            static void privacy_handler(struct open_cfw_cordio_dm_device_message_header *p) {
                privacy_calls++; memcpy(&privacy_message,p,sizeof(privacy_message)); }
            static void cte_handler(struct open_cfw_cordio_dm_device_message_header *p) {
                cte_calls++; cte_message=*p; }
            void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t length) {
                assert(length==4U); if (!allocation_enabled) return 0;
                memset(allocated,0,sizeof(allocated)); return allocated; }
            void open_cfw_cordio_wsf_message_send_candidate(uint8_t h,void *p) {
                assert(p==allocated); sends++; sent_handler=h; }
            void open_cfw_cordio_hci_reset_sequence(void) { reset_sequences++; }
            void open_cfw_cordio_hci_set_random_address(const uint8_t *p) {
                set_random_calls++; memcpy(random_address,p,6U); }
            void open_cfw_cordio_hci_white_list_add(uint8_t t,const uint8_t *p) {
                assert(t==2U&&p[0]==1U); add_calls++; }
            void open_cfw_cordio_hci_white_list_remove(uint8_t t,const uint8_t *p) {
                assert(t==3U&&p[0]==1U); remove_calls++; }
            void open_cfw_cordio_hci_white_list_clear(void) { clear_calls++; }

            int main(void) {
                struct open_cfw_cordio_dm_device_message_header event={0};
                uint8_t address[6]={1,2,3,4,5,6}; unsigned i;
                for (i=0;i<21;i++) { interfaces[i].reset=component_reset;
                    open_cfw_cordio_dm_device_function_interfaces[i]=(uintptr_t)&interfaces[i]; }
                interfaces[1].message_handler=privacy_handler;
                interfaces[13].message_handler=cte_handler;
                open_cfw_cordio_dm_device_main_control.callback=(uintptr_t)callback;

                open_cfw_cordio_dm_device_action_reset(&event);
                assert(reset_calls==21U&&reset_sequences==1U);
                assert(open_cfw_cordio_dm_device_main_control.resetting==1U);
                open_cfw_cordio_dm_device_action_reset(&event);
                assert(reset_calls==21U&&reset_sequences==1U);

                event.event=0U; open_cfw_cordio_dm_device_hci_handler(&event);
                assert(callbacks==1U&&last_callback_event==0x20U);
                assert(open_cfw_cordio_dm_device_main_control.resetting==0U);
                event.event=18U; open_cfw_cordio_dm_device_hci_handler(&event);
                assert(last_callback_event==0x7BU);
                event.event=19U; open_cfw_cordio_dm_device_hci_handler(&event);
                assert(last_callback_event==0x7AU);
                event.event=20U; open_cfw_cordio_dm_device_hci_handler(&event);
                assert(last_callback_event==0x79U&&callbacks==4U);
                event.event=21U; open_cfw_cordio_dm_device_hci_handler(&event);
                assert(callbacks==4U);

                open_cfw_cordio_dm_device_main_control.resetting=0U;
                event.event=0x38U; open_cfw_cordio_dm_device_message_handler(&event);
                assert(reset_sequences==2U);
                event.event=0x39U; open_cfw_cordio_dm_device_message_handler(&event);
                assert(reset_sequences==2U);

                open_cfw_cordio_dm_device_pass_event_to_privacy(12U,0x21U,1U,9U);
                assert(privacy_calls==1U&&privacy_message.header.event==12U);
                assert(privacy_message.header.parameter==0x21U);
                assert(privacy_message.advertising_handle==1U&&privacy_message.connectable==1U);
                open_cfw_cordio_dm_device_pass_event_to_connection_cte(7U,3U);
                assert(cte_calls==1U&&cte_message.event==0x6FU);
                assert(cte_message.status==7U&&cte_message.parameter==3U);

                open_cfw_cordio_dm_device_main_control.handler_id=9U;
                open_cfw_cordio_dm_device_main_control.resetting=1U;
                open_cfw_cordio_dm_device_reset();
                assert(sends==1U&&sent_handler==9U&&allocated[2]==0x38U);
                assert(open_cfw_cordio_dm_device_main_control.resetting==0U);
                allocation_enabled=0U; open_cfw_cordio_dm_device_reset(); assert(sends==1U);

                open_cfw_cordio_dm_device_set_random_address(address);
                assert(set_random_calls==1U&&memcmp(random_address,address,6U)==0);
                assert(memcmp(open_cfw_cordio_dm_device_main_control.local_address,address,6U)==0);
                open_cfw_cordio_dm_device_set_random_address(0); assert(set_random_calls==1U);
                open_cfw_cordio_dm_device_white_list_add(2U,address);
                open_cfw_cordio_dm_device_white_list_remove(3U,address);
                open_cfw_cordio_dm_device_white_list_clear();
                assert(add_calls==1U&&remove_calls==1U&&clear_calls==1U);

                assert(open_cfw_cordio_dm_device_set_filter_policy_internal(1U,0U,3U)==1U);
                assert(open_cfw_cordio_dm_device_main_control.advertising_filter_policy[1]==3U);
                assert(open_cfw_cordio_dm_device_set_filter_policy_internal(2U,0U,1U)==0U);
                assert(open_cfw_cordio_dm_device_set_filter_policy(1U,3U)==1U);
                assert(open_cfw_cordio_dm_device_main_control.scanning_filter_policy==3U);
                assert(open_cfw_cordio_dm_device_set_filter_policy(2U,2U)==0U);
                assert(open_cfw_cordio_dm_device_set_filter_policy(2U,1U)==1U);
                open_cfw_cordio_dm_device_main_control.synchronization_options=0xA4U;
                assert(open_cfw_cordio_dm_device_set_extended_filter_policy(0U,3U,1U)==1U);
                assert(open_cfw_cordio_dm_device_main_control.synchronization_options==0xA5U);
                assert(open_cfw_cordio_dm_device_set_filter_policy(9U,0U)==0U);
                open_cfw_cordio_dm_device_vendor_initialize(4U);

                open_cfw_cordio_dm_device_hci_handler(0);
                open_cfw_cordio_dm_device_message_handler(0);
                open_cfw_cordio_dm_device_hci_reset_complete(0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(SOURCE), str(harness_path),
                 "-o", str(executable)], check=True)
            subprocess.run([str(executable)], check=True)

    def test_complete_and_all_isolated_cortex_m55_builds(self) -> None:
        selectors = [
            "ACTION_RESET", "HCI_RESET", "HCI_VENDOR_COMMAND",
            "HCI_VENDOR_EVENT", "HCI_HARDWARE_ERROR", "HCI_HANDLER",
            "MESSAGE_HANDLER", "PASS_PRIVACY", "PASS_CTE", "RESET",
            "SET_RANDOM", "VENDOR_INIT", "WHITE_LIST_ADD",
            "WHITE_LIST_REMOVE", "WHITE_LIST_CLEAR", "FILTER_INTERNAL",
            "FILTER", "FILTER_EXTENDED",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in [None, *selectors]:
                command = [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR),
                ]
                if selector:
                    command.append(f"-DOPEN_CFW_DM_DEV_{selector}_ONLY=1")
                command += ["-DOPEN_CFW_DM_DEV_PRODUCTION=1", "-c",
                            str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

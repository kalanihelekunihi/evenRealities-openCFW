import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_main.c"


class CordioDmMainSourceTests(unittest.TestCase):
    def test_router_registration_advertising_address_and_phy_policy(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_dm_main.h"

            struct open_cfw_cordio_dm_device_main_control
                open_cfw_cordio_dm_device_main_control;
            uintptr_t open_cfw_cordio_dm_device_function_interfaces[21];
            uintptr_t open_cfw_cordio_dm_default_interface;
            static struct open_cfw_cordio_dm_device_function_interface interfaces[21];
            static unsigned hci_calls[21], message_calls[21], callback_calls;
            static uint8_t last_hci_event, last_message_event, callback_event;
            static uint8_t callback_status;
            static uint16_t maximum_receive_acl_length = 69U;
            static void (*registered_hci_callback)(
                struct open_cfw_cordio_dm_device_message_header *event);

            #define DEFINE_HCI(N) static void hci_##N( \
                struct open_cfw_cordio_dm_device_message_header *event) { \
                hci_calls[N]++; last_hci_event = event->event; }
            #define DEFINE_MESSAGE(N) static void message_##N( \
                struct open_cfw_cordio_dm_device_message_header *message) { \
                message_calls[N]++; last_message_event = message->event; }
            DEFINE_HCI(0) DEFINE_HCI(1) DEFINE_HCI(2) DEFINE_HCI(3)
            DEFINE_HCI(4) DEFINE_HCI(5) DEFINE_HCI(6) DEFINE_HCI(7)
            DEFINE_HCI(8) DEFINE_HCI(9) DEFINE_HCI(10) DEFINE_HCI(11)
            DEFINE_HCI(12) DEFINE_HCI(13) DEFINE_HCI(14) DEFINE_HCI(15)
            DEFINE_HCI(16) DEFINE_HCI(17) DEFINE_HCI(18) DEFINE_HCI(19)
            DEFINE_HCI(20)
            DEFINE_MESSAGE(0) DEFINE_MESSAGE(1) DEFINE_MESSAGE(2)
            DEFINE_MESSAGE(3) DEFINE_MESSAGE(4) DEFINE_MESSAGE(5)
            DEFINE_MESSAGE(6) DEFINE_MESSAGE(7) DEFINE_MESSAGE(8)
            DEFINE_MESSAGE(9) DEFINE_MESSAGE(10) DEFINE_MESSAGE(11)
            DEFINE_MESSAGE(12) DEFINE_MESSAGE(13) DEFINE_MESSAGE(14)
            DEFINE_MESSAGE(15) DEFINE_MESSAGE(16) DEFINE_MESSAGE(17)
            DEFINE_MESSAGE(18) DEFINE_MESSAGE(19) DEFINE_MESSAGE(20)

            static void (*const hci_handlers[21])(
                struct open_cfw_cordio_dm_device_message_header *) = {
                hci_0,hci_1,hci_2,hci_3,hci_4,hci_5,hci_6,hci_7,hci_8,
                hci_9,hci_10,hci_11,hci_12,hci_13,hci_14,hci_15,hci_16,
                hci_17,hci_18,hci_19,hci_20
            };
            static void (*const message_handlers[21])(
                struct open_cfw_cordio_dm_device_message_header *) = {
                message_0,message_1,message_2,message_3,message_4,message_5,
                message_6,message_7,message_8,message_9,message_10,message_11,
                message_12,message_13,message_14,message_15,message_16,
                message_17,message_18,message_19,message_20
            };

            void open_cfw_cordio_hci_event_register(
                void (*callback)(struct open_cfw_cordio_dm_device_message_header *)) {
                registered_hci_callback = callback;
            }
            uint16_t open_cfw_cordio_hci_get_maximum_receive_acl_length(void) {
                return maximum_receive_acl_length;
            }
            static void application_callback(void *raw) {
                struct open_cfw_cordio_dm_device_message_header *event = raw;
                callback_calls++; callback_event = event->event;
                callback_status = event->status;
            }

            int main(void) {
                struct open_cfw_cordio_dm_device_message_header event = {0};
                uint8_t advertising[] = {2U,1U,0xAAU,3U,9U,'x','y',0U};
                uint8_t malformed[] = {4U,9U,1U};
                unsigned i;
                for (i=0U;i<21U;i++) {
                    interfaces[i].hci_handler=hci_handlers[i];
                    interfaces[i].message_handler=message_handlers[i];
                    open_cfw_cordio_dm_device_function_interfaces[i]=
                        (uintptr_t)&interfaces[i];
                }
                open_cfw_cordio_dm_default_interface=(uintptr_t)&interfaces[0];

                event.event=0U; open_cfw_cordio_dm_hci_event_callback(&event);
                assert(hci_calls[7]==1U&&last_hci_event==0U);
                event.event=1U; open_cfw_cordio_dm_hci_event_callback(&event);
                assert(hci_calls[3]==1U);
                open_cfw_cordio_dm_device_main_control.resetting=1U;
                event.event=1U; open_cfw_cordio_dm_hci_event_callback(&event);
                assert(hci_calls[3]==1U);
                event.event=0U; open_cfw_cordio_dm_hci_event_callback(&event);
                assert(hci_calls[7]==2U);
                open_cfw_cordio_dm_device_main_control.resetting=0U;
                event.event=70U; open_cfw_cordio_dm_hci_event_callback(&event);
                event.event=90U; open_cfw_cordio_dm_hci_event_callback(&event);
                open_cfw_cordio_dm_hci_event_callback(0);

                event.event=9U;
                open_cfw_cordio_dm_pass_hci_event_to_connection(&event);
                assert(hci_calls[3]==2U&&last_hci_event==9U);
                open_cfw_cordio_dm_pass_hci_event_to_connection(0);

                open_cfw_cordio_dm_device_function_interfaces[8]=
                    open_cfw_cordio_dm_default_interface;
                maximum_receive_acl_length=1U;
                open_cfw_cordio_dm_register_callback((uintptr_t)application_callback);
                assert(callback_calls==0U);
                open_cfw_cordio_dm_device_function_interfaces[8]=
                    (uintptr_t)&interfaces[8];
                maximum_receive_acl_length=68U;
                open_cfw_cordio_dm_register_callback((uintptr_t)application_callback);
                assert(callback_calls==1U&&callback_event==0x78U&&callback_status==1U);
                maximum_receive_acl_length=69U;
                open_cfw_cordio_dm_register_callback((uintptr_t)application_callback);
                assert(callback_calls==1U);
                open_cfw_cordio_dm_register_callback(0U);

                assert(open_cfw_cordio_dm_find_advertising_type(9U,
                    sizeof(advertising),advertising)==&advertising[3]);
                assert(open_cfw_cordio_dm_find_advertising_type(8U,
                    sizeof(advertising),advertising)==0);
                assert(open_cfw_cordio_dm_find_advertising_type(9U,
                    sizeof(malformed),malformed)==0);
                assert(open_cfw_cordio_dm_find_advertising_type(9U,4U,0)==0);

                open_cfw_cordio_dm_device_main_control.resetting=1U;
                open_cfw_cordio_dm_main_host_link_layer_privacy=1U;
                open_cfw_cordio_dm_handler_initialize(12U);
                assert(open_cfw_cordio_dm_device_main_control.handler_id==12U);
                assert(open_cfw_cordio_dm_device_main_control.resetting==0U);
                assert(open_cfw_cordio_dm_main_host_link_layer_privacy==0U);
                assert(registered_hci_callback==open_cfw_cordio_dm_hci_event_callback);
                event.event=(uint8_t)((5U<<3U)|2U);
                open_cfw_cordio_dm_handler(0U,&event);
                assert(message_calls[5]==1U&&last_message_event==event.event);
                open_cfw_cordio_dm_device_main_control.resetting=1U;
                open_cfw_cordio_dm_handler(0U,&event);
                assert(message_calls[5]==1U);
                open_cfw_cordio_dm_device_main_control.resetting=0U;
                event.event=(uint8_t)(21U<<3U);
                open_cfw_cordio_dm_handler(0U,&event);
                open_cfw_cordio_dm_handler(0U,0);

                assert(open_cfw_cordio_dm_link_layer_privacy_enabled()==0U);
                assert(open_cfw_cordio_dm_link_layer_address_type(0U)==0U);
                assert(open_cfw_cordio_dm_host_address_type(2U)==2U);
                open_cfw_cordio_dm_main_host_link_layer_privacy=1U;
                assert(open_cfw_cordio_dm_link_layer_privacy_enabled()==1U);
                assert(open_cfw_cordio_dm_link_layer_address_type(0U)==2U);
                assert(open_cfw_cordio_dm_link_layer_address_type(1U)==3U);
                assert(open_cfw_cordio_dm_link_layer_address_type(4U)==4U);
                assert(open_cfw_cordio_dm_host_address_type(2U)==0U);
                assert(open_cfw_cordio_dm_host_address_type(3U)==1U);
                assert(open_cfw_cordio_dm_host_address_type(4U)==4U);

                event.event=0x20U; assert(open_cfw_cordio_dm_size_of_event(&event)==4U);
                event.event=0x23U; assert(open_cfw_cordio_dm_size_of_event(&event)==12U);
                event.event=0x7BU; assert(open_cfw_cordio_dm_size_of_event(&event)==136U);
                event.event=0x7CU; assert(open_cfw_cordio_dm_size_of_event(&event)==4U);
                assert(open_cfw_cordio_dm_size_of_event(0)==4U);

                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(0U,2U)==0U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(1U,4U)==0U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(2U,1U)==0U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(2U,2U)==1U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(3U,1U)==0U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(3U,2U)==1U);
                assert(open_cfw_cordio_dm_scan_phy_to_index_internal(3U,4U)==2U);
                assert(open_cfw_cordio_dm_scan_phy_to_index(1U)==0U);
                assert(open_cfw_cordio_dm_scan_phy_to_index(4U)==1U);
                assert(open_cfw_cordio_dm_initiator_phy_to_index_internal(1U,4U)==0U);
                assert(open_cfw_cordio_dm_initiator_phy_to_index_internal(3U,4U)==2U);
                assert(open_cfw_cordio_dm_initiator_phy_to_index(2U)==1U);
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
            "HCI_CALLBACK", "EMPTY_RESET", "EMPTY_HANDLER", "PASS_CONNECTION",
            "REGISTER", "FIND_AD_TYPE", "HANDLER_INIT", "HANDLER",
            "LL_PRIVACY", "LL_ADDRESS", "HOST_ADDRESS", "SIZE_EVENT",
            "SCAN_INTERNAL", "SCAN", "INIT_INTERNAL", "INIT",
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
                    command.append(f"-DOPEN_CFW_DM_MAIN_{selector}_ONLY=1")
                command += ["-DOPEN_CFW_DM_MAIN_PRODUCTION=1", "-c",
                            str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

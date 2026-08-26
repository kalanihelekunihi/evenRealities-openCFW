import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_adv_leg.c"


class CordioDmAdvLegacySourceTests(unittest.TestCase):
    def test_host_state_machine_callbacks_dispatch_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_dm_adv_leg.h"

            struct open_cfw_cordio_dm_adv_control_block
                open_cfw_cordio_dm_adv_control_block;
            struct open_cfw_cordio_dm_main_control_block
                open_cfw_cordio_dm_main_control_block;
            uint8_t open_cfw_cordio_dm_adv_legacy_type;
            const struct open_cfw_cordio_dm_adv_legacy_function_interface
                *open_cfw_cordio_dm_adv_registered_interface;
            uintptr_t open_cfw_cordio_dm_dev_adv_set_random_address_callback;

            static unsigned params, adv_data, scan_data, enables, timer_starts;
            static unsigned timer_stops, private_events, callbacks, initializes;
            static unsigned completions, locks, unlocks;
            static uint8_t enabled, data_len, last_event, last_parameter;
            static uint8_t callback_event, complete_status, copied[31];
            static uint16_t timer_ms, param_min, param_max;
            static uint8_t param_type, param_own, param_peer, param_channels;
            static uint8_t param_filter, param_address[6];

            uint8_t open_cfw_cordio_dm_legacy_link_layer_address_type(uint8_t v) {
                return (uint8_t)(v + 0x40U);
            }
            void open_cfw_cordio_hci_set_legacy_advertising_parameters(
                uint16_t min, uint16_t max, uint8_t type, uint8_t own,
                uint8_t peer, const uint8_t *address, uint8_t channels,
                uint8_t filter) {
                params++; param_min=min; param_max=max; param_type=type;
                param_own=own; param_peer=peer; param_channels=channels;
                param_filter=filter; memcpy(param_address,address,6U);
            }
            void open_cfw_cordio_hci_set_legacy_advertising_data(
                uint8_t len,const uint8_t *data) {
                adv_data++; data_len=len; memcpy(copied,data,len);
            }
            void open_cfw_cordio_hci_set_legacy_scan_response_data(
                uint8_t len,const uint8_t *data) {
                scan_data++; data_len=len; memcpy(copied,data,len);
            }
            void open_cfw_cordio_hci_set_legacy_advertising_enable(uint8_t v) {
                enables++; enabled=v;
            }
            void open_cfw_cordio_wsf_timer_start_ms(void *timer,uint32_t ms) {
                (void)timer; timer_starts++; timer_ms=(uint16_t)ms;
            }
            void open_cfw_cordio_wsf_timer_stop(void *timer) {
                (void)timer; timer_stops++;
            }
            void open_cfw_cordio_dm_device_pass_private_event(
                uint8_t event,uint8_t parameter,uint8_t handle,uint8_t connectable) {
                assert(handle==0U&&connectable==0U); private_events++;
                last_event=event; last_parameter=parameter;
            }
            void open_cfw_cordio_dm_adv_legacy_application_callback(void *event) {
                callbacks++;
                callback_event=((struct open_cfw_cordio_dm_message_header *)event)->event;
            }
            void open_cfw_cordio_dm_adv_initialize(void) {
                initializes++;
                open_cfw_cordio_dm_adv_control_block.advertising_state[0]=0U;
                open_cfw_cordio_dm_adv_control_block.advertising_type[0]=0xFFU;
            }
            void open_cfw_cordio_dm_adv_generate_connection_complete(
                uint8_t handle,uint8_t status) {
                assert(handle==0U); completions++; complete_status=status;
            }
            void open_cfw_cordio_wsf_task_lock_candidate(void) { locks++; }
            void open_cfw_cordio_wsf_task_unlock_candidate(void) { unlocks++; }

            int main(void) {
                uint8_t peer[6]={1,2,3,4,5,6};
                uint8_t storage[64]={0};
                union open_cfw_cordio_dm_adv_legacy_message *message=
                    (union open_cfw_cordio_dm_adv_legacy_message *)(void *)storage;
                struct open_cfw_cordio_dm_message_header hci={0U,53U,0U};

                open_cfw_cordio_dm_adv_control_block.interval_minimum[0]=32U;
                open_cfw_cordio_dm_adv_control_block.interval_maximum[0]=64U;
                open_cfw_cordio_dm_adv_control_block.channel_map[0]=7U;
                open_cfw_cordio_dm_main_control_block.advertising_address_type=2U;
                open_cfw_cordio_dm_main_control_block.advertising_filter_policy[0]=3U;
                open_cfw_cordio_dm_adv_legacy_configure_parameters(5U,1U,peer);
                assert(params==1U&&param_min==32U&&param_max==64U);
                assert(param_type==5U&&param_own==0x42U&&param_peer==1U);
                assert(param_channels==7U&&param_filter==3U);
                assert(memcmp(param_address,peer,6U)==0);
                assert(open_cfw_cordio_dm_adv_legacy_type==5U);
                open_cfw_cordio_dm_adv_legacy_configure_parameters(1U,0U,0);
                assert(params==1U);

                memset(storage,0,sizeof(storage));
                message->configure.advertising_type=2U;
                message->configure.peer_address_type=3U;
                memcpy(message->configure.peer_address,peer,6U);
                open_cfw_cordio_dm_adv_legacy_action_configure(message);
                assert(params==2U&&open_cfw_cordio_dm_adv_legacy_type==2U);
                open_cfw_cordio_dm_adv_control_block.advertising_type[0]=1U;
                open_cfw_cordio_dm_adv_legacy_action_configure(message);
                assert(params==2U);
                open_cfw_cordio_dm_adv_control_block.advertising_type[0]=0U;

                memset(storage,0,sizeof(storage));
                message->set_data.length=3U;
                memcpy(message->set_data.data,peer,3U);
                open_cfw_cordio_dm_adv_legacy_action_set_data(message);
                assert(adv_data==1U&&data_len==3U&&memcmp(copied,peer,3U)==0);
                message->set_data.location=1U;
                open_cfw_cordio_dm_adv_legacy_action_set_data(message);
                assert(scan_data==1U);
                message->set_data.length=32U;
                open_cfw_cordio_dm_adv_legacy_action_set_data(message);
                assert(scan_data==1U);

                memset(storage,0,sizeof(storage));
                message->start.number_of_sets=1U;
                message->start.duration[0]=123U;
                open_cfw_cordio_dm_adv_legacy_action_start(message);
                assert(enables==1U&&enabled==1U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==3U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_duration[0]==123U);
                open_cfw_cordio_dm_adv_legacy_type=0U;
                open_cfw_cordio_dm_adv_legacy_hci_handler(&hci);
                assert(timer_starts==1U&&timer_ms==123U);
                assert(private_events==1U&&last_event==12U&&last_parameter==0x21U);
                assert(callbacks==1U&&callback_event==0x21U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==1U);

                open_cfw_cordio_dm_adv_legacy_action_stop(message);
                assert(enables==2U&&enabled==0U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==5U);
                hci.event=53U; hci.status=0U;
                open_cfw_cordio_dm_adv_legacy_hci_handler(&hci);
                assert(timer_stops==1U&&private_events==2U&&last_event==13U);
                assert(callbacks==2U&&callback_event==0x22U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==0U);

                open_cfw_cordio_dm_adv_control_block.advertising_state[0]=5U;
                open_cfw_cordio_dm_adv_legacy_type=4U;
                hci.event=53U; hci.status=0U;
                open_cfw_cordio_dm_adv_legacy_hci_handler(&hci);
                assert(completions==1U&&complete_status==0x3CU);

                open_cfw_cordio_dm_adv_control_block.advertising_state[0]=0U;
                open_cfw_cordio_dm_adv_legacy_start_directed(1U,77U,2U,peer);
                assert(enabled==1U&&open_cfw_cordio_dm_adv_control_block.advertising_state[0]==2U);
                assert(memcmp(open_cfw_cordio_dm_adv_control_block.peer_address[0],peer,6U)==0);
                open_cfw_cordio_dm_adv_legacy_type=1U;
                open_cfw_cordio_dm_adv_legacy_stop_directed();
                assert(enabled==0U&&open_cfw_cordio_dm_adv_control_block.advertising_state[0]==4U);
                open_cfw_cordio_dm_adv_legacy_connected();
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==0U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_type[0]==0xFFU);
                open_cfw_cordio_dm_adv_legacy_connect_failed();

                open_cfw_cordio_dm_dev_adv_set_random_address_callback=123U;
                open_cfw_cordio_dm_adv_legacy_initialize();
                assert(locks==1U&&unlocks==1U&&initializes==1U);
                assert(open_cfw_cordio_dm_dev_adv_set_random_address_callback==0U);
                assert(open_cfw_cordio_dm_adv_mode_legacy()==1U);
                open_cfw_cordio_dm_adv_registered_interface=0;
                assert(open_cfw_cordio_dm_adv_mode_legacy()==0U);

                memset(storage,0,sizeof(storage));
                message->header.event=7U;
                open_cfw_cordio_dm_adv_control_block.advertising_state[0]=1U;
                open_cfw_cordio_dm_adv_legacy_message_handler(&message->header);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_state[0]==5U);
                open_cfw_cordio_dm_adv_legacy_message_handler(0);
                hci.event=1U;
                open_cfw_cordio_dm_adv_legacy_hci_handler(&hci);

                open_cfw_cordio_dm_adv_control_block.advertising_state[0]=1U;
                open_cfw_cordio_dm_adv_control_block.advertising_type[0]=0U;
                open_cfw_cordio_dm_adv_legacy_reset();
                assert(initializes==2U&&callback_event==0x22U);
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
                 "-o", str(executable)], check=True
            )
            subprocess.run([str(executable)], check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selectors = [
            "CONFIG_PARAMETERS", "ACTION_CONFIGURE", "ACTION_SET_DATA",
            "ACTION_START", "ACTION_STOP", "ACTION_REMOVE", "ACTION_CLEAR",
            "ACTION_SET_RANDOM", "ACTION_TIMEOUT", "RESET", "HCI_HANDLER",
            "MESSAGE_HANDLER", "START_DIRECTED", "STOP_DIRECTED", "CONNECTED",
            "CONNECT_FAILED", "INITIALIZE", "MODE",
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
                    command.append(
                        f"-DOPEN_CFW_DM_ADV_LEG_{selector}_ONLY=1"
                    )
                command += ["-DOPEN_CFW_DM_ADV_LEG_PRODUCTION=1", "-c",
                            str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

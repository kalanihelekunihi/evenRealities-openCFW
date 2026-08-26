import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_phy.c"


class CordioDmPhySourceTests(unittest.TestCase):
    def test_events_commands_initialization_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_dm_phy.h"

            struct open_cfw_cordio_dm_device_main_control
                open_cfw_cordio_dm_device_main_control;
            uintptr_t open_cfw_cordio_dm_device_function_interfaces[21];
            static struct open_cfw_cordio_dm_phy_connection connection;
            static struct open_cfw_cordio_dm_phy_event indication;
            static unsigned callbacks, lock_calls, unlock_calls;
            static unsigned lookup_handle_calls, lookup_id_calls;
            static unsigned read_calls, default_calls, set_calls, feature_calls;
            static uint16_t last_handle, last_options;
            static uint8_t last_all, last_tx, last_rx, lookup_enabled=1U;
            static uint64_t last_features;

            static void callback(void *raw) {
                callbacks++; memcpy(&indication,raw,sizeof(indication));
            }
            struct open_cfw_cordio_dm_phy_connection *
            open_cfw_cordio_dm_connection_control_by_handle(uint16_t handle) {
                lookup_handle_calls++; last_handle=handle;
                return lookup_enabled ? &connection : 0;
            }
            struct open_cfw_cordio_dm_phy_connection *
            open_cfw_cordio_dm_connection_control_by_id(uint8_t id) {
                lookup_id_calls++; assert(id==3U);
                return lookup_enabled ? &connection : 0;
            }
            void open_cfw_cordio_hci_read_phy(uint16_t handle) {
                read_calls++; last_handle=handle;
            }
            void open_cfw_cordio_hci_set_default_phy(uint8_t a,uint8_t t,uint8_t r) {
                default_calls++; last_all=a; last_tx=t; last_rx=r;
            }
            void open_cfw_cordio_hci_set_phy(uint16_t h,uint8_t a,uint8_t t,
                    uint8_t r,uint16_t o) {
                set_calls++;last_handle=h;last_all=a;last_tx=t;last_rx=r;last_options=o;
            }
            void open_cfw_cordio_hci_set_supported_features(uint64_t m,uint8_t e) {
                feature_calls++;last_features=m;assert(e==1U);
            }
            void open_cfw_cordio_wsf_task_lock(void) { lock_calls++; }
            void open_cfw_cordio_wsf_task_unlock(void) { unlock_calls++; }

            int main(void) {
                struct open_cfw_cordio_dm_phy_event event={0};
                connection.handle=0x123U;connection.connection_id=3U;
                open_cfw_cordio_dm_phy_host_callback=callback;
                open_cfw_cordio_dm_phy_host_interface=(uintptr_t)0x12345679U;

                event.header.parameter=0x123U;event.header.event=0x29U;
                event.status=7U;event.transmit_phy=2U;event.receive_phy=3U;
                open_cfw_cordio_dm_phy_hci_handler(&event);
                assert(lookup_handle_calls==1U&&callbacks==1U);
                assert(indication.header.event==0x44U&&indication.header.parameter==3U);
                assert(indication.header.status==7U&&indication.status==7U);
                assert(indication.handle==0x123U&&indication.transmit_phy==2U);
                assert(indication.receive_phy==3U);

                event.header.event=0x2AU;event.status=4U;
                open_cfw_cordio_dm_phy_hci_handler(&event);
                assert(callbacks==2U&&indication.header.event==0x45U);
                assert(indication.header.parameter==0U&&indication.status==4U);
                event.header.event=0x2BU;event.status=5U;
                open_cfw_cordio_dm_phy_hci_handler(&event);
                assert(callbacks==3U&&indication.header.event==0x46U);
                event.header.event=0x7FU;
                open_cfw_cordio_dm_phy_hci_handler(&event);
                assert(callbacks==3U);
                lookup_enabled=0U;event.header.event=0x29U;
                open_cfw_cordio_dm_phy_hci_handler(&event);
                open_cfw_cordio_dm_phy_hci_handler(0);
                open_cfw_cordio_dm_phy_action_read(0,&event);
                open_cfw_cordio_dm_phy_action_default(0);
                open_cfw_cordio_dm_phy_action_update(&connection,0);
                assert(callbacks==3U);

                lookup_enabled=1U;open_cfw_cordio_dm_phy_read(3U);
                assert(read_calls==1U&&last_handle==0x123U);
                open_cfw_cordio_dm_phy_set_default(1U,2U,3U);
                assert(default_calls==1U&&last_all==1U&&last_tx==2U&&last_rx==3U);
                open_cfw_cordio_dm_phy_set(3U,4U,5U,6U,0x789U);
                assert(set_calls==1U&&last_handle==0x123U&&last_all==4U);
                assert(last_tx==5U&&last_rx==6U&&last_options==0x789U);
                lookup_enabled=0U;open_cfw_cordio_dm_phy_read(3U);
                open_cfw_cordio_dm_phy_set(3U,0U,0U,0U,0U);
                assert(read_calls==1U&&set_calls==1U);
                assert(lock_calls==4U&&unlock_calls==4U&&lookup_id_calls==4U);

                open_cfw_cordio_dm_phy_initialize();
                assert(lock_calls==5U&&unlock_calls==5U&&feature_calls==1U);
                assert(last_features==0x900U);
                assert(open_cfw_cordio_dm_device_function_interfaces[9]==
                    open_cfw_cordio_dm_phy_host_interface);
                open_cfw_cordio_dm_phy_host_callback=0;
                open_cfw_cordio_dm_phy_action_default(&event);
                assert(callbacks==3U);
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
        selectors = ["HCI", "ACTION_READ", "ACTION_DEFAULT", "ACTION_UPDATE",
                     "READ", "SET_DEFAULT", "SET", "INIT"]
        with tempfile.TemporaryDirectory() as directory:
            for selector in [None, *selectors]:
                command = ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                           "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                           "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                           "-I", str(SOURCE_DIR)]
                if selector:
                    command.append(f"-DOPEN_CFW_DM_PHY_{selector}_ONLY=1")
                command += ["-DOPEN_CFW_DM_PHY_PRODUCTION=1", "-c", str(SOURCE),
                            "-o", str(Path(directory)/f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

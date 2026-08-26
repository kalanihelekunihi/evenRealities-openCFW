import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_conn_sm.c"


class CordioDmConnectionStateMachineSourceTests(unittest.TestCase):
    def test_all_transitions_dispatch_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_dm_conn_sm.h"

            uintptr_t open_cfw_cordio_dm_connection_action_sets[3];
            static uintptr_t main_actions[6];
            static uintptr_t master_actions[2];
            static uintptr_t slave_actions[4];
            static unsigned calls[3][6];
            static unsigned none_calls;
            static uint8_t expected_state;

            static void action_main(
                struct open_cfw_cordio_dm_connection_control_block *control,
                struct open_cfw_cordio_dm_connection_message *message) {
                assert(control->state == expected_state); (void)message;
                calls[0][0]++;
            }
            static void action_master(
                struct open_cfw_cordio_dm_connection_control_block *control,
                struct open_cfw_cordio_dm_connection_message *message) {
                assert(control->state == expected_state); (void)message;
                calls[1][0]++;
            }
            static void action_slave(
                struct open_cfw_cordio_dm_connection_control_block *control,
                struct open_cfw_cordio_dm_connection_message *message) {
                assert(control->state == expected_state); (void)message;
                calls[2][0]++;
            }
            void open_cfw_cordio_dm_connection_action_none(
                struct open_cfw_cordio_dm_connection_control_block *control,
                struct open_cfw_cordio_dm_connection_message *message) {
                (void)control; (void)message; none_calls++;
            }

            int main(void) {
                static const uint8_t expected[5][8][2] = {
                    {{1,0x10},{0,0},{2,0x20},{0,0},{3,0x22},{0,0},{0,0},{0,0}},
                    {{1,0},{4,0x11},{1,0},{0,3},{3,2},{0,3},{1,0},{1,0}},
                    {{2,0},{0,0x21},{2,0},{0,0x23},{3,0x22},{0,0x23},{2,0},{2,0}},
                    {{3,0},{4,1},{3,0},{3,0},{3,0},{0,4},{3,5},{3,0}},
                    {{4,0},{4,0},{4,0},{0,4},{4,1},{0,4},{4,0},{4,0}}
                };
                struct open_cfw_cordio_dm_connection_control_block control;
                struct open_cfw_cordio_dm_connection_message message = {0};
                unsigned state, event, set, id;

                for (id=0; id<6; ++id) main_actions[id]=(uintptr_t)action_main;
                for (id=0; id<2; ++id) master_actions[id]=(uintptr_t)action_master;
                for (id=0; id<4; ++id) slave_actions[id]=(uintptr_t)action_slave;
                open_cfw_cordio_dm_connection_action_sets[0]=(uintptr_t)main_actions;
                open_cfw_cordio_dm_connection_action_sets[1]=(uintptr_t)master_actions;
                open_cfw_cordio_dm_connection_action_sets[2]=(uintptr_t)slave_actions;

                for (state=0; state<5; ++state) for (event=0; event<8; ++event) {
                    uint8_t action=expected[state][event][1];
                    memset(&control,0,sizeof(control)); control.state=(uint8_t)state;
                    message.event=(uint8_t)(event | 0xA0U);
                    expected_state=expected[state][event][0];
                    open_cfw_cordio_dm_connection_state_machine_execute(&control,&message);
                    assert(control.state==expected_state);
                    set=action>>4; id=action&15U;
                    assert(calls[set][0]>0U);
                }

                memset(&control,0,sizeof(control)); control.state=5U;
                open_cfw_cordio_dm_connection_state_machine_execute(&control,&message);
                assert(none_calls==1U&&control.state==5U);
                open_cfw_cordio_dm_connection_action_sets[1]=0U;
                control.state=0U; message.event=0U;
                open_cfw_cordio_dm_connection_state_machine_execute(&control,&message);
                assert(none_calls==2U&&control.state==1U);
                open_cfw_cordio_dm_connection_action_sets[1]=(uintptr_t)master_actions;
                master_actions[0]=0U; control.state=0U;
                open_cfw_cordio_dm_connection_state_machine_execute(&control,&message);
                assert(none_calls==3U&&control.state==1U);
                open_cfw_cordio_dm_connection_state_machine_execute(0,&message);
                open_cfw_cordio_dm_connection_state_machine_execute(&control,0);
                assert(none_calls==3U);
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
        with tempfile.TemporaryDirectory() as directory:
            for isolated in (False, True):
                command = [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR),
                ]
                if isolated:
                    command.append("-DOPEN_CFW_DM_CONN_SM_EXECUTE_ONLY=1")
                command += ["-DOPEN_CFW_DM_CONN_SM_PRODUCTION=1", "-c",
                            str(SOURCE), "-o",
                            str(Path(directory) / f"{isolated}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

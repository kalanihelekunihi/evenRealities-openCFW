#!/usr/bin/env python3
"""Exercise the recovered G2 Cordio master application-framework ABI."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_app_master.c"


class RuntimeCordioAppMasterTests(unittest.TestCase):
    def test_host_master_resolution_connection_and_security(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_app_master.c"

            volatile uint8_t open_cfw_app_master_runtime_state[0xA0];
            volatile uint8_t open_cfw_app_master_connection_state[3U*0x30U];
            volatile uint8_t *open_cfw_app_master_security_config;
            static unsigned opens, finds, resolved, security_calls;
            static uint8_t open_result=2U, sec_level, last_client, last_phys;
            static uint8_t last_type, last_security_connection;
            static uint16_t last_resolve_parameter;
            static uint32_t last_find_handle;
            static int record_in_use;

            static uint32_t read32(const volatile uint8_t *p) {
                return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
                    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
            }
            uint8_t open_cfw_cordio_dm_connection_open(
                uint8_t client, uint8_t phys, uint8_t type, uint8_t *address
            ) {
                assert(address[0]==0xA5U);last_client=client;last_phys=phys;
                last_type=type;opens++;return open_result;
            }
            int open_cfw_app_database_record_in_use(uint32_t handle) {
                assert(handle==0x11223344U);return record_in_use;
            }
            uint32_t open_cfw_app_database_find_by_address(
                uint8_t type, uint8_t *address
            ) {
                assert(type==2U&&address[0]==0xA5U);finds++;
                last_find_handle=0x55667788U;return last_find_handle;
            }
            int open_cfw_mram_handle_resolved_address(
                const volatile uint8_t *device, uint16_t parameter
            ) {
                assert(device==open_cfw_app_master_runtime_state+30U);
                last_resolve_parameter=parameter;resolved++;return 1;
            }
            uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t id) {
                assert(id==1U);return sec_level;
            }
            void open_cfw_app_master_initiate_security_internal(
                uint8_t id, uint8_t pair, volatile uint8_t *connection
            ) {
                assert(pair==1U&&connection==open_cfw_app_master_connection_state);
                last_security_connection=id;security_calls++;
            }

            int main(void) {
                uint8_t address[6]={0xA5U};uint8_t event[8]={0};
                uint8_t security_config[8]={0};
                memset((void *)open_cfw_app_master_runtime_state,0,
                       sizeof(open_cfw_app_master_runtime_state));
                memset((void *)open_cfw_app_master_connection_state,0,
                       sizeof(open_cfw_app_master_connection_state));
                open_cfw_app_master_scan_stop_event(event);
                event[0]=0x34U;event[1]=0x12U;event[3]=0U;
                open_cfw_app_master_runtime_state[0x97]=2U;
                open_cfw_app_master_runtime_state[0x9C]=1U;
                open_cfw_app_master_resolved_address_event(event);
                assert(resolved==1U&&last_resolve_parameter==0x1234U);
                assert(open_cfw_app_master_runtime_state[0x9C]==0U);
                open_cfw_app_master_resolved_address_event(event);
                assert(resolved==1U);
                open_cfw_app_master_runtime_state[0x9C]=1U;event[3]=5U;
                open_cfw_app_master_resolved_address_event(event);
                assert(resolved==1U&&open_cfw_app_master_runtime_state[0x9C]==0U);

                record_in_use=1;
                assert(open_cfw_app_master_connection_open(
                    3U,2U,address,0x11223344U)==2U);
                assert(opens==1U&&finds==0U&&last_client==3U);
                assert(last_phys==3U&&last_type==2U);
                assert(open_cfw_app_master_connection_state[0x34]==2U);
                assert(read32(open_cfw_app_master_connection_state+0x30)==0x11223344U);
                record_in_use=0;open_result=1U;
                assert(open_cfw_app_master_connection_open(
                    1U,2U,address,0x11223344U)==1U);
                assert(finds==1U&&read32(open_cfw_app_master_connection_state)==0x55667788U);
                open_result=0U;
                assert(open_cfw_app_master_connection_open(1U,2U,address,0U)==0U);
                assert(finds==1U);
                assert(open_cfw_app_master_connection_open(1U,2U,0,0U)==0U);

                open_cfw_app_master_security_config=security_config;
                sec_level=0U;
                open_cfw_app_master_security_request(1U);
                assert(security_calls==1U&&last_security_connection==1U);
                open_cfw_app_master_connection_state[8]=1U;
                open_cfw_app_master_security_request(1U);
                assert(security_calls==1U);
                open_cfw_app_master_connection_state[8]=0U;security_config[4]=1U;
                open_cfw_app_master_security_request(1U);
                assert(security_calls==1U);
                security_config[4]=0U;sec_level=2U;
                open_cfw_app_master_security_request(1U);
                assert(security_calls==1U);
                open_cfw_app_master_security_request(0U);
                open_cfw_app_master_security_request(4U);
                assert(security_calls==1U);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "cordio-app-master-test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(harness_path), "-o", str(executable)],
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        selectors = [
            "SCAN_STOP", "RESOLVED_ADDRESS", "CONNECTION_OPEN",
            "SECURITY_REQUEST",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run(
                    ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                     "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                     "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                     "-Wall", "-Wextra", "-Werror",
                     "-DOPEN_CFW_CORDIO_APP_MASTER_PRODUCTION=1",
                     f"-DOPEN_CFW_CORDIO_APP_MASTER_{selector}_ONLY=1",
                     "-c", str(SOURCE), "-o",
                     str(Path(directory) / f"{selector}.o")],
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()

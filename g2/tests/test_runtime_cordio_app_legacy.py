#!/usr/bin/env python3
"""Exercise the recovered G2 Cordio legacy application-framework ABI."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_app_legacy.c"


class RuntimeCordioAppLegacyTests(unittest.TestCase):
    def test_host_master_slave_and_g2_retry_policy(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_app_legacy.c"

            volatile uint8_t open_cfw_app_master_state[0xA0];
            volatile uint8_t open_cfw_app_slave_state[0x80];
            volatile uint8_t *open_cfw_app_adv_config;
            volatile uint8_t *open_cfw_app_master_config;
            volatile uint8_t open_cfw_app_retry_flag;
            volatile uint8_t open_cfw_app_retry_timer[16];
            volatile uint8_t open_cfw_app_handler_id;

            static unsigned scan_sets, scan_starts, scan_stops, conn_opens;
            static unsigned adv_starts, slave_starts, adv_stops, data_sets;
            static unsigned type_sets, timer_starts, timer_stops;
            static uint8_t extended_mode, last_mode, last_scan_type;
            static uint8_t last_location, last_length, last_adv_type;
            static uint16_t last_duration, last_interval;
            static uint32_t last_timer_ms;
            static void *last_database;

            static uint16_t read16(const volatile uint8_t *p) {
                return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
            }
            static void write16(volatile uint8_t *p, uint16_t v) {
                p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8);
            }
            static uint32_t read32(const volatile uint8_t *p) {
                return (uint32_t)p[0] | ((uint32_t)p[1]<<8) |
                    ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
            }

            void open_cfw_cordio_dm_scan_set_interval(
                uint8_t phys, uint16_t *interval, uint16_t *window
            ) {
                assert(phys==1U); assert(*interval==0x1234U);
                assert(*window==0x5678U); scan_sets++;
            }
            void open_cfw_cordio_dm_scan_start(
                uint8_t phys, uint8_t mode, const uint8_t *type,
                uint8_t filter, uint16_t duration, uint16_t period
            ) {
                assert(phys==1U&&filter==1U&&period==0U);
                last_mode=mode;last_scan_type=*type;last_duration=duration;
                scan_starts++;
            }
            void open_cfw_cordio_dm_scan_stop(void) { scan_stops++; }
            uint8_t open_cfw_app_connection_open_internal(
                uint8_t phys, uint8_t type, uint8_t *address, void *database
            ) {
                assert(phys==1U&&type==2U&&address[0]==0xA5U);
                last_database=database;conn_opens++;return 3U;
            }
            uint8_t open_cfw_cordio_dm_advertising_extended_mode(uint8_t h) {
                assert(h==0U);return extended_mode;
            }
            void open_cfw_app_advertising_start_internal(
                uint8_t count, uint8_t *handles, uint16_t *interval,
                uint16_t *duration, uint8_t *events, uint8_t configure
            ) {
                assert(count==1U&&handles[0]==0U&&events[0]==0U&&configure==1U);
                last_interval=*interval;last_duration=*duration;adv_starts++;
            }
            void open_cfw_app_slave_advertising_start_internal(
                uint8_t count, uint8_t *handles, uint16_t *interval,
                uint16_t *duration, uint8_t *events, uint8_t configure,
                uint8_t mode
            ) {
                assert(count==1U&&handles[0]==0U&&events[0]==0U&&configure==1U);
                last_interval=*interval;last_duration=*duration;last_mode=mode;
                slave_starts++;
            }
            void open_cfw_app_advertising_stop_internal(
                uint8_t count, uint8_t *handles
            ) { assert(count==1U&&handles[0]==0U);adv_stops++; }
            void open_cfw_app_advertising_set_data_internal(
                uint8_t handle, uint8_t location, uint16_t length,
                uint8_t *data, uint16_t buffer, uint16_t maximum
            ) {
                assert(handle==0U&&data[0]==0x5AU&&buffer==31U&&maximum==31U);
                last_location=location;last_length=(uint8_t)length;data_sets++;
            }
            void open_cfw_app_advertising_set_type_internal(
                uint8_t handle, uint8_t type, uint16_t interval,
                uint16_t duration, uint8_t events, uint8_t configure
            ) {
                assert(handle==0U&&events==0U&&configure==1U);
                last_adv_type=type;last_interval=interval;last_duration=duration;
                type_sets++;
            }
            void open_cfw_cordio_wsf_timer_start_ms(void *timer, uint32_t ms) {
                assert(timer==(void *)open_cfw_app_retry_timer);
                last_timer_ms=ms;timer_starts++;
            }
            void open_cfw_cordio_wsf_timer_stop(void *timer) {
                assert(timer==(void *)open_cfw_app_retry_timer);timer_stops++;
            }

            int main(void) {
                uint8_t master_cfg[4], adv_cfg[12], address[6]={0xA5U};
                uint8_t data[40]={0x5AU};
                uint8_t event[8]={0};
                memset((void *)open_cfw_app_master_state,0,sizeof(open_cfw_app_master_state));
                memset((void *)open_cfw_app_slave_state,0,sizeof(open_cfw_app_slave_state));
                memset((void *)open_cfw_app_retry_timer,0,sizeof(open_cfw_app_retry_timer));
                write16(master_cfg,0x1234U);write16(master_cfg+2,0x5678U);
                write16(adv_cfg+0,100U);write16(adv_cfg+2,200U);
                write16(adv_cfg+4,300U);write16(adv_cfg+6,160U);
                write16(adv_cfg+8,320U);write16(adv_cfg+10,480U);
                open_cfw_app_master_config=master_cfg;open_cfw_app_adv_config=adv_cfg;
                open_cfw_app_handler_id=9U;

                open_cfw_app_master_state[0x9D]=0xFFU;
                assert(open_cfw_app_master_scan_mode()==1);
                assert(open_cfw_app_master_state[0x9D]==0U);
                open_cfw_app_scan_start(4U,1U,750U);
                assert(scan_sets==1U&&scan_starts==1U&&last_mode==4U);
                assert(last_scan_type==1U&&last_duration==750U);
                open_cfw_app_master_state[0x9C]=1U;open_cfw_app_scan_stop();
                assert(scan_stops==1U&&open_cfw_app_master_state[0x9C]==0U);
                assert(open_cfw_app_connection_open(2U,address,(void *)0x1234U)==3U);
                assert(conn_opens==1U&&last_database==(void *)0x1234U);
                open_cfw_app_master_state[0x9D]=1U;
                open_cfw_app_scan_start(1U,0U,1U);open_cfw_app_scan_stop();
                assert(open_cfw_app_connection_open(2U,address,0)==0U);
                assert(scan_starts==1U&&scan_stops==1U&&conn_opens==1U);

                assert(open_cfw_app_slave_legacy_advertising_mode()==1);
                assert(read32(open_cfw_app_slave_state+0x78)==0x004B2AFFU);
                assert(read32(open_cfw_app_slave_state+0x7C)==0x004B2B91U);
                open_cfw_app_advertising_set_data(2U,40U,data);
                assert(data_sets==1U&&last_location==2U&&last_length==31U);
                open_cfw_app_advertising_start(7U);
                assert(slave_starts==1U&&last_mode==7U);
                assert(last_interval==160U&&last_duration==100U);
                open_cfw_app_advertising_stop();assert(adv_stops==1U);
                open_cfw_app_advertising_set_type(4U);
                assert(type_sets==1U&&last_adv_type==4U);
                assert(last_interval==160U&&last_duration==100U);

                open_cfw_app_slave_state[0x57]=1U;extended_mode=0U;
                open_cfw_app_slave_legacy_advertising_start();
                assert(adv_starts==1U&&last_interval==320U&&last_duration==200U);
                open_cfw_app_slave_state[0x57]=2U;write16(adv_cfg+10,0U);
                open_cfw_app_slave_legacy_advertising_start();
                assert(open_cfw_app_slave_state[0x57]==3U&&adv_starts==1U);
                write16(adv_cfg+10,480U);open_cfw_app_slave_state[0x57]=2U;
                extended_mode=1U;open_cfw_app_retry_flag=0U;
                open_cfw_app_slave_legacy_advertising_start();
                assert(open_cfw_app_retry_flag==1U&&timer_starts==1U);
                assert(last_timer_ms==200U&&read16(open_cfw_app_retry_timer+8)==0U);
                assert(open_cfw_app_retry_timer[10]==0x22U);
                assert(open_cfw_app_retry_timer[12]==9U);

                event[2]=0x22U;
                open_cfw_app_slave_legacy_advertising_stop(event);
                assert(timer_starts==2U&&last_timer_ms==100U);
                extended_mode=0U;
                open_cfw_app_slave_legacy_advertising_stop(event);
                assert(open_cfw_app_retry_flag==0U&&timer_stops==1U);
                assert(open_cfw_app_slave_state[0x57]==3U);

                open_cfw_app_slave_state[0x57]=2U;
                open_cfw_app_slave_state[0x5B]=1U;
                open_cfw_app_slave_legacy_advertising_stop(event);
                assert(open_cfw_app_slave_state[0x5B]==0U);
                assert(open_cfw_app_slave_state[0x57]==0U&&adv_starts==2U);
                event[2]=0x48U;event[4]=0U;
                open_cfw_app_slave_state[0x57]=1U;
                open_cfw_app_slave_legacy_advertising_stop(event);
                assert(open_cfw_app_slave_state[0x57]==1U);

                event[2]=0x28U;open_cfw_app_slave_state[0x75]=1U;
                open_cfw_app_slave_legacy_advertising_restart(event);
                assert(open_cfw_app_slave_state[0x75]==0U);
                open_cfw_app_slave_state[0x57]=3U;
                open_cfw_app_slave_legacy_advertising_restart(event);
                assert(open_cfw_app_slave_state[0x57]==0U&&adv_starts==3U);
                event[2]=0x27U;open_cfw_app_slave_state[0x75]=1U;
                open_cfw_app_slave_legacy_advertising_restart(event);
                assert(open_cfw_app_slave_state[0x75]==0U);

                open_cfw_app_slave_state[0x78]=0xAAU;
                assert(open_cfw_app_slave_legacy_advertising_mode()==0);
                open_cfw_app_advertising_set_data(0U,1U,data);
                assert(data_sets==1U);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "cordio-app-legacy-test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(harness_path), "-o", str(executable)],
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        selectors = [
            "MASTER_MODE", "SCAN_START", "SCAN_STOP", "CONNECTION_OPEN",
            "ADV_START_INTERNAL", "ADV_TYPE_CHANGED", "ADV_NEXT_STATE",
            "ADV_STOP_CALLBACK", "ADV_RESTART_CALLBACK", "ADV_MODE",
            "ADV_SET_DATA", "ADV_START", "ADV_STOP", "ADV_SET_TYPE",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run(
                    ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                     "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                     "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                     "-Wall", "-Wextra", "-Werror",
                     "-DOPEN_CFW_CORDIO_APP_LEGACY_PRODUCTION=1",
                     f"-DOPEN_CFW_CORDIO_APP_LEGACY_{selector}_ONLY=1",
                     "-c", str(SOURCE), "-o",
                     str(Path(directory) / f"{selector}.o")],
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Exercise the recovered G2 Cordio slave application-framework ABI."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_app_slave.c"


class RuntimeCordioAppSlaveTests(unittest.TestCase):
    def test_host_resolution_restore_and_dispatch(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_app_slave.c"

            volatile uint8_t open_cfw_app_slave_runtime_state[0x80];
            volatile uint8_t open_cfw_app_slave_connection_state[3U*0x30U];
            volatile uint8_t *open_cfw_app_slave_security_config;
            volatile uint8_t open_cfw_app_slave_database_ready;
            open_cfw_app_slave_callback_t open_cfw_app_slave_callback;
            static unsigned syncs, nexts, resolves, ccc, csf_get, csf_open;
            static unsigned service_changed, csrk, counters, ltk;
            static unsigned reset_calls, open_calls, close_calls, remote_calls;
            static unsigned reset_ext, adv_reset, callbacks;
            static uint32_t records[4], record_index, last_counter;
            static uint8_t irk1[23], irk2[23], csrk_key[23], peer[6], csf[4];
            static uint16_t ccc_table[4];

            static uint32_t read32(const volatile uint8_t *p) {
                return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
                    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
            }
            void open_cfw_mram_sync_records(void){syncs++;record_index=0U;}
            uint32_t open_cfw_app_database_get_next_record(uint32_t previous){
                nexts++;
                if(previous==0U){record_index=0U;}
                else {while(records[record_index]&&records[record_index]!=previous)record_index++;
                      if(records[record_index])record_index++;}
                return records[record_index];
            }
            uint8_t *open_cfw_app_slave_database_get_key(
                uint32_t record,uint8_t type,uint8_t *length
            ){
                assert(length==0);
                if(type==4U){if(record==0x1000U)return irk1;if(record==0x2000U)return irk2;}
                if(type==8U&&record==0x2000U)return csrk_key;
                return 0;
            }
            uint8_t *open_cfw_cordio_dm_connection_peer_address(uint8_t id){assert(id==1U);return peer;}
            void open_cfw_cordio_dm_priv_resolve_address(uint8_t *a,uint8_t *k,uint16_t p){
                assert(a==peer&&(k==irk1||k==irk2)&&p==1U);resolves++;
            }
            uint16_t *open_cfw_app_slave_test_ccc_table(uint32_t r){assert(r==0x2000U);return ccc_table;}
            uint32_t open_cfw_app_slave_test_sign_counter(uint32_t r){assert(r==0x2000U);return 0x12345678U;}
            void open_cfw_cordio_atts_ccc_initialize_table(uint8_t id,uint16_t *t){assert(id==1U&&t==ccc_table);ccc++;}
            void open_cfw_app_database_get_csf_record(uint32_t r,uint8_t *state,uint8_t **out){
                assert(r==0x2000U);*state=3U;*out=csf;csf_get++;
            }
            void open_cfw_cordio_atts_csf_connection_open(uint8_t id,uint8_t state,uint8_t *p){assert(id==1U&&state==3U&&p==csf);csf_open++;}
            void open_cfw_cordio_gatt_send_service_changed_indication(uint8_t id,uint16_t s,uint16_t e){assert(id==1U&&s==1U&&e==0xffffU);service_changed++;}
            void open_cfw_cordio_atts_set_csrk(uint8_t id,uint8_t *k,uint8_t local){assert(id==1U&&k==csrk_key&&local==0U);csrk++;}
            void open_cfw_cordio_atts_set_sign_counter(uint8_t id,uint32_t v){assert(id==1U);last_counter=v;counters++;}
            void open_cfw_app_slave_security_respond_ltk_internal(volatile uint8_t *c){assert(c==open_cfw_app_slave_connection_state);ltk++;}
            void open_cfw_app_slave_reset_event_internal(const void *m,volatile uint8_t *c){(void)m;(void)c;reset_calls++;}
            void open_cfw_app_slave_connection_open_event_internal(const void *m,volatile uint8_t *c){(void)m;assert(c==open_cfw_app_slave_connection_state);open_calls++;}
            void open_cfw_app_slave_connection_close_event_internal(const void *m,volatile uint8_t *c){(void)m;assert(c==open_cfw_app_slave_connection_state);close_calls++;}
            void open_cfw_app_slave_remote_parameter_event_internal(const void *m,volatile uint8_t *c){(void)m;assert(c==open_cfw_app_slave_connection_state);remote_calls++;}
            void open_cfw_app_slave_reset_extension_internal(uint8_t v){assert(v==0U);reset_ext++;}
            void open_cfw_app_slave_advertising_reset_internal(void){adv_reset++;}
            static void callback(void *m){assert(m!=0);callbacks++;}

            int main(void){
                uint8_t event[12]={1U,0U,0U,0U};uint8_t sec[8]={0};
                memset((void*)open_cfw_app_slave_runtime_state,0,sizeof(open_cfw_app_slave_runtime_state));
                memset((void*)open_cfw_app_slave_connection_state,0,sizeof(open_cfw_app_slave_connection_state));
                open_cfw_app_slave_connection_state[4]=1U;
                records[0]=0x1000U;records[1]=0x2000U;records[2]=0U;
                open_cfw_app_slave_resolve_address(event);
                assert(syncs==1U&&resolves==1U&&read32(open_cfw_app_slave_runtime_state+0x70)==0x1000U);
                assert(open_cfw_app_slave_runtime_state[0x74]==1U);
                open_cfw_app_slave_resolve_address(event);assert(syncs==1U);
                event[3]=5U;
                open_cfw_app_slave_resolved_address_event(event,open_cfw_app_slave_connection_state);
                assert(resolves==2U&&read32(open_cfw_app_slave_runtime_state+0x70)==0x2000U);
                event[3]=0U;open_cfw_app_slave_runtime_state[0x6c]=1U;
                open_cfw_app_slave_resolved_address_event(event,open_cfw_app_slave_connection_state);
                assert(open_cfw_app_slave_database_ready==1U);
                assert(read32(open_cfw_app_slave_connection_state)==0x2000U);
                assert(ccc==1U&&csf_get==1U&&csf_open==1U&&service_changed==1U);
                assert(csrk==1U&&counters==1U&&last_counter==0x12345678U);
                assert(ltk==1U&&open_cfw_app_slave_runtime_state[0x6c]==0U);
                assert(open_cfw_app_slave_runtime_state[0x74]==0U);

                open_cfw_app_slave_callback=callback;
                event[2]=0x20U;open_cfw_app_slave_process_dm_message(event);assert(reset_calls==1U);
                event[2]=0x27U;open_cfw_app_slave_process_dm_message(event);assert(open_calls==1U);
                event[2]=0x28U;open_cfw_app_slave_process_dm_message(event);assert(close_calls==1U);
                event[2]=0x40U;open_cfw_app_slave_process_dm_message(event);assert(remote_calls==1U);
                event[2]=0x79U;open_cfw_app_slave_process_dm_message(event);assert(reset_ext==1U&&adv_reset==1U);
                event[2]=0x22U;open_cfw_app_slave_process_dm_message(event);assert(callbacks==1U);
                event[2]=0x41U;open_cfw_app_slave_process_dm_message(event);assert(callbacks==1U);
                event[0]=0U;event[2]=0x27U;open_cfw_app_slave_process_dm_message(event);assert(open_calls==1U);
                open_cfw_app_slave_security_config=sec;sec[4]=1U;
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary=Path(directory);harness_path=temporary/"harness.c";exe=temporary/"test"
            harness_path.write_text(harness)
            subprocess.run(["cc","-std=c11","-O2","-Wall","-Wextra","-Werror","-I",str(SOURCE_DIR),str(harness_path),"-o",str(exe)],check=True)
            subprocess.run([str(exe)],check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        for selector in ("RESOLVE_ADDRESS","RESOLVED_EVENT","PROCESS_DM"):
            with tempfile.TemporaryDirectory() as directory:
                subprocess.run(["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-std=c11","-O2","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION=1",f"-DOPEN_CFW_CORDIO_APP_SLAVE_{selector}_ONLY=1","-c",str(SOURCE),"-o",str(Path(directory)/f"{selector}.o")],check=True)


if __name__ == "__main__":
    unittest.main()

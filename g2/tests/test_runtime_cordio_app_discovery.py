#!/usr/bin/env python3
"""Exercise the recovered G2 Cordio application discovery state machine."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_app_discovery.c"


class RuntimeCordioAppDiscoveryTests(unittest.TestCase):
    def test_host_discovery_lifecycle_and_failure_paths(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_app_discovery.c"

            volatile open_cfw_app_disc_control_t open_cfw_app_disc_control[3];
            open_cfw_app_disc_callback_t open_cfw_app_disc_callback;
            uint32_t open_cfw_app_disc_connection_database[3];
            static uint8_t record_hash[16], new_hash[16], peer_address[6];
            static uint16_t record_handles[4]={11U,22U,33U,44U};
            static uint8_t record_status=8U, allocation[20];
            static unsigned notifications, new_records, set_hash, set_cache;
            static unsigned set_status, set_handles, idle_calls, allocs, frees;
            static unsigned svc_cmpl, char_start, char_cmpl, cfg_cmpl;
            static unsigned discover_calls, cfg_start_calls, read_hash_calls;
            static unsigned prepare_service, prepare_config;
            static uint8_t last_notification, service_result, char_result;
            static uint8_t config_result, security_level, last_idle;

            static void callback(uint8_t connection,uint8_t status){
                assert(connection==1U);last_notification=status;notifications++;
            }
            uint32_t open_cfw_app_disc_database_handle(uint8_t id){assert(id==1U);return open_cfw_app_disc_connection_database[0];}
            uint32_t open_cfw_app_disc_database_new_record(uint8_t type,uint8_t *addr,int master){assert(type==2U&&addr==peer_address&&master);new_records++;return 0x1000U;}
            uint8_t open_cfw_cordio_dm_connection_role(uint8_t id){assert(id==1U);return 0U;}
            uint8_t *open_cfw_cordio_dm_connection_peer_address(uint8_t id){assert(id==1U);return peer_address;}
            uint8_t open_cfw_cordio_dm_connection_peer_address_type(uint8_t id){assert(id==1U);return 2U;}
            void open_cfw_app_disc_database_set_peer_hash(uint32_t h,uint8_t *p){assert(h==0x1000U&&p&&p[0]==new_hash[0]);memcpy(record_hash,p,16U);set_hash++;}
            void open_cfw_app_disc_database_set_cache_by_hash(uint32_t h,uint8_t v){assert(h==0x1000U&&v==1U);set_cache++;}
            void open_cfw_app_disc_database_set_status(uint32_t h,uint8_t v){assert(h==0x1000U);record_status=v;set_status++;}
            void open_cfw_app_disc_database_set_handle_list(uint32_t h,uint16_t *p){assert(h==0x1000U);(void)p;set_handles++;}
            int open_cfw_app_check_bonded(uint8_t id){assert(id==1U);return 1;}
            void open_cfw_cordio_dm_connection_set_idle(uint8_t id,uint8_t client,uint8_t state){assert(id==1U&&client==8U);last_idle=state;idle_calls++;}
            void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint32_t n){assert(n==20U);allocs++;memset(allocation,0,sizeof(allocation));return allocation;}
            void open_cfw_cordio_wsf_buffer_free_candidate(void *p){assert(p==allocation);frees++;}
            uint8_t open_cfw_cordio_attc_discovery_service_complete(void *p,open_cfw_app_disc_event_t *m){assert(p==allocation&&m);svc_cmpl++;return service_result;}
            void open_cfw_cordio_attc_discovery_characteristic_start(uint8_t id,void *p){assert(id==1U&&p==allocation);char_start++;}
            uint8_t open_cfw_cordio_attc_discovery_characteristic_complete(void *p,open_cfw_app_disc_event_t *m){assert(p==allocation&&m);char_cmpl++;return char_result;}
            uint8_t open_cfw_cordio_attc_discovery_configuration_complete(uint8_t id,void *p){assert(id==1U&&p==allocation);cfg_cmpl++;return config_result;}
            void open_cfw_cordio_attc_discover_service(uint8_t id,void *p,uint8_t len,uint8_t *uuid){assert(id==1U&&p==allocation&&len==2U&&uuid);discover_calls++;}
            uint8_t open_cfw_cordio_attc_start_configuration(uint8_t id,void *p){assert(id==1U&&p==allocation);cfg_start_calls++;return config_result;}
            void open_cfw_cordio_attc_read_by_type_request(uint8_t id,uint16_t s,uint16_t e,uint8_t len,uint8_t *uuid,uint8_t cont){assert(id==1U&&s==1U&&e==0xffffU&&len==2U&&uuid[0]==0x2aU&&uuid[1]==0x2bU&&cont==0U);read_hash_calls++;}
            uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t id){assert(id==1U);return security_level;}
            uint8_t *open_cfw_app_disc_test_record_hash(uint32_t h){assert(h==0x1000U);return record_hash;}
            uint16_t *open_cfw_app_disc_test_record_handles(uint32_t h){assert(h==0x1000U);return record_handles;}
            uint8_t open_cfw_app_disc_test_record_status(uint32_t h){assert(h==0x1000U);return record_status;}
            void open_cfw_app_disc_test_prepare_service_control(void *p,void *chars,uint16_t *handles,uint8_t len){assert(p==allocation&&chars==(void*)0x1234U&&handles&&len==4U);prepare_service++;}
            void open_cfw_app_disc_test_prepare_configuration_control(void *p,void *cfg,uint8_t cfglen,uint16_t *handles,uint8_t hlen){assert(p==allocation&&cfg==(void*)0x5678U&&cfglen==2U&&handles&&hlen==4U);prepare_config++;}

            int main(void){
                uint16_t handles[4]={0};uint8_t uuid[2]={1U,2U};
                uint8_t value[24]={0};open_cfw_app_disc_event_t event={0};
                memset((void*)open_cfw_app_disc_control,0,sizeof(open_cfw_app_disc_control));
                open_cfw_app_disc_callback=callback;
                open_cfw_app_disc_configuration_start(1U,4U);assert(last_notification==6U);
                open_cfw_app_disc_configuration_start(1U,8U);assert(last_notification==7U);
                open_cfw_app_disc_set_handle_list(1U,4U,handles);
                open_cfw_app_disc_start(1U);assert(last_notification==3U);

                open_cfw_app_disc_find_service(1U,2U,uuid,4U,(void*)0x1234U,handles);
                assert(allocs==1U&&prepare_service==1U&&discover_calls==1U&&last_idle==1U);
                assert(open_cfw_app_disc_control[0].in_progress==1U);
                event.parameter=1U;event.event=3U;service_result=0U;
                open_cfw_app_disc_process_att_message(&event);assert(svc_cmpl==1U&&char_start==1U);
                event.event=4U;event.value=value;event.value_length=8U;char_result=0U;
                open_cfw_app_disc_process_att_message(&event);assert(char_cmpl==1U&&last_notification==4U);

                open_cfw_app_disc_control[0].discovery=0;
                config_result=0U;
                open_cfw_app_disc_configure(1U,7U,2U,(void*)0x5678U,4U,handles);
                assert(allocs==2U&&prepare_config==1U&&cfg_start_calls==1U);
                assert(last_notification==8U&&open_cfw_app_disc_control[0].in_progress==2U);
                event.event=5U;event.status=5U;security_level=0U;
                open_cfw_app_disc_process_att_message(&event);
                assert(open_cfw_app_disc_control[0].security_required==1U&&last_notification==2U);
                open_cfw_app_disc_control[0].service_changed_pending=1U;event.status=0U;
                open_cfw_app_disc_process_att_message(&event);
                assert(open_cfw_app_disc_control[0].service_changed_pending==0U);

                open_cfw_app_disc_control[0].in_progress=0U;
                open_cfw_app_disc_read_database_hash(1U);assert(read_hash_calls==1U);
                event.event=4U;event.status=0U;event.value=value;event.value_length=19U;
                new_hash[0]=0xa5U;memcpy(value+3,new_hash,16U);
                open_cfw_app_disc_connection_database[0]=0U;
                open_cfw_app_disc_process_att_message(&event);
                assert(new_records==1U&&open_cfw_app_disc_connection_database[0]==0x1000U);
                assert(set_hash==1U&&set_cache==1U&&last_notification==3U);
                open_cfw_app_disc_control[0].in_progress=0U;
                open_cfw_app_disc_control[0].connection_configuration_status=0U;
                open_cfw_app_disc_read_database_hash(1U);
                open_cfw_app_disc_process_att_message(&event);
                assert(handles[0]==11U&&handles[3]==44U&&last_notification==7U);

                open_cfw_app_disc_control[0].discovery=allocation;
                open_cfw_app_disc_control[0].in_progress=1U;
                open_cfw_app_disc_complete(1U,4U);
                assert(frees==1U&&set_status>=1U&&set_handles>=1U);
                assert(open_cfw_app_disc_control[0].discovery==0&&last_idle==0U);
                open_cfw_app_disc_control[0].in_progress=2U;
                open_cfw_app_disc_restart(1U);
                assert(open_cfw_app_disc_control[0].service_changed_pending==1U);
                open_cfw_app_disc_parse_read_by_type(0,0);
                open_cfw_app_disc_parse_find_information(0,0);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary=Path(directory);harness_path=temporary/"harness.c";exe=temporary/"test"
            harness_path.write_text(harness)
            subprocess.run(["cc","-std=c11","-O2","-Wall","-Wextra","-Werror","-I",str(SOURCE_DIR),str(harness_path),"-o",str(exe)],check=True)
            subprocess.run([str(exe)],check=True)

    def test_all_isolated_cortex_m55_entries_compile(self) -> None:
        selectors=("CFG_START","START","RESTART","PARSE_READ_TYPE","PARSE_FIND_INFO","PROCESS_ATT","SET_HANDLE_LIST","COMPLETE","FIND_SERVICE","CONFIGURE","READ_HASH")
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run(["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-std=c11","-O2","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_CORDIO_APP_DISC_PRODUCTION=1",f"-DOPEN_CFW_CORDIO_APP_DISC_{selector}_ONLY=1","-c",str(SOURCE),"-o",str(Path(directory)/f"{selector}.o")],check=True)


if __name__ == "__main__":
    unittest.main()

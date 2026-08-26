#!/usr/bin/env python3
"""Exercise bounded ATT client discovery and configuration behavior."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_attc_disc.c"


class CordioAttcDiscSourceTests(unittest.TestCase):
    def test_host_discovery_parsing_configuration_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_cordio_attc_disc.h"

            uint8_t open_cfw_cordio_attc_discovery_characteristic_uuid[2]={3,0x28};
            uint8_t open_cfw_cordio_attc_discovery_include_uuid[2]={2,0x28};
            static int find_type,find_info,read_type,reads,writes;
            static uint16_t last_start,last_end,last_handle;
            static uint8_t last_continuing,last_uuid_length,last_value_length;

            uint8_t open_cfw_cordio_att_uuid_compare_16_to_128(
                const uint8_t *u16,const uint8_t *u128) {
                return (uint8_t)(u16[0]==u128[12]&&u16[1]==u128[13]);
            }
            void open_cfw_cordio_attc_find_by_type_value_request(
                uint8_t c,uint16_t s,uint16_t e,uint16_t uuid,uint16_t n,
                uint8_t *v,uint8_t continuing) {
                assert(c==1U&&uuid==0x2800U&&v!=NULL);find_type++;
                last_start=s;last_end=e;last_value_length=(uint8_t)n;
                last_continuing=continuing;
            }
            void open_cfw_cordio_attc_find_information_request(
                uint8_t c,uint16_t s,uint16_t e,uint8_t continuing) {
                assert(c==1U);find_info++;last_start=s;last_end=e;
                last_continuing=continuing;
            }
            void open_cfw_cordio_attc_read_by_type_request(
                uint8_t c,uint16_t s,uint16_t e,uint8_t n,uint8_t *uuid,
                uint8_t continuing) {
                assert(c==1U&&uuid!=NULL);read_type++;last_start=s;last_end=e;
                last_uuid_length=n;last_continuing=continuing;
            }
            void open_cfw_cordio_attc_read_request(uint8_t c,uint16_t h) {
                assert(c==1U);reads++;last_handle=h;
            }
            void open_cfw_cordio_attc_write_request(
                uint8_t c,uint16_t h,uint16_t n,uint8_t *v) {
                assert(c==1U&&v!=NULL);writes++;last_handle=h;
                last_value_length=(uint8_t)n;
            }

            int main(void) {
                uint8_t char_uuid[2]={0x00,0x2A};
                uint8_t desc_uuid[2]={0x02,0x29};
                uint8_t include_uuid[2]={0x0F,0x18};
                struct open_cfw_cordio_attc_discovery_characteristic ch={char_uuid,2U};
                struct open_cfw_cordio_attc_discovery_characteristic desc={desc_uuid,6U};
                struct open_cfw_cordio_attc_discovery_characteristic inc={include_uuid,0U};
                struct open_cfw_cordio_attc_discovery_characteristic *list[2]={&ch,&desc};
                uint16_t handles[2]={0};
                struct open_cfw_cordio_attc_discovery_control_block cb={0};
                struct open_cfw_cordio_att_event event={0};
                uint8_t service[4]={1,0,20,0};
                uint8_t chars[8]={7,2,0,2,3,0,0x00,0x2A};
                uint8_t descriptors[5]={1,4,0,0x02,0x29};
                uint8_t value=1;
                struct open_cfw_cordio_attc_discovery_configuration cfg[2]={
                    {NULL,0,0},{&value,1,1}
                };
                cb.characteristics=list;cb.handles=handles;
                cb.characteristic_count=2;cb.service_start_handle=1;
                cb.service_end_handle=20;

                assert(open_cfw_cordio_attc_discovery_uuid_compare(&ch,char_uuid,0)==1U);
                assert(open_cfw_cordio_attc_discovery_uuid_compare(&ch,desc_uuid,0)==0U);
                assert(open_cfw_cordio_attc_discovery_verify(&cb)==0x76U);

                open_cfw_cordio_attc_discover_service(1,&cb,2,char_uuid);
                assert(find_type==1&&last_start==1U&&last_end==0xFFFFU);
                event.header.event=3U;event.value=service;event.value_length=3U;
                assert(open_cfw_cordio_attc_complete_service_discovery(&cb,&event)==0x73U);
                event.value_length=4U;
                assert(open_cfw_cordio_attc_complete_service_discovery(&cb,&event)==0U);

                open_cfw_cordio_attc_start_characteristic_discovery(1,&cb);
                assert(read_type==1&&last_uuid_length==2U&&last_continuing==1U);
                event.header.parameter=1U;event.header.event=4U;event.header.status=0U;
                event.value=chars;event.value_length=8U;event.continuing=0U;
                assert(open_cfw_cordio_attc_complete_characteristic_discovery(&cb,&event)==0x79U);
                assert(handles[0]==3U&&handles[1]==0U);
                assert(find_info==1&&last_start==4U&&last_end==20U);

                event.header.event=2U;event.value=descriptors;event.value_length=5U;
                event.continuing=0U;
                assert(open_cfw_cordio_attc_complete_characteristic_discovery(&cb,&event)==0U);
                assert(handles[0]==3U&&handles[1]==4U);

                {uint8_t malformed[3]={1,4,0};event.value=malformed;
                 event.value_length=3U;event.header.event=2U;
                 assert(open_cfw_cordio_attc_complete_characteristic_discovery(&cb,&event)==0x73U);
                 assert(handles[0]==0U&&handles[1]==0U);}

                handles[0]=3U;handles[1]=4U;cb.configuration=cfg;
                cb.configuration_count=2U;
                assert(open_cfw_cordio_attc_start_configuration(1,&cb)==0x79U);
                assert(reads==1&&last_handle==3U);
                assert(open_cfw_cordio_attc_complete_configuration(1,&cb)==0x79U);
                assert(writes==1&&last_handle==4U&&last_value_length==1U);
                assert(open_cfw_cordio_attc_complete_configuration(1,&cb)==0U);
                cfg[0].handle_index=3U;cb.characteristic_index=0U;
                assert(open_cfw_cordio_attc_resume_configuration(1,&cb)==0x73U);

                list[0]=&inc;cb.characteristic_count=1U;handles[0]=0U;
                {uint8_t declaration[8]={5,0,1,0,20,0,0x0F,0x18};
                 open_cfw_cordio_attc_discovery_process_included_service(
                    &cb,0U,declaration);assert(handles[0]==5U);}
                event.header.event=4U;event.header.status=0U;
                {uint8_t included[9]={8,5,0,1,0,20,0,0x0F,0x18};
                 event.value=included;event.value_length=9U;event.continuing=0U;
                 assert(open_cfw_cordio_attc_complete_included_service_discovery(
                    &cb,&event)==0U);}
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
            "UUID_COMPARE", "VERIFY", "DESCRIPTORS", "DESCRIPTOR_PAIR",
            "DESCRIPTOR", "CHAR_DECL", "CHARACTERISTIC", "CONFIG_NEXT",
            "INCLUDED_SERVICE", "SERVICE_START", "SERVICE_COMPLETE",
            "CHAR_START", "CHAR_COMPLETE", "INC_START", "INC_COMPLETE",
            "CONFIG_START", "CONFIG_COMPLETE", "CONFIG_RESUME",
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
                    command.append(f"-DOPEN_CFW_ATTC_DISC_{selector}_ONLY=1")
                command += ["-c", str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

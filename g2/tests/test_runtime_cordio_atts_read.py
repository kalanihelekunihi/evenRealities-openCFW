#!/usr/bin/env python3
"""Exercise the G2 Cordio optional ATT server read processors."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_read.c"


class CordioAttsReadSourceTests(unittest.TestCase):
    def test_host_discovery_blob_type_multiple_group_and_hash_deferral(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_read.h"

            struct open_cfw_cordio_wsf_queue_candidate open_cfw_cordio_atts_group_queue;
            open_cfw_cordio_atts_authorization_callback_t open_cfw_cordio_atts_authorization_callback;
            open_cfw_cordio_atts_ccc_write_callback_t open_cfw_cordio_atts_proc_ccc_callback;
            uint8_t open_cfw_cordio_atts_primary_service_uuid[2]={0x00,0x28};
            uint8_t open_cfw_cordio_atts_secondary_service_uuid[2]={0x01,0x28};
            uint8_t open_cfw_cordio_atts_database_hash_uuid[2]={0x2a,0x2b};
            static struct open_cfw_cordio_att_main_control_block main_cb;
            static struct open_cfw_cordio_atts_attribute attrs[6];
            static struct open_cfw_cordio_atts_group group;
            static uint8_t uuid[6][2]={{0x00,0x28},{0x03,0x28},{0x00,0x28},{0x99,0x2a},{0x99,0x2a},{0x2a,0x2b}};
            static uint8_t values[6][4]={{0x0a,0x18},{9},{0x0b,0x18},{1,2},{3,4},{5,6,7,8}};
            static uint16_t lengths[6]={2,1,2,2,2,4};
            static uint8_t response[300], last_error, last_opcode, last_slot;
            static uint16_t last_handle, response_length;
            static unsigned sends, errors, frees, busy, permission_calls, callback_calls;
            static uint8_t hash_busy;

            uint8_t open_cfw_cordio_att_uuid_compare_16_to_128(const uint8_t *a,const uint8_t *b){return a[0]==b[12]&&a[1]==b[13];}
            uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t id){(void)id;return 2;}
            void open_cfw_cordio_atts_csf_get_features(uint8_t id,uint8_t *f,uint8_t n){(void)id;(void)n;*f=0;}
            uint16_t open_cfw_cordio_hci_get_maximum_receive_acl_length(void){return 260;}
            void open_cfw_cordio_att_set_mtu(struct open_cfw_cordio_att_main_control_block *m,uint8_t s,uint16_t p,uint16_t l){(void)m;(void)s;(void)p;(void)l;}
            uint8_t open_cfw_cordio_atts_uuid_compare(struct open_cfw_cordio_atts_attribute *a,uint8_t n,uint8_t *u){return n==2&&a->uuid[0]==u[0]&&a->uuid[1]==u[1];}
            uint8_t open_cfw_cordio_atts_uuid16_compare(uint8_t *u16,uint8_t n,uint8_t *u){return n==2&&u16[0]==u[0]&&u16[1]==u[1];}
            struct open_cfw_cordio_atts_attribute *open_cfw_cordio_atts_find_by_handle(uint16_t h,struct open_cfw_cordio_atts_group **g){if(h<0x10||h>0x15)return 0;*g=&group;return &attrs[h-0x10];}
            uint8_t open_cfw_cordio_atts_permissions(uint8_t id,uint8_t permit,uint16_t h,uint8_t p){assert(id==1&&permit==1);permission_calls++;return (h>=0x10&&(p&1))?0:2;}
            uint8_t open_cfw_cordio_atts_csf_get_hash_update_status(void){return hash_busy;}
            void *open_cfw_cordio_att_message_allocate(uint16_t n){assert(n<=sizeof(response));memset(response,0,sizeof(response));return response;}
            void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t n){return calloc(1,n);}
            void open_cfw_cordio_att_l2c_data_request(struct open_cfw_cordio_att_main_control_block *m,uint8_t s,uint16_t n,uint8_t *p){assert(m==&main_cb&&p==response);sends++;last_slot=s;response_length=n;}
            void open_cfw_cordio_atts_error_response(struct open_cfw_cordio_att_main_control_block *m,uint8_t s,uint8_t op,uint16_t h,uint8_t e){assert(m==&main_cb);errors++;last_slot=s;last_opcode=op;last_handle=h;last_error=e;}
            void open_cfw_cordio_atts_discovery_busy(struct open_cfw_cordio_atts_connection_control_block *c){assert(c->main==&main_cb);busy++;}
            void open_cfw_cordio_wsf_message_free(void *p){assert(p==response);frees++;}
            void open_cfw_cordio_att_message_free(void *p,uint8_t op){(void)p;(void)op;}
            static uint8_t read_callback(uint8_t id,uint16_t h,uint8_t op,uint16_t off,struct open_cfw_cordio_atts_attribute *a){assert(id==1&&h==0x13&&op==0x0c&&off==1&&a==&attrs[3]);callback_calls++;return 0;}

            static void put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
            int main(void){
                struct open_cfw_cordio_atts_connection_control_block ccb;
                struct open_cfw_cordio_atts_attribute *a=0;
                struct open_cfw_cordio_atts_group *g=0;
                uint8_t packet[80]={0};
                memset(&main_cb,0,sizeof(main_cb));memset(&ccb,0,sizeof(ccb));memset(&group,0,sizeof(group));
                for(unsigned i=0;i<6;i++){attrs[i].uuid=uuid[i];attrs[i].value=values[i];attrs[i].length=&lengths[i];attrs[i].permissions=1;}
                group.attributes=attrs;group.start_handle=0x10;group.end_handle=0x15;open_cfw_cordio_atts_group_queue.head=&group;
                ccb.main=&main_cb;ccb.connection_id=1;ccb.slot=1;main_cb.connection_id=1;main_cb.bearer[1].mtu=23;
                assert(open_cfw_cordio_atts_find_uuid_in_range(1,0x15,2,uuid[3],&a,&g)==0x13&&a==&attrs[3]&&g==&group);
                assert(open_cfw_cordio_atts_find_uuid_in_range(0x14,0x14,2,uuid[3],&a,&g)==0x14);
                assert(open_cfw_cordio_atts_find_service_group_end(0x10)==0x11);
                assert(open_cfw_cordio_atts_find_service_group_end(0x12)==0xffff);
                assert(open_cfw_cordio_atts_find_service_group_end(0xffff)==0xffff);

                put16(packet+9,0x13);put16(packet+11,1);attrs[3].settings=4;group.read_callback=(void *)read_callback;
                open_cfw_cordio_atts_process_read_blob_request(&ccb,5,packet);
                assert(callback_calls==1&&sends==1&&response[8]==0x0d&&response[9]==2&&response_length==2&&last_slot==1);
                put16(packet+11,3);open_cfw_cordio_atts_process_read_blob_request(&ccb,5,packet);
                assert(last_opcode==0x0c&&last_handle==0x13&&last_error==7);
                attrs[3].settings=0;group.read_callback=0;

                memset(packet,0,sizeof(packet));put16(packet+9,0x10);put16(packet+11,0x15);packet[13]=0;packet[14]=0x28;
                open_cfw_cordio_atts_process_find_type_request(&ccb,7,packet);
                assert(response[8]==7&&response[9]==0x10&&response[11]==0x11&&response[13]==0x12&&response[15]==0xff);
                assert(response_length==9&&busy>=1);
                packet[13]=0xaa;packet[14]=0xbb;open_cfw_cordio_atts_process_find_type_request(&ccb,7,packet);
                assert(frees==1&&last_opcode==6&&last_error==0x0a);

                memset(packet,0,sizeof(packet));put16(packet+9,0x13);put16(packet+11,0x14);packet[13]=0x99;packet[14]=0x2a;
                open_cfw_cordio_atts_process_read_type_request(&ccb,7,packet);
                assert(response[8]==9&&response[9]==4&&response[10]==0x13&&response[12]==1&&response[14]==0x14&&response[16]==3&&response_length==10);
                packet[13]=0x2a;packet[14]=0x2b;put16(packet+9,0x15);put16(packet+11,0x15);hash_busy=1;
                open_cfw_cordio_atts_process_read_type_request(&ccb,7,packet);
                assert(main_cb.pending_database_hash_response!=0);
                struct open_cfw_cordio_atts_pending_database_hash_response *pending=main_cb.pending_database_hash_response;
                assert(pending->start_handle==0x15&&pending->handle==0x15);free(pending);main_cb.pending_database_hash_response=0;hash_busy=0;

                memset(packet,0,sizeof(packet));put16(packet+9,0x13);put16(packet+11,0x14);
                open_cfw_cordio_atts_process_read_multiple_request(&ccb,5,packet);
                assert(response[8]==0x0f&&response[9]==1&&response[10]==2&&response[11]==3&&response[12]==4&&response_length==5);
                put16(packet+11,0x99);open_cfw_cordio_atts_process_read_multiple_request(&ccb,5,packet);
                assert(last_opcode==0x0e&&last_handle==0x99&&last_error==1&&frees==2);

                memset(packet,0,sizeof(packet));put16(packet+9,0x10);put16(packet+11,0x15);packet[13]=0;packet[14]=0x28;
                open_cfw_cordio_atts_process_read_group_type_request(&ccb,7,packet);
                assert(response[8]==0x11&&response[9]==6&&response[10]==0x10&&response[12]==0x11&&response[14]==0x0a);
                assert(response[16]==0x12&&response[18]==0xff&&response_length==14);
                packet[13]=0x99;packet[14]=0x2a;open_cfw_cordio_atts_process_read_group_type_request(&ccb,7,packet);
                assert(last_opcode==0x10&&last_error==0x10);
                assert(permission_calls>0&&errors>=3&&sends>=5);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "harness.c"
            binary = Path(directory) / "harness"
            src.write_text(harness)
            subprocess.run([
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE_DIR), str(src), str(SOURCE), "-o", str(binary),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(binary)], check=True)

    def test_isolated_arm_leaves(self) -> None:
        selectors = (
            "FIND_UUID", "FIND_SERVICE_END", "BLOB", "FIND_TYPE",
            "TYPE", "MULTIPLE", "GROUP_TYPE",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_READ_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_READ_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()

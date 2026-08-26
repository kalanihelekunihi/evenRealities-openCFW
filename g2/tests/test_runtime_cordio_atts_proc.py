#!/usr/bin/env python3
"""Exercise the G2 Cordio common ATT server processors."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_proc.c"


class CordioAttsProcSourceTests(unittest.TestCase):
    def test_host_lookup_security_mtu_discovery_and_read_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_proc.h"

            struct open_cfw_cordio_wsf_queue_candidate
                open_cfw_cordio_atts_group_queue;
            open_cfw_cordio_atts_authorization_callback_t
                open_cfw_cordio_atts_authorization_callback;
            open_cfw_cordio_atts_ccc_write_callback_t
                open_cfw_cordio_atts_proc_ccc_callback;
            static struct open_cfw_cordio_att_configuration configuration = {
                0, 300, 30, 3
            };
            struct open_cfw_cordio_att_configuration
                *open_cfw_cordio_att_configuration = &configuration;
            static struct open_cfw_cordio_att_main_control_block main_cb;
            static uint8_t output[600], features, security_level;
            static uint8_t last_error, last_opcode, last_slot;
            static uint16_t last_handle, last_length, peer_mtu, local_mtu;
            static unsigned sends, errors, frees, busy_calls;

            uint8_t open_cfw_cordio_att_uuid_compare_16_to_128(
                const uint8_t *u16, const uint8_t *u128
            ) { return u16[0] == u128[12] && u16[1] == u128[13]; }
            uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t id) {
                assert(id == 2); return security_level;
            }
            static uint8_t authorize(uint8_t id, uint8_t permit, uint16_t h) {
                assert(id == 2 && permit == 1 && h == 0x11); return 0x80;
            }
            void open_cfw_cordio_atts_csf_get_features(
                uint8_t id, uint8_t *out, uint8_t n
            ) { assert(id == 2 && n == 1); *out = features; }
            uint16_t open_cfw_cordio_hci_get_maximum_receive_acl_length(void) {
                return 260;
            }
            void open_cfw_cordio_att_set_mtu(
                struct open_cfw_cordio_att_main_control_block *m, uint8_t s,
                uint16_t peer, uint16_t local
            ) { assert(m == &main_cb && s == 1); peer_mtu=peer; local_mtu=local; }
            void *open_cfw_cordio_att_message_allocate(uint16_t n) {
                assert(n <= sizeof(output)); memset(output, 0, sizeof(output));
                return output;
            }
            void open_cfw_cordio_att_l2c_data_request(
                struct open_cfw_cordio_att_main_control_block *m, uint8_t s,
                uint16_t n, uint8_t *p
            ) { assert(m == &main_cb && p == output); sends++; last_slot=s; last_length=n; }
            void open_cfw_cordio_atts_error_response(
                struct open_cfw_cordio_att_main_control_block *m, uint8_t s,
                uint8_t opcode, uint16_t h, uint8_t reason
            ) { assert(m == &main_cb); errors++; last_slot=s; last_opcode=opcode; last_handle=h; last_error=reason; }
            void open_cfw_cordio_atts_discovery_busy(
                struct open_cfw_cordio_atts_connection_control_block *c
            ) { assert(c->main == &main_cb); busy_calls++; }
            void open_cfw_cordio_wsf_message_free(void *p) { assert(p == output); frees++; }
            void open_cfw_cordio_att_message_free(void *p, uint8_t op) {
                assert(p == output && op == 0x21); frees++;
            }

            int main(void) {
                struct open_cfw_cordio_atts_attribute attrs[3];
                struct open_cfw_cordio_atts_group group;
                struct open_cfw_cordio_atts_connection_control_block ccb;
                uint8_t uuids[3][16] = {{0x01,0x18},{0x02,0x18},{0}};
                uint8_t values[3][8] = {{1,2,3},{4,5},{6}};
                uint16_t lengths[3] = {3,2,1};
                uint8_t packet[64] = {0};
                struct open_cfw_cordio_atts_group *found_group = 0;
                struct open_cfw_cordio_atts_attribute *found_attr = 0;
                uint8_t uuid128[16] = {0};

                memset(attrs,0,sizeof(attrs)); memset(&group,0,sizeof(group));
                memset(&ccb,0,sizeof(ccb)); memset(&main_cb,0,sizeof(main_cb));
                for (unsigned i=0;i<3;i++) { attrs[i].uuid=uuids[i]; attrs[i].value=values[i]; attrs[i].length=&lengths[i]; attrs[i].permissions=1; }
                attrs[2].settings=1;
                group.attributes=attrs; group.start_handle=0x10; group.end_handle=0x12;
                open_cfw_cordio_atts_group_queue.head=&group;
                ccb.main=&main_cb; ccb.connection_id=2; ccb.slot=1;
                main_cb.connection_id=2; main_cb.bearer[1].mtu=23;

                assert(open_cfw_cordio_atts_find_by_handle(0x11,&found_group)==&attrs[1]);
                assert(found_group==&group);
                assert(open_cfw_cordio_atts_find_by_handle(0x20,&found_group)==0);
                assert(open_cfw_cordio_atts_find_in_range(1,0x10,&found_attr)==0x10);
                assert(found_attr==&attrs[0]);
                assert(open_cfw_cordio_atts_find_in_range(0x20,0x30,&found_attr)==0);
                assert(open_cfw_cordio_atts_uuid_compare(&attrs[0],2,uuids[0])==1);
                uuid128[12]=1; uuid128[13]=0x18;
                assert(open_cfw_cordio_atts_uuid_compare(&attrs[0],16,uuid128)==1);
                assert(open_cfw_cordio_atts_uuid16_compare(uuids[0],16,uuid128)==1);

                assert(open_cfw_cordio_atts_permissions(2,1,0x11,0)==2);
                assert(open_cfw_cordio_atts_permissions(2,0x10,0x11,0)==3);
                security_level=0;
                assert(open_cfw_cordio_atts_permissions(2,1,0x11,3)==5);
                security_level=2;
                assert(open_cfw_cordio_atts_permissions(2,1,0x11,7)==0);
                assert(open_cfw_cordio_atts_permissions(2,1,0x11,9)==8);
                open_cfw_cordio_atts_authorization_callback=authorize;
                assert(open_cfw_cordio_atts_permissions(2,1,0x11,9)==0x80);

                packet[9]=23;
                open_cfw_cordio_atts_process_mtu_request(&ccb,3,packet);
                assert(peer_mtu==247 && local_mtu==256);
                assert(output[8]==3 && output[9]==0 && output[10]==1);
                features=2;
                open_cfw_cordio_atts_process_mtu_request(&ccb,3,packet);
                assert(last_opcode==2 && last_error==6);
                features=0;

                packet[9]=0x10; packet[10]=0; packet[11]=0x12; packet[12]=0;
                open_cfw_cordio_atts_process_find_information_request(&ccb,5,packet);
                assert(busy_calls==1 && output[8]==5 && output[9]==1);
                assert(output[10]==0x10 && output[12]==1 && last_length==10);
                packet[9]=0; packet[10]=0;
                open_cfw_cordio_atts_process_find_information_request(&ccb,5,packet);
                assert(last_opcode==4 && last_error==1 && last_handle==0);

                packet[9]=0x10; packet[10]=0;
                open_cfw_cordio_atts_process_read_request(&ccb,3,packet);
                assert(output[8]==0x0b && output[9]==1 && output[11]==3);
                assert(last_length==4 && last_slot==1);
                packet[9]=0x99;
                open_cfw_cordio_atts_process_read_request(&ccb,3,packet);
                assert(last_opcode==0x0a && last_error==1);

                main_cb.bearer[1].mtu=12;
                packet[9]=0x10; packet[10]=0; packet[11]=0x11; packet[12]=0;
                open_cfw_cordio_atts_process_read_multiple_variable_request(&ccb,5,packet);
                assert(output[8]==0x21 && output[9]==3 && output[11]==1);
                assert(output[14]==2 && output[16]==4 && last_length==10);
                attrs[1].permissions=0;
                open_cfw_cordio_atts_process_read_multiple_variable_request(&ccb,5,packet);
                assert(frees==1 && last_opcode==0x20 && last_handle==0x11 && last_error==2);
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
            "UUID", "UUID16", "FIND_HANDLE", "FIND_RANGE", "PERMISSIONS",
            "MTU", "FIND_INFO", "READ", "READ_MULTI_VAR",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_PROC_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_PROC_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()

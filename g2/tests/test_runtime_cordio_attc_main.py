#!/usr/bin/env python3
"""Exercise the production-routable Cordio ATT client core."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_attc_main.c"


class CordioAttcMainSourceTests(unittest.TestCase):
    def test_host_request_connection_and_dispatch_behavior(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_attc_main.h"

            struct open_cfw_cordio_attc_connection_control_block
                open_cfw_cordio_attc_main_connections[3][3];
            struct open_cfw_cordio_attc_api_message
                open_cfw_cordio_attc_on_deck[3];
            const struct open_cfw_cordio_attc_sign_interface
                *open_cfw_cordio_attc_sign_interface;
            uint8_t open_cfw_cordio_attc_auto_confirm;
            struct open_cfw_cordio_attc_main_control_block
                open_cfw_cordio_attc_main_control_blocks[3];
            struct open_cfw_cordio_attc_interface
                *open_cfw_cordio_attc_client_interface;
            struct open_cfw_cordio_attc_interface
                *open_cfw_cordio_attc_stock_interface;
            uint8_t open_cfw_cordio_attc_handler_id = 9;
            open_cfw_cordio_attc_callback_t open_cfw_cordio_attc_callback;
            static struct open_cfw_cordio_attc_configuration cfg = {0,80,7,3};
            struct open_cfw_cordio_attc_configuration
                *open_cfw_cordio_attc_configuration = &cfg;

            static int in_use[4] = {0,1,1,1};
            static uint8_t role;
            static uint16_t max_rx = 100;
            static int starts, stops, sends, frees, callbacks, confirms;
            static int rsp, ind, multi, mtu_requests, sign_closes, sign_messages;
            static uint32_t last_seconds;
            static uint16_t last_length, last_mtu, last_handle;
            static uint8_t *last_packet;
            static uint8_t last_event, last_status;

            uint8_t open_cfw_cordio_dm_connection_in_use(uint8_t id) {
                return id < 4U ? (uint8_t)in_use[id] : 0U;
            }
            uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t h) {
                return h == 0x2222U ? 1U : 0U;
            }
            uint8_t open_cfw_cordio_dm_connection_role(uint8_t id) {
                (void)id; return role;
            }
            uint16_t open_cfw_cordio_hci_get_max_rx_acl_length(void) {
                return max_rx;
            }
            void *open_cfw_cordio_att_message_allocate(uint16_t n) {
                return calloc(1,n);
            }
            void open_cfw_cordio_wsf_message_free_candidate(void *p) {
                frees++; free(p);
            }
            void open_cfw_cordio_wsf_timer_start_sec_candidate(void *p,uint32_t s) {
                (void)p; starts++; last_seconds=s;
            }
            void open_cfw_cordio_wsf_timer_stop_candidate(void *p) {
                (void)p; stops++;
            }
            void open_cfw_cordio_att_l2c_data_request(
                struct open_cfw_cordio_attc_main_control_block *m,
                uint8_t slot,uint16_t n,uint8_t *p) {
                assert(m==&open_cfw_cordio_attc_main_control_blocks[0]);
                assert(slot<3U); sends++; last_length=n; last_packet=p;
            }
            void open_cfw_cordio_att_execute_callback(
                uint8_t id,uint8_t event,uint16_t handle,uint8_t status,uint16_t mtu) {
                assert(id==1U); callbacks++; last_event=event; last_handle=handle;
                last_status=status; assert(mtu==0U);
            }
            void open_cfw_cordio_attc_process_response(
                struct open_cfw_cordio_attc_connection_control_block *c,
                uint16_t n,uint8_t *p) {(void)c;(void)n;(void)p;rsp++;}
            void open_cfw_cordio_attc_process_indication_notification(
                struct open_cfw_cordio_attc_connection_control_block *c,
                uint16_t n,uint8_t *p) {(void)c;(void)n;(void)p;ind++;}
            void open_cfw_cordio_attc_process_multiple_variable_notification(
                struct open_cfw_cordio_attc_connection_control_block *c,
                uint16_t n,uint8_t *p) {(void)c;(void)n;(void)p;multi++;}
            void open_cfw_cordio_attc_mtu_request(uint8_t id,uint16_t mtu) {
                assert(id==1U);mtu_requests++;last_mtu=mtu;
            }
            void open_cfw_cordio_attc_indication_confirm(uint8_t id) {
                assert(id==1U);confirms++;
            }
            static void sign_message(
                struct open_cfw_cordio_attc_connection_control_block *c,
                struct open_cfw_cordio_attc_api_message *m) {
                assert(c==NULL&&m!=NULL);sign_messages++;
            }
            static void sign_close(
                struct open_cfw_cordio_attc_connection_control_block *c,
                uint8_t status) {assert(c!=NULL&&status==0xB3U);sign_closes++;}
            static const struct open_cfw_cordio_attc_sign_interface sign_if = {
                sign_message,sign_close
            };
            static struct open_cfw_cordio_attc_interface stock_if;

            static union open_cfw_cordio_attc_packet_parameter *packet(uint16_t len) {
                union open_cfw_cordio_attc_packet_parameter *p=calloc(1,8U+len);
                assert(p!=NULL);p->length=len;return p;
            }

            int main(void) {
                struct open_cfw_cordio_attc_connection_control_block *c;
                struct open_cfw_cordio_attc_api_message msg={0};
                uint8_t pdu[16]={0};
                open_cfw_cordio_attc_stock_interface=&stock_if;
                open_cfw_cordio_attc_initialize();
                assert(open_cfw_cordio_attc_auto_confirm==1U);
                assert(open_cfw_cordio_attc_client_interface==&stock_if);
                for(uint8_t i=0;i<3U;i++) {
                    open_cfw_cordio_attc_main_control_blocks[i].connection_id=
                        (uint8_t)(i+1U);
                    for(uint8_t s=0;s<3U;s++) {
                    c=&open_cfw_cordio_attc_main_connections[i][s];
                    assert(c->main==&open_cfw_cordio_attc_main_control_blocks[i]);
                    assert(c->connection_id==i+1U&&c->slot==s);
                    assert(c->outstanding_timer[8]==i+1U);
                    assert(c->outstanding_timer[9]==0U);
                    assert(c->outstanding_timer[12]==9U);
                    }
                }
                assert(open_cfw_cordio_attc_connection_by_id(0,0)==NULL);
                assert(open_cfw_cordio_attc_connection_by_id(4,0)==NULL);
                assert(open_cfw_cordio_attc_connection_by_id(1,3)==NULL);
                assert(open_cfw_cordio_attc_connection_by_handle(0x2222,0)==
                    &open_cfw_cordio_attc_main_connections[0][0]);
                assert(open_cfw_cordio_attc_connection_by_handle(0x3333,0)==NULL);

                c=&open_cfw_cordio_attc_main_connections[0][0];
                assert(open_cfw_cordio_attc_pending_write_command(c,0x1111)==0U);
                c->outstanding_request.handle=0x1111;
                open_cfw_cordio_attc_set_pending_write_command(c);
                assert(open_cfw_cordio_attc_pending_write_command(c,0x2222)==1U);
                open_cfw_cordio_attc_write_command_callback(1,c,0x72);
                assert(c->pending_write_handles[0]==0U&&last_status==0x72U);

                c->outstanding_request.header.event=5U;
                c->outstanding_request.slot=0U;c->outstanding_request.packet=packet(3U);
                open_cfw_cordio_attc_send_simple_request(c);
                assert(c->outstanding_request.packet==NULL&&starts==1);
                assert(last_seconds==7U&&c->outstanding_timer[10]==20U);
                assert(sends==1&&last_length==3U);free(last_packet);

                c->outstanding_request.header.event=2U;
                c->outstanding_request.header.status=0U;
                c->outstanding_request.packet=packet(5U);
                c->outstanding_parameters.handles.start_handle=0x1234U;
                c->outstanding_parameters.handles.end_handle=0x5678U;
                open_cfw_cordio_attc_send_continuing_request(c);
                assert(last_packet[9]==0x34U&&last_packet[10]==0x12U);
                assert(last_packet[11]==0x78U&&last_packet[12]==0x56U);
                free(last_packet);

                c->outstanding_request.header.event=1U;
                c->outstanding_request.packet=packet(3U);
                open_cfw_cordio_attc_send_mtu_request(c);
                assert((open_cfw_cordio_attc_main_control_blocks[0].bearer[0].control&1U)!=0U);
                free(last_packet);
                c->outstanding_request.header.event=1U;
                c->outstanding_request.packet=packet(3U);
                open_cfw_cordio_attc_send_mtu_request(c);
                assert(c->outstanding_request.header.event==0U&&frees==1);

                open_cfw_cordio_attc_main_control_blocks[0].bearer[0].mtu=8U;
                c->outstanding_request.header.event=11U;
                c->outstanding_request.header.status=1U;
                c->outstanding_request.packet=packet(5U);
                c->outstanding_parameters.prepare.length=5U;
                c->outstanding_parameters.prepare.offset=2U;
                {static uint8_t value[5]={1,2,3,4,5};
                 c->outstanding_parameters.prepare.value=value;}
                open_cfw_cordio_attc_send_prepare_write_request(c);
                assert(last_length==8U&&last_packet[11]==2U);
                assert(last_packet[13]==1U&&last_packet[15]==3U);
                assert(c->outstanding_parameters.prepare.length==2U);
                free(last_packet);open_cfw_cordio_attc_free_packet(&c->outstanding_request);

                open_cfw_cordio_attc_data_callback(0x2222,0U,pdu);
                pdu[8]=0x13U;open_cfw_cordio_attc_data_callback(0x2222,1U,pdu);
                pdu[8]=0x1BU;open_cfw_cordio_attc_data_callback(0x2222,3U,pdu);
                pdu[8]=0x23U;open_cfw_cordio_attc_data_callback(0x2222,1U,pdu);
                assert(rsp==1&&ind==1&&multi==1);

                c->pending_write_handles[0]=0x3344U;
                {struct open_cfw_cordio_wsf_message_header h={1U,0U,0U};
                 open_cfw_cordio_attc_control_callback(&h);}
                assert(confirms==1&&c->pending_write_handles[0]==0U);

                role=0U;max_rx=100U;
                {struct open_cfw_cordio_attc_dm_event e={{0U,0x27U,0U},{0},0U};
                 open_cfw_cordio_attc_connection_callback(
                    &open_cfw_cordio_attc_main_control_blocks[0],&e);}
                assert(mtu_requests==1&&last_mtu==80U);

                open_cfw_cordio_attc_sign_interface=&sign_if;
                open_cfw_cordio_attc_on_deck[0].header.event=5U;
                open_cfw_cordio_attc_on_deck[0].handle=0x5555U;
                open_cfw_cordio_attc_on_deck[0].packet=packet(1U);
                for(uint8_t s=0;s<3U;s++) {
                    open_cfw_cordio_attc_main_connections[0][s].pending_write_handles[0]=
                        (uint16_t)(0x6000U+s);
                    open_cfw_cordio_attc_main_control_blocks[0].bearer[s].control=0x12U;
                }
                {struct open_cfw_cordio_attc_dm_event e={{0U,0x28U,0U},{0},0x13U};
                 open_cfw_cordio_attc_connection_callback(
                    &open_cfw_cordio_attc_main_control_blocks[0],&e);}
                assert(open_cfw_cordio_attc_on_deck[0].header.event==0U);
                assert(sign_closes==3&&last_status==0xB3U);
                for(uint8_t s=0;s<3U;s++)
                    assert(open_cfw_cordio_attc_main_control_blocks[0].bearer[s].control==0U);

                msg.header.event=17U;open_cfw_cordio_attc_message_callback(&msg);
                assert(sign_messages==1);
                open_cfw_cordio_attc_sign_interface=NULL;
                c->outstanding_request.header.event=1U;
                msg.header.parameter=1U;msg.header.event=5U;msg.slot=0U;
                msg.packet=packet(3U);msg.handle=0x7777U;
                open_cfw_cordio_attc_message_callback(&msg);
                assert(open_cfw_cordio_attc_on_deck[0].header.event==5U);
                msg.header.event=19U;msg.packet=NULL;
                open_cfw_cordio_attc_message_callback(&msg);
                assert(open_cfw_cordio_attc_on_deck[0].header.event==0U);
                assert(last_status==0x74U);

                c->outstanding_request.header.event=5U;
                c->outstanding_request.handle=0x8888U;
                c->outstanding_request.packet=packet(3U);
                msg.header.event=20U;msg.slot=0U;
                open_cfw_cordio_attc_message_callback(&msg);
                assert(c->outstanding_request.header.event==0U);
                assert(last_status==0x71U);
                assert((open_cfw_cordio_attc_main_control_blocks[0].bearer[0].control&4U)!=0U);
                open_cfw_cordio_attc_set_auto_confirm(0U);
                assert(open_cfw_cordio_attc_auto_confirm==0U);
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
            "PEND_WRITE", "SET_PEND_WRITE", "WRITE_CALLBACK", "SIMPLE_REQ",
            "CONTINUING_REQ", "MTU_REQ", "WRITE_CMD", "PREP_WRITE_REQ",
            "SEND_REQ", "SETUP_REQ", "DATA_CALLBACK", "CONTROL_CALLBACK",
            "CONNECTION_CALLBACK", "MESSAGE_CALLBACK", "CCB_BY_ID",
            "CCB_BY_HANDLE", "FREE_PACKET", "EXEC_CALLBACK", "REQUEST_CLEAR",
            "INITIALIZE", "AUTO_CONFIRM",
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
                    command.append(f"-DOPEN_CFW_ATTC_MAIN_{selector}_ONLY=1")
                command += ["-c", str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Exercise the production-routed G2 Cordio ATT client PDU processor."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_attc_proc.c"


class CordioAttcProcSourceTests(unittest.TestCase):
    def test_host_dispatch_serialization_and_hardening(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_attc_proc.h"

            open_cfw_cordio_attc_callback_t open_cfw_cordio_attc_callback;
            uint8_t open_cfw_cordio_attc_handler_id = 7;
            uint8_t open_cfw_cordio_attc_auto_confirm = 1;
            struct open_cfw_cordio_attc_api_message open_cfw_cordio_attc_on_deck[3];
            static struct open_cfw_cordio_attc_configuration cfg = {0, 100, 30, 3};
            struct open_cfw_cordio_attc_configuration *open_cfw_cordio_attc_configuration = &cfg;
            static struct open_cfw_cordio_attc_connection_control_block ccb;
            static struct open_cfw_cordio_attc_main_control_block main_cb;
            static int locks, unlocks, timer_stops, callbacks, frees, sent_msgs, l2c_sends;
            static int setup_requests;
            static int exec_callbacks; static uint8_t exec_status;
            static struct open_cfw_cordio_att_event last_event;
            static struct open_cfw_cordio_attc_api_message *last_msg;
            static uint8_t *last_l2c;

            void *open_cfw_cordio_att_message_allocate(uint16_t n) { return calloc(1,n); }
            void open_cfw_cordio_att_set_mtu(struct open_cfw_cordio_attc_main_control_block *m,
                uint8_t s,uint16_t peer,uint16_t local){m->bearer[s].mtu=peer<local?peer:local;}
            uint16_t open_cfw_cordio_hci_get_max_rx_acl_length(void){return 104;}
            void open_cfw_cordio_wsf_timer_stop_candidate(void *t){(void)t;timer_stops++;}
            void open_cfw_cordio_attc_free_packet(struct open_cfw_cordio_attc_api_message *m){
                m->packet=NULL;frees++;}
            void open_cfw_cordio_attc_send_request(struct open_cfw_cordio_attc_connection_control_block *c){(void)c;}
            void open_cfw_cordio_attc_setup_request(struct open_cfw_cordio_attc_connection_control_block *c,
                struct open_cfw_cordio_attc_api_message *m){(void)c;setup_requests++;
                assert(m==&open_cfw_cordio_attc_on_deck[0]);}
            void open_cfw_cordio_wsf_task_lock_candidate(void){locks++;}
            void open_cfw_cordio_wsf_task_unlock_candidate(void){unlocks++;}
            struct open_cfw_cordio_attc_connection_control_block *open_cfw_cordio_attc_connection_by_id(uint8_t id,uint8_t s){
                (void)s;return id==ccb.connection_id?&ccb:NULL;}
            struct open_cfw_cordio_attc_connection_control_block *open_cfw_cordio_attc_connection_by_handle(uint16_t h,uint8_t s){
                (void)s;return h==main_cb.handle?&ccb:NULL;}
            void open_cfw_cordio_attc_execute_callback(uint8_t c,uint8_t e,uint16_t h,uint8_t s){
                (void)c;(void)e;(void)h;exec_callbacks++;exec_status=s;}
            void open_cfw_cordio_att_l2c_data_request(struct open_cfw_cordio_attc_main_control_block *m,
                uint8_t s,uint16_t n,uint8_t *p){(void)m;(void)s;assert(n==1);l2c_sends++;last_l2c=p;}
            void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t n){return calloc(1,n);}
            void open_cfw_cordio_wsf_message_free_candidate(void *p){free(p);frees++;}
            void open_cfw_cordio_wsf_message_send_candidate(uint8_t h,void *p){assert(h==7);sent_msgs++;last_msg=p;}
            static void callback(struct open_cfw_cordio_att_event *e){callbacks++;last_event=*e;}

            int main(void){
                uint8_t packet[40]={0}; uint8_t value[2]={0xAA,0xBB};
                memset(&ccb,0,sizeof(ccb));memset(&main_cb,0,sizeof(main_cb));
                ccb.main=&main_cb;ccb.connection_id=1;main_cb.connection_id=1;
                main_cb.handle=0x2222;main_cb.bearer[0].mtu=23;
                open_cfw_cordio_attc_callback=callback;

                ccb.outstanding_request.header.event=5; ccb.outstanding_request.handle=0x1234;
                packet[9]=0x0A;packet[10]=0x34;packet[11]=0x12;packet[12]=0;
                {struct open_cfw_cordio_att_event e={0};
                 open_cfw_cordio_attc_process_error_response(&ccb,5,packet,&e);
                 assert(e.header.event==5&&e.header.status==0x75&&e.value_length==0);}

                ccb.outstanding_request.header.event=9;ccb.outstanding_request.header.status=0;
                ccb.outstanding_request.header.parameter=1;ccb.outstanding_request.packet=(void*)1;
                open_cfw_cordio_attc_on_deck[0].header.event=5;
                packet[8]=0x13;
                open_cfw_cordio_attc_process_response(&ccb,1,packet);
                assert(timer_stops==1&&frees==1&&callbacks==1);
                assert(last_event.header.event==9&&last_event.value_length==0);
                assert(setup_requests==1&&open_cfw_cordio_attc_on_deck[0].header.event==0);

                ccb.outstanding_request.header.event=9;packet[8]=0x23;
                open_cfw_cordio_attc_process_response(&ccb,1,packet);
                assert(timer_stops==1); /* method 17 is rejected before table access. */

                packet[8]=0x1D;packet[9]=0x44;packet[10]=0x33;packet[11]=0x99;
                open_cfw_cordio_attc_process_indication_notification(&ccb,4,packet);
                assert(callbacks==2&&last_event.handle==0x3344&&l2c_sends==1);
                assert(last_l2c[8]==0x1E);free(last_l2c);

                {union open_cfw_cordio_attc_packet_parameter *p=calloc(1,11);
                 p->length=3;open_cfw_cordio_attc_send_message(1,0x1234,5,p,0);
                 assert(locks==1&&unlocks==1&&sent_msgs==1);
                 assert(last_msg->header.event==5&&last_msg->packet==p);
                 free(last_msg);free(p);}
                main_cb.bearer[0].mtu=2;
                {union open_cfw_cordio_attc_packet_parameter *p=calloc(1,11);p->length=3;
                 open_cfw_cordio_attc_send_message(1,1,5,p,0);
                 assert(exec_callbacks==1&&exec_status==0x77);}

                main_cb.bearer[0].mtu=23;
                open_cfw_cordio_attc_read_request(1,0x4455);
                assert(last_msg->header.event==5);
                assert(((uint8_t*)last_msg->packet)[8]==0x0A);
                assert(((uint8_t*)last_msg->packet)[9]==0x55);
                free(last_msg->packet);free(last_msg);
                open_cfw_cordio_attc_write_request(1,0x1122,2,value);
                assert(last_msg->header.event==9);
                assert(((uint8_t*)last_msg->packet)[11]==0xAA);
                free(last_msg->packet);free(last_msg);

                open_cfw_cordio_attc_cancel_request(1);
                assert(last_msg->header.event==19);
                assert(last_msg->packet==NULL);
                free(last_msg);

                main_cb.handle=0;main_cb.bearer[0].control=0x10;
                open_cfw_cordio_attc_indication_confirm(0);assert(l2c_sends==1);
                open_cfw_cordio_attc_indication_confirm(1);assert(l2c_sends==2);
                assert((main_cb.bearer[0].control&0x10)==0);free(last_l2c);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temp=Path(directory); hp=temp/"harness.c"; exe=temp/"test"
            hp.write_text(harness)
            subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror",
                "-I",str(SOURCE_DIR),str(SOURCE),
                str(SOURCE_DIR / "runtime_cordio_attc_read.c"),
                str(SOURCE_DIR / "runtime_cordio_attc_write.c"),
                str(hp),"-o",str(exe)],check=True)
            subprocess.run([str(exe)],check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selectors=["ERROR_RESPONSE","MTU_RESPONSE","FIND_READ_RESPONSE","READ_RESPONSE",
            "WRITE_RESPONSE","READ_MULTI_VAR_RESPONSE","MULTI_VAR_NOTIFICATION","RESPONSE",
            "INDICATION","SEND_MESSAGE","FIND_INFO_REQUEST","READ_REQUEST","WRITE_REQUEST",
            "CANCEL_REQUEST","MTU_REQUEST","INDICATION_CONFIRM"]
        with tempfile.TemporaryDirectory() as directory:
            for selector in [None,*selectors]:
                command=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55",
                    "-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror",
                    "-I",str(SOURCE_DIR)]
                if selector: command.append(f"-DOPEN_CFW_ATTC_PROC_{selector}_ONLY=1")
                command += ["-c",str(SOURCE),"-o",str(Path(directory)/f"{selector or 'all'}.o")]
                subprocess.run(command,check=True)

if __name__=="__main__": unittest.main()

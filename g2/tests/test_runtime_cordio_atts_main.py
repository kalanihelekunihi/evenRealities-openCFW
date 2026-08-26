#!/usr/bin/env python3
"""Exercise the G2 Cordio ATT server owner/dispatcher runtime."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_main.c"


class CordioAttsMainSourceTests(unittest.TestCase):
    def test_host_owner_dispatch_hash_groups_and_public_helpers(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_main.h"

            struct open_cfw_cordio_atts_ind_connection open_cfw_cordio_atts_main_connections[3][3];
            struct open_cfw_cordio_wsf_queue_candidate open_cfw_cordio_atts_main_prepared_write_queues[4];
            struct open_cfw_cordio_wsf_queue_candidate open_cfw_cordio_atts_main_group_queue;
            struct open_cfw_cordio_atts_interface *open_cfw_cordio_atts_main_indication_interface;
            open_cfw_cordio_atts_message_callback_t open_cfw_cordio_atts_main_sign_message_callback;
            struct open_cfw_cordio_att_main_control_block open_cfw_cordio_atts_main_control_blocks[3];
            struct open_cfw_cordio_atts_interface *open_cfw_cordio_atts_main_server_interface;
            uint8_t open_cfw_cordio_atts_main_handler_id=7,open_cfw_cordio_atts_main_error_test;
            uint8_t open_cfw_cordio_atts_main_hashable_next_value;
            void (*open_cfw_cordio_atts_main_application_callback)(struct open_cfw_cordio_att_event *);
            open_cfw_cordio_atts_processor_t open_cfw_cordio_atts_main_processor_table[18];
            uint8_t open_cfw_cordio_atts_main_minimum_pdu_length[18];
            open_cfw_cordio_atts_authorization_callback_t open_cfw_cordio_atts_authorization_callback;
            uint8_t open_cfw_cordio_atts_database_hash_uuid[2]={0x2a,0x2b};
            static struct open_cfw_cordio_att_configuration config={5,247,30,3};
            struct open_cfw_cordio_att_configuration *open_cfw_cordio_att_configuration=&config;
            static uint8_t output[300],last_reason,last_slot,csf_error;
            static uint16_t output_len,idle_mask;
            static unsigned sends,sets_idle,timer_starts,timer_stops,locks,unlocks,frees;
            static unsigned proc_calls,msg_calls,ctrl_calls,conn_calls,sign_calls,app_calls,asserts,cmacs;
            static uint8_t *cmac_message;
            static struct open_cfw_cordio_atts_attribute attrs[4];
            static struct open_cfw_cordio_atts_group groups[3];
            static uint8_t uuids[4][2]={{0x00,0x28},{0x03,0x28},{0x99,0x2a},{0x2a,0x2b}};
            static uint8_t values[4][20]={{0x0a,0x18},{1,2,3},{4,5},{0}};
            static uint16_t lengths[4]={2,3,2,16};

            static void proc(struct open_cfw_cordio_atts_connection_control_block *c,uint16_t n,uint8_t *p){assert(c&&n==3&&p[8]==0x0a);proc_calls++;}
            static void msg(void *p){assert(p);msg_calls++;}
            static void signmsg(void *p){assert(p);sign_calls++;}
            static void ctrl(struct open_cfw_cordio_wsf_message_header *p){assert(p);ctrl_calls++;}
            static void conn(struct open_cfw_cordio_att_main_control_block *m,struct open_cfw_cordio_dm_event *e){assert(m&&e);conn_calls++;}
            static void app(struct open_cfw_cordio_att_event *e){assert(e->header.event==0x15&&e->value_length==16);app_calls++;}
            static struct open_cfw_cordio_atts_interface interface={0,ctrl,msg,conn};

            uint8_t open_cfw_cordio_dm_connection_in_use(uint8_t id){return id>=1&&id<=3;}
            uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t h){return h==0x40?1:0;}
            uint16_t open_cfw_cordio_dm_connection_check_idle(uint8_t id){assert(id==1);return 4;}
            void open_cfw_cordio_dm_connection_set_idle(uint8_t id,uint16_t mask,uint8_t idle){assert(id==1);sets_idle++;idle_mask=mask;last_reason=idle;}
            uint8_t open_cfw_cordio_security_cmac(uint8_t *key,uint8_t *message,uint16_t n,uint8_t handler,uint16_t param,uint8_t event){assert(key&&message&&n>0&&handler==7&&param==0&&event==0x24);cmacs++;cmac_message=message;return 1;}
            uint8_t open_cfw_cordio_atts_csf_act_client_state(uint16_t h,uint8_t op,uint8_t *p){assert(h==0x40&&op==p[8]);return csf_error;}
            void open_cfw_cordio_atts_csf_set_hash_update_status(uint8_t s){last_reason=s;}
            struct open_cfw_cordio_atts_attribute *open_cfw_cordio_atts_find_by_handle(uint16_t h,struct open_cfw_cordio_atts_group **g){if(h<0x10||h>0x13)return 0;*g=&groups[0];return &attrs[h-0x10];}
            uint16_t open_cfw_cordio_atts_find_uuid_in_range(uint16_t s,uint16_t e,uint8_t n,uint8_t *u,struct open_cfw_cordio_atts_attribute **a,struct open_cfw_cordio_atts_group **g){(void)s;(void)e;assert(n==2);for(unsigned i=0;i<4;i++)if(attrs[i].uuid[0]==u[0]&&attrs[i].uuid[1]==u[1]){*a=&attrs[i];*g=&groups[0];return (uint16_t)(0x10+i);}return 0;}
            void *open_cfw_cordio_att_message_allocate(uint16_t n){assert(n<=sizeof(output));memset(output,0,sizeof(output));return output;}
            void open_cfw_cordio_att_l2c_data_request(struct open_cfw_cordio_att_main_control_block *m,uint8_t s,uint16_t n,uint8_t *p){assert(m&&p==output);sends++;last_slot=s;output_len=n;}
            void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t n){return calloc(1,n?n:1);}
            void open_cfw_cordio_wsf_buffer_free_candidate(void *p){frees++;free(p);}
            void open_cfw_cordio_wsf_task_lock(void){locks++;}
            void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
            void open_cfw_cordio_wsf_timer_start_seconds(struct open_cfw_cordio_wsf_timer *t,uint32_t s){assert(t&&s==5);timer_starts++;}
            void open_cfw_cordio_wsf_timer_stop(struct open_cfw_cordio_wsf_timer *t){timer_stops++;t->started=0;}
            void open_cfw_cordio_wsf_assert_candidate(const char *f,uint16_t l){(void)f;(void)l;asserts++;}
            void *open_cfw_cordio_wsf_queue_dequeue_candidate(struct open_cfw_cordio_wsf_queue_candidate *q){void *p=q->head;if(p){q->head=*(void **)p;if(!q->head)q->tail=0;}return p;}
            void open_cfw_cordio_wsf_queue_insert_candidate(struct open_cfw_cordio_wsf_queue_candidate *q,void *e,void *prev){if(prev){*(void **)e=*(void **)prev;*(void **)prev=e;}else{*(void **)e=q->head;q->head=e;}if(!*(void **)e)q->tail=e;}
            void open_cfw_cordio_wsf_queue_remove_candidate(struct open_cfw_cordio_wsf_queue_candidate *q,void *e,void *prev){if(prev)*(void **)prev=*(void **)e;else q->head=*(void **)e;if(q->tail==e)q->tail=prev;*(void **)e=0;}

            static void put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
            int main(void){
                uint8_t packet[20]={0},new_value[3]={7,8,9},*got=0;
                uint16_t got_len=0;
                struct open_cfw_cordio_wsf_message_header message={0};
                struct open_cfw_cordio_dm_event dm={0};
                struct open_cfw_cordio_atts_connection_control_block ccb={0};
                struct open_cfw_cordio_sec_cmac_message cmac={0};
                uint8_t cipher[16],*plain;
                struct {void *next;uint32_t x;} *w1,*w2;
                memset(open_cfw_cordio_atts_main_connections,0,sizeof(open_cfw_cordio_atts_main_connections));
                memset(open_cfw_cordio_atts_main_control_blocks,0,sizeof(open_cfw_cordio_atts_main_control_blocks));
                for(unsigned i=0;i<4;i++){attrs[i].uuid=uuids[i];attrs[i].value=values[i];attrs[i].length=&lengths[i];attrs[i].maximum_length=20;attrs[i].permissions=1;}
                groups[0].attributes=attrs;groups[0].start_handle=0x10;groups[0].end_handle=0x13;
                open_cfw_cordio_atts_initialize();
                for(unsigned i=0;i<3;i++)for(unsigned s=0;s<3;s++){struct open_cfw_cordio_atts_ind_connection *c=&open_cfw_cordio_atts_main_connections[i][s];assert(c->main==&open_cfw_cordio_atts_main_control_blocks[i]&&c->connection_id==i+1&&c->slot==s);}
                open_cfw_cordio_atts_main_indication_interface=&interface;open_cfw_cordio_atts_main_sign_message_callback=signmsg;open_cfw_cordio_atts_main_application_callback=app;
                assert(open_cfw_cordio_atts_ind_connection_by_id(1,2)==&open_cfw_cordio_atts_main_connections[0][2]);
                assert(open_cfw_cordio_atts_ind_connection_by_id(0,0)==0);
                assert(open_cfw_cordio_atts_ind_connection_by_handle(0x40,1)==&open_cfw_cordio_atts_main_connections[0][1]);
                assert(open_cfw_cordio_atts_ind_connection_by_handle(0x41,0)==0);

                open_cfw_cordio_atts_main_control_blocks[0].connection_id=1;open_cfw_cordio_atts_main_control_blocks[0].bearer[0].mtu=23;
                ccb.main=&open_cfw_cordio_atts_main_control_blocks[0];ccb.connection_id=1;ccb.slot=0;
                open_cfw_cordio_atts_main_processor_table[5]=proc;open_cfw_cordio_atts_main_minimum_pdu_length[5]=3;
                packet[8]=0x0a;put16(packet+9,0x10);open_cfw_cordio_atts_data_callback(0x40,3,packet);assert(proc_calls==1);
                open_cfw_cordio_atts_data_callback(0x40,0,packet);assert(proc_calls==1);
                csf_error=0x12;open_cfw_cordio_atts_data_callback(0x40,3,packet);assert(output[8]==1&&output[9]==0x0a&&output[10]==0x10&&output[12]==0x12);csf_error=0;
                packet[8]=0x04;open_cfw_cordio_atts_data_callback(0x40,3,packet);assert(output[12]==6);
                open_cfw_cordio_atts_error_response(&open_cfw_cordio_atts_main_control_blocks[0],2,8,0x1234,7);assert(last_slot==2&&output_len==5&&output[10]==0x34&&output[11]==0x12);

                message.parameter=1;message.event=0x20;open_cfw_cordio_atts_message_callback(&message);assert(sets_idle==1&&idle_mask==4&&last_reason==0);
                message.event=0x21;open_cfw_cordio_atts_message_callback(&message);assert(msg_calls==1);
                message.event=0x23;open_cfw_cordio_atts_message_callback(&message);assert(sign_calls==1);
                open_cfw_cordio_atts_l2c_control_callback(&message);assert(ctrl_calls==1);

                w1=calloc(1,sizeof(*w1));w2=calloc(1,sizeof(*w2));w1->next=w2;open_cfw_cordio_atts_main_prepared_write_queues[1].head=w1;open_cfw_cordio_atts_main_prepared_write_queues[1].tail=w2;
                open_cfw_cordio_atts_clear_prepared_writes(&ccb);assert(frees==2);
                open_cfw_cordio_atts_discovery_busy(&ccb);assert(timer_starts==1&&sets_idle==2);
                dm.header.event=0x28;open_cfw_cordio_atts_connection_callback(&open_cfw_cordio_atts_main_control_blocks[0],&dm);assert(timer_stops==3&&conn_calls==1);

                groups[1].start_handle=0x30;groups[2].start_handle=0x20;open_cfw_cordio_atts_main_group_queue.head=0;open_cfw_cordio_atts_main_group_queue.tail=0;
                open_cfw_cordio_atts_add_group(&groups[1]);open_cfw_cordio_atts_add_group(&groups[2]);open_cfw_cordio_atts_add_group(&groups[0]);
                assert(open_cfw_cordio_atts_main_group_queue.head==&groups[0]&&groups[0].next==&groups[2]&&groups[2].next==&groups[1]);
                open_cfw_cordio_atts_remove_group(0x20);assert(groups[0].next==&groups[1]);
                open_cfw_cordio_atts_remove_group(0x99);assert(locks==5&&unlocks==5&&last_reason==1);

                assert(open_cfw_cordio_atts_set_attribute(0x12,3,new_value)==0&&lengths[2]==2&&values[2][0]==7);
                attrs[2].settings=8;assert(open_cfw_cordio_atts_set_attribute(0x12,3,new_value)==0&&lengths[2]==3);
                assert(open_cfw_cordio_atts_get_attribute(0x12,&got_len,&got)==0&&got_len==3&&got==values[2]);
                assert(open_cfw_cordio_atts_get_attribute(0x99,&got_len,&got)==0x0a);
                open_cfw_cordio_atts_error_test(9);assert(open_cfw_cordio_atts_main_error_test==9);

                assert(open_cfw_cordio_atts_is_hashable_attribute(&attrs[0])==6);
                assert(open_cfw_cordio_atts_is_hashable_attribute(&attrs[1])==7);
                assert(open_cfw_cordio_atts_is_hashable_attribute(&attrs[2])==0);
                open_cfw_cordio_atts_main_group_queue.head=&groups[0];groups[0].next=0;open_cfw_cordio_atts_calculate_database_hash();assert(cmacs==1&&cmac_message);free(cmac_message);cmac_message=0;

                for(unsigned i=0;i<16;i++)cipher[i]=(uint8_t)i;plain=malloc(1);cmac.ciphertext=cipher;cmac.plaintext=plain;
                open_cfw_cordio_atts_process_database_hash_update(&cmac);assert(cmac.plaintext==0&&cipher[0]==15&&cipher[15]==0&&app_calls==1&&last_reason==0);
                struct open_cfw_cordio_atts_pending_database_hash_response *pending=calloc(1,sizeof(*pending));pending->start_handle=0x10;pending->handle=0x13;open_cfw_cordio_atts_main_control_blocks[0].pending_database_hash_response=pending;
                open_cfw_cordio_atts_check_pending_database_hash_read_response();assert(open_cfw_cordio_atts_main_control_blocks[0].pending_database_hash_response==0&&output[8]==9&&output[10]==0x13);
                assert(asserts==0&&sends>=4);
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
            ], check=True, text=True)
            subprocess.run([str(binary)], check=True)

    def test_isolated_arm_leaves(self) -> None:
        selectors = (
            "DATA", "CONNECTION", "MESSAGE", "CONTROL", "ERROR_RESPONSE",
            "CLEAR_WRITES", "DISCOVERY_BUSY", "PROCESS_HASH", "CHECK_HASH",
            "HASHABLE", "CCB_ID", "CCB_HANDLE", "INITIALIZE", "HASH_STRING",
            "CALCULATE_HASH", "ADD_GROUP", "REMOVE_GROUP", "AUTHOR_REGISTER",
            "SET_ATTRIBUTE", "GET_ATTRIBUTE", "ERROR_TEST",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_MAIN_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_MAIN_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()

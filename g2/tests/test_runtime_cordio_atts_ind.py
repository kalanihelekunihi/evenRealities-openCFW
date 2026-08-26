#!/usr/bin/env python3
"""Exercise the G2 Cordio ATT server indication/notification runtime."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_atts_ind.c"


class CordioAttsIndSourceTests(unittest.TestCase):
    def test_host_indication_notification_state_machine(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_atts_ind.h"

            struct open_cfw_cordio_atts_ind_connection
                open_cfw_cordio_atts_ind_connections[3][3];
            uint8_t open_cfw_cordio_att_handler_id = 9;
            uint8_t open_cfw_cordio_atts_service_changed_uuid[2] = {0x05, 0x2a};
            void *open_cfw_cordio_atts_indication_interface;
            static struct open_cfw_cordio_att_configuration configuration = {
                0, 247, 30, 3
            };
            struct open_cfw_cordio_att_configuration
                *open_cfw_cordio_att_configuration = &configuration;

            static struct open_cfw_cordio_att_main_control_block main_cb[3];
            static struct open_cfw_cordio_atts_attribute service_attribute;
            static struct open_cfw_cordio_atts_group service_group;
            static uint8_t service_uuid[2] = {0x05, 0x2a};
            static unsigned callback_count, l2c_count, timer_starts, timer_stops;
            static unsigned locks, unlocks, message_frees, att_frees, sends;
            static unsigned lookup_count, aware_sets;
            static uint8_t callback_connection, callback_event, callback_status;
            static uint16_t callback_handle, callback_mtu, l2c_length;
            static uint8_t l2c_slot, aware = 1, aware_state = 1;
            static void *last_sent;

            void open_cfw_cordio_att_execute_callback(
                uint8_t id, uint8_t event, uint16_t handle,
                uint8_t status, uint16_t mtu
            ) {
                callback_count++; callback_connection=id; callback_event=event;
                callback_handle=handle; callback_status=status; callback_mtu=mtu;
            }
            uint16_t open_cfw_cordio_att_message_parameter(uint8_t id, uint8_t slot) {
                return (uint16_t)(((uint16_t)slot << 8) | id);
            }
            void open_cfw_cordio_att_decode_message_parameter(
                uint16_t parameter, uint8_t *id, uint8_t *slot
            ) { *id=(uint8_t)parameter; *slot=(uint8_t)(parameter >> 8); }
            void open_cfw_cordio_wsf_timer_start_seconds(
                struct open_cfw_cordio_wsf_timer *timer, uint32_t seconds
            ) { assert(seconds==30); timer_starts++; timer->started=1; }
            void open_cfw_cordio_wsf_timer_stop(
                struct open_cfw_cordio_wsf_timer *timer
            ) { timer_stops++; timer->started=0; }
            struct open_cfw_cordio_atts_ind_connection *
            open_cfw_cordio_atts_ind_connection_by_id(uint8_t id, uint8_t slot) {
                lookup_count++;
                if (id==0 || id>3 || slot>2) return 0;
                return &open_cfw_cordio_atts_ind_connections[id-1][slot];
            }
            void open_cfw_cordio_wsf_task_lock(void) { locks++; }
            void open_cfw_cordio_wsf_task_unlock(void) { unlocks++; }
            void *open_cfw_cordio_wsf_message_allocate(uint16_t length) {
                return calloc(1, length);
            }
            void open_cfw_cordio_wsf_message_send(uint8_t handler, void *message) {
                assert(handler==9); sends++; last_sent=message;
            }
            uint8_t open_cfw_cordio_atts_csf_is_client_change_aware(
                uint8_t id, uint16_t handle
            ) { assert(id>=1 && handle!=0); return aware; }
            uint8_t open_cfw_cordio_atts_csf_get_change_aware_state(uint8_t id) {
                assert(id==1); return aware_state;
            }
            void open_cfw_cordio_atts_csf_set_clients_change_awareness_state(
                uint8_t id, uint8_t state
            ) { assert(id==1 && state==0); aware_sets++; aware_state=state; }
            void open_cfw_cordio_att_l2c_data_request(
                struct open_cfw_cordio_att_main_control_block *main,
                uint8_t slot, uint16_t length, uint8_t *packet
            ) { assert(main!=0 && packet!=0); l2c_count++; l2c_slot=slot; l2c_length=length; }
            void *open_cfw_cordio_att_message_allocate(uint16_t length) {
                return calloc(1, length);
            }
            void open_cfw_cordio_wsf_message_free(void *message) {
                message_frees++; free(message);
            }
            void open_cfw_cordio_att_message_free(void *message, uint8_t opcode) {
                assert(opcode==0x1b || opcode==0x1d); att_frees++;
                free((uint8_t *)message - 11);
            }
            struct open_cfw_cordio_atts_attribute *open_cfw_cordio_atts_find_by_handle(
                uint16_t handle, struct open_cfw_cordio_atts_group **group
            ) {
                if (handle != 0x1234) return 0;
                *group=&service_group; return &service_attribute;
            }

            static struct open_cfw_cordio_atts_ind_packet *packet(
                uint8_t opcode, uint16_t handle, uint16_t value_length
            ) {
                struct open_cfw_cordio_atts_ind_packet *p=calloc(1,11+value_length);
                assert(p); p->length=(uint16_t)(3+value_length); p->handle=handle;
                p->pdu[0]=opcode; p->pdu[1]=(uint8_t)handle;
                p->pdu[2]=(uint8_t)(handle>>8); return p;
            }
            static void reset_callbacks(void) {
                callback_count=0; callback_connection=0; callback_event=0;
                callback_handle=0; callback_status=0; callback_mtu=0;
            }

            int main(void) {
                struct open_cfw_cordio_atts_ind_connection *c;
                struct open_cfw_cordio_atts_ind_packet *p;
                struct open_cfw_cordio_atts_ind_api_message api;
                struct open_cfw_cordio_wsf_message_header control;
                struct open_cfw_cordio_dm_event dm;
                uint8_t *zero_storage, *zero_value;
                uint8_t value[4]={1,2,3,4};
                unsigned before;

                memset(open_cfw_cordio_atts_ind_connections,0,
                    sizeof(open_cfw_cordio_atts_ind_connections));
                memset(main_cb,0,sizeof(main_cb));
                for (unsigned id=0;id<3;id++) {
                    main_cb[id].connection_id=(uint8_t)(id+1);
                    for (unsigned slot=0;slot<3;slot++) {
                        c=&open_cfw_cordio_atts_ind_connections[id][slot];
                        c->main=&main_cb[id]; c->connection_id=(uint8_t)(id+1);
                        c->slot=(uint8_t)slot; main_cb[id].bearer[slot].mtu=247;
                    }
                }
                service_attribute.uuid=service_uuid;

                c=&open_cfw_cordio_atts_ind_connections[0][0];
                p=packet(OPEN_CFW_ATTS_IND_VALUE_INDICATION,0x100,1);
                assert(open_cfw_cordio_atts_ind_pending(c,p)==0);
                c->pending_indication_handle=0x99;
                assert(open_cfw_cordio_atts_ind_pending(c,p)==1);
                c->pending_indication_handle=0;
                p->pdu[0]=OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION;
                for (unsigned i=0;i<10;i++)
                    open_cfw_cordio_atts_ind_set_pending_notification(c,(uint16_t)(i+1));
                assert(open_cfw_cordio_atts_ind_pending(c,p)==1);
                p->handle=5; assert(open_cfw_cordio_atts_ind_pending(c,p)==1);
                c->pending_notification_handle[9]=0;
                p->handle=99; assert(open_cfw_cordio_atts_ind_pending(c,p)==0);
                free(p);

                c->pending_indication_handle=0x80;
                reset_callbacks();
                open_cfw_cordio_atts_ind_notification_callback(1,c,0xa7);
                assert(callback_count==10 && callback_handle==9);
                assert(callback_event==OPEN_CFW_ATTS_IND_VALUE_CONFIRM_EVENT);
                assert(callback_status==0xa7 && c->pending_indication_handle==0);
                for (unsigned i=0;i<10;i++) assert(c->pending_notification_handle[i]==0);

                p=packet(OPEN_CFW_ATTS_IND_VALUE_INDICATION,0x234,2);
                open_cfw_cordio_atts_ind_setup_message(c,1,0,p);
                assert(l2c_count==1 && l2c_slot==0 && l2c_length==5);
                assert(c->pending_indication_handle==0x234);
                assert(c->outstanding_indication_handle==0x234 && timer_starts==1);
                assert(c->indication_timer.message.event==OPEN_CFW_ATTS_IND_TIMEOUT_EVENT);
                assert(c->indication_timer.message.parameter==1);
                main_cb[0].bearer[0].control=OPEN_CFW_ATTS_IND_FLOW_DISABLED;
                p->pdu[0]=OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION; p->handle=0x301;
                open_cfw_cordio_atts_ind_setup_message(c,1,0,p);
                assert(c->pending_notification_handle[0]==0x301);
                main_cb[0].bearer[0].control=0;
                reset_callbacks();
                open_cfw_cordio_atts_ind_setup_message(c,1,0,p);
                assert(callback_count==1 && callback_handle==0x301 && callback_status==0);
                p->pdu[0]=OPEN_CFW_ATTS_IND_MULTIPLE_VALUE_NOTIFICATION;
                open_cfw_cordio_atts_ind_setup_message(c,1,0,p);
                assert(callback_event==OPEN_CFW_ATTS_IND_MULTIPLE_CONFIRM_EVENT);
                free(p);

                memset(&api,0,sizeof(api)); api.header.event=OPEN_CFW_ATTS_IND_API_EVENT;
                api.header.parameter=0; api.packet=packet(0x1b,0x40,1);
                before=message_frees; open_cfw_cordio_atts_ind_message_callback(&api);
                assert(message_frees==before+1);
                api.header.parameter=1; api.packet=packet(0x1d,0x41,1);
                c->pending_indication_handle=0x33; reset_callbacks();
                open_cfw_cordio_atts_ind_message_callback(&api);
                assert(callback_count==1 && callback_status==OPEN_CFW_ATTS_IND_ERR_OVERFLOW);
                c->pending_indication_handle=0;
                api.packet=packet(0x1b,0x42,1);
                before=l2c_count; open_cfw_cordio_atts_ind_message_callback(&api);
                assert(l2c_count==before+1); free(api.packet);
                api.header.event=OPEN_CFW_ATTS_IND_TIMEOUT_EVENT;
                api.header.parameter=(uint16_t)(2U<<8|1U); before=lookup_count;
                reset_callbacks(); open_cfw_cordio_atts_ind_message_callback(&api);
                assert(lookup_count==before+1 && api.header.parameter==1);
                assert(callback_count==0);

                memset(&control,0,sizeof(control)); control.parameter=1;
                c->pending_notification_handle[0]=0x77;
                open_cfw_cordio_atts_ind_control_callback(&control);
                assert(callback_handle==0x77 && c->pending_notification_handle[0]==0);

                memset(&dm,0,sizeof(dm)); dm.header.event=OPEN_CFW_ATTS_IND_CONNECTION_CLOSE_EVENT;
                dm.header.status=7; c->outstanding_indication_handle=0x44;
                c->pending_indication_handle=0x45; reset_callbacks(); before=timer_stops;
                open_cfw_cordio_atts_ind_connection_callback(&main_cb[0],&dm);
                assert(timer_stops==before+1 && callback_status==(uint8_t)(7+0xa0));
                dm.header.status=0; dm.reason=8; c->pending_indication_handle=0x46;
                open_cfw_cordio_atts_ind_connection_callback(&main_cb[0],&dm);
                assert(callback_status==(uint8_t)(8+0xa0));
                main_cb[0].connection_id=0; before=callback_count;
                open_cfw_cordio_atts_ind_connection_callback(&main_cb[0],&dm);
                assert(callback_count==before); main_cb[0].connection_id=1;

                reset_callbacks(); sends=0; last_sent=0;
                open_cfw_cordio_atts_handle_value_indication_notification(
                    1,0x500,0,4,value,OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION,0);
                assert(locks==1 && unlocks==1 && sends==1 && last_sent);
                api=*(struct open_cfw_cordio_atts_ind_api_message *)last_sent;
                assert(api.header.parameter==1 && api.header.event==OPEN_CFW_ATTS_IND_API_EVENT);
                assert(api.packet->length==7 && api.packet->handle==0x500);
                assert(memcmp(&api.packet->pdu[3],value,4)==0);
                free(api.packet); free(last_sent); last_sent=0;
                main_cb[0].bearer[0].mtu=6;
                open_cfw_cordio_atts_handle_value_indication_notification(
                    1,0x501,0,4,value,0x1b,0);
                assert(callback_status==OPEN_CFW_ATTS_IND_ERR_MTU_EXCEEDED);
                main_cb[0].bearer[0].mtu=247;
                main_cb[0].bearer[0].control=OPEN_CFW_ATTS_IND_TRANSACTION_TIMEOUT;
                open_cfw_cordio_atts_handle_value_indication_notification(
                    1,0x502,0,4,value,0x1b,0);
                assert(callback_status==OPEN_CFW_ATTS_IND_ERR_TIMEOUT);
                main_cb[0].bearer[0].control=0; aware=0; before=sends;
                open_cfw_cordio_atts_handle_value_indication_notification(
                    1,0x503,0,4,value,0x1b,0);
                assert(sends==before); aware=1;

                zero_storage=calloc(1,15); assert(zero_storage); zero_value=zero_storage+11;
                memcpy(zero_value,value,4);
                open_cfw_cordio_atts_handle_value_notification_zero_copy(1,0x504,4,zero_value);
                assert(sends==before+1); api=*(struct open_cfw_cordio_atts_ind_api_message *)last_sent;
                assert((uint8_t *)api.packet==zero_storage && api.packet->pdu[3]==1);
                free(last_sent); free(zero_storage); last_sent=0;
                zero_storage=calloc(1,15); zero_value=zero_storage+11;
                before=att_frees; open_cfw_cordio_atts_handle_value_notification_zero_copy(0,0x505,4,zero_value);
                assert(att_frees==before+1);

                c->outstanding_indication_handle=0x1234;
                c->pending_indication_handle=0x1234; aware_state=1;
                reset_callbacks(); before=timer_stops;
                open_cfw_cordio_atts_process_value_confirmation(c,0,0);
                assert(timer_stops==before+1 && aware_sets==1 && callback_handle==0x1234);
                assert(c->outstanding_indication_handle==0 && c->pending_indication_handle==0);
                c->outstanding_indication_handle=0x1234; c->pending_indication_handle=0x1234;
                main_cb[0].bearer[0].control=OPEN_CFW_ATTS_IND_FLOW_DISABLED;
                before=callback_count; open_cfw_cordio_atts_process_value_confirmation(c,0,0);
                assert(callback_count==before && c->pending_indication_handle==0x1234);
                main_cb[0].bearer[0].control=0;

                open_cfw_cordio_atts_ind_initialize();
                for (unsigned id=0;id<3;id++) for (unsigned slot=0;slot<3;slot++) {
                    c=&open_cfw_cordio_atts_ind_connections[id][slot];
                    assert(c->indication_timer.handler_id==9);
                    assert(c->indication_timer.message.parameter==id+1);
                }
                sends=0; open_cfw_cordio_atts_handle_value_indication(1,0x601,4,value);
                assert(sends==1); api=*(struct open_cfw_cordio_atts_ind_api_message *)last_sent;
                assert(api.packet->pdu[0]==OPEN_CFW_ATTS_IND_VALUE_INDICATION);
                free(api.packet); free(last_sent);
                sends=0; open_cfw_cordio_atts_handle_value_notification(1,0x602,4,value);
                assert(sends==1); api=*(struct open_cfw_cordio_atts_ind_api_message *)last_sent;
                assert(api.packet->pdu[0]==OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION);
                free(api.packet); free(last_sent);
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
            "PENDING", "SET_PENDING", "EXEC_CALLBACK", "NOTIFICATION_CALLBACK",
            "SETUP", "CONNECTION_CALLBACK", "MESSAGE_CALLBACK", "CONTROL_CALLBACK",
            "HANDLE", "CONFIRM", "INITIALIZE", "INDICATION", "NOTIFICATION",
            "INDICATION_ZERO_COPY", "NOTIFICATION_ZERO_COPY",
        )
        with tempfile.TemporaryDirectory() as directory:
            for selector in selectors:
                subprocess.run([
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-I", str(SOURCE_DIR),
                    "-DOPEN_CFW_ATTS_IND_PRODUCTION=1",
                    f"-DOPEN_CFW_ATTS_IND_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()

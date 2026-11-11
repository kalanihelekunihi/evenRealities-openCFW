/**
 * Copyright (c) 2012 - 2021, Nordic Semiconductor ASA
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 *
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 *
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

/* R1 connection adapter derived from the pinned Nordic NUS on_connect
 * skeleton and stock application 0x7ccb4. The explicit local frame preserves
 * the stock escaping record and context-output addresses with the manifest
 * compiler; private padding is never read. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "nrf_sdh_ble.h"
#define SVCALL_AS_NORMAL_FUNCTION
#include "ble_gatts.h"
extern uint32_t r1_dfu_value_get(uint32_t,uint32_t,void *);
extern uint32_t r1_native_bae8_context_get(void *,uint32_t,void *volatile *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern _Bool ble_srv_is_notification_enabled(const uint8_t *);
struct record {
    uint8_t type,pad0[3];
    void *service;
    uint16_t connection;
    uint8_t pad1[2];
    void *client;
    const void *data;
    uint16_t length;
    uint8_t pad2[2];
};
_Static_assert(sizeof(struct record)==24,"stock event record");
_Static_assert(offsetof(struct record,service)==4,"stock service member");
_Static_assert(offsetof(struct record,connection)==8,"stock connection member");
_Static_assert(offsetof(struct record,client)==12,"stock client member");
_Static_assert(offsetof(struct record,data)==16,"stock data member");
_Static_assert(offsetof(struct record,length)==20,"stock length member");
typedef void (*handler)(struct record *);
static uint16_t half(const volatile uint8_t *p)
{ return *(const volatile uint16_t *)p; }
static handler callback(const volatile uint8_t *service)
{ return *(handler volatile const *)(service+44); }
static const char ring[]="[RING]Link context for 0x%02X connection handle could not be fetched.";
static const char sdk[]="Link context for 0x%02X connection handle could not be fetched.";
struct connect_frame {
    void *volatile client;
    ble_gatts_value_t value;
    struct record out;
    uint32_t reserved;
    uint8_t cccd[2];
};
_Static_assert(SD_BLE_GATTS_VALUE_GET==173,"stock SVC number");
_Static_assert(sizeof(ble_gatts_value_t)==8,"stock value descriptor size");
_Static_assert(offsetof(struct connect_frame,value)==4,"stock GATTS value");
_Static_assert(offsetof(struct connect_frame,out)==12,"stock callback record");
_Static_assert(offsetof(struct connect_frame,cccd)==40,"stock CCCD bytes");
void r1_bae8_connection_event_plan_build(void *service,ble_evt_t const *event)
{
    volatile uint8_t *s=service;
    const volatile uint8_t *e=(const volatile uint8_t *)event;
    struct connect_frame frame __attribute__((aligned(8)));
    frame.client=0;
    uint32_t connection=half(e+4);
    void *storage=*(void *volatile *)(s+40);
    uint32_t status=r1_native_bae8_context_get(storage,connection,&frame.client);
    if (status) {
        if ((r1_structured_log_mode_get()&1u)||
            (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04400000,ring,ring,(uint32_t)half(e+4));
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,sdk,(uint32_t)half(e+4));
    }
    frame.value.p_value=frame.cccd;
    frame.value.len=2;
    frame.value.offset=0;
    uint32_t handle=half(s+10);
    connection=half(e+4);
    status=r1_dfu_value_get(connection,handle,&frame.value);
    if (!status && callback(s) &&
        ble_srv_is_notification_enabled(frame.value.p_value) && frame.client)
        ((volatile uint8_t *)frame.client)[0]=1;
    handle=half(s+26);
    connection=half(e+4);
    status=r1_dfu_value_get(connection,handle,&frame.value);
    if (!status) {
        if (!callback(s)) return;
        if (ble_srv_is_notification_enabled(frame.value.p_value) && frame.client)
            ((volatile uint8_t *)frame.client)[1]=1;
    }
    if (!callback(s)) return;
    memset(&frame.out,0,sizeof(frame.out));
    frame.out.type=0;
    frame.out.service=service;
    frame.out.connection=half(e+4);
    frame.out.client=frame.client;
    callback(s)(&frame.out);
}

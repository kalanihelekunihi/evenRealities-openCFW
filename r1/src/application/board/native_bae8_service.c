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

/* R1 service configuration, stock application 0x529bc. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "ble.h"
#include "ble_srv_common.h"
struct service_frame {
    ble_add_char_params_t parameters;
    ble_uuid128_t base;
    ble_uuid_t uuid;
};
_Static_assert(sizeof(ble_add_char_params_t)==32,"stock characteristic parameters");
_Static_assert(offsetof(struct service_frame,base)==32,"stock base UUID offset");
_Static_assert(offsetof(struct service_frame,uuid)==48,"stock service UUID offset");
static const ble_uuid128_t base_uuid={{0x1f,0x9d,0x32,0xf7,0xf1,0x3a,0x65,0x8e,0x03,0x45,0x05,0x4f,0,0,0xe8,0xba}};
__attribute__((noinline)) static void parameters_init(ble_add_char_params_t *p,uint32_t uuid_type,uint32_t tx)
{
    for (uint32_t i=0;i<sizeof(*p);i++) ((volatile uint8_t *)p)[i]=0;
    p->uuid=(uint16_t)uuid_type;
    p->uuid_type=uuid_type>>16;
    p->max_len=244;p->init_len=1;p->is_var_len=true;
    p->read_access=SEC_OPEN;p->write_access=SEC_OPEN;
    if (tx) {p->char_props.notify=1;p->cccd_write_access=SEC_OPEN;}
    else p->char_props.write_wo_resp=1;
}
uint32_t r1_bae8_service_configuration(void *service,const void *configuration)
{
    struct service_frame frame __attribute__((aligned(8)));
    ((volatile uint8_t *)frame.base.uuid128)[0]=base_uuid.uuid128[0];
    ((volatile uint8_t *)frame.base.uuid128)[1]=base_uuid.uuid128[1];
    ((volatile uint8_t *)frame.base.uuid128)[2]=base_uuid.uuid128[2];
    ((volatile uint8_t *)frame.base.uuid128)[3]=base_uuid.uuid128[3];
    ((volatile uint8_t *)frame.base.uuid128)[4]=base_uuid.uuid128[4];
    ((volatile uint8_t *)frame.base.uuid128)[5]=base_uuid.uuid128[5];
    ((volatile uint8_t *)frame.base.uuid128)[6]=base_uuid.uuid128[6];
    ((volatile uint8_t *)frame.base.uuid128)[7]=base_uuid.uuid128[7];
    ((volatile uint8_t *)frame.base.uuid128)[8]=base_uuid.uuid128[8];
    ((volatile uint8_t *)frame.base.uuid128)[9]=base_uuid.uuid128[9];
    ((volatile uint8_t *)frame.base.uuid128)[10]=base_uuid.uuid128[10];
    ((volatile uint8_t *)frame.base.uuid128)[11]=base_uuid.uuid128[11];
    ((volatile uint8_t *)frame.base.uuid128)[12]=base_uuid.uuid128[12];
    ((volatile uint8_t *)frame.base.uuid128)[13]=base_uuid.uuid128[13];
    ((volatile uint8_t *)frame.base.uuid128)[14]=base_uuid.uuid128[14];
    ((volatile uint8_t *)frame.base.uuid128)[15]=base_uuid.uuid128[15];
    if (!service || !configuration) return 14;
    volatile uint8_t *s=service;
    *(void *volatile *)(s+44)=*(void *volatile const *)configuration;
    uint32_t status=sd_ble_uuid_vs_add(&frame.base,(uint8_t *)service);
    if (status) return status;
    frame.uuid.type=s[0];
    frame.uuid.uuid=1;
    status=sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,&frame.uuid,(uint16_t *)(s+4));
    if (status) return status;
    for (uint32_t i=0;i<4;i++) {
        uint32_t offset=(i&1u) ? (i==1 ? 6 : 22) : (i==0 ? 14 : 30);
        parameters_init(&frame.parameters,(uint32_t)s[0]<<16 | (0x10+i),i&1u);
        status=characteristic_add(*(const volatile uint16_t *)(s+4),&frame.parameters,
                                  (ble_gatts_char_handles_t *)(s+offset));
        if (status) return status;
    }
    return status;
}

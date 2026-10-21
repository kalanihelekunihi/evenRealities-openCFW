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

/* R1 send-policy adaptation from authenticated pseudocode/disassembly. The
 * SDK HVX type/SVC identifier are reused; this is not a complete ble_nus_t. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "ble_gatts.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_native_bae8_context_get(void *,uint32_t,void *volatile *);
struct service_prefix {
    uint8_t reserved0[6];volatile uint16_t bc_handle;
    uint8_t reserved8[14];volatile uint16_t eus_handle;
    uint8_t reserved24[16];void *volatile link_storage;
};
_Static_assert(offsetof(struct service_prefix,bc_handle)==6,"stock BC value handle");
_Static_assert(offsetof(struct service_prefix,eus_handle)==22,"stock EUS value handle");
_Static_assert(offsetof(struct service_prefix,link_storage)==40,"stock link storage");
_Static_assert(sizeof(ble_gatts_hvx_params_t)==16,"stock HVX record size");
_Static_assert(offsetof(ble_gatts_hvx_params_t,p_len)==8,"stock HVX length pointer");
_Static_assert(offsetof(ble_gatts_hvx_params_t,p_data)==12,"stock HVX data pointer");
_Static_assert(SD_BLE_GATTS_HVX==174,"stock SoftDevice call number");
/* Preserve the stock full r0 value at SVC, including words wider than the
 * public uint16_t API's valid input range. Only the ABI glue is assembly. */
__attribute__((naked)) uint32_t r1_native_sd_ble_gatts_hvx(
    uint32_t connection __attribute__((unused)),
    const ble_gatts_hvx_params_t *parameters __attribute__((unused)))
{ __asm__ volatile ("svc %0\nbx lr" :: "I"(SD_BLE_GATTS_HVX) : "r0","memory"); }

#define TEXT(name,value) const char r1_bae8_##name[] __attribute__((section(".r1.bae8.log." #name),aligned(1)))=value
TEXT(invalid_ring,"[RING]conn_handle == BLE_CONN_HANDLE_INVALID");
TEXT(invalid_sdk,"conn_handle == BLE_CONN_HANDLE_INVALID");
TEXT(lookup_ring,"[RING]Link context for 0x%02X connection handle could not be fetched err_code = %d p_client = 0x%x");
TEXT(lookup_sdk,"Link context for 0x%02X connection handle could not be fetched err_code = %d p_client = 0x%x");
TEXT(bc_ring,"[RING]BC notification not enabled! conn_handle=0x%x, is_glasses_notification_enabled=%d");
TEXT(bc_sdk,"BC notification not enabled! conn_handle=0x%x, is_glasses_notification_enabled=%d");
TEXT(eus_ring,"[RING]EUS notification not enabled! conn_handle=0x%x, is_eus_notification_enabled=%d");
TEXT(eus_sdk,"EUS notification not enabled! conn_handle=0x%x, is_eus_notification_enabled=%d");
TEXT(length_ring,"[RING]*p_length > BLE_EUS_MAX_DATA_LEN");
TEXT(length_sdk,"*p_length > BLE_EUS_MAX_DATA_LEN");
TEXT(hvx_ring,"[RING]sd_ble_gatts_hvx failed: 0x%x, conn_handle=0x%x, is_eus=%d");
TEXT(hvx_sdk,"sd_ble_gatts_hvx failed: 0x%x, conn_handle=0x%x, is_eus=%d");

static void plain_log(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
}
uint32_t r1_native_bae8_send(void *service,const void *payload,volatile uint32_t *length_word,uint32_t connection,uint32_t flag)
{
    if (!service) return 14;
    struct service_prefix *view=service;
    void *volatile client=0;
    if (connection==0xffff) { plain_log(r1_bae8_invalid_ring,r1_bae8_invalid_sdk);return 5; }
    uint32_t status=r1_native_bae8_context_get(view->link_storage,connection,&client);
    if (status || !client) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04c00000,r1_bae8_lookup_ring,r1_bae8_lookup_ring,connection,status,(uint32_t)(uintptr_t)client);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_3(0x001c0001,r1_bae8_lookup_sdk,connection,status,(uint32_t)(uintptr_t)client);
        return 5;
    }
    uint32_t index=flag ? 1u : 0u;
    if (!((volatile uint8_t *)client)[index]) {
        const char *ring=flag ? r1_bae8_eus_ring : r1_bae8_bc_ring;
        const char *sdk=flag ? r1_bae8_eus_sdk : r1_bae8_bc_sdk;
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04800000,ring,ring,connection,(uint32_t)((volatile uint8_t *)client)[index]);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x001c0001,sdk,connection,(uint32_t)((volatile uint8_t *)client)[index]);
        return 8;
    }
    const volatile uint8_t *length_bytes=(const volatile uint8_t *)length_word;
    uint32_t length=(uint32_t)length_bytes[0]|((uint32_t)length_bytes[1]<<8);
    if (length>244) { plain_log(r1_bae8_length_ring,r1_bae8_length_sdk);return 7; }
    ble_gatts_hvx_params_t parameters;
    memset(&parameters,0,sizeof(parameters));
    parameters.handle=flag ? view->eus_handle : view->bc_handle;
    parameters.type=BLE_GATT_HVX_NOTIFICATION;
    parameters.p_len=(uint16_t *)(uintptr_t)length_word;
    parameters.p_data=payload;
    status=r1_native_sd_ble_gatts_hvx(connection,&parameters);
    if (status!=0 && status!=19) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04c00000,r1_bae8_hvx_ring,r1_bae8_hvx_ring,status,connection,flag);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_3(0x001c0001,r1_bae8_hvx_sdk,status,connection,flag);
    }
    return status;
}

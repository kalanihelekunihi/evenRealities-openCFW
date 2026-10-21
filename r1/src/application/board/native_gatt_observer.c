/**
 * Copyright (c) 2016 - 2021, Nordic Semiconductor ASA
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

/* R1 GATT adaptation: native event routing, unconditional data-length requests
 * and dual logging differ from the pinned Nordic module. Public ABI types and
 * initialization are supplied by unchanged attributable Nordic source. */
#include <stdint.h>
#include <string.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "nrf_ble_gatt.h"
#include "nrf_strerror.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void r1_sdk_gatt_link_init(nrf_ble_gatt_link_t *);
#define TEXT(name,value) const char r1_gatt_##name[] __attribute__((section(".r1.gatt.log." #name),aligned(1)))=value
TEXT(mtu_request_ring,"[RING]sd_ble_gattc_exchange_mtu_request() returned %s.");
TEXT(mtu_request_sdk,"sd_ble_gattc_exchange_mtu_request() returned %s.");
TEXT(mtu_reply_ring,"[RING]sd_ble_gatts_exchange_mtu_reply() returned %s.");
TEXT(mtu_reply_sdk,"sd_ble_gatts_exchange_mtu_reply() returned %s.");
TEXT(length_ring,"[RING]sd_ble_gap_data_length_update() (request) on connection 0x%x returned %s.");
TEXT(length_sdk,"sd_ble_gap_data_length_update() (request) on connection 0x%x returned %s.");
TEXT(octets_ring,"[RING]The requested TX/RX packet length is too long by %u/%u octets.");
TEXT(octets_sdk,"The requested TX/RX packet length is too long by %u/%u octets.");
TEXT(time_ring,"[RING]The requested combination of TX and RX packet lengths is too long by %u microseconds.");
TEXT(time_sdk,"The requested combination of TX and RX packet lengths is too long by %u microseconds.");
#define SVC2(name,number) __attribute__((naked)) uint32_t name(uint32_t a __attribute__((unused)),uint32_t b __attribute__((unused))) { __asm__ volatile("svc %0\nbx lr"::"I"(number):"r0","memory"); }
SVC2(r1_gatt_sd_mtu_request,SD_BLE_GATTC_EXCHANGE_MTU_REQUEST)
SVC2(r1_gatt_sd_mtu_reply,SD_BLE_GATTS_EXCHANGE_MTU_REPLY)
__attribute__((naked)) uint32_t r1_gatt_sd_length_update(uint32_t a __attribute__((unused)),const ble_gap_data_length_params_t *b __attribute__((unused)),ble_gap_data_length_limitation_t *c __attribute__((unused)))
{ __asm__ volatile("svc %0\nbx lr"::"I"(SD_BLE_GAP_DATA_LENGTH_UPDATE):"r0","memory"); }
_Static_assert(SD_BLE_GAP_DATA_LENGTH_UPDATE==144 && SD_BLE_GATTC_EXCHANGE_MTU_REQUEST==165 && SD_BLE_GATTS_EXCHANGE_MTU_REPLY==181,"native SVC contracts");
_Static_assert(sizeof(ble_gap_data_length_params_t)==8 && sizeof(ble_gap_data_length_limitation_t)==6,"native length records");
static void error_log(uint32_t status,const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04400000,ring,ring,nrf_strerror_get(status));
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x00030001,sdk,(uint32_t)(uintptr_t)nrf_strerror_get(status));
}
uint32_t r1_gatt_data_length_update(uint32_t connection,uint32_t length)
{
    ble_gap_data_length_params_t p={.max_rx_octets=(uint16_t)length,.max_tx_octets=(uint16_t)length,.max_rx_time_us=0,.max_tx_time_us=0};
    ble_gap_data_length_limitation_t limits={0};
    uint32_t status=r1_gatt_sd_length_update(connection,&p,&limits);
    if (status) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04800000,r1_gatt_length_ring,r1_gatt_length_ring,connection,nrf_strerror_get(status));
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x00030001,r1_gatt_length_sdk,connection,(uint32_t)(uintptr_t)nrf_strerror_get(status));
        if (limits.tx_payload_limited_octets || limits.rx_payload_limited_octets) {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04800000,r1_gatt_octets_ring,r1_gatt_octets_ring,(uint32_t)limits.tx_payload_limited_octets,(uint32_t)limits.rx_payload_limited_octets);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_2(0x00030001,r1_gatt_octets_sdk,limits.tx_payload_limited_octets,limits.rx_payload_limited_octets);
        }
        if (limits.tx_rx_time_limited_us) {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04400000,r1_gatt_time_ring,r1_gatt_time_ring,(uint32_t)limits.tx_rx_time_limited_us);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_1(0x00030001,r1_gatt_time_sdk,limits.tx_rx_time_limited_us);
        }
    }
    return status;
}
/* Raw byte reads preserve the native nonzero test even for mapped noncanonical
 * flag representations; stores use the SDK's bool fields. */
static uint8_t flag_read(const volatile bool *flag) { return *(const volatile uint8_t *)flag; }
struct gatt_event_record { uint16_t id,connection,value,padding; };
_Static_assert(sizeof(struct gatt_event_record)==8,"native callback template");
static void notify(volatile nrf_ble_gatt_t *g,uint16_t id,uint16_t connection,uint16_t value)
{
    struct gatt_event_record event={id,connection,value,0};
    g->evt_handler((nrf_ble_gatt_t *)g,(const nrf_ble_gatt_evt_t *)&event);
}
void r1_gatt_on_mtu_request(nrf_ble_gatt_t *context,const ble_evt_t *event)
{
    volatile nrf_ble_gatt_t *g=context;uint16_t connection=event->evt.gatts_evt.conn_handle;
    volatile nrf_ble_gatt_link_t *link=&g->links[connection];
    uint16_t client=event->evt.gatts_evt.params.exchange_mtu_request.client_rx_mtu;
    if (client<23) client=23;
    link->att_mtu_effective=client<link->att_mtu_desired ? client:link->att_mtu_desired;
    link->att_mtu_exchange_pending=false;
    uint32_t status=r1_gatt_sd_mtu_reply(connection,link->att_mtu_desired);
    if (status) error_log(status,r1_gatt_mtu_reply_ring,r1_gatt_mtu_reply_sdk);
    if (flag_read(&link->att_mtu_exchange_requested)) return;
    if (g->evt_handler) notify(g,0xa77,connection,link->att_mtu_effective);
}
void nrf_ble_gatt_on_ble_evt(const ble_evt_t *event,void *context)
{
    uint16_t connection=event->evt.common_evt.conn_handle;
    if (connection>=3) return;
    volatile nrf_ble_gatt_t *g=context;volatile nrf_ble_gatt_link_t *link=&g->links[connection];
    switch (event->header.evt_id) {
    case BLE_GAP_EVT_CONNECTED:
        link->data_length_desired=g->data_length;
        if (event->evt.gap_evt.params.connected.role==1) link->att_mtu_desired=g->att_mtu_desired_periph;
        else if (event->evt.gap_evt.params.connected.role==2) link->att_mtu_desired=g->att_mtu_desired_central;
        (void)r1_gatt_data_length_update(connection,link->data_length_desired);break;
    case BLE_GAP_EVT_DISCONNECTED:
        r1_sdk_gatt_link_init((nrf_ble_gatt_link_t *)link);break;
    case BLE_GATTC_EVT_EXCHANGE_MTU_RSP: {
        uint16_t mtu=event->evt.gattc_evt.params.exchange_mtu_rsp.server_rx_mtu;
        link->att_mtu_effective=mtu<link->att_mtu_desired ? mtu:link->att_mtu_desired;
        if (link->att_mtu_effective<23) link->att_mtu_effective=23;
        if (g->evt_handler && flag_read(&link->att_mtu_exchange_requested)) notify(g,0xa77,connection,link->att_mtu_effective);
        link->att_mtu_exchange_requested=false;link->att_mtu_exchange_pending=false;break;
    }
    case BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST:r1_gatt_on_mtu_request((nrf_ble_gatt_t *)g,event);break;
    case BLE_GAP_EVT_DATA_LENGTH_UPDATE: {
        ble_gap_evt_t copy;memcpy(&copy,&event->evt.gap_evt,sizeof(copy));
        _Static_assert(sizeof(copy)==44,"native gap copy span");
        g->links[copy.conn_handle].data_length_effective=(uint8_t)copy.params.data_length_update.effective_params.max_tx_octets;
        if (g->evt_handler) notify(g,0xda7a,copy.conn_handle,g->links[copy.conn_handle].data_length_effective);break;
    }
    case BLE_GAP_EVT_DATA_LENGTH_UPDATE_REQUEST:(void)r1_gatt_data_length_update(connection,link->data_length_desired);break;
    default:break;
    }
    if (flag_read(&link->att_mtu_exchange_pending)) {
        uint32_t status=r1_gatt_sd_mtu_request(connection,link->att_mtu_desired);
        if (!status) { link->att_mtu_exchange_pending=false;link->att_mtu_exchange_requested=true; }
        else if (status!=17) error_log(status,r1_gatt_mtu_request_ring,r1_gatt_mtu_request_sdk);
    }
}

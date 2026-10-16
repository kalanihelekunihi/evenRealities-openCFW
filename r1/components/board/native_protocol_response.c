#include <stdint.h>
#include <stddef.h>
#include "native_battery_memory.h"
extern uint32_t r1_authenticated_phone_connection_gate(void),r1_peer_channel_b_valid(void);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_model_encode(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_protocol_send_hook_call(uint32_t,const void *,uint32_t),r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_protocol_response_alloc_ring[] __attribute__((section(".r1.protocol_response.alloc_ring")))="[RING]proto malloc failed, cmd: %d, len:%d";
const char r1_protocol_response_alloc_sdk[] __attribute__((section(".r1.protocol_response.alloc_sdk")))="proto malloc failed, cmd: %d, len:%d";
const char r1_protocol_response_tx_ring[] __attribute__((section(".r1.protocol_response.tx_ring")))="[RING]ble proto tx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";
const char r1_protocol_response_tx_sdk[] __attribute__((section(".r1.protocol_response.tx_sdk")))="ble proto tx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";
const char r1_protocol_response_send_ring[] __attribute__((section(".r1.protocol_response.send_ring")))="[RING]proto_cmd_report: ble send failed, result = %d";
const char r1_protocol_response_send_sdk[] __attribute__((section(".r1.protocol_response.send_sdk")))="proto_cmd_report: ble send failed, result = %d";
static uint32_t command(const volatile uint8_t *p)
{
    uint32_t value=(uint32_t)p[1]<<16;
    value|=(uint32_t)p[6]<<8;value|=p[7];return value;
}
static uint32_t reversed_command(const volatile uint8_t *p)
{
    uint32_t value=read16(p+2);return ((value&255u)<<8)|(value>>8);
}
uint32_t r1_protocol_send_response(uint32_t handle,const void *header,const void *payload,uint32_t length)
{
    const volatile uint8_t *h=header;
    if (!h) return 2;
    if (!r1_authenticated_phone_connection_gate() && !r1_peer_channel_b_valid()) return 5;
    uint32_t capacity=(uint16_t)(length+12u);
    volatile uint8_t *buffer=pvPortMalloc(capacity);
    if (!buffer) {
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04800000,r1_protocol_response_alloc_ring,r1_protocol_response_alloc_ring,reversed_command(h),length);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x001c0001,r1_protocol_response_alloc_sdk,reversed_command(h),length);
        return 3;
    }
    uint32_t status=read16(h+4),flags=h[0],operation_low=h[3],operation_high=h[2],version=h[1];
    uint32_t result=r1_model_encode((void *)buffer,capacity,version,operation_high,operation_low,flags,status,payload,length);
    if (result) { vPortFree((void *)buffer);return result; }
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        uint32_t cmd=command(buffer),packet_flags=buffer[5],packet_length=read16(buffer+3);
        (void)r1_structured_log_format(0x0d000000,r1_protocol_response_tx_ring,r1_protocol_response_tx_ring,handle,cmd,packet_flags,packet_length);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t packet_length=read16(buffer+3),packet_flags=buffer[5],cmd=command(buffer);
        nrf_log_frontend_std_4(0x001c0003,r1_protocol_response_tx_sdk,handle,cmd,packet_flags,packet_length);
    }
    result=r1_protocol_send_hook_call(handle,(const void *)buffer,capacity);
    if (result) {
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04400000,r1_protocol_response_send_ring,r1_protocol_response_send_ring,result);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,r1_protocol_response_send_sdk,result);
        vPortFree((void *)buffer);return 4;
    }
    vPortFree((void *)buffer);return 0;
}

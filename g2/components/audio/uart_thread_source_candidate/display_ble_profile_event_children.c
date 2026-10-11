/* Native Cordio profile-write wrapper 0x533ed8 and OTA connection forward
 * 0x4bb04a. Selected callers ignore their unconventional register returns. */
#include <stdint.h>
extern void audio_ble_ota_connection_route(uint32_t,uint8_t,uint32_t); /* 0x4b6c82 */
extern uint32_t audio_ble_att_write_request(uint8_t,uint16_t,uint8_t,uint32_t,
                                            uint32_t,uint8_t,uint8_t); /* 0x533c6c */
void audio_ble_ota_connection_changed(uint8_t connection) {
    audio_ble_ota_connection_route(3u,connection,0x13u);
}
void audio_ble_profile_write_event(uint8_t connection,uint16_t attribute,
                                   uint16_t length,uint32_t value) {
    (void)audio_ble_att_write_request(connection,attribute,0u,length,value,0x1bu,0u);
}

/* Native 0x4d3534: authenticated device-control MMIO and halt loops. */
uint32_t audio_ble_ota_reset_event(uint32_t request,uint32_t unused) {
    (void)unused;
    if((uint8_t)request==0u) {
        *(volatile uint32_t *)(uintptr_t)0x40000008u=0xd4u;
        for(;;) { }
    }
    if((uint8_t)request==1u) {
        *(volatile uint32_t *)(uintptr_t)0x40000004u=0x1bu;
        for(;;) { }
    }
    return 6u;
}

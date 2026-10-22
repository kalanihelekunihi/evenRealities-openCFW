/* Direct children of native HciDrvHandler 0x4b4ab2. */
#include <stdint.h>
extern void *audio_wsf_msg_alloc(uint16_t); /* selected WsfMsgAlloc 0x4bf99e */
extern void audio_ble_hci_cmd_send(void *); /* hciCmdSend selected 0x52ae5e */
extern void audio_ble_wsf_timer_insert(void *,uint32_t); /* 0x52a424 */
extern void audio_ble_hci_radio_scheduler_53006c(void *,const void *,uint32_t,uint32_t);
/* The 0x491102 microsecond delay wrapper is g2_norflash_delay_us_491102
 * (drivers/flash/fal-norflash); audio_ble_hci_boot_delay_491102 is a payload
 * defsym alias of it. */
void WsfTimerStartMs(void *timer,uint32_t milliseconds) {
    audio_ble_wsf_timer_insert(timer,milliseconds/10u);
}
void audio_ble_hci_driver_empty_queue_4b4d18(void) {
    audio_ble_hci_radio_scheduler_53006c((void *)(uintptr_t)0x20073ba8u,
        (const void *)(uintptr_t)0x20065a10u,0x104u,0x820u);
}
/* 0x5300e2 is am_hal_queue_item_get (AmbiqSuite 5.1.0 hal/am_hal_queue.c);
 * audio_ble_hci_ring_consume_5300e2 is a payload defsym alias of it. */

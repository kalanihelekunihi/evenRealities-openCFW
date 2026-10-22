/* Native BLE application forward chains 0x46ef74 and 0x4a19c0. */
#include <stdint.h>
extern void audio_ble_adv_message_preprocess(void *); /* 0x46e098 */
extern void audio_ble_msgtx_message(uint8_t,void *);  /* 0x4782dc */
extern void audio_ble_ota_message(uint8_t,void *);    /* 0x4bdd70 */
extern void audio_ble_eus_message(uint8_t,void *);    /* 0x4bdfe6 */
extern void audio_ble_ess_message(uint8_t,void *);    /* 0x4be2e8 */
extern void audio_ble_efs_message(uint8_t,void *);    /* 0x4be572 */
extern void audio_ble_nus_message(uint8_t,void *);    /* 0x4be848 */
extern void audio_ble_ancc_message(uint8_t,void *);   /* 0x4bf780 */
extern void audio_ble_master_message_preprocess(void *); /* 0x4a06d4 */
extern void audio_ble_master_message(uint8_t,void *);    /* 0x4c4910 */

/* Stock 0x0046EF74 (dmConnSmEventDispatch) */
uint32_t audio_ble_comm_forward_a(uint8_t handler,void *message,
                                   uint32_t unused,uint32_t passthrough) {
    (void)unused;
    if(message)audio_ble_adv_message_preprocess(message);
    audio_ble_msgtx_message(handler,message);
    audio_ble_ota_message(handler,message);
    audio_ble_eus_message(handler,message);
    audio_ble_ess_message(handler,message);
    audio_ble_efs_message(handler,message);
    audio_ble_nus_message(handler,message);
    audio_ble_ancc_message(handler,message);
    return passthrough;
}

/* Stock 0x004A19C0 (ring_dm_event_dispatch) */
uint32_t audio_ble_comm_forward_b(uint8_t handler,void *message,
                                   uint32_t unused,uint32_t passthrough) {
    (void)unused;
    if(message)audio_ble_master_message_preprocess(message);
    audio_ble_master_message(handler,message);
    return passthrough;
}

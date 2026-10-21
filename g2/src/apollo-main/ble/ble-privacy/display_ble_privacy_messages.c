/* Native Cordio DM privacy message constructors 0x4d2524/282e/28cc. */
#include <stdint.h>
extern const void *audio_ble_dm_security_state[2]; /* selected state at RAM 0x20074114 */
extern uint8_t audio_ble_dm_privacy_state[]; /* live RAM 0x20073b78 */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected WsfMsgAlloc */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected WsfMsgSend */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected copy 0x439be4 */
const uint8_t *DmSecGetLocalIrk(void) { return (const uint8_t *)audio_ble_dm_security_state[0]; }
void DmPrivAddDevToResList(uint8_t address_type,const uint8_t *address,
                           const uint8_t *peer_irk,const uint8_t *local_irk,
                           uint8_t last,uint16_t handle) {
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(0x2cu);
    if(message==0) return;
    *(uint16_t *)(void *)message=handle;
    message[2u]=0x31u;
    message[4u]=address_type;
    (void)audio_queue_copy_bytes(message+5u,address,6u);
    (void)audio_queue_copy_bytes(message+0x0bu,peer_irk,16u);
    (void)audio_queue_copy_bytes(message+0x1bu,local_irk,16u);
    message[0x2bu]=last;
    audio_wsf_msg_send(audio_ble_dm_privacy_state[0x0cu],message);
}
void DmPrivSetAddrResEnable(uint8_t enabled) {
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(0x2cu);
    if(message==0) return;
    *(uint16_t *)(void *)message=0u;
    message[2u]=0x34u;
    message[4u]=enabled;
    audio_wsf_msg_send(audio_ble_dm_privacy_state[0x0cu],message);
}

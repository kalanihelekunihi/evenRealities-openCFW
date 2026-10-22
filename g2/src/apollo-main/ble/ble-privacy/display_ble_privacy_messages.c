/* Native Cordio DM privacy message constructors 0x4d2524/282e/28cc. */
#include <stdint.h>
extern const void *audio_ble_dm_security_state[2]; /* selected state at RAM 0x20074114 */
extern uint8_t audio_ble_dm_privacy_state[]; /* live RAM 0x20073b78 */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected WsfMsgAlloc */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected WsfMsgSend */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected copy 0x439be4 */
const uint8_t *DmSecGetLocalIrk(void) { return (const uint8_t *)audio_ble_dm_security_state[0]; }

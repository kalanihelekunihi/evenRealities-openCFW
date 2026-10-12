/* Native 0x4bafda passkey branch and 0x53634e Cordio random-byte getter. */
#include <stdint.h>
extern uint8_t audio_ble_stack_state_20072cb8[]; /* live random ring, native 0x20072cb8 */
extern void HciLeRandCmd(void); /* selected native 0x52b304 */
extern void audio_ble_slave_event_state(uint8_t); /* selected AppUiAction 0x4bd054 */
extern void DmSecAuthRsp(uint8_t,uint8_t,const uint8_t *); /* native 0x4d24d4 */
extern void audio_ble_pair_passkey_trace(uint32_t); /* native 0x4bd7fa */
__attribute__((noinline)) void audio_ble_random_bytes(uint8_t *out,uint8_t count) {
    uint8_t index=(uint8_t)(audio_ble_stack_state_20072cb8[0x3au]<<3u);
    for(uint32_t i=0u;i<count;i++) {
        out[i]=audio_ble_stack_state_20072cb8[index];
        index=(uint8_t)(index==0x1fu?0u:index+1u);
    }
    uint32_t replenishments=((uint32_t)count+7u)/8u;
    for(uint32_t i=0u;i<replenishments;i++) {
        HciLeRandCmd();
        uint8_t cursor=audio_ble_stack_state_20072cb8[0x3au];
        audio_ble_stack_state_20072cb8[0x3au]=(uint8_t)(cursor<3u?cursor+1u:0u);
    }
}
void audio_ble_pair_key_process(void *event) {
    const uint8_t *message=(const uint8_t *)event;
    if(message[5u]==0u) {
        audio_ble_slave_event_state(14u);
        return;
    }
    uint8_t random_bytes[4];
    audio_ble_random_bytes(random_bytes,4u);
    uint32_t value=(uint32_t)random_bytes[0]|((uint32_t)random_bytes[1]<<8u)
                  |((uint32_t)random_bytes[2]<<16u)|((uint32_t)random_bytes[3]<<24u);
    value%=1000000u; /* authenticated ROM 0x4bb3c8 */
    uint8_t passkey[4]={(uint8_t)value,(uint8_t)(value>>8u),(uint8_t)(value>>16u),(uint8_t)(value>>24u)};
    DmSecAuthRsp(message[0],3u,passkey);
    audio_ble_pair_passkey_trace(value);
}

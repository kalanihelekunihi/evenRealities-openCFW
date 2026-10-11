/* Native Cordio AttsCsfRegister 0x52d4e0. */
#include <stdint.h>
extern uint8_t audio_ble_connection_state_table[]; /* live 0x20073e04 */
void audio_ble_atts_csf_register(void (*callback)(void)) {
    __builtin_memcpy(audio_ble_connection_state_table+8u,&callback,4u);
}

/* Selector command byte and host counter, stock 0x5eca3e and 0x5973d4. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* observed RAM 0x2010fd20 */

uint32_t audio_terminal_session_command_5eca3e(uint32_t payload) {
    return (uint8_t)(payload>>16);
}

uint32_t audio_td_host_counter_get_5973d4(void) {
    const uint8_t *p=audio_td_state+0x9560u;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

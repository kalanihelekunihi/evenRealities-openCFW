/* Apollo host-status and terminal-data getters 0x5e8294/2e6,0x59734a/3dc. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

static const char no_host[]="HOST_STATUS_NO_HOST";
static const char offline[]="HOST_STATUS_OFFLINE";
static const char streaming[]="HOST_STATUS_STREAMING";
static const char unknown[]="HOST_STATUS_UNKNOWN";

const char *audio_terminal_host_status_name(uint32_t status) {
    switch((uint8_t)status) {
    case 0:return no_host;
    case 1:return offline;
    case 2:return streaming;
    default:return unknown;
    }
}

uint8_t audio_terminal_state_is_processing(uint32_t state) {
    uint8_t value=(uint8_t)state;
    return (uint8_t)(value>=1u && value<=3u);
}

uint8_t *audio_td_state_ptr_alias2(void) {return audio_td_state;}

uint32_t audio_td_counter_b_get(void) {
    const uint8_t *p=audio_td_state+0x9564u;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

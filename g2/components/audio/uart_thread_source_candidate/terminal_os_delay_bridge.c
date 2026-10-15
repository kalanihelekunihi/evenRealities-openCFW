/* Terminal caller name for the selected osDelay 0x449376 C body. */
#include <stdint.h>
extern uint32_t audio_delay(uint32_t);
void audio_os_delay(uint32_t ticks) {
    (void)audio_delay(ticks);
}

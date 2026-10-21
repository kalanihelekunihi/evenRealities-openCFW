/* Stock flag-B setter entry, 0x597572..0x59758d, through the C-owned TD provider. */
#include <stdint.h>
extern void audio_td_flag_set_with_reset(uint8_t);
void audio_td_flag_b_set_597572(uint32_t enabled) {
    audio_td_flag_set_with_reset((uint8_t)enabled);
}

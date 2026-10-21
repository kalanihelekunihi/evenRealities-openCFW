/* Native setting type-5 wear-detect route 0x467134..0x46713e. */
#include <stdint.h>
extern void audio_wear_detect_set_enable_49eb1e(uint32_t);
void audio_setting_dispatch_type5_467134(uint32_t value) {
    audio_wear_detect_set_enable_49eb1e((uint8_t)value);
}

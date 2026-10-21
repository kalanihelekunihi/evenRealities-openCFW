#include <stdint.h>

/* Native 0x4c3138..0x4c31d5. The pin configuration word at
 * 0x78ee48 is product-owned read-only data. */
extern const uint32_t g2_audio_clock_pin_config;
extern uint32_t g2_codec_pin_function(uint32_t pin, uint32_t config);

void audio_clock_stop(uint32_t group, uint32_t mode) {
    if (group == 0u) {
        (void)g2_codec_pin_function(32u, g2_audio_clock_pin_config);
        (void)g2_codec_pin_function(100u, g2_audio_clock_pin_config);
        (void)g2_codec_pin_function(102u, g2_audio_clock_pin_config);
        if ((uint8_t)mode == 0u)
            (void)g2_codec_pin_function(101u, g2_audio_clock_pin_config);
    } else if (group == 1u) {
        (void)g2_codec_pin_function(35u, g2_audio_clock_pin_config);
        (void)g2_codec_pin_function(34u, g2_audio_clock_pin_config);
        (void)g2_codec_pin_function(36u, g2_audio_clock_pin_config);
        if ((uint8_t)mode == 0u)
            (void)g2_codec_pin_function(3u, g2_audio_clock_pin_config);
    }
}

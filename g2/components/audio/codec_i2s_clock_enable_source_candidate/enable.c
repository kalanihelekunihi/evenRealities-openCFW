#include <stdint.h>

/* Stock 0x004c3074..0x004c3135. The nine words are product-owned
 * pin configuration descriptors at authenticated RAM literal addresses. */
extern const uint32_t g2_codec_clock_pin_0a; /* 0x20000114 */
extern const uint32_t g2_codec_clock_pin_0b; /* 0x2000011c */
extern const uint32_t g2_codec_clock_pin_0c; /* 0x20000120 */
extern const uint32_t g2_codec_clock_pin_0d; /* 0x20000118 */
extern const uint32_t g2_codec_clock_pin_1a; /* 0x20000124 */
extern const uint32_t g2_codec_clock_pin_1b; /* 0x20000130 */
extern const uint32_t g2_codec_clock_pin_1c; /* 0x20000134 */
extern const uint32_t g2_codec_clock_pin_1d; /* 0x20000128 */
extern const uint32_t g2_codec_clock_pin_1e; /* 0x2000012c */
extern uint32_t g2_codec_pin_function(uint32_t pin, uint32_t config); /* 0x480f0c */

void g2_codec_clock_enable(uint32_t group, uint32_t mode) {
    if (group >= 2u)
        return;
    mode = (uint8_t)mode;
    if (group == 0u) {
        if (mode != 0u) {
            (void)g2_codec_pin_function(32u, g2_codec_clock_pin_0a);
            (void)g2_codec_pin_function(100u, g2_codec_clock_pin_0b);
            (void)g2_codec_pin_function(102u, g2_codec_clock_pin_0c);
            return;
        }
        (void)g2_codec_pin_function(100u, g2_codec_clock_pin_0b);
        (void)g2_codec_pin_function(102u, g2_codec_clock_pin_0c);
        (void)g2_codec_pin_function(101u, g2_codec_clock_pin_0d);
        return;
    }
    if (mode != 0u) {
        (void)g2_codec_pin_function(35u, g2_codec_clock_pin_1a);
        (void)g2_codec_pin_function(34u, g2_codec_clock_pin_1b);
        (void)g2_codec_pin_function(36u, g2_codec_clock_pin_1c);
        return;
    }
    (void)g2_codec_pin_function(35u, g2_codec_clock_pin_1d);
    (void)g2_codec_pin_function(34u, g2_codec_clock_pin_1b);
    (void)g2_codec_pin_function(36u, g2_codec_clock_pin_1c);
    (void)g2_codec_pin_function(3u, g2_codec_clock_pin_1e);
}

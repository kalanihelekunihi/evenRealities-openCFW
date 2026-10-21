#include <stdint.h>

/* Complete stock 0x0058fd7e..0x0058fdbb instance/mode dispatcher. */
extern uint32_t g2_codec_clock_mux_request(uint32_t source, uint32_t user);

void g2_codec_source_mux(uint32_t instance, uint32_t mode) {
    uint32_t source = 10u;
    if (mode == 0u)
        source = instance == 0u ? 8u : 11u;
    else if (mode == 1u)
        source = instance == 0u ? 9u : 12u;
    else if (mode == 2u)
        source = instance == 0u ? 10u : 13u;
    (void)g2_codec_clock_mux_request((uint8_t)source, 0x11u);
}

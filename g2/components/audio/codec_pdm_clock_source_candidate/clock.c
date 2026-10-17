#include <stdint.h>

/* Stock 0x004c31d8..0x004c31fd; pin descriptor cells are product RAM. */
extern uint32_t g2_pdm_clock_pin_50; /* mutable RAM 0x2007421c */
extern uint32_t g2_pdm_clock_pin_51; /* mutable RAM 0x20074220 */
extern uint32_t g2_codec_pin_function(uint32_t pin, uint32_t config);

void g2_pdm_clock_enable(uint32_t group) {
    if (group == 0u) {
        (void)g2_codec_pin_function(50u, g2_pdm_clock_pin_50);
        (void)g2_codec_pin_function(51u, g2_pdm_clock_pin_51);
    }
}

#include <stdint.h>

/* Stock 0x00539bbc..0x00539c99. Its table readers and output gate
 * retain their own native entry contracts. The register at 0x400204e8
 * is an authenticated clock-control MMIO cell. */
extern uint8_t g2_clock_mux_group(uint8_t source);       /* 0x539348 */
extern uint8_t g2_clock_mux_setting(uint8_t source);     /* 0x539352 */
extern uint32_t g2_clock_mux_prepare(uint8_t group, uint8_t *selection); /* 0x539c9a */
extern uint8_t g2_clock_mux_mask(uint8_t source);        /* 0x539372 */
extern uint8_t g2_clock_mux_path(uint8_t group);         /* 0x53935c */
extern void g2_clock_mux_gate(uint8_t path, uint8_t mask); /* 0x44b0d6 */
extern void stock_delay_us(uint32_t us);                 /* 0x4807a0 */

uint32_t g2_codec_clock_mux_request(uint32_t source, uint32_t delay_us) {
    uint8_t const input = (uint8_t)source;
    uint8_t selection = 2u;
    uint8_t const group = g2_clock_mux_group(input);
    uint8_t const setting = g2_clock_mux_setting(input);
    (void)g2_clock_mux_prepare(group, &selection);
    uint8_t const requested = g2_clock_mux_mask(selection);
    uint8_t const prior = g2_clock_mux_mask(input);
    uint8_t const path = g2_clock_mux_path(group);
    g2_clock_mux_gate(path, (uint8_t)(requested | prior));
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)0x400204e8u;
    if (group <= 4u) {
        uint32_t const shift = group < 2u ? group * 2u :
                               group == 2u ? 4u :
                               group == 3u ? 5u : 7u;
        uint32_t const mask = group == 2u ? 1u : 3u;
        *control = (*control & ~(mask << shift)) |
                   (((uint32_t)setting & mask) << shift);
    }
    stock_delay_us(delay_us);
    g2_clock_mux_gate(path, prior);
    return 0u;
}

#include <stdint.h>

/* Stock 0x0059005e..0x005900cd. The two 100-byte handle rows begin
 * at the authenticated literal 0x20071114; their initializer is product
 * data and intentionally remains an external contract. */
extern uint8_t g2_codec_i2s_handle_pool[]; /* stock 0x20071114 */

uint32_t g2_codec_i2s_acquire(uint32_t instance, void **handle_cell) {
    if (instance >= 2u)
        return 5u;
    if (handle_cell == 0)
        return 6u;
    volatile uint32_t *const row = (volatile uint32_t *)(void *)
        (g2_codec_i2s_handle_pool + instance * 100u);
    if ((row[0] & 0x01000000u) != 0u)
        return 7u;
    row[0] |= 0x01000000u;
    row[0] &= ~0x02000000u;
    row[0] = (row[0] & 0xff000000u) | 0x00125125u;
    row[1] = instance;
    *handle_cell = (void *)row;
    return 0u;
}

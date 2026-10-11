#include <stdint.h>

/* Stock 0x00591fac..0x00592013, four 32-byte handle rows at RAM
 * 0x200718c8. Initial row contents remain product-owned. */
extern uint8_t g2_pdm_handle_rows[]; /* 0x200718c8 */

uint32_t g2_pdm_acquire(uint32_t instance, void **cell) {
    if (instance >= 4u)
        return 5u;
    if (cell == 0)
        return 6u;
    volatile uint32_t *const row = (volatile uint32_t *)(void *)
        (g2_pdm_handle_rows + instance * 32u);
    if ((row[0] & 0x01000000u) != 0u)
        return 7u;
    row[0] |= 0x01000000u;
    row[0] = (row[0] & 0xff000000u) | 0x00f956e2u;
    row[2] = instance;
    ((volatile uint8_t *)(void *)row)[4] = 0u;
    ((volatile uint8_t *)(void *)row)[30] = 0u;
    *cell = (void *)row;
    return 0u;
}

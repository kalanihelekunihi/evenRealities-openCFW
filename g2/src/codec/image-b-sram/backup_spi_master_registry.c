/* SPDX-License-Identifier: MIT
 * Image-B 0x10008204/0x10008218: initialize and register SPI masters.
 * Registry heads at 0x20017660 are native SRAM state.
 */
#include <stdint.h>

static volatile uint32_t *const registry =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20017660);

void gx8002_image_b_spi_master_registry_initialize_10008204(void)
{
    registry[0] = UINT32_C(0x20017660);
    registry[1] = UINT32_C(0x20017660);
    registry[2] = UINT32_C(0x20017668);
    registry[3] = UINT32_C(0x20017668);
}

int32_t gx8002_image_b_spi_register_master_10008218(uint32_t *master)
{
    if (master == (uint32_t *)0) return -19;
    uint32_t priority = master[1];
    uint32_t bus = master[0];
    if (priority == 0u || (int32_t)bus < 0) return -22;

    uint32_t old_tail = registry[1];
    uint32_t link = (uint32_t)(uintptr_t)(master + 7);
    master[7] = UINT32_C(0x20017660);
    registry[1] = link;
    master[8] = old_tail;
    *(uint32_t *)(uintptr_t)old_tail = link;

    uint32_t node = registry[2];
    for (;;) {
        uint32_t next = *(uint32_t *)(uintptr_t)node;
        if (node == UINT32_C(0x20017668)) return 0;
        uint32_t existing_bus = *(uint32_t *)(uintptr_t)(node - 24u);
        if (bus == existing_bus) {
            uint8_t existing_priority = *(uint8_t *)(uintptr_t)(node - 12u);
            if (priority > existing_priority) {
                *(uint32_t *)(uintptr_t)(node - 20u) =
                    (uint32_t)(uintptr_t)master;
                return 0;
            }
        }
        node = next;
    }
}

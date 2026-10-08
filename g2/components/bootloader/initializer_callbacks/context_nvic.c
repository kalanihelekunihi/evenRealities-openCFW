/* Reconstructed locked bootloader 0x430470..0x43048e.
 * This reproduces the signed-low-halfword guard; no silicon IRQ range check
 * or read/modify/write is present in the original wrapper. */
#include <stdint.h>
void opencfw_boot_context_nvic_enable(uint32_t interrupt)
{
    uint32_t irq = interrupt & 0xffffu;
    if ((irq & 0x8000u) != 0u)
        return;
    *(volatile uint32_t *)(uintptr_t)(0xe000e100u + ((irq >> 5) << 2)) =
        1u << (interrupt & 31u);
}

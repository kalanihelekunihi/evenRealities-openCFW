/* NOR callers BL stock 0x4205f4 with the same five-word PIO ABI. */
#include <stdint.h>
__attribute__((naked)) uint32_t opencfw_provider_4205f4(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *destination, uint32_t length)
{
    __asm__ volatile("b.w opencfw_bl_mspi_status_transfer");
}

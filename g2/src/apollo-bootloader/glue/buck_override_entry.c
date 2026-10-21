/* Deep-sleep stock call binds buck_override to 0x41c838 TON gate. */
#include <stdint.h>
__attribute__((naked)) uint32_t buck_override(uint32_t argument)
{
    __asm__ volatile("b.w opencfw_boot_ton_gate_write");
}

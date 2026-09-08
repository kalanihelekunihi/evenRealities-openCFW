/* SPDX-License-Identifier: MIT */
/* Reconstructed NPU control wrappers; SDK snpu_regs.o relocations identify
 * the primitive register helpers. Candidate only, pending qualification. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_reg_get_bit(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_reg_set_bit(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_reg_clear_bit(volatile uint32_t *, uint32_t);
void open_cfw_gx8002_npu_enable(void *registers)
{
    open_cfw_gx8002_reg_set_bit(registers, 0);
}
void open_cfw_gx8002_npu_disable(void *registers)
{
    open_cfw_gx8002_reg_clear_bit(registers, 0);
}
int open_cfw_gx8002_npu_is_enabled(void *registers)
{
    return (int)open_cfw_gx8002_reg_get_bit(registers, 0);
}
int open_cfw_gx8002_npu_all_idle(void *registers)
{
    return (int)open_cfw_gx8002_reg_get_bit((volatile uint32_t *)registers + 3, 31);
}

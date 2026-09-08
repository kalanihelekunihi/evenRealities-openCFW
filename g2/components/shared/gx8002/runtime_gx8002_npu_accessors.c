/* SPDX-License-Identifier: MIT */
/* Reconstructed NPU accessors from authenticated symbol/call-target identity.
 * Candidate only. Getter returns explicitly preserve observed r0 as well as
 * the output store; private original C return types are not claimed. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_reg_get_value(volatile uint32_t *);
extern void open_cfw_gx8002_reg_set_value(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_reg_set_bit(volatile uint32_t *, uint32_t);
static inline volatile uint32_t *at(void *base, uint32_t offset)
{
    return (volatile uint32_t *)((uintptr_t)base + offset);
}
uint32_t open_cfw_gx8002_npu_get_over_cmd_addr(void *base, uint32_t *output)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(at(base, 260));
    *output = value;
    return value;
}
uint32_t open_cfw_gx8002_npu_get_op_overflow_cmd_addr(void *base, uint32_t *output)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(at(base, 292));
    *output = value;
    return value;
}
void open_cfw_gx8002_npu_reset(void *base)
{
    open_cfw_gx8002_reg_set_bit(at(base, 4), 3);
    open_cfw_gx8002_reg_set_bit(at(base, 8), 3);
}
void open_cfw_gx8002_npu_set_task_head(void *base, uint32_t value)
{
    open_cfw_gx8002_reg_set_value(at(base, 16), value);
}
uint32_t open_cfw_gx8002_npu_get_task_head(void *base, uint32_t *output)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(at(base, 16));
    *output = value;
    return value;
}
uint32_t open_cfw_gx8002_npu_get_base_addr(void *base, uint32_t index, uint32_t *output)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(at(base, index << 2));
    *output = value;
    return value;
}
uint32_t open_cfw_gx8002_npu_get_cur_cmd_addr(void *base, uint32_t *output)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(at(base, 256));
    *output = value;
    return value;
}

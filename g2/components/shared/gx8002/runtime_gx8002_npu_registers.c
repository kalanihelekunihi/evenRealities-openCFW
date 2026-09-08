/* SPDX-License-Identifier: MIT */
/* Source-defined NPU register operations. The optional three instruction
 * wrappers preserve C-SKY low-six-bit counts, including zero for 32..63.
 * The fully defined portable C path remains a comparison oracle. */
#include <stdint.h>
static inline uint32_t shift_right(uint32_t value, uint32_t bit)
{
#ifdef OPEN_CFW_GX8002_NATIVE_SHIFTS
    uint32_t result;
    __asm__("lsr %0, %1, %2" : "=r"(result) : "r"(value), "r"(bit));
    return result;
#else
    unsigned int shift = bit & 63u;
    return shift < 32 ? value >> shift : 0;
#endif
}
static inline uint32_t set_mask(uint32_t bit)
{
#ifdef OPEN_CFW_GX8002_NATIVE_SHIFTS
    uint32_t result;
    __asm__("lsl %0, %1, %2" : "=r"(result) : "r"(UINT32_C(1)), "r"(bit));
    return result;
#else
    unsigned int shift = bit & 63u;
    return shift < 32 ? UINT32_C(1) << shift : 0;
#endif
}
static inline uint32_t clear_mask(uint32_t bit)
{
#ifdef OPEN_CFW_GX8002_NATIVE_SHIFTS
    uint32_t result;
    __asm__("rotl %0, %1, %2" : "=r"(result) : "r"(UINT32_C(0xfffffffe)), "r"(bit));
    return result;
#else
    unsigned int shift = bit & 63u;
    return shift < 32 ? ~(UINT32_C(1) << shift) : 0;
#endif
}
uint32_t open_cfw_gx8002_reg_get_bit(volatile uint32_t *reg, uint32_t bit)
{
    uint32_t value = *reg;
    return shift_right(value, bit) & 1u;
}
void open_cfw_gx8002_reg_set_bit(volatile uint32_t *reg, uint32_t bit)
{
    uint32_t value = *reg;
    *reg = value | set_mask(bit);
}
void open_cfw_gx8002_reg_clear_bit(volatile uint32_t *reg, uint32_t bit)
{
    uint32_t value = *reg;
    *reg = value & clear_mask(bit);
}
uint32_t open_cfw_gx8002_reg_get_value(volatile uint32_t *reg)
{
    return *reg;
}
void open_cfw_gx8002_reg_set_value(volatile uint32_t *reg, uint32_t value)
{
    *reg = value;
}

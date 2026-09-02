/* SPDX-License-Identifier: MIT */
/* Hard-float ABI veneers for the fixed-address G2 bootloader math cores. */

typedef __UINT32_TYPE__ open_cfw_math_veneer_u32;

typedef union {
    float value;
    open_cfw_math_veneer_u32 bits;
} open_cfw_math_veneer_float_bits;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_MATH_VENEER_AAPCS __attribute__((pcs("aapcs-vfp")))
#define OPEN_CFW_MATH_VENEER_NAKED __attribute__((naked))
#else
#define OPEN_CFW_MATH_VENEER_AAPCS
#define OPEN_CFW_MATH_VENEER_NAKED
#endif

#define OPEN_CFW_MATH_VENEER \
    __attribute__((used, noinline, visibility("default"))) \
    OPEN_CFW_MATH_VENEER_AAPCS OPEN_CFW_MATH_VENEER_NAKED

extern open_cfw_math_veneer_u32
open_cfw_bootloader_floor_bits_427ca0(open_cfw_math_veneer_u32 value);
extern open_cfw_math_veneer_u32 open_cfw_bootloader_fmod_bits_427cdc(
    open_cfw_math_veneer_u32 x_bits,
    open_cfw_math_veneer_u32 y_bits
);
extern open_cfw_math_veneer_u32
open_cfw_bootloader_round_bits_427da8(open_cfw_math_veneer_u32 value);
extern open_cfw_math_veneer_u32
open_cfw_bootloader_ceil_bits_427de0(open_cfw_math_veneer_u32 value);

#if defined(__arm__) || defined(__thumb__)
OPEN_CFW_MATH_VENEER float open_cfw_bootloader_floorf_427c90(float value)
{
    __asm volatile(
        "vmov r0, s0\n"
        "mov ip, lr\n"
        "bl open_cfw_bootloader_floor_bits_427ca0\n"
        "vmov s0, r0\n"
        "bx ip\n"
    );
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_fmodf_427ccc(
    float dividend,
    float divisor
)
{
    __asm volatile(
        "push {lr}\n"
        "vmov r0, r1, s0, s1\n"
        "bl open_cfw_bootloader_fmod_bits_427cdc\n"
        "vmov s0, r0\n"
        "pop {pc}\n"
    );
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_roundf_427d98(float value)
{
    __asm volatile(
        "vmov r0, s0\n"
        "mov ip, lr\n"
        "bl open_cfw_bootloader_round_bits_427da8\n"
        "vmov s0, r0\n"
        "bx ip\n"
    );
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_ceilf_427dd0(float value)
{
    __asm volatile(
        "vmov r0, s0\n"
        "mov r3, lr\n"
        "bl open_cfw_bootloader_ceil_bits_427de0\n"
        "vmov s0, r0\n"
        "bx r3\n"
    );
}
#else
OPEN_CFW_MATH_VENEER float open_cfw_bootloader_floorf_427c90(float value)
{
    open_cfw_math_veneer_float_bits result = { value };
    result.bits = open_cfw_bootloader_floor_bits_427ca0(result.bits);
    return result.value;
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_fmodf_427ccc(
    float dividend,
    float divisor
)
{
    open_cfw_math_veneer_float_bits x = { dividend };
    open_cfw_math_veneer_float_bits y = { divisor };
    x.bits = open_cfw_bootloader_fmod_bits_427cdc(x.bits, y.bits);
    return x.value;
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_roundf_427d98(float value)
{
    open_cfw_math_veneer_float_bits result = { value };
    result.bits = open_cfw_bootloader_round_bits_427da8(result.bits);
    return result.value;
}

OPEN_CFW_MATH_VENEER float open_cfw_bootloader_ceilf_427dd0(float value)
{
    open_cfw_math_veneer_float_bits result = { value };
    result.bits = open_cfw_bootloader_ceil_bits_427de0(result.bits);
    return result.value;
}
#endif

/* SPDX-License-Identifier: MIT */
/*
 * Freestanding binary32 helpers for the G2 bootloader hard-float ABI.
 *
 * The fmod reduction follows the integer normalization algorithm used by
 * musl libc. The rounding cores are clean-room expressions of the
 * authenticated IAR-compatible bit contracts in the stock image.
 */

typedef __UINT32_TYPE__ open_cfw_u32;
typedef __INT32_TYPE__ open_cfw_s32;

typedef union {
    float value;
    open_cfw_u32 bits;
} open_cfw_float_bits;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

#define OPEN_CFW_LEAF \
    __attribute__((used, noinline, visibility("default")))
#define OPEN_CFW_FLOAT_LEAF OPEN_CFW_LEAF OPEN_CFW_AAPCS_VFP
#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_NAKED_LEAF OPEN_CFW_LEAF __attribute__((naked))
#endif

#if defined(__arm__) || defined(__thumb__)
OPEN_CFW_NAKED_LEAF open_cfw_u32
open_cfw_bootloader_floor_bits_427ca0(open_cfw_u32 value)
{
    __asm volatile(
        "ubfx r2, r0, #23, #8\n"
        "subs r2, #126\n"
        "ble 1f\n"
        "cmp r2, #24\n"
        "bge 2f\n"
        "mvn r1, #0xff000000\n"
        "lsrs r1, r2\n"
        "tst r0, r0\n"
        "it mi\n"
        "addmi r0, r0, r1\n"
        "bics r0, r1\n"
        "bx lr\n"
        "1:\n"
        "cmn r0, r0\n"
        "itt ne\n"
        "movne r0, #0\n"
        "movtne r0, #0xbf80\n"
        "it lo\n"
        "movlo r0, #0\n"
        "2:\n"
        "bx lr\n"
    );
}
#else
OPEN_CFW_LEAF open_cfw_u32
open_cfw_bootloader_floor_bits_427ca0(open_cfw_u32 value)
{
    open_cfw_s32 exponent =
        (open_cfw_s32)((value >> 23) & 0xFFU) - 126;

    if (exponent <= 0) {
        if ((value << 1) != 0U) {
            return (value & 0x80000000U) != 0U ? 0xBF800000U : 0U;
        }
    } else if (exponent < 24) {
        open_cfw_u32 mask = 0x00FFFFFFU >> (open_cfw_u32)exponent;
        if ((value & 0x80000000U) != 0U) {
            value += mask;
        }
        value &= ~mask;
    }
    return value;
}
#endif

OPEN_CFW_LEAF open_cfw_u32 open_cfw_bootloader_fmod_bits_427cdc(
    open_cfw_u32 x_bits,
    open_cfw_u32 y_bits
)
{
    open_cfw_s32 x_exponent = (open_cfw_s32)((x_bits >> 23) & 0xFFU);
    open_cfw_s32 y_exponent = (open_cfw_s32)((y_bits >> 23) & 0xFFU);
    open_cfw_u32 sign = x_bits & 0x80000000U;
    open_cfw_u32 temporary;

    if ((y_bits << 1) == 0U || y_exponent == 0xFF ||
        x_exponent == 0xFF) {
        return 0x7FFFFFFFU;
    }
    if ((x_bits << 1) <= (y_bits << 1)) {
        return (x_bits << 1) == (y_bits << 1) ? sign : x_bits;
    }

    if (x_exponent == 0) {
        temporary = (open_cfw_u32)__builtin_clz(x_bits << 9);
        x_exponent = -(open_cfw_s32)temporary;
        x_bits <<= temporary + 1U;
    } else {
        x_bits = (x_bits & 0x007FFFFFU) | 0x00800000U;
    }
    if (y_exponent == 0) {
        temporary = (open_cfw_u32)__builtin_clz(y_bits << 9);
        y_exponent = -(open_cfw_s32)temporary;
        y_bits <<= temporary + 1U;
    } else {
        y_bits = (y_bits & 0x007FFFFFU) | 0x00800000U;
    }

    while (x_exponent > y_exponent) {
        temporary = x_bits - y_bits;
        if ((temporary >> 31) == 0U) {
            if (temporary == 0U) {
                return sign;
            }
            x_bits = temporary;
        }
        x_bits <<= 1;
        --x_exponent;
    }
    temporary = x_bits - y_bits;
    if ((temporary >> 31) == 0U) {
        if (temporary == 0U) {
            return sign;
        }
        x_bits = temporary;
    }
    temporary = (open_cfw_u32)__builtin_clz(x_bits) - 8U;
    x_bits <<= temporary;
    x_exponent -= (open_cfw_s32)temporary;
    if (x_exponent > 0) {
        x_bits = (x_bits - 0x00800000U) |
            ((open_cfw_u32)x_exponent << 23);
    } else {
        x_bits >>= (open_cfw_u32)(-x_exponent + 1);
    }
    return x_bits | sign;
}

#if defined(__arm__) || defined(__thumb__)
OPEN_CFW_NAKED_LEAF open_cfw_u32
open_cfw_bootloader_round_bits_427da8(open_cfw_u32 value)
{
    __asm volatile(
        "ubfx r2, r0, #23, #8\n"
        "subs r2, #126\n"
        "ble 1f\n"
        "cmp r2, #24\n"
        "bge 2f\n"
        "mvn r1, #0xff000000\n"
        "lsrs r1, r2\n"
        "bic r0, r0, r1, lsr #1\n"
        "adds r0, r0, r1\n"
        "bics r0, r1\n"
        "bx lr\n"
        "1:\n"
        "and r0, r0, #0x80000000\n"
        "it eq\n"
        "orreq r0, r0, #0x3f800000\n"
        "2:\n"
        "bx lr\n"
    );
}
#else
OPEN_CFW_LEAF open_cfw_u32
open_cfw_bootloader_round_bits_427da8(open_cfw_u32 value)
{
    open_cfw_s32 exponent =
        (open_cfw_s32)((value >> 23) & 0xFFU) - 126;

    if (exponent <= 0) {
        open_cfw_u32 sign = value & 0x80000000U;
        value = sign | (exponent == 0 ? 0x3F800000U : 0U);
    } else if (exponent < 24) {
        open_cfw_u32 mask = 0x00FFFFFFU >> (open_cfw_u32)exponent;
        value = ((value & ~(mask >> 1)) + mask) & ~mask;
    }
    return value;
}
#endif

#if defined(__arm__) || defined(__thumb__)
OPEN_CFW_NAKED_LEAF open_cfw_u32
open_cfw_bootloader_ceil_bits_427de0(open_cfw_u32 value)
{
    __asm volatile(
        "ubfx r2, r0, #23, #8\n"
        "subs r2, #126\n"
        "ble 1f\n"
        "cmp r2, #24\n"
        "bge 2f\n"
        "mvn r1, #0xff000000\n"
        "lsrs r1, r2\n"
        "tst r0, r0\n"
        "it pl\n"
        "addpl r0, r0, r1\n"
        "bics r0, r1\n"
        "bx lr\n"
        "1:\n"
        "cmn r0, r0\n"
        "it ne\n"
        "movne r0, #0x3f800000\n"
        "it hs\n"
        "movhs r0, #0x80000000\n"
        "2:\n"
        "bx lr\n"
    );
}
#else
OPEN_CFW_LEAF open_cfw_u32
open_cfw_bootloader_ceil_bits_427de0(open_cfw_u32 value)
{
    open_cfw_s32 exponent =
        (open_cfw_s32)((value >> 23) & 0xFFU) - 126;

    if (exponent <= 0) {
        if ((value << 1) != 0U) {
            value = (value & 0x80000000U) == 0U
                ? 0x3F800000U : 0x80000000U;
        }
    } else if (exponent < 24) {
        open_cfw_u32 mask = 0x00FFFFFFU >> (open_cfw_u32)exponent;
        if ((value & 0x80000000U) == 0U) {
            value += mask;
        }
        value &= ~mask;
    }
    return value;
}
#endif

OPEN_CFW_FLOAT_LEAF open_cfw_u32
open_cfw_bootloader_float_range_classify_427e0c(float value)
{
    open_cfw_float_bits input = { value };
    open_cfw_u32 magnitude = input.bits & 0x7FFFFFFFU;

    if (magnitude > 0x7F800000U) {
        return 4U;
    }
    if ((input.bits & 0x80000000U) != 0U) {
        if (magnitude == 0U) {
            return 2U;
        }
        return magnitude <= 0x41A00000U ? 1U : 4U;
    }
    if (input.bits < 0x447A0000U) {
        return 2U;
    }
    if (input.bits < 0x4FFEE92DU) {
        return 3U;
    }
    return 4U;
}

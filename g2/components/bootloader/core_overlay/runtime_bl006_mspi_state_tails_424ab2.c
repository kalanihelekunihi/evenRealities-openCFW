/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two dead G2 bootloader MSPI tails:
 *
 *  A. per-instance state-initializer tail at 0x00424AB2..0x00424AEA
 *     (56 B), inside the retained span "between initialize and
 *     configure". The replaced initialize head recomputes this work;
 *     the tail survives only as unreachable stock bytes.
 *     Registers on entry (set by the replaced head): r0 = per-instance
 *     stride, r1 = out-slot pointer, r3 = instance index, r4 = state
 *     base; r5 is scratch. The tail publishes the instance window:
 *       p = base + index * stride
 *       p->u8[0x0C] = 0
 *       p->u32[0x18] = 0
 *       p->u8[0x8C9] = 7
 *       p->u32[0x8CC] = 8
 *       *out = (uint32_t)p
 *     and returns 0, preserving r4/r5. Each store recomputes
 *     p from (base, index, stride) exactly as the stock body does;
 *     the final instance address is recomputed once more into r0
 *     before the out-slot store.
 *
 *  B. public device-configuration pre-step tail at
 *     0x00424B88..0x00424BD4 (76 B), inside the retained "handle,
 *     MSPI base, and pad-mask literals" span. Registers on entry:
 *     r0 = value to publish, r1 = configuration byte source,
 *     r2 = destination word, r3 = key, r5 = state base; r4/r6 are
 *     scratch saved across the tail. The tail:
 *       k = key + 0x42A
 *       [dst + 0x858] = value
 *       q = [base + k*key + 0x858]; if (q >= 0x101) q = 0x100
 *       (clamps the 0x101-magic field, defaulting an out-of-range
 *       reading to 0x100)
 *       [base + k*key + 9] = cfg->u8[8]
 *       [base + k*key + 8] = 1
 *       [base + k*key + 0xA] = 0x1A
 *     and returns 0.
 *
 * Both tails are single-exit, call-free, and literal-free. The
 * whole-image survey grades both spans corroborated_unreachable_
 * control_flow and a whole-image `bl` sweep finds no caller of
 * either entry, so neither tail executes in the shipped image;
 * the reconstructions document the bytes and pin the behavior the
 * replaced heads must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-424ab2-4250e6-427c72-source-closure.md.
 */

typedef __UINT8_TYPE__ open_cfw_bl006_tails_u8;
typedef __UINT32_TYPE__ open_cfw_bl006_tails_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_TAILS_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_TAILS_ATTR __attribute__((used, noinline))
#endif

/* Tail A: per-instance MSPI state-initializer tail. */
OPEN_CFW_BL006_TAILS_ATTR
open_cfw_bl006_tails_u32 open_cfw_bootloader_mspi_state_init_tail_424ab2(
    open_cfw_bl006_tails_u32 stride,
    open_cfw_bl006_tails_u32 *out,
    open_cfw_bl006_tails_u32 reserved,
    open_cfw_bl006_tails_u32 index,
    open_cfw_bl006_tails_u8 *base)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb r2, [r5, #0xc]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "str r2, [r5, #0x18]\n"
        "movs r2, #7\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0x8c9]\n"
        "movs r2, #8\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "str.w r2, [r5, #0x8cc]\n"
        "muls r0, r3, r0\n"
        "add r0, r4\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "pop {r4, r5}\n"
        "bx lr\n");
#else
    open_cfw_bl006_tails_u8 *p = base + (open_cfw_bl006_tails_u32)(index * stride);
    (void)reserved;
    p[0x0CU] = (open_cfw_bl006_tails_u8)0U;
    *(open_cfw_bl006_tails_u32 *)(p + 0x18U) = 0U;
    p[0x8C9U] = (open_cfw_bl006_tails_u8)7U;
    *(open_cfw_bl006_tails_u32 *)(p + 0x8CCU) = 8U;
    *out = (open_cfw_bl006_tails_u32)(open_cfw_bl006_tails_u32)(__UINTPTR_TYPE__)p;
    return 0U;
#endif
}

/* Tail B: public MSPI device-configuration pre-step tail. */
OPEN_CFW_BL006_TAILS_ATTR
open_cfw_bl006_tails_u32 open_cfw_bootloader_mspi_config_pre_tail_424b88(
    open_cfw_bl006_tails_u32 value,
    const open_cfw_bl006_tails_u8 *cfg,
    open_cfw_bl006_tails_u32 *dst,
    open_cfw_bl006_tails_u32 key,
    open_cfw_bl006_tails_u8 *base)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "addw r4, r3, #0x42a\n"
        "str.w r0, [r2, #0x858]\n"
        "mul r0, r4, r3\n"
        "add r0, r5\n"
        "ldr.w r0, [r0, #0x858]\n"
        "movw r2, #0x101\n"
        "cmp r0, r2\n"
        "blo 1f\n"
        "mov.w r0, #0x100\n"
        "mul r2, r4, r3\n"
        "add r2, r5\n"
        "str.w r0, [r2, #0x858]\n"
        "1:\n"
        "ldrb r0, [r1, #8]\n"
        "mul r1, r4, r3\n"
        "add r1, r5\n"
        "strb r0, [r1, #9]\n"
        "movs r0, #1\n"
        "mul r1, r4, r3\n"
        "add r1, r5\n"
        "strb r0, [r1, #8]\n"
        "movs r0, #0x1a\n"
        "muls r3, r4, r3\n"
        "add.w r1, r5, r3\n"
        "strb r0, [r1, #0xa]\n"
        "movs r0, #0\n"
        "pop {r4, r5, r6}\n"
        "bx lr\n");
#else
    open_cfw_bl006_tails_u32 k = key + 0x42AU;
    open_cfw_bl006_tails_u8 *q;
    *(open_cfw_bl006_tails_u32 *)((open_cfw_bl006_tails_u8 *)dst + 0x858U) = value;
    q = base + (open_cfw_bl006_tails_u32)(k * key);
    if (*(open_cfw_bl006_tails_u32 *)(q + 0x858U) >= 0x101U) {
        *(open_cfw_bl006_tails_u32 *)(q + 0x858U) = 0x100U;
    }
    q = base + (open_cfw_bl006_tails_u32)(k * key);
    q[9U] = cfg[8U];
    q = base + (open_cfw_bl006_tails_u32)(k * key);
    q[8U] = (open_cfw_bl006_tails_u8)1U;
    q = base + (open_cfw_bl006_tails_u32)(k * key);
    q[0xAU] = (open_cfw_bl006_tails_u8)0x1AU;
    return 0U;
#endif
}

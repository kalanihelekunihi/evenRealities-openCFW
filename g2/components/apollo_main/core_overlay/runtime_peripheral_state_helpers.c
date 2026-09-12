/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of the nine-function first-party
 * peripheral-state cluster retained in G2 firmware 2.2.6.10 at
 * 0x0048D558..0x0048D570 (3-word parameter init, 16 bytes),
 * 0x0048D570..0x0048D588 (nibble-to-mode map, 24 bytes),
 * 0x0048D588..0x0048D620 (register-state mode switch, 152 bytes),
 * 0x0048D620..0x0048D654 (state-flag getter, 52 bytes),
 * 0x0048D654..0x0048D670 (IRQ-guarded triple-sample vote, 28 bytes),
 * 0x0048D670..0x0048D6DC (sample retry loop, 108 bytes),
 * 0x0048D6DC..0x0048D6E6 (flag OR-set, 10 bytes),
 * 0x0048D6E6..0x0048D6F0 (flag store/fetch, 10 bytes), and
 * 0x0048D6F0..0x0048D704 (masked flag get, 20 bytes; Apollo main
 * application, component `apollo_main`, work item AM-040).
 *
 * All nine are clean-room C written from the stock instruction stream
 * (decoded with capstone on macOS). The exact peripheral block is not
 * named: the cluster drives the register block rooted at 0x40008800
 * with SRAM state at 0x20074F7A/0x20000318, called from the 0x004563xx
 * driver, with two still-stock channel setters at 0x004C44BC/0x004C4530
 * (both 116 bytes, still decompiled). The audit records this as a
 * first-party state cluster with the peripheral identity still open.
 *
 * Address provenance (every constant below read back from the image):
 *  - 0x0048D568/0x0048D56C literal pool: 0x20071E30, 0x2005F154
 *    (third word is the immediate 0x400).
 *  - Holder words read fresh on every call, exactly as stock does:
 *    0x0048D704 -> 0x40008800 (control register),
 *    0x0048D708 -> 0x20074F7A (dirty byte),
 *    0x0048D70C -> 0x40008820 (per-lane table),
 *    0x0048D710 -> 0x40008900 (mask register),
 *    0x0048D714 -> 0x40008904 (value register),
 *    0x0048D718 -> 0x40008908 (latch register),
 *    0x0048D71C -> 0x40008804 (sample register),
 *    0x0048D720 -> 0x20000318 (SRAM sample shadow).
 *
 * Deliberate faithful quirks (all verified in the disassembly):
 *  - The mode switch stores the full 32-bit argument to the control
 *    register, passes mode&0xFF with the constant second argument
 *    0x32 to the channel setters, writes the dirty BYTE (strb) 1, and
 *    returns the previous register word (stock also passes the untouched
 *    fourth argument back in r1 through an asymmetric pop; both known
 *    callers discard r1, so the C port leaves it unspecified).
 *  - The flag getter returns 0 unless the dirty byte is nonzero, the
 *    low nibble is nonzero, and bit 31 is clear; then it returns
 *    bit30^1.
 *  - The triple-sample vote returns the second sample when the first
 *    two agree, else the third (stock compares [sp] vs [sp+4]).
 *  - The retry loop spins while the fresh sample equals the shadow or
 *    shadow+1 (unsigned 32-bit wrap is preserved: stock uses adds),
 *    disables IRQs via the retained hook and stashes the prior state
 *    in a stack slot, clamps the lane target to (first + (limit -
 *    fresh) - 3) when (fresh - first + 3) < limit else stores 1 with
 *    status 0x8000000, records the fresh sample to the shadow, then
 *    restores PRIMASK from the stashed state with a single
 *    `msr primask, r0` (opcode 0xF3808810, verified by hand-decode:
 *    half1 0xF380 selects MSR-with-Rn=r0, half2 low byte 0x10 selects
 *    PRIMASK; Ghidra renders this as an enableIRQinterrupts call) and
 *    returns the status word (0 ok, 5 bad lane, 0x8000000 clamped).
 *    Out-of-range lanes (>= 8) return 5 with no register traffic.
 *  - The masked get narrows its selector with uxtb before comparing
 *    against zero, exactly as stock does.
 *
 * Retained callees (still stock, all outside this item's range):
 *  - 0x004D5888 IRQ-guarded triple register read
 *  - 0x00473940 IRQ-disable returning the prior PRIMASK bit
 *  - 0x004C44BC / 0x004C4530 channel setters (mode&0xFF, 0x32)
 *  - 0x0048D570 nibble map is intra-cluster (target_function link)
 *
 * Hardware qualification stays blocked by unavailable physical
 * evidence; no flashing, DFU, MMIO probing, signing, or publishing
 * was performed.
 */

typedef unsigned int open_cfw_state_word;
typedef unsigned char open_cfw_state_byte;

#ifndef OPEN_CFW_STATE_SAMPLE_TRIPLE
typedef void (*open_cfw_state_sample_triple_fn)(
    open_cfw_state_word *reg, open_cfw_state_word out[3]);
#define OPEN_CFW_STATE_SAMPLE_TRIPLE(reg, out) \
    (((open_cfw_state_sample_triple_fn)0x004D5889U)((reg), (out)))
#endif

#ifndef OPEN_CFW_STATE_IRQ_DISABLE
typedef open_cfw_state_word (*open_cfw_state_irq_disable_fn)(void);
#define OPEN_CFW_STATE_IRQ_DISABLE() \
    (((open_cfw_state_irq_disable_fn)0x00473941U)())
#endif

#ifndef OPEN_CFW_STATE_IRQ_RESTORE
#define OPEN_CFW_STATE_IRQ_RESTORE(saved) \
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory")
#endif

#ifndef OPEN_CFW_STATE_CHANNEL_A
typedef void (*open_cfw_state_channel_fn)(
    open_cfw_state_word mode, open_cfw_state_word arg);
#define OPEN_CFW_STATE_CHANNEL_A(mode, arg) \
    (((open_cfw_state_channel_fn)0x004C44BDU)((mode), (arg)))
#endif

#ifndef OPEN_CFW_STATE_CHANNEL_B
#define OPEN_CFW_STATE_CHANNEL_B(mode, arg) \
    (((open_cfw_state_channel_fn)0x004C4531U)((mode), (arg)))
#endif

enum {
    OPEN_CFW_STATE_PARAM_THIRD = 0x400U,
    OPEN_CFW_STATE_CHANNEL_ARG = 0x32U,
    OPEN_CFW_STATE_LANE_COUNT = 8U,
    OPEN_CFW_STATE_CLAMP_STATUS = 0x8000000U,
    OPEN_CFW_STATE_BAD_LANE = 5U
};

#ifndef OPEN_CFW_STATE_PARAM_FIRST
#define OPEN_CFW_STATE_PARAM_FIRST ((open_cfw_state_word)0x20071E30U)
#endif
#ifndef OPEN_CFW_STATE_PARAM_SECOND
#define OPEN_CFW_STATE_PARAM_SECOND ((open_cfw_state_word)0x2005F154U)
#endif

#ifndef OPEN_CFW_STATE_HOLDER_CONTROL
#define OPEN_CFW_STATE_HOLDER_CONTROL 0x0048D704U
#endif
#ifndef OPEN_CFW_STATE_HOLDER_DIRTY
#define OPEN_CFW_STATE_HOLDER_DIRTY 0x0048D708U
#endif
#ifndef OPEN_CFW_STATE_HOLDER_LANES
#define OPEN_CFW_STATE_HOLDER_LANES 0x0048D70CU
#endif
#ifndef OPEN_CFW_STATE_HOLDER_MASK
#define OPEN_CFW_STATE_HOLDER_MASK 0x0048D710U
#endif
#ifndef OPEN_CFW_STATE_HOLDER_VALUE
#define OPEN_CFW_STATE_HOLDER_VALUE 0x0048D714U
#endif
#ifndef OPEN_CFW_STATE_HOLDER_LATCH
#define OPEN_CFW_STATE_HOLDER_LATCH 0x0048D718U
#endif
#ifndef OPEN_CFW_STATE_HOLDER_SAMPLE
#define OPEN_CFW_STATE_HOLDER_SAMPLE 0x0048D71CU
#endif
#ifndef OPEN_CFW_STATE_HOLDER_SHADOW
#define OPEN_CFW_STATE_HOLDER_SHADOW 0x0048D720U
#endif

/*
 * Holder read hook: production dereferences the flash-resident holder
 * word; host tests substitute a slot map (avoids truncating 64-bit
 * host addresses through the 32-bit holder word).
 */
#ifndef OPEN_CFW_STATE_HOLDER_WORD
#define OPEN_CFW_STATE_HOLDER_WORD(addr) \
    ((__UINTPTR_TYPE__)(*(volatile open_cfw_state_word *)(addr)))
#endif

__attribute__((used, noinline))
void open_cfw_state_init_params(
    open_cfw_state_word *first,
    open_cfw_state_word *second,
    open_cfw_state_word *third)
{
    *first = OPEN_CFW_STATE_PARAM_FIRST;
    *second = OPEN_CFW_STATE_PARAM_SECOND;
    *third = OPEN_CFW_STATE_PARAM_THIRD;
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_nibble_to_mode(open_cfw_state_word nibble)
{
    open_cfw_state_word value = nibble - 1U;

    if (value <= 1U) {
        return 4U;
    }
    if (value == 5U) {
        return 0U;
    }
    return 7U;
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_mode_switch(
    open_cfw_state_word next,
    open_cfw_state_word unused2,
    open_cfw_state_word unused3,
    open_cfw_state_word leftover)
{
    volatile open_cfw_state_word *reg =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_CONTROL);
    volatile open_cfw_state_byte *dirty =
        (volatile open_cfw_state_byte *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_DIRTY);
    open_cfw_state_word old = *reg;
    open_cfw_state_word new_nibble = next & 0xFU;
    open_cfw_state_word old_nibble = old & 0xFU;
    open_cfw_state_word new_mode = open_cfw_state_nibble_to_mode(new_nibble);
    open_cfw_state_word old_mode = open_cfw_state_nibble_to_mode(old_nibble);
    int do_new;
    int do_old;

    (void)unused2;
    (void)unused3;
    (void)leftover;
    if ((next & 0xC0000000U) != 0U) {
        do_new = 0;
        do_old = 1;
    } else if ((old & 0xC0000000U) != 0U) {
        do_new = 1;
        do_old = 0;
    } else if (new_mode == old_mode) {
        do_new = 0;
        do_old = 0;
    } else {
        do_new = 1;
        do_old = 1;
    }
    if (do_new != 0 && new_nibble != 0U && new_nibble < 7U) {
        OPEN_CFW_STATE_CHANNEL_A(
            new_mode & 0xFFU, OPEN_CFW_STATE_CHANNEL_ARG);
    }
    *reg = next;
    if (do_old != 0 && old_nibble != 0U && old_nibble < 7U) {
        OPEN_CFW_STATE_CHANNEL_B(
            old_mode & 0xFFU, OPEN_CFW_STATE_CHANNEL_ARG);
    }
    *dirty = 1U;
    return old;
}

__attribute__((used, noinline))
open_cfw_state_byte open_cfw_state_flag_get(void)
{
    volatile open_cfw_state_byte *dirty =
        (volatile open_cfw_state_byte *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_DIRTY);
    volatile open_cfw_state_word *reg =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_CONTROL);
    open_cfw_state_word value;

    if (*dirty == 0U) {
        return 0U;
    }
    value = *reg;
    if ((value & 0xFU) == 0U) {
        return 0U;
    }
    if ((int)value < 0) {
        return 0U;
    }
    return (open_cfw_state_byte)(((value >> 30) & 1U) ^ 1U);
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_sample_vote(void)
{
    open_cfw_state_word *reg =
        (open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_SAMPLE);
    open_cfw_state_word samples[3];

    OPEN_CFW_STATE_SAMPLE_TRIPLE(reg, samples);
    if (samples[0] == samples[1]) {
        return samples[1];
    }
    return samples[2];
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_sample_retry(
    open_cfw_state_word lane,
    open_cfw_state_word limit,
    open_cfw_state_word spare)
{
    open_cfw_state_word *shadow =
        (open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_SHADOW);
    volatile open_cfw_state_word *lanes =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_LANES);
    open_cfw_state_word status = 0U;
    open_cfw_state_word first;
    open_cfw_state_word fresh;
    open_cfw_state_word saved;

    (void)spare;
    first = open_cfw_state_sample_vote();
    if (lane >= OPEN_CFW_STATE_LANE_COUNT) {
        return OPEN_CFW_STATE_BAD_LANE;
    }
    for (;;) {
        fresh = open_cfw_state_sample_vote();
        if (fresh != shadow[lane] && fresh != shadow[lane] + 1U) {
            break;
        }
    }
    saved = OPEN_CFW_STATE_IRQ_DISABLE();
    fresh = open_cfw_state_sample_vote();
    if ((fresh - first + 3U) < limit) {
        limit = first + (limit - fresh) - 3U;
    } else {
        limit = 1U;
        status = OPEN_CFW_STATE_CLAMP_STATUS;
    }
    lanes[lane] = limit;
    fresh = open_cfw_state_sample_vote();
    shadow[lane] = fresh;
    OPEN_CFW_STATE_IRQ_RESTORE(saved);
    return status;
}

__attribute__((used, noinline))
void open_cfw_state_flag_or(open_cfw_state_word bits)
{
    volatile open_cfw_state_word *reg =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_MASK);

    *reg = (open_cfw_state_word)(*reg | bits);
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_latch_store(
    open_cfw_state_word value)
{
    volatile open_cfw_state_word *latch =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_LATCH);
    volatile open_cfw_state_word *reg =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_VALUE);

    *latch = value;
    return *reg;
}

__attribute__((used, noinline))
open_cfw_state_word open_cfw_state_value_get(open_cfw_state_byte select)
{
    volatile open_cfw_state_word *reg =
        (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_VALUE);
    open_cfw_state_word value = *reg;

    if ((open_cfw_state_byte)select != 0U) {
        volatile open_cfw_state_word *mask =
            (volatile open_cfw_state_word *)OPEN_CFW_STATE_HOLDER_WORD(OPEN_CFW_STATE_HOLDER_MASK);
        value &= *mask;
    }
    return value;
}

#ifdef OPEN_CFW_STATE_DEFINE_TEST_HOOKS
#undef OPEN_CFW_STATE_SAMPLE_TRIPLE
#undef OPEN_CFW_STATE_IRQ_DISABLE
#undef OPEN_CFW_STATE_IRQ_RESTORE
#undef OPEN_CFW_STATE_CHANNEL_A
#undef OPEN_CFW_STATE_CHANNEL_B
#endif

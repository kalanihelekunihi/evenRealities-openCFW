/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitution for the AM-040 string/state-helper tranche: stubs
 * the retained libc-locale callees, the C-library SRAM digit table,
 * the IRQ/sample/channel providers, and the flash holder words with
 * host cells instead of the fixed stock addresses. Production macros
 * in the included sources are overridden here before inclusion.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---- retained libc-locale stubs ---- */

int open_cfw_test_str_errno_calls;

static int stub_isspace(int c)
{
    return c == ' ' || (c >= '\t' && c <= '\r');
}

/*
 * Digit-class model: the stock locale mapper accepts both letter cases
 * for hex (the "0X1F" and "0xFFFFFFFFF" cases pin this: uppercase must
 * classify); folding A-Z to a-z reproduces exactly that over the
 * identity class table below. Other mappings stay identity.
 */
static int stub_digit_class(int c)
{
    if (c >= 'A' && c <= 'Z') {
        c += 'a' - 'A';
    }
    return c & 0xFF;
}

static void *stub_table_memchr(const void *table, int value, unsigned int n)
{
    return memchr(table, value, (size_t)n);
}

static void stub_overflow_errno(void)
{
    open_cfw_test_str_errno_calls += 1;
}

#define OPEN_CFW_STR_ISSPACE(c) stub_isspace(c)
#define OPEN_CFW_STR_DIGIT_CLASS(c) stub_digit_class(c)
#define OPEN_CFW_STR_TABLE_MEMCHR(table, value, count) \
    stub_table_memchr((table), (value), (count))
#define OPEN_CFW_STR_OVERFLOW_ERRNO() stub_overflow_errno()

/* ---- host digit table: thresholds + identity class bytes ---- */

static unsigned char open_cfw_test_digit_table[0x28 + 37];

static void open_cfw_test_digit_table_init(void)
{
    static const char classes[] = "0123456789abcdefghijklmnopqrstuvwxyz";
    unsigned int base;
    memcpy(open_cfw_test_digit_table + 0x28, classes, 36);
    open_cfw_test_digit_table[0x28 + 36] = '\0';
    for (base = 2U; base <= 36U; base += 1U) {
        /* Significant-digit count of ULONG_MAX: any sane table agrees,
         * and any threshold at or above it is observationally identical
         * (see the port header note). */
        unsigned int limit = 0xFFFFFFFFU;
        unsigned int digits = 0U;
        do {
            digits += 1U;
            limit /= base;
        } while (limit != 0U);
        open_cfw_test_digit_table[base] = (unsigned char)digits;
    }
}

#define OPEN_CFW_STRTOUL_TABLE \
    ((const unsigned char *)open_cfw_test_digit_table)

/* ---- peripheral-state host cells ---- */

static uint32_t host_control_reg;
static unsigned char host_dirty_byte;
static uint32_t host_lanes[8];
static uint32_t host_mask_reg;
static uint32_t host_value_reg;
static uint32_t host_latch_reg;
static uint32_t host_sample_reg;
static uint32_t host_shadow[8];

static uintptr_t stub_holder_word(unsigned int addr)
{
    switch (addr) {
    case 0x0048D704U:
        return (uintptr_t)&host_control_reg;
    case 0x0048D708U:
        return (uintptr_t)&host_dirty_byte;
    case 0x0048D70CU:
        return (uintptr_t)&host_lanes[0];
    case 0x0048D710U:
        return (uintptr_t)&host_mask_reg;
    case 0x0048D714U:
        return (uintptr_t)&host_value_reg;
    case 0x0048D718U:
        return (uintptr_t)&host_latch_reg;
    case 0x0048D71CU:
        return (uintptr_t)&host_sample_reg;
    case 0x0048D720U:
        return (uintptr_t)&host_shadow[0];
    default:
        abort();
    }
    return 0U;
}

#define OPEN_CFW_STATE_HOLDER_WORD(addr) stub_holder_word(addr)

/* ---- sample / irq / channel stubs ---- */

static uint32_t stub_sample_script[64];
static unsigned int stub_sample_len;
static unsigned int stub_sample_pos;

static void open_cfw_test_sample_reset(void)
{
    stub_sample_len = 0U;
    stub_sample_pos = 0U;
}

static uint32_t stub_sample_next(void)
{
    if (stub_sample_pos >= stub_sample_len) {
        abort();
    }
    return stub_sample_script[stub_sample_pos++];
}

static void stub_sample_triple(uint32_t *reg, uint32_t out[3])
{
    (void)reg;
    out[0] = stub_sample_next();
    out[1] = stub_sample_next();
    out[2] = stub_sample_next();
}

#define OPEN_CFW_STATE_SAMPLE_TRIPLE(reg, out) stub_sample_triple((reg), (out))

static unsigned int stub_irq_disable_calls;
static unsigned int stub_irq_restore_calls;
static unsigned int stub_irq_restore_value;
static uint32_t stub_irq_saved = 1U;

static unsigned int stub_irq_disable(void)
{
    stub_irq_disable_calls += 1U;
    return stub_irq_saved;
}

static void stub_irq_restore(unsigned int saved)
{
    stub_irq_restore_calls += 1U;
    stub_irq_restore_value = saved;
}

#define OPEN_CFW_STATE_IRQ_DISABLE() stub_irq_disable()
#define OPEN_CFW_STATE_IRQ_RESTORE(saved) stub_irq_restore(saved)

static unsigned int stub_channel_a_calls;
static unsigned int stub_channel_b_calls;
static uint32_t stub_channel_a_mode;
static uint32_t stub_channel_a_arg;
static uint32_t stub_channel_b_mode;
static uint32_t stub_channel_b_arg;

static void stub_channel_a(uint32_t mode, uint32_t arg)
{
    stub_channel_a_calls += 1U;
    stub_channel_a_mode = mode;
    stub_channel_a_arg = arg;
}

static void stub_channel_b(uint32_t mode, uint32_t arg)
{
    stub_channel_b_calls += 1U;
    stub_channel_b_mode = mode;
    stub_channel_b_arg = arg;
}

#define OPEN_CFW_STATE_CHANNEL_A(mode, arg) stub_channel_a((mode), (arg))
#define OPEN_CFW_STATE_CHANNEL_B(mode, arg) stub_channel_b((mode), (arg))

void open_cfw_test_state_reset(void)
{
    host_control_reg = 0U;
    host_dirty_byte = 0U;
    memset(host_lanes, 0, sizeof(host_lanes));
    host_mask_reg = 0U;
    host_value_reg = 0U;
    host_latch_reg = 0U;
    host_sample_reg = 0U;
    memset(host_shadow, 0, sizeof(host_shadow));
    open_cfw_test_sample_reset();
    stub_irq_disable_calls = 0U;
    stub_irq_restore_calls = 0U;
    stub_irq_restore_value = 0U;
    stub_irq_saved = 1U;
    stub_channel_a_calls = 0U;
    stub_channel_b_calls = 0U;
    stub_channel_a_mode = 0U;
    stub_channel_a_arg = 0U;
    stub_channel_b_mode = 0U;
    stub_channel_b_arg = 0U;
    open_cfw_test_str_errno_calls = 0;
    open_cfw_test_digit_table_init();
}

#include "../../components/apollo_main/core_overlay/runtime_string_helpers.c"
#include "../../components/apollo_main/core_overlay/runtime_peripheral_state_helpers.c"

/* ---- exported test accessors (ctypes cannot see file statics) ---- */

uintptr_t open_cfw_test_holder(unsigned int addr)
{
    return stub_holder_word(addr);
}

void open_cfw_test_sample_push(unsigned int a, unsigned int b, unsigned int c)
{
    stub_sample_script[stub_sample_len++] = (uint32_t)a;
    stub_sample_script[stub_sample_len++] = (uint32_t)b;
    stub_sample_script[stub_sample_len++] = (uint32_t)c;
}

unsigned int open_cfw_test_irq_disable_calls(void)
{
    return stub_irq_disable_calls;
}

unsigned int open_cfw_test_irq_restore_calls(void)
{
    return stub_irq_restore_calls;
}

unsigned int open_cfw_test_irq_restore_value(void)
{
    return stub_irq_restore_value;
}

unsigned int open_cfw_test_channel_a_calls(void)
{
    return stub_channel_a_calls;
}

unsigned int open_cfw_test_channel_b_calls(void)
{
    return stub_channel_b_calls;
}

int open_cfw_test_str_errno_calls_fn(void)
{
    return open_cfw_test_str_errno_calls;
}

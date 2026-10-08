/* SPDX-License-Identifier: BSD-3-Clause
 * Clean portable models of four startup callback bodies selected by 0x41ce52.
 * They are analysis sources with injected state and providers; not integrated firmware.
 */
#include <stdint.h>
#include <stddef.h>

typedef uint32_t (*info_read_fn)(void *opaque, uint32_t selector,
                                 uint32_t word_offset, uint32_t word_count,
                                 uint32_t *destination);
typedef void (*trim_commit_fn)(void *opaque);

typedef struct {
    uint32_t word[27];
    uint32_t power_control; /* stock 0x400201bc */
    uint32_t kernel_control;/* stock 0x40021008 */
} spot_profile_state;

static int init_blocked(uint32_t power, uint32_t kernel)
{
    return ((power >> 3) & 1U) != 0U && ((kernel >> 27) & 1U) == 0U;
}

/* Stock entry 0x42abbc, exact extent 146 bytes. */
uint32_t spotmgr_init_42abbc_model(spot_profile_state *s,
                                    info_read_fn read_info,
                                    trim_commit_fn commit,
                                    void *opaque)
{
    uint32_t temporary[5];
    uint32_t status;
    if (init_blocked(s->power_control, s->kernel_control)) return 7U;
    status = read_info(opaque, 1U, 0x25cU, 20U, &s->word[1]);
    if (status != 0U) return status;
    status = read_info(opaque, 1U, 0x270U, 5U, temporary);
    if (status != 0U) return status;
    for (uint32_t i = 0; i < 5U; ++i) s->word[21U + i] = temporary[i];
    status = read_info(opaque, 1U, 0x278U, 1U, temporary);
    if (status != 0U) return status;
    s->word[26] = temporary[0];
    s->word[0] = 0x1f01600dU;
    commit(opaque);
    return 0U;
}

static uint32_t insert_bits(uint32_t dst, uint32_t src, unsigned shift,
                            unsigned width)
{
    uint32_t mask = ((1U << width) - 1U) << shift;
    return (dst & ~mask) | ((src << shift) & mask);
}

/* Stock entry 0x42bdf0, exact extent 350 bytes. */
uint32_t hw_state_compose_42bdf0_model(spot_profile_state *s,
                                       info_read_fn read_info,
                                       trim_commit_fn commit,
                                       void *opaque)
{
    uint32_t temporary[4];
    uint32_t one_word;
    uint32_t status;
    if (init_blocked(s->power_control, s->kernel_control)) return 7U;
    status = read_info(opaque, 1U, 0x25cU, 16U, &s->word[1]);
    if (status != 0U) return status;
    for (uint32_t i = 0; i < 4U; ++i)
        s->word[17U + i] = (s->word[5U + i] & ~0x7fU) |
                           (s->word[13U + i] & 0x7fU);
    status = read_info(opaque, 1U, 0x270U, 4U, temporary);
    if (status != 0U) return status;
    for (uint32_t i = 0; i < 4U; ++i) s->word[21U + i] = temporary[i];
    status = read_info(opaque, 1U, 0x278U, 1U, &one_word);
    if (status != 0U) return status;
    s->word[26] = one_word;

    s->word[9] = insert_bits(s->word[9],
        ((((s->word[14] & 0x0fffffffU) >> 21) +
          ((s->word[13] & 0x0fffffffU) >> 21)) / 2U), 21, 7);
    s->word[10] = insert_bits(s->word[10], (s->word[11] >> 21) & 0x7fU, 21, 7);
    s->word[9] = insert_bits(s->word[9], s->word[13] >> 28, 28, 1);
    s->word[10] = insert_bits(s->word[10], s->word[11] >> 28, 28, 1);
    s->word[13] = insert_bits(s->word[13], s->word[14] >> 21, 21, 7);
    s->word[13] = insert_bits(s->word[13], s->word[14] >> 28, 28, 1);
    s->word[13] = insert_bits(s->word[13], s->word[14] >> 17, 17, 4);
    s->word[13] = insert_bits(s->word[13], s->word[14] >> 7, 7, 10);
    s->word[26] = (s->word[26] & 0xfc0fffffU) | 0x01f00000U;
    s->word[0] = 0x1f01600dU;
    commit(opaque);
    return 0U;
}

typedef struct {
    uint32_t revision_word; /* read from 0x4002000c */
    uint32_t variant;       /* read from 0x20000098 */
    uint32_t hw_state_word; /* read from 0x200267f8 + 0x44 */
    uint8_t state_200271b3;
    uint8_t state_200271b4;
    uint8_t state_200271b5;
} boot_flag_state;

/* Stock entry 0x42d6c0, exact extent 222 bytes; it makes no calls. */
uint32_t state_flag_dispatch_42d6c0_model(boot_flag_state *s)
{
    uint32_t revision = s->revision_word & 0xffU;
    uint32_t variant = s->variant;
    uint32_t word = s->hw_state_word;
    s->state_200271b3 = (uint8_t)(revision == 0x21U && variant == 2U);
    s->state_200271b4 = (uint8_t)((revision == 0x21U &&
        (variant == 2U || variant == 3U)) || (revision == 0x22U && variant == 0U));
    if (revision == 0x22U && variant == 1U) {
        s->state_200271b5 = 1U;
    } else if (revision == 0x23U && variant == 0U) {
        uint32_t field = ((word & 0x3fffffffU) >> 25);
        uint32_t special = (word & 0x3fe00000U) == 0x31800000U &&
                           ((word & 0x1fffffU) >> 16) > 0x13U &&
                           (word & 0xffffU) == 0U;
        /* Stock sets one for the invalid general encoding, but zero for the
         * special 0x318... encoding and for a valid general encoding. */
        s->state_200271b5 = (uint8_t)(!special &&
            (field < 0x19U || (word & 0xffffU) != 0U));
    } else {
        s->state_200271b5 = 0U;
    }
    return 0U;
}

/* Stock entry 0x42f670, exact extent 4 bytes. */
uint32_t startup_noop_42f670_model(void)
{
    return 0U;
}

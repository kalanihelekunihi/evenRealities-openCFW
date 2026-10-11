/* SPDX-License-Identifier: MIT
 * C reduction of locked bootloader 0x41c4b4..0x41c7de (810 bytes).
 * Isolated candidate: the product RAM/MMIO bindings and child ABI have not
 * yet been matched against a whole-entry oracle. The current selected caller
 * declares void(void); this Ghidra-derived four-word/64-bit ABI is unresolved
 * and must not be linked to it until raw-register evidence fixes the contract.
 * No stock executable bytes.
 */
#include <stdbool.h>
#include <stdint.h>

/* Pointer cells denoted DAT_0041cb04..DAT_0041cbd0 in the frozen decompile.
 * A product linker/configuration translation unit must supply every field. */
struct boot_power_root_state {
    volatile uint32_t *revision, *control, *initial_gate, *request, *clock;
    volatile uint32_t *info, *trim, *mode_override, *mode_word, *mode_mask;
    volatile uint32_t *clear_word, *supply, *source0, *destination0;
    volatile uint32_t *source1, *destination1, *source2, *destination2;
    volatile uint32_t *source3, *destination3, *source4, *destination4;
    volatile uint32_t *source5, *destination5, *source6, *destination6;
    volatile uint32_t *source7, *destination7, *source8, *destination8;
    volatile uint32_t *source9, *destination9, *source10, *destination10;
    volatile uint32_t *source11, *destination11, *source12, *destination12;
    volatile uint32_t *source13, *destination13, *source14, *destination14;
    volatile uint32_t *source15, *destination15;
    volatile uint32_t *enable0, *enable1, *dispatch_arg, *late_flags;
    volatile uint8_t *initialized, *profile_initialized;
};
extern const struct boot_power_root_state opencfw_boot_product_power_root;

extern uint32_t opencfw_boot_root_prepare(void);                  /* 0x42252e */
extern uint32_t opencfw_boot_root_enable(uint32_t);              /* 0x41c17a */
extern uint32_t opencfw_boot_root_configure(uint32_t);           /* 0x41c9ca */
extern uint32_t opencfw_boot_control_query(uint32_t, uint32_t *);/* 0x41c2d8 */
extern uint32_t opencfw_boot_root_disable(uint32_t);             /* 0x41bf84 */
extern uint32_t opencfw_boot_root_query(uint32_t *);             /* 0x41b918 */
extern uint32_t opencfw_boot_root_prepare_io(void);              /* 0x41c320 */
extern int32_t opencfw_boot_root_info_read(uint32_t,uint32_t,uint32_t,volatile uint32_t *); /* 0x421548 */
extern uint32_t opencfw_boot_root_dispatch(void);               /* 0x41ce52 */
extern uint32_t opencfw_boot_root_mode_apply(volatile uint32_t *);/* 0x41bbd0 */
extern uint32_t opencfw_boot_root_trim_apply(volatile uint32_t *);/* 0x41be36 */
extern uint32_t opencfw_bl_critical_save(void);                 /* 0x41b8ec */
extern uint32_t opencfw_boot_root_commit(void);                 /* 0x41cdca */
extern uint32_t opencfw_boot_root_publish(uint32_t,uint32_t);   /* 0x41cde0 */
extern bool opencfw_boot_current_mode_privileged(void);
extern void opencfw_boot_root_restore_irq(bool);
extern uint32_t opencfw_boot_root_finish(uint32_t);             /* 0x41ce10 */
extern uint32_t opencfw_boot_root_finalize(void);               /* 0x41acb2 */

uint64_t opencfw_boot_startup_power_initialize(uint32_t arg0,
                                                uint32_t arg1,
                                                uint32_t arg2,
                                                uint32_t arg3)
{
    const struct boot_power_root_state *s = &opencfw_boot_product_power_root;
    uint32_t query[3] = {arg1 & 0xffffff00u, 0u, arg3};
    (void)arg0; (void)arg2;
    if ((*s->control & 2u) != 0u) *s->control &= ~4u;
    if (*s->initial_gate == 0u) {
        (void)opencfw_boot_root_prepare();
        (void)opencfw_boot_root_enable(0x1cu);
        *s->request &= ~1u;
        *s->request &= ~0xeu;
    }
    (void)opencfw_boot_root_configure(*s->clock);
    *s->supply |= 1u;
    if ((*s->info & 8u) &&
        ((void)opencfw_boot_control_query(0x1du, query),
         (uint8_t)query[0] == 0u))
        (void)opencfw_boot_root_disable(0x1du);
    (void)opencfw_boot_root_query(&query[1]);
    int32_t status = (int32_t)opencfw_boot_root_prepare_io();
    if (*s->trim != *s->mode_override) {
        status = opencfw_boot_root_info_read(1u, 0x210u, 1u, s->trim + 13);
        if (status == 0)
            status = opencfw_boot_root_info_read(1u, 0x245u, 1u, s->trim + 17);
    }
    if (status == 0 || *s->trim == *s->mode_override) {
        (void)opencfw_boot_root_dispatch();
        (void)opencfw_boot_root_enable(0x17u);
        (void)opencfw_boot_root_enable(0x1du);
        if ((*s->revision & 0xffu) > 0x21u) *s->mode_word = 1u;
        (void)opencfw_boot_root_mode_apply(s->mode_word);
        (void)opencfw_boot_root_trim_apply(s->mode_mask);
        *s->clear_word = (*s->clear_word | 0xf80000u | *s->source0) & ~0x4000u;
        *s->destination0 = 0u;
        *s->source1 = (*s->source1 & 0xffff00ffu) | 0x400u;
        if (*s->profile_initialized == 0u) {
            *s->destination1 = (*s->source2 & 0x3ffffffu) >> 20;
            *s->destination2 = *s->source3 & 0x3fu;
            *s->destination3 = *s->source2 >> 26;
            *s->destination4 = (*s->source3 & 0xffffffu) >> 18;
            *s->destination5 = *s->source4 & 0x7fu;
            *s->destination6 = *s->source5 & 0x7fu;
            *s->destination7 = (*s->source6 & 0x7fffffffu) >> 29;
            *s->destination8 = (*s->source7 & 0x3fffu) >> 10;
            *s->destination9 = *s->source7 & 0x3ffu;
            uint32_t revision = *s->revision & 0xffu;
            uint32_t variant = *s->source9;
            if (((*s->source8 & 0x3fu) >> 4) == 3u &&
                ((revision == 0x21u && variant != 0u) || revision > 0x21u)) {
                if ((revision == 0x21u && variant > 2u) ||
                    (revision == 0x22u && variant == 1u) ||
                    (revision == 0x23u && variant == 0u))
                    *s->destination9 += 7u;
                else if ((revision == 0x21u && variant < 3u) ||
                         (revision == 0x22u && variant == 0u))
                    *s->destination9 += 6u;
            }
            *s->destination10 = *s->source10;
            *s->destination11 = (*s->source11 & 0x3fffffffu) >> 25;
            *s->destination12 = (*s->source11 & 0xffffu) >> 11;
            *s->destination13 = (*s->source12 & 0x3fffffffu) >> 25;
            *s->destination14 = (*s->source12 & 0xffffu) >> 11;
            *s->destination15 = (*s->source13 & 0x1fffu) >> 8;
            *s->source14 = (*s->source15 & 0x3fffffu) >> 17;
            *s->profile_initialized = 1u;
        }
        *s->enable0 |= 0x40000000u;
        *s->enable1 |= 0x11000u;
        query[2] = opencfw_bl_critical_save();
        (void)opencfw_boot_root_commit();
        (void)opencfw_boot_root_publish(0u, *s->dispatch_arg);
        if (opencfw_boot_current_mode_privileged())
            opencfw_boot_root_restore_irq((query[2] & 1u) != 0u);
        (void)opencfw_boot_root_finish(query[2]);
        (void)opencfw_boot_root_finalize();
        if ((*s->revision & 0xffu) > 0x21u) *s->late_flags |= 6u;
        status = 0;
    }
    return ((uint64_t)query[0] << 32) | (uint32_t)status;
}

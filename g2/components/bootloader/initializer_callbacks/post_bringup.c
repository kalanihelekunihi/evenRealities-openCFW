/* SPDX-License-Identifier: MIT */
#include <stdint.h>

struct post_bringup_row {
    uint32_t kind;
    uint32_t context;
    volatile const uint32_t *register_config;
    uint32_t transfer;
    volatile const uint32_t *extended_config;
    uint32_t reserved14;
    volatile uint8_t initialized;
    uint8_t reserved19[3];
};

extern uint32_t opencfw_bl_power_register_update(uint32_t id, uint32_t value);
extern uint32_t opencfw_bl_register_mode(uint32_t kind, uint32_t mode);
extern uint32_t opencfw_bl_post_context_register(uint32_t id,
                                                 const void *context);
extern uint32_t opencfw_bl_post_configure(uint32_t transfer,
                                         uint32_t a, uint32_t b);
extern uint32_t opencfw_bl_post_validate(uint32_t transfer,
                                         uint32_t context);
extern uint32_t opencfw_bl_post_activate(uint32_t transfer,
                                         uint32_t a, uint32_t b,
                                         uint32_t c, uint32_t d);
extern uint32_t opencfw_bl_post_enable(uint32_t kind);
extern uint32_t opencfw_bl_post_precommit(uint32_t kind);
extern uint32_t opencfw_bl_post_finish(uint32_t context, uint32_t code);
extern uint32_t opencfw_bl_post_record_initialized(uint32_t index);

#define POST_TABLE ((volatile struct post_bringup_row *)0x20000454u)
#define SPECIAL_REGISTER_ID (*(volatile const uint32_t *)0x43419cu)

static int32_t signed_kind(uint32_t kind)
{
    return (int16_t)(kind + 0x0fu);
}

/* Reconstructed 0x41f612.  The four-row RAM table and hardware/framework
 * callees are supplied as explicit fixtures/providers by the differential
 * profile; this source owns iteration, guards, call order, status folding,
 * and the initialized byte store. */
uint32_t opencfw_bl_post_bringup_setup(void)
{
    uint32_t status = 0u;
    for (uint32_t index = 0; index < 4u; ++index) {
        volatile struct post_bringup_row *const row = &POST_TABLE[index];
        if (row->register_config == 0 || row->transfer == 0)
            continue;

        status |= opencfw_bl_post_context_register(
            row->kind, (const void *)&row->context);

        if (index == 2u) {
            status |= opencfw_bl_power_register_update(
                row->register_config[0], SPECIAL_REGISTER_ID);
        } else {
            status |= opencfw_bl_power_register_update(
                row->register_config[0], row->register_config[2]);
        }

        const volatile uint32_t *const registers = row->register_config;
        status |= opencfw_bl_power_register_update(registers[1], registers[3]);
        status |= opencfw_bl_post_configure(row->context, 0u, 0u);
        status |= opencfw_bl_post_validate(row->context, row->transfer);

        const volatile uint32_t *const extended = row->extended_config;
        const uint32_t activation = opencfw_bl_post_activate(
            row->context, extended[1], extended[0], 0u, 0u);
        status |= activation;
        (void)opencfw_bl_post_enable((uint32_t)signed_kind(row->kind));

        if (index == 0u)
            (void)opencfw_bl_register_mode((uint32_t)signed_kind(row->kind),
                                           3u);
        else
            (void)opencfw_bl_register_mode((uint32_t)signed_kind(row->kind),
                                           4u);
        (void)opencfw_bl_post_precommit((uint32_t)signed_kind(row->kind));
        status = opencfw_bl_post_finish(row->context, 0x471u) | status;
        row->initialized = 1u;
        (void)opencfw_bl_post_record_initialized(index);
    }
    return status != 0u;
}

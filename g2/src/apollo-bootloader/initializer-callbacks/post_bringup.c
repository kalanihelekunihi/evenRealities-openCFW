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
extern uint32_t am_hal_uart_initialize(uint32_t id,
                                                 const void *context);
extern uint32_t am_hal_uart_power_control(uint32_t context,
                                          uint32_t state, uint32_t retain);
extern uint32_t am_hal_uart_configure(uint32_t transfer,
                                         uint32_t context);
extern uint32_t am_hal_uart_buffer_configure(uint32_t transfer,
                                         uint32_t a, uint32_t b,
                                         uint32_t c, uint32_t d);
extern uint32_t opencfw_bl_post_enable(uint32_t kind);
extern uint32_t opencfw_bl_post_precommit(uint32_t kind);
extern uint32_t am_hal_uart_interrupt_enable(uint32_t context, uint32_t code);
extern uint32_t opencfw_bl_post_record_initialized(uint32_t index);

#define POST_TABLE ((volatile struct post_bringup_row *)0x20000454u)
extern const uint32_t opencfw_boot_post_special_register_value;
#define SPECIAL_REGISTER_ID opencfw_boot_post_special_register_value

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

        status |= am_hal_uart_initialize(
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
        status |= am_hal_uart_power_control(row->context, 0u, 0u);
        status |= am_hal_uart_configure(row->context, row->transfer);

        const volatile uint32_t *const extended = row->extended_config;
        const uint32_t activation = am_hal_uart_buffer_configure(
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
        status = am_hal_uart_interrupt_enable(row->context, 0x471u) | status;
        row->initialized = 1u;
        (void)opencfw_bl_post_record_initialized(index);
    }
    return status != 0u;
}

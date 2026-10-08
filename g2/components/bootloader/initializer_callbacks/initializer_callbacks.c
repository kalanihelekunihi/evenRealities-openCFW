/* SPDX-License-Identifier: MIT.
 * Source bodies for three callbacks stored in the locked initializer table.
 * Their platform leaf routines remain named external APIs in this profile.
 */
#include "initializer_callbacks.h"

#include "gpio_descriptors.h"
extern uint32_t opencfw_bl_mode_register_update(uint32_t register_id,
                                                uint32_t value);
extern void opencfw_bl_platform_bringup(void);
extern void opencfw_bl_post_bringup_setup(void);
extern void opencfw_bl_platform_finish(void);

extern uint32_t opencfw_boot_services_initialize(uint32_t initial_state);
extern void opencfw_boot_services_pin_configure(uint32_t pin, uint32_t value);
extern void opencfw_boot_services_finalize(void);

extern uintptr_t opencfw_bl_mutex_create(const void *attributes);
extern void opencfw_bl_logger_output(int level, const char *function,
                                     const char *file, const char *tag,
                                     int line, const char *message, ...);
extern void opencfw_bl_service_mode(uint32_t mode);
extern uint32_t opencfw_bl_service_guard(void);
extern void opencfw_bl_service_reset(uint32_t value);
extern void opencfw_bl_service_enable(uint32_t value);
extern void opencfw_bl_service_configure(uint32_t value);
extern void opencfw_bl_service_commit(void);
extern void opencfw_bl_service_wake(void);
extern void opencfw_bl_service_sleep(void);
extern void opencfw_bl_invalid_pin_configure(uint32_t pin, uint32_t value);

#define SERVICES_STATE ((volatile uint8_t *)(uintptr_t)0x20026700u)

void opencfw_boot_services_reset(uint32_t value);
void opencfw_boot_services_enable(uint32_t value);
void opencfw_boot_services_configure(uint32_t selector);
void opencfw_boot_services_pin_configure(uint32_t pin, uint32_t value);

/* Leaf wrapper at 0x4303bc, reached by the initializer's mode-1 branch. */
__attribute__((used, noinline, naked))
static uint32_t mode_register_update_wrapper(
    uint32_t mode __attribute__((unused)),
    uint32_t enabled __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "uxtb r1, r1\n"
        "cmp r1, #1\n"
        "bne 1f\n"
        "movs r1, #1\n"
        "b 2f\n"
        "1: movs r1, #0\n"
        "2: bl opencfw_bl_mode_register_update\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "movs r0, #0\n"
        "mvns r0, r0\n"
        "b 4f\n"
        "3: movs r0, #0\n"
        "4: pop {r1, pc}\n");
}

/* Exact 0x42ff00 branch reached by the initializer's fixed (1, 1) call. */
__attribute__((used, noinline))
static void mode_apply_initializer_route(void)
{
    (void)mode_register_update_wrapper(0x81u, 1u);
}

/* Exact wrapper behavior at 0x42fff2 for this recovered route. */
__attribute__((naked)) static void mode_apply_wrapper(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r1, #1\n"
        "movs r0, #1\n"
        "bl mode_apply_initializer_route\n"
        "pop {r0, pc}\n");
}

uint32_t opencfw_boot_init_callback_platform_sequence(void)
{
    opencfw_bl_descriptor_register((const void *)(uintptr_t)0x42f674u, 0x61u);
    mode_apply_wrapper();
    opencfw_bl_platform_bringup();
    opencfw_bl_post_bringup_setup();
    opencfw_bl_platform_finish();
    return 0u;
}

uint32_t opencfw_boot_init_callback_services(void)
{
    (void)opencfw_boot_services_initialize(0u);
    opencfw_boot_services_pin_configure(0u, 0xffu);
    opencfw_boot_services_pin_configure(1u, 0xd7u);
    opencfw_boot_services_pin_configure(2u, 0xd7u);
    opencfw_boot_services_pin_configure(3u, 0xd7u);
    opencfw_boot_services_pin_configure(4u, 0xd7u);
    opencfw_boot_services_pin_configure(5u, 0xd7u);
    opencfw_boot_services_finalize();
    return 0u;
}

uint32_t opencfw_boot_services_initialize(uint32_t initial_state)
{
    (void)initial_state;
    if (SERVICES_STATE[0xf0] == 1u)
        return 0u;

    const uint32_t status = opencfw_bl_service_guard();
    if ((uint8_t)status != 0u)
        return (uint8_t)status;

    opencfw_boot_services_reset(1u);
    SERVICES_STATE[0xf3] = 0u;
    SERVICES_STATE[0xf4] = 0u;
    opencfw_boot_services_enable(1u);
    opencfw_boot_services_configure(5u);
    opencfw_bl_service_commit();
    SERVICES_STATE[0xf0] = 1u;
    return (uint8_t)status;
}

void opencfw_boot_services_reset(uint32_t value)
{
    SERVICES_STATE[0xf2] = (uint8_t)value;
    if (SERVICES_STATE[0xf2] == 0u)
        return;
    if (SERVICES_STATE[0xf4] == 0u && SERVICES_STATE[0xf3] != 0u)
        opencfw_bl_service_wake();
    else if (SERVICES_STATE[0xf4] != 0u && SERVICES_STATE[0xf3] == 0u)
        opencfw_bl_service_sleep();
}

void opencfw_boot_services_enable(uint32_t value)
{
    const uint8_t selected = (uint8_t)value;
    if (selected > 1u) {
        opencfw_bl_service_enable(selected);
        return;
    }
    SERVICES_STATE[0xf5] = selected;
}

void opencfw_boot_services_configure(uint32_t selector)
{
    const uint8_t selected = (uint8_t)selector;
    if (selected >= 6u) {
        opencfw_bl_service_configure(selected);
        return;
    }
    SERVICES_STATE[0] = selected;
}

void opencfw_boot_services_pin_configure(uint32_t pin, uint32_t value)
{
    const uint8_t selected = (uint8_t)pin;
    if (selected >= 6u) {
        opencfw_bl_invalid_pin_configure(pin, value);
        return;
    }
    *(volatile uint32_t *)(void *)(SERVICES_STATE + 0xd8u +
                                   (uint32_t)selected * 4u) = value;
}

static void services_set_mode(uint32_t mode)
{
    if ((uint8_t)mode <= 1u)
        SERVICES_STATE[0xf1] = (uint8_t)mode;
    else
        opencfw_bl_service_mode(mode);
}

void opencfw_boot_services_finalize(void)
{
    if (SERVICES_STATE[0xf0] == 0u)
        return;

    services_set_mode(1u);
    opencfw_bl_logger_output(3,
        (const char *)(uintptr_t)0x43406cu,
        (const char *)(uintptr_t)0x430ec0u,
        (const char *)(uintptr_t)0x433f38u, 0xf7,
        (const char *)(uintptr_t)0x432ac4u,
        (const char *)(uintptr_t)0x434074u);
}

uint32_t opencfw_boot_init_callback_redirect(void)
{
    volatile uint32_t *const redirect_mutex =
        (volatile uint32_t *)(uintptr_t)0x2002712cu;
    volatile uint32_t *const protection_mutex =
        (volatile uint32_t *)(uintptr_t)0x20027130u;
    const uintptr_t redirect = opencfw_bl_mutex_create(0);
    *redirect_mutex = (uint32_t)redirect;
    const uintptr_t protection = opencfw_bl_mutex_create(0);
    *protection_mutex = (uint32_t)protection;

    if (redirect == 0u || protection == 0u) {
        opencfw_bl_logger_output(1,
            (const char *)(uintptr_t)0x433fd4u,
            (const char *)(uintptr_t)0x431258u,
            (const char *)(uintptr_t)0x433e68u, 0x271,
            (const char *)(uintptr_t)0x432808u);
        return UINT32_MAX;
    }
    opencfw_bl_logger_output(3,
        (const char *)(uintptr_t)0x433fd4u,
        (const char *)(uintptr_t)0x431258u,
        (const char *)(uintptr_t)0x433e68u, 0x275,
        (const char *)(uintptr_t)0x432bdcu);
    return 0u;
}

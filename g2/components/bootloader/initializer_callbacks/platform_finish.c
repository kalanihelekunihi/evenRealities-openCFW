/* SPDX-License-Identifier: MIT */
#include <stdint.h>

struct platform_context_row {
    uint32_t context;
    uint32_t transfer;
    volatile const uint32_t *configuration;
    uint32_t instance;
};

extern uint32_t opencfw_bl_mutex_create(const void *attributes);
extern void opencfw_bl_context_claim(uint32_t context, const void *row);
extern uint32_t opencfw_bl_power_register_update(uint32_t id, uint32_t value);
extern void opencfw_bl_config_transaction(uint32_t transfer, uint32_t a,
                                          uint32_t b);
extern void opencfw_bl_instance_configure(uint32_t transfer,
                                          uint32_t instance);
extern uint32_t opencfw_bl_context_enable(uint32_t transfer);
extern void opencfw_bl_config_retry(uint32_t index);
extern void opencfw_bl_context_interrupt_enable(uint32_t handle, uint32_t mask);
extern void opencfw_bl_context_nvic_enable(uint32_t interrupt);
extern uint32_t opencfw_bl_semaphore_create(uint32_t maximum,
                                            uint32_t initial,
                                            uint32_t attributes);
extern void opencfw_bl_logger_output(int level, const char *function,
                                     const char *file, const char *tag,
                                     int line, const char *message, ...);

#define CONTEXT_TABLE ((volatile struct platform_context_row *)0x20000374u)
#define CONTEXT_HANDLES ((volatile uint32_t *)0x20026ed8u)
#define I2C_SEMAPHORE (*(volatile uint32_t *)0x20027104u)

/* Reconstructed stock body 0x430502..0x43060f.  HAL operations remain named
 * external providers; this function owns the loop, predicates, stores and
 * status branches. */
uint32_t opencfw_bl_platform_finish(void)
{
    uint32_t status = 0u;
    for (uint32_t index = 0; index < 8u; ++index) {
        volatile struct platform_context_row *const row =
            &CONTEXT_TABLE[index];
        if (row->configuration == 0 || row->instance == 0u)
            continue;

        if (CONTEXT_HANDLES[index] == 0u) {
            const uint32_t handle = opencfw_bl_mutex_create(0);
            CONTEXT_HANDLES[index] = handle;
            if (handle == 0u)
                return 1u;
        }

        opencfw_bl_context_claim(row->context, (const void *)&row->transfer);
        const volatile uint32_t *const config = row->configuration;
        if (opencfw_bl_power_register_update(config[0], config[2]) != 0u)
            return 1u;
        if (opencfw_bl_power_register_update(config[1], config[3]) != 0u)
            return 1u;
        opencfw_bl_config_transaction(row->transfer, 0u, 0u);
        opencfw_bl_instance_configure(row->transfer, row->instance);
        status = opencfw_bl_context_enable(row->transfer);
        opencfw_bl_config_retry(index);
    }

    /* Stock 0x4305ca loads table+0x44: row 4 transfer, not instance. */
    opencfw_bl_context_interrupt_enable(CONTEXT_TABLE[4].transfer, 0xffu);
    opencfw_bl_context_nvic_enable(10u);
    I2C_SEMAPHORE = opencfw_bl_semaphore_create(1u, 0u, 0u);
    if (I2C_SEMAPHORE == 0u) {
        opencfw_bl_logger_output(1,
            (const char *)(uintptr_t)0x4340a4u,
            (const char *)(uintptr_t)0x43164cu,
            (const char *)(uintptr_t)0x433f74u, 0x131,
            (const char *)(uintptr_t)0x4322c8u);
        status = 1u;
    }
    return status;
}

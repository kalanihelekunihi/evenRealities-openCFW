/* SPDX-License-Identifier: MIT
 * Readable candidates for the NOR initializer's MSPI setup at 0x420254 and
 * internal handle-state constructor at 0x424a5a. Register/HAL/RTOS operations
 * remain explicit providers at their original addresses.
 */
#include "nor_mspi_init.h"
#include <stddef.h>

#define OPENCFW_MSPI_SLOT_RECORDS UINT32_C(0x20026fd0)
#define OPENCFW_MSPI_HANDLE_SLOT  UINT32_C(0x200270dc)
#define OPENCFW_MSPI_STATE_BASE   UINT32_C(0x2001caa0)
#define OPENCFW_DEFAULT_DEVICE    UINT32_C(0x20000224)
#define OPENCFW_DEFAULT_MODE      UINT32_C(0x2000020c)
#define OPENCFW_TCB_BASE          UINT32_C(0x200f4c00)

enum {
    OPENCFW_STATUS_OUT_OF_RANGE = 5,
    OPENCFW_STATUS_INVALID_ARG = 6,
    OPENCFW_STATUS_INVALID_OPERATION = 7,
    OPENCFW_MSPI_MODULE_COUNT = 4,
    OPENCFW_MSPI_STATE_STRIDE = 0x8d0,
    OPENCFW_MSPI_INTERRUPTS = 0x1a80
};

typedef struct {
    uint32_t tcb_words;
    uint32_t *tcb;
    uint8_t clock_on_d4;
    uint8_t reserved[3];
} opencfw_mspi_config_t;

_Static_assert(sizeof(void *) == 4, "stock code is 32-bit");
_Static_assert(sizeof(opencfw_mspi_config_t) == 12,
               "stock MSPI config is 12 bytes");
_Static_assert(offsetof(opencfw_mspi_config_t, tcb) == 4,
               "MSPI TCB pointer offset");
_Static_assert(offsetof(opencfw_mspi_config_t, clock_on_d4) == 8,
               "MSPI clock option offset");

extern uint32_t opencfw_hal_power_control(uint32_t handle, uint32_t state,
                                          uint32_t retain);
extern uint32_t opencfw_hal_mspi_configure(uint32_t handle,
                                           const opencfw_mspi_config_t *config);
extern uint32_t opencfw_hal_mspi_device_configure(uint32_t handle,
                                                  const void *device_config);
extern uint32_t opencfw_hal_mspi_enable(uint32_t handle);
extern uint32_t opencfw_hal_mspi_deinitialize(uint32_t handle);
extern uint32_t opencfw_hal_mspi_interrupt_clear(uint32_t handle,
                                                 uint32_t mask);
extern uint32_t opencfw_hal_mspi_interrupt_enable(uint32_t handle,
                                                  uint32_t mask);
extern uint32_t opencfw_hal_mspi_control_latency(uint8_t enabled);
extern uint32_t opencfw_publish_mspi_mode(uint32_t module, uint32_t mode);
extern uint32_t opencfw_read_mspi_register_id(uint32_t register_id,
                                              uint32_t *value);
extern void opencfw_bl_interrupt_priority(uint32_t interrupt,
                                          uint32_t priority);
extern void opencfw_bl_interrupt_enable(uint32_t interrupt);
extern uint32_t opencfw_bl_irq_guard_initialize(void);
extern void opencfw_bl_log(uint32_t level, const char *module,
                           const char *file, const char *function,
                           uint32_t line, const char *format, ...);

static const char log_module[] = "drv.norflash";
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char init_function[] = "am_devices_norflash_qspi_init";
static const char power_failed[] = "Error - Failed to power on MSPI.\n";
static const char configure_failed[] = "Error - Failed to configure MSPI.\n";
static const char device_configure_failed[] =
    "Error - Failed to configure MSPI device.\n";
static const char enable_failed[] = "Error - Failed to enable MSPI.\n";
static const char interrupt_enable_failed[] =
    "Error - Failed to enable interrupt .\n";
static const char initialized[] = "MX25U25643G mSPI interface initialized.";

uint32_t opencfw_provider_424a5a(uint32_t module, void **handle_out)
{
    if (module >= OPENCFW_MSPI_MODULE_COUNT)
        return OPENCFW_STATUS_OUT_OF_RANGE;
    if (handle_out == NULL)
        return OPENCFW_STATUS_INVALID_ARG;

    volatile uint32_t *const state = (volatile uint32_t *)(uintptr_t)
        (OPENCFW_MSPI_STATE_BASE + module * OPENCFW_MSPI_STATE_STRIDE);
    if ((int32_t)(state[0] << 7) < 0)
        return OPENCFW_STATUS_INVALID_OPERATION;

    state[0] = (state[0] & UINT32_C(0xff000000)) | UINT32_C(0x01000000);
    state[0] = (state[0] & UINT32_C(0xff000000)) | UINT32_C(0x00bebebe);
    state[1] = module;
    *(volatile uint8_t *)(uintptr_t)((uintptr_t)state + 0x0cu) = 0u;
    *(volatile uint32_t *)(uintptr_t)((uintptr_t)state + 0x18u) = 0u;
    *(volatile uint8_t *)(uintptr_t)((uintptr_t)state + 0x8c9u) = 7u;
    *(volatile uint32_t *)(uintptr_t)((uintptr_t)state + 0x8ccu) = 8u;
    *handle_out = (void *)state;
    return 0u;
}

uint32_t opencfw_provider_420254(uint32_t module,
                                 const void *device_config,
                                 void **current_device_out,
                                 uint32_t reserved)
{
    (void)reserved;
    volatile uint8_t *const slot =
        (volatile uint8_t *)(uintptr_t)OPENCFW_MSPI_SLOT_RECORDS;
    if (slot[0x0cu] != 0u)
        return UINT32_MAX;

    uint32_t status = opencfw_provider_424a5a(module,
        (void **)(uintptr_t)OPENCFW_MSPI_HANDLE_SLOT);
    if (status != 0u)
        return status;

    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_MSPI_HANDLE_SLOT;
    status = opencfw_hal_power_control(handle, 0u, 0u);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, source_file, init_function, 0x22au,
                       power_failed);
        return 1u;
    }

    const opencfw_mspi_config_t base_config = {
        .tcb_words = 0x100u,
        .tcb = (uint32_t *)(uintptr_t)OPENCFW_TCB_BASE,
        .clock_on_d4 = 0u,
        .reserved = {0u, 0u, 0u}
    };
    status = opencfw_hal_mspi_configure(handle, &base_config);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, source_file, init_function, 0x233u,
                       configure_failed);
        (void)opencfw_hal_mspi_deinitialize(handle);
        return status;
    }

    const void *const config = device_config != NULL ? device_config :
        (const void *)(uintptr_t)OPENCFW_DEFAULT_DEVICE;
    status = opencfw_hal_mspi_device_configure(handle, config);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, source_file, init_function, 0x23fu,
                       device_configure_failed);
        (void)opencfw_hal_mspi_deinitialize(handle);
        return status;
    }

    status = opencfw_hal_mspi_enable(handle);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, source_file, init_function, 0x246u,
                       enable_failed);
        (void)opencfw_hal_mspi_deinitialize(handle);
        return status;
    }

    (void)opencfw_hal_mspi_control_latency(0u);
    (void)opencfw_publish_mspi_mode(module, 0x10u);
    uint32_t ignored_register_value = 0u;
    (void)opencfw_read_mspi_register_id(0x67u, &ignored_register_value);

    status = opencfw_hal_mspi_interrupt_clear(handle,
                                               OPENCFW_MSPI_INTERRUPTS);
    if (status != 0u)
        return 1u;
    status = opencfw_hal_mspi_interrupt_enable(handle,
                                                OPENCFW_MSPI_INTERRUPTS);
    if (status != 0u) {
        opencfw_bl_log(1u, log_module, source_file, init_function, 0x269u,
                       interrupt_enable_failed);
        return 1u;
    }

    opencfw_bl_interrupt_priority(0x15u, 4u);
    opencfw_bl_interrupt_enable(0x15u);
    (void)opencfw_bl_irq_guard_initialize();

    volatile uint32_t *const record =
        (volatile uint32_t *)(uintptr_t)OPENCFW_MSPI_SLOT_RECORDS;
    record[0] = module;
    const uint8_t device_mode = *(const volatile uint8_t *)(uintptr_t)
        ((uintptr_t)(device_config != NULL ? device_config :
            (const void *)(uintptr_t)OPENCFW_DEFAULT_MODE) + 8u);
    record[1] = device_mode;
    record[2] = handle;
    *(volatile uint8_t *)(uintptr_t)((uintptr_t)record + 0x0cu) = 1u;
    *current_device_out = (void *)record;
    opencfw_bl_log(3u, log_module, source_file, init_function, 0x27au,
                   initialized);
    return 0u;
}

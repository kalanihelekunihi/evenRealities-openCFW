/* SPDX-License-Identifier: MIT
 * Readable candidates for reset-command, read-mode, and timing-wrapper paths.
 * MSPI MMIO/RTOS operations and the timing-scan algorithm remain providers.
 */
#include "nor_commands.h"
#include <stddef.h>

#define OPENCFW_ACTIVE_HANDLE_SLOT UINT32_C(0x200270dc)
#define OPENCFW_CURRENT_DEVICE     UINT32_C(0x200270d8)
#define OPENCFW_TIMING_CONTROL     UINT32_C(0x2000023c)
#define OPENCFW_READ_DEVICE_CONFIG UINT32_C(0x2000020c)
#define OPENCFW_NOR_ADDRESS_LIMIT UINT32_C(0x02000000)
#define OPENCFW_TRANSFER_TIMEOUT_USEC UINT32_C(1000000)
#define OPENCFW_TRANSFER_ERROR_MODULE UINT32_C(0x00431468)

enum {
    OPENCFW_STATUS_INVALID_HANDLE = 2,
    OPENCFW_STATUS_OUT_OF_RANGE = 5,
    OPENCFW_STATUS_INVALID_ARGUMENT = 6,
    OPENCFW_MSPI_RX = 0,
    OPENCFW_MSPI_TX = 1
};

typedef struct {
    uint32_t byte_count;
    uint8_t scrambling;
    uint8_t dcx;
    uint8_t direction;
    uint8_t send_address;
    uint32_t device_address;
    uint8_t send_instruction;
    uint8_t reserved_13;
    uint16_t device_instruction;
    uint8_t turnaround;
    uint8_t write_latency;
    uint8_t continuation;
    uint8_t reserved_19;
    void *buffer;
} opencfw_mspi_pio_transfer_t;

_Static_assert(sizeof(void *) == 4, "stock MSPI descriptor uses 32-bit pointers");
_Static_assert(sizeof(opencfw_mspi_pio_transfer_t) == 24,
               "stock PIO descriptor is 24 bytes");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, direction) == 6,
               "direction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, device_address) == 8,
               "address offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t,
                        device_instruction) == 14,
               "instruction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, buffer) == 20,
               "buffer offset");

extern uint32_t opencfw_bl_mspi_blocking_transfer(uint32_t handle,
    const opencfw_mspi_pio_transfer_t *transfer, uint32_t timeout_usec);
extern void opencfw_bl_transfer_error(uint32_t module, uint16_t instruction,
    uint32_t address, uint32_t length, uint32_t status);
extern void opencfw_bl_delay(uint32_t raw_argument);
extern void opencfw_bl_log(uint32_t level, const char *module,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);
extern uint32_t opencfw_hal_mspi_disable(uint32_t handle);
extern uint32_t opencfw_hal_mspi_device_configure(uint32_t handle,
    const void *device_config);
extern uint32_t opencfw_hal_mspi_enable(uint32_t handle);
extern uint32_t opencfw_hal_mspi_control(uint32_t handle, uint32_t request,
    void *value);
extern uint32_t opencfw_hal_mspi_control_latency(uint8_t enabled);
extern uint32_t opencfw_publish_device_mode(uint32_t module, uint8_t mode);
extern uint32_t opencfw_provider_420002(uint8_t *six_byte_timing);

static const char nor_module[] = "drv.norflash";
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char soft_reset_function[] = "DRV_Mx25u25643g_SoftReset";
static const char reset_enable_failed[] = "mx25u25643g RSTEN error\n";
static const char reset_command_failed[] =
    "Write enable failed before sector erase\n";
static const char timing_function[] = "mspi_timing_auto_check";
static const char timing_success[] =
    "Time scan success, use scan timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d";
static const char timing_failure[] =
    "Time scan failed, use default timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d";
static const char reconfigure_function[] =
    "am_devices_mspi_device_reconfigure";
static const char disable_failed[] = "Error - Failed to disable mspi.\n";
static const char configure_failed[] = "Error - Failed to configure mspi.\n";
static const char reconfigure_failed[] =
    "Failed to reconfigure serail mode\n";
static const char control_failed[] = "Failed to control serail mode\n";
static const char reconfigure_function_name[] =
    "mx25u25643g_set_serail_mode";

uint32_t opencfw_provider_42069e(uint32_t instruction,
                                uint32_t address,
                                uint32_t send_address,
                                void *buffer,
                                uint32_t length)
{
    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_ACTIVE_HANDLE_SLOT;
    if (handle == 0u)
        return OPENCFW_STATUS_INVALID_HANDLE;
    if (address >= OPENCFW_NOR_ADDRESS_LIMIT || length >= 0x101u)
        return OPENCFW_STATUS_OUT_OF_RANGE;

    const uint8_t transmit_address = (uint8_t)send_address;
    const opencfw_mspi_pio_transfer_t transfer = {
        .byte_count = length,
        .scrambling = 0u,
        .dcx = 0u,
        .direction = OPENCFW_MSPI_TX,
        .send_address = transmit_address != 0u ? 1u : 0u,
        .device_address = transmit_address != 0u ? address : 0u,
        .send_instruction = 1u,
        .reserved_13 = 0u,
        .device_instruction = (uint16_t)instruction,
        .turnaround = 0u,
        .write_latency = 0u,
        .continuation = 0u,
        .reserved_19 = 0u,
        .buffer = buffer
    };
    const uint32_t status = opencfw_bl_mspi_blocking_transfer(
        handle, &transfer, OPENCFW_TRANSFER_TIMEOUT_USEC);
    if (status != 0u)
        opencfw_bl_transfer_error(OPENCFW_TRANSFER_ERROR_MODULE,
            (uint16_t)instruction, address, length, status);
    return status;
}

void opencfw_provider_42052a(void)
{
    uint32_t status = opencfw_provider_42069e(0x66u, 0u, 0u, NULL, 0u);
    if (status != 0u)
        opencfw_bl_log(1u, nor_module, source_file, soft_reset_function,
            0x2c4u, reset_enable_failed);

    opencfw_bl_delay(1u);
    status = opencfw_provider_42069e(0x99u, 0u, 0u, NULL, 0u);
    if (status != 0u)
        opencfw_bl_log(1u, nor_module, source_file, soft_reset_function,
            0x2c9u, reset_command_failed);
    opencfw_bl_delay(0x32u);
}

uint32_t opencfw_provider_420e08(const void *device_config)
{
    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_ACTIVE_HANDLE_SLOT;
    uint32_t status = opencfw_hal_mspi_disable(handle);
    if (status != 0u) {
        opencfw_bl_log(2u, nor_module, source_file,
            reconfigure_function, 0x58au, disable_failed);
        return 1u;
    }
    status = opencfw_hal_mspi_device_configure(handle, device_config);
    if (status != 0u) {
        opencfw_bl_log(2u, nor_module, source_file,
            reconfigure_function, 0x592u, configure_failed);
        return 1u;
    }
    status = opencfw_hal_mspi_enable(handle);
    if (status != 0u) {
        opencfw_bl_log(2u, nor_module, source_file,
            reconfigure_function, 0x59au, configure_failed);
        return 1u;
    }

    const uint32_t record = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_CURRENT_DEVICE;
    const uint32_t module = *(volatile const uint32_t *)(uintptr_t)record;
    const uint8_t mode = *(const volatile uint8_t *)
        ((uintptr_t)device_config + 8u);
    (void)opencfw_publish_device_mode(module, mode);
    return 0u;
}

void opencfw_provider_420f10(void)
{
    const void *const device_config =
        (const void *)(uintptr_t)OPENCFW_READ_DEVICE_CONFIG;
    if (opencfw_provider_420e08(device_config) != 0u) {
        opencfw_bl_log(2u, nor_module, source_file,
            reconfigure_function_name, 0x5c0u, reconfigure_failed);
        return;
    }

    (void)opencfw_hal_mspi_control_latency(0u);
    uint8_t control_value = 0u;
    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_ACTIVE_HANDLE_SLOT;
    if (opencfw_hal_mspi_control(handle, 0x18u, &control_value) != 0u)
        opencfw_bl_log(2u, nor_module, source_file,
            reconfigure_function_name, 0x5c7u, control_failed);
}

void opencfw_provider_4201ba_core(uint8_t *scan_timing)
{
    const uint32_t status = opencfw_provider_420002(
        scan_timing);
    volatile uint8_t *const current_timing =
        (volatile uint8_t *)(uintptr_t)OPENCFW_TIMING_CONTROL;
    if (status == 0u)
        *(volatile uint64_t *)(uintptr_t)OPENCFW_TIMING_CONTROL =
            *(const volatile uint64_t *)(const void *)scan_timing;

    const uint32_t level = status == 0u ? 2u : 1u;
    const uint32_t line = status == 0u ? 0x1f3u : 0x1fbu;
    const char *const format = status == 0u ? timing_success : timing_failure;
    opencfw_bl_log(level, nor_module, source_file, timing_function, line,
        format, current_timing[0], current_timing[1], current_timing[2],
        current_timing[3], current_timing[4], current_timing[5]);
}

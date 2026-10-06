/* SPDX-License-Identifier: MIT
 * Readable source for the four local setup/teardown helpers called by stock
 * 0x00420F70, plus their local wait/configuration callees. Hardware, RTOS,
 * logging, copy and delay seams remain explicit linked providers.
 */
#include "nor_read_setup.h"
#include <stddef.h>

#define SLOT_ACTIVE_MSPI       UINT32_C(0x200270dc)
#define SLOT_FLASH_ACTIVITY    UINT32_C(0x200270e0)
#define BYTE_READ_POWER_STATE  UINT32_C(0x200271c6)
#define BYTE_XIP_POWER_STATE   UINT32_C(0x200271c5)
#define BYTE_READ_MODE         UINT32_C(0x200270d4)
#define SLOT_STATUS_TEMPLATE   UINT32_C(0x2000023c)
#define DEVICE_TEMPLATE        UINT32_C(0x20000224)
#define SLOT_CURRENT_DEVICE    UINT32_C(0x200270d8)

extern void opencfw_bl_copy(void *dst, const void *src, uint32_t n);
extern void opencfw_bl_power_control(uint32_t handle, uint32_t state,
                                     uint32_t retain);        /* 0x426808 */
extern uint32_t opencfw_bl_check_activity(uint32_t handle,
                                          uint32_t mode);      /* 0x4166AA */
extern uint32_t opencfw_bl_check_pending(uint32_t handle);    /* 0x416710 */
extern void opencfw_bl_log(uint32_t level, const char *tag,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);                                  /* 0x4176CE */
extern void opencfw_bl_delay(uint32_t amount);                 /* 0x41D1C0 */
extern uint32_t opencfw_bl_runtime_mode(void);                 /* 0x418B56 */
extern void opencfw_bl_notify(uint32_t event);                 /* 0x416378 */
extern uint32_t opencfw_bl_poll_status(uint16_t instruction,
    uint32_t address, uint32_t send_address, uint8_t *out,
    uint32_t length);                                          /* 0x4205F4 */
extern uint32_t opencfw_bl_mspi_disable(uint32_t handle);       /* 0x4250F0 */
extern uint32_t opencfw_bl_mspi_device_configure(
    uint32_t handle, const void *config);                       /* 0x424BE4 */
extern uint32_t opencfw_bl_mspi_enable(uint32_t handle);        /* 0x425066 */
extern uint32_t opencfw_bl_mspi_control(uint32_t handle,
    uint32_t request, void *value);                             /* 0x4251C0 */
extern void opencfw_bl_publish_device_state(uint32_t device,
    uint8_t mode);                                              /* 0x41FADC */

static uint32_t active_handle(void)
{
    return *(volatile const uint32_t *)(uintptr_t)SLOT_ACTIVE_MSPI;
}

void opencfw_bl_mspi_power_down(void)
{
    opencfw_bl_power_control(active_handle(), 0u, 1u);
    *(volatile uint8_t *)(uintptr_t)BYTE_READ_POWER_STATE = 0u;
}

void opencfw_bl_mspi_power_up(void)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)BYTE_READ_POWER_STATE;
    if (*state != 1u) {
        opencfw_bl_power_control(active_handle(), 2u, 1u);
        *state = 1u;
    }
}

void opencfw_bl_activity_log(void)
{
    const uint32_t context =
        *(volatile const uint32_t *)(uintptr_t)SLOT_FLASH_ACTIVITY;
    if (context != 0u &&
        opencfw_bl_check_activity(context, UINT32_MAX) != 0u)
        opencfw_bl_log(1u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00433784u, 0xc3u,
            (const char *)(uintptr_t)0x00432ca0u);
}

void opencfw_bl_pending_log(void)
{
    const uint32_t context =
        *(volatile const uint32_t *)(uintptr_t)SLOT_FLASH_ACTIVITY;
    if (context != 0u && opencfw_bl_check_pending(context) != 0u)
        opencfw_bl_log(1u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x0043379cu, 0xccu,
            (const char *)(uintptr_t)0x00432a24u);
}

void opencfw_bl_nor_read_before(void)
{
    opencfw_bl_activity_log();
    if (*(volatile const uint8_t *)(uintptr_t)BYTE_XIP_POWER_STATE != 1u)
        opencfw_bl_mspi_power_down();
}

void opencfw_bl_nor_read_after(void)
{
    if (*(volatile const uint8_t *)(uintptr_t)BYTE_XIP_POWER_STATE != 1u)
        opencfw_bl_mspi_power_up();
    opencfw_bl_pending_log();
}

void opencfw_bl_mspi_control_latency(uint8_t enable)
{
    volatile uint8_t *const config =
        (volatile uint8_t *)(uintptr_t)SLOT_STATUS_TEMPLATE;
    config[5] = enable == 1u ? 8u : 0u;
    (void)opencfw_bl_mspi_control(active_handle(), 0x10u, (void *)config);
}

static uint32_t configure_device(const void *config)
{
    const uint32_t handle = active_handle();
    uint32_t status = opencfw_bl_mspi_disable(handle);
    if (status != 0u) {
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00432de4u, 0x58au,
            (const char *)(uintptr_t)0x00432e08u);
        return 1u;
    }
    status = opencfw_bl_mspi_device_configure(handle, config);
    if (status != 0u) {
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00432de4u, 0x592u,
            (const char *)(uintptr_t)0x00432e2cu);
        return 1u;
    }
    status = opencfw_bl_mspi_enable(handle);
    if (status != 0u) {
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00432de4u, 0x59au,
            (const char *)(uintptr_t)0x00432e2cu);
        return 1u;
    }

    const uint32_t current_device =
        *(volatile const uint32_t *)(uintptr_t)SLOT_CURRENT_DEVICE;
    const uint32_t device =
        *(volatile const uint32_t *)(uintptr_t)current_device;
    opencfw_bl_publish_device_state(device,
        *(const volatile uint8_t *)((uintptr_t)config + 8u));
    return 0u;
}

void opencfw_bl_nor_read_configure(void)
{
    uint8_t config[24];
    uint8_t control_value = 0u;
    opencfw_bl_copy(config, (const void *)(uintptr_t)DEVICE_TEMPLATE,
                    sizeof(config));
    config[0] = 8u;
    *(uint16_t *)(void *)(config + 4u) = 0x006cu;
    config[8] = 16u;
    config[15] = 1u;

    if (configure_device(config) != 0u) {
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00433578u, 0x5aeu,
            (const char *)(uintptr_t)0x00432e50u);
        return;
    }

    opencfw_bl_mspi_control_latency(1u);
    control_value = 16u;
    if (opencfw_bl_mspi_control(active_handle(), 0x18u,
                                &control_value) != 0u)
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00433578u, 0x5b5u,
            (const char *)(uintptr_t)0x00433240u);
}

static uint32_t mspi_ready(void)
{
    uint8_t status[5] = {0};
    const uint32_t result = opencfw_bl_poll_status(5u, 0u, 0u, status, 1u);
    if (result != 0u) {
        opencfw_bl_log(2u, (const char *)(uintptr_t)0x00433cd8u,
            (const char *)(uintptr_t)0x00431540u,
            (const char *)(uintptr_t)0x00433b00u, 0x376u,
            (const char *)(uintptr_t)0x00433508u);
        return result;
    }
    return (status[0] & 0x01u) != 0u;
}

static uint32_t runtime_state(void)
{
    const uint32_t mode = opencfw_bl_runtime_mode();
    if (mode == 0u)
        return 3u;
    if (mode == 2u)
        return 2u;
    return *(volatile const uint32_t *)(uintptr_t)BYTE_READ_MODE == 1u
        ? 1u : 0u;
}

uint32_t opencfw_bl_mspi_ready_wait(uint32_t retries)
{
    for (uint32_t i = 0u; i < 200u; ++i) {
        if (mspi_ready() == 0u)
            return 0u;
        opencfw_bl_delay(5u);
    }
    for (uint32_t i = 0u; i < retries; ++i) {
        if (runtime_state() == 2u)
            opencfw_bl_notify(1u);
        else
            opencfw_bl_delay(1000u);
        if (mspi_ready() == 0u)
            return 0u;
    }
    return 1u;
}

void opencfw_bl_nor_read_delay(void)
{
    (void)opencfw_bl_mspi_ready_wait(500u);
}

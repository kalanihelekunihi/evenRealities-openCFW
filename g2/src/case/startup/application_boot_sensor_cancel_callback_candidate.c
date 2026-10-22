/* SPDX-License-Identifier: MIT
 * Native CASE 0x080086e0 indirect sensor cancellation callback.
 * The final 0x08005f42 weak callback is the sourced BX LR leaf.
 */
#include <stdint.h>

extern void HAL_UART_ErrorCallback(void *state);

/* Stock 0x080086E0 (case_reset_timer_fields) */
uint32_t case_boot_sensor_cancel_callback(uint32_t descriptor)
{
    uint32_t state=*(volatile uint32_t *)(uintptr_t)(descriptor+40u);
    *(volatile uint16_t *)(uintptr_t)(state+94u)=0u;
    *(volatile uint16_t *)(uintptr_t)(state+86u)=0u;
    HAL_UART_ErrorCallback((void *)(uintptr_t)state);
    return state;
}

/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash initializer, stock 0x100245f0.
 * Platform module dispatch remains a typed lower contract because its native
 * jump tables and product module table have not yet been source-attributed.
 */
#include <stdint.h>
#include "resident_flash_api_data.h"

extern uint32_t gx8002_resident_platform_config_25d74(
    uint32_t module, uint32_t *result);
extern void gx8002_resident_platform_gate_25080(
    uint32_t module, uint32_t enabled);
extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern int32_t gx8002_resident_flash_discover_24190(void);
extern uint32_t gx8002_resident_flash_quad_enable_242b4(void);
extern uint32_t gx8002_resident_flash_quad_enable_pair_24330(void);
extern uint32_t gx8002_resident_flash_device_config_242ec(void);
extern uint32_t gx8002_resident_xip_initialize_2436c(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t,
    uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_resident_flash_word_program_23788(
    uint32_t, const uint32_t *, uint32_t);
extern uint32_t gx8002_resident_flash_word_read_23cac(
    uint32_t, uint32_t *, uint32_t);

uint32_t gx8002_resident_flash_initialize_245f0(void)
{
    uint32_t platform_result = 0u;
    gx8002_resident_platform_config_25d74(9u, &platform_result);
    gx8002_resident_platform_gate_25080(13u, 1u);
    gx8002_resident_flash_wait_bus_2364c();
    volatile uint32_t *const controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    controller[0x10u / 4u] = 1u;
    spi[0x08u / 4u] = 0u;
    spi[0x2cu / 4u] = 0x4eu;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f0) = 1u;
    spi[0x14u / 4u] = 2u;
    spi[0x1cu / 4u] = 0x1fu;
    spi[0x08u / 4u] = 1u;
    gx8002_resident_flash_wait_ready_2375c();
    if (gx8002_resident_flash_discover_24190() != 0) return 0u;

    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint32_t *const selected =
        (const volatile uint32_t *)(uintptr_t)state[3];
    uint32_t jedec = selected[1];
    if (jedec == UINT32_C(0x854012) || jedec == UINT32_C(0x856013)) {
        gx8002_resident_flash_quad_enable_pair_24330();
    } else if ((uint32_t)(jedec + UINT32_C(0xffe3c7ee)) >= 2u) {
        gx8002_resident_flash_quad_enable_242b4();
    }
    if (jedec == UINT32_C(0x204016))
        gx8002_resident_flash_device_config_242ec();

    /* The stock descriptor stores raw even instruction addresses. C-SKY
     * function-pointer low bits are ISA tags, so clear that tag in the
     * descriptor and let the downstream caller restore its call ABI. */
    state[6] = (uint32_t)(uintptr_t)&gx8002_resident_flash_word_program_23788
               & ~UINT32_C(1);
    state[7] = (uint32_t)(uintptr_t)&gx8002_resident_flash_word_read_23cac
               & ~UINT32_C(1);
    gx8002_resident_xip_initialize_2436c(
        0xebu, 8u, 1u, 0x18u, 4u, 0u, 1u, 4u, 4u);
    return (uint32_t)(uintptr_t)gx8002_flash_api_26504;
}

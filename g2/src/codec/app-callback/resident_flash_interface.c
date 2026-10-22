/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash interface initializer, stock 0x1002443c. JEDEC
 * decisions and literal addresses are from direct native instructions.
 */
#include <stdint.h>
#include "resident_flash_api_data.h"

extern uint32_t gx8002_resident_platform_config_25d74(uint32_t, uint32_t *);
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_resident_flash_wait_bus_2364c(void);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_resident_flash_spi_irq_handler_23ac0(void);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern int32_t gx8002_resident_flash_discover_24190(void);
extern void gx8002_resident_flash_protection_initialize_246c4(void);
extern uint32_t gx8002_resident_flash_quad_enable_242b4(void);
extern uint32_t gx8002_resident_flash_quad_enable_pair_24330(void);
extern uint32_t gx8002_resident_flash_device_config_242ec(void);
extern uint8_t gx8002_resident_flash_read_status_23734(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t, const uint8_t *, int32_t);
extern uint32_t gx8002_resident_xip_initialize_2436c(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t,
    uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_resident_flash_word_program_23788(
    uint32_t, const uint32_t *, uint32_t);
extern uint32_t gx8002_resident_flash_word_read_23cac(
    uint32_t, uint32_t *, uint32_t);

/* Stock 0x1002443C (flash_interface_initialize) */
uint32_t gx8002_resident_flash_interface_initialize_2443c(void)
{
    uint32_t platform_result = 0u;
    gx8002_resident_platform_config_25d74(9u, &platform_result);
    gx8002_resident_platform_gate_25080(13u, 1u);
    gx8002_resident_flash_wait_bus_2364c();
    volatile uint32_t *const controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    spi[0x08u / 4u] = 0u;
    controller[0x10u / 4u] = 1u;
    spi[0x2cu / 4u] = 0x4eu;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f0) = 1u;
    spi[0x14u / 4u] = 4u;
    spi[0x1cu / 4u] = 0x1fu;
    spi[0x08u / 4u] = 1u;
    uint32_t raw_irq =
        (uint32_t)(uintptr_t)&gx8002_resident_flash_spi_irq_handler_23ac0 &
        ~UINT32_C(1);
    gx8002_resident_request_irq_2553c(15u, raw_irq, 0u);
    gx8002_resident_flash_wait_ready_2375c();
    if (gx8002_resident_flash_discover_24190() != 0) return 0u;
    gx8002_resident_flash_protection_initialize_246c4();
    spi[0x08u / 4u] = 0u;
    spi[0x14u / 4u] = 2u;

    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint32_t *const selected =
        (const volatile uint32_t *)(uintptr_t)state[3];
    uint32_t jedec = selected[1];
    uint32_t special = 0u;
    switch (jedec) {
    case UINT32_C(0x856013): case UINT32_C(0x856014):
    case UINT32_C(0x0b4014): case UINT32_C(0x0b4016):
    case UINT32_C(0x0b4017): case UINT32_C(0x854012):
    case UINT32_C(0xb36014): case UINT32_C(0xba6015):
    case UINT32_C(0xc84015): case UINT32_C(0xc84215):
    case UINT32_C(0xc86015): case UINT32_C(0xc86016):
    case UINT32_C(0xcd7015): case UINT32_C(0xef4015):
        gx8002_resident_flash_quad_enable_pair_24330();
        break;
    case UINT32_C(0x1c3812): case UINT32_C(0x1c3813):
    case UINT32_C(0x1c7017):
        break;
    case UINT32_C(0x684015):
        gx8002_resident_flash_quad_enable_242b4();
        gx8002_resident_flash_quad_enable_pair_24330();
        special = 1u;
        break;
    case UINT32_C(0xc22017): {
        uint8_t status = gx8002_resident_flash_read_status_23734();
        if ((status & 0x40u) == 0u) {
            status |= 0x40u;
            gx8002_resident_flash_wait_ready_2375c();
            gx8002_resident_flash_write_enable_2374c();
            gx8002_resident_flash_command_write_236dc(1u, &status, 1);
            gx8002_resident_flash_wait_ready_2375c();
        }
        special = 1u;
        break;
    }
    default:
        gx8002_resident_flash_quad_enable_242b4();
        break;
    }
    if (special == 0u && jedec == UINT32_C(0x204016))
        gx8002_resident_flash_device_config_242ec();

    state[6] = (uint32_t)(uintptr_t)&gx8002_resident_flash_word_program_23788 &
               ~UINT32_C(1);
    state[7] = (uint32_t)(uintptr_t)&gx8002_resident_flash_word_read_23cac &
               ~UINT32_C(1);
    gx8002_resident_xip_initialize_2436c(
        0xebu, 8u, 1u, 0x18u, 4u, 0u, 1u, 4u, 4u);
    return (uint32_t)(uintptr_t)gx8002_flash_api_26504;
}

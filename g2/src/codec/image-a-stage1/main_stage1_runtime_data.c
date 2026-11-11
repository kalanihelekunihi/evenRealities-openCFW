/* SPDX-License-Identifier: MIT
 * BINH A stage-1 initialized state at the locked D-bus view 0x20001280.
 */
#include <stdint.h>
#include <spl/spl.h>

__attribute__((used, section(".spl_a.boot_info")))
volatile struct boot_info gx8002_image_a_stage1_boot_info = {
    .boot_device = BOOT_DEVICE_NONE,
};

__attribute__((used, section(".spl_a.transfer_modes")))
volatile uint8_t gx8002_image_a_stage1_transfer_modes[2] = {UNKNOW, UNKNOW};

__attribute__((used, section(".spl_a.uart_baud")))
volatile uint32_t gx8002_image_a_stage1_uart_new_baudrate = 115200u;

__attribute__((used, section(".spl_a.flash_jedec")))
volatile uint32_t gx8002_image_a_stage1_flash_jedec = UINT32_C(0x00ffffff);

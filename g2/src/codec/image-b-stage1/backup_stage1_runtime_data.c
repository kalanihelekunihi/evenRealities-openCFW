/* SPDX-License-Identifier: GPL-2.0+
 * Authenticated BINH-B stage1 initialized records from pinned spl.c and
 * spl_spinor.c; native VMAs are fixed by the experimental linker script.
 */
#include <stdint.h>
#include <spl/spl.h>

__attribute__((used, section(".stage1.boot_info")))
volatile struct boot_info gx8002_stage1_boot_info = {
    .boot_device = BOOT_DEVICE_NONE,
};

__attribute__((used, section(".stage1.transfer_modes")))
volatile uint8_t gx8002_stage1_transfer_modes[2] = {UNKNOW, UNKNOW};

__attribute__((used, section(".stage1.uart_baud")))
volatile uint32_t gx8002_stage1_uart_new_baudrate = 115200u;

__attribute__((used, section(".stage1.flash_jedec")))
volatile uint32_t gx8002_stage1_flash_jedec = 0x00ffffffu;

/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x100247b8, 0x100247e0, 0x100247f4: descriptor callback
 * dispatch wrappers. Direct C-SKY instructions establish the field offsets,
 * forwarded register arguments, and missing-callback return value.
 */
#include <stdint.h>

typedef int32_t (*flash_read_fn)(uint32_t, uint32_t, uint32_t);
typedef int32_t (*flash_info_fn)(uint32_t);
typedef int32_t (*flash_otp_read_fn)(uint32_t, uint32_t, uint32_t);

int32_t gx8002_resident_flash_dispatch_read_247b8(
    const volatile uint8_t *descriptor, uint32_t arg1,
    uint32_t arg2, uint32_t arg3)
{
    uint32_t raw = *(const volatile uint32_t *)(uintptr_t)(descriptor + 4);
    if (raw == 0u) return -1;
    return ((flash_read_fn)(uintptr_t)raw)(arg1, arg2, arg3);
}

int32_t gx8002_resident_flash_dispatch_getinfo_247e0(
    const volatile uint8_t *descriptor, uint32_t arg1)
{
    uint32_t raw = *(const volatile uint32_t *)(uintptr_t)(descriptor + 0x34);
    if (raw == 0u) return -1;
    return ((flash_info_fn)(uintptr_t)raw)(arg1);
}

int32_t gx8002_resident_flash_dispatch_otp_read_247f4(
    const volatile uint8_t *descriptor, uint32_t arg1,
    uint32_t arg2, uint32_t arg3)
{
    uint32_t raw = *(const volatile uint32_t *)(uintptr_t)(descriptor + 0x58);
    if (raw == 0u) return -1;
    return ((flash_otp_read_fn)(uintptr_t)raw)(arg1, arg2, arg3);
}

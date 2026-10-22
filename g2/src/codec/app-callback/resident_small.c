/* SPDX-License-Identifier: MIT
 * Image-A SRAM small resident bodies, native base 0x10023400.
 */
#include <stdint.h>

/* 0x10024244; literal at 0x1002424c is SRAM flash_state 0x200264e4. */
/* Stock 0x10024244 (gx8002_flash_gettype) */
uint32_t gx8002_resident_flash_gettype_24244(void)
{
    uintptr_t descriptor = *(volatile const uint32_t *)(uintptr_t)
        UINT32_C(0x200264f0);
    return *(volatile const uint32_t *)descriptor;
}

/* 0x10025e38; the native body writes its fourth register argument. */
uint32_t gx8002_resident_clock_subband_hz_25e38(
    uint32_t unused0, uint32_t unused1,
    uint32_t *destination, uint32_t value)
{
    (void)unused0;
    (void)unused1;
    *destination = value;
    return 0u;
}

/* 0x100247d4: invoke optional descriptor callback at byte offset 0x30. */
/* Stock 0x100247D4 (gx8002_flash_type_api) */
uintptr_t gx8002_resident_flash_type_api_247d4(const void *descriptor)
{
    uintptr_t raw = *(volatile const uint32_t *)
        ((uintptr_t)descriptor + 0x30u);
    if (raw != 0u) {
        uintptr_t (*callback)(void) = (uintptr_t (*)(void))raw;
        return callback();
    }
    return 0u;
}

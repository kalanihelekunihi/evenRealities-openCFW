/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025d04 OTP mode probe. Direct native disassembly
 * establishes callback registers, all return branches, and literals at
 * 0x100249f4/0x10024a0a. XIP 0x10206c7c/0x10206ca0 are its exact
 * comparison and length lowers.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t module);
extern int32_t gx8002_resident_flash_dispatch_otp_read_247f4(
    const volatile uint8_t *descriptor, uint32_t arg1,
    uint32_t arg2, uint32_t arg3);
extern void gx8002_xip_tws_publish_10206c24(const char *format, ...);

int32_t gx8002_xip_strncmp_10206c7c(
    const uint8_t *left, const uint8_t *right, uint32_t count)
{
    const uint8_t *const end = right + count;
    while (right != end) {
        uint32_t a = *left;
        uint32_t b = *right;
        int32_t difference = (int32_t)(a - b);
        if (difference != 0) return difference;
        ++left;
        ++right;
        if (a == 0u) break;
    }
    return 0;
}

uint32_t gx8002_xip_strlen_10206ca0(const char *text)
{
    const char *cursor = text;
    while (*cursor != '\0') ++cursor;
    return (uint32_t)(cursor - text);
}

int32_t gx8002_resident_flash_otp_mode_25d04(uint32_t *mode)
{
    *mode = UINT32_C(0x8002);
    uint32_t clock = gx8002_resident_clock_frequency_25210(13u);
    volatile const uint32_t *const initializer =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20026504);
    uintptr_t entry = *initializer;
    volatile uint8_t *descriptor =
        ((volatile uint8_t *(*)(uint32_t, uint32_t, uint32_t, uint32_t))entry)(
            0u, 0u, clock >> 1, UINT32_C(0x800));
    if (descriptor == 0) return -1;

    uint8_t otp[5] = {0u, 0u, 0u, 0u, 0u};
    int32_t read = gx8002_resident_flash_dispatch_otp_read_247f4(
        descriptor, 0u, (uint32_t)(uintptr_t)otp, 5u);
    if (read < 0) {
        gx8002_xip_tws_publish_10206c24("read flash otp error\n");
        return -1;
    }
    static const char expected[] = "8003A";
    uint32_t count = gx8002_xip_strlen_10206ca0(expected);
    if (gx8002_xip_strncmp_10206c7c(otp,
            (const uint8_t *)expected, count) == 0)
        *mode = UINT32_C(0x8003a);
    return 0;
}

/* SPDX-License-Identifier: MIT
 * Separate image-B SRAM candidate, pinned image SHA-256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Native entries 0x100051c4, 0x10009998 and 0x100099bc. These are source functions,
 * not a layout claim for the loaded image.
 */
#include <stdint.h>

uint32_t gx8002_image_b_dma_bus_address_100051c4(uint32_t address)
{
    return address < UINT32_C(0x20000000)
        ? address & UINT32_C(0x07ffffff) : address;
}

int32_t gx8002_image_b_strncmp_10009998(
    const unsigned char *left, const unsigned char *right, uint32_t count)
{
    while (count != 0u) {
        unsigned char a = *left;
        unsigned char b = *right;
        int32_t difference = (int32_t)a - (int32_t)b;
        if (difference != 0) {
            return difference;
        }
        if (a == 0u) {
            return 0;
        }
        ++left;
        ++right;
        --count;
    }
    return 0;
}

int32_t gx8002_image_b_strlen_100099bc(const char *text)
{
    const char *cursor = text;
    while (*cursor != '\0') {
        ++cursor;
    }
    return (int32_t)(cursor - text);
}

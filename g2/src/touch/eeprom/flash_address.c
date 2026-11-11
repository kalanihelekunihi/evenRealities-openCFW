/* Flash and supervisory-flash row addressing for the locked PSoC 4000T image. */
#include <stdbool.h>
#include <stdint.h>

#include "provider.h"

bool touch_flash_valid_addr(uint32_t address)
{
    bool valid = false;

    if (address < 0x10000u) {
        if ((address % 128u) == 0u) {
            valid = true;
        }
    } else if (address >= 0x0ffff200u && address < 0x0ffff400u) {
        if ((address % 128u) == 0u) {
            valid = true;
        }
    }
    return valid;
}

uint32_t touch_flash_row_number(uint32_t address)
{
    uint32_t row = 0;

    if (address < 0x10000u) {
        row = address / 128u;
    } else {
        row = (address - 0x0ffff200u) / 128u;
    }
    return row;
}

/* Source-owned stock 0x42a1bc event-A power TON adjustment leaf. */
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define BYTE(address) (*(volatile uint8_t *)(uintptr_t)(address))

void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major)
{
    uint32_t ton, trim;
    if (major == 8u)
        new_minor = 7u;
    if (new_minor == 0u) {
        const uint32_t value = WORD(0x20026bfcu);
        ton = BYTE(0x20026bfcu) & 0x1fu;
        trim = (value & 0x7fffu) >> 10;
    } else if (new_minor == 2u) {
        ton = BYTE(0x20026bf4u) & 0x1fu;
        trim = BYTE(0x20026bf8u) & 0x1fu;
    } else if (new_minor < 2u) {
        ton = (WORD(0x20026bfcu) & 0x3ffu) >> 5;
        trim = (WORD(0x20026bfcu) & 0xfffffu) >> 15;
    } else if (new_minor == 4u) {
        ton = (WORD(0x20026bf4u) & 0x3ffu) >> 5;
        trim = (WORD(0x20026bf8u) & 0x3ffu) >> 5;
    } else if (new_minor < 4u) {
        ton = (WORD(0x20026bf4u) & 0x7fffu) >> 10;
        trim = (WORD(0x20026bf8u) & 0x7fffu) >> 10;
    } else if (new_minor == 6u) {
        ton = BYTE(0x20026c00u) & 0x1fu;
        trim = (WORD(0x20026c00u) & 0x7fffu) >> 10;
    } else if (new_minor < 6u) {
        ton = (WORD(0x20026bf4u) & 0xfffffu) >> 15;
        trim = (WORD(0x20026bf8u) & 0xfffffu) >> 15;
    } else if (new_minor == 7u) {
        ton = (WORD(0x40020344u) & 0xffffu) >> 11;
        trim = (WORD(0x40020354u) & 0x3fffffu) >> 17;
    } else {
        ton = (WORD(0x20026bf4u) & 0xfffffu) >> 15;
        trim = (WORD(0x20026bf8u) & 0xfffffu) >> 15;
    }
    WORD(0x40020344u) = (WORD(0x40020344u) & 0xc1ffffffu) | (ton << 25);
    WORD(0x40020358u) = (WORD(0x40020358u) & 0xffffe0ffu) | (trim << 8);
}

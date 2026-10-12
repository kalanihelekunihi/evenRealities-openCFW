#include <stdint.h>

static int32_t source_extract(uint32_t value)
{
    return (int32_t)(value << 2) >> 16;
}

int main(void)
{
    static const uint32_t input[] = {
        0u, 1u, 0x3fffu, 0x4000u, 0x1fff8000u,
        0x20000000u, 0x3fffffffu, 0x7fffffffu,
        0x80000000u, 0xffffffffu, 0xa3419cb2u
    };
    for (uint32_t index = 0; index < sizeof input / sizeof input[0]; ++index) {
        uint32_t value = input[index];
        int32_t native;
        __asm__ volatile("sext %0, %1, 29, 14"
                         : "=r"(native) : "r"(value));
        if (native != source_extract(value))
            return (int)(index + 1u);
    }
    return 0;
}

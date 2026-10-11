/* Source-owned stock 0x42ae24 and 0x42ae6c spot trim leaves. */
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define BYTE(address) (*(volatile uint8_t *)(uintptr_t)(address))

void native_spot_profile_trim_42ae24(uint32_t restore)
{
    WORD(0x40020088u) = (WORD(0x40020088u) & 0xffffffc0u) |
                         ((WORD(0x20026c08u) >> 2) & 0x3fu);
    WORD(0x400201b0u) = (WORD(0x400201b0u) & 0xfffe7fffu) |
                         ((WORD(0x20026c08u) & 3u) << 15);
    if ((restore & 0xffu) != 0u) {
        const uint32_t old = WORD(0x40020080u);
        WORD(0x40020080u) = (old - WORD(0x200270a4u)) & 0x3ffu |
                            (old & 0xfffffc00u);
    }
}

void native_spot_trim_restore_42ae6c(void)
{
    if (BYTE(0x200271aeu) == 0u) {
        WORD(0x40020044u) = (WORD(0x40020044u) & 0xffffff80u) |
                            (WORD(0x200270a8u) & 0x7fu);
        WORD(0x4002004cu) = (WORD(0x4002004cu) & 0xffffff80u) |
                            (WORD(0x200270acu) & 0x7fu);
    }
}

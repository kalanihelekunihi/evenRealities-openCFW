/* SPDX-License-Identifier: MIT
 * Native AIN reset 0x10203c88..0x10203dc0. Direct C-SKY disassembly,
 * including the hardware status poll missed by retained decompilation.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

static void set_bit(uint32_t word, uint32_t bit)
{
    ain[word] = ain[word] | (UINT32_C(1) << bit);
}

static void clear_bit(uint32_t word, uint32_t bit)
{
    ain[word] = ain[word] & ~(UINT32_C(1) << bit);
}

uint32_t gx8002_xip_ain_reset_10203c88(void)
{
    ain[0x100u / 4u] = 0u;
    ain[0x104u / 4u] = ~UINT32_C(0x700);
    clear_bit(0u, 31u);
    set_bit(0u, 15u);
    clear_bit(0u, 14u);
    set_bit(0u, 7u);
    clear_bit(0u, 6u);
    set_bit(0x4u / 4u, 31u);
    clear_bit(0x4u / 4u, 30u);
    set_bit(0x8u / 4u, 31u);
    clear_bit(0x8u / 4u, 30u);
    clear_bit(0xcu / 4u, 9u);
    clear_bit(0x28u / 4u, 9u);
    clear_bit(0x2cu / 4u, 9u);
    clear_bit(0x48u / 4u, 9u);
    clear_bit(0x4cu / 4u, 9u);
    ain[0x104u / 4u] = 0x200u;
    while (((ain[0x104u / 4u] >> 8u) & 1u) == 0u) {}
    ain[0x104u / 4u] = 0x100u;
    ain[0x104u / 4u] = 0x400u;
    ain[0x104u / 4u] = UINT32_C(0x071f003f);
    set_bit(0x108u / 4u, 15u);
    clear_bit(0x108u / 4u, 14u);
    set_bit(0x108u / 4u, 7u);
    clear_bit(0x108u / 4u, 6u);
    set_bit(0x108u / 4u, 23u);
    clear_bit(0x108u / 4u, 22u);
    set_bit(0x158u / 4u, 31u);
    clear_bit(0x158u / 4u, 30u);
    set_bit(0x180u / 4u, 31u);
    clear_bit(0x180u / 4u, 30u);
    clear_bit(0x180u / 4u, 29u);
    return 0u;
}

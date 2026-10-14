/* SPDX-License-Identifier: MIT
 * Main 0x4bfed6: per-serial-mode MSPI transfer registers. Mode rows are
 * transcribed from the locked 0x4bfed6 case tree, including no-op modes.
 */
#include <stdint.h>

struct mode_row {
    uint8_t command;
    uint16_t mode_bits;
    uint8_t instruction_kind;
    uint8_t set_bit25;
};

static const struct mode_row rows[26] = {
    {  1u, 0x000u, 0u, 1u }, {  2u, 0x000u, 0u, 1u },
    {  5u, 0x000u, 0u, 0u }, {  6u, 0x000u, 0u, 0u },
    {  9u, 0x000u, 1u, 0u }, { 10u, 0x000u, 1u, 0u },
    { 13u, 0x000u, 2u, 0u }, { 14u, 0x000u, 2u, 0u },
    { 13u, 0x000u, 2u, 0u }, { 14u, 0x000u, 2u, 0u },
    { 17u, 0x000u, 3u, 0u }, { 18u, 0x000u, 3u, 0u },
    {  1u, 0x100u, 0u, 0u }, {  2u, 0x100u, 0u, 0u },
    {  1u, 0x300u, 0u, 0u }, {  2u, 0x300u, 0u, 0u },
    {  1u, 0x500u, 1u, 0u }, {  2u, 0x500u, 1u, 0u },
    {  1u, 0x700u, 1u, 0u }, {  2u, 0x700u, 1u, 0u },
    {  1u, 0x000u, 0u, 0u }, {  2u, 0x000u, 0u, 0u },
    {  1u, 0x900u, 2u, 0u }, {  2u, 0x900u, 2u, 0u },
    {  1u, 0xb00u, 2u, 0u }, {  2u, 0xb00u, 2u, 0u },
};

uint32_t g2_main_mspi_configure_aux_4bfed6(uint32_t controller)
{
    const volatile uint8_t *const handle =
        (const volatile uint8_t *)(uintptr_t)controller;
    const uint8_t mode = handle[10];
    if (mode >= 26u)
        return 0u;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uintptr_t base = UINT32_C(0x40060000) + module * 0x1000u;
    volatile uint32_t *const format =
        (volatile uint32_t *)(base + 0x84u);
    volatile uint32_t *const options =
        (volatile uint32_t *)(base + 0x90u);
    const struct mode_row row = rows[mode];

    *format = (*format & ~31u) | row.command;
    if (row.set_bit25)
        *format |= UINT32_C(0x02000000);
    else
        *format &= ~UINT32_C(0x02000000);
    *options = (*options & ~UINT32_C(0x0f00)) | row.mode_bits;

    uint32_t instruction;
    if (row.instruction_kind == 2u)
        instruction = 0x3ffu;
    else if (row.instruction_kind == 3u)
        instruction = 0x7ffffu;
    else if (handle[9] == 0u)
        instruction = row.instruction_kind ? 0x10fu : 0x103u;
    else
        instruction = row.instruction_kind ?
            UINT32_C(0x8000001f) : UINT32_C(0x80000013);
    *(volatile uint32_t *)(base + 0x44u) = instruction;
    return 0u;
}

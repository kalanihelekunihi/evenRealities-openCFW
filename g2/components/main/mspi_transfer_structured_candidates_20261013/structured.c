/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selectors 14..19: packed register records and readback.
 * The complete selector dispatcher remains gated.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_transfer_mode16_candidate(uint32_t,
                                                         const void *);

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * 0x1000u + offset);
}

static void field(volatile uint32_t *word, uint32_t mask, uint32_t value)
{
    *word = (*word & mask) | value;
}

uint32_t g2_main_mspi_transfer_structured_candidate(
    uint32_t controller, uint32_t selector, void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint8_t operation = (uint8_t)selector;
    if (operation > 40u) return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (operation < 14u || operation > 19u)
        return 6u;
    if (operation == 16u)
        return g2_main_mspi_transfer_mode16_candidate(
            controller, configuration);
    if (operation != 18u && configuration == 0)
        return 6u;

    uint8_t *const cfg = (uint8_t *)configuration;
    const uint32_t *const words = (const uint32_t *)configuration;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    volatile uint32_t *const format = reg(module, 0x84u);
    volatile uint32_t *const control = reg(module, 0x88u);
    volatile uint32_t *const options = reg(module, 0x8cu);
    volatile uint32_t *const auxiliary = reg(module, 0xa8u);

    switch (operation) {
    case 14:
        field(control, UINT32_C(0xfffffffb), (uint32_t)(cfg[0] & 1u) << 2);
        field(control, UINT32_C(0xfffffff7), (uint32_t)(cfg[1] & 1u) << 3);
        field(control, UINT32_C(0xffffffef), (uint32_t)(cfg[2] & 1u) << 4);
        field(control, UINT32_C(0xfffffc1f), (uint32_t)(cfg[3] & 0x1fu) << 5);
        field(control, UINT32_C(0xffff83ff), (uint32_t)(cfg[4] & 0x1fu) << 10);
        field(auxiliary, UINT32_C(0xfffffffe),
              (uint32_t)((cfg[4] & 0x3fu) >> 5));
        field(control, UINT32_C(0xfff07fff),
              (uint32_t)(cfg[5] & 0x1fu) << 15);
        field(auxiliary, UINT32_C(0xfffffeff),
              (uint32_t)((cfg[5] & 0x3fu) >> 5) << 8);
        field(control, UINT32_C(0xffefffff),
              (uint32_t)(cfg[6] & 1u) << 20);
        field(control, UINT32_C(0xfc1fffff),
              (uint32_t)(cfg[7] & 0x1fu) << 21);
        field(control, UINT32_C(0x83ffffff),
              (uint32_t)(cfg[8] & 0x1fu) << 26);
        field(control, UINT32_C(0x7fffffff),
              (uint32_t)cfg[9] << 31);
        return 0u;
    case 15:
        field(options, UINT32_C(0xfffffff0), cfg[9] & 0xfu);
        field(options, UINT32_C(0xffffffef),
              (uint32_t)(cfg[8] & 1u) << 4);
        field(options, UINT32_C(0xffffffdf),
              (uint32_t)(cfg[7] & 1u) << 5);
        field(options, UINT32_C(0xffffff7f),
              (uint32_t)(cfg[6] & 1u) << 7);
        field(options, UINT32_C(0xfffffeff),
              (uint32_t)(cfg[5] & 1u) << 8);
        field(options, UINT32_C(0xfffff9ff),
              (uint32_t)(cfg[4] & 3u) << 9);
        field(options, UINT32_C(0xfffff7ff),
              (uint32_t)(cfg[3] & 1u) << 11);
        field(options, UINT32_C(0xffffefff),
              (uint32_t)(cfg[2] & 1u) << 12);
        field(options, UINT32_C(0xffffdfff),
              (uint32_t)(cfg[1] & 1u) << 13);
        field(options, UINT32_C(0xfffe3fff),
              (uint32_t)(cfg[0] & 7u) << 14);
        return 0u;
    case 17:
        cfg[0] = (uint8_t)(*format >> 24) & 1u;
        cfg[1] = (uint8_t)(*format >> 23) & 1u;
        cfg[2] = (uint8_t)(*format >> 22) & 1u;
        cfg[5] = (uint8_t)(*format >> 8) & 0x3fu;
        cfg[5] = (uint8_t)(*reg(module, 0x90u) >> 14) & 0x3fu;
        cfg[3] = (uint8_t)(*control >> 5) & 0x1fu;
        cfg[4] = (uint8_t)(*control >> 10) & 0x1fu;
        cfg[4] = (uint8_t)(((uint8_t)(*auxiliary << 5) & 0x20u) + cfg[4]);
        return 0u;
    case 18: {
        const uint32_t address = words[2];
        if (module == 0u) {
            if (address + UINT32_C(0xa0000000) > UINT32_C(0x0fffffff))
                return 5u;
        } else if (module == 2u) {
            if (address + UINT32_C(0x7c000000) > UINT32_C(0x03ffffff))
                return 5u;
        } else if (module == 1u) {
            if (address + UINT32_C(0x80000000) > UINT32_C(0x03ffffff))
                return 5u;
        } else if (module == 3u) {
            if (address + UINT32_C(0x78000000) > UINT32_C(0x07ffffff))
                return 5u;
        }
        volatile uint32_t *const execute = reg(module, 0x9cu);
        field(execute, UINT32_C(0xffffe000),
              (words[0] & UINT32_C(0x1fffffff)) >> 16);
        field(execute, UINT32_C(0xe000ffff),
              words[1] & UINT32_C(0x1fff0000));
        *reg(module, 0x80u) =
            (address & UINT32_C(0x1fff0000)) |
            ((uint32_t)(cfg[12] & 1u) << 4) |
            (cfg[13] & 0xfu);
        return 0u;
    }
    case 19:
        *reg(module, 0xa0u) =
            ((uint32_t)cfg[6] << 21) |
            ((uint32_t)cfg[7] << 14) |
            ((uint32_t)(cfg[8] & 1u) << 13) |
            ((uint32_t)cfg[5] << 12) |
            (words[0] & 0xfffu);
        return 0u;
    default:
        return 6u;
    }
}

/* SPDX-License-Identifier: MIT
 * Main NOR clock selector at 0x4c32b4. The SRAM words are the stock clock
 * configuration slots; their initialization and the request lower remain open.
 */
#include <stddef.h>
#include <stdint.h>

extern uint32_t g2_main_clock_request_480f0c(uint32_t, uint32_t);

typedef struct {
    uint8_t clock_id;
    const volatile uint32_t *value;
} clock_request_t;

/* sim15: stock .data pad-config words 0x20000138..0x200001ac live in
 * g2_stock_ram_2000006c below; raw addresses read unrelated objects here.
 * Stock .data 0x2000006c..0x200001c8: GPIO pad-configuration words read by
 * 0x4c2b68 (radio power groups) and 0x4c32b4 (NOR/clock groups).
 * Evidence: values copied verbatim from the stock init image
 * .waves/init_20000000.bin offsets 0x6c..0x1c8 (no pointers in this span;
 * 0x2000005c is a code pointer and is excluded). stock_ram_cells.c begins at
 * 0x200001c8, so this range was previously uncovered (sim15).
 * Defined here because this file is in the build manifest. */
uint32_t g2_stock_ram_2000006c[87] __attribute__((aligned(4))) = {
    0x00000587u, 0x00000400u, 0x00000401u, 0x00000401u, 0x00004600u, 0x00004600u,
    0x00040187u, 0x00000004u, 0x00000005u, 0x00000005u, 0x00004204u, 0x00004204u,
    0x00080187u, 0x00000001u, 0x00000001u, 0x00004200u, 0x00004200u, 0x000c0187u,
    0x00000001u, 0x00000001u, 0x00004200u, 0x00004200u, 0x00100187u, 0x00000001u,
    0x00000001u, 0x00004200u, 0x00004200u, 0x00140187u, 0x00000001u, 0x00000001u,
    0x00004200u, 0x00004200u, 0x00180187u, 0x00000001u, 0x00000001u, 0x00004200u,
    0x00004200u, 0x001c0187u, 0x00000001u, 0x00000001u, 0x00004200u, 0x00004200u,
    0x00000402u, 0x00000409u, 0x00000c09u, 0x00000409u, 0x0000040au, 0x00000409u,
    0x0000040au, 0x0000040au, 0x0000040au, 0x00000d81u, 0x00000c80u, 0x00001c80u,
    0x00000c80u, 0x00000c80u, 0x00000480u, 0x00000480u, 0x00000480u, 0x00000480u,
    0x00000c80u, 0x00000480u, 0x00000480u, 0x00000480u, 0x00000480u, 0x00000480u,
    0x00000480u, 0x00000480u, 0x00000480u, 0x00000480u, 0x00000582u, 0x00000480u,
    0x00000480u, 0x00000c00u, 0x00000c00u, 0x00000c00u, 0x00000c00u, 0x00000c00u,
    0x00000c00u, 0x00000c00u, 0x00000c00u, 0x00000001u, 0x00000000u, 0x00f42400u,
    0x00000000u, 0x00000000u, 0x00000000u,
};
#define PAD_WORD(index) (&g2_stock_ram_2000006c[index])

static const clock_request_t group0_leaf[] = {
    {0xc7u,PAD_WORD(51u)},{0x40u,PAD_WORD(52u)},
    {0x41u,PAD_WORD(53u)},{0x48u,PAD_WORD(60u)},
};
static const clock_request_t group0_mid[] = {
    {0x42u,PAD_WORD(54u)},{0x43u,PAD_WORD(55u)},
};
static const clock_request_t group0_high[] = {
    {0x44u,PAD_WORD(56u)},{0x45u,PAD_WORD(57u)},
    {0x46u,PAD_WORD(58u)},{0x47u,PAD_WORD(59u)},
};
static const clock_request_t group0_top[] = {
    {0x25u,PAD_WORD(61u)},{0x26u,PAD_WORD(62u)},
    {0x27u,PAD_WORD(63u)},{0x28u,PAD_WORD(64u)},
    {0x29u,PAD_WORD(65u)},{0x2au,PAD_WORD(66u)},
    {0x2bu,PAD_WORD(67u)},{0x2cu,PAD_WORD(68u)},
    {0x2du,PAD_WORD(69u)},
};
static const clock_request_t group1_leaf[] = {
    {0x31u,PAD_WORD(70u)},{0x5fu,PAD_WORD(71u)},
    {0x60u,PAD_WORD(72u)},{0x67u,PAD_WORD(79u)},
    {0x68u,PAD_WORD(80u)},
};
static const clock_request_t group1_mid[] = {
    {0x61u,PAD_WORD(73u)},{0x62u,PAD_WORD(74u)},
};
static const clock_request_t group1_high[] = {
    {0x63u,PAD_WORD(75u)},{0x64u,PAD_WORD(76u)},
    {0x65u,PAD_WORD(77u)},{0x66u,PAD_WORD(78u)},
};

static void request_group(const clock_request_t *entries, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        const uint32_t value = *entries[i].value;
        (void)g2_main_clock_request_480f0c(entries[i].clock_id, value);
    }
}

#define REQUEST_GROUP(group) request_group((group), sizeof(group) / sizeof((group)[0]))

void g2_norflash_clock_select_4c32b4(uint32_t controller, uint32_t mode)
{
    const uint8_t kind = (uint8_t)mode;
    if (controller == 0u) {
        if (kind == 10u)
            REQUEST_GROUP(group0_top);
        if (kind == 6u || kind == 8u || kind == 10u)
            REQUEST_GROUP(group0_high);
        if (kind == 4u || kind == 6u || kind == 8u || kind == 10u ||
            kind == 16u || kind == 18u)
            REQUEST_GROUP(group0_mid);
        if (kind == 0u || kind == 4u || kind == 6u || kind == 8u ||
            kind == 10u || kind == 16u || kind == 18u)
            REQUEST_GROUP(group0_leaf);
    } else if (controller == 1u) {
        if (kind == 6u || kind == 8u || kind == 22u || kind == 24u)
            REQUEST_GROUP(group1_high);
        if (kind == 4u || kind == 6u || kind == 8u || kind == 16u ||
            kind == 18u || kind == 22u || kind == 24u)
            REQUEST_GROUP(group1_mid);
        if (kind == 0u || kind == 4u || kind == 6u || kind == 8u ||
            kind == 16u || kind == 18u || kind == 22u || kind == 24u)
            REQUEST_GROUP(group1_leaf);
    }
}

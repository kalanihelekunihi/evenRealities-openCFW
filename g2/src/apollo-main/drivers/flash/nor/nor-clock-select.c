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
#define V(a) (&g2_stock_ram_2000006c[((a) - 0x2000006cu) / 4u])

static const clock_request_t group0_leaf[] = {
    {0xc7u,V(0x20000138u)},{0x40u,V(0x2000013cu)},
    {0x41u,V(0x20000140u)},{0x48u,V(0x2000015cu)},
};
static const clock_request_t group0_mid[] = {
    {0x42u,V(0x20000144u)},{0x43u,V(0x20000148u)},
};
static const clock_request_t group0_high[] = {
    {0x44u,V(0x2000014cu)},{0x45u,V(0x20000150u)},
    {0x46u,V(0x20000154u)},{0x47u,V(0x20000158u)},
};
static const clock_request_t group0_top[] = {
    {0x25u,V(0x20000160u)},{0x26u,V(0x20000164u)},
    {0x27u,V(0x20000168u)},{0x28u,V(0x2000016cu)},
    {0x29u,V(0x20000170u)},{0x2au,V(0x20000174u)},
    {0x2bu,V(0x20000178u)},{0x2cu,V(0x2000017cu)},
    {0x2du,V(0x20000180u)},
};
static const clock_request_t group1_leaf[] = {
    {0x31u,V(0x20000184u)},{0x5fu,V(0x20000188u)},
    {0x60u,V(0x2000018cu)},{0x67u,V(0x200001a8u)},
    {0x68u,V(0x200001acu)},
};
static const clock_request_t group1_mid[] = {
    {0x61u,V(0x20000190u)},{0x62u,V(0x20000194u)},
};
static const clock_request_t group1_high[] = {
    {0x63u,V(0x20000198u)},{0x64u,V(0x2000019cu)},
    {0x65u,V(0x200001a0u)},{0x66u,V(0x200001a4u)},
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

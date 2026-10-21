/* SPDX-License-Identifier: MIT
 * Main NOR clock selector at 0x4c32b4. The SRAM words are the stock clock
 * configuration slots; their initialization and the request lower remain open.
 */
#include <stddef.h>
#include <stdint.h>

extern uint32_t g2_main_clock_request_480f0c(uint32_t, uint32_t);

typedef struct {
    uint8_t clock_id;
    uint32_t value_address;
} clock_request_t;

static const clock_request_t group0_leaf[] = {
    {0xc7u,0x20000138u},{0x40u,0x2000013cu},
    {0x41u,0x20000140u},{0x48u,0x2000015cu},
};
static const clock_request_t group0_mid[] = {
    {0x42u,0x20000144u},{0x43u,0x20000148u},
};
static const clock_request_t group0_high[] = {
    {0x44u,0x2000014cu},{0x45u,0x20000150u},
    {0x46u,0x20000154u},{0x47u,0x20000158u},
};
static const clock_request_t group0_top[] = {
    {0x25u,0x20000160u},{0x26u,0x20000164u},
    {0x27u,0x20000168u},{0x28u,0x2000016cu},
    {0x29u,0x20000170u},{0x2au,0x20000174u},
    {0x2bu,0x20000178u},{0x2cu,0x2000017cu},
    {0x2du,0x20000180u},
};
static const clock_request_t group1_leaf[] = {
    {0x31u,0x20000184u},{0x5fu,0x20000188u},
    {0x60u,0x2000018cu},{0x67u,0x200001a8u},
    {0x68u,0x200001acu},
};
static const clock_request_t group1_mid[] = {
    {0x61u,0x20000190u},{0x62u,0x20000194u},
};
static const clock_request_t group1_high[] = {
    {0x63u,0x20000198u},{0x64u,0x2000019cu},
    {0x65u,0x200001a0u},{0x66u,0x200001a4u},
};

static void request_group(const clock_request_t *entries, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        const uint32_t value = *(const volatile uint32_t *)(uintptr_t)
            entries[i].value_address;
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

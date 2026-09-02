/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

volatile uint8_t open_cfw_em9305_ram_u8[16];
volatile uint16_t open_cfw_em9305_ram_u16[4];
volatile uint32_t open_cfw_em9305_ram_u32[4];
volatile uint32_t open_cfw_em9305_mmio_u32;
uint8_t open_cfw_em9305_zero_144_destination[144];

void *open_cfw_em9305_memset_33301c(void *destination, int value, size_t length)
{
    uint8_t *bytes = destination;
    size_t index;

    for (index = 0; index < length; ++index) {
        bytes[index] = (uint8_t)value;
    }
    return destination;
}

void open_cfw_em9305_noop_302d80_impl(void);
uint8_t open_cfw_em9305_load_u8_303e50_impl(void);
uint8_t open_cfw_em9305_load_u8_303e5c_impl(void);
uint8_t open_cfw_em9305_load_u8_303f50_impl(void);
uint32_t open_cfw_em9305_load_u32_303f68_impl(void);
uint32_t open_cfw_em9305_equals_one_3047b0_impl(void);
void open_cfw_em9305_noop_304eb4_impl(void);
void open_cfw_em9305_store_u32_3069b8_impl(uint32_t value);
uint32_t open_cfw_em9305_nonzero_307c08_impl(void);
uint32_t open_cfw_em9305_nonzero_307dd8_impl(void);
uint16_t open_cfw_em9305_load_u16_30f368_impl(void);
void open_cfw_em9305_set_bit23_30f710_impl(void);
void open_cfw_em9305_set_bit23_30f720_impl(void);
void open_cfw_em9305_store_u8_310480_impl(uint8_t value);
void open_cfw_em9305_store_u8_31048c_impl(uint8_t value);
uint32_t open_cfw_em9305_load_u32_3108f4_impl(void);
void open_cfw_em9305_store_u16_311f84_impl(uint16_t value);
void open_cfw_em9305_store_u8_3122f0_impl(uint8_t value);
void open_cfw_em9305_zero_144_31369c_impl(void);
uint16_t open_cfw_em9305_load_u16_313760_impl(void);
void open_cfw_em9305_noop_313778_impl(void);
void open_cfw_em9305_noop_3137f4_impl(void);
void open_cfw_em9305_noop_3137f8_impl(void);
uint8_t open_cfw_em9305_load_offset23_31b2f8_impl(const uint8_t *base);
void open_cfw_em9305_store_40_32cac4_impl(uint8_t *base);
void open_cfw_em9305_store_30_32cacc_impl(uint8_t *base);
void open_cfw_em9305_store_48_32cad4_impl(uint8_t *base);
void open_cfw_em9305_store_34_32cadc_impl(uint8_t *base);

int main(void)
{
    uint8_t structure[32] = {0};
    size_t index;

    open_cfw_em9305_ram_u8[0] = 0xa1u;
    open_cfw_em9305_ram_u8[1] = 0xb2u;
    open_cfw_em9305_ram_u8[2] = 0xc3u;
    assert(open_cfw_em9305_load_u8_303e50_impl() == 0xa1u);
    assert(open_cfw_em9305_load_u8_303e5c_impl() == 0xb2u);
    assert(open_cfw_em9305_load_u8_303f50_impl() == 0xc3u);

    open_cfw_em9305_ram_u32[0] = UINT32_C(0x12345678);
    assert(open_cfw_em9305_load_u32_303f68_impl() == UINT32_C(0x12345678));
    open_cfw_em9305_ram_u8[3] = 1u;
    assert(open_cfw_em9305_equals_one_3047b0_impl() == 1u);
    open_cfw_em9305_ram_u8[3] = 2u;
    assert(open_cfw_em9305_equals_one_3047b0_impl() == 0u);

    open_cfw_em9305_store_u32_3069b8_impl(UINT32_C(0x89abcdef));
    assert(open_cfw_em9305_ram_u32[1] == UINT32_C(0x89abcdef));
    open_cfw_em9305_ram_u8[4] = 0u;
    open_cfw_em9305_ram_u8[5] = 7u;
    assert(open_cfw_em9305_nonzero_307c08_impl() == 0u);
    assert(open_cfw_em9305_nonzero_307dd8_impl() == 1u);

    open_cfw_em9305_ram_u16[0] = UINT16_C(0x9abc);
    assert(open_cfw_em9305_load_u16_30f368_impl() == UINT16_C(0x9abc));
    open_cfw_em9305_mmio_u32 = UINT32_C(0x100);
    open_cfw_em9305_set_bit23_30f710_impl();
    open_cfw_em9305_set_bit23_30f720_impl();
    assert(open_cfw_em9305_mmio_u32 == (UINT32_C(0x100) | (UINT32_C(1) << 23)));

    open_cfw_em9305_store_u8_310480_impl(0x55u);
    open_cfw_em9305_store_u8_31048c_impl(0x66u);
    assert(open_cfw_em9305_ram_u8[6] == 0x55u);
    assert(open_cfw_em9305_ram_u8[7] == 0x66u);
    open_cfw_em9305_ram_u32[2] = UINT32_C(0xdeadbeef);
    assert(open_cfw_em9305_load_u32_3108f4_impl() == UINT32_C(0xdeadbeef));
    open_cfw_em9305_store_u16_311f84_impl(UINT16_C(0x7654));
    open_cfw_em9305_store_u8_3122f0_impl(0x87u);
    assert(open_cfw_em9305_ram_u16[1] == UINT16_C(0x7654));
    assert(open_cfw_em9305_ram_u8[8] == 0x87u);

    for (index = 0; index < 144; ++index) {
        open_cfw_em9305_zero_144_destination[index] = 0xa5u;
    }
    open_cfw_em9305_zero_144_31369c_impl();
    for (index = 0; index < 144; ++index) {
        assert(open_cfw_em9305_zero_144_destination[index] == 0u);
    }
    open_cfw_em9305_ram_u16[2] = UINT16_C(0x2468);
    assert(open_cfw_em9305_load_u16_313760_impl() == UINT16_C(0x2468));

    structure[23] = 0xd4u;
    assert(open_cfw_em9305_load_offset23_31b2f8_impl(structure) == 0xd4u);
    open_cfw_em9305_store_40_32cac4_impl(structure);
    assert(structure[12] == 40u);
    open_cfw_em9305_store_30_32cacc_impl(structure);
    assert(structure[12] == 30u);
    open_cfw_em9305_store_48_32cad4_impl(structure);
    assert(structure[12] == 48u);
    open_cfw_em9305_store_34_32cadc_impl(structure);
    assert(structure[12] == 34u);

    open_cfw_em9305_noop_302d80_impl();
    open_cfw_em9305_noop_304eb4_impl();
    open_cfw_em9305_noop_313778_impl();
    open_cfw_em9305_noop_3137f4_impl();
    open_cfw_em9305_noop_3137f8_impl();
    return 0;
}

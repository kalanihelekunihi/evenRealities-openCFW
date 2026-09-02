/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Production ARCv2-EM replacements for the mechanically reconstructible
 * EM9305 residual-tail entries.  Each function has one authenticated stock
 * entry and is placed there by reconstructible_tail.ld.
 */

#include <stddef.h>
#include <stdint.h>

#ifdef OPEN_CFW_EM9305_HOST_TEST
#define OPEN_CFW_EM9305_ENTRY(name) __attribute__((used, noinline))
#else
#define OPEN_CFW_EM9305_ENTRY(name) \
    __attribute__((used, noinline, aligned(2), section(".text.impl." name)))
#endif

#define open_cfw_em9305_noop_302d80 open_cfw_em9305_noop_302d80_impl
#define open_cfw_em9305_load_u8_303e50 open_cfw_em9305_load_u8_303e50_impl
#define open_cfw_em9305_load_u8_303e5c open_cfw_em9305_load_u8_303e5c_impl
#define open_cfw_em9305_load_u8_303f50 open_cfw_em9305_load_u8_303f50_impl
#define open_cfw_em9305_load_u32_303f68 open_cfw_em9305_load_u32_303f68_impl
#define open_cfw_em9305_equals_one_3047b0 open_cfw_em9305_equals_one_3047b0_impl
#define open_cfw_em9305_noop_304eb4 open_cfw_em9305_noop_304eb4_impl
#define open_cfw_em9305_store_u32_3069b8 open_cfw_em9305_store_u32_3069b8_impl
#define open_cfw_em9305_nonzero_307c08 open_cfw_em9305_nonzero_307c08_impl
#define open_cfw_em9305_nonzero_307dd8 open_cfw_em9305_nonzero_307dd8_impl
#define open_cfw_em9305_load_u16_30f368 open_cfw_em9305_load_u16_30f368_impl
#define open_cfw_em9305_set_bit23_30f710 open_cfw_em9305_set_bit23_30f710_impl
#define open_cfw_em9305_set_bit23_30f720 open_cfw_em9305_set_bit23_30f720_impl
#define open_cfw_em9305_store_u8_310480 open_cfw_em9305_store_u8_310480_impl
#define open_cfw_em9305_store_u8_31048c open_cfw_em9305_store_u8_31048c_impl
#define open_cfw_em9305_load_u32_3108f4 open_cfw_em9305_load_u32_3108f4_impl
#define open_cfw_em9305_store_u16_311f84 open_cfw_em9305_store_u16_311f84_impl
#define open_cfw_em9305_store_u8_3122f0 open_cfw_em9305_store_u8_3122f0_impl
#define open_cfw_em9305_zero_144_31369c open_cfw_em9305_zero_144_31369c_impl
#define open_cfw_em9305_load_u16_313760 open_cfw_em9305_load_u16_313760_impl
#define open_cfw_em9305_noop_313778 open_cfw_em9305_noop_313778_impl
#define open_cfw_em9305_noop_3137f4 open_cfw_em9305_noop_3137f4_impl
#define open_cfw_em9305_noop_3137f8 open_cfw_em9305_noop_3137f8_impl
#define open_cfw_em9305_load_offset23_31b2f8 open_cfw_em9305_load_offset23_31b2f8_impl
#define open_cfw_em9305_store_40_32cac4 open_cfw_em9305_store_40_32cac4_impl
#define open_cfw_em9305_store_30_32cacc open_cfw_em9305_store_30_32cacc_impl
#define open_cfw_em9305_store_48_32cad4 open_cfw_em9305_store_48_32cad4_impl
#define open_cfw_em9305_store_34_32cadc open_cfw_em9305_store_34_32cadc_impl

#ifdef OPEN_CFW_EM9305_HOST_TEST
extern volatile uint8_t open_cfw_em9305_ram_u8[16];
extern volatile uint16_t open_cfw_em9305_ram_u16[4];
extern volatile uint32_t open_cfw_em9305_ram_u32[4];
extern volatile uint32_t open_cfw_em9305_mmio_u32;
extern uint8_t open_cfw_em9305_zero_144_destination[144];
#define RAM_U8_80163B (&open_cfw_em9305_ram_u8[0])
#define RAM_U8_801639 (&open_cfw_em9305_ram_u8[1])
#define RAM_U8_8016BE (&open_cfw_em9305_ram_u8[2])
#define RAM_U32_80163C (&open_cfw_em9305_ram_u32[0])
#define RAM_U8_8018BC (&open_cfw_em9305_ram_u8[3])
#define RAM_U32_80190C (&open_cfw_em9305_ram_u32[1])
#define RAM_U8_803BB8 (&open_cfw_em9305_ram_u8[4])
#define RAM_U8_804FFC (&open_cfw_em9305_ram_u8[5])
#define RAM_U16_80FB9C (&open_cfw_em9305_ram_u16[0])
#define MMIO_U32_F00430 (&open_cfw_em9305_mmio_u32)
#define RAM_U8_805EA0 (&open_cfw_em9305_ram_u8[6])
#define RAM_U8_805EA6 (&open_cfw_em9305_ram_u8[7])
#define RAM_U32_801998 (&open_cfw_em9305_ram_u32[2])
#define RAM_U16_805FDC (&open_cfw_em9305_ram_u16[1])
#define RAM_U8_80FD5E (&open_cfw_em9305_ram_u8[8])
#define RAM_U16_805F1C (&open_cfw_em9305_ram_u16[2])
#define ZERO_144_DESTINATION open_cfw_em9305_zero_144_destination
#else
#define OPEN_CFW_EM9305_PTR(type, address) \
    ((volatile type *)(uintptr_t)(address))
#define RAM_U8_80163B OPEN_CFW_EM9305_PTR(uint8_t, 0x0080163bu)
#define RAM_U8_801639 OPEN_CFW_EM9305_PTR(uint8_t, 0x00801639u)
#define RAM_U8_8016BE OPEN_CFW_EM9305_PTR(uint8_t, 0x008016beu)
#define RAM_U32_80163C OPEN_CFW_EM9305_PTR(uint32_t, 0x0080163cu)
#define RAM_U8_8018BC OPEN_CFW_EM9305_PTR(uint8_t, 0x008018bcu)
#define RAM_U32_80190C OPEN_CFW_EM9305_PTR(uint32_t, 0x0080190cu)
#define RAM_U8_803BB8 OPEN_CFW_EM9305_PTR(uint8_t, 0x00803bb8u)
#define RAM_U8_804FFC OPEN_CFW_EM9305_PTR(uint8_t, 0x00804ffcu)
#define RAM_U16_80FB9C OPEN_CFW_EM9305_PTR(uint16_t, 0x0080fb9cu)
#define MMIO_U32_F00430 OPEN_CFW_EM9305_PTR(uint32_t, 0x00f00430u)
#define RAM_U8_805EA0 OPEN_CFW_EM9305_PTR(uint8_t, 0x00805ea0u)
#define RAM_U8_805EA6 OPEN_CFW_EM9305_PTR(uint8_t, 0x00805ea6u)
#define RAM_U32_801998 OPEN_CFW_EM9305_PTR(uint32_t, 0x00801998u)
#define RAM_U16_805FDC OPEN_CFW_EM9305_PTR(uint16_t, 0x00805fdcu)
#define RAM_U8_80FD5E OPEN_CFW_EM9305_PTR(uint8_t, 0x0080fd5eu)
#define RAM_U16_805F1C OPEN_CFW_EM9305_PTR(uint16_t, 0x00805f1cu)
#define ZERO_144_DESTINATION OPEN_CFW_EM9305_PTR(uint8_t, 0x00805f28u)
#endif

extern void *open_cfw_em9305_memset_33301c(
    void *destination,
    int value,
    size_t length
);

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_noop_302d80")
void open_cfw_em9305_noop_302d80(void)
{
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u8_303e50")
uint8_t open_cfw_em9305_load_u8_303e50(void)
{
    return *RAM_U8_80163B;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u8_303e5c")
uint8_t open_cfw_em9305_load_u8_303e5c(void)
{
    return *RAM_U8_801639;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u8_303f50")
uint8_t open_cfw_em9305_load_u8_303f50(void)
{
    return *RAM_U8_8016BE;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u32_303f68")
uint32_t open_cfw_em9305_load_u32_303f68(void)
{
    return *RAM_U32_80163C;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_equals_one_3047b0")
uint32_t open_cfw_em9305_equals_one_3047b0(void)
{
    return *RAM_U8_8018BC == 1u ? 1u : 0u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_noop_304eb4")
void open_cfw_em9305_noop_304eb4(void)
{
    __asm__ volatile ("nop");
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_u32_3069b8")
void open_cfw_em9305_store_u32_3069b8(uint32_t value)
{
    *RAM_U32_80190C = value;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_nonzero_307c08")
uint32_t open_cfw_em9305_nonzero_307c08(void)
{
    return *RAM_U8_803BB8 != 0u ? 1u : 0u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_nonzero_307dd8")
uint32_t open_cfw_em9305_nonzero_307dd8(void)
{
    return *RAM_U8_804FFC != 0u ? 1u : 0u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u16_30f368")
uint16_t open_cfw_em9305_load_u16_30f368(void)
{
    return *RAM_U16_80FB9C;
}

static void open_cfw_em9305_set_mmio_bit23(void)
{
    *MMIO_U32_F00430 |= UINT32_C(1) << 23;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_set_bit23_30f710")
void open_cfw_em9305_set_bit23_30f710(void)
{
    open_cfw_em9305_set_mmio_bit23();
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_set_bit23_30f720")
void open_cfw_em9305_set_bit23_30f720(void)
{
    open_cfw_em9305_set_mmio_bit23();
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_u8_310480")
void open_cfw_em9305_store_u8_310480(uint8_t value)
{
    *RAM_U8_805EA0 = value;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_u8_31048c")
void open_cfw_em9305_store_u8_31048c(uint8_t value)
{
    *RAM_U8_805EA6 = value;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u32_3108f4")
uint32_t open_cfw_em9305_load_u32_3108f4(void)
{
    return *RAM_U32_801998;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_u16_311f84")
void open_cfw_em9305_store_u16_311f84(uint16_t value)
{
    *RAM_U16_805FDC = value;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_u8_3122f0")
void open_cfw_em9305_store_u8_3122f0(uint8_t value)
{
    *RAM_U8_80FD5E = value;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_zero_144_31369c")
void open_cfw_em9305_zero_144_31369c(void)
{
    (void)open_cfw_em9305_memset_33301c(
        (void *)ZERO_144_DESTINATION,
        0,
        144u
    );
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_u16_313760")
uint16_t open_cfw_em9305_load_u16_313760(void)
{
    return *RAM_U16_805F1C;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_noop_313778")
void open_cfw_em9305_noop_313778(void)
{
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_noop_3137f4")
void open_cfw_em9305_noop_3137f4(void)
{
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_noop_3137f8")
void open_cfw_em9305_noop_3137f8(void)
{
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_load_offset23_31b2f8")
uint8_t open_cfw_em9305_load_offset23_31b2f8(const uint8_t *base)
{
    return base[23];
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_40_32cac4")
void open_cfw_em9305_store_40_32cac4(uint8_t *base)
{
    base[12] = 40u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_30_32cacc")
void open_cfw_em9305_store_30_32cacc(uint8_t *base)
{
    base[12] = 30u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_48_32cad4")
void open_cfw_em9305_store_48_32cad4(uint8_t *base)
{
    base[12] = 48u;
}

OPEN_CFW_EM9305_ENTRY("open_cfw_em9305_store_34_32cadc")
void open_cfw_em9305_store_34_32cadc(uint8_t *base)
{
    base[12] = 34u;
}

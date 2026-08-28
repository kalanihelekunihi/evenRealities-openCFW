/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 bootloader mode routing and cleanup. */

typedef __UINT8_TYPE__ open_cfw_route_u8;
typedef __UINT32_TYPE__ open_cfw_route_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_route_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_route_u32, open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_bitmap_row0_set_421a30(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_bitmap_row0_clear_421a62(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_bitmap_row1_set_421a94(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_bitmap_row1_clear_421ad6(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_mode0_enable_421bd2(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_mode0_disable_421cce(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_mode1_enable_421b08(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_mode1_disable_421b5c(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row4_enable_421d5e(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row4_disable_421e4a(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row5_enable_421eba(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row5_disable_422040(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row6_enable_4220b2(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_row6_disable_422220(open_cfw_route_u32);
extern open_cfw_route_u32 open_cfw_bootloader_mode_disable_route_target_422364(open_cfw_route_u32, open_cfw_route_u32);
extern void *open_cfw_bootloader_memcpy_41568c(void *, const void *, open_cfw_route_u32);
#define OPEN_CFW_ROUTE_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_route_u32 open_cfw_route_host_bitmap_test(open_cfw_route_u32, open_cfw_route_u32);
open_cfw_route_u32 open_cfw_route_host_enable(open_cfw_route_u8, open_cfw_route_u8);
open_cfw_route_u32 open_cfw_route_host_disable(open_cfw_route_u8, open_cfw_route_u8);
void open_cfw_route_host_copy(void *, const void *, open_cfw_route_u32);
extern open_cfw_route_u8 open_cfw_route_host_configuration[20];
#define OPEN_CFW_ROUTE_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_ROUTE_ATTR
open_cfw_route_u32 open_cfw_bootloader_mode_enable_route_4222f0(open_cfw_route_u32 kind, open_cfw_route_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r7, lr}\n" "movs r2, #6\n" "movs r2, r1\n" "uxtb r2, r2\n" "cmp r2, #0x39\n" "blt 1f\n" "movs r0, #6\n" "b 9f\n"
        "1:\n" "uxtb r0, r0\n" "cmp r0, #0\n" "beq 2f\n" "cmp r0, #2\n" "beq 4f\n" "blo 3f\n" "cmp r0, #4\n" "beq 6f\n" "blo 5f\n" "cmp r0, #6\n" "beq 8f\n" "blo 7f\n" "b 10f\n"
        "2:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_bitmap_row0_set_421a30\n" "b 9f\n"
        "3:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_bitmap_row1_set_421a94\n" "b 9f\n"
        "4:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_mode0_enable_421bd2\n" "b 9f\n"
        "5:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_mode1_enable_421b08\n" "b 9f\n"
        "6:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row4_enable_421d5e\n" "b 9f\n"
        "7:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row5_enable_421eba\n" "b 9f\n"
        "8:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row6_enable_4220b2\n" "b 9f\n"
        "10:\n" "movs r0, #6\n" "9:\n" "pop {r1, pc}\n");
#else
    kind = (open_cfw_route_u8)kind; bit = (open_cfw_route_u8)bit;
    if (bit >= 0x39U || kind > 6U) return 6U;
    return open_cfw_route_host_enable((open_cfw_route_u8)kind, (open_cfw_route_u8)bit);
#endif
}

OPEN_CFW_ROUTE_ATTR
open_cfw_route_u32 open_cfw_bootloader_mode_disable_route_422364(open_cfw_route_u32 kind, open_cfw_route_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r7, lr}\n" "movs r2, #0\n" "movs r2, r1\n" "uxtb r2, r2\n" "cmp r2, #0x39\n" "blt 1f\n" "movs r0, #6\n" "b 9f\n"
        "1:\n" "uxtb r0, r0\n" "cmp r0, #0\n" "beq 2f\n" "cmp r0, #2\n" "beq 4f\n" "blo 3f\n" "cmp r0, #4\n" "beq 6f\n" "blo 5f\n" "cmp r0, #6\n" "beq 8f\n" "blo 7f\n" "b 10f\n"
        "2:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_bitmap_row0_clear_421a62\n" "b 9f\n"
        "3:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_bitmap_row1_clear_421ad6\n" "b 9f\n"
        "4:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_mode0_disable_421cce\n" "b 9f\n"
        "5:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_mode1_disable_421b5c\n" "b 9f\n"
        "6:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row4_disable_421e4a\n" "b 9f\n"
        "7:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row5_disable_422040\n" "b 9f\n"
        "8:\n" "movs r0, r1\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_row6_disable_422220\n" "b 9f\n"
        "10:\n" "movs r0, #6\n" "9:\n" "pop {r1, pc}\n");
#else
    kind = (open_cfw_route_u8)kind; bit = (open_cfw_route_u8)bit;
    if (bit >= 0x39U || kind > 6U) return 6U;
    return open_cfw_route_host_disable((open_cfw_route_u8)kind, (open_cfw_route_u8)bit);
#endif
}

OPEN_CFW_ROUTE_ATTR
open_cfw_route_u32 open_cfw_bootloader_mode_clear_all_4223d8(open_cfw_route_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n" "movs r4, r0\n" "movs r0, r4\n" "uxtb r0, r0\n" "cmp r0, #0x39\n" "blt 1f\n" "movs r0, #6\n" "b 5f\n"
        "1:\n" "movs r5, #0\n" "b 4f\n"
        "2:\n" "movs r1, r4\n" "uxtb r1, r1\n" "movs r0, r5\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_bitmap_test_4215dc\n" "cmp r0, #0\n" "beq 3f\n" "movs r1, r4\n" "uxtb r1, r1\n" "movs r0, r5\n" "uxtb r0, r0\n" "bl open_cfw_bootloader_mode_disable_route_target_422364\n"
        "3:\n" "adds r5, r5, #1\n" "4:\n" "movs r0, r5\n" "uxtb r0, r0\n" "cmp r0, #7\n" "blt 2b\n" "movs r0, #0\n" "5:\n" "pop {r1, r4, r5, pc}\n");
#else
    open_cfw_route_u32 row; bit = (open_cfw_route_u8)bit;
    if (bit >= 0x39U) return 6U;
    for (row = 0U; row < 7U; ++row) if (open_cfw_route_host_bitmap_test(row, bit) != 0U) (void)open_cfw_route_host_disable((open_cfw_route_u8)row, (open_cfw_route_u8)bit);
    return 0U;
#endif
}

OPEN_CFW_ROUTE_ATTR
open_cfw_route_u32 open_cfw_bootloader_mode_configuration_copy_422416(const void *configuration)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r4, lr}\n" "cmp r0, #0\n" "bne 1f\n" "movs r0, #6\n" "b 2f\n"
        "1:\n" "movs r2, #0x14\n" "ldr r4, [pc, #0x40]\n" "movs r1, r0\n" "movs r0, r4\n" "bl open_cfw_bootloader_memcpy_41568c\n" "movs r0, #0\n"
        "2:\n" "pop {r4, pc}\n");
#else
    if (configuration == (const void *)0) return 6U;
    open_cfw_route_host_copy(open_cfw_route_host_configuration, configuration, 20U); return 0U;
#endif
}

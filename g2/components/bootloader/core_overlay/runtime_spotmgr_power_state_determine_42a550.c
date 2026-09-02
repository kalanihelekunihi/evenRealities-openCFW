/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager power-state and Ton-state classifier authenticated
 * at G2 bootloader address 0x0042A550.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_state_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_state_u8;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_state_u32
open_cfw_bootloader_spotmgr_power_state_determine_42a550(
    const void *power_status __attribute__((unused)),
    open_cfw_spotmgr_state_u32 *power_state __attribute__((unused)),
    open_cfw_spotmgr_state_u32 *ton_state __attribute__((unused)))
{
    __asm volatile(
        "push {r4, r5}\n"
        "ldr.w r3, [pc, #0x76c]\n"
        "ldr r4, [r3]\n"
        "ldrb r3, [r0, #0x10]\n"
        "ands r3, r3, #0xf\n"
        "bfi r4, r3, #8, #4\n"
        "ldrb r3, [r0, #0x11]\n"
        "cmp r3, #1\n"
        "bne.n .Lspot_state_cpu_lp\n"
        "movs r3, #1\n"
        "bfi r4, r3, #0, #4\n"
        "b.n .Lspot_state_cpu_done\n"
        ".Lspot_state_cpu_lp:\n"
        "ldrb r3, [r0, #0x11]\n"
        "cmp r3, #0\n"
        "bne.n .Lspot_state_cpu_retained\n"
        "lsrs r4, r4, #4\n"
        "lsls r4, r4, #4\n"
        "b.n .Lspot_state_cpu_done\n"
        ".Lspot_state_cpu_retained:\n"
        "ldr.w r3, [pc, #0x744]\n"
        "ldr r3, [r3]\n"
        "ands r3, r3, #3\n"
        "cmp r3, #2\n"
        "beq.n .Lspot_state_cpu_set_hp\n"
        "lsrs r4, r4, #4\n"
        "lsls r4, r4, #4\n"
        "b.n .Lspot_state_cpu_done\n"
        ".Lspot_state_cpu_set_hp:\n"
        "movs r3, #1\n"
        "bfi r4, r3, #0, #4\n"
        ".Lspot_state_cpu_done:\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #1\n"
        "beq.n .Lspot_state_periph1_on\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #2\n"
        "beq.n .Lspot_state_periph1_on\n"
        "ldr r3, [r0]\n"
        "lsls r3, r3, #2\n"
        "bne.n .Lspot_state_periph1_on\n"
        "ldr r3, [r0, #4]\n"
        "movw r5, #0x4c4\n"
        "tst r3, r5\n"
        "beq.n .Lspot_state_periph1_off\n"
        ".Lspot_state_periph1_on:\n"
        "movs r3, #1\n"
        "bfi r4, r3, #4, #4\n"
        "b.n .Lspot_state_periph1_done\n"
        ".Lspot_state_periph1_off:\n"
        "bics r4, r4, #0xf0\n"
        ".Lspot_state_periph1_done:\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #2\n"
        "bne.n .Lspot_state_gpu_lp_test\n"
        "movs r3, #2\n"
        "bfi r4, r3, #0xc, #4\n"
        "b.n .Lspot_state_gpu_done\n"
        ".Lspot_state_gpu_lp_test:\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #1\n"
        "bne.n .Lspot_state_gpu_off\n"
        "movs r3, #1\n"
        "bfi r4, r3, #0xc, #4\n"
        "b.n .Lspot_state_gpu_done\n"
        ".Lspot_state_gpu_off:\n"
        "bics r4, r4, #0xf000\n"
        ".Lspot_state_gpu_done:\n"
        "ldr r3, [r0]\n"
        "lsls r3, r3, #2\n"
        "bne.n .Lspot_state_periph_on\n"
        "ldr r3, [r0, #4]\n"
        "movw r5, #0x4c4\n"
        "tst r3, r5\n"
        "beq.n .Lspot_state_periph_off\n"
        ".Lspot_state_periph_on:\n"
        "movs r3, #1\n"
        "bfi r4, r3, #0x10, #4\n"
        "b.n .Lspot_state_periph_done\n"
        ".Lspot_state_periph_off:\n"
        "bics r4, r4, #0xf0000\n"
        ".Lspot_state_periph_done:\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #1\n"
        "beq.n .Lspot_state_gpu_sdio_on\n"
        "ldrb r3, [r0, #0x12]\n"
        "cmp r3, #2\n"
        "beq.n .Lspot_state_gpu_sdio_on\n"
        "ldr r0, [r0]\n"
        "tst.w r0, #0xc00000\n"
        "beq.n .Lspot_state_gpu_sdio_off\n"
        ".Lspot_state_gpu_sdio_on:\n"
        "movs r0, #1\n"
        "bfi r4, r0, #0x14, #4\n"
        "b.n .Lspot_state_gpu_sdio_done\n"
        ".Lspot_state_gpu_sdio_off:\n"
        "bics r4, r4, #0xf00000\n"
        ".Lspot_state_gpu_sdio_done:\n"
        "ldr.w r0, [pc, #0x6ac]\n"
        "ands r0, r4\n"
        "cmp r0, #0\n"
        "beq.w .Lspot_power_desc_000000\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000001\n"
        "subs r0, #0xf\n"
        "beq.w .Lspot_power_desc_000010\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000011\n"
        "subs r0, #0xef\n"
        "beq.w .Lspot_power_desc_000100\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000101\n"
        "subs r0, #0xf\n"
        "beq.w .Lspot_power_desc_000110\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000111\n"
        "subs r0, #0xef\n"
        "beq.n .Lspot_power_desc_000200\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000201\n"
        "subs r0, #0xf\n"
        "beq.w .Lspot_power_desc_000210\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000211\n"
        "subs r0, #0xef\n"
        "beq.n .Lspot_power_desc_000300\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000301\n"
        "subs r0, #0xf\n"
        "beq.w .Lspot_power_desc_000310\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_000311\n"
        "ldr.w r3, [pc, #0x64c]\n"
        "subs r0, r0, r3\n"
        "beq.w .Lspot_power_desc_100010\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_100011\n"
        "subs r0, #0xff\n"
        "beq.w .Lspot_power_desc_100110\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_100111\n"
        "subs r0, #0xff\n"
        "beq.w .Lspot_power_desc_100210\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_100211\n"
        "subs r0, #0xff\n"
        "beq.w .Lspot_power_desc_100310\n"
        "subs r0, r0, #1\n"
        "beq.w .Lspot_power_desc_100311\n"
        "b.n .Lspot_state_out_of_range\n"

        ".Lspot_power_desc_000300:\n"
        "ldr.w r0, [pc, #0x61c]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000300_normal\n"
        "movs r0, #4\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_000300_normal:\n"
        "movs r0, #0\n"
        "str r0, [r1]\n"

        ".Lspot_power_to_ton:\n"
        "ldr.w r0, [pc, #0x60c]\n"
        "ands r4, r0\n"
        "cmp r4, #0\n"
        "beq.n .Lspot_ton_desc_00000\n"
        "cmp r4, #1\n"
        "beq.w .Lspot_ton_desc_00001\n"
        "cmp.w r4, #0x1000\n"
        "beq.w .Lspot_ton_desc_01000\n"
        "movw r0, #0x1001\n"
        "cmp r4, r0\n"
        "beq.w .Lspot_ton_desc_01001\n"
        "cmp.w r4, #0x2000\n"
        "beq.w .Lspot_ton_desc_02000\n"
        "movw r0, #0x2001\n"
        "cmp r4, r0\n"
        "beq.w .Lspot_ton_desc_02001\n"
        "cmp.w r4, #0x10000\n"
        "beq.w .Lspot_ton_desc_10000\n"
        "cmp.w r4, #0x10001\n"
        "beq.w .Lspot_ton_desc_10001\n"
        "cmp.w r4, #0x11000\n"
        "beq.w .Lspot_ton_desc_01000\n"
        "ldr.w r0, [pc, #0x5c4]\n"
        "cmp r4, r0\n"
        "beq.w .Lspot_ton_desc_01001\n"
        "cmp.w r4, #0x12000\n"
        "beq.w .Lspot_ton_desc_02000\n"
        "ldr.w r0, [pc, #0x5b4]\n"
        "cmp r4, r0\n"
        "beq.w .Lspot_ton_desc_02001\n"
        "b.n .Lspot_ton_out_of_range\n"

        ".Lspot_ton_desc_00000:\n"
        "movs r0, #0\n"
        "str r0, [r2]\n"
        ".Lspot_state_success:\n"
        "movs r0, #0\n"
        ".Lspot_state_return:\n"
        "pop {r4, r5}\n"
        "bx lr\n"

        ".Lspot_power_desc_000200:\n"
        "ldr.w r0, [pc, #0x594]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000200_normal\n"
        "movs r0, #5\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_200\n"
        ".Lspot_power_000200_normal:\n"
        "movs r0, #1\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_200:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000100:\n"
        "ldr.w r0, [pc, #0x57c]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000100_normal\n"
        "movs r0, #6\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_100\n"
        ".Lspot_power_000100_normal:\n"
        "movs r0, #2\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_100:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000000:\n"
        "ldr.w r0, [pc, #0x568]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000000_normal\n"
        "movs r0, #7\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_000\n"
        ".Lspot_power_000000_normal:\n"
        "movs r0, #3\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_000:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000310:\n"
        "movs r0, #4\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000210:\n"
        "movs r0, #5\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000110:\n"
        "movs r0, #6\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000010:\n"
        "movs r0, #7\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000301:\n"
        "ldr.w r0, [pc, #0x538]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000301_normal\n"
        "movs r0, #0xc\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_301\n"
        ".Lspot_power_000301_normal:\n"
        "movs r0, #8\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_301:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000201:\n"
        "ldr.w r0, [pc, #0x524]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000201_normal\n"
        "movs r0, #0xd\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_201\n"
        ".Lspot_power_000201_normal:\n"
        "movs r0, #9\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_201:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000101:\n"
        "ldr.w r0, [pc, #0x50c]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000101_normal\n"
        "movs r0, #0xe\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_101\n"
        ".Lspot_power_000101_normal:\n"
        "movs r0, #0xa\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_101:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000001:\n"
        "ldr.w r0, [pc, #0x4f8]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_power_000001_normal\n"
        "movs r0, #0xf\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton_001\n"
        ".Lspot_power_000001_normal:\n"
        "movs r0, #0xb\n"
        "str r0, [r1]\n"
        ".Lspot_power_to_ton_001:\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000311:\n"
        ".Lspot_power_desc_100311:\n"
        "movs r0, #0xc\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000211:\n"
        ".Lspot_power_desc_100211:\n"
        "movs r0, #0xd\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000111:\n"
        ".Lspot_power_desc_100111:\n"
        "movs r0, #0xe\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_000011:\n"
        ".Lspot_power_desc_100011:\n"
        "movs r0, #0xf\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_100310:\n"
        "movs r0, #0x10\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_100210:\n"
        "movs r0, #0x11\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_100110:\n"
        "movs r0, #0x12\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_power_desc_100010:\n"
        "movs r0, #0x13\n"
        "str r0, [r1]\n"
        "b.n .Lspot_power_to_ton\n"
        ".Lspot_state_out_of_range:\n"
        "movs r0, #5\n"
        "b.n .Lspot_state_return\n"

        ".Lspot_ton_desc_00001:\n"
        "ldr.w r0, [pc, #0x4ac]\n"
        "ldrb r0, [r0]\n"
        "lsls r0, r0, #0x1f\n"
        "bpl.n .Lspot_ton_00001_normal\n"
        "movs r0, #7\n"
        "str r0, [r2]\n"
        "b.n .Lspot_ton_success_1\n"
        ".Lspot_ton_00001_normal:\n"
        "movs r0, #1\n"
        "str r0, [r2]\n"
        ".Lspot_ton_success_1:\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_01000:\n"
        "movs r0, #2\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_02000:\n"
        "movs r0, #3\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_01001:\n"
        "movs r0, #4\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_02001:\n"
        "movs r0, #5\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_10000:\n"
        "movs r0, #6\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_desc_10001:\n"
        "movs r0, #7\n"
        "str r0, [r2]\n"
        "b.n .Lspot_state_success\n"
        ".Lspot_ton_out_of_range:\n"
        "movs r0, #5\n"
        "b.n .Lspot_state_return\n"
    );
}

#else

typedef struct open_cfw_spotmgr_power_status {
    open_cfw_spotmgr_state_u32 device_power;
    open_cfw_spotmgr_state_u32 audio_power;
    open_cfw_spotmgr_state_u32 memory_power;
    open_cfw_spotmgr_state_u32 ssram_power;
    open_cfw_spotmgr_state_u8 temperature_range;
    open_cfw_spotmgr_state_u8 cpu_state;
    open_cfw_spotmgr_state_u8 gpu_state;
} open_cfw_spotmgr_power_status;

static open_cfw_spotmgr_state_u32 open_cfw_spotmgr_insert_field(
    open_cfw_spotmgr_state_u32 value,
    open_cfw_spotmgr_state_u32 field,
    open_cfw_spotmgr_state_u32 shift)
{
    return (value & ~(15U << shift)) | ((field & 15U) << shift);
}

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_state_u32
open_cfw_bootloader_spotmgr_power_state_determine_42a550(
    const open_cfw_spotmgr_power_status *status,
    open_cfw_spotmgr_state_u32 *power_state,
    open_cfw_spotmgr_state_u32 *ton_state,
    open_cfw_spotmgr_state_u32 retained_mcu_mode,
    open_cfw_spotmgr_state_u32 collapse_profile)
{
    open_cfw_spotmgr_state_u32 descriptor = 0U;
    open_cfw_spotmgr_state_u32 power_descriptor;
    open_cfw_spotmgr_state_u32 ton_descriptor;
    open_cfw_spotmgr_state_u32 cpu_mode;
    open_cfw_spotmgr_state_u32 periph;
    open_cfw_spotmgr_state_u32 gpu_mode;
    open_cfw_spotmgr_state_u32 gpu_sdio;

    descriptor = open_cfw_spotmgr_insert_field(
        descriptor, status->temperature_range, 8U);
    if (status->cpu_state == 1U) {
        cpu_mode = 1U;
    } else if (status->cpu_state == 0U) {
        cpu_mode = 0U;
    } else {
        cpu_mode = ((retained_mcu_mode & 3U) == 2U) ? 1U : 0U;
    }
    descriptor = open_cfw_spotmgr_insert_field(descriptor, cpu_mode, 0U);

    periph = ((status->device_power << 2) != 0U) ||
             ((status->audio_power & 0x4C4U) != 0U);
    descriptor = open_cfw_spotmgr_insert_field(
        descriptor,
        (status->gpu_state == 1U) || (status->gpu_state == 2U) || periph,
        4U);
    gpu_mode = status->gpu_state == 2U ? 2U :
               (status->gpu_state == 1U ? 1U : 0U);
    descriptor = open_cfw_spotmgr_insert_field(descriptor, gpu_mode, 12U);
    descriptor = open_cfw_spotmgr_insert_field(descriptor, periph, 16U);
    gpu_sdio = (status->gpu_state == 1U) || (status->gpu_state == 2U) ||
               ((status->device_power & 0x00C00000U) != 0U);
    descriptor = open_cfw_spotmgr_insert_field(descriptor, gpu_sdio, 20U);

    power_descriptor = descriptor & 0x00F00FFFU;
    switch (power_descriptor) {
    case 0x000300U: *power_state = collapse_profile ? 4U : 0U; break;
    case 0x000200U: *power_state = collapse_profile ? 5U : 1U; break;
    case 0x000100U: *power_state = collapse_profile ? 6U : 2U; break;
    case 0x000000U: *power_state = collapse_profile ? 7U : 3U; break;
    case 0x000310U: *power_state = 4U; break;
    case 0x000210U: *power_state = 5U; break;
    case 0x000110U: *power_state = 6U; break;
    case 0x000010U: *power_state = 7U; break;
    case 0x000301U: *power_state = collapse_profile ? 12U : 8U; break;
    case 0x000201U: *power_state = collapse_profile ? 13U : 9U; break;
    case 0x000101U: *power_state = collapse_profile ? 14U : 10U; break;
    case 0x000001U: *power_state = collapse_profile ? 15U : 11U; break;
    case 0x000311U:
    case 0x100311U: *power_state = 12U; break;
    case 0x000211U:
    case 0x100211U: *power_state = 13U; break;
    case 0x000111U:
    case 0x100111U: *power_state = 14U; break;
    case 0x000011U:
    case 0x100011U: *power_state = 15U; break;
    case 0x100310U: *power_state = 16U; break;
    case 0x100210U: *power_state = 17U; break;
    case 0x100110U: *power_state = 18U; break;
    case 0x100010U: *power_state = 19U; break;
    default: return 5U;
    }

    ton_descriptor = descriptor & 0x000FF00FU;
    switch (ton_descriptor) {
    case 0x00000U: *ton_state = 0U; break;
    case 0x00001U: *ton_state = collapse_profile ? 7U : 1U; break;
    case 0x01000U:
    case 0x11000U: *ton_state = 2U; break;
    case 0x02000U:
    case 0x12000U: *ton_state = 3U; break;
    case 0x01001U:
    case 0x11001U: *ton_state = 4U; break;
    case 0x02001U:
    case 0x12001U: *ton_state = 5U; break;
    case 0x10000U: *ton_state = 6U; break;
    case 0x10001U: *ton_state = 7U; break;
    default: return 5U;
    }
    return 0U;
}

#endif

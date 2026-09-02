/* SPDX-License-Identifier: MIT */
typedef __UINT8_TYPE__ open_cfw_channel_u8;
typedef __UINT32_TYPE__ open_cfw_channel_u32;
#define OPEN_CFW_CHANNEL_MAGIC 0x01AFAFAFU

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_channel_u32 open_cfw_bootloader_hw_channel_config_42eaf6(
    open_cfw_channel_u32 *handle, open_cfw_channel_u32 index,
    const open_cfw_channel_u8 *config)
{
    __asm volatile(
        "movs r3, r0\nldr r3, [r3, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\nldr.w r3, [pc, #1652]\n"
        "cmp r0, r3\nbeq 2f\n1:\nmovs r0, #2\nb 6f\n"
        "2:\ncmp r1, #8\nblo 3f\nmovs r0, #5\nb 6f\n"
        "3:\nldr r0, [r2, #4]\ncmp r0, #32\nblo 4f\n"
        "ldr r0, [r2, #4]\ncmp r0, #64\nblo 5f\n"
        "4:\nmovs r0, #6\nb 6f\n"
        "5:\nmovs r3, #0\nldrb r0, [r2]\nlsls r0, r0, #24\n"
        "ands r0, r0, #0x7000000\norrs r3, r0\nldr r0, [r2, #4]\n"
        "lsls r0, r0, #18\nands r0, r0, #0xfc0000\norrs r3, r0\n"
        "ldrb r0, [r2, #8]\nlsls r0, r0, #16\nands r0, r0, #0x30000\n"
        "orrs r3, r0\nldrb r0, [r2, #9]\nlsls r0, r0, #8\n"
        "ands r0, r0, #0xf00\norrs r3, r0\nldrb r0, [r2, #10]\n"
        "orrs.w r3, r3, r0, lsl #1\nldrb r0, [r2, #11]\norrs r3, r0\n"
        "ldr.w r0, [pc, #1572]\nadds.w r0, r0, r1, lsl #2\nstr r3, [r0]\n"
        "ldr.w r0, [pc, #1516]\nldr r1, [r0]\nadds r1, r1, #1\nstr r1, [r0]\n"
        "movs r0, #0\n6:\nbx lr\n"
    );
}
#else
typedef struct open_cfw_channel_handle { open_cfw_channel_u32 word0, word1; }
    open_cfw_channel_handle;
typedef struct open_cfw_channel_config {
    open_cfw_channel_u8 byte0, pad1, pad2, pad3;
    open_cfw_channel_u32 word4;
    open_cfw_channel_u8 byte8, byte9, byte10, byte11;
} open_cfw_channel_config;
typedef struct open_cfw_channel_registers {
    open_cfw_channel_u32 channel[8];
    open_cfw_channel_u32 update_count;
} open_cfw_channel_registers;

__attribute__((used, noinline, visibility("default")))
open_cfw_channel_u32 open_cfw_bootloader_hw_channel_config_42eaf6_portable(
    const open_cfw_channel_handle *handle, open_cfw_channel_u32 index,
    const open_cfw_channel_config *config, open_cfw_channel_registers *registers)
{
    open_cfw_channel_u32 packed;
    if (handle == (const open_cfw_channel_handle *)0 ||
        (handle->word0 & ~0xFE000000U) != OPEN_CFW_CHANNEL_MAGIC) return 2U;
    if (index >= 8U) return 5U;
    if (config->word4 < 32U || config->word4 >= 64U) return 6U;
    packed = (((open_cfw_channel_u32)config->byte0 & 7U) << 24) |
             ((config->word4 & 63U) << 18) |
             (((open_cfw_channel_u32)config->byte8 & 3U) << 16) |
             (((open_cfw_channel_u32)config->byte9 & 15U) << 8) |
             ((open_cfw_channel_u32)config->byte10 << 1) |
             config->byte11;
    registers->channel[index] = packed;
    registers->update_count += 1U;
    return 0U;
}
#endif

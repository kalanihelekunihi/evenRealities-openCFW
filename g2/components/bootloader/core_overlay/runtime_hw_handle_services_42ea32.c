/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room hardware-handle services authenticated at G2
 * bootloader addresses 0x0042EA32, 0x0042EB74, 0x0042EBAA, and 0x0042EBE2.
 */

typedef __UINT8_TYPE__ open_cfw_hw_u8;
typedef __UINT32_TYPE__ open_cfw_hw_u32;

#define OPEN_CFW_HW_HANDLE_MAGIC 0x01AFAFAFU

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_reset_42ea32(open_cfw_hw_u32 *handle)
{
    __asm volatile(
        "movs r1, r0\nmovs r0, #0\nmovs r2, r1\ncmp r1, #0\nbeq 1f\n"
        "ldr r1, [r1]\nbic r1, r1, #0xfe000000\n"
        "ldr.w r3, [pc, #1848]\ncmp r1, r3\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 3f\n"
        "2:\nmovs r1, r2\nldr r3, [r1]\nbics r3, r3, #0x1000000\n"
        "str r3, [r1]\nmovs r1, r2\nldr r3, [r1]\n"
        "ands r3, r3, #0xff000000\nstr r3, [r1]\nmovs r1, #0\nstr r1, [r2, #4]\n"
        "3:\nbx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_configure_42eb74(
    open_cfw_hw_u32 *handle, const open_cfw_hw_u8 *config)
{
    __asm volatile(
        "movs r2, #0\nldr r3, [r0, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\n"
        "ldr.w r3, [pc, #1528]\ncmp r0, r3\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 3f\n"
        "2:\nldrb r0, [r1, #1]\nlsls r0, r0, #16\nands r0, r0, #0x70000\n"
        "orrs r2, r0\nldr r0, [r1, #4]\nlsls r0, r0, #22\nlsrs r0, r0, #22\n"
        "orrs r2, r0\nldr.w r0, [pc, #1508]\nstr r2, [r0]\nmovs r0, #0\n"
        "3:\nbx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_enable_42ebaa(open_cfw_hw_u32 *handle)
{
    __asm volatile(
        "movs r1, r0\nldr r1, [r1, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\n"
        "ldr.w r1, [pc, #1472]\ncmp r0, r1\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 4f\n"
        "2:\nldr.w r0, [pc, #1464]\nldr r0, [r0]\nlsls r0, r0, #31\n"
        "bpl 3f\nldr.w r0, [pc, #1464]\nldr r1, [r0]\n"
        "orrs r1, r1, #0x80000000\nstr r1, [r0]\nmovs r0, #0\nb 4f\n"
        "3:\nmovs r0, #7\n4:\nbx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_disable_42ebe2(open_cfw_hw_u32 *handle)
{
    __asm volatile(
        "movs r1, r0\nldr r1, [r1, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\n"
        "ldr.w r1, [pc, #1416]\ncmp r0, r1\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 3f\n"
        "2:\nldr.w r0, [pc, #1416]\nldr r1, [r0]\n"
        "bic r1, r1, #0x80000000\nstr r1, [r0]\nmovs r0, #0\n"
        "3:\nbx lr\n"
    );
}

#else

typedef struct open_cfw_hw_handle {
    open_cfw_hw_u32 word0;
    open_cfw_hw_u32 word1;
} open_cfw_hw_handle;

typedef struct open_cfw_hw_config {
    open_cfw_hw_u8 byte0;
    open_cfw_hw_u8 byte1;
    open_cfw_hw_u8 padding[2];
    open_cfw_hw_u32 word4;
} open_cfw_hw_config;

typedef struct open_cfw_hw_registers {
    open_cfw_hw_u32 status;
    open_cfw_hw_u32 command;
    open_cfw_hw_u32 configuration;
} open_cfw_hw_registers;

static open_cfw_hw_u32 open_cfw_hw_valid(const open_cfw_hw_handle *handle)
{
    return handle != (const open_cfw_hw_handle *)0 &&
           (handle->word0 & ~0xFE000000U) == OPEN_CFW_HW_HANDLE_MAGIC;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_reset_42ea32_portable(
    open_cfw_hw_handle *handle)
{
    if (open_cfw_hw_valid(handle) == 0U) return 2U;
    handle->word0 = (handle->word0 & ~0x01000000U) & 0xFF000000U;
    handle->word1 = 0U;
    return 0U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_configure_42eb74_portable(
    open_cfw_hw_handle *handle, const open_cfw_hw_config *config,
    open_cfw_hw_registers *registers)
{
    if (open_cfw_hw_valid(handle) == 0U) return 2U;
    registers->configuration = (((open_cfw_hw_u32)config->byte1 & 7U) << 16) |
                               (config->word4 & 0x3FFU);
    return 0U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_enable_42ebaa_portable(
    open_cfw_hw_handle *handle, open_cfw_hw_registers *registers)
{
    if (open_cfw_hw_valid(handle) == 0U) return 2U;
    if ((registers->status & 1U) == 0U) return 7U;
    registers->command |= 0x80000000U;
    return 0U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_hw_u32 open_cfw_bootloader_hw_handle_disable_42ebe2_portable(
    open_cfw_hw_handle *handle, open_cfw_hw_registers *registers)
{
    if (open_cfw_hw_valid(handle) == 0U) return 2U;
    registers->command &= ~0x80000000U;
    return 0U;
}

#endif

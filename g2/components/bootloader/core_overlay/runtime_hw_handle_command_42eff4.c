/* SPDX-License-Identifier: MIT */

typedef __UINT32_TYPE__ open_cfw_command_u32;

#define OPEN_CFW_COMMAND_HANDLE_MAGIC 0x01AFAFAFU

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_command_u32 open_cfw_bootloader_hw_handle_command_42eff4(
    open_cfw_command_u32 *handle)
{
    __asm volatile(
        "ldr r1, [r0, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\n"
        "ldr r1, [pc, #376]\ncmp r0, r1\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 3f\n"
        "2:\nmovs r0, #55\nldr r1, [pc, #436]\nstr r0, [r1]\nmovs r0, #0\n"
        "3:\nbx lr\n"
    );
}
#else
typedef struct open_cfw_command_handle {
    open_cfw_command_u32 word0;
    open_cfw_command_u32 word1;
} open_cfw_command_handle;

__attribute__((used, noinline, visibility("default")))
open_cfw_command_u32 open_cfw_bootloader_hw_handle_command_42eff4_portable(
    const open_cfw_command_handle *handle, open_cfw_command_u32 *command)
{
    if (handle == (const open_cfw_command_handle *)0 ||
        (handle->word0 & ~0xFE000000U) != OPEN_CFW_COMMAND_HANDLE_MAGIC) {
        return 2U;
    }
    *command = 55U;
    return 0U;
}
#endif

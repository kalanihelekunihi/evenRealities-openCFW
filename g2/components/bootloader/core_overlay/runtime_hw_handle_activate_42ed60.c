/* SPDX-License-Identifier: MIT */
typedef __UINT32_TYPE__ open_cfw_activate_u32;
#define OPEN_CFW_ACTIVATE_MAGIC 0x01AFAFAFU

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline, naked, visibility("default")))
open_cfw_activate_u32 open_cfw_bootloader_hw_handle_activate_42ed60(
    open_cfw_activate_u32 *handle)
{
    __asm volatile(
        "movs r1, r0\nldr r2, [r1, #4]\ncmp r0, #0\nbeq 1f\n"
        "ldr r0, [r0]\nbic r0, r0, #0xfe000000\n"
        "ldr.w r2, [pc, #1036]\ncmp r0, r2\nbeq 2f\n"
        "1:\nmovs r0, #2\nb 4f\n"
        "2:\nldr r0, [r1]\nubfx r0, r0, #25, #1\ncmp r0, #0\nbeq 3f\n"
        "movs r0, #0\nb 4f\n"
        "3:\nldr.w r0, [pc, #1012]\nldr r2, [r0]\norrs r2, r2, #1\n"
        "str r2, [r0]\nldr r0, [r1]\norrs r0, r0, #0x2000000\n"
        "str r0, [r1]\nmovs r0, #0\n4:\nbx lr\n"
    );
}
#else
typedef struct open_cfw_activate_handle { open_cfw_activate_u32 word0, word1; }
    open_cfw_activate_handle;
__attribute__((used, noinline, visibility("default")))
open_cfw_activate_u32 open_cfw_bootloader_hw_handle_activate_42ed60_portable(
    open_cfw_activate_handle *handle, open_cfw_activate_u32 *control)
{
    if (handle == (open_cfw_activate_handle *)0 ||
        (handle->word0 & ~0xFE000000U) != OPEN_CFW_ACTIVATE_MAGIC) return 2U;
    if ((handle->word0 & 0x02000000U) == 0U) {
        *control |= 1U;
        handle->word0 |= 0x02000000U;
    }
    return 0U;
}
#endif

/* SPDX-License-Identifier: MIT */
/* Clean-room overlap-safe byte move for the authenticated G2 ABI. */

typedef __SIZE_TYPE__ open_cfw_move_size;
typedef __UINTPTR_TYPE__ open_cfw_move_uintptr;
typedef __UINT8_TYPE__ open_cfw_move_u8;

__attribute__((used, noinline))
void *
open_cfw_bootloader_memmove_4276bc(void *destination, const void *source,
                                   open_cfw_move_size byte_count)
{
    open_cfw_move_u8 *dst = (open_cfw_move_u8 *)destination;
    const open_cfw_move_u8 *src = (const open_cfw_move_u8 *)source;
    open_cfw_move_uintptr dst_address = (open_cfw_move_uintptr)destination;
    open_cfw_move_uintptr src_address = (open_cfw_move_uintptr)source;

    if (src_address < dst_address &&
        dst_address < src_address + (open_cfw_move_uintptr)byte_count) {
        while (byte_count != 0U) {
            --byte_count;
            dst[byte_count] = src[byte_count];
        }
    } else {
        open_cfw_move_size index;

        for (index = 0U; index < byte_count; ++index) {
            dst[index] = src[index];
        }
    }

    return destination;
}

/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader's conventional memset ABI
 * wrapper at 0x00426C10.  The linked Arm EABI byte-fill provider accepts the
 * count before the fill value, while this entry preserves the standard
 * destination/value/count argument order and returns the destination.
 */

typedef __SIZE_TYPE__ open_cfw_bootloader_memset_wrapper_size;

extern void open_cfw_bootloader_retained_memset_41560c(
    void *destination,
    open_cfw_bootloader_memset_wrapper_size count,
    int value
);

__attribute__((used, noinline))
void *open_cfw_bootloader_memset_wrapper_426c10(
    void *destination,
    int value,
    open_cfw_bootloader_memset_wrapper_size count
)
{
    open_cfw_bootloader_retained_memset_41560c(destination, count, value);
    return destination;
}

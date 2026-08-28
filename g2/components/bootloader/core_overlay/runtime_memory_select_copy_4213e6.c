/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader mapped-memory copy service. */

typedef __UINT8_TYPE__ open_cfw_memory_select_u8;
typedef __UINT32_TYPE__ open_cfw_memory_select_u32;
typedef __UINTPTR_TYPE__ open_cfw_memory_select_word;

enum {
    OPEN_CFW_MEMORY_SELECT_CONTROL = 0x400201BCU,
    OPEN_CFW_MEMORY_SELECT_SECURITY = 0x40021008U,
    OPEN_CFW_MEMORY_SELECT_BASE_ZERO = 0x42000000U,
    OPEN_CFW_MEMORY_SELECT_BASE_ONE = 0x42002000U,
    OPEN_CFW_MEMORY_SELECT_BASE_TWO = 0x42004000U,
    OPEN_CFW_MEMORY_SELECT_BASE_THREE = 0x42006000U,
    OPEN_CFW_MEMORY_SELECT_BAD_SIZE = 5,
    OPEN_CFW_MEMORY_SELECT_BAD_ARGUMENT = 6,
    OPEN_CFW_MEMORY_SELECT_UNAVAILABLE = 9
};

open_cfw_memory_select_u32 open_cfw_bootloader_address_identity_4213d8(
    open_cfw_memory_select_u32 value);
open_cfw_memory_select_u32 open_cfw_bootloader_address_map_4213da(
    open_cfw_memory_select_u32 value);
void open_cfw_bootloader_copy_41d28a(
    const void *source, void *destination, open_cfw_memory_select_u32 size);

#ifdef OPEN_CFW_MEMORY_SELECT_HOST
open_cfw_memory_select_u32 open_cfw_memory_select_host_read(
    open_cfw_memory_select_u32 address);
#define OPEN_CFW_MEMORY_SELECT_READ(address) \
    open_cfw_memory_select_host_read(address)
#else
#define OPEN_CFW_MEMORY_SELECT_READ(address) \
    (*(volatile const open_cfw_memory_select_u32 *) \
        (open_cfw_memory_select_word)(address))
#endif

__attribute__((used, noinline))
open_cfw_memory_select_u32 open_cfw_bootloader_memory_select_copy_4213e6(
    open_cfw_memory_select_u32 kind_value,
    open_cfw_memory_select_u32 offset,
    open_cfw_memory_select_u32 size,
    void *destination)
{
    open_cfw_memory_select_u32 control =
        OPEN_CFW_MEMORY_SELECT_READ(OPEN_CFW_MEMORY_SELECT_CONTROL);
    open_cfw_memory_select_u32 security =
        OPEN_CFW_MEMORY_SELECT_READ(OPEN_CFW_MEMORY_SELECT_SECURITY);
    open_cfw_memory_select_u32 compact_zero = (control >> 4) & 1U;
    open_cfw_memory_select_u32 compact_one = (control >> 3) & 1U;
    open_cfw_memory_select_u32 external_available = (security >> 27) & 1U;
    open_cfw_memory_select_u32 capacity;
    open_cfw_memory_select_u32 source;
    open_cfw_memory_select_u8 kind = (open_cfw_memory_select_u8)kind_value;

    if (destination == (void *)0) {
        return OPEN_CFW_MEMORY_SELECT_BAD_ARGUMENT;
    }

    switch (kind) {
    case 0:
        capacity = compact_zero ? 0x40U : 0x200U;
        break;
    case 1:
        capacity = compact_one ? 0x2C0U : 0x600U;
        break;
    case 2:
        capacity = 0x40U;
        break;
    case 3:
        capacity = 0x2C0U;
        break;
    case 4:
        capacity = 0x200U;
        break;
    case 5:
        capacity = 0x600U;
        break;
    default:
        return OPEN_CFW_MEMORY_SELECT_BAD_ARGUMENT;
    }
    if (offset + size > capacity) {
        return OPEN_CFW_MEMORY_SELECT_BAD_SIZE;
    }

    switch (kind) {
    case 0:
        if (compact_zero != 0U) {
            if (external_available == 0U) {
                return OPEN_CFW_MEMORY_SELECT_UNAVAILABLE;
            }
            source = OPEN_CFW_MEMORY_SELECT_BASE_TWO + (offset << 2);
        } else {
            source = OPEN_CFW_MEMORY_SELECT_BASE_ZERO
                + (open_cfw_bootloader_address_identity_4213d8(offset) << 2);
        }
        break;
    case 1:
        if (compact_one != 0U) {
            if (external_available == 0U) {
                return OPEN_CFW_MEMORY_SELECT_UNAVAILABLE;
            }
            source = OPEN_CFW_MEMORY_SELECT_BASE_THREE + (offset << 2);
        } else {
            source = OPEN_CFW_MEMORY_SELECT_BASE_ONE
                + (open_cfw_bootloader_address_map_4213da(offset) << 2);
        }
        break;
    case 2:
        if (external_available == 0U) {
            return OPEN_CFW_MEMORY_SELECT_UNAVAILABLE;
        }
        source = OPEN_CFW_MEMORY_SELECT_BASE_TWO + (offset << 2);
        break;
    case 3:
        if (external_available == 0U) {
            return OPEN_CFW_MEMORY_SELECT_UNAVAILABLE;
        }
        source = OPEN_CFW_MEMORY_SELECT_BASE_THREE + (offset << 2);
        break;
    case 4:
        source = OPEN_CFW_MEMORY_SELECT_BASE_ZERO + (offset << 2);
        break;
    default:
        source = OPEN_CFW_MEMORY_SELECT_BASE_ONE + (offset << 2);
        break;
    }

    open_cfw_bootloader_copy_41d28a(
        (const void *)(open_cfw_memory_select_word)source,
        destination,
        size);
    return 0;
}

__attribute__((used, noinline))
open_cfw_memory_select_u32 open_cfw_bootloader_memory_select_odd_421548(
    open_cfw_memory_select_u32 kind,
    open_cfw_memory_select_u32 offset,
    open_cfw_memory_select_u32 size,
    void *destination)
{
    open_cfw_memory_select_u8 narrowed = (open_cfw_memory_select_u8)kind;
    if (narrowed != 1U && narrowed != 3U && narrowed != 5U) {
        return OPEN_CFW_MEMORY_SELECT_BAD_ARGUMENT;
    }
    return open_cfw_bootloader_memory_select_copy_4213e6(
        narrowed, offset, size, destination);
}

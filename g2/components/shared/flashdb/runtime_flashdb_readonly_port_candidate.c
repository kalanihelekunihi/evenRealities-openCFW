/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-excluded G2 FlashDB 2.1.1 read-only FAL port candidate.
 *
 * The record layouts and read dispatch follow the authenticated FlashDB/FAL
 * 2.1.1 source and the statically recovered G2 2.2.6.10 configuration.  The
 * released zero-on-transport-error behavior is deliberately corrected to a
 * negative FAL error.  No database initializer, mount, format, default-reset,
 * program, or erase path exists in this translation unit.
 */

#include "runtime_flashdb_readonly_port_candidate.h"

#define OPEN_CFW_FLASHDB_READONLY_BUILD 1

#if OPEN_CFW_FLASHDB_READONLY_BUILD != 1
#error "the FlashDB candidate must remain a read-only build"
#endif

#ifdef OPEN_CFW_FLASHDB_ENABLE_MUTATION
#error "the FlashDB read-only candidate has no mutation-capable build mode"
#endif

typedef open_cfw_flashdb_i32 (*open_cfw_flashdb_mx25_read_function)(
    open_cfw_flashdb_u32,
    open_cfw_flashdb_u8 *,
    open_cfw_flashdb_u32
);
typedef open_cfw_flashdb_i32 (*open_cfw_flashdb_cmsis_mutex_acquire_function)(
    void *,
    open_cfw_flashdb_u32
);
typedef open_cfw_flashdb_i32 (*open_cfw_flashdb_cmsis_mutex_release_function)(
    void *
);

#ifndef OPEN_CFW_FLASHDB_READONLY_MX25_READ
#define OPEN_CFW_FLASHDB_READONLY_MX25_READ(offset, buffer, size) \
    (((open_cfw_flashdb_mx25_read_function)(open_cfw_flashdb_uintptr) \
        OPEN_CFW_FLASHDB_MX25_READ_ENTRY)((offset), (buffer), (size)))
#endif

#ifndef OPEN_CFW_FLASHDB_READONLY_MUTEX_ID
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_ID() \
    (*(void * volatile *)(open_cfw_flashdb_uintptr) \
        OPEN_CFW_FLASHDB_SHARED_MUTEX_SLOT)
#endif

#ifndef OPEN_CFW_FLASHDB_READONLY_MUTEX_ACQUIRE
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_ACQUIRE(mutex, timeout) \
    (((open_cfw_flashdb_cmsis_mutex_acquire_function) \
        (open_cfw_flashdb_uintptr) \
        OPEN_CFW_FLASHDB_CMSIS_MUTEX_ACQUIRE_ENTRY)((mutex), (timeout)))
#endif

#ifndef OPEN_CFW_FLASHDB_READONLY_MUTEX_RELEASE
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_RELEASE(mutex) \
    (((open_cfw_flashdb_cmsis_mutex_release_function) \
        (open_cfw_flashdb_uintptr) \
        OPEN_CFW_FLASHDB_CMSIS_MUTEX_RELEASE_ENTRY)((mutex)))
#endif

__attribute__((used))
const struct open_cfw_flashdb_fal_flash_dev_abi32
open_cfw_flashdb_readonly_stock_norflash_abi = {
    "norflash",
    OPEN_CFW_FLASHDB_NORFLASH_ADDRESS,
    OPEN_CFW_FLASHDB_NORFLASH_LENGTH,
    OPEN_CFW_FLASHDB_NORFLASH_BLOCK_SIZE,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_INIT_ENTRY,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_READ_ENTRY,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_WRITE_ENTRY,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_ERASE_ENTRY,
    OPEN_CFW_FLASHDB_NORFLASH_WRITE_GRAN_BITS
};

__attribute__((used))
const struct open_cfw_flashdb_fal_partition_abi32
open_cfw_flashdb_readonly_partitions[OPEN_CFW_FLASHDB_PARTITION_COUNT] = {
    {
        OPEN_CFW_FLASHDB_FAL_MAGIC,
        "kvdb",
        "norflash",
        OPEN_CFW_FLASHDB_KVDB_OFFSET,
        OPEN_CFW_FLASHDB_KVDB_LENGTH,
        0U
    },
    {
        OPEN_CFW_FLASHDB_FAL_MAGIC,
        "NVdb",
        "norflash",
        OPEN_CFW_FLASHDB_NVDB_OFFSET,
        OPEN_CFW_FLASHDB_NVDB_LENGTH,
        0U
    }
};

static open_cfw_flashdb_i32 open_cfw_flashdb_readonly_partition_is_known(
    const struct open_cfw_flashdb_fal_partition_abi32 *partition
)
{
    return (
        partition == &open_cfw_flashdb_readonly_partitions[
            OPEN_CFW_FLASHDB_PARTITION_KVDB
        ] ||
        partition == &open_cfw_flashdb_readonly_partitions[
            OPEN_CFW_FLASHDB_PARTITION_NVDB
        ]
    );
}

__attribute__((used, noinline))
const struct open_cfw_flashdb_fal_partition_abi32 *
open_cfw_flashdb_readonly_partition(open_cfw_flashdb_u32 index)
{
    if (index >= OPEN_CFW_FLASHDB_PARTITION_COUNT) {
        return (const struct open_cfw_flashdb_fal_partition_abi32 *)0;
    }
    return &open_cfw_flashdb_readonly_partitions[index];
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_mutex_lock(void)
{
    void *mutex = OPEN_CFW_FLASHDB_READONLY_MUTEX_ID();

    if (mutex == (void *)0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    if (
        OPEN_CFW_FLASHDB_READONLY_MUTEX_ACQUIRE(
            mutex,
            OPEN_CFW_FLASHDB_CMSIS_WAIT_FOREVER
        ) != 0
    ) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    return 0;
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_mutex_unlock(void)
{
    void *mutex = OPEN_CFW_FLASHDB_READONLY_MUTEX_ID();

    if (mutex == (void *)0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    if (OPEN_CFW_FLASHDB_READONLY_MUTEX_RELEASE(mutex) != 0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    return 0;
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_read(
    open_cfw_flashdb_u32 offset,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
)
{
    if (buffer == (open_cfw_flashdb_u8 *)0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    if (
        offset < OPEN_CFW_FLASHDB_NORFLASH_ADDRESS ||
        offset > OPEN_CFW_FLASHDB_NORFLASH_LENGTH ||
        size > OPEN_CFW_FLASHDB_NORFLASH_LENGTH - offset
    ) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    if (size == 0U) {
        return 0;
    }

    /* The recovered MX25 seam returns zero only after a complete transfer. */
    if (OPEN_CFW_FLASHDB_READONLY_MX25_READ(offset, buffer, size) != 0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    return (open_cfw_flashdb_i32)size;
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_partition_read_unlocked(
    const struct open_cfw_flashdb_fal_partition_abi32 *partition,
    open_cfw_flashdb_u32 address,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
)
{
    if (
        open_cfw_flashdb_readonly_partition_is_known(partition) == 0 ||
        buffer == (open_cfw_flashdb_u8 *)0
    ) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }

    /* Subtraction form closes the unsigned-wrap bug in upstream's sum test. */
    if (address > partition->length || size > partition->length - address) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }

    return open_cfw_flashdb_readonly_norflash_read(
        partition->offset + address,
        buffer,
        size
    );
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_partition_read(
    const struct open_cfw_flashdb_fal_partition_abi32 *partition,
    open_cfw_flashdb_u32 address,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
)
{
    open_cfw_flashdb_i32 result;

    if (
        open_cfw_flashdb_readonly_partition_is_known(partition) == 0 ||
        buffer == (open_cfw_flashdb_u8 *)0 ||
        address > partition->length ||
        size > partition->length - address
    ) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    if (size == 0U) {
        return 0;
    }
    if (open_cfw_flashdb_readonly_mutex_lock() < 0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }

    result = open_cfw_flashdb_readonly_partition_read_unlocked(
        partition,
        address,
        buffer,
        size
    );
    if (open_cfw_flashdb_readonly_mutex_unlock() < 0) {
        return OPEN_CFW_FLASHDB_FAL_ERROR;
    }
    return result;
}

/*
 * Compile-time fail-closed mutation callbacks.  There is deliberately no
 * program/erase transport type, declaration, macro, address, or dispatch.
 */
__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_write_denied(
    open_cfw_flashdb_u32 offset,
    const open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
)
{
    (void)offset;
    (void)buffer;
    (void)size;
    return OPEN_CFW_FLASHDB_FAL_ERROR;
}

__attribute__((used, noinline))
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_erase_denied(
    open_cfw_flashdb_u32 offset,
    open_cfw_flashdb_u32 size
)
{
    (void)offset;
    (void)size;
    return OPEN_CFW_FLASHDB_FAL_ERROR;
}

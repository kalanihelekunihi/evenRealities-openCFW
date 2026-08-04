/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-excluded, read-only FlashDB/FAL port candidate for the G2.
 * This interface is intentionally absent from every production overlay and
 * manifest.  It cannot initialize or mount a database.
 */

#ifndef OPEN_CFW_RUNTIME_FLASHDB_READONLY_PORT_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FLASHDB_READONLY_PORT_CANDIDATE_H

typedef __UINT8_TYPE__ open_cfw_flashdb_u8;
typedef __UINT32_TYPE__ open_cfw_flashdb_u32;
typedef __INT32_TYPE__ open_cfw_flashdb_i32;
typedef __UINTPTR_TYPE__ open_cfw_flashdb_uintptr;

enum {
    OPEN_CFW_FLASHDB_FAL_MAGIC = 0x45503130U,
    OPEN_CFW_FLASHDB_FAL_NAME_MAX = 24U,
    OPEN_CFW_FLASHDB_PARTITION_COUNT = 2U,
    OPEN_CFW_FLASHDB_PARTITION_KVDB = 0U,
    OPEN_CFW_FLASHDB_PARTITION_NVDB = 1U,
    OPEN_CFW_FLASHDB_KVDB_OFFSET = 0x01FC0000U,
    OPEN_CFW_FLASHDB_KVDB_LENGTH = 0x00038000U,
    OPEN_CFW_FLASHDB_NVDB_OFFSET = 0x01FF8000U,
    OPEN_CFW_FLASHDB_NVDB_LENGTH = 0x00008000U,
    OPEN_CFW_FLASHDB_NORFLASH_ADDRESS = 0x01FC0000U,
    OPEN_CFW_FLASHDB_NORFLASH_LENGTH = 0x02000000U,
    OPEN_CFW_FLASHDB_NORFLASH_BLOCK_SIZE = 0x00001000U,
    OPEN_CFW_FLASHDB_NORFLASH_WRITE_GRAN_BITS = 1U,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_INIT_ENTRY = 0x00540ED1U,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_READ_ENTRY = 0x00540ED5U,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_WRITE_ENTRY = 0x00540F2DU,
    OPEN_CFW_FLASHDB_STOCK_NORFLASH_ERASE_ENTRY = 0x00540F85U,
    OPEN_CFW_FLASHDB_MX25_READ_ENTRY = 0x004709C9U,
    OPEN_CFW_FLASHDB_CMSIS_MUTEX_ACQUIRE_ENTRY = 0x004497B7U,
    OPEN_CFW_FLASHDB_CMSIS_MUTEX_RELEASE_ENTRY = 0x0044981DU,
    OPEN_CFW_FLASHDB_SHARED_MUTEX_SLOT = 0x20074944U,
    OPEN_CFW_FLASHDB_CMSIS_WAIT_FOREVER = 0xFFFFFFFFU,
    OPEN_CFW_FLASHDB_FAL_ERROR = -1
};

/*
 * Fixed-width representations of the released 32-bit FAL records.  Callback
 * entries are addresses, rather than host function pointers, so these layouts
 * remain exact and testable on both 32-bit target and 64-bit host builds.
 */
struct open_cfw_flashdb_fal_flash_dev_abi32 {
    char name[OPEN_CFW_FLASHDB_FAL_NAME_MAX];
    open_cfw_flashdb_u32 address;
    open_cfw_flashdb_u32 length;
    open_cfw_flashdb_u32 block_size;
    open_cfw_flashdb_u32 init_entry;
    open_cfw_flashdb_u32 read_entry;
    open_cfw_flashdb_u32 write_entry;
    open_cfw_flashdb_u32 erase_entry;
    open_cfw_flashdb_u32 write_granularity_bits;
};

struct open_cfw_flashdb_fal_partition_abi32 {
    open_cfw_flashdb_u32 magic_word;
    char name[OPEN_CFW_FLASHDB_FAL_NAME_MAX];
    char flash_name[OPEN_CFW_FLASHDB_FAL_NAME_MAX];
    open_cfw_flashdb_u32 offset;
    open_cfw_flashdb_u32 length;
    open_cfw_flashdb_u32 reserved;
};

_Static_assert(
    sizeof(struct open_cfw_flashdb_fal_flash_dev_abi32) == 0x38U,
    "G2 FAL flash-device ABI size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_flashdb_fal_flash_dev_abi32,
        read_entry
    ) == 0x28U,
    "G2 FAL read-callback slot changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_flashdb_fal_flash_dev_abi32,
        write_entry
    ) == 0x2CU,
    "G2 FAL write-callback slot changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_flashdb_fal_flash_dev_abi32,
        erase_entry
    ) == 0x30U,
    "G2 FAL erase-callback slot changed"
);
_Static_assert(
    sizeof(struct open_cfw_flashdb_fal_partition_abi32) == 0x40U,
    "G2 FAL partition ABI size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_flashdb_fal_partition_abi32,
        offset
    ) == 0x34U,
    "G2 FAL partition-offset slot changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_flashdb_fal_partition_abi32,
        length
    ) == 0x38U,
    "G2 FAL partition-length slot changed"
);

extern const struct open_cfw_flashdb_fal_flash_dev_abi32
    open_cfw_flashdb_readonly_stock_norflash_abi;
extern const struct open_cfw_flashdb_fal_partition_abi32
    open_cfw_flashdb_readonly_partitions[OPEN_CFW_FLASHDB_PARTITION_COUNT];

const struct open_cfw_flashdb_fal_partition_abi32 *
open_cfw_flashdb_readonly_partition(open_cfw_flashdb_u32 index);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_mutex_lock(void);
open_cfw_flashdb_i32 open_cfw_flashdb_readonly_mutex_unlock(void);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_read(
    open_cfw_flashdb_u32 offset,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_partition_read_unlocked(
    const struct open_cfw_flashdb_fal_partition_abi32 *partition,
    open_cfw_flashdb_u32 address,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_partition_read(
    const struct open_cfw_flashdb_fal_partition_abi32 *partition,
    open_cfw_flashdb_u32 address,
    open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_write_denied(
    open_cfw_flashdb_u32 offset,
    const open_cfw_flashdb_u8 *buffer,
    open_cfw_flashdb_u32 size
);

open_cfw_flashdb_i32 open_cfw_flashdb_readonly_norflash_erase_denied(
    open_cfw_flashdb_u32 offset,
    open_cfw_flashdb_u32 size
);

#endif /* OPEN_CFW_RUNTIME_FLASHDB_READONLY_PORT_CANDIDATE_H */

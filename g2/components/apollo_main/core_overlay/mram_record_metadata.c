/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database metadata accessors and writers matched
 * to the stock AppDb-style cluster at 0x0047B3AE...0x0047B4D3.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_metadata_uintptr;

typedef unsigned int (*open_cfw_mram_metadata_verify_function)(
    const unsigned char *
);
typedef unsigned int (*open_cfw_mram_metadata_connection_id_function)(
    void
);
typedef int (*open_cfw_mram_metadata_connection_active_function)(
    unsigned int
);

#define OPEN_CFW_MRAM_METADATA_RECORD_SIZE 200U
#define OPEN_CFW_MRAM_METADATA_RECORD_COUNT 10U

#define OPEN_CFW_MRAM_METADATA_PEER_ADDR_RES_OFFSET 0x31U
#define OPEN_CFW_MRAM_METADATA_CCC_TABLE_OFFSET 0x6CU
#define OPEN_CFW_MRAM_METADATA_PEER_SIGN_COUNTER_OFFSET 0x80U
#define OPEN_CFW_MRAM_METADATA_CHANGE_AWARE_OFFSET 0x84U
#define OPEN_CFW_MRAM_METADATA_CSF_OFFSET 0x85U
#define OPEN_CFW_MRAM_METADATA_CACHE_BY_HASH_OFFSET 0x86U
#define OPEN_CFW_MRAM_METADATA_PEER_DB_HASH_OFFSET 0x87U
#define OPEN_CFW_MRAM_METADATA_HANDLE_LIST_OFFSET 0x98U
#define OPEN_CFW_MRAM_METADATA_DISCOVERY_STATUS_OFFSET 0xC2U

#define OPEN_CFW_MRAM_METADATA_DB_HASH_SIZE 16U
#define OPEN_CFW_MRAM_METADATA_CSF_SIZE 1U
#define OPEN_CFW_MRAM_METADATA_HANDLE_LIST_SIZE 42U

#ifndef OPEN_CFW_MRAM_METADATA_UPDATE
#define OPEN_CFW_MRAM_METADATA_UPDATE(record) \
    open_cfw_mram_app_db_update(record)
#endif
#ifndef OPEN_CFW_MRAM_METADATA_VERIFY
#define OPEN_CFW_MRAM_METADATA_VERIFY(record) \
    (((open_cfw_mram_metadata_verify_function) \
        (open_cfw_mram_metadata_uintptr)0x0047B731U)(record))
#endif
#ifndef OPEN_CFW_MRAM_METADATA_CONNECTION_ID
#define OPEN_CFW_MRAM_METADATA_CONNECTION_ID() \
    (((open_cfw_mram_metadata_connection_id_function) \
        (open_cfw_mram_metadata_uintptr)0x004BB05BU)())
#endif
#ifndef OPEN_CFW_MRAM_METADATA_CONNECTION_ACTIVE
#define OPEN_CFW_MRAM_METADATA_CONNECTION_ACTIVE(connection_id) \
    (((open_cfw_mram_metadata_connection_active_function) \
        (open_cfw_mram_metadata_uintptr)0x004BAD27U)(connection_id))
#endif
#ifndef OPEN_CFW_MRAM_METADATA_RECORDS
#define OPEN_CFW_MRAM_METADATA_RECORDS \
    ((unsigned char *)(open_cfw_mram_metadata_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_METADATA_DEVICE_DB_HASH
#define OPEN_CFW_MRAM_METADATA_DEVICE_DB_HASH \
    ((unsigned char *)(open_cfw_mram_metadata_uintptr)0x20068215U)
#endif

unsigned int open_cfw_mram_app_db_update(
    const unsigned char *
);

static __attribute__((always_inline)) inline void
open_cfw_mram_metadata_copy(
    unsigned char *destination,
    const unsigned char *source,
    unsigned int size
)
{
    unsigned int index;

    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_metadata_store_halfword(
    unsigned char *destination,
    unsigned int value
)
{
    destination[0] = (unsigned char)value;
    destination[1] = (unsigned char)(value >> 8U);
}

static __attribute__((always_inline)) inline void
open_cfw_mram_metadata_store_word(
    unsigned char *destination,
    unsigned int value
)
{
    destination[0] = (unsigned char)value;
    destination[1] = (unsigned char)(value >> 8U);
    destination[2] = (unsigned char)(value >> 16U);
    destination[3] = (unsigned char)(value >> 24U);
}

static __attribute__((always_inline)) inline void
open_cfw_mram_metadata_persist(unsigned char *record)
{
    (void)OPEN_CFW_MRAM_METADATA_UPDATE(record);
    (void)OPEN_CFW_MRAM_METADATA_VERIFY(record);
}

__attribute__((used, noinline))
void open_cfw_mram_set_peer_db_hash(
    unsigned char *record,
    const unsigned char *peer_db_hash
)
{
    open_cfw_mram_metadata_copy(
        record + OPEN_CFW_MRAM_METADATA_PEER_DB_HASH_OFFSET,
        peer_db_hash,
        OPEN_CFW_MRAM_METADATA_DB_HASH_SIZE
    );
    open_cfw_mram_metadata_persist(record);
}

__attribute__((used, noinline))
void open_cfw_mram_set_cache_by_hash(
    unsigned char *record,
    unsigned int cache_by_hash
)
{
    record[OPEN_CFW_MRAM_METADATA_CACHE_BY_HASH_OFFSET] =
        (unsigned char)cache_by_hash;
    open_cfw_mram_metadata_persist(record);
}

__attribute__((used, noinline))
void open_cfw_mram_set_ccc_table_value(
    unsigned char *record,
    unsigned int index,
    unsigned int value
)
{
    unsigned int bounded_index = (unsigned short)index;
    unsigned int connection_id;

    open_cfw_mram_metadata_store_halfword(
        record
            + OPEN_CFW_MRAM_METADATA_CCC_TABLE_OFFSET
            + bounded_index * 2U,
        value
    );
    connection_id =
        (unsigned char)OPEN_CFW_MRAM_METADATA_CONNECTION_ID();
    if (OPEN_CFW_MRAM_METADATA_CONNECTION_ACTIVE(connection_id) != 0) {
        open_cfw_mram_metadata_persist(record);
    }
}

__attribute__((used, noinline))
void open_cfw_mram_get_csf_record(
    unsigned char *record,
    unsigned char *change_aware_state,
    unsigned char **client_supported_features
)
{
    *change_aware_state =
        record[OPEN_CFW_MRAM_METADATA_CHANGE_AWARE_OFFSET];
    *client_supported_features =
        record + OPEN_CFW_MRAM_METADATA_CSF_OFFSET;
}

__attribute__((used, noinline))
void open_cfw_mram_set_csf_record(
    unsigned char *record,
    unsigned int change_aware_state,
    const unsigned char *client_supported_features
)
{
    if (
        client_supported_features != (const unsigned char *)0
        && record != (unsigned char *)0
    ) {
        record[OPEN_CFW_MRAM_METADATA_CHANGE_AWARE_OFFSET] =
            (unsigned char)change_aware_state;
        open_cfw_mram_metadata_copy(
            record + OPEN_CFW_MRAM_METADATA_CSF_OFFSET,
            client_supported_features,
            OPEN_CFW_MRAM_METADATA_CSF_SIZE
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_set_client_change_aware_state(
    unsigned char *record,
    unsigned int state
)
{
    if (record == (unsigned char *)0) {
        unsigned char *current = OPEN_CFW_MRAM_METADATA_RECORDS;
        unsigned int remaining = OPEN_CFW_MRAM_METADATA_RECORD_COUNT;

        while (remaining != 0U) {
            current[OPEN_CFW_MRAM_METADATA_CHANGE_AWARE_OFFSET] =
                (unsigned char)state;
            current += OPEN_CFW_MRAM_METADATA_RECORD_SIZE;
            --remaining;
        }
        return;
    }

    record[OPEN_CFW_MRAM_METADATA_CHANGE_AWARE_OFFSET] =
        (unsigned char)state;
}

__attribute__((used, noinline))
unsigned char *open_cfw_mram_get_device_db_hash(void)
{
    return OPEN_CFW_MRAM_METADATA_DEVICE_DB_HASH;
}

__attribute__((used, noinline))
void open_cfw_mram_set_device_db_hash(
    const unsigned char *device_db_hash
)
{
    if (device_db_hash != (const unsigned char *)0) {
        open_cfw_mram_metadata_copy(
            OPEN_CFW_MRAM_METADATA_DEVICE_DB_HASH,
            device_db_hash,
            OPEN_CFW_MRAM_METADATA_DB_HASH_SIZE
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_set_discovery_status(
    unsigned char *record,
    unsigned int status
)
{
    record[OPEN_CFW_MRAM_METADATA_DISCOVERY_STATUS_OFFSET] =
        (unsigned char)status;
}

__attribute__((used, noinline))
void open_cfw_mram_set_handle_list(
    unsigned char *record,
    const unsigned char *handle_list
)
{
    open_cfw_mram_metadata_copy(
        record + OPEN_CFW_MRAM_METADATA_HANDLE_LIST_OFFSET,
        handle_list,
        OPEN_CFW_MRAM_METADATA_HANDLE_LIST_SIZE
    );
    open_cfw_mram_metadata_persist(record);
}

__attribute__((used, noinline))
void open_cfw_mram_set_peer_sign_counter(
    unsigned char *record,
    unsigned int sign_counter
)
{
    open_cfw_mram_metadata_store_word(
        record + OPEN_CFW_MRAM_METADATA_PEER_SIGN_COUNTER_OFFSET,
        sign_counter
    );
}

__attribute__((used, noinline))
void open_cfw_mram_set_peer_address_resolution(
    unsigned char *record,
    unsigned int address_resolution
)
{
    record[OPEN_CFW_MRAM_METADATA_PEER_ADDR_RES_OFFSET] =
        (unsigned char)address_resolution;
}

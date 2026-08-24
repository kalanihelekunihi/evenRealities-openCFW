/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 factory-NV database lifecycle core.
 * The implementation deliberately defaults to a non-destructive schema
 * mismatch policy: factory defaults may be restored only by a build which
 * explicitly enables OPEN_CFW_NVDB_ALLOW_FACTORY_RESET after media validation.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

#ifndef OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS
#define OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS 0x20003868u
#endif
#ifndef OPEN_CFW_NVDB_SYSTEM_DATA_ADDRESS
#define OPEN_CFW_NVDB_SYSTEM_DATA_ADDRESS 0x20003994u
#endif
#ifndef OPEN_CFW_NVDB_MAGIC_KEY
#define OPEN_CFW_NVDB_MAGIC_KEY ((const char *)0x0078E5E4u)
#endif
#ifndef OPEN_CFW_NVDB_SYSTEM_KEY
#define OPEN_CFW_NVDB_SYSTEM_KEY ((const char *)0x0078E5ECu)
#endif
#ifndef OPEN_CFW_NVDB_FACTORY_NAME
#define OPEN_CFW_NVDB_FACTORY_NAME ((const char *)0x0078E60Cu)
#endif
#ifndef OPEN_CFW_NVDB_PARTITION_NAME
#define OPEN_CFW_NVDB_PARTITION_NAME ((const char *)0x0078E614u)
#endif
#ifndef OPEN_CFW_NVDB_ALLOW_FACTORY_RESET
#define OPEN_CFW_NVDB_ALLOW_FACTORY_RESET 0
#endif

#define OPEN_CFW_NVDB_DATABASE_INDEX 1u
#define OPEN_CFW_NVDB_MAGIC 0x55550022u
#define OPEN_CFW_NVDB_DEFAULT_COUNT 9u
#define OPEN_CFW_NVDB_OK 0
#define OPEN_CFW_NVDB_ERR_INIT 8
#define OPEN_CFW_NVDB_ERR_SCHEMA 9

#ifndef OPEN_CFW_NVDB_TYPES_DEFINED
#define OPEN_CFW_NVDB_TYPES_DEFINED 1
typedef struct {
    const char *key;
    const void *value;
    uint32_t value_length;
} open_cfw_nvdb_default_node;

typedef struct {
    const open_cfw_nvdb_default_node *nodes;
    uint32_t count;
} open_cfw_nvdb_defaults;
#endif

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(open_cfw_nvdb_default_node) == 12u,
    "G2 FlashDB default-node ABI changed");
_Static_assert(sizeof(open_cfw_nvdb_defaults) == 8u,
    "G2 FlashDB default-table ABI changed");
#endif

#ifndef OPEN_CFW_NVDB_DB_READ
int open_cfw_nvdb_db_read(uint32_t index, const char *key, void *value,
    uint16_t length);
#define OPEN_CFW_NVDB_DB_READ(index, key, value, length) \
    open_cfw_nvdb_db_read((index), (key), (value), (length))
#endif
#ifndef OPEN_CFW_NVDB_DB_WRITE
int open_cfw_nvdb_db_write(uint32_t index, const char *key,
    const void *value, uint16_t length);
#define OPEN_CFW_NVDB_DB_WRITE(index, key, value, length) \
    open_cfw_nvdb_db_write((index), (key), (value), (length))
#endif
#ifndef OPEN_CFW_NVDB_DB_GET
void *open_cfw_nvdb_db_get(uint32_t index);
#define OPEN_CFW_NVDB_DB_GET(index) open_cfw_nvdb_db_get((index))
#endif
#ifndef OPEN_CFW_NVDB_DB_CONTROL
int open_cfw_nvdb_db_control(void *database, uint32_t command, void *argument);
#define OPEN_CFW_NVDB_DB_CONTROL(database, command, argument) \
    open_cfw_nvdb_db_control((database), (command), (argument))
#endif
#ifndef OPEN_CFW_NVDB_DB_INIT
int open_cfw_nvdb_db_init(void *database, const char *name,
    const char *partition, const open_cfw_nvdb_defaults *defaults,
    void *user_data);
#define OPEN_CFW_NVDB_DB_INIT(database, name, partition, defaults, user_data) \
    open_cfw_nvdb_db_init((database), (name), (partition), (defaults), \
        (user_data))
#endif
#ifndef OPEN_CFW_NVDB_DB_SET_DEFAULT
int open_cfw_nvdb_db_set_default(void *database);
#define OPEN_CFW_NVDB_DB_SET_DEFAULT(database) \
    open_cfw_nvdb_db_set_default((database))
#endif
#ifndef OPEN_CFW_NVDB_LEGACY_PSN_SCAN
void open_cfw_nvdb_legacy_psn_scan(void);
#define OPEN_CFW_NVDB_LEGACY_PSN_SCAN() open_cfw_nvdb_legacy_psn_scan()
#endif
#ifndef OPEN_CFW_NVDB_OTP_PSN_READ
int open_cfw_nvdb_otp_psn_read(char *destination, uint32_t flags);
#define OPEN_CFW_NVDB_OTP_PSN_READ(destination, flags) \
    open_cfw_nvdb_otp_psn_read((destination), (flags))
#endif
#ifndef OPEN_CFW_NVDB_DIAGNOSTIC_MISSING
#define OPEN_CFW_NVDB_DIAGNOSTIC_MISSING(index, key) ((void)(index), (void)(key))
#endif
#ifndef OPEN_CFW_NVDB_DIAGNOSTIC_INIT
#define OPEN_CFW_NVDB_DIAGNOSTIC_INIT(result) ((void)(result))
#endif
#ifndef OPEN_CFW_NVDB_DIAGNOSTIC_MAGIC
#define OPEN_CFW_NVDB_DIAGNOSTIC_MAGIC(value, result) \
    ((void)(value), (void)(result))
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
static __attribute__((always_inline)) int open_cfw_nvdb_key_equal(
    const char *left, const char *right)
{
    if (left == NULL || right == NULL) {
        return 0;
    }
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

static __attribute__((always_inline)) void open_cfw_nvdb_copy_psn(
    volatile uint8_t *destination, const char *source)
{
    uint32_t index;
    for (index = 0u; index < 14u; ++index) {
        destination[index + 1u] = (uint8_t)source[index];
    }
    destination[15u] = 0u;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline))
int open_cfw_service_nvdb_read(const char *key, void *value, uint16_t length)
{
    return OPEN_CFW_NVDB_DB_READ(
        OPEN_CFW_NVDB_DATABASE_INDEX, key, value, length);
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used, noinline))
int open_cfw_service_nvdb_write(
    const char *key, const void *value, uint16_t length)
{
    return OPEN_CFW_NVDB_DB_WRITE(
        OPEN_CFW_NVDB_DATABASE_INDEX, key, value, length);
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 3
__attribute__((used, noinline))
void open_cfw_service_nvdb_defaults_get(open_cfw_nvdb_defaults *defaults)
{
    if (defaults != NULL) {
        defaults->nodes = (const open_cfw_nvdb_default_node *)(uintptr_t)
            OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS;
        defaults->count = OPEN_CFW_NVDB_DEFAULT_COUNT;
    }
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
__attribute__((used, noinline))
void open_cfw_service_nvdb_defaults_validate(void)
{
    const open_cfw_nvdb_default_node *default_nodes =
        (const open_cfw_nvdb_default_node *)(uintptr_t)
            OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS;
    uint32_t index;

    for (index = 0u; index < OPEN_CFW_NVDB_DEFAULT_COUNT; ++index) {
        const open_cfw_nvdb_default_node *node = &default_nodes[index];
        if (node->value_length == 0u) {
            continue;
        }
        if (OPEN_CFW_NVDB_DB_READ(OPEN_CFW_NVDB_DATABASE_INDEX, node->key,
                (void *)node->value, (uint16_t)node->value_length) == 0) {
            OPEN_CFW_NVDB_DIAGNOSTIC_MISSING(index, node->key);
        }
        if (open_cfw_nvdb_key_equal(node->key, OPEN_CFW_NVDB_SYSTEM_KEY)) {
            char psn[15] = {0};
            OPEN_CFW_NVDB_LEGACY_PSN_SCAN();
            if (OPEN_CFW_NVDB_OTP_PSN_READ(psn, 0u) == 0) {
                open_cfw_nvdb_copy_psn(
                    (volatile uint8_t *)(uintptr_t)
                        OPEN_CFW_NVDB_SYSTEM_DATA_ADDRESS,
                    psn);
            }
        }
    }
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 5
void open_cfw_service_nvdb_defaults_validate(void);

__attribute__((used, noinline))
int open_cfw_service_nvdb_init(void *lock_callback, void *unlock_callback)
{
    open_cfw_nvdb_defaults defaults;
    void *database = OPEN_CFW_NVDB_DB_GET(OPEN_CFW_NVDB_DATABASE_INDEX);
    uint32_t magic = 0u;
    int result;

    if (lock_callback != NULL && unlock_callback != NULL) {
        (void)OPEN_CFW_NVDB_DB_CONTROL(database, 2u, lock_callback);
        (void)OPEN_CFW_NVDB_DB_CONTROL(database, 3u, unlock_callback);
    }
    defaults.nodes = (const open_cfw_nvdb_default_node *)(uintptr_t)
        OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS;
    defaults.count = OPEN_CFW_NVDB_DEFAULT_COUNT;
    result = OPEN_CFW_NVDB_DB_INIT(database, OPEN_CFW_NVDB_FACTORY_NAME,
        OPEN_CFW_NVDB_PARTITION_NAME, &defaults, NULL);
    OPEN_CFW_NVDB_DIAGNOSTIC_INIT(result);
    if (result != 0) {
        return OPEN_CFW_NVDB_ERR_INIT;
    }

    result = OPEN_CFW_NVDB_DB_READ(OPEN_CFW_NVDB_DATABASE_INDEX,
        OPEN_CFW_NVDB_MAGIC_KEY, &magic, (uint16_t)sizeof(magic));
    OPEN_CFW_NVDB_DIAGNOSTIC_MAGIC(magic, result);
    if (result == 0 || magic != OPEN_CFW_NVDB_MAGIC) {
#if OPEN_CFW_NVDB_ALLOW_FACTORY_RESET
        (void)OPEN_CFW_NVDB_DB_SET_DEFAULT(database);
        result = OPEN_CFW_NVDB_DB_READ(OPEN_CFW_NVDB_DATABASE_INDEX,
            OPEN_CFW_NVDB_MAGIC_KEY, &magic, (uint16_t)sizeof(magic));
        if (result == 0 || magic != OPEN_CFW_NVDB_MAGIC) {
            return OPEN_CFW_NVDB_ERR_SCHEMA;
        }
#else
        return OPEN_CFW_NVDB_ERR_SCHEMA;
#endif
    }
    open_cfw_service_nvdb_defaults_validate();
    return OPEN_CFW_NVDB_OK;
}
#endif

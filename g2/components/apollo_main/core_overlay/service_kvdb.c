/* SPDX-License-Identifier: MIT */
/* Clean-room G2 sysenv KVDB lifecycle with destructive reset disabled. */
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif
#ifndef OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS
#define OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS 0x2000372Cu
#endif
#ifndef OPEN_CFW_KVDB_MAGIC_KEY
#define OPEN_CFW_KVDB_MAGIC_KEY ((const char *)0x0078E574u)
#endif
#ifndef OPEN_CFW_KVDB_PARTITION_NAME
#define OPEN_CFW_KVDB_PARTITION_NAME ((const char *)0x0078E58Cu)
#endif
#ifndef OPEN_CFW_KVDB_DATABASE_NAME
#define OPEN_CFW_KVDB_DATABASE_NAME ((const char *)0x0078E594u)
#endif
#ifndef OPEN_CFW_KVDB_BOOT_COUNT_KEY
#define OPEN_CFW_KVDB_BOOT_COUNT_KEY ((const char *)0x0078BF6Cu)
#endif
#ifndef OPEN_CFW_KVDB_ALLOW_FACTORY_RESET
#define OPEN_CFW_KVDB_ALLOW_FACTORY_RESET 0
#endif

#define OPEN_CFW_KVDB_INDEX 0u
#define OPEN_CFW_KVDB_MAGIC 0x5A000020u
#define OPEN_CFW_KVDB_DEFAULT_COUNT 12u
#define OPEN_CFW_KVDB_ERR_INIT 8
#define OPEN_CFW_KVDB_ERR_SCHEMA 9

#ifndef OPEN_CFW_KVDB_TYPES_DEFINED
#define OPEN_CFW_KVDB_TYPES_DEFINED 1
typedef struct {
    const char *key;
    const void *value;
    uint32_t value_length;
} open_cfw_kvdb_default_node;
typedef struct {
    const open_cfw_kvdb_default_node *nodes;
    uint32_t count;
} open_cfw_kvdb_defaults;
#endif
#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(open_cfw_kvdb_default_node) == 12u, "KVDB node ABI");
_Static_assert(sizeof(open_cfw_kvdb_defaults) == 8u, "KVDB defaults ABI");
#endif

#ifndef OPEN_CFW_KVDB_DB_READ
int open_cfw_kvdb_db_read(uint32_t, const char *, void *, uint16_t);
#define OPEN_CFW_KVDB_DB_READ(i,k,v,z) open_cfw_kvdb_db_read((i),(k),(v),(z))
#endif
#ifndef OPEN_CFW_KVDB_DB_WRITE
int open_cfw_kvdb_db_write(uint32_t, const char *, const void *, uint16_t);
#define OPEN_CFW_KVDB_DB_WRITE(i,k,v,z) open_cfw_kvdb_db_write((i),(k),(v),(z))
#endif
#ifndef OPEN_CFW_KVDB_DB_GET
void *open_cfw_kvdb_db_get(uint32_t);
#define OPEN_CFW_KVDB_DB_GET(i) open_cfw_kvdb_db_get((i))
#endif
#ifndef OPEN_CFW_KVDB_DB_CONTROL
int open_cfw_kvdb_db_control(void *, uint32_t, void *);
#define OPEN_CFW_KVDB_DB_CONTROL(d,c,a) open_cfw_kvdb_db_control((d),(c),(a))
#endif
#ifndef OPEN_CFW_KVDB_DB_INIT
int open_cfw_kvdb_db_init(void *, const char *, const char *,
    const open_cfw_kvdb_defaults *, void *);
#define OPEN_CFW_KVDB_DB_INIT(d,n,p,f,u) open_cfw_kvdb_db_init((d),(n),(p),(f),(u))
#endif
#ifndef OPEN_CFW_KVDB_DB_SET_DEFAULT
int open_cfw_kvdb_db_set_default(void *);
#define OPEN_CFW_KVDB_DB_SET_DEFAULT(d) open_cfw_kvdb_db_set_default((d))
#endif

#define DECLARE_MIGRATION(n) void open_cfw_kvdb_migrate_##n(void)
DECLARE_MIGRATION(1); DECLARE_MIGRATION(2); DECLARE_MIGRATION(3);
DECLARE_MIGRATION(4); DECLARE_MIGRATION(5); DECLARE_MIGRATION(6);
DECLARE_MIGRATION(7); DECLARE_MIGRATION(8); DECLARE_MIGRATION(9);
DECLARE_MIGRATION(10); DECLARE_MIGRATION(11);

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used,noinline)) void open_cfw_service_kvdb_run_migrations(void)
{
    open_cfw_kvdb_migrate_1(); open_cfw_kvdb_migrate_2();
    open_cfw_kvdb_migrate_3(); open_cfw_kvdb_migrate_4();
    open_cfw_kvdb_migrate_5(); open_cfw_kvdb_migrate_6();
    open_cfw_kvdb_migrate_7(); open_cfw_kvdb_migrate_8();
    open_cfw_kvdb_migrate_9(); open_cfw_kvdb_migrate_10();
    open_cfw_kvdb_migrate_11();
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used,noinline)) int open_cfw_service_kvdb_read(
    const char *key, void *value, uint16_t length)
{ return OPEN_CFW_KVDB_DB_READ(OPEN_CFW_KVDB_INDEX,key,value,length); }
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 3
__attribute__((used,noinline)) int open_cfw_service_kvdb_write(
    const char *key, const void *value, uint16_t length)
{ return OPEN_CFW_KVDB_DB_WRITE(OPEN_CFW_KVDB_INDEX,key,value,length); }
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
__attribute__((used,noinline)) void open_cfw_service_kvdb_defaults_get(
    open_cfw_kvdb_defaults *defaults)
{
    if (defaults != NULL) {
        defaults->nodes=(const open_cfw_kvdb_default_node *)(uintptr_t)
            OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS;
        defaults->count=OPEN_CFW_KVDB_DEFAULT_COUNT;
    }
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 5
__attribute__((used,noinline)) void open_cfw_service_kvdb_read_all(void)
{
    const open_cfw_kvdb_default_node *default_nodes=
        (const open_cfw_kvdb_default_node *)(uintptr_t)
            OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS;
    uint32_t index;
    for (index=0; index<OPEN_CFW_KVDB_DEFAULT_COUNT; ++index) {
        if (default_nodes[index].value_length != 0u) {
            (void)OPEN_CFW_KVDB_DB_READ(OPEN_CFW_KVDB_INDEX,default_nodes[index].key,
                (void *)default_nodes[index].value,(uint16_t)default_nodes[index].value_length);
        }
    }
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 6
void open_cfw_service_kvdb_run_migrations(void);
void open_cfw_service_kvdb_read_all(void);
__attribute__((used,noinline)) int open_cfw_service_kvdb_init(
    void *lock_callback, void *unlock_callback)
{
    open_cfw_kvdb_defaults defaults;
    void *database=OPEN_CFW_KVDB_DB_GET(OPEN_CFW_KVDB_INDEX);
    uint32_t magic=0u, boot_count=0u;
    int result;
    if (lock_callback != NULL && unlock_callback != NULL) {
        (void)OPEN_CFW_KVDB_DB_CONTROL(database,2u,lock_callback);
        (void)OPEN_CFW_KVDB_DB_CONTROL(database,3u,unlock_callback);
    }
    defaults.nodes=(const open_cfw_kvdb_default_node *)(uintptr_t)
        OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS;
    defaults.count=OPEN_CFW_KVDB_DEFAULT_COUNT;
    result=OPEN_CFW_KVDB_DB_INIT(database,OPEN_CFW_KVDB_DATABASE_NAME,
        OPEN_CFW_KVDB_PARTITION_NAME,&defaults,NULL);
    if (result != 0) return OPEN_CFW_KVDB_ERR_INIT;
    result=OPEN_CFW_KVDB_DB_READ(OPEN_CFW_KVDB_INDEX,OPEN_CFW_KVDB_MAGIC_KEY,
        &magic,(uint16_t)sizeof(magic));
    if (result == 0 || magic != OPEN_CFW_KVDB_MAGIC) {
#if OPEN_CFW_KVDB_ALLOW_FACTORY_RESET
        (void)OPEN_CFW_KVDB_DB_SET_DEFAULT(database);
#else
        return OPEN_CFW_KVDB_ERR_SCHEMA;
#endif
    }
    if (OPEN_CFW_KVDB_DB_READ(OPEN_CFW_KVDB_INDEX,
            OPEN_CFW_KVDB_BOOT_COUNT_KEY,&boot_count,4u) == 0) boot_count=0u;
    ++boot_count;
    (void)OPEN_CFW_KVDB_DB_WRITE(OPEN_CFW_KVDB_INDEX,
        OPEN_CFW_KVDB_BOOT_COUNT_KEY,&boot_count,4u);
    open_cfw_service_kvdb_run_migrations();
    open_cfw_service_kvdb_read_all();
    return 0;
}
#endif
#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 7
__attribute__((used,noinline)) int open_cfw_service_kvdb_invalidate_magic(void)
{
#if OPEN_CFW_KVDB_ALLOW_FACTORY_RESET
    uint32_t magic=0u;
    return OPEN_CFW_KVDB_DB_WRITE(OPEN_CFW_KVDB_INDEX,
        OPEN_CFW_KVDB_MAGIC_KEY,&magic,4u);
#else
    return OPEN_CFW_KVDB_ERR_SCHEMA;
#endif
}
#endif

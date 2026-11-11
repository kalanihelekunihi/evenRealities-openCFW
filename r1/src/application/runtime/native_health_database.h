#ifndef R1_NATIVE_HEALTH_DATABASE_H
#define R1_NATIVE_HEALTH_DATABASE_H
#include <stdint.h>
#include <flashdb.h>
#include <cmsis_os2.h>
struct r1_health_database_storage {
    struct fdb_tsdb database;
    uint32_t mutex_control[20];
};
extern struct r1_health_database_storage r1_health_database_storage;
extern osMutexId_t volatile r1_health_database_mutex;
void r1_health_database_lock(fdb_db_t);
void r1_health_database_unlock(fdb_db_t);
fdb_time_t r1_health_database_get_time(void);
void r1_native_health_database_initialize(void);
#endif

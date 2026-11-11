/* Stock 0x70030 health DB startup and its native lock/time callbacks. */
#include "native_health_database.h"
#include "native_health_hour_storage.h"
#include "native_health_time_storage.h"
#include "native_health_daily_replay.h"
#include "native_crash_recovery.h"
#include "native_subscriber.h"
#include "time_calendar/time_calendar.h"
#include <stddef.h>
#include <string.h>
_Static_assert(sizeof(struct fdb_tsdb)==100 && offsetof(struct fdb_tsdb,get_time)==84 && offsetof(struct fdb_tsdb,max_len)==88 && offsetof(struct fdb_tsdb,rollover)==92,"native short-enum TSDB ABI");
_Static_assert(offsetof(struct r1_health_database_storage,mutex_control)==100 && sizeof(struct r1_health_database_storage)==180 && sizeof(osMutexAttr_t)==16,"native DB and static mutex extent");
struct r1_health_database_storage r1_health_database_storage __attribute__((section(".r1.health.db.storage"),aligned(4)))={0};
osMutexId_t volatile r1_health_database_mutex __attribute__((section(".r1.health.db.mutex"),aligned(4)))=NULL;
const osMutexAttr_t r1_health_database_mutex_attr={.name="db_mutex",.attr_bits=0,.cb_mem=r1_health_database_storage.mutex_control,.cb_size=80};
extern const uint8_t r1_health_sync_kind0[2],r1_health_sync_kind1[2],r1_health_sync_kind2[2],r1_health_sync_kind3[2],r1_health_sync_kind4[2],r1_health_sync_kind5[2];
struct r1_event_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
extern struct r1_event_context r1_event_system;
extern uint32_t r1_health_sync_provider_00063694(volatile uint8_t *,uint32_t,volatile uint8_t *);
extern void r1_health_sync_provider_00063ad8(fdb_tsdb_t,fdb_time_t,fdb_time_t,fdb_tsl_cb,void *);
extern void r1_health_crash_snapshot_restore(void);
extern uint32_t r1_time_backend_timestamp(void),r1_event_service_0008aea4(void);
extern uint32_t r1_event_service_0008aeb0(uint32_t,int32_t);
extern int32_t r1_time_utc_offset_get(void);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
#define TEXT(name,value) static const char name[]=value
TEXT(size_ring,"[RING]db_storage init failed, store size is too large");
TEXT(size_sdk,"db_storage init failed, store size is too large");
TEXT(init_ring,"[RING]db_storage init failed, error:%d");
TEXT(init_sdk,"db_storage init failed, error:%d");
TEXT(restore_ring,"[RING]db_storage crash time restore, timestamp:%d, timezone:%d");
TEXT(restore_sdk,"db_storage crash time restore, timestamp:%d, timezone:%d");
TEXT(range_ring,"[RING]db storage timezone:%d, zero_time:%d, current_time:%d");
TEXT(range_sdk,"db storage timezone:%d, zero_time:%d, current_time:%d");
TEXT(alloc_ring,"[RING]db_storage recover_query_by_time_cb malloc failed");
TEXT(alloc_sdk,"db_storage recover_query_by_time_cb malloc failed");
#undef TEXT
static uint32_t ring_enabled(void){return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void error0(const char *ring,const char *sdk){if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,sdk);}
void r1_health_database_lock(fdb_db_t db){(void)db;osMutexId_t mutex=r1_health_database_mutex;if(mutex)(void)osMutexAcquire(mutex,osWaitForever);}
void r1_health_database_unlock(fdb_db_t db){(void)db;osMutexId_t mutex=r1_health_database_mutex;if(mutex)(void)osMutexRelease(mutex);}
fdb_time_t r1_health_database_get_time(void){return (fdb_time_t)r1_time_backend_timestamp();}
void r1_native_health_database_initialize(void)
{
    const volatile uint8_t *descriptors[6]={r1_health_sync_kind0,r1_health_sync_kind1,r1_health_sync_kind2,r1_health_sync_kind3,r1_health_sync_kind4,r1_health_sync_kind5};
    uint16_t total=0;
    for(uint32_t i=0;i<6;++i)total=(uint16_t)(total+descriptors[i][1]);
    total=(uint16_t)(total+8u);
    if(total>128){error0(size_ring,size_sdk);return;}
    fdb_tsdb_t db=&r1_health_database_storage.database;
    (void)r1_health_sync_provider_00063694((volatile uint8_t *)db,2,(volatile uint8_t *)(uintptr_t)r1_health_database_lock);
    (void)r1_health_sync_provider_00063694((volatile uint8_t *)db,3,(volatile uint8_t *)(uintptr_t)r1_health_database_unlock);
    fdb_err_t status=fdb_tsdb_init(db,"health","health.db",r1_health_database_get_time,128,NULL);
    if(status!=FDB_NO_ERR){if(ring_enabled())(void)r1_structured_log_format(0x0c400000,init_ring,init_ring,(uint32_t)status);if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,init_sdk,(uint32_t)status);return;}
    if(!r1_health_database_mutex)r1_health_database_mutex=osMutexNew(&r1_health_database_mutex_attr);
    (void)r1_subscriber_register(1,(uint32_t)(uintptr_t)r1_health_hour_boundary_storage_orchestrator,(uint32_t)(uintptr_t)&r1_event_system.thread);
    (void)r1_subscriber_register(0,(uint32_t)(uintptr_t)r1_health_time_transition_storage_orchestrator,(uint32_t)(uintptr_t)&r1_event_system.thread);
    if(r1_health_crash_record_magic_probe()){
        uint32_t timestamp;uint16_t offset;uint8_t pending;
        if(r1_health_crash_time_accessor(&timestamp,&offset,&pending)){
            (void)r1_event_service_0008aeb0(timestamp,(int32_t)offset);
            if(pending)(void)r1_event_service_0008aea4();
            (void)r1_health_crash_time_clear();
            if(ring_enabled())(void)r1_structured_log_format(0x0c800000,restore_ring,restore_ring,timestamp,(uint32_t)offset);
            if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,restore_sdk,timestamp,(uint32_t)offset);
        }
    }
    uint32_t now=r1_time_backend_timestamp();int32_t offset=r1_time_utc_offset_get();
    time_calendar_datetime calendar={0};
    (void)time_calendar_utc_to_calendar((int32_t)now,offset,&calendar);
    calendar.hour=0;calendar.minute=0;calendar.second=0;
    uint32_t midnight=(uint32_t)time_calendar_to_utc(&calendar,offset);
    if(ring_enabled())(void)r1_structured_log_format(0x0cc00000,range_ring,range_ring,(uint32_t)offset,midnight,now);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_3(0x001c0003,range_sdk,(uint32_t)offset,midnight,now);
    void *buffer=pvPortMalloc(128);
    if(!buffer){error0(alloc_ring,alloc_sdk);return;}
    memset(buffer,0,128);
    r1_health_sync_provider_00063ad8(db,(fdb_time_t)midnight,(fdb_time_t)now,r1_health_daily_record_replay,buffer);
    vPortFree(buffer);
    r1_health_crash_snapshot_restore();
}

/* Native 0x70028: the existing database owner, no independent state. */
fdb_tsdb_t r1_health_sync_provider_00070028(void)
{return &r1_health_database_storage.database;}

/* R1 port bindings recovered from native cold data and callback bodies.
 * Initializer/store backends remain unresolved production functions. */
#include "native_kv_class.h"
extern int32_t osMutexAcquire(void *,uint32_t);
extern int32_t osMutexRelease(void *);
extern void *volatile r1_kv_storage_context;
extern uint32_t r1_kv_port_initialize(void);
extern uint32_t r1_kv_store_get(uint32_t,void *,uint32_t);
extern uint32_t r1_kv_store_put(uint32_t,const void *,uint32_t);
struct r1_kv_port_view *volatile r1_kv_port __attribute__((section(".r1.kv.port_slot")));
void *volatile r1_kv_mutex __attribute__((section(".r1.kv.mutex")));
volatile uint8_t r1_kv_block_cursor __attribute__((section(".r1.kv.block_cursor")));
uint32_t r1_kv_port_zero_4(void) { return 0; }
uint32_t r1_kv_port_zero_8(void) { return 0; }
uint32_t r1_kv_port_zero_12(void) { return 0; }
void r1_kv_port_lock(void)
{ void *mutex=r1_kv_mutex;if (mutex) (void)osMutexAcquire(mutex,UINT32_MAX); }
void r1_kv_port_unlock(void)
{ void *mutex=r1_kv_mutex;if (mutex) (void)osMutexRelease(mutex); }
uint32_t r1_kv_port_control(uint32_t operation,uint32_t *result)
{
    if (operation==1) r1_kv_block_cursor=(uint8_t)(r1_kv_block_cursor+1u);
    else if (operation==3) {
        if (!result) return 1;
        void *storage=r1_kv_storage_context;
        *result=storage ? *(const uint32_t *)storage:UINT32_C(0xa5a5a5a5);
    }
    return 0;
}
struct r1_kv_port_record {
    uint32_t (*initialize)(void),(*slot4)(void),(*slot8)(void),(*slot12)(void);
    uint32_t (*get)(uint32_t,void *,uint32_t);
    uint32_t (*put)(uint32_t,const void *,uint32_t);
    uint32_t (*control)(uint32_t,uint32_t *);
    void (*enter)(void),(*leave)(void);
};
_Static_assert(sizeof(struct r1_kv_port_record)==36,"native port record");
_Static_assert(offsetof(struct r1_kv_port_record,enter)==28 && offsetof(struct r1_kv_port_record,leave)==32,"native critical callbacks");
struct r1_kv_port_record r1_kv_native_port_record __attribute__((section(".r1.kv.port_record")))={
    r1_kv_port_initialize,r1_kv_port_zero_4,r1_kv_port_zero_8,r1_kv_port_zero_12,
    r1_kv_store_get,r1_kv_store_put,r1_kv_port_control,r1_kv_port_lock,r1_kv_port_unlock
};
void r1_kv_port_bind(struct r1_kv_port_view *volatile *destination)
{ *destination=(struct r1_kv_port_view *)&r1_kv_native_port_record; }

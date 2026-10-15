#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "native_watchdog.h"
_Static_assert(sizeof(struct r1_native_watchdog_record)==28,"native watchdog record");
volatile uint8_t r1_native_watchdog_enabled __attribute__((section(".r1.watchdog.enabled"),aligned(1)));
void *volatile r1_native_watchdog_mutex __attribute__((section(".r1.watchdog.mutex"),aligned(4)));
struct r1_native_watchdog_registry r1_native_watchdog_registry
 __attribute__((section(".r1.watchdog.registry"),aligned(4)));
extern int32_t osMutexAcquire(void *,uint32_t),osMutexRelease(void *);
extern void *pvPortMalloc(size_t);
struct tskTaskControlBlock;
extern struct tskTaskControlBlock *xTaskGetCurrentTaskHandle(void);

void r1_native_watchdog_lock(void)
{ if (r1_native_watchdog_mutex) osMutexAcquire(r1_native_watchdog_mutex,UINT32_MAX); }
void r1_native_watchdog_unlock(void)
{ if (r1_native_watchdog_mutex) osMutexRelease(r1_native_watchdog_mutex); }
void *r1_native_list_head(struct r1_native_list *list) { return list ? list->head : 0; }
void *r1_native_list_tail(struct r1_native_list *list) { return list ? list->tail : 0; }
void *r1_native_list_next(struct r1_native_list *list,void *node)
{ return *(void **)((uintptr_t)node+list->payload_bytes+4u); }
void r1_native_list_set_next(struct r1_native_list *list,void *node,void *next)
{ if (node) *(void **)((uintptr_t)node+list->payload_bytes+4u)=next; }
void r1_native_list_set_previous(struct r1_native_list *list,void *node,void *previous)
{ if (node) *(void **)((uintptr_t)node+list->payload_bytes)=previous; }
void r1_native_list_initialize(struct r1_native_list *list,uint32_t payload_bytes)
{ list->payload_bytes=(payload_bytes+3u)&~UINT32_C(3);list->head=0;list->tail=0; }
uint32_t r1_native_list_empty(struct r1_native_list *list)
{ return !list || (!list->head && !list->tail); }
void *r1_native_list_append(struct r1_native_list *list)
{
    void *node=pvPortMalloc(list->payload_bytes+8u);
    if (node) {
        r1_native_list_set_next(list,node,0);
        r1_native_list_set_previous(list,node,list->tail);
        if (list->tail) r1_native_list_set_next(list,list->tail,node);
        list->tail=node;
        if (!list->head) list->head=node;
    }
    return node;
}
void *r1_native_list_prepend(struct r1_native_list *list)
{
    void *node=pvPortMalloc(list->payload_bytes+8u);
    if (node) {
        r1_native_list_set_previous(list,node,0);
        r1_native_list_set_next(list,node,list->head);
        if (list->head) r1_native_list_set_previous(list,list->head,node);
        list->head=node;
        if (!list->tail) list->tail=node;
    }
    return node;
}
uint32_t r1_native_watchdog_register(const char *name,uint32_t interval)
{
    if (!r1_native_watchdog_enabled || !name || !interval) return 0;
    r1_native_watchdog_lock();
    struct r1_native_list *list=&r1_native_watchdog_registry.list;
    for (struct r1_native_watchdog_record *record=r1_native_list_head(list);record;record=r1_native_list_next(list,record))
        if (strcmp(record->name,name)==0) { r1_native_watchdog_unlock();return 0; }
    struct r1_native_watchdog_record *record=r1_native_list_append(list);
    if (record) {
        memset(record,0,28);record->owner=&r1_native_watchdog_registry;
        uint32_t bytes=(uint8_t)strlen(name);if (bytes>7) bytes=7;
        memcpy(record->name,name,bytes);record->name[bytes]=0;
        record->interval=interval;record->flags&=~UINT32_C(3);
        record->task=xTaskGetCurrentTaskHandle();
    }
    r1_native_watchdog_unlock();return (uint32_t)(uintptr_t)record;
}
void r1_native_watchdog_arm(uint32_t handle)
{
    struct r1_native_watchdog_record *record=(void *)(uintptr_t)handle;
    if (record) { r1_native_watchdog_lock();record->flags|=2u;r1_native_watchdog_unlock(); }
}
void r1_native_watchdog_disarm(uint32_t handle)
{
    struct r1_native_watchdog_record *record=(void *)(uintptr_t)handle;
    if (record) {
        r1_native_watchdog_lock();record->flags&=~UINT32_C(2);record->timestamp=0;
        record->owner->port->sample(1,&record->timestamp);
        r1_native_watchdog_unlock();
    }
}
void r1_native_watchdog_feed(uint32_t handle)
{
    struct r1_native_watchdog_record *record=(void *)(uintptr_t)handle;
    if (record) {
        r1_native_watchdog_lock();
        r1_native_watchdog_registry.port->sample(1,&record->timestamp);
        r1_native_watchdog_registry.port->sample(0,0);
        r1_native_watchdog_unlock();
    }
}

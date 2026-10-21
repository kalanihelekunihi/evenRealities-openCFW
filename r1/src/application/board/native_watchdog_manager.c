#include <stdint.h>
#include <stddef.h>
#include "cmsis_os2.h"
#include "native_watchdog.h"

struct r1_native_watchdog_record *volatile r1_native_watchdog_fault_record
 __attribute__((section(".r1.watchdog.fault_record"),aligned(4)));
uint8_t r1_native_watchdog_mutex_storage[80]
 __attribute__((section(".r1.watchdog.mutex_storage"),aligned(4)));
const osMutexAttr_t r1_native_watchdog_mutex_attributes
 __attribute__((section(".r1.watchdog.mutex_attributes"),aligned(4)))={
    .name="fw_wtd",.attr_bits=0,.cb_mem=r1_native_watchdog_mutex_storage,.cb_size=80
};
_Static_assert(sizeof(osMutexAttr_t)==16,"native CMSIS mutex attributes");

uint32_t r1_native_watchdog_initialize(void)
{
    if (r1_native_watchdog_enabled) return 1;
    struct r1_native_watchdog_port *port=r1_native_watchdog_port_get();
    if (!port) return 0;
    r1_native_watchdog_registry.list.payload_bytes=0;
    r1_native_watchdog_registry.list.head=0;r1_native_watchdog_registry.list.tail=0;
    r1_native_watchdog_registry.port=port;
    r1_native_list_initialize(&r1_native_watchdog_registry.list,28);
    if (!r1_native_watchdog_mutex) {
        r1_native_watchdog_mutex=osMutexNew(&r1_native_watchdog_mutex_attributes);
        if (!r1_native_watchdog_mutex) return 0;
    }
    if (!r1_native_watchdog_registry.port->start(10000)) return 0;
    r1_native_watchdog_fault_record=0;r1_native_watchdog_enabled=1;return 1;
}
uint32_t r1_native_watchdog_expired_task(void)
{
    struct r1_native_watchdog_record *record=r1_native_watchdog_fault_record;
    if (!record || !(record->flags&1u) || !record->task) return 0;
    return (uint32_t)(uintptr_t)record->task;
}
void r1_native_watchdog_check(void)
{
    if (!r1_native_watchdog_enabled) return;
    r1_native_watchdog_lock();
    uint32_t now;r1_native_watchdog_registry.port->sample(1,&now);
    struct r1_native_list *list=&r1_native_watchdog_registry.list;
    for (struct r1_native_watchdog_record *record=r1_native_list_head(list);record;record=r1_native_list_next(list,record)) {
        if (!(record->flags&2u) && now-record->timestamp>=record->interval) {
            record->flags|=1u;
            __asm__ volatile ("msr basepri, %0" :: "r"(UINT32_C(64)) : "memory");
            r1_native_watchdog_fault_record=record;
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
            for (;;) {}
        }
    }
    r1_native_watchdog_unlock();
}

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
/* The registered sample operation writes a complete uint32_t tick count.
 * Initialize the C scratch word deterministically; the void C operation has
 * no scratch-register return. BASEPRI still needs its architectural write. */
__attribute__((noinline)) void r1_native_watchdog_check(void)
{
    volatile struct {uint32_t now;struct r1_native_list *list;} frame;
    _Static_assert(sizeof(frame)==8,"native watchdog C frame locals");
    frame.now=0;
    if (r1_native_watchdog_enabled) {
        r1_native_watchdog_lock();
        r1_native_watchdog_registry.port->sample(1,(uint32_t *)(uintptr_t)&frame.now);
        frame.list=&r1_native_watchdog_registry.list;
        for (struct r1_native_watchdog_record *record=r1_native_list_head(frame.list);record;record=r1_native_list_next(frame.list,record)) {
            volatile struct r1_native_watchdog_record *live=record;
            if (!(*(volatile uint8_t *)&live->flags&2u)) {
                uint32_t timestamp=live->timestamp,interval=live->interval,current=frame.now;
                if (current-timestamp>=interval) {
                    live->flags|=1u;
                    __builtin_arm_wsr("basepri",UINT32_C(64));
                    r1_native_watchdog_fault_record=record;
                    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
                    for (;;) {}
                }
            }
        }
        r1_native_watchdog_unlock();
    }
}

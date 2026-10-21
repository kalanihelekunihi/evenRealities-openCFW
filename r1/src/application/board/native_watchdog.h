#ifndef R1_NATIVE_WATCHDOG_H
#define R1_NATIVE_WATCHDOG_H
#include <stdint.h>
struct r1_native_list { uint32_t payload_bytes; void *head,*tail; };
struct r1_native_watchdog_port {
    uint32_t (*start)(uint32_t),(*stop)(void),(*sample)(uint32_t,uint32_t *);
};
struct r1_native_watchdog_registry { struct r1_native_watchdog_port *volatile port; struct r1_native_list list; };
struct r1_native_watchdog_record {
    struct r1_native_watchdog_registry *owner;
    void *task;
    char name[8];
    uint32_t flags,timestamp,interval;
};
extern volatile uint8_t r1_native_watchdog_enabled;
extern void *volatile r1_native_watchdog_mutex;
extern struct r1_native_watchdog_registry r1_native_watchdog_registry;
extern struct r1_native_watchdog_record *volatile r1_native_watchdog_fault_record;
void r1_native_watchdog_lock(void),r1_native_watchdog_unlock(void);
void *r1_native_list_head(struct r1_native_list *);
void *r1_native_list_next(struct r1_native_list *,void *);
void r1_native_list_initialize(struct r1_native_list *,uint32_t);
struct r1_native_watchdog_port *r1_native_watchdog_port_get(void);
uint32_t r1_native_watchdog_hw_handle_init(void),r1_native_watchdog_hw_open_feed(void);
uint32_t r1_native_watchdog_hw_close(void),r1_native_watchdog_hw_feed(void);
#endif

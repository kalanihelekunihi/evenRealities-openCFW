#include <stdint.h>
#include <stddef.h>
/* Authenticated CMSIS-RTOS2 36-byte native attributes and 16-byte task prefixes.
 * 112-byte TCB reservations do not prove the kernel's complete TCB layout. */
struct r1_event_context { void (*create)(void),(*stop)(void); void *thread,*queue; };
struct r1_tx_context { void (*create)(void),(*stop)(void); void *thread,*queue; };
struct r1_native_thread_attr { const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size; void *stack_mem; uint32_t stack_size; int32_t priority; uint32_t tz_module,reserved; };
_Static_assert(sizeof(struct r1_native_thread_attr)==36,"native attributes");
extern void *osThreadNew(void (*entry)(void *),void *argument,const struct r1_native_thread_attr *attributes);
extern int32_t osThreadTerminate(void *thread);
static void create(void **handle,void (*entry)(void *),const struct r1_native_thread_attr *attributes)
{
    *handle=osThreadNew(entry,0,attributes);
    if (!*handle) {
        __asm__ volatile ("msr basepri, %0" :: "r"(UINT32_C(64)) : "memory");
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
        for (;;) {}
    }
}
static void stop(void **handle)
{
    if (*handle) { osThreadTerminate(*handle);*handle=0; }
}

extern struct r1_event_context r1_event_sensor;
extern void r1_native_task_service(void *);
uint8_t r1_task_a_tcb[112] __attribute__((section(".r1.task.a.tcb"),aligned(8)));
uint8_t r1_task_a_stack[8192] __attribute__((section(".r1.task.a.stack"),aligned(8)));
const struct r1_native_thread_attr r1_task_a_attributes={"service",0,r1_task_a_tcb,112,r1_task_a_stack,8192,38,1,0};
void r1_thread_create_a(void) { create(&r1_event_sensor.thread,r1_native_task_service,&r1_task_a_attributes); }
void r1_task_stop_668c(void) { stop(&r1_event_sensor.thread); }

extern struct r1_event_context r1_event_system;
extern void r1_native_task_sensor(void *);
uint8_t r1_task_f_tcb[112] __attribute__((section(".r1.task.f.tcb"),aligned(8)));
uint8_t r1_task_f_stack[11264] __attribute__((section(".r1.task.f.stack"),aligned(8)));
const struct r1_native_thread_attr r1_task_f_attributes={"sensor",0,r1_task_f_tcb,112,r1_task_f_stack,11264,39,1,0};
void r1_thread_create_f(void) { create(&r1_event_system.thread,r1_native_task_sensor,&r1_task_f_attributes); }
void r1_task_stop_6608(void) { stop(&r1_event_system.thread); }

extern struct r1_event_context r1_event_storage;
extern void r1_native_task_storage(void *);
uint8_t r1_task_g_tcb[112] __attribute__((section(".r1.task.g.tcb"),aligned(8)));
uint8_t r1_task_g_stack[2048] __attribute__((section(".r1.task.g.stack"),aligned(8)));
const struct r1_native_thread_attr r1_task_g_attributes={"storage",0,r1_task_g_tcb,112,r1_task_g_stack,2048,8,1,0};
void r1_thread_create_g(void) { create(&r1_event_storage.thread,r1_native_task_storage,&r1_task_g_attributes); }
void r1_task_stop_66d8(void) { stop(&r1_event_storage.thread); }

extern struct r1_tx_context r1_tx_shared;
extern void r1_native_task_gtx(void *);
uint8_t r1_task_b_tcb[112] __attribute__((section(".r1.task.b.tcb"),aligned(8)));
uint8_t r1_task_b_stack[2048] __attribute__((section(".r1.task.b.stack"),aligned(8)));
const struct r1_native_thread_attr r1_task_b_attributes={"ble_gtx",0,r1_task_b_tcb,112,r1_task_b_stack,2048,52,1,0};
void r1_thread_create_b(void) { create(&r1_tx_shared.thread,r1_native_task_gtx,&r1_task_b_attributes); }
void r1_task_stop_65e0(void) { stop(&r1_tx_shared.thread); }

extern struct r1_tx_context r1_tx_channel1;
extern void r1_native_task_msgtx(void *);
uint8_t r1_task_e_tcb[112] __attribute__((section(".r1.task.e.tcb"),aligned(8)));
uint8_t r1_task_e_stack[4096] __attribute__((section(".r1.task.e.stack"),aligned(8)));
const struct r1_native_thread_attr r1_task_e_attributes={"ble_msgtx",0,r1_task_e_tcb,112,r1_task_e_stack,4096,51,1,0};
void r1_thread_create_e(void) { create(&r1_tx_channel1.thread,r1_native_task_msgtx,&r1_task_e_attributes); }
void r1_task_stop_65bc(void) { stop(&r1_tx_channel1.thread); }

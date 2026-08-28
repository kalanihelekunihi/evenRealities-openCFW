/* SPDX-License-Identifier: MIT */
#include "../../components/shared/lvgl/runtime_ambiq_nema_hal_candidate.h"
#include <string.h>

enum { ALLOC = 1, FREE, ACQUIRE, RELEASE, CREATE, RING, CLEAN, INVALIDATE,
       CLEAR_IRQ, ENABLE_IRQ, PRIORITY, PEND, CALLBACK };
struct event { uint32_t op; uintptr_t a; uint32_t b; uint32_t c; };
static struct event events[32];
static uint32_t event_count;
static uint32_t registers_[0x150U / 4U];
static struct open_cfw_nema_heap heaps[3];
static struct open_cfw_nema_hal hal;
static int heap_contexts[3];

static void record(uint32_t op, uintptr_t a, uint32_t b, uint32_t c)
{ events[event_count++] = (struct event){op, a, b, c}; }
static void *allocate(void *heap, uint32_t size, uint32_t alignment)
{ record(ALLOC, (uintptr_t)heap, size, alignment); return (void *)(uintptr_t)(0x1000U + ((uintptr_t)heap & 0xffU) * 0x100U + size); }
static void release_(void *heap, void *allocation)
{ record(FREE, (uintptr_t)heap, (uint32_t)(uintptr_t)allocation, 0); }
static int32_t acquire(void *sem, uint32_t timeout)
{ record(ACQUIRE, (uintptr_t)sem, timeout, 0); return 1; }
static int32_t release_sem(void *sem)
{ record(RELEASE, (uintptr_t)sem, 0, 0); return 1; }
static void *create(uint32_t maximum, uint32_t initial, uint32_t type)
{ record(CREATE, maximum, initial, type); return (void *)(uintptr_t)0x55; }
static int32_t ring(struct open_cfw_nema_ringbuffer *r, int reset)
{ record(RING, (uintptr_t)r, (uint32_t)reset, 0); return 0; }
static void clean(uintptr_t a, uint32_t s) { record(CLEAN, a, s, 0); }
static void invalidate(uintptr_t a, uint32_t s) { record(INVALIDATE, a, s, 0); }
static void clear_irq(uint32_t irq) { record(CLEAR_IRQ, irq, 0, 0); }
static void enable_irq(uint32_t irq) { record(ENABLE_IRQ, irq, 0, 0); }
static void priority(uint32_t irq, uint32_t p) { record(PRIORITY, irq, p, 0); }
static void pend(void) { record(PEND, 0, 0, 0); }
static void diagnostic(const char *message) { (void)message; }
static void fatal(void) { }
static void callback(int32_t cl) { record(CALLBACK, (uintptr_t)(uint32_t)cl, 0, 0); }
static const struct open_cfw_nema_hal_ports ports = {
 allocate, release_, acquire, release_sem, create, ring, clean, invalidate,
 clear_irq, enable_irq, priority, pend, diagnostic, fatal
};

void test_nema_hal_reset(uint32_t render_cacheable, uint32_t assets_cacheable, uint32_t cpu_cacheable)
{
 memset(events, 0, sizeof(events)); event_count = 0; memset(registers_, 0, sizeof(registers_));
 memset(&hal, 0, sizeof(hal)); memset(heaps, 0, sizeof(heaps));
 heap_contexts[0] = 1; heap_contexts[1] = 2; heap_contexts[2] = 3;
 heaps[0] = (struct open_cfw_nema_heap){0x20010000U, 0x1000U, render_cacheable != 0U, &heap_contexts[0]};
 heaps[1] = (struct open_cfw_nema_heap){0x60000000U, 0x2000U, assets_cacheable != 0U, &heap_contexts[1]};
 heaps[2] = (struct open_cfw_nema_heap){0x20020000U, 0x0800U, cpu_cacheable != 0U, &heap_contexts[2]};
 hal.registers = registers_; hal.render_heap = &heaps[0]; hal.assets_heap = &heaps[1];
 hal.cpu_heap = &heaps[2]; hal.last_cl_id = -1; hal.interrupt_callback = callback; hal.ports = &ports;
}
uint64_t test_nema_hal_create(int32_t pool, uint32_t size)
{ struct open_cfw_nema_buffer b = open_cfw_nema_buffer_create_pool_candidate(&hal, pool, size); return ((uint64_t)b.size << 32) | (uint32_t)b.fd; }
uint32_t test_nema_hal_within(int32_t pool, uint32_t start, uint32_t length)
{ return open_cfw_nema_buffer_is_within_pool_candidate(&hal, pool, start, length); }
int32_t test_nema_hal_sys_init(void) { return open_cfw_nema_sys_init_candidate(&hal); }
void test_nema_hal_irq(uint32_t clid) { registers_[OPEN_CFW_NEMA_CLID >> 2] = clid; open_cfw_nema_irq_candidate(&hal); }
uint32_t test_nema_hal_count(void) { return event_count; }
uint32_t test_nema_hal_op(uint32_t i) { return events[i].op; }
uint64_t test_nema_hal_arg(uint32_t i) { return events[i].a; }
uint32_t test_nema_hal_b(uint32_t i) { return events[i].b; }
uint32_t test_nema_hal_c(uint32_t i) { return events[i].c; }
uint32_t test_nema_hal_ring_size(void) { return hal.ring.bo.size; }
uint32_t test_nema_hal_ring_fd(void) { return (uint32_t)hal.ring.bo.fd; }
int32_t test_nema_hal_last(void) { return hal.last_cl_id; }

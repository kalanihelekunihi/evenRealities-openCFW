#ifndef R1_NATIVE_KV_CLASS_H
#define R1_NATIVE_KV_CLASS_H
#include <stdint.h>
#include <stddef.h>
/* Cached-class and port views; storage bootstrap remains a separate gate. */
struct r1_kv_class_view {
    uint8_t reserved0[18];volatile uint16_t flags;
    volatile uint16_t payload_size;uint8_t reserved22[2];uint8_t payload[];
};
struct r1_kv_port_view {
    uint8_t reserved0[28];void (*volatile enter)(void);void (*volatile leave)(void);
};
_Static_assert(offsetof(struct r1_kv_class_view,flags)==18,"native dirty flags");
_Static_assert(offsetof(struct r1_kv_class_view,payload_size)==20,"native size");
_Static_assert(offsetof(struct r1_kv_class_view,payload)==24,"native cached data");
_Static_assert(offsetof(struct r1_kv_port_view,enter)==28 && offsetof(struct r1_kv_port_view,leave)==32,"native port critical-section callbacks");
extern struct r1_kv_port_view *volatile r1_kv_port;
#define R1_NV_HANDLE_COUNT 7u
extern void *volatile *const r1_nv_handle_owners[R1_NV_HANDLE_COUNT];
extern volatile uint16_t r1_nv_registered_class_count;
void r1_storage_manager_initialize_731a0(void);
uint32_t r1_nv_store_bootstrap_73220(void);
uint32_t r1_kv_class_read(void *,void *,uint32_t);
uint32_t r1_kv_class_write(void *,const void *,uint32_t);
#endif

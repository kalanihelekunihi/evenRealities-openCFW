#ifndef R1_NATIVE_KV_CLASS_H
#define R1_NATIVE_KV_CLASS_H
#include <stdint.h>
#include <stddef.h>
/* Read views only; complete allocation and port initialization remain gates. */
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
uint32_t r1_kv_class_read(void *,void *,uint32_t);
uint32_t r1_kv_class_write(void *,const void *,uint32_t);
#endif

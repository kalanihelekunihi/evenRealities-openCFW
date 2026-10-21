#ifndef CASE_EVENT_ABI_H
#define CASE_EVENT_ABI_H
/* Reconstructed ARM32 prefixes. No ownership transfer implied by a pointer field. */
#include <stdint.h>
#include <stddef.h>
#define CASE_EVENT_CLEAR_ON_EXIT 0x01000000u
#define CASE_EVENT_UNBLOCKED_BY_BITS 0x02000000u
#define CASE_EVENT_WAIT_ALL 0x04000000u
#define CASE_EVENT_VALUE_IN_USE 0x80000000u
#define CASE_EVENT_USER_BITS 0x00ffffffu
typedef struct case_event_item {
 uint32_t value;
 struct case_event_item *next,*previous;
 void *owner,*container;
} case_event_item;
typedef struct {
 uint32_t count;
 case_event_item *index;
 uint32_t sentinel_value;
 case_event_item *next,*previous;
} case_event_list;
typedef struct {
 uint32_t bits;
 case_event_list waiting;
 uint32_t unrecovered_word24;
 uint8_t static_allocated,padding[3];
} case_event_layout32;
typedef struct {
 uint32_t initial_word;
 case_event_item state_item,event_item;
 uint32_t priority;
} case_tcb_prefix48;
typedef struct {
 const char *name;
 uint32_t attribute_bits;
 void *control_memory;
 uint32_t control_size;
} case_event_attributes;
_Static_assert(sizeof(case_event_item)==20,"ARM32 item");
_Static_assert(sizeof(case_event_list)==20,"ARM32 list");
_Static_assert(sizeof(case_event_layout32)==32,"stock event allocation");
_Static_assert(offsetof(case_event_layout32,static_allocated)==28,"allocation marker");
_Static_assert(offsetof(case_tcb_prefix48,event_item)==24,"event item offset");
_Static_assert(offsetof(case_tcb_prefix48,priority)==44,"priority offset");
#endif

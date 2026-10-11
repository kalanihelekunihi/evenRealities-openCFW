#ifndef CASE_SCHEDULER_LIST_ABI_H
#define CASE_SCHEDULER_LIST_ABI_H
#include <stdint.h>
typedef struct case_item case_item;
typedef struct case_list case_list;
struct case_item { uint32_t value; case_item *next,*previous; void *owner; case_list *container; };
struct case_list {
    uint32_t count;
    case_item *index;
    struct { uint32_t value; case_item *next,*previous; } end;
};
typedef struct {
    uint32_t prefix;
    case_item state_item;
    case_item event_item;
    uint32_t priority;
} case_tcb;
_Static_assert(sizeof(case_list)==20,"FreeRTOS list ABI");
_Static_assert(__builtin_offsetof(case_tcb,state_item)==4,"state item");
_Static_assert(__builtin_offsetof(case_tcb,event_item)==24,"event item");
_Static_assert(__builtin_offsetof(case_tcb,priority)==44,"priority");
uint32_t case_source_list_remove(case_item *item);
void case_source_list_insert_end(case_list *list,case_item *item);
#endif

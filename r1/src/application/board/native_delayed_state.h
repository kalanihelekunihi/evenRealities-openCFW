#ifndef R1_NATIVE_DELAYED_STATE_H
#define R1_NATIVE_DELAYED_STATE_H
#include <stdint.h>
struct r1_delayed_queue_attr { const char *name;uint32_t bits;void *cb;uint32_t cb_size;void *storage;uint32_t storage_size; };
struct r1_delayed_thread_attr { const char *name;uint32_t bits;void *cb;uint32_t cb_size;void *stack;uint32_t stack_size;int32_t priority;uint32_t zone,reserved; };
struct r1_delayed_object_attr { const char *name;uint32_t bits;void *cb;uint32_t cb_size; };
extern volatile uint32_t r1_delayed_context[6];
extern const struct r1_delayed_queue_attr r1_delayed_queue_attributes;
extern const struct r1_delayed_thread_attr r1_delayed_thread_attributes;
extern const struct r1_delayed_object_attr r1_delayed_mutex_attributes,r1_delayed_timer_attributes;
#endif

#ifndef OPENCFW_DISPLAY_DRIVER_ATTRIBUTES_H
#define OPENCFW_DISPLAY_DRIVER_ATTRIBUTES_H
#include <stdint.h>

struct display_driver_thread_attrs {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
    void *stack_mem;
    uint32_t stack_size;
    uint32_t priority;
    uint32_t tz_module;
    uint32_t reserved;
};
struct display_driver_queue_attrs {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
    void *mq_mem;
    uint32_t mq_size;
};
extern const struct display_driver_thread_attrs audio_display_driver_thread_attrs;
extern struct display_driver_queue_attrs audio_display_driver_queue_attrs;
#endif

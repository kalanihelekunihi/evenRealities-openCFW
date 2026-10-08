/* Recovered ARM32 asynchronous IOM interfaces, not a device scheduling API. */
#ifndef OPENCFW_BOOT_CONTEXT_EVENTS_H
#define OPENCFW_BOOT_CONTEXT_EVENTS_H
#include <stdint.h>
/* 32-byte serialized record. First six words publish to these MMIO offsets;
 * callback/context words are CPU addresses, not host pointers or owned data. */
struct opencfw_iom_descriptor {
    uint32_t register_128,register_2c4,register_21c,register_220;
    uint32_t register_218,register_120,callback_address,callback_context;
};
struct opencfw_iom_cq_status {
    uint32_t completed_index,committed_index,end_index;
    uint8_t flag_1c,flag_24,flag_20,untouched_padding;
};
uint32_t opencfw_boot_iom_interrupt_status(void *,uint32_t,uint32_t *);
uint32_t opencfw_boot_iom_interrupt_clear(void *,uint32_t);
void opencfw_boot_iom4_irq_dispatch(void);
void opencfw_boot_iom_descriptor_publish(void *);
uint32_t opencfw_boot_iom_event_service(void *,uint32_t events);
uint32_t opencfw_boot_iom_error_classify(uint32_t module,uint32_t events);
void opencfw_boot_iom_event_apply(void *,uint32_t events);
void opencfw_boot_iom_cq_refresh_indices(void *);
uint32_t opencfw_boot_iom_cq_status(void *,void *status);
uint32_t opencfw_boot_iom_cq_resume(void *);
#endif

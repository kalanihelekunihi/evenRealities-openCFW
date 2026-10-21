/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPENCFW_WSF_RADIO_H
#define OPENCFW_WSF_RADIO_H
#include <stdint.h>
typedef void (*opencfw_wsf_handler_t)(uint32_t event,void *message);
/* Recovered stock64-byte control block; addresses/pointers are ARM32.
 * queue words remain owned by the external WSF queue provider. */
typedef struct {
    opencfw_wsf_handler_t handler[10];
    uint8_t handler_event[10],reserved_gap[2];
    uint32_t queue_head,queue_tail;
    uint8_t task_events,num_handlers,reserved_tail[2];
} opencfw_wsf_state_t;
/* Stock-effective8-bit event slots; ID low4bits selects slot without validation.
 * Valid initialized handler IDs0..9 only. ID10..15 aliases padding/queue bytes.
 * Masks truncate to8bits; zero still sets task-ready bit and requests wake.
 * Privileged balanced nesting required,0..254 before enter. Critical exit
 * enables IRQs at depth0 and DOES NOT restore prior PRIMASK.
 * Event bits coalesce; message ownership is separate. Dispatcher frees dequeued
 * messages after callback, not timer messages. All providers below need real
 * platform implementations beyond the callable simulator. */
void opencfw_wsf_cs_enter(void);
void opencfw_wsf_cs_exit(void);
void opencfw_wsf_wake(void);
void opencfw_wsf_set_event(uint32_t,uint32_t);
void opencfw_wsf_task_ready(uint32_t,uint32_t);
uint32_t opencfw_wsf_ready_to_sleep(void);
void opencfw_wsf_dispatch(void);
/* Opaque external-call ABI boundaries recovered from call sites; these are not
 * claimed to be complete FreeRTOS/CMSIS providers or published typedefs. */
uint32_t opencfw_wsf_context_is_isr(void);
int32_t opencfw_wsf_notify_isr(uint32_t,uint32_t,int32_t *);
int32_t opencfw_wsf_notify_task(uint32_t,uint32_t);
void opencfw_wsf_timer_update(void);
void *opencfw_wsf_msg_deq(void *,uint8_t *);
void opencfw_wsf_msg_free(void *);
void *opencfw_wsf_timer_expired(uint32_t);
void opencfw_wsf_wait(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
#endif

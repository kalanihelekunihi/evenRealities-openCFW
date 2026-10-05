/* SPDX-License-Identifier: Apache-2.0 */
/* Synthetic providers intercepted in verification, never production RTOS. */
#include "../../wsf_radio/wsf_radio.h"
uint32_t opencfw_wsf_context_is_isr(void){return 0;}
void opencfw_wsf_timer_update(void){}
void *opencfw_wsf_msg_deq(void *q,uint8_t *id){(void)q;(void)id;return (void *)0;}
void opencfw_wsf_msg_free(void *m){(void)m;}
void *opencfw_wsf_timer_expired(uint32_t x){(void)x;return (void *)0;}
void opencfw_wsf_wait(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;}
#include "../event_group.h"
void vTaskSuspendAll(void){}
BaseType_t xTaskResumeAll(void){return 0;}
void vTaskRemoveFromUnorderedEventList(ListItem_t *i,EventBits_t b){(void)i;(void)b;}
BaseType_t opencfw_event_queue_send_isr(void *q,const void *m,BaseType_t *w,BaseType_t pos){(void)q;(void)m;(void)w;(void)pos;return 0;}
void opencfw_event_group_assert_failure(void){for(;;){}}

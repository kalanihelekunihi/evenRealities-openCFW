/* SPDX-License-Identifier: Apache-2.0 */
/* Synthetic providers intercepted in verification, never production RTOS. */
#include "../wsf_radio.h"
uint32_t opencfw_wsf_context_is_isr(void){return 0;}
int32_t opencfw_wsf_notify_isr(uint32_t a,uint32_t b,int32_t *c){(void)a;(void)b;*c=0;return 0;}
int32_t opencfw_wsf_notify_task(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
void opencfw_wsf_timer_update(void){}
void *opencfw_wsf_msg_deq(void *q,uint8_t *id){(void)q;(void)id;return (void *)0;}
void opencfw_wsf_msg_free(void *m){(void)m;}
void *opencfw_wsf_timer_expired(uint32_t x){(void)x;return (void *)0;}
void opencfw_wsf_wait(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;}

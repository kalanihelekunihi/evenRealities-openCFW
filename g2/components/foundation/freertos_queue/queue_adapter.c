/* SPDX-License-Identifier: MIT */
#include "queue.h"
BaseType_t opencfw_event_queue_send_isr(void *q,const void *m,BaseType_t *w,BaseType_t p)
{return xQueueGenericSendFromISR(q,m,w,p);}
/* Reconstructed helpers: executable source, not retained opcode arrays. */
uint32_t opencfw_queue_mask_set(void)
{uint32_t saved;__asm__ volatile("mrs %0, basepri\nmov r1, #0x30\nmsr basepri, r1\ndsb sy\nisb sy":"=r"(saved)::"r1","memory");return saved;}
void opencfw_queue_mask_restore(uint32_t saved)
{__asm__ volatile("msr basepri, %0\ndsb sy\nisb sy"::"r"(saved):"memory");}
void *opencfw_queue_memcpy(void *dst,const void *src,uint32_t n)
{uint8_t *d=dst;const uint8_t *s=src;for(uint32_t i=0;i<n;i++)d[i]=s[i];return dst;}

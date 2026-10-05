/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_WSF_TIMER_STOP_H
#define OPENCFW_WSF_TIMER_STOP_H
#include <stdint.h>
/* Stock cancellation view. The two middle words and handler byte are retained
 * without assigning expiration/message units; stop only uses next/started.
 */
typedef struct wsfTimer_tag {
    struct wsfTimer_tag *pNext;
    uint32_t opaque4,opaque8;
    uint8_t opaque12,isStarted;
    uint8_t padding[2];
} wsfTimer_t;
typedef struct { void *pHead,*pTail; } wsfQueue_t;
void WsfQueueRemove(wsfQueue_t *,void *,void *);
void WsfTimerStop(wsfTimer_t *);
void WsfTaskLock(void);
void WsfTaskUnlock(void);
/* Private removal helper requires outer exclusion if used directly. */
void opencfw_wsf_timer_remove_raw(wsfTimer_t *);
/* Contiguous stock slice4b49d0..4b49e6; following state clearing/release excluded. */
void opencfw_radio_timer_gpio_shutdown_phase(void);
#endif

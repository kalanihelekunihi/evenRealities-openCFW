/* Stock 0x45547c / pinned FreeRTOS V10.5.1 unordered event-list removal.
 * Called only with scheduler suspended and a valid initialized waiter TCB. */
#include "../../foundation/freertos_ready/ready.h"
#include <stdint.h>

extern void audio_resume_next_unblock(void); /* stock 0x455876 */
extern void opencfw_event_group_assert_failure(void) __attribute__((noreturn));

static volatile uint32_t *const suspended=(volatile uint32_t *)(uintptr_t)0x20074a58u;
static volatile uint32_t *const top_ready=(volatile uint32_t *)(uintptr_t)0x20074a38u;
static volatile uint32_t *const yield_pending=(volatile uint32_t *)(uintptr_t)0x20074a44u;
static TCB_t *volatile *const current=(TCB_t *volatile *)(uintptr_t)0x20074a20u;
static List_t *const ready=(List_t *)(uintptr_t)0x2006a49cu;

void vTaskRemoveFromUnorderedEventList(ListItem_t *item,uint32_t value) {
    if(*suspended==0u || !item || !item->pvOwner)
        opencfw_event_group_assert_failure();
    item->xItemValue=value|0x80000000u;
    TCB_t *tcb=(TCB_t *)item->pvOwner;
    (void)uxListRemove(item);
    audio_resume_next_unblock();
    (void)uxListRemove(&tcb->xStateListItem);
    if(*top_ready<tcb->uxPriority) *top_ready=tcb->uxPriority;
    vListInsertEnd(&ready[tcb->uxPriority],&tcb->xStateListItem);
    if(tcb->uxPriority>(*current)->uxPriority) *yield_pending=1u;
}

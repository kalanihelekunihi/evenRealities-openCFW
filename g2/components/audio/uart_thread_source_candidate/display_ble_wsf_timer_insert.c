/* Native wsfTimerInsert 0x52a424, WsfQueueInsert 0x538c8c,
 * and WsfQueuePush 0x538c6e. */
#include <stdint.h>
extern uint32_t audio_wsf_timer_list[2]; /* live queue 0x200741b0 */
extern void WsfTaskLock(void); /* selected 0x52b8c8 */
extern void WsfTaskUnlock(void); /* selected 0x52b8d0 */
extern void audio_wsf_timer_remove(void *); /* selected 0x52a3fc */
extern void audio_wsf_cs_enter(void); /* selected */
extern void audio_wsf_cs_exit(void); /* selected */
extern void audio_wsf_queue_enqueue(void *,void *); /* selected 0x538c24 */

static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(void *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
void audio_wsf_queue_push(void *queue,void *element) {
    uint8_t *q=(uint8_t *)queue;
    audio_wsf_cs_enter();
    put(element,word(q));
    if(word(q)==0u)put(q+4u,(uint32_t)(uintptr_t)element);
    put(q,(uint32_t)(uintptr_t)element);
    audio_wsf_cs_exit();
}
void audio_wsf_queue_insert(void *queue,void *element,void *previous) {
    uint8_t *q=(uint8_t *)queue;
    audio_wsf_cs_enter();
    if(word(q)==0u || previous==(void *)(uintptr_t)word(q+4u))
        audio_wsf_queue_enqueue(queue,element);
    else if(previous==0)audio_wsf_queue_push(queue,element);
    else {
        put(element,word(previous));
        put(previous,(uint32_t)(uintptr_t)element);
    }
    audio_wsf_cs_exit();
}
void audio_ble_wsf_timer_insert(void *timer,uint32_t ticks) {
    uint8_t *t=(uint8_t *)timer;
    WsfTaskLock();
    if(t[0x0du]!=0u)audio_wsf_timer_remove(timer);
    t[0x0du]=1u;
    put(t+4u,ticks);
    uint32_t current=audio_wsf_timer_list[0];
    uint32_t previous=0u;
    while(current!=0u && word((void *)(uintptr_t)(current+4u))<=ticks) {
        previous=current;
        current=word((void *)(uintptr_t)current);
    }
    audio_wsf_queue_insert(audio_wsf_timer_list,timer,(void *)(uintptr_t)previous);
    WsfTaskUnlock();
}

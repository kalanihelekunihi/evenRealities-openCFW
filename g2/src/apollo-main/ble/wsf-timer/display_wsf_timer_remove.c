/* Native Cordio wsfTimerRemove 0x52a3fc and WsfQueueRemove 0x538cc8. */
#include <stdint.h>
extern uint32_t audio_wsf_timer_list[2]; /* live WSF timer queue 0x200741b0 */
extern void audio_wsf_cs_enter(void);
extern void audio_wsf_cs_exit(void);

extern void audio_wsf_queue_remove(void **queue,void *element,void *previous); /* opencfw U5: now provided by the Cordio unit */

/* Stock 0x0052A3FC (wsfTimerRemove) */
void audio_wsf_timer_remove(void *timer) {
    void *previous=0;
    void *current=(void *)(uintptr_t)audio_wsf_timer_list[0];
    while(current!=0 && current!=timer) {
        previous=current;
        current=*(void **)current;
    }
    if(current!=0) {
        audio_wsf_queue_remove((void **)audio_wsf_timer_list,timer,previous);
        ((uint8_t *)timer)[0x0du]=0u;
    }
}

/* SPDX-License-Identifier: MIT */
/* Instruction reconstruction through explicit provider cuts, not a whole task. */
#include "consumer.h"
#include "../audio_cache_handoff/handoff.h"
#include "../freertos_queue/queue.h"
#include "../freertos_daemon/daemon.h"
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_audio_scheduler_state(void)
{ if (!WORD(0x20074a3c)) return 1; return WORD(0x20074a58) ? 0 : 2; }
uint32_t opencfw_audio_irq_context(void)
{
    uint32_t r; __asm__ volatile("mrs %0, ipsr":"=r"(r));
    if (r) return 1;
    if (opencfw_audio_scheduler_state()==1) return 0;
    __asm__ volatile("mrs %0, primask":"=r"(r)); if (r) return 1;
    __asm__ volatile("mrs %0, basepri":"=r"(r)); return r!=0;
}
uint32_t opencfw_audio_tick(void)
{
    /* Both task and ISR stock providers read this same counter. Keep context
     * query so special-register/RAM access order follows the wrapper. */
    (void)opencfw_audio_irq_context(); return WORD(0x20074a34);
}
BaseType_t opencfw_daemon_scheduler_state(void)
{ return (BaseType_t)opencfw_audio_scheduler_state(); }
UBaseType_t uxTaskGetNumberOfTasks(void) { return WORD(0x20074a30); }
int32_t opencfw_audio_queue_put_isr(void *queue,const void *message)
{
    /* This function represents only the timeout=0 ISR branch of449abe. */
    if (!queue || !message) return -4;
    BaseType_t higher=0;
    if (xQueueGenericSendFromISR(queue,message,&higher,0)!=1) return -3;
    if (higher) WORD(0xe000ed04)=0x10000000;
    return 0;
}
int32_t opencfw_audio_queue_get_task_nowait(void *queue,void *message)
{
    /* Only the zero-timeout task branch of449b3c, no blocking/ISR receive. */
    if (!queue || !message) return -4;
    return opencfw_queue_receive_nowait(queue,message)==1 ? 0 : -3;
}
static void reset(opencfw_audio_cut_t *cut)
{ cut->disposition=AUDIO_RETURN;cut->mode=0;cut->pcm=0;cut->length=0;cut->callback=0;cut->age=0; }
void opencfw_audio_notify_prefix(opencfw_audio_cut_t *cut)
{
    reset(cut);
    opencfw_audio_message_t message={2,0,0}; message.tick=opencfw_audio_tick();
    uint32_t queue=WORD(0x20003f98+12);
    if (!queue) return;
    int32_t status=opencfw_audio_queue_put_isr((void *)(uintptr_t)queue,&message);
    cut->disposition=status ? AUDIO_QUEUE_LOG : AUDIO_WAKE;
    /* Stop before43d0ce logging or449238 thread-flags provider. */
    if (!status) cut->callback=WORD(0x20003f98+8);
}
void opencfw_pcm_dispatch_prefix(uint32_t mode,uint32_t pcm,uint32_t length,opencfw_audio_cut_t *cut)
{
    uint32_t selected=(uint8_t)mode;
    cut->mode=selected;cut->pcm=pcm;cut->length=length;cut->callback=0;cut->disposition=AUDIO_RETURN;
    if (selected>=2 || !pcm || !length) return;
    uintptr_t record=0x20073c20u+12u*selected;
    if (WORD(record+8) && *(volatile uint8_t *)(record+4)==selected) {
        /* Stock rereads callback before BLX; do not snapshot the first read. */
        cut->callback=WORD(record+8);cut->disposition=AUDIO_CALLBACK;return;
    }
    if (selected==0) cut->disposition=AUDIO_DSP; /* before57ae56 body setup */
}
void opencfw_audio_consume_prefix(const opencfw_audio_message_t *message,opencfw_audio_cut_t *cut)
{
    reset(cut);
    uint32_t tick=message->tick;
    cut->age=opencfw_audio_tick()-tick;
    if (cut->age>=41) {cut->disposition=AUDIO_STALE_LOG;return;}
    uint32_t pcm=0,length=0;
    (void)opencfw_audio_rx_buffer_get(&pcm,&length);
    WORD(0x20074a9c)=WORD(0x20074a9c)+1u;
    opencfw_pcm_dispatch_prefix(0,pcm,length,cut);
}

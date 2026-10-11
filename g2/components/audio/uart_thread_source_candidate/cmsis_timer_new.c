/* Native osTimerNew 0x4493b0 and TimerCallback 0x449398. */
#include <stdint.h>
struct timer_attributes {const char *name;uint32_t flags;void *control_block;uint32_t control_block_size;};
struct timer_context {void (*callback)(void *);void *argument;};
extern uint32_t audio_irq_context(void); /* selected 0x44900e */
extern void *pvPortMalloc(uint32_t); /* selected 0x456110 */
extern void vPortFree(void *); /* selected 0x456210 */
extern void *audio_freertos_timer_create_dynamic(const char *,uint32_t,uint32_t,
                                                  uintptr_t,void (*)(void *)); /* native 0x47e6dc */
extern void *audio_freertos_timer_create_static(const char *,uint32_t,uint32_t,
                                                 uintptr_t,void (*)(void *),void *); /* native 0x47e712 */
extern uintptr_t audio_freertos_timer_get_id(void *); /* native 0x47eb26 */
void audio_uart_timer_callback_dispatch(void *timer) {
    uintptr_t tagged=audio_freertos_timer_get_id(timer);
    struct timer_context *context=(struct timer_context *)(tagged&~(uintptr_t)1u);
    if(context!=0) context->callback(context->argument);
}
void *audio_uart_timer_new(void (*callback)(void *),uint32_t type,void *argument,
                           const struct timer_attributes *attrs) {
    if(audio_irq_context()!=0u||callback==0) return 0;
    struct timer_context *context=0;
    uint32_t allocated=0;
    if(attrs!=0&&attrs->control_block!=0&&attrs->control_block_size>=52u)
        context=(struct timer_context *)((uint8_t *)attrs->control_block+44u);
    if(context==0) {
        context=(struct timer_context *)pvPortMalloc(8u);
        if(context!=0) allocated=1;
    }
    if(context==0) return 0;
    context->callback=callback;
    context->argument=argument;
    uint32_t storage_mode=0;
    const char *name=0;
    if(attrs!=0) {
        name=attrs->name;
        if(attrs->control_block!=0&&attrs->control_block_size>=44u)
            storage_mode=1;
        else if(attrs->control_block!=0||attrs->control_block_size!=0)
            storage_mode=2; /* native skips both constructors */
    }
    uintptr_t id=(uintptr_t)context|allocated;
    void *timer=0;
    if(storage_mode==1)
        timer=audio_freertos_timer_create_static(name,1u,(uint8_t)type!=0u,id,
                                                audio_uart_timer_callback_dispatch,
                                                attrs->control_block);
    else if(storage_mode==0)
        timer=audio_freertos_timer_create_dynamic(name,1u,(uint8_t)type!=0u,id,
                                                 audio_uart_timer_callback_dispatch);
    if(timer==0&&allocated!=0)
        vPortFree((void *)((uintptr_t)context&~(uintptr_t)1u));
    return timer;
}

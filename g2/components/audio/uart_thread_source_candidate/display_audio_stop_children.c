/* Native audio stop event children 0x45f6da/0x45f840/0x45f6c0/0x45f6ec.
 * Events are delivered synchronously with a stack-local ID as in stock. */
#include <stdint.h>
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);

void audio_uart_display_audio_stop_all_45f6da(void *state,uint32_t unused)
{
    (void)unused;
    if (state!=0) {
        void *object=*(void **)((uint8_t *)state+24u);
        (void)audio_uart_lv_obj_event_451670(object,0x3du,0);
    }
}

void *audio_uart_display_audio_find_45f840(void *state,uint32_t id)
{
    if (state==0 || id==0u) return 0;
    for (uint32_t i=8u;i<=12u;i+=4u) {
        uint8_t *entry=*(uint8_t **)((uint8_t *)state+i);
        while (entry!=0) {
            if (*(uint32_t *)(void *)entry==id) return entry;
            entry=*(uint8_t **)(void *)(entry+32u);
        }
    }
    return 0;
}

uint32_t audio_uart_display_audio_stop_one_45f6c0(void *state,uint32_t id)
{
    uint32_t local=id;
    if (state!=0 && id!=0u) {
        void *object=*(void **)((uint8_t *)state+24u);
        (void)audio_uart_lv_obj_event_451670(object,0x3cu,&local);
    }
    return local;
}

uint32_t audio_uart_display_audio_stop_top_45f6ec(void *state,uint32_t id)
{
    uint32_t local=id;
    if (state!=0 && id!=0u) {
        void *object=*(void **)((uint8_t *)state+24u);
        (void)audio_uart_lv_obj_event_451670(object,0x3eu,&local);
    }
    return local;
}

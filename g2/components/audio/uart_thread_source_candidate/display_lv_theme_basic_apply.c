/* Native LV grid_update callback 0x48ca3c; child effects remain explicit. */
#include <stdint.h>

extern void audio_uart_lv_basic_state_init_48cad8(void *,void *);
extern void audio_uart_lv_basic_box_init_48c80e(void *,uint32_t);
extern int32_t audio_uart_lv_basic_x_48c920(void *,uint32_t);
extern int32_t audio_uart_lv_basic_y_48c94e(void *,uint32_t);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern void audio_uart_lv_basic_item_48cfe0(void *,void *,void *);
extern void audio_uart_lv_basic_state_done_48cbda(void *);
extern int32_t audio_uart_lv_basic_width_48c81a(void *,uint32_t);
extern int32_t audio_uart_lv_basic_height_48c824(void *,uint32_t);
extern uint32_t audio_uart_lv_basic_invalidate_43f1a4(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);

void audio_uart_lv_theme_basic_apply_48ca3c(void *object)
{
    uint8_t state[32];
    struct { uint8_t box[8]; int32_t x; int32_t y; } region;
    audio_uart_lv_basic_state_init_48cad8(object,state);
    audio_uart_lv_basic_box_init_48c80e(&region,0x10u);
    int32_t x=audio_uart_lv_basic_x_48c920(object,0u);
    int32_t y=audio_uart_lv_basic_y_48c94e(object,0u);
    region.x=*(int32_t *)((uint8_t *)object+0x14u)+x-audio_uart_lv_obj_x_44e486(object);
    region.y=*(int32_t *)((uint8_t *)object+0x18u)+y-audio_uart_lv_obj_y_44e498(object);
    uint8_t *children=*(uint8_t **)((uint8_t *)object+8u);
    uint32_t count=*(uint16_t *)(void *)(children+0x30u);
    uint32_t *items=*(uint32_t **)(void *)children;
    for(uint32_t i=0;i<count;i++)
        audio_uart_lv_basic_item_48cfe0((void *)(uintptr_t)items[i],state,&region);
    audio_uart_lv_basic_state_done_48cbda(state);
    int32_t w=audio_uart_lv_basic_width_48c81a(object,0u);
    int32_t h=audio_uart_lv_basic_height_48c824(object,0u);
    if(w==0x3fffffff || h==0x3fffffff)
        audio_uart_lv_basic_invalidate_43f1a4(object);
    (void)audio_uart_lv_obj_event_451670(object,0x33u,0);
}

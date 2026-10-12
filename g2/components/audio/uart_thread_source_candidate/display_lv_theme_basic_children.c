/* Native LV grid helpers at 0x48c80e..0x48c94e and object offsets. */
#include <stdint.h>

extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern int32_t audio_uart_lv_basic_x_base_48c84c(void *,uint32_t);
extern int32_t audio_uart_lv_basic_y_base_48c842(void *,uint32_t);
extern int32_t audio_uart_lv_basic_offset_48c892(void *,uint32_t);
extern uint32_t audio_uart_lv_basic_flags_48c89c(void *,uint32_t);

void audio_uart_lv_basic_box_init_48c80e(void *box,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(box,0u,size);
}
int32_t audio_uart_lv_basic_width_48c81a(void *object,uint32_t selector)
{
    return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,1u);
}
int32_t audio_uart_lv_basic_height_48c824(void *object,uint32_t selector)
{
    return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,2u);
}
void audio_uart_lv_basic_state_done_48cbda(void *state)
{
    void **entries=(void **)state;
    for(unsigned i=0;i<4u;i++) audio_uart_lv_heap_free(entries[i]);
}
int32_t audio_uart_lv_basic_x_48c920(void *object,uint32_t selector)
{
    int32_t base=audio_uart_lv_basic_x_base_48c84c(object,selector);
    int32_t offset=audio_uart_lv_basic_offset_48c892(object,selector);
    if(audio_uart_lv_basic_flags_48c89c(object,selector)&4u)
        base=(int32_t)((uint32_t)base+(uint32_t)offset);
    return base;
}
int32_t audio_uart_lv_basic_y_48c94e(void *object,uint32_t selector)
{
    int32_t base=audio_uart_lv_basic_y_base_48c842(object,selector);
    int32_t offset=audio_uart_lv_basic_offset_48c892(object,selector);
    if(audio_uart_lv_basic_flags_48c89c(object,selector)&2u)
        base=(int32_t)((uint32_t)base+(uint32_t)offset);
    return base;
}
int32_t audio_uart_lv_obj_x_44e486(void *object)
{
    uint8_t *parent=*(uint8_t **)((uint8_t *)object+8u);
    return parent ? -(int32_t)*(uint32_t *)(void *)(parent+0x20u) : 0;
}
int32_t audio_uart_lv_obj_y_44e498(void *object)
{
    uint8_t *parent=*(uint8_t **)((uint8_t *)object+8u);
    return parent ? -(int32_t)*(uint32_t *)(void *)(parent+0x24u) : 0;
}

/* Complete native454746..45475a: low-byte fill, length/fill reorder.
 * The native buffer provider43c0e4 is already selected source. */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
void audio_uart_lv_basic_box_clear_454746(void *box,uint32_t fill,uint32_t size)
{
    audio_uart_buffer_zero(box,size,(uint8_t)fill);
}

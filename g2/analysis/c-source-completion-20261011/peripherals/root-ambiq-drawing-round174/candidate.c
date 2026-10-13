#include <stdint.h>
extern void audio_uart_ambiq_area_copy_4c73c4(uint32_t *,const void *);
extern void audio_uart_ambiq_area_move_450bb2(uint32_t *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_ambiq_transform_area_488cda(uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,void *);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern void audio_uart_ambiq_buffer_invalidate_48abb8(void *,uint32_t *);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *,uint32_t *,uint32_t);
extern void audio_uart_ambiq_draw_fill_53dc38(void *,void *,void *);
extern void audio_uart_ambiq_draw_border_53df00(void *,void *,void *);
extern void audio_uart_ambiq_draw_triangle_53e728(void *,void *);
extern void audio_uart_ambiq_draw_line_53ecfc(void *,void *);
extern void audio_uart_ambiq_draw_arc_53f09c(void *,void *,void *);
extern void audio_uart_ambiq_draw_image_53f42a(void *,void *,void *);
extern void audio_uart_ambiq_draw_layer_53f400(void *,void *,void *);
extern void audio_uart_ambiq_set_resolution_4b0bea(uint32_t,uint32_t);
extern void audio_uart_ambiq_draw_label_53faa6(void *,void *,void *);
extern void audio_uart_ambiq_draw_box_shadow_540036(void *,void *,void *);
extern void audio_uart_ambiq_draw_mask_5409f0(void *,void *,void *);
extern void audio_uart_ambiq_submit_4b0c8a(uint32_t);
extern void audio_uart_ambiq_buffer_flush_48ab30(void *,uint32_t *);
/* Native4c7752..4c791a. Wrapped uint32 arithmetic; all input loads volatile.
 * Native type13 intentionally performs no drawing call before submit/flush. */
void audio_uart_ambiq_execute_drawing_4c7752(void *task) {
    volatile uint8_t *t=task;
    volatile uint32_t *layer=(void *)(uintptr_t)*(volatile uint32_t *)(t+72u);
    void *buffer=(void *)(uintptr_t)layer[0];
    uint32_t clip[4],area[4];
    (void)*(volatile uint32_t *)(t+76u);
    audio_uart_ambiq_area_copy_4c73c4(clip,(void *)(t+56u));
    uint32_t y=0u-layer[2],x=0u-layer[1];
    audio_uart_ambiq_area_move_450bb2(clip,x,y);
    audio_uart_ambiq_area_copy_4c73c4(area,(void *)(t+8u));
    if(t[4]==6u) {
        volatile uint32_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if(d[12]!=0u||d[13]!=256u||d[14]!=256u||d[16]!=0u||d[15]!=0u) {
            uint32_t w=audio_uart_lv_area_width_451598(area);
            uint32_t h=audio_uart_lv_area_height_4515a4(area);
            uint32_t sy=d[14],sx=d[13],rotation=d[12];
            audio_uart_ambiq_transform_area_488cda(area,w,h,rotation,sx,sy,(void *)(d+17));
            area[0]+=*(volatile uint32_t *)(t+8u);
            area[1]+=*(volatile uint32_t *)(t+12u);
            area[2]+=*(volatile uint32_t *)(t+8u);
            area[3]+=*(volatile uint32_t *)(t+12u);
        }
    }
    y=0u-layer[2];x=0u-layer[1];
    audio_uart_ambiq_area_move_450bb2(area,x,y);
    if(!audio_uart_lv_area_intersect_450bcc((int32_t *)area,(const int32_t *)area,(const int32_t *)clip))return;
    audio_uart_ambiq_buffer_invalidate_48abb8(buffer,area);
    if((uint8_t)audio_uart_ambiq_bind_buffer_4b092a(buffer,clip,0u)!=1u)return;
    switch(t[4]) {
    case 1:audio_uart_ambiq_draw_fill_53dc38(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 2:audio_uart_ambiq_draw_border_53df00(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 3:audio_uart_ambiq_draw_box_shadow_540036(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 5: {
        volatile uint32_t *b=buffer;
        uint32_t height=b[1]>>16,width=(uint16_t)b[1];
        audio_uart_ambiq_set_resolution_4b0bea(width,height);
        audio_uart_ambiq_draw_label_53faa6(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));
        break;
    }
    case 6:audio_uart_ambiq_draw_image_53f42a(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 7:audio_uart_ambiq_draw_layer_53f400(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 8:audio_uart_ambiq_draw_line_53ecfc(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u));break;
    case 9:audio_uart_ambiq_draw_arc_53f09c(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 10:audio_uart_ambiq_draw_triangle_53e728(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u));break;
    case 11:audio_uart_ambiq_draw_mask_5409f0(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    default:break;
    }
    audio_uart_ambiq_submit_4b0c8a(1u);
    audio_uart_ambiq_buffer_flush_48ab30(buffer,area);
}

/* Native Main 0x440dda transform and style driven scrollbar clipping.
 * The five style getters and 0x4513c8 retain their native ABIs as imports. */
#include <stdint.h>
extern int32_t audio_uart_lv_transform_angle_43ef2a(void *,uint32_t);
extern int32_t audio_uart_lv_transform_scale_x_43f07e(void *,uint32_t);
extern int32_t audio_uart_lv_transform_scale_y_43f08c(void *,uint32_t);
extern uint32_t audio_uart_lv_transform_pivot_x_43ef34(void *,uint32_t);
extern uint32_t audio_uart_lv_transform_pivot_y_43ef3e(void *,uint32_t);
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern int32_t audio_uart_lv_area_height_4515a4(const int32_t *);
extern void audio_uart_lv_transform_area_4513c8(int32_t *,uint32_t,int32_t,
                                                  int32_t,int32_t,const int32_t *,uint32_t);

static int32_t native_pivot(uint32_t style,int32_t extent) {
    uint32_t encoded=style&0x9fffffffu;
    if((style&0x60000000u)==0x20000000u && (int32_t)encoded<0x1fffffff) {
        int32_t factor=encoded<0x10000000u?(int32_t)encoded:
                       (int32_t)(0x0fffffffu-encoded);
        return (int32_t)(((int32_t)((uint32_t)extent*(uint32_t)factor))/100);
    }
    return (int32_t)style;
}

void audio_uart_lv_scrollbar_clip_child_440dda(void *object,int32_t *area,
                                                 uint32_t part,uint32_t reverse) {
    int32_t angle=audio_uart_lv_transform_angle_43ef2a(object,0u);
    int32_t sx=audio_uart_lv_transform_scale_x_43f07e(object,0u);
    int32_t sy=audio_uart_lv_transform_scale_y_43f08c(object,0u);
    if(sx==0)sx=1;
    if(sy==0)sy=1;
    if(angle==0 && sx==256 && sy==256)return;
    uint32_t px=audio_uart_lv_transform_pivot_x_43ef34(object,0u);
    uint32_t py=audio_uart_lv_transform_pivot_y_43ef3e(object,0u);
    int32_t pivot[2];
    pivot[0]=(int32_t)((uint32_t)native_pivot(px,audio_uart_lv_area_width_451598(
                          (const int32_t *)((const uint8_t *)object+0x14u)))+
                        *(const uint32_t *)((const uint8_t *)object+0x14u));
    pivot[1]=(int32_t)((uint32_t)native_pivot(py,audio_uart_lv_area_height_4515a4(
                          (const int32_t *)((const uint8_t *)object+0x14u)))+
                        *(const uint32_t *)((const uint8_t *)object+0x18u));
    uint32_t rev=(uint8_t)reverse!=0u;
    if(rev) {
        angle=(int32_t)(0u-(uint32_t)angle);
        sx=(int32_t)((int32_t)((uint32_t)sx+65535u)/sx);
        sy=(int32_t)((int32_t)((uint32_t)sy+65535u)/sy);
    }
    audio_uart_lv_transform_area_4513c8(area,part,angle,sx,sy,pivot,!rev);
}

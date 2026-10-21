/* Apollo single-point LV transform wrapper at native 0x4513ae. */
#include <stdint.h>
extern void audio_uart_lv_transform_area_4513c8(int32_t *,uint32_t,int32_t,
                                                 int32_t,int32_t,const int32_t *,
                                                 uint32_t);
void audio_uart_lv_transform_point_4513ae(int32_t *point,int32_t angle,
                                           uint32_t scale_x,uint32_t scale_y,
                                           const void *pivot,uint32_t flags) {
    audio_uart_lv_transform_area_4513c8(point,1u,angle,(int32_t)scale_x,
                                         (int32_t)scale_y,pivot,flags&0xffu);
}

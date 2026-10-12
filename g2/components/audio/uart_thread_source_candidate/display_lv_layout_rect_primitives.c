/* Native LV rectangle width/height setters and flex/grid 16-byte snapshots. */
#include <stdint.h>
void audio_uart_lv_rect_set_width_450b6c(void *rectangle,int32_t width)
{
    int32_t *r=(int32_t *)rectangle;
    r[2]=(int32_t)((uint32_t)r[0]+(uint32_t)width-1u);
}
void audio_uart_lv_rect_set_height_450b76(void *rectangle,int32_t height)
{
    int32_t *r=(int32_t *)rectangle;
    r[3]=(int32_t)((uint32_t)r[1]+(uint32_t)height-1u);
}
void audio_uart_lv_flex_rect_copy_48b8f8(void *destination,const void *source)
{
    uint32_t *d=(uint32_t *)destination;const uint32_t *s=(const uint32_t *)source;
    d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];
}
void audio_uart_lv_grid_box_copy_48c7fc(void *destination,const void *source)
{
    uint32_t *d=(uint32_t *)destination;const uint32_t *s=(const uint32_t *)source;
    d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];
}

/* Native LV display dimensions 0x44fa7e/0x44faa8 and 16-byte area
 * intersection/copy 0x450bcc/0x4530fc. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);

uint32_t audio_uart_lv_display_width_44fa7e(void *display) {
    if(display==0)display=audio_uart_display_default_get();
    if(display==0)return 0u;
    const uint8_t *d=(const uint8_t *)display;
    uint8_t rot=d[0x2fcu]&7u;
    return *(const uint32_t *)(const void *)(d+((rot==1u || rot==3u)?4u:0u));
}
uint32_t audio_uart_lv_display_height_44faa8(void *display) {
    if(display==0)display=audio_uart_display_default_get();
    if(display==0)return 0u;
    const uint8_t *d=(const uint8_t *)display;
    uint8_t rot=d[0x2fcu]&7u;
    return *(const uint32_t *)(const void *)(d+((rot==1u || rot==3u)?0u:4u));
}
uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *out,const int32_t *a,const int32_t *b) {
    out[0]=a[0]>b[0]?a[0]:b[0];
    out[1]=a[1]>b[1]?a[1]:b[1];
    out[2]=a[2]<b[2]?a[2]:b[2];
    out[3]=a[3]<b[3]?a[3]:b[3];
    return (uint32_t)(out[2]>=out[0] && out[3]>=out[1]);
}
void audio_uart_lv_area_copy_4530fc(int32_t *out,const int32_t *src) {
    out[0]=src[0];out[1]=src[1];out[2]=src[2];out[3]=src[3];
}

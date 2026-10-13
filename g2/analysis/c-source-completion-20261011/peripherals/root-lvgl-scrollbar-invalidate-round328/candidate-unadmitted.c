/* Complete native area size450b80..450b97 and scrollbar invalidate44f2ca..44f315.
 * Pinned Ambiq LVGL lv_area.c69-77 and lv_obj_scroll.c637-647.
 * Inclusive extents and product wrap modulo2^32; preserve repeated size reads. */
#include <stdint.h>
extern void audio_uart_lv_get_scrollbar_areas_44eb28(void *,int32_t *,int32_t *);
extern void audio_uart_display_invalidate_area(void *,const int32_t *);
uint32_t audio_uart_lv_area_size_450b80(const void *area)
{
 const volatile uint32_t *p=(const volatile uint32_t *)area;
 uint32_t x2=p[2];uint32_t x1=p[0];uint32_t width=x2-x1+1u;
 uint32_t y2=p[3];uint32_t y1=p[1];uint32_t height=y2-y1+1u;
 return height*width;
}
void audio_uart_lv_scrollbar_invalidate_44f2ca(void *object)
{
 int32_t horizontal[4],vertical[4];
 audio_uart_lv_get_scrollbar_areas_44eb28(object,horizontal,vertical);
 if(audio_uart_lv_area_size_450b80(horizontal)==0u && audio_uart_lv_area_size_450b80(vertical)==0u)return;
 if(audio_uart_lv_area_size_450b80(horizontal)!=0u)audio_uart_display_invalidate_area(object,horizontal);
 if(audio_uart_lv_area_size_450b80(vertical)!=0u)audio_uart_display_invalidate_area(object,vertical);
}

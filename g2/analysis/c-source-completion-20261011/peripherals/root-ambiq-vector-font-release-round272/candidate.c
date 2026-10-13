#include <stdint.h>
extern void audio_uart_ambiq_get_path_buffers_5fa21c(void *,uint32_t *,uint32_t *,void **,void **);
extern void audio_uart_nema_vg_path_destroy_514d98(void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char release272_null[]="NULL pointer";
static const char release272_expression[]="outline != NULL";
static const char release272_message[]="Asserted at expression: %s (%s)";
static const char release272_function[]="lv_ambiq_ft_outline_destroy";
static const char release272_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
/* Native53db3c..53dbd8: fresh glyph loads bracket buffer and path release calls. */
void audio_uart_ambiq_vector_font_release_53db3c(void *cell) {
 volatile uint32_t *glyph=cell;
 if(!glyph) {
  audio_uart_lvgl_log(3u,release272_file,312u,release272_function,release272_message,release272_expression,release272_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t segment_size,data_size;void *segments,*data;
 if(glyph[0]!=0u) {
  audio_uart_ambiq_get_path_buffers_5fa21c((void *)(uintptr_t)glyph[0],&segment_size,&data_size,&segments,&data);
  audio_uart_lv_heap_free(data);audio_uart_lv_heap_free(segments);
 }
 if(glyph[1]!=0u) {
  audio_uart_ambiq_get_path_buffers_5fa21c((void *)(uintptr_t)glyph[1],&segment_size,&data_size,&segments,&data);
  audio_uart_lv_heap_free(data);audio_uart_lv_heap_free(segments);
 }
 if(glyph[0]!=0u) {
  audio_uart_nema_vg_path_destroy_514d98((void *)(uintptr_t)glyph[0]);glyph[0]=0u;
 }
 if(glyph[1]!=0u) {
  audio_uart_nema_vg_path_destroy_514d98((void *)(uintptr_t)glyph[1]);glyph[1]=0u;
 }
 audio_uart_lv_heap_free((void *)glyph);
}

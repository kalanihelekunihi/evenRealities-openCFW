#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void *audio_uart_display_surface_alloc(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char stencil263_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char stencil263_message[]="Failed to create stencil buffer!";
static const char stencil263_function[]="lv_draw_ambiq_stencil_buffer_adjust";
/* Native4b0b5a..4b0bea: cached unit, fresh framebuffer loads after children. */
uint32_t audio_uart_ambiq_stencil_adjust_4b0b5a(void *cell,uint32_t width,uint32_t height) {
 volatile uint32_t *unit=cell;
 if(!unit)unit=audio_uart_ambiq_default_unit_4c791a();
 void *buffer=(void *)(uintptr_t)unit[16];
 if(buffer) {
  const volatile uint32_t *header=buffer;
  if((uint32_t)(uint16_t)header[1]==width && (header[1]>>16u)==height)return 1u;
 }
 if(!buffer)unit[16]=(uint32_t)(uintptr_t)audio_uart_display_surface_alloc(width,height,14u,0u);
 else {
  void *reshaped=audio_uart_lv_draw_buf_reshape_48b196(buffer,14u,width,height,0u);
  if(!reshaped) {
   audio_uart_font_bitmap_release((void *)(uintptr_t)unit[16]);
   unit[16]=(uint32_t)(uintptr_t)audio_uart_display_surface_alloc(width,height,14u,0u);
  } else unit[16]=(uint32_t)(uintptr_t)reshaped;
 }
 if(unit[16]!=0u)return 1u;
 audio_uart_lvgl_log(3u,stencil263_file,482u,stencil263_function,stencil263_message);
 return 0u;
}

#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void audio_uart_nema_vg_path_reset_514e50(void *);
extern void audio_uart_nema_vg_paint_reset_515048(void *);
extern void audio_uart_nema_vg_state_reset_515676(void);
extern void audio_uart_ambiq_blend_clear_4b075e(void *);
extern uint32_t audio_uart_ambiq_stencil_adjust_4b0b5a(void *,uint32_t,uint32_t);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
typedef struct {uint32_t words[4];} audio_uart_vg_framebuffer_264;
extern void audio_uart_nema_vg_set_framebuffer_5223a2(uint32_t,uint32_t,audio_uart_vg_framebuffer_264);
static const char resolution264_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char resolution264_message[]="Failed to adjust stencil buffer!";
static const char resolution264_function[]="lv_draw_ambiq_vg_start";
/* Native4b0bea..4b0c8a: cached unit, wrapped alignment and by-value descriptor. */
void audio_uart_ambiq_set_resolution_4b0bea(uint32_t width,uint32_t height) {
 volatile uint32_t *unit=audio_uart_ambiq_default_unit_4c791a();
 audio_uart_nema_vg_path_reset_514e50((void *)(uintptr_t)unit[17]);
 audio_uart_nema_vg_paint_reset_515048((void *)(uintptr_t)unit[18]);
 audio_uart_nema_vg_state_reset_515676();
 audio_uart_ambiq_blend_clear_4b075e((void *)unit);
 width=(width+3u)&~3u;height=(height+3u)&~3u;
 uint32_t status=audio_uart_ambiq_stencil_adjust_4b0b5a((void *)unit,width,height);
 if((uint8_t)status!=1u) {
  audio_uart_lvgl_log(3u,resolution264_file,509u,resolution264_function,resolution264_message);
  return;
 }
 audio_uart_vg_framebuffer_264 framebuffer;
 audio_uart_lv_memzero_48949c(&framebuffer,16u);
 framebuffer.words[0]=((volatile uint32_t *)(uintptr_t)unit[16])[3];
 framebuffer.words[2]=((volatile uint32_t *)(uintptr_t)unit[16])[4];
 framebuffer.words[3]=((volatile uint32_t *)(uintptr_t)unit[16])[4];
 audio_uart_nema_vg_set_framebuffer_5223a2(width,height,framebuffer);
}

#include <stdint.h>
extern uint32_t audio_uart_lv_array_push_488506(void *,const void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
static const char pair288_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char pair288_function[]="lv_ambiq_ft_data_array_push";
static const char pair288_format[]="Asserted at expression: %s";
static const char pair288_expression[]="res == LV_RESULT_OK";
static void pair288_fail(uint32_t line) {
 audio_uart_lvgl_log(3u,pair288_file,line,pair288_function,pair288_format,pair288_expression);
 for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native53d87c..53d8fc: both float conversions precede the first append. */
void audio_uart_ambiq_vector_data_pair_53d87c(uint32_t x,uint32_t y) {
 volatile float x_float=(float)(int32_t)x;
 volatile float y_float=(float)(int32_t)y;
 uint32_t result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_data_20073cd4,(const void *)&x_float);
 if((uint8_t)result!=1u)pair288_fail(199u);
 result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_data_20073cd4,(const void *)&y_float);
 if((uint8_t)result!=1u)pair288_fail(202u);
}

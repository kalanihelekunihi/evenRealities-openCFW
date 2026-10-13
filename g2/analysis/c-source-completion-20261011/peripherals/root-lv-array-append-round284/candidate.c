#include <stdint.h>
extern uint32_t audio_uart_lv_array_resize_48849c(void *,uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char append284_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char append284_function[]="lv_array_push_back";
static const char append284_format[]="Asserted at expression: %s (%s)";
static const char append284_expression[]="array->data != NULL";
static const char append284_null[]="NULL pointer";
/* Native4883f0..4883fc: consumed void zero-fill wrapper. */
void audio_uart_lv_array_zero_4883f0(void *destination,uint32_t size) {
 audio_uart_lv_basic_box_clear_454746(destination,0u,size);
}
/* Native488506..488578: equality gate, full result, fresh descriptor loads. */
uint32_t audio_uart_lv_array_push_488506(void *array,const void *source) {
 volatile uint32_t *a=array;
 if(a[0]==0u) {
  audio_uart_lvgl_log(3u,append284_file,176u,append284_function,append284_format,append284_expression,append284_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t count=a[1];uint32_t capacity=a[2];
 if(count==capacity) {
  uint32_t wanted=a[2]+4u;
  if(audio_uart_lv_array_resize_48849c(array,wanted)==0u)return 0u;
 }
 uint32_t data=a[0];count=a[1];uint32_t stride=a[3];
 void *destination=(void *)(uintptr_t)(data+count*stride);
 if(source)(void)audio_uart_lv_grid_copy_454738(destination,source,a[3]);
 else audio_uart_lv_array_zero_4883f0(destination,a[3]);
 a[1]=a[1]+1u;
 return 1u;
}

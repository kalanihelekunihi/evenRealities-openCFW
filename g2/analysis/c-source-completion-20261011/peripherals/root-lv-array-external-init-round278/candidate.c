#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char array278_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char array278_function[]="lv_array_init_from_buf";
static const char array278_format[]="Asserted at expression: %s (%s)";
static const char array278_expression[]="buf != NULL";
static const char array278_null[]="NULL pointer";
/* Native488440..488478: external buffer initialization with ordered sparse stores. */
void audio_uart_lv_array_init_external_488440(void *array,void *buffer,uint32_t count,uint32_t stride) {
 if(!buffer) {
  audio_uart_lvgl_log(3u,array278_file,51u,array278_function,array278_format,array278_expression,array278_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 volatile uint32_t *a=array;
 a[1]=0u;a[2]=count;a[3]=stride;a[0]=(uint32_t)(uintptr_t)buffer;
 ((volatile uint8_t *)array)[16]=0u;
}

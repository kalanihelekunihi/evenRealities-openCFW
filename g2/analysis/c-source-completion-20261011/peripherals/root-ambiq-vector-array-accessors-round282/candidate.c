#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char access282_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char access282_function[]="lv_array_at";
static const char access282_format[]="Asserted at expression: %s (%s)";
static const char access282_expression[]="array->data != NULL";
static const char access282_null[]="NULL pointer";
/* Native488578..4885b8: count gate precedes data assertion and fresh pointer reload. */
void *audio_uart_lv_array_item_488578(void *array,uint32_t index) {
 const volatile uint32_t *a=array;
 if(index>=a[1])return 0;
 if(a[0]==0u) {
  audio_uart_lvgl_log(3u,access282_file,202u,access282_function,access282_format,access282_expression,access282_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t data=a[0];uint32_t stride=a[3];
 return (void *)(uintptr_t)(data+index*stride);
}
/* Native53d6cc..53d6d0: count only. */
uint32_t audio_uart_ambiq_vector_array_count_53d6cc(void *array) {
 return ((const volatile uint32_t *)array)[1];
}
/* Native53d6d0..53d6da: actual indexed-item contract at zero. */
void *audio_uart_ambiq_vector_array_front_53d6d0(void *array) {
 return audio_uart_lv_array_item_488578(array,0u);
}

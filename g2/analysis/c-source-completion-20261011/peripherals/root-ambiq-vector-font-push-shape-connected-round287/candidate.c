#include <stdint.h>
extern uint32_t audio_uart_lv_array_push_488506(void *,const void *);
extern void audio_uart_ambiq_vector_data_pair_53d87c(uint32_t,uint32_t);
extern void *audio_uart_ambiq_vector_array_front_53d6d0(void *);
extern uint32_t audio_uart_ambiq_vector_array_count_53d6cc(void *);
extern void audio_uart_nema_vg_path_shape_514f3c(void *,uint32_t,void *,uint32_t,void *);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern volatile uint32_t audio_uart_ambiq_vector_current_path_200746c4;
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
extern uint8_t audio_uart_ambiq_vector_path_segments_20073cc0[];
static const char push281_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char push281_function[]="lv_ambiq_ft_outline_push";
static const char push281_null[]="NULL pointer";
static const char push281_outline[]="outline != NULL";
static const char push281_assertfull[]="Asserted at expression: %s (%s)";
static const char push281_result[]="res == LV_RESULT_OK";
static const char push281_assert[]="Asserted at expression: %s";
static const char push281_unknown[]="unknown point type: %d";
/* Native53d8fc..53da50: command mapping and post-child segment reloads. */
void audio_uart_ambiq_vector_font_push_53d8fc(void *parameter) {
 volatile uint32_t *p=parameter;
 volatile uint32_t *outline=(void *)(uintptr_t)p[0];
 if(!outline) {
  audio_uart_lvgl_log(3u,push281_file,209u,push281_function,push281_assertfull,push281_outline,push281_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 volatile uint8_t segment=0u;
 uint32_t type=((volatile uint8_t *)parameter)[4];
 switch(type) {
 case 0:segment=0;break;case 1:segment=1;break;case 2:segment=2;break;
 case 3:segment=6;break;case 4:segment=5;break;case 5:segment=0;break;
 default:audio_uart_lvgl_log(3u,push281_file,235u,push281_function,push281_unknown,type);break;
 }
 uint32_t result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_segments_20073cc0,(const void *)&segment);
 if((uint8_t)result!=1u) {
  audio_uart_lvgl_log(3u,push281_file,240u,push281_function,push281_assert,push281_result);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 if(segment==6u || segment==5u) {
  uint32_t y=p[5];uint32_t x=p[4];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(segment==6u) {
  uint32_t y=p[7];uint32_t x=p[6];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(segment!=0u) {
  uint32_t y=p[3];uint32_t x=p[2];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(type==0u || type==5u) {
  void *data=audio_uart_ambiq_vector_array_front_53d6d0(audio_uart_ambiq_vector_path_data_20073cd4);
  uint32_t data_count=audio_uart_ambiq_vector_array_count_53d6cc(audio_uart_ambiq_vector_path_data_20073cd4);
  void *segments=audio_uart_ambiq_vector_array_front_53d6d0(audio_uart_ambiq_vector_path_segments_20073cc0);
  uint32_t segment_count=audio_uart_ambiq_vector_array_count_53d6cc(audio_uart_ambiq_vector_path_segments_20073cc0);
  audio_uart_nema_vg_path_shape_514f3c((void *)(uintptr_t)audio_uart_ambiq_vector_current_path_200746c4,segment_count,segments,data_count,data);
 }
 if(type==5u) {
  outline[1]=(uint32_t)(uintptr_t)audio_uart_nema_vg_path_create_514ebc();
  audio_uart_ambiq_vector_current_path_200746c4=outline[1];
 }
}

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

#include <stdint.h>
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_vg_path_process_561c68(void *);
/* Native514f3c..514f60: ordered shape stores precede genuine postprocessor. */
void audio_uart_nema_vg_path_shape_514f3c(void *path,uint32_t segment_count,void *segments,uint32_t data_count,void *data) {
 if(!path){audio_uart_nema_vg_set_error_51565c(1u);return;}
 volatile uint32_t *p=path;
 p[2]=(uint32_t)(uintptr_t)segments;p[3]=(uint32_t)(uintptr_t)data;
 p[0]=segment_count;p[1]=data_count;
 audio_uart_nema_vg_path_process_561c68(path);
}

extern volatile uint32_t audio_uart_nema_vg_context_cell;
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}

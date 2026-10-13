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

#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void audio_uart_lv_array_clear_488478(void *);
extern void audio_uart_lv_array_init_external_488440(void *,void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern volatile uint32_t audio_uart_ambiq_vector_current_path_200746c4;
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
extern uint8_t audio_uart_ambiq_vector_path_segments_20073cc0[];
static const char alloc277_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char alloc277_function[]="lv_ambiq_ft_outline_alloc";
static const char alloc277_format[]="Asserted at expression: %s (%s)";
static const char alloc277_memory[]="Out of memory";
static const char alloc277_outline[]="outline != NULL";
static const char alloc277_data[]="data != NULL";
static const char alloc277_segments[]="seg != NULL";
static void alloc277_fail(uint32_t line,const char *expression) {
 audio_uart_lvgl_log(3u,alloc277_file,line,alloc277_function,alloc277_format,expression,alloc277_memory);
 for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native53da54..53db3c: allocator failure is native diagnostic/fail-stop. */
void audio_uart_ambiq_vector_font_allocate_53da54(void *parameter) {
 volatile uint32_t *p=parameter;
 if(p[0]==0u) {
  volatile uint32_t *outline=audio_uart_lv_malloc(8u);
  if(!outline)alloc277_fail(281u,alloc277_outline);
  outline[0]=(uint32_t)(uintptr_t)audio_uart_nema_vg_path_create_514ebc();outline[1]=0u;
  p[0]=(uint32_t)(uintptr_t)outline;
  audio_uart_ambiq_vector_current_path_200746c4=outline[0];
 }
 audio_uart_lv_array_clear_488478(audio_uart_ambiq_vector_path_data_20073cd4);
 audio_uart_lv_array_clear_488478(audio_uart_ambiq_vector_path_segments_20073cc0);
 uint32_t data_size=p[9];uint32_t segment_size=p[8]+1u;
 void *data=audio_uart_lv_malloc(data_size<<2);
 if(!data)alloc277_fail(297u,alloc277_data);
 void *segments=audio_uart_lv_malloc(segment_size);
 if(!segments)alloc277_fail(299u,alloc277_segments);
 audio_uart_lv_array_init_external_488440(audio_uart_ambiq_vector_path_data_20073cd4,data,data_size,4u);
 audio_uart_lv_array_init_external_488440(audio_uart_ambiq_vector_path_segments_20073cc0,segments,segment_size,1u);
}

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

extern void audio_uart_lv_heap_free(void *);
void audio_uart_lv_array_clear_488478(void *array) {
    volatile uint8_t *a=array;
    volatile uint32_t *words=array;
    if(words[0]!=0u) {
        if(a[16u]!=0u)audio_uart_lv_heap_free((void *)(uintptr_t)words[0]);
        words[0]=0u;
    }
    words[1]=0u;words[2]=0u;
}

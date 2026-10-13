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

#include <stdint.h>
/* Native5fa21c..5fa236: sequential volatile accesses preserve output/path aliases. */
void audio_uart_ambiq_get_path_buffers_5fa21c(void *path,uint32_t *segment_size,uint32_t *data_size,void **segments,void **data) {
 const volatile uint32_t *p=path;
 *(volatile uint32_t *)segment_size=p[0];
 *(volatile uint32_t *)data_size=p[1];
 *(volatile uint32_t *)(void *)segments=p[2];
 *(volatile uint32_t *)(void *)data=p[3];
}

#include <stdint.h>
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
/* Native514d98..514e0a: reset then release; NULL error bypasses both. */
void audio_uart_nema_vg_path_destroy_514d98(void *cell) {
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)((uint32_t)(uintptr_t)cell+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
 audio_uart_nema_cl_node_release_514178(cell);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_context_cell;
extern void audio_uart_lv_pool_free_48429e(void *,void *);
void audio_uart_nema_matrix_identity_561810(void *cell) {
 volatile uint32_t *matrix=cell;
 matrix[0]=0x3f800000u;matrix[1]=0;matrix[2]=0;matrix[3]=0;
 matrix[4]=0x3f800000u;matrix[5]=0;matrix[6]=0;matrix[7]=0;matrix[8]=0x3f800000u;
}
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}
void audio_uart_nema_cl_node_release_514178(void *node) {
    audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000338u,node);
}
#include <stdint.h>
extern volatile uint32_t audio_uart_ambiq_unit_cell[]; /* RAM200746c0 */
extern void audio_uart_ambiq_buffer_handlers_53d5da(void);
extern void *audio_uart_lv_draw_unit_create_484398(uint32_t);
extern void audio_uart_ambiq_dispatch_4c76a8(void);
extern void audio_uart_ambiq_evaluate_4c7548(void);
extern void audio_uart_ambiq_delete_4c74f0(void);
extern void audio_uart_ambiq_render_thread_4c7700(void);
extern void *audio_uart_display_surface_alloc(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void *audio_uart_nema_vg_paint_create_515096(void);
extern void *audio_uart_nema_vg_grad_create_51510e(void);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* Native hidden structure-return ABI: caller supplies60-byte result inR0. */
extern void audio_uart_nema_cl_create_sized_514278(void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern void audio_uart_ambiq_vector_font_init_53d6da(void *);
extern uint32_t audio_uart_lv_async_init_4d465c(void *);
extern uint32_t audio_uart_lv_thread_init_4d4610(void *,const char *,uint32_t,void (*)(void),uint32_t,void *);
static const char ambiq_name[]="AMBIQ";
static const char ambiq_reason[]="NULL pointer";
static const char ambiq_expression[]="draw_ambiq_unit->cl.bo.base_virt != NULL";
static const char ambiq_format[]="Asserted at expression: %s (%s)";
static const char ambiq_function[]="lv_draw_ambiq_init";
static const char ambiq_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq.c";
static const char ambiq_thread[]="ambiqdraw";
static volatile uint32_t *ambiq_unit(void) {
    return (volatile uint32_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
}
/* Full native4c73d6..4c74ee; legacy group name retained for existing caller. */
void audio_uart_lv_init_group_4c73d6(void) {
    audio_uart_ambiq_buffer_handlers_53d5da();
    audio_uart_ambiq_unit_cell[0]=(uint32_t)(uintptr_t)audio_uart_lv_draw_unit_create_484398(228u);
    ambiq_unit()[3]=(uint32_t)(uintptr_t)audio_uart_ambiq_dispatch_4c76a8;
    ambiq_unit()[4]=(uint32_t)(uintptr_t)audio_uart_ambiq_evaluate_4c7548;
    ambiq_unit()[6]=(uint32_t)(uintptr_t)audio_uart_ambiq_delete_4c74f0;
    ambiq_unit()[1]=(uint32_t)(uintptr_t)ambiq_name;
    void *texture=audio_uart_display_surface_alloc(64u,1u,16u,0u);
    ambiq_unit()[15]=(uint32_t)(uintptr_t)texture;
    ambiq_unit()[16]=0u;
    void *path=audio_uart_nema_vg_path_create_514ebc();ambiq_unit()[17]=(uint32_t)(uintptr_t)path;
    void *paint=audio_uart_nema_vg_paint_create_515096();ambiq_unit()[18]=(uint32_t)(uintptr_t)paint;
    void *grad=audio_uart_nema_vg_grad_create_51510e();ambiq_unit()[19]=(uint32_t)(uintptr_t)grad;
    ambiq_unit()[20]=0u;
    ((volatile uint8_t *)ambiq_unit())[84]=255u;
    ((volatile uint8_t *)ambiq_unit())[85]=255u;
    ((volatile uint8_t *)ambiq_unit())[86]=255u;
    audio_uart_lv_basic_box_clear_454746((uint8_t *)ambiq_unit()+88u,0u,28u);
    audio_uart_lv_basic_box_clear_454746((uint8_t *)ambiq_unit()+116u,0u,16u);
    uint32_t command_list[15];
    audio_uart_nema_cl_create_sized_514278(command_list,102400u);
    audio_uart_checksum_copy((uint8_t *)ambiq_unit()+144u,command_list,60u);
    if(ambiq_unit()[38]==0u) {
        audio_uart_lvgl_log(3u,ambiq_path,87u,ambiq_function,ambiq_format,ambiq_expression,ambiq_reason);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    ambiq_unit()[35]=0u;
    audio_uart_ambiq_vector_font_init_53d6da((void *)ambiq_unit());
    (void)audio_uart_lv_async_init_4d465c((uint8_t *)ambiq_unit()+132u);
    void *unit=(void *)ambiq_unit();
    (void)audio_uart_lv_thread_init_4d4610((uint8_t *)unit+44u,ambiq_thread,40u,audio_uart_ambiq_render_thread_4c7700,32768u,unit);
}

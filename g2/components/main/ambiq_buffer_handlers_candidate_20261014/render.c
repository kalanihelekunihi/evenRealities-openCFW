/* Apollo S200 Ambiq buffer copy/render path at 0x53d25a. */
#include <stdint.h>

extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *,const void *,
                                                     uint32_t);
extern uint32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t);
extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,
                                              uint32_t,uint32_t,uint32_t,
                                              uint32_t);
extern void display_driver_gpu_mode_lower_4b06c0(uint32_t,uint32_t,uint32_t,
                                                    uint32_t,uint32_t,uint32_t);
extern void audio_uart_ambiq_buffer_draw_4b1b0e(int32_t,int32_t,uint32_t,
                                                   uint32_t,int32_t,int32_t);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_ambiq_clip_change_4b077e(uint32_t,const int32_t *,
                                                  uint32_t);
extern void display_driver_gpu_position_4b1b48(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char render_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_buffer.c";
static const char render_function[] = "lv_draw_ambiq_buffer_copy";
static const char format_expression[] =
    "dest->header.cf == src->header.cf";
static const char format_message[] =
    "Asserted at expression: %s Color format mismatch: %d != %d";
static const char asserted_message[] = "Asserted at expression: %s (%s)";
static const char area_expression[] =
    "((line_width_src == line_width_dest) && (line_hight_src == line_hight_dest))";
static const char area_message[] =
    "Source and destination areas have different width and hight";
static const char unreachable_expression[] = "false";
static const char unreachable_message[] = "Should never come to this!";

static void render_fault(uint32_t line,const char *expression,
                         const char *message,uint32_t a,uint32_t b) {
    if (line == 0xb5u)
        audio_uart_lvgl_log(3u,render_path,line,render_function,
                            message,expression,a,b);
    else
        audio_uart_lvgl_log(3u,render_path,line,render_function,
                            asserted_message,expression,message);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_ambiq_buffer_render_53d25a(
        uint32_t *dest,const int32_t *dest_clip,
        const uint32_t *src,const int32_t *src_clip) {
    const uint32_t dest_format = (dest[0] >> 8) & 0xffu;
    const uint32_t src_format = (src[0] >> 8) & 0xffu;
    if (dest_format != src_format)
        render_fault(0xb5u,format_expression,format_message,
                     dest_format,src_format);

    const uint32_t dest_width = dest_clip == 0 ?
        (dest[1] & 0xffffu) : audio_uart_lv_area_width_451598(dest_clip);
    const uint32_t dest_height = dest_clip == 0 ?
        (dest[1] >> 16) : audio_uart_lv_area_height_4515a4(dest_clip);
    const int32_t dest_x = dest_clip == 0 ? 0 : dest_clip[0];
    const int32_t dest_y = dest_clip == 0 ? 0 : dest_clip[1];
    const uint32_t src_width = src_clip == 0 ?
        (src[1] & 0xffffu) : audio_uart_lv_area_width_451598(src_clip);
    const uint32_t src_height = src_clip == 0 ?
        (src[1] >> 16) : audio_uart_lv_area_height_4515a4(src_clip);
    const int32_t src_x = src_clip == 0 ? 0 : src_clip[0];
    const int32_t src_y = src_clip == 0 ? 0 : src_clip[1];
    if (dest_width != src_width || dest_height != src_height)
        render_fault(0xddu,area_expression,area_message,0u,0u);
    if ((audio_uart_ambiq_bind_buffer_4b092a(dest,dest_clip,1u)
         & 0xffu) != 1u)
        return;

    const uint32_t palette_width = src_format == 7u ? 2u :
        src_format == 8u ? 4u : src_format == 9u ? 16u :
        src_format == 10u ? 256u : 0u;
    const uint32_t texture_format =
        audio_uart_ambiq_color_format_src_4b05a4(src_format);
    const uint32_t src_address = src[4] +
        (src_format >= 7u && src_format <= 10u ?
         palette_width * 4u : 0u);
    audio_uart_nema_bind_tex_4b1298(1u,src_address,
        src[1] & 0xffffu,src[1] >> 16,texture_format,
        src[2] & 0xffffu,0u);
    display_driver_gpu_mode_lower_4b06c0(
        0u,1u,0u,1u,UINT32_MAX,0u);
    audio_uart_ambiq_buffer_draw_4b1b0e(
        dest_x,dest_y,src_width,src_height,src_x,src_y);

    if (dest_format == 0x14u) {
        const uint32_t dw = dest[1] & 0xffffu;
        const uint32_t dh = dest[1] >> 16;
        audio_uart_nema_bind_tex_4b1298(2u,
            dest[4] + dw * dh * 2u,dw,dh,8u,
            (dest[2] & 0xffffu) / 2u,0u);
        const uint32_t sw = src[1] & 0xffffu;
        const uint32_t sh = src[1] >> 16;
        audio_uart_nema_bind_tex_4b1298(1u,
            src[4] + sw * sh * 2u,sw,sh,8u,
            (src[2] & 0xffffu) / 2u,0u);
        display_driver_gpu_mode_lower_4b06c0(
            0u,1u,2u,1u,UINT32_MAX,0u);
        audio_uart_ambiq_buffer_draw_4b1b0e(
            dest_x,dest_y,src_width,src_height,src_x,src_y);
    } else if (dest_format >= 7u && dest_format <= 10u &&
               dest_clip == 0 && src_clip == 0) {
        audio_uart_nema_bind_tex_4b1298(
            2u,dest[4],palette_width,1u,16u,UINT32_MAX,0u);
        int32_t palette_clip[4];
        audio_uart_lv_memzero_48949c(palette_clip,16u);
        palette_clip[2] = (int32_t)(palette_width - 1u);
        audio_uart_ambiq_clip_change_4b077e(0u,palette_clip,0u);
        audio_uart_nema_bind_tex_4b1298(
            1u,src[4],palette_width,1u,16u,UINT32_MAX,0u);
        display_driver_gpu_mode_lower_4b06c0(
            0u,1u,2u,1u,UINT32_MAX,0u);
        display_driver_gpu_position_4b1b48(0u,0u);
    } else {
        render_fault(0xffu,unreachable_expression,unreachable_message,
                     0u,0u);
    }
    (void)audio_uart_ambiq_submit_4b0c8a(1u);
}

/* Native display-driver construction 0x473782. Lower LVGL/display
 * allocators and platform callbacks remain actual typed code imports. */
#include <stdint.h>

extern void *audio_uart_display_instance; /* *DAT_004738f8 */
extern void *audio_uart_display_surface; /* *DAT_004738fc */
extern const void *audio_uart_display_flush_callback; /* DAT_00473908 */
extern const char *audio_uart_display_source_path; /* DAT_004738f0 */
extern const char audio_uart_display_create_error[]; /* DAT_00473904 */
extern void *audio_uart_lv_malloc(uint32_t); /* same native 0x44f718, full selected C body */
extern uint32_t audio_uart_display_pixel_format(void); /* 0x46ca6e */
extern uint8_t audio_uart_display_platform_bind(void *,uint32_t,uint32_t,
                                                uint32_t,uint32_t,uint32_t,
                                                uint32_t); /* 0x48aef8 */
extern void *audio_uart_display_draw_buffer(uint32_t,uint32_t); /* 0x44f7c0 */
extern void audio_uart_display_flush_bind(void *,const void *); /* 0x44fc2e */
extern void *audio_uart_display_surface_alloc(uint32_t,uint32_t,
                                               uint32_t,uint32_t); /* 0x48affa */
extern void audio_uart_display_buffer_attach(void *,void *,uint32_t); /* 0x44fbfc */
extern void audio_uart_display_buffer_mode(void *,uint32_t); /* 0x44fc18 */
extern void audio_uart_display_buffer_size(void *,uint32_t,uint32_t); /* 0x44fa3e */
extern void audio_uart_display_buffer_origin(void *,uint32_t,uint32_t); /* 0x44fa5e */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */

void audio_uart_display_driver_create(void) {
    audio_uart_display_instance=audio_uart_lv_malloc(0x1cu);
    uint32_t format=audio_uart_display_pixel_format();
    if(audio_uart_display_platform_bind(audio_uart_display_instance,
                                         0x240u,0x120u,0xdu,0u,format,
                                         0x14400u)==0u) {
        audio_uart_lvgl_log(3u,audio_uart_display_source_path,0x105u,
                            audio_uart_display_create_error);
        return;
    }
    void *buffer=audio_uart_display_draw_buffer(0x240u,0x120u);
    audio_uart_display_flush_bind(buffer,audio_uart_display_flush_callback);
    audio_uart_display_surface=audio_uart_display_surface_alloc(0x240u,0x120u,
                                                                 6u,0u);
    audio_uart_display_buffer_attach(buffer,audio_uart_display_surface,0u);
    audio_uart_display_buffer_mode(buffer,1u);
    audio_uart_display_buffer_size(buffer,0x240u,0x120u);
    audio_uart_display_buffer_origin(buffer,0u,0u);
}

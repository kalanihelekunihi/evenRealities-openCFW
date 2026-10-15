/* Apollo S200 Ambiq buffer blend path at 0x53d0b6. */
#include <stdint.h>

extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *,const void *,
                                                      const void *);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *,const void *,
                                                     uint32_t);
extern void display_driver_gpu_mode_lower_4b06c0(uint32_t,uint32_t,uint32_t,
                                                    uint32_t,uint32_t,uint32_t);
extern void display_driver_nema_select_522a16(uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,
                                               uint32_t);
extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,
                                              uint32_t,uint32_t,uint32_t,
                                              uint32_t);
extern void audio_uart_ambiq_clip_change_4b077e(uint32_t,const int32_t *,
                                                  uint32_t);
extern uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t);

void audio_uart_ambiq_buffer_blend_53d0b6(const uint32_t *buffer,
                                            const int32_t *clip) {
    int32_t bounds[4];
    int32_t area[4];
    audio_uart_lv_memzero_48949c(bounds,16u);
    bounds[2] = (int32_t)(buffer[1] & 0xffffu) - 1;
    bounds[3] = (int32_t)(buffer[1] >> 16) - 1;
    if (clip == 0)
        audio_uart_checksum_copy(area,bounds,16u);
    else if (audio_uart_lv_area_intersect_450bcc(area,clip,bounds) == 0u)
        return;
    if ((audio_uart_ambiq_bind_buffer_4b092a((void *)buffer,clip,1u)
         & 0xffu) != 1u)
        return;
    display_driver_gpu_mode_lower_4b06c0(0u,1u,0u,UINT32_MAX,UINT32_MAX,0u);
    display_driver_nema_select_522a16(0u);
    const uint32_t first_height = audio_uart_lv_area_height_4515a4(area);
    const uint32_t first_width = audio_uart_lv_area_width_451598(area);
    display_driver_nema_clear_522ae0(
        (uint32_t)area[0],(uint32_t)area[1],first_width,first_height);

    const uint32_t format = (buffer[0] & 0xffffu) >> 8;
    if (format == 0x14u) {
        const uint32_t width = buffer[1] & 0xffffu;
        const uint32_t height = buffer[1] >> 16;
        audio_uart_nema_bind_tex_4b1298(1u,
            buffer[4] + height * width * 2u,width,height,8u,
            (buffer[2] & 0xffffu) / 2u,0u);
        display_driver_gpu_mode_lower_4b06c0(
            0u,1u,1u,UINT32_MAX,UINT32_MAX,0u);
        const uint32_t second_height = audio_uart_lv_area_height_4515a4(area);
        const uint32_t second_width = audio_uart_lv_area_width_451598(area);
        display_driver_nema_clear_522ae0(
            (uint32_t)area[0],(uint32_t)area[1],second_width,second_height);
    } else if (format >= 7u && format <= 10u && clip == 0) {
        const uint32_t width = format == 7u ? 2u :
            format == 8u ? 4u : format == 9u ? 16u : 256u;
        audio_uart_nema_bind_tex_4b1298(1u,buffer[4],width,1u,1u,
                                         UINT32_MAX,0u);
        int32_t palette_clip[4];
        audio_uart_lv_memzero_48949c(palette_clip,16u);
        palette_clip[2] = (int32_t)(width - 1u);
        audio_uart_ambiq_clip_change_4b077e(0u,palette_clip,0u);
        display_driver_gpu_mode_lower_4b06c0(
            0u,1u,1u,UINT32_MAX,UINT32_MAX,0u);
        display_driver_nema_clear_522ae0(0u,0u,width,1u);
    }
    (void)audio_uart_ambiq_submit_4b0c8a(1u);
}

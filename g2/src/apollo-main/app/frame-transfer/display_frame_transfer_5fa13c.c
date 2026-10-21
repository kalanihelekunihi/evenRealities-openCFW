/* Apollo Main frame transfer 0x5fa13c..0x5fa215. The second pass's
 * sampler word is the stock literal at 0x5fa218 (0x10000101). */
#include <stdint.h>

extern void audio_uart_nema_bind_tex_4b1298(uint32_t, const void *, uint32_t,
                                             uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_display_graphics_target_4b1516(uint32_t, uint32_t,
                                                        uint32_t, uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void audio_uart_nema_matrix_upload_5226e8(const void *);
extern void audio_uart_display_graphics_blend_513924(uint32_t, uint32_t,
                                                       uint32_t, uint32_t);
extern void audio_uart_ambiq_texture_color_4b146c(uint32_t);
extern void audio_uart_nema_mask_rectangle_522ae0(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern void audio_uart_ambiq_image_alpha_513e2e(uint32_t);
extern void audio_uart_display_graphics_finish_4b1548(void);

uint32_t audio_uart_display_frame_transfer_5fa13c(const void *input,
                                                   const void *output,
                                                   uint32_t width,
                                                   uint32_t height) {
    if ((width & 1u) == 0u) {
        uint32_t half_width = width >> 1u;
        uint32_t matrix[9];
        audio_uart_nema_bind_tex_4b1298(2u, output, half_width, height,
                                         0x45u, half_width, 0u);
        audio_uart_display_graphics_target_4b1516(0u, 0u, half_width, height);
        audio_uart_nema_bind_tex_4b1298(1u, input, width << 1u, height,
                                         0x34u, width, 0u);
        audio_uart_nema_matrix_identity_561810(matrix);
        matrix[2] = 0xc0000000u;
        matrix[0] = 0x40800000u;
        audio_uart_nema_matrix_upload_5226e8(matrix);
        audio_uart_display_graphics_blend_513924(1u, 2u, 1u, UINT32_MAX);
        audio_uart_ambiq_texture_color_4b146c(0xff000000u);
        audio_uart_nema_mask_rectangle_522ae0(0u, 0u, half_width, height);
        audio_uart_nema_bind_tex_4b1298(1u, input, width << 1u, height,
                                         0x35u, width, 0u);
        audio_uart_nema_matrix_identity_561810(matrix);
        matrix[2] = 0u;
        matrix[0] = 0x40800000u;
        audio_uart_nema_matrix_upload_5226e8(matrix);
        audio_uart_display_graphics_blend_513924(0x10000101u, 2u, 1u,
                                                   UINT32_MAX);
        audio_uart_ambiq_image_alpha_513e2e(0u);
        audio_uart_nema_mask_rectangle_522ae0(0u, 0u, half_width, height);
        audio_uart_display_graphics_finish_4b1548();
    }
    return 0u;
}

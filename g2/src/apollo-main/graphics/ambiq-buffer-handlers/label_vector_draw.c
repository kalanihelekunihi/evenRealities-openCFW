/* Apollo outline glyph draw, native entry 0x53d708. Lower GPU calls remain imports. */
#include <stdint.h>

extern uint32_t audio_uart_lv_area_intersect_450bcc(void *,const void *,const void *);
extern void audio_uart_ambiq_vector_command_51566c(uint32_t);
extern uint32_t audio_uart_ambiq_font_units_529bfe(uint32_t);
extern void audio_uart_nema_matrix_identity_561810(float *);
extern void audio_uart_nema_matrix_scale_5618b8(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_translate_561856(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_ambiq_vector_fill_mode_515634(uint32_t);
extern void audio_uart_ambiq_vector_path_select_5150ea(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_color_resolve_4b06a8(uint32_t,uint8_t);
extern void audio_uart_ambiq_vector_path_color_515136(uint32_t,uint32_t);
extern void audio_uart_ambiq_vector_shape_matrix_514f60(uint32_t,float *);
extern void audio_uart_ambiq_vector_shape_draw_5202ec(uint32_t,uint32_t);
extern void audio_uart_ambiq_vector_stroke_width_515640(float)
    __attribute__((pcs("aapcs-vfp")));

static uint32_t load32(const void *p) { return *(const uint32_t *)p; }
static uint16_t load16(const void *p) { return *(const uint16_t *)p; }
static void copy_rgb(uint32_t *dst,const uint8_t *src) {
    uint8_t *out=(uint8_t *)dst;
    out[0]=src[0]; out[1]=src[1]; out[2]=src[2];
}

void audio_uart_ambiq_label_vector_draw_53d708(const void *unit,
                                                  const void *glyph) {
    const uint8_t *u=(const uint8_t *)unit;
    const uint8_t *g=(const uint8_t *)glyph;
    const uint8_t *area=(const uint8_t *)(uintptr_t)load32(g+8u);
    uint32_t intersection[5];
    if(audio_uart_lv_area_intersect_450bcc(intersection,area,u+0x38u)==0u)
        return;

    uint32_t gpu=load32(u+0x4cu);
    uint32_t outline=load32(g);
    audio_uart_ambiq_vector_command_51566c(0x501u);
    int32_t x=(int32_t)load32(area);
    int32_t y=(int32_t)load32(area+4u);
    const uint8_t *header=(const uint8_t *)(uintptr_t)load32(g+16u);
    uint32_t units=audio_uart_ambiq_font_units_529bfe(load32(header));
    float factor=((float)units/64.0f)/64.0f;
    float matrix[9];
    audio_uart_nema_matrix_identity_561810(matrix);
    audio_uart_nema_matrix_scale_5618b8(factor,-factor,matrix);
    int32_t tx=(int32_t)((uint32_t)x-(uint32_t)(int32_t)(int16_t)load16(header+10u));
    int32_t ty=(int32_t)((uint32_t)y+(uint32_t)load16(header+8u)+
                         (uint32_t)(int32_t)(int16_t)load16(header+12u));
    audio_uart_nema_matrix_translate_561856((float)tx,(float)ty,matrix);

    uint32_t path=load32((const void *)(uintptr_t)(gpu+0x48u));
    audio_uart_ambiq_vector_fill_mode_515634(1u);
    audio_uart_ambiq_vector_path_select_5150ea(path,0u);
    /* Native three-byte copy leaves the high byte of the earlier X local intact. */
    uint32_t color_word=(uint32_t)x;
    copy_rgb(&color_word,g+20u);
    uint32_t color=audio_uart_ambiq_color_resolve_4b06a8(color_word,g[23u]);
    audio_uart_ambiq_vector_path_color_515136(path,color);
    uint32_t shape=load32((const void *)(uintptr_t)outline);
    audio_uart_ambiq_vector_shape_matrix_514f60(shape,matrix);
    audio_uart_ambiq_vector_shape_draw_5202ec(shape,path);

    int32_t stroke=(int32_t)load32(g+28u);
    if(stroke>0) {
        audio_uart_ambiq_vector_fill_mode_515634(0u);
        audio_uart_ambiq_vector_stroke_width_515640((float)stroke/factor);
        copy_rgb(&color_word,g+24u);
        color=audio_uart_ambiq_color_resolve_4b06a8(color_word,g[27u]);
        audio_uart_ambiq_vector_path_color_515136(path,color);
        shape=load32((const void *)(uintptr_t)(outline+4u));
        audio_uart_ambiq_vector_shape_matrix_514f60(shape,matrix);
        audio_uart_ambiq_vector_shape_draw_5202ec(shape,path);
    }
}

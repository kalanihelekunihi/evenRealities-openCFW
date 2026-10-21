/* Nema VG shape transform, native 0x514f60..0x515045. */
#include <stdint.h>

extern void audio_uart_nema_vg_set_error_51565c(uint32_t);

void audio_uart_ambiq_vector_shape_matrix_514f60(uint32_t shape,
                                                   const float *matrix) {
    if(shape==0u) {
        audio_uart_nema_vg_set_error_51565c(1u);
        return;
    }
    uint8_t *s=(uint8_t *)(uintptr_t)shape;
    uint32_t *flags=(uint32_t *)(void *)(s+0x84u);
    if(matrix==0) {
        *flags&=~1u;
        audio_uart_nema_vg_set_error_51565c(1u);
        return;
    }
    uint32_t *dst=(uint32_t *)(void *)(s+0x60u);
    const uint32_t *src=(const uint32_t *)(const void *)matrix;
    for(unsigned row=0;row<3u;row++) {
        dst[row*3u]=src[row*3u];
        dst[row*3u+1u]=src[row*3u+1u];
        dst[row*3u+2u]=src[row*3u+2u];
    }
    for(unsigned row=0;row<3u;row++) {
        for(unsigned col=0;col<3u;col++) {
            float expected=(row==col)?1.0f:0.0f;
            if(matrix[row*3u+col]!=expected) {
                *flags|=1u;
                return;
            }
        }
    }
    *flags&=~1u;
}

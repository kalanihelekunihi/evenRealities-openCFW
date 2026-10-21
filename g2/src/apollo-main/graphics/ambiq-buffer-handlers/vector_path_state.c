/* Native Nema vector context and paint setters at 0x5150ea..0x51566c. */
#include <stdint.h>

extern volatile uint32_t audio_uart_nema_vg_context_cell;
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);

void audio_uart_ambiq_vector_command_51566c(uint32_t command) {
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    *(volatile uint32_t *)(context+0x84u)=command;
}

void audio_uart_ambiq_vector_fill_mode_515634(uint32_t mode) {
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[0x7cu]=(uint8_t)mode;
}

void audio_uart_ambiq_vector_stroke_width_515640(float width)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_ambiq_vector_stroke_width_515640(float width) {
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    *(volatile float *)(context+0x2d8u)=width;
}

void audio_uart_ambiq_vector_path_select_5150ea(uint32_t path,uint32_t mode) {
    if(path==0u) {
        audio_uart_nema_vg_set_error_51565c(1u);
    } else if(mode<=4u) {
        *(volatile uint8_t *)(uintptr_t)(path+0xd5u)=(uint8_t)mode;
    } else {
        audio_uart_nema_vg_set_error_51565c(8u);
    }
}

void audio_uart_ambiq_vector_path_color_515136(uint32_t path,uint32_t color) {
    if(path!=0u)
        *(volatile uint32_t *)(uintptr_t)(path+0xd8u)=color;
    else
        audio_uart_nema_vg_set_error_51565c(1u);
}

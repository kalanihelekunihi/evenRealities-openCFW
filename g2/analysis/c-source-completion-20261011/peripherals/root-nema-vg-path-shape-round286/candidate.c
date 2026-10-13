#include <stdint.h>
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_vg_path_process_561c68(void *);
/* Native514f3c..514f60: ordered shape stores precede genuine postprocessor. */
void audio_uart_nema_vg_path_shape_514f3c(void *path,uint32_t segment_count,void *segments,uint32_t data_count,void *data) {
 if(!path){audio_uart_nema_vg_set_error_51565c(1u);return;}
 volatile uint32_t *p=path;
 p[2]=(uint32_t)(uintptr_t)segments;p[3]=(uint32_t)(uintptr_t)data;
 p[0]=segment_count;p[1]=data_count;
 audio_uart_nema_vg_path_process_561c68(path);
}

#include <stdint.h>
/* Native5fa21c..5fa236: sequential volatile accesses preserve output/path aliases. */
void audio_uart_ambiq_get_path_buffers_5fa21c(void *path,uint32_t *segment_size,uint32_t *data_size,void **segments,void **data) {
 const volatile uint32_t *p=path;
 *(volatile uint32_t *)segment_size=p[0];
 *(volatile uint32_t *)data_size=p[1];
 *(volatile uint32_t *)(void *)segments=p[2];
 *(volatile uint32_t *)(void *)data=p[3];
}

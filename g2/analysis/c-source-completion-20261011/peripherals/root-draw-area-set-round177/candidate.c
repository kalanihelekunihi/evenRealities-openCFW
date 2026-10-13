#include <stdint.h>
/* Native450b5c..450b6c; four words written in coordinate order. */
void audio_uart_lv_area_set_450b5c(void *area,uint32_t x1,uint32_t y1,uint32_t x2,uint32_t y2) {
    volatile uint32_t *a=area;
    a[0]=x1;a[1]=y1;a[2]=x2;a[3]=y2;
}

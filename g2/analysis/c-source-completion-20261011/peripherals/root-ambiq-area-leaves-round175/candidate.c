#include <stdint.h>
/* Native4c73c4..4c73d6. Forward word copy, including overlapping areas. */
void audio_uart_ambiq_area_copy_4c73c4(uint32_t *destination,const void *source) {
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];
}
/* Native450bb2..450bcc: x1,x2,y1,y2 access ordering and wrapped sums. */
void audio_uart_ambiq_area_move_450bb2(uint32_t *area,uint32_t x,uint32_t y) {
    volatile uint32_t *a=area;
    a[0]=a[0]+x;
    a[2]=a[2]+x;
    a[1]=a[1]+y;
    a[3]=a[3]+y;
}

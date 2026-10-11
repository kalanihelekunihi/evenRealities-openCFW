/* Native FT_Outline_Get_CBox 0x527ace. */
#include <stdint.h>
void audio_uart_font_outline_cbox(void *outline,void *box) {
    if(outline==0 || box==0) return;
    int32_t *b=(int32_t *)box;
    int16_t count=*(int16_t *)(void *)((uint8_t *)outline+2u);
    if(count==0) { b[0]=0;b[1]=0;b[2]=0;b[3]=0;return; }
    int32_t *points=(int32_t *)(uintptr_t)
        *(uint32_t *)(void *)((uint8_t *)outline+4u);
    int32_t xmin=points[0],ymin=points[1],xmax=xmin,ymax=ymin;
    for(int32_t i=1;i<count;i++) {
        int32_t x=points[i*2],y=points[i*2+1];
        if(x<xmin) xmin=x;
        if(x>xmax) xmax=x;
        if(y<ymin) ymin=y;
        if(y>ymax) ymax=y;
    }
    b[0]=xmin;b[1]=ymin;b[2]=xmax;b[3]=ymax;
}

/* Apollo LV transformed image bounds at native 0x488cda. */
#include <stdint.h>
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_lv_transform_point_4513ae(int32_t *,int32_t,uint32_t,
                                                  uint32_t,const void *,uint32_t);
void audio_uart_ambiq_transform_area_488cda(int32_t out[4],int32_t width,
                                             int32_t height,int32_t rotation,
                                             uint32_t scale_x,uint32_t scale_y,
                                             const void *pivot) {
    if(rotation==0 && (scale_x&0xffffu)==256u &&
       (scale_y&0xffffu)==256u) {
        out[0]=0;out[1]=0;
        out[2]=(int32_t)((uint32_t)width-1u);
        out[3]=(int32_t)((uint32_t)height-1u);
        return;
    }
    int32_t points[8];
    audio_uart_lv_memzero_48949c(points,sizeof(points));
    points[2]=width;points[5]=height;
    points[6]=width;points[7]=height;
    for(uint32_t i=0u;i<4u;i++)
        audio_uart_lv_transform_point_4513ae(
            &points[i*2u],rotation,scale_x&0xffffu,scale_y&0xffffu,
            pivot,1u);
    int32_t xmin=points[0],xmax=points[0];
    int32_t ymin=points[1],ymax=points[1];
    for(uint32_t i=1u;i<4u;i++) {
        const int32_t x=points[i*2u],y=points[i*2u+1u];
        if(x<xmin)xmin=x;
        if(x>xmax)xmax=x;
        if(y<ymin)ymin=y;
        if(y>ymax)ymax=y;
    }
    out[0]=xmin;out[1]=ymin;
    out[2]=(int32_t)((uint32_t)xmax-1u);
    out[3]=(int32_t)((uint32_t)ymax-1u);
}

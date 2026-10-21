/* Native Main 0x4513c8 point-array transform, LVGL 9.3 fixed arithmetic. */
#include <stdint.h>
extern int32_t audio_uart_lv_sin_4885f0(int16_t degrees);
static int32_t mul32(int32_t a,int32_t b) {
    return (int32_t)((uint32_t)a*(uint32_t)b);
}
static int32_t add32(int32_t a,int32_t b) {
    return (int32_t)((uint32_t)a+(uint32_t)b);
}
static int32_t sub32(int32_t a,int32_t b) {
    return (int32_t)((uint32_t)a-(uint32_t)b);
}
static int32_t sar(int32_t a,unsigned shift) {return a>>shift;}

void audio_uart_lv_transform_area_4513c8(int32_t *points,uint32_t count,
                                           int32_t angle,int32_t scale_x,
                                           int32_t scale_y,const int32_t *pivot,
                                           uint32_t scale_before_rotate) {
    if(angle==0 && scale_x==256 && scale_y==256)return;
    for(uint32_t i=0;i<count;i++) {
        points[2u*i]=sub32(points[2u*i],pivot[0]);
        points[2u*i+1u]=sub32(points[2u*i+1u],pivot[1]);
    }
    if(angle==0) {
        for(uint32_t i=0;i<count;i++) {
            points[2u*i]=add32(pivot[0],sar(mul32(scale_x,points[2u*i]),8));
            points[2u*i+1u]=add32(pivot[1],sar(mul32(scale_y,points[2u*i+1u]),8));
        }
        return;
    }
    if(angle>3600)angle=sub32(angle,3600);
    if(angle<0)angle=add32(angle,3600);
    int32_t angle_next=add32(angle/10,1);
    int32_t rem=angle%10;
    int16_t base=(int16_t)(angle/10);
    int32_t sn0=audio_uart_lv_sin_4885f0(base);
    int32_t sn1=audio_uart_lv_sin_4885f0((int16_t)angle_next);
    int32_t cs0=audio_uart_lv_sin_4885f0((int16_t)(base+90));
    int32_t cs1=audio_uart_lv_sin_4885f0((int16_t)((int16_t)angle_next+90));
    int32_t sn=sar(add32(mul32(10-rem,sn0),mul32(rem,sn1))/10,5);
    int32_t cs=sar(add32(mul32(10-rem,cs0),mul32(rem,cs1))/10,5);
    for(uint32_t i=0;i<count;i++) {
        int32_t x=points[2u*i],y=points[2u*i+1u];
        int32_t xx=sub32(mul32(x,cs),mul32(y,sn));
        int32_t yy=add32(mul32(x,sn),mul32(y,cs));
        if(scale_x==256 && scale_y==256) {
            points[2u*i]=add32(pivot[0],sar(xx,10));
            points[2u*i+1u]=add32(pivot[1],sar(yy,10));
        } else if(scale_before_rotate==0) {
            points[2u*i]=add32(pivot[0],sar(mul32(scale_x,xx),18));
            points[2u*i+1u]=add32(pivot[1],sar(mul32(scale_y,yy),18));
        } else {
            points[2u*i]=add32(pivot[0],sar(sub32(mul32(mul32(scale_x,x),cs),mul32(mul32(scale_y,y),sn)),18));
            points[2u*i+1u]=add32(pivot[1],sar(add32(mul32(mul32(scale_x,x),sn),mul32(mul32(scale_y,y),cs)),18));
        }
    }
}

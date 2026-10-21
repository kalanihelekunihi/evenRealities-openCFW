/* Native FT_Outline_EmboldenXY0x527bd6, pinned FreeType 2.9.1 ftoutln.c. */
#include <stdint.h>
typedef struct {int32_t x,y;} Vector;
extern uint32_t audio_uart_font_outline_orientation(void *); /* 0x527e0a */
extern uint32_t audio_uart_font_vector_normlen(Vector *); /* 0x524902 */
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* MulFix0x5246f8 */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* 0x524606 */
int32_t audio_uart_font_embolden_xy(void *outline,int32_t xstrength,int32_t ystrength) {
    if(outline==0) return 0x14;
    xstrength/=2;ystrength/=2;
    if((xstrength|ystrength)==0) return 0;
    uint32_t orientation=audio_uart_font_outline_orientation(outline);
    int16_t contour_count=*(const int16_t *)(const void *)outline;
    if(orientation==2u) return contour_count!=0?6:0;
    Vector *points=(Vector *)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)outline+4u);
    const int16_t *contours=(const int16_t *)(uintptr_t)
        *(uint32_t *)(void *)((uint8_t *)outline+12u);
    int32_t first=0;
    for(int32_t c=0;c<contour_count;c++) {
        int32_t last=contours[c];
        Vector in={0,0},out={0,0},anchor={0,0},shift={0,0};
        int32_t l_in=0,l_out=0,l_anchor=0;
        int32_t i=last,j=first,k=-1;
        while(j!=i && i!=k) {
            if(j!=k) {
                out.x=(int32_t)((uint32_t)points[j].x-(uint32_t)points[i].x);
                out.y=(int32_t)((uint32_t)points[j].y-(uint32_t)points[i].y);
                l_out=(int32_t)audio_uart_font_vector_normlen(&out);
                if(l_out==0) {j=j<last?j+1:first;continue;}
            } else {out=anchor;l_out=l_anchor;}
            if(l_in!=0) {
                if(k<0) {k=i;anchor=in;l_anchor=l_in;}
                int32_t d=(int32_t)((uint32_t)audio_uart_font_scale_metric((uint32_t)in.x,out.x)+
                                    (uint32_t)audio_uart_font_scale_metric((uint32_t)in.y,out.y));
                if(d>-0xf000) {
                    d=(int32_t)((uint32_t)d+0x10000u);
                    shift.x=(int32_t)((uint32_t)in.y+(uint32_t)out.y);
                    shift.y=(int32_t)((uint32_t)in.x+(uint32_t)out.x);
                    if(orientation==0u) shift.x=(int32_t)(0u-(uint32_t)shift.x);
                    else shift.y=(int32_t)(0u-(uint32_t)shift.y);
                    int32_t q=(int32_t)((uint32_t)audio_uart_font_scale_metric((uint32_t)out.x,in.y)-
                                        (uint32_t)audio_uart_font_scale_metric((uint32_t)out.y,in.x));
                    if(orientation==0u) q=(int32_t)(0u-(uint32_t)q);
                    int32_t l=l_in<l_out?l_in:l_out;
                    shift.x=audio_uart_font_scale_metric((uint32_t)xstrength,q)<=
                            audio_uart_font_scale_metric((uint32_t)l,d)?
                            audio_uart_font_mul_div(shift.x,xstrength,d):
                            audio_uart_font_mul_div(shift.x,l,q);
                    shift.y=audio_uart_font_scale_metric((uint32_t)ystrength,q)<=
                            audio_uart_font_scale_metric((uint32_t)l,d)?
                            audio_uart_font_mul_div(shift.y,ystrength,d):
                            audio_uart_font_mul_div(shift.y,l,q);
                } else shift.x=shift.y=0;
                while(i!=j) {
                    points[i].x=(int32_t)((uint32_t)points[i].x+(uint32_t)xstrength+(uint32_t)shift.x);
                    points[i].y=(int32_t)((uint32_t)points[i].y+(uint32_t)ystrength+(uint32_t)shift.y);
                    i=i<last?i+1:first;
                }
            } else i=j;
            in=out;l_in=l_out;
            j=j<last?j+1:first;
        }
        first=last+1;
    }
    return 0;
}

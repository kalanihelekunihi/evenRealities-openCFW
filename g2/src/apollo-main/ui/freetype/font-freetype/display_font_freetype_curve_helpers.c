/* Native conic subdivision 0x567fce, angle continuity 0x568020, and
 * border quadratic append 0x56847a. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_vector_angle(int32_t,int32_t); /* 0x528fbc */
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_stroker_border_grow(void *,uint32_t); /* 0x5682de */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static int32_t midpoint(int32_t a,int32_t b) {
    return (int32_t)((uint32_t)((uint32_t)a+(uint32_t)b))/2;
}
void audio_uart_font_conic_split(void *points) {
    Vector *p=(Vector *)points;
    p[4]=p[2];
    p[3].x=midpoint(p[1].x,p[2].x);
    p[1].x=midpoint(p[0].x,p[1].x);
    p[2].x=midpoint(p[1].x,p[3].x);
    p[4].y=p[2].y;
    p[3].y=midpoint(p[1].y,p[2].y);
    p[1].y=midpoint(p[0].y,p[1].y);
    p[2].y=midpoint(p[1].y,p[3].y);
}
void audio_uart_font_cubic_split(void *points) { /* 0x5680ce */
    Vector *p=(Vector *)points;
    Vector a=p[0],b=p[1],c=p[2],d=p[3];
    Vector ab={midpoint(a.x,b.x),midpoint(a.y,b.y)};
    Vector bc={midpoint(b.x,c.x),midpoint(b.y,c.y)};
    Vector cd={midpoint(c.x,d.x),midpoint(c.y,d.y)};
    Vector abc={midpoint(ab.x,bc.x),midpoint(ab.y,bc.y)};
    Vector bcd={midpoint(bc.x,cd.x),midpoint(bc.y,cd.y)};
    Vector middle={midpoint(abc.x,bcd.x),midpoint(abc.y,bcd.y)};
    p[1]=ab;p[2]=abc;p[3]=middle;p[4]=bcd;p[5]=cd;p[6]=d;
}
uint32_t audio_uart_font_conic_angle_ok(const Vector *points,int32_t *angle_a,
                                         int32_t *angle_b) {
    int32_t ax=(int32_t)((uint32_t)points[1].x-(uint32_t)points[2].x);
    int32_t ay=(int32_t)((uint32_t)points[1].y-(uint32_t)points[2].y);
    int32_t bx=(int32_t)((uint32_t)points[0].x-(uint32_t)points[1].x);
    int32_t by=(int32_t)((uint32_t)points[0].y-(uint32_t)points[1].y);
    uint8_t a_small=(uint32_t)(ax+1u)<3u&&(uint32_t)(ay+1u)<3u;
    uint8_t b_small=(uint32_t)(bx+1u)<3u&&(uint32_t)(by+1u)<3u;
    if(a_small&&!b_small) *angle_a=*angle_b=audio_uart_font_vector_angle(bx,by);
    else if(!a_small&&b_small) *angle_a=*angle_b=audio_uart_font_vector_angle(ax,ay);
    else if(!a_small&&!b_small) {
        *angle_a=audio_uart_font_vector_angle(ax,ay);
        *angle_b=audio_uart_font_vector_angle(bx,by);
    }
    int32_t difference=audio_uart_font_stroker_angle_diff(*angle_a,*angle_b);
    uint32_t magnitude=difference<0?0u-(uint32_t)difference:(uint32_t)difference;
    return magnitude<0x1e0000u;
}
uint32_t audio_uart_font_cubic_angle_ok(const Vector *points,int32_t *incoming,
                                        int32_t *middle,int32_t *outgoing) { /* 0x568176 */
    Vector d1={(int32_t)((uint32_t)points[2].x-(uint32_t)points[3].x),
               (int32_t)((uint32_t)points[2].y-(uint32_t)points[3].y)};
    Vector d2={(int32_t)((uint32_t)points[1].x-(uint32_t)points[2].x),
               (int32_t)((uint32_t)points[1].y-(uint32_t)points[2].y)};
    Vector d3={(int32_t)((uint32_t)points[0].x-(uint32_t)points[1].x),
               (int32_t)((uint32_t)points[0].y-(uint32_t)points[1].y)};
    uint8_t small1=(uint32_t)((uint32_t)d1.x+1u)<3u&&
                   (uint32_t)((uint32_t)d1.y+1u)<3u;
    uint8_t small2=(uint32_t)((uint32_t)d2.x+1u)<3u&&
                   (uint32_t)((uint32_t)d2.y+1u)<3u;
    uint8_t small3=(uint32_t)((uint32_t)d3.x+1u)<3u&&
                   (uint32_t)((uint32_t)d3.y+1u)<3u;
    if(small1) {
        if(small2) {
            if(!small3) *incoming=*middle=*outgoing=
                audio_uart_font_vector_angle(d3.x,d3.y);
        } else if(small3) {
            *incoming=*middle=*outgoing=audio_uart_font_vector_angle(d2.x,d2.y);
        } else {
            *incoming=*middle=audio_uart_font_vector_angle(d2.x,d2.y);
            *outgoing=audio_uart_font_vector_angle(d3.x,d3.y);
        }
    } else if(small2) {
        if(small3) {
            *incoming=*middle=*outgoing=audio_uart_font_vector_angle(d1.x,d1.y);
        } else {
            *incoming=audio_uart_font_vector_angle(d1.x,d1.y);
            *outgoing=audio_uart_font_vector_angle(d3.x,d3.y);
            *middle=*incoming+audio_uart_font_stroker_angle_diff(*incoming,*outgoing)/2;
        }
    } else if(small3) {
        *incoming=audio_uart_font_vector_angle(d1.x,d1.y);
        *middle=*outgoing=audio_uart_font_vector_angle(d2.x,d2.y);
    } else {
        *incoming=audio_uart_font_vector_angle(d1.x,d1.y);
        *middle=audio_uart_font_vector_angle(d2.x,d2.y);
        *outgoing=audio_uart_font_vector_angle(d3.x,d3.y);
    }
    int32_t turn1=audio_uart_font_stroker_angle_diff(*incoming,*middle);
    int32_t turn2=audio_uart_font_stroker_angle_diff(*middle,*outgoing);
    uint32_t abs1=turn1<0?0u-(uint32_t)turn1:(uint32_t)turn1;
    uint32_t abs2=turn2<0?0u-(uint32_t)turn2:(uint32_t)turn2;
    return abs1<0x168000u&&abs2<0x168000u;
}
int32_t audio_uart_font_stroker_border_conic(void *border,const Vector *control,
                                              const Vector *to) {
    uint8_t *b=(uint8_t *)border;
    int32_t error=audio_uart_font_stroker_border_grow(border,2u);
    if(error==0) {
        uint32_t n=word(b,0u);
        Vector *points=(Vector *)(uintptr_t)word(b,8u);
        uint8_t *tags=(uint8_t *)(uintptr_t)word(b,12u);
        points[n]=*control;points[n+1u]=*to;
        tags[n]=0u;tags[n+1u]=1u;
        store(b,0u,n+2u);
    }
    b[16u]=0u;
    return error;
}

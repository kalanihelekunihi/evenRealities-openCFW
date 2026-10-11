/* Native FT_Stroker_CubicTo 0x569160, mapped to pinned FreeType 2.9.1
 * ftstroke.c and the authenticated stock stroker layout/call graph. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern void audio_uart_font_cubic_split(void *); /* 0x5680ce */
extern uint32_t audio_uart_font_cubic_angle_ok(const Vector *,int32_t *,
                                               int32_t *,int32_t *); /* 0x568176 */
extern int32_t audio_uart_font_stroker_process_corner(void *,int32_t,int32_t); /* 0x568d2a */
extern int32_t audio_uart_font_stroker_subpath_start(void *,int32_t); /* 0x568ce2 */
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_vector_angle(int32_t,int32_t); /* 0x528fbc */
extern int32_t audio_uart_font_vector_length(const Vector *); /* 0x529086 */
extern int32_t audio_uart_font_vector_cos(int32_t); /* 0x528f8c */
extern int32_t audio_uart_font_vector_sin(int32_t); /* 0x528f9a */
extern int32_t audio_uart_font_divide_metric(int32_t,int32_t); /* 0x524754 */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* 0x524606 */
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_border_add(void *,const Vector *,uint32_t); /* 0x5683f2 */
extern int32_t audio_uart_font_stroker_border_cubic(void *,const Vector *,
                                                    const Vector *,const Vector *); /* 0x5684c2 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
static uint8_t close_coord(int32_t a,int32_t b) {
    return (uint32_t)((uint32_t)a-(uint32_t)b+1u)<3u;
}
static uint32_t magnitude(int32_t value) {
    return value<0?0u-(uint32_t)value:(uint32_t)value;
}
static Vector add(Vector a,Vector b) {
    Vector r={(int32_t)((uint32_t)a.x+(uint32_t)b.x),
              (int32_t)((uint32_t)a.y+(uint32_t)b.y)};
    return r;
}
static Vector subtract(Vector a,Vector b) {
    Vector r={(int32_t)((uint32_t)a.x-(uint32_t)b.x),
              (int32_t)((uint32_t)a.y-(uint32_t)b.y)};
    return r;
}
static int32_t angle(Vector v) { return audio_uart_font_vector_angle(v.x,v.y); }
int32_t audio_uart_font_stroker_cubic(void *stroker,const Vector *control1,
                                      const Vector *control2,const Vector *to) {
    if(stroker==0||control1==0||control2==0||to==0) return 6;
    uint8_t *s=(uint8_t *)stroker;
    Vector center={(int32_t)word(s,8u),(int32_t)word(s,12u)};
    if(close_coord(center.x,control1->x)&&close_coord(center.y,control1->y)&&
       close_coord(control1->x,control2->x)&&close_coord(control1->y,control2->y)&&
       close_coord(control2->x,to->x)&&close_coord(control2->y,to->y)) {
        store(s,8u,(uint32_t)to->x);store(s,12u,(uint32_t)to->y);
        return 0;
    }
    Vector stack[37];
    stack[0]=*to;stack[1]=*control2;stack[2]=*control1;stack[3]=center;
    Vector *arc=stack;
    uint8_t first=1u;
    while(arc>=stack) {
        int32_t incoming=(int32_t)word(s,0u),middle=incoming,outgoing=incoming;
        if(arc<stack+32 && audio_uart_font_cubic_angle_ok(arc,&incoming,
                                                          &middle,&outgoing)==0u) {
            if(s[20u]!=0u) store(s,0u,(uint32_t)incoming);
            audio_uart_font_cubic_split(arc);arc+=3;continue;
        }
        int32_t error=0;
        if(first!=0u) {
            first=0u;
            if(s[20u]!=0u)
                error=audio_uart_font_stroker_process_corner(s,incoming,0);
            else {
                store(s,4u,(uint32_t)incoming);
                error=audio_uart_font_stroker_subpath_start(s,0);
            }
        } else if(magnitude(audio_uart_font_stroker_angle_diff(
                   (int32_t)word(s,0u),incoming))>=0x78001u) {
            store(s,8u,(uint32_t)arc[3].x);store(s,12u,(uint32_t)arc[3].y);
            store(s,4u,(uint32_t)incoming);s[42u]=0u;
            error=audio_uart_font_stroker_subpath_start(s,0);
            s[42u]=s[43u];
        }
        if(error!=0) return error;
        int32_t theta1=audio_uart_font_stroker_angle_diff(incoming,middle)/2;
        int32_t theta2=audio_uart_font_stroker_angle_diff(middle,outgoing)/2;
        uint32_t phi1=(uint32_t)incoming+(uint32_t)theta1;
        uint32_t phi2=(uint32_t)middle+(uint32_t)theta2;
        int32_t reach1=audio_uart_font_divide_metric((int32_t)word(s,0x30u),
                                                      audio_uart_font_vector_cos(theta1));
        int32_t reach2=audio_uart_font_divide_metric((int32_t)word(s,0x30u),
                                                      audio_uart_font_vector_cos(theta2));
        int32_t original_angle=0;
        if(s[40u]!=0u) original_angle=angle(subtract(arc[0],arc[3]));
        for(uint32_t side=0;side<2u;++side) {
            uint8_t *border=s+0x34u+side*0x20u;
            uint32_t rotate=0x5a0000u-side*0xb40000u;
            Vector ctrl1,ctrl2,end;
            audio_uart_font_vector_from_polar(&ctrl1,(uint32_t)reach1,phi1+rotate);
            ctrl1=add(ctrl1,arc[2]);
            audio_uart_font_vector_from_polar(&ctrl2,(uint32_t)reach2,phi2+rotate);
            ctrl2=add(ctrl2,arc[1]);
            audio_uart_font_vector_from_polar(&end,word(s,0x30u),
                                               (uint32_t)outgoing+rotate);
            end=add(end,arc[0]);
            if(s[40u]!=0u) {
                uint32_t n=word(border,0u);
                Vector *points=(Vector *)(uintptr_t)word(border,8u);
                Vector start=points[n-1u];
                int32_t outer_angle=angle(subtract(end,start));
                if(magnitude(audio_uart_font_stroker_angle_diff(original_angle,
                                                                outer_angle))>=0x5a0001u) {
                    int32_t beta=angle(subtract(arc[3],start));
                    int32_t gamma=angle(subtract(arc[0],end));
                    Vector span=subtract(end,start);
                    int32_t span_length=audio_uart_font_vector_length(&span);
                    int32_t sine_a=audio_uart_font_vector_sin(
                                            (int32_t)((uint32_t)outer_angle-(uint32_t)gamma));
                    int32_t sine_b=audio_uart_font_vector_sin(
                                            (int32_t)((uint32_t)beta-(uint32_t)gamma));
                    int32_t extent=audio_uart_font_mul_div(span_length,
                                        (int32_t)magnitude(sine_a),
                                        (int32_t)magnitude(sine_b));
                    Vector delta;
                    audio_uart_font_vector_from_polar(&delta,(uint32_t)extent,(uint32_t)beta);
                    delta=add(delta,start);border[16u]=0u;
                    error=audio_uart_font_stroker_border_add(border,&delta,0u);
                    if(error!=0) return error;
                    error=audio_uart_font_stroker_border_add(border,&end,0u);
                    if(error!=0) return error;
                    error=audio_uart_font_stroker_border_cubic(border,&ctrl2,&ctrl1,&start);
                    if(error!=0) return error;
                    error=audio_uart_font_stroker_border_add(border,&end,0u);
                    if(error!=0) return error;
                    continue;
                }
            }
            error=audio_uart_font_stroker_border_cubic(border,&ctrl1,&ctrl2,&end);
            if(error!=0) return error;
        }
        arc-=3;store(s,0u,(uint32_t)outgoing);
    }
    store(s,8u,(uint32_t)to->x);store(s,12u,(uint32_t)to->y);
    return 0;
}

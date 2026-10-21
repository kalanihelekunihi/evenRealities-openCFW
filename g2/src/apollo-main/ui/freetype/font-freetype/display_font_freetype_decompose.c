/* Native FT_Outline_Decompose 0x527508: FreeType on/conic/cubic tag walk. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
typedef struct {
    int32_t (*move_to)(const Vector *,void *);
    int32_t (*line_to)(const Vector *,void *);
    int32_t (*conic_to)(const Vector *,const Vector *,void *);
    int32_t (*cubic_to)(const Vector *,const Vector *,const Vector *,void *);
    int32_t shift,delta;
} DecomposeFuncs;
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static int32_t transformed(int32_t value,uint32_t shift,int32_t delta) {
    uint32_t shifted=(shift&0xffu)>=32u?0u:(uint32_t)value<<(shift&0xffu);
    return (int32_t)(shifted-(uint32_t)delta);
}
static Vector point(const Vector *points,int32_t index,uint32_t shift,int32_t delta) {
    Vector v={transformed(points[index].x,shift,delta),
              transformed(points[index].y,shift,delta)};
    return v;
}
static Vector midpoint(Vector a,Vector b) {
    Vector v={(int32_t)(((int64_t)a.x+(int64_t)b.x)/2),
              (int32_t)(((int64_t)a.y+(int64_t)b.y)/2)};
    return v;
}
int32_t audio_uart_font_decompose_outline(const void *outline,
                                          const void *functions,void *user) {
    if(outline==0) return 0x14;
    if(functions==0) return 6;
    const DecomposeFuncs *fn=(const DecomposeFuncs *)functions;
    const Vector *points=(const Vector *)(uintptr_t)word(outline,4u);
    const uint8_t *tags=(const uint8_t *)(uintptr_t)word(outline,8u);
    const int16_t *contours=(const int16_t *)(uintptr_t)word(outline,0x0cu);
    int32_t count=*(const int16_t *)outline;
    int32_t first=0;
    uint32_t shift=(uint32_t)fn->shift;
    int32_t delta=fn->delta;
    for(int32_t contour=0;contour<count;contour++) {
        int32_t last=contours[contour];
        if(last<0) return 0;
        Vector start=point(points,first,shift,delta);
        Vector end=point(points,last,shift,delta);
        uint8_t first_tag=tags[first]&3u;
        if(first_tag==2u) return 0x14;
        int32_t cursor=first;
        if(first_tag==0u) {
            if((tags[last]&3u)==1u) { start=end;last--; }
            else start=midpoint(start,end);
            cursor=first-1;
        }
        int32_t error=fn->move_to(&start,user);
        if(error!=0) return error;
        for(;;) {
            if(cursor>=last) {
                error=fn->line_to(&start,user);
                if(error!=0) return error;
                break;
            }
            int32_t next=cursor+1;
            uint8_t tag=tags[next]&3u;
            if(tag==1u) {
                Vector to=point(points,next,shift,delta);
                error=fn->line_to(&to,user);
                if(error!=0) return error;
                cursor=next;
                continue;
            }
            if(tag==0u) {
                Vector control=point(points,next,shift,delta);
                for(;;) {
                    if(next>=last) {
                        error=fn->conic_to(&control,&start,user);
                        if(error!=0) return error;
                        goto contour_done;
                    }
                    int32_t after=next+1;
                    uint8_t after_tag=tags[after]&3u;
                    Vector to=point(points,after,shift,delta);
                    if(after_tag==1u) {
                        error=fn->conic_to(&control,&to,user);
                        if(error!=0) return error;
                        cursor=after;
                        break;
                    }
                    if(after_tag!=0u) return 0x14;
                    Vector middle=midpoint(control,to);
                    error=fn->conic_to(&control,&middle,user);
                    if(error!=0) return error;
                    control=to;next=after;
                }
                continue;
            }
            if(next+1>last || (tags[next+1]&3u)!=2u) return 0x14;
            Vector a=point(points,next,shift,delta);
            Vector b=point(points,next+1,shift,delta);
            if(next+2>last) {
                error=fn->cubic_to(&a,&b,&start,user);
                if(error!=0) return error;
                break;
            }
            Vector to=point(points,next+2,shift,delta);
            error=fn->cubic_to(&a,&b,&to,user);
            if(error!=0) return error;
            cursor=next+2;
        }
contour_done:
        first=contours[contour]+1;
    }
    return 0;
}

/* Native FT_Stroker_ParseOutline 0x569748. Child stroke geometry remains
 * named, typed source contracts; the outline tag walk and exits are C. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern void audio_uart_font_stroker_reset(void *); /* 0x56882a */
extern int32_t audio_uart_font_stroker_begin(void *,const Vector *,uint8_t); /* 0x5694e0 */
extern int32_t audio_uart_font_stroker_line(void *,const Vector *); /* 0x568d86 */
extern int32_t audio_uart_font_stroker_conic(void *,const Vector *,const Vector *); /* 0x568e52 */
extern int32_t audio_uart_font_stroker_cubic(void *,const Vector *,const Vector *,const Vector *); /* 0x569160 */
extern int32_t audio_uart_font_stroker_close(void *); /* 0x5695f8 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static Vector midpoint(Vector a,Vector b) {
    Vector m={(int32_t)(((int64_t)a.x+(int64_t)b.x)/2),
              (int32_t)(((int64_t)a.y+(int64_t)b.y)/2)};
    return m;
}
int32_t audio_uart_font_stroker_parse_outline(void *stroker,const void *outline,
                                                uint32_t opened) {
    if(outline==0) return 20;
    if(stroker==0) return 6;
    audio_uart_font_stroker_reset(stroker);
    int32_t contours=*(const int16_t *)outline;
    const Vector *points=(const Vector *)(uintptr_t)word(outline,4u);
    const uint8_t *tags=(const uint8_t *)(uintptr_t)word(outline,8u);
    const int16_t *ends=(const int16_t *)(uintptr_t)word(outline,12u);
    int32_t first=0;
    for(int32_t c=0;c<contours;c++) {
        int32_t last=ends[c];
        if(first>=last) {first=last+1;continue;}
        Vector start=points[first],end=points[last];
        uint8_t first_tag=tags[first]&3u;
        if(first_tag==2u) return 20;
        int32_t cursor=first;
        if(first_tag==0u) {
            if((tags[last]&3u)==1u) {start=end;last--;}
            else start=midpoint(start,end);
            cursor=first-1;
        }
        int32_t error=audio_uart_font_stroker_begin(stroker,&start,(uint8_t)opened);
        if(error!=0) return error;
        for(;;) {
            if(cursor>=last) break;
            int32_t next=cursor+1;
            uint8_t tag=tags[next]&3u;
            if(tag==1u) {
                Vector to=points[next];
                error=audio_uart_font_stroker_line(stroker,&to);
                if(error!=0) return error;
                cursor=next;continue;
            }
            if(tag==0u) {
                Vector control=points[next];
                for(;;) {
                    if(next>=last) {
                        error=audio_uart_font_stroker_conic(stroker,&control,&start);
                        if(error!=0) return error;
                        goto contour_done;
                    }
                    int32_t after=next+1;
                    uint8_t after_tag=tags[after]&3u;
                    Vector to=points[after];
                    if(after_tag==1u) {
                        error=audio_uart_font_stroker_conic(stroker,&control,&to);
                        if(error!=0) return error;
                        cursor=after;break;
                    }
                    if(after_tag!=0u) return 20;
                    Vector middle=midpoint(control,to);
                    error=audio_uart_font_stroker_conic(stroker,&control,&middle);
                    if(error!=0) return error;
                    control=to;next=after;
                }
                continue;
            }
            if(next+1>last||(tags[next+1]&3u)!=2u) return 20;
            Vector a=points[next],b=points[next+1];
            if(next+2>last) {
                error=audio_uart_font_stroker_cubic(stroker,&a,&b,&start);
                if(error!=0) return error;
                break;
            }
            Vector to=points[next+2];
            error=audio_uart_font_stroker_cubic(stroker,&a,&b,&to);
            if(error!=0) return error;
            cursor=next+2;
        }
contour_done:
        if(((const uint8_t *)stroker)[20u]==0u) {
            int32_t error=audio_uart_font_stroker_close(stroker);
            if(error!=0) return error;
        }
        first=ends[c]+1;
    }
    return 0;
}

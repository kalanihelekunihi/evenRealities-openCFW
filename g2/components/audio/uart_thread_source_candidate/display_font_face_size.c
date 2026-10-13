/* Native FreeType face size API 0x526ca8, 0x526ce4, 0x526d54. */
#include <stdint.h>
extern void audio_uart_font_select_size_metrics(void *,uint32_t); /* native 0x526a9c */
int32_t audio_uart_font_request_size_internal(void *,const void *,uint32_t,uint32_t *); /* 0x526944 */
extern void audio_uart_font_request_size_metrics(void *,const void *); /* native 0x526b04 */
typedef int32_t (*face_size_callback)(void *);
static uint32_t word(const void *base,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)base+offset);
}
int32_t audio_uart_font_face_select_size(void *face,uint32_t index) {
    if(face==0 || (*(uint8_t *)(void *)((uint8_t *)face+8u)&2u)==0u) return 0x23;
    if((int32_t)index<0 || index>=word(face,0x1cu)) return 6;
    const void *driver=(const void *)(uintptr_t)word((const void *)(uintptr_t)word(face,0x60u),0x0cu);
    uint32_t callback=word(driver,0x5cu);
    if(callback==0u) {
        audio_uart_font_select_size_metrics(face,index);
        return 0;
    }
    return ((face_size_callback)(uintptr_t)callback)((void *)(uintptr_t)word(face,0x58u));
}
int32_t audio_uart_font_face_request_size(void *face,const void *request) {
    if(face==0) return 0x23;
    if(request==0 || (int32_t)word(request,4u)<0 ||
       (int32_t)word(request,8u)<0 || *(const uint8_t *)request>4u) return 6;
    void *size=(void *)(uintptr_t)word(face,0x58u);
    void *metrics=(void *)(uintptr_t)word(size,0x28u);
    *(uint32_t *)(void *)((uint8_t *)metrics+0x0cu)=0u;
    const void *driver=(const void *)(uintptr_t)word((const void *)(uintptr_t)word(face,0x60u),0x0cu);
    uint32_t callback=word(driver,0x58u);
    if(callback!=0u)
        return ((face_size_callback)(uintptr_t)callback)(size);
    if((*(uint8_t *)(void *)((uint8_t *)face+8u)&3u)==2u) {
        uint32_t selected=0u;
        int32_t result=audio_uart_font_request_size_internal(face,request,0u,&selected);
        if(result==0) result=audio_uart_font_face_select_size(face,selected);
        return result;
    }
    audio_uart_font_request_size_metrics(face,request);
    return 0;
}
int32_t audio_uart_font_face_load_scalable(void *face,uint32_t width,uint32_t height) {
    uint32_t x=height;
    uint32_t y=height;
    if(width!=0u) { x=width; if(height==0u) y=width; }
    if(x==0u) x=1u;
    if(y==0u) y=1u;
    if(x>0xffffu) x=0xffffu;
    if(y>0xffffu) y=0xffffu;
    uint32_t request[5]={0u,x<<6u,y<<6u,0u,0u};
    return audio_uart_font_face_request_size(face,request);
}

int32_t audio_uart_font_request_size_internal(void *face,const void *request,
                                              uint32_t ignore_width,uint32_t *index) {
    uint8_t *f=(uint8_t *)face;
    const uint8_t *r=(const uint8_t *)request;
    if((f[8u]&2u)==0u) return 0x23;
    if(r[0]!=0u) return 7;
    int32_t x=(int32_t)word(r,4u),y=(int32_t)word(r,8u);
    int32_t x_dpi=(int32_t)word(r,0x0cu),y_dpi=(int32_t)word(r,0x10u);
    if(x_dpi!=0) x=(int32_t)((uint32_t)x_dpi*(uint32_t)x+36u)/72;
    if(y_dpi!=0) y=(int32_t)((uint32_t)y_dpi*(uint32_t)y+36u)/72;
    if(word(r,4u)==0u) x=y;
    if(word(r,8u)==0u) y=x;
    uint32_t x_pixels=((uint32_t)x+0x20u)&~0x3fu;
    uint32_t y_pixels=((uint32_t)y+0x20u)&~0x3fu;
    if(x_pixels==0u || y_pixels==0u) return 0x17;
    uint32_t count=word(f,0x1cu);
    uint8_t *strikes=(uint8_t *)(uintptr_t)word(f,0x20u);
    for(uint32_t i=0u;(int32_t)i<(int32_t)count;i++) {
        uint8_t *strike=strikes+i*0x10u;
        uint32_t sy=(word(strike,0x0cu)+0x20u)&~0x3fu;
        uint32_t sx=(word(strike,8u)+0x20u)&~0x3fu;
        if(y_pixels==sy && (x_pixels==sx || (ignore_width&255u)!=0u)) {
            if(index!=0) *index=i;
            return 0;
        }
    }
    return 0x17;
}

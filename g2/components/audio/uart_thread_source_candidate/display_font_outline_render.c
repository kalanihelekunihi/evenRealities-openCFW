/* Native outline renderer 0x529f8e-0x52a1ee and its 0x529ee8 callbacks. */
#include <stdint.h>
extern int32_t audio_uart_font_face_load_scalable(void *,uint32_t,uint32_t); /* 0x526d54 */
extern int32_t audio_uart_font_load_glyph(void *,uint32_t,uint32_t); /* 0x525574 */
extern int32_t audio_uart_font_embolden_outline(void *,uint32_t); /* 0x527bca */
extern int32_t audio_uart_font_decompose_outline(const void *,const void *,void *); /* 0x527508 */
extern int32_t audio_uart_font_stroker_create(void *,void **); /* 0x5687b6 */
extern void audio_uart_font_stroker_configure(void *,uint32_t,uint8_t,uint8_t,uint32_t); /* 0x5687fe */
extern void audio_uart_font_stroker_destroy(void *); /* 0x568844 */
extern int32_t audio_uart_font_get_glyph(void *,void **); /* 0x567ec8 */
extern int32_t audio_uart_font_stroke_glyph(void **,void *,uint32_t,uint32_t); /* 0x569954 */
extern void audio_uart_font_outline_release(void *,void *); /* 0x52a264 */
extern void *audio_uart_font_outline_context(void); /* 0x4b1fcc */
extern uint32_t audio_uart_font_outline_dispatch(void *,uint32_t,void *); /* 0x529ea2 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x529b2c -> memset */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 -> 0x439be4 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c";
static const char function[]="outline_create";
static uint32_t word(const void *p,uint32_t o) { return *(const uint32_t *)(const void *)((const uint8_t *)p+o); }
static void pair_copy(void *to,const void *from) {
    uint32_t *d=(uint32_t *)to;
    if(from==0) { d[0]=0u;d[1]=0u; }
    else { d[0]=word(from,0u);d[1]=word(from,4u); }
}
static void send_operation(void *outline,uint8_t operation,const void *a,
                           const void *b,const void *c) { /* 0x529ee8 */
    uint8_t packet[40];
    audio_uart_buffer_zero(packet,40u,0u);
    *(uint32_t *)(void *)packet=(uint32_t)(uintptr_t)outline;
    packet[4u]=operation;
    pair_copy(packet+0x10u,a);
    pair_copy(packet+0x18u,b);
    pair_copy(packet+8u,c);
    (void)audio_uart_font_outline_dispatch(audio_uart_font_outline_context(),0x24u,packet);
}
static int32_t move_to(const void *point,void *user) {
    send_operation(user,1u,0,0,point);return 0;
}
static int32_t line_to(const void *point,void *user) {
    send_operation(user,2u,0,0,point);return 0;
}
static int32_t conic_to(const void *control,const void *point,void *user) {
    send_operation(user,4u,control,0,point);return 0;
}
static int32_t cubic_to(const void *control_a,const void *control_b,
                        const void *point,void *user) {
    send_operation(user,3u,control_a,control_b,point);return 0;
}
typedef struct {
    int32_t (*move_to)(const void *,void *);
    int32_t (*line_to)(const void *,void *);
    int32_t (*conic_to)(const void *,const void *,void *);
    int32_t (*cubic_to)(const void *,const void *,const void *,void *);
    int32_t shift,delta;
} OutlineCallbacks;
static const OutlineCallbacks callbacks={move_to,line_to,conic_to,cubic_to,0,0};
static void estimate_outline(const uint8_t *outline,uint32_t *packet) {
    int32_t points=*(const int16_t *)(const void *)(outline+2u);
    int32_t contours=*(const int16_t *)(const void *)outline;
    const uint8_t *tags=(const uint8_t *)(uintptr_t)word(outline,8u);
    uint32_t vertices=0u,bytes=0u;
    for(int32_t i=0;i<points;i++) {
        if((tags[i]&1u)!=0u) { vertices++;bytes++; }
        else if(i+1<points && (tags[i+1]&1u)==0u) { vertices++;bytes+=2u; }
        else bytes++;
    }
    packet[8u]=(uint32_t)((int32_t)vertices+contours);
    packet[9u]=(uint32_t)(((int32_t)bytes+contours)*2);
}
void *audio_uart_font_outline_render(void *context,void *face,uint32_t glyph_index,
                                     uint32_t size,uint32_t embolden,void *stroke_width) {
    if(context==0) {
        audio_uart_lvgl_log(3u,source,0x138u,function,
            "Asserted at expression: %s (%s)","ctx != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u; /* native fault loop */
    }
    int32_t error=audio_uart_font_face_load_scalable(face,0u,size);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0x13fu,function,"FT_Set_Char_Size error(0x%x)",error);
        return 0;
    }
    error=audio_uart_font_load_glyph(face,glyph_index,0x8008u);
    if(error!=0) {
        audio_uart_lvgl_log(3u,source,0x14bu,function,"FT_Load_Glyph error(0x%x)",error);
        return 0;
    }
    uint8_t *slot=(uint8_t *)(uintptr_t)word(face,0x54u);
    if(embolden!=0u) {
        error=audio_uart_font_embolden_outline(slot+0x6cu,embolden<<6u);
        if(error!=0)
            audio_uart_lvgl_log(3u,source,0x153u,function,
                                "FT_Outline_Embolden error(0x%x)",error);
    }
    uint32_t packet[10];
    audio_uart_buffer_zero(packet,40u,0u);
    uint32_t width=(uint32_t)(uintptr_t)stroke_width;
    for(uint32_t pass=0u;pass<(width==0u?1u:2u);pass++) {
        uint8_t outline[20];
        if(pass==0u) audio_uart_checksum_copy(outline,slot+0x6cu,20u);
        else {
            void *stroker=0;
            (void)audio_uart_font_stroker_create((void *)(uintptr_t)word(context,0u),&stroker);
            audio_uart_font_stroker_configure(stroker,width<<6u,1u,0u,0u);
            void *original=0;
            (void)audio_uart_font_get_glyph(slot,&original);
            (void)audio_uart_font_stroke_glyph(&original,stroker,0u,1u);
            void *stroked=original;
            audio_uart_font_stroker_destroy(stroker);
            audio_uart_checksum_copy(outline,(uint8_t *)stroked+0x14u,20u);
        }
        estimate_outline(outline,packet);
        uint32_t dispatched=audio_uart_font_outline_dispatch(context,0x28u,packet);
        void *created=(void *)(uintptr_t)packet[0];
        if((uint8_t)dispatched!=1u || created==0) {
            audio_uart_lvgl_log(3u,source,0x1b1u,function,"Outline object create failed");
            return 0;
        }
        error=audio_uart_font_decompose_outline(outline,&callbacks,created);
        if(error!=0) {
            audio_uart_lvgl_log(3u,source,0x1b9u,function,
                                "FT_Outline_Decompose error(0x%x)",error);
            audio_uart_font_outline_release(context,created);
            return 0;
        }
        if(pass==0u && width!=0u) {
            /* Native operation 5 closes the first contour before the stroked pass. */
            uint32_t command[10];
            audio_uart_buffer_zero(command,40u,0u);
            command[0]=(uint32_t)(uintptr_t)created;
            ((uint8_t *)command)[4u]=5u;
            if((uint8_t)audio_uart_font_outline_dispatch(audio_uart_font_outline_context(),
                                                         0x24u,command)!=1u) {
                audio_uart_lvgl_log(3u,source,0x1c4u,function,"Outline object close failed");
                audio_uart_font_outline_release(context,created);
                return 0;
            }
            continue;
        }
        uint32_t command[10];
        audio_uart_buffer_zero(command,40u,0u);
        command[0]=(uint32_t)(uintptr_t)created;
        if((uint8_t)audio_uart_font_outline_dispatch(audio_uart_font_outline_context(),
                                                     0x24u,command)!=1u) {
            audio_uart_lvgl_log(3u,source,0x1d0u,function,"Outline object close failed");
            audio_uart_font_outline_release(context,created);
            return 0;
        }
    }
    return (void *)(uintptr_t)packet[0];
}

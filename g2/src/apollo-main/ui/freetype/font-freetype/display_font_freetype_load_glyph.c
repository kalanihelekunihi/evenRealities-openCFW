/* Native FT_Load_Glyph 0x525574-0x525832. Driver, hinter and renderer methods
 * are called through the FreeType objects that own them. */
#include <stdint.h>
extern void audio_uart_font_glyphslot_clear(void *); /* 0x5252bc */
extern const char *audio_uart_font_get_format(void *); /* 0x524b64 */
extern int32_t audio_uart_font_outline_check(void *); /* 0x52798c */
extern void audio_uart_font_grid_fit_metrics(void *,uint32_t); /* 0x5254c8 */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* 0x524606 */
extern void *audio_uart_font_slot_renderer(void *); /* 0x527096 */
extern void audio_uart_font_outline_transform(void *,void *); /* 0x527ba0 */
extern void audio_uart_font_outline_translate(void *,int32_t,int32_t); /* 0x527b2e */
extern void audio_uart_font_vector_transform(void *,void *); /* 0x527b60 */
extern int32_t audio_uart_font_render_glyph(void *,uint32_t); /* 0x527228 */
extern void audio_uart_font_preset_bitmap(void *,uint32_t,const void *); /* 0x5250de */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
static uint32_t bit(uint32_t value,uint32_t number) { return (value>>number)&1u; }
static uint32_t is_type_one(const char *name) {
    static const char expected[]="Type 1"; /* authenticated ROM0x78d634 */
    if(name==0) return 0;
    for(uint32_t i=0u;;i++) {
        if(name[i]!=(char)expected[i]) return 0;
        if(name[i]==0) return 1;
    }
}
int32_t audio_uart_font_load_glyph(void *face,uint32_t index,uint32_t flags) {
    if(face==0 || word(face,0x58u)==0u || word(face,0x54u)==0u) return 0x23;
    uint8_t *slot=(uint8_t *)(uintptr_t)word(face,0x54u);
    audio_uart_font_glyphslot_clear(slot);
    uint8_t *driver=(uint8_t *)(uintptr_t)word(face,0x60u);
    uint8_t *library=(uint8_t *)(uintptr_t)word(driver,4u);
    uint8_t *hinter=(uint8_t *)(uintptr_t)word(library,0xa0u);
    if(bit(flags,10u)!=0u) flags|=0x801u;
    if(bit(flags,0u)!=0u) flags=(flags|0xau)&~4u;
    if(bit(flags,22u)!=0u) flags&=~4u;
    uint8_t *internal=(uint8_t *)(uintptr_t)word(face,0x80u);
    uint32_t driver_flags=word((void *)(uintptr_t)word(driver,0u),0u);
    uint32_t face_flags=word(face,8u);
    uint32_t use_hinter=0u;
    if(hinter!=0 && (flags&0x8002u)==0u && (driver_flags&0x300u)==0x100u &&
       bit(face_flags,13u)==0u &&
       (bit(flags,11u)!=0u ||
        (word(internal,8u)==0u && word(internal,0u)!=0u) ||
        (word(internal,0u)==0u && word(internal,8u)!=0u))) {
        if(bit(flags,5u)!=0u || bit(driver_flags,10u)==0u) use_hinter=1u;
        else {
            uint32_t type_one=is_type_one(audio_uart_font_get_format(face)) && word(driver,0x1cu)==1u;
            uint32_t target=(flags>>16u)&0xfu;
            if((target==1u && bit(driver_flags,11u)==0u && !type_one) ||
               (bit(face_flags,3u)!=0u && word(face,0x2d4u)!=0u &&
                *(uint16_t *)(void *)((uint8_t *)face+0x11eu)==0u &&
                word(face,0x288u)==0u && word(face,0x290u)==0u)) use_hinter=1u;
        }
    }
    int32_t error=0;
    if(use_hinter!=0u) {
        if(bit(face_flags,1u)==0u && bit(flags,3u)==0u) {
            uint8_t *driver_class=(uint8_t *)(uintptr_t)word(driver,0x0cu);
            uint32_t load=word(driver_class,0x48u);
            error=((int32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)load)(
                slot,(void *)(uintptr_t)word(face,0x58u),index,flags|0x4000u);
            if(error==0 && word(slot,0x48u)==0x62697473u) goto loaded;
        }
        uint32_t saved=word(internal,0x18u);
        store(internal,0x18u,0u);
        uint8_t *hinter_module=(uint8_t *)(uintptr_t)word(hinter,0u);
        uint8_t *hinter_class=(uint8_t *)(uintptr_t)word(hinter_module,0x14u);
        uint32_t load=word(hinter_class,0x0cu);
        error=((int32_t (*)(void *,void *,void *,uint32_t))(uintptr_t)load)(
            hinter,slot,(void *)(uintptr_t)word(face,0x58u),index);
        store(internal,0x18u,saved);
    } else {
        uint8_t *driver_class=(uint8_t *)(uintptr_t)word(driver,0x0cu);
        uint32_t load=word(driver_class,0x48u);
        error=((int32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)load)(
            slot,(void *)(uintptr_t)word(face,0x58u),index,flags);
        if(error!=0) return error;
        if(word(slot,0x48u)==0x6f75746cu) {
            error=audio_uart_font_outline_check(slot+0x6cu);
            if(error!=0) return error;
            if(bit(flags,1u)==0u) audio_uart_font_grid_fit_metrics(slot,flags&0x10u);
        }
    }
loaded:
    if(bit(flags,4u)!=0u) {
        store(slot,0x40u,0u);
        store(slot,0x44u,word(slot,0x34u));
    } else {
        store(slot,0x40u,word(slot,0x28u));
        store(slot,0x44u,0u);
    }
    if(bit(flags,13u)==0u && bit(face_flags,0u)!=0u) {
        void *size=(void *)(uintptr_t)word(face,0x58u);
        store(slot,0x38u,(uint32_t)audio_uart_font_mul_div((int32_t)word(slot,0x38u),
                       (int32_t)word(size,0x10u),0x40));
        store(slot,0x3cu,(uint32_t)audio_uart_font_mul_div((int32_t)word(slot,0x3cu),
                       (int32_t)word(size,0x14u),0x40));
    }
    if(bit(flags,11u)==0u && word(internal,0x18u)!=0u) {
        void *renderer=audio_uart_font_slot_renderer(slot);
        if(renderer!=0) {
            uint8_t *clazz=(uint8_t *)(uintptr_t)word(renderer,0x0cu);
            uint32_t transform=word(clazz,0x2cu);
            error=((int32_t (*)(void *,void *,void *,void *))(uintptr_t)transform)(
                renderer,slot,internal,internal+0x10u);
        } else if(word(slot,0x48u)==0x6f75746cu) {
            if(bit(word(internal,0x18u),0u)!=0u)
                audio_uart_font_outline_transform(slot+0x6cu,internal);
            if(bit(word(internal,0x18u),1u)!=0u)
                audio_uart_font_outline_translate(slot+0x6cu,
                    (int32_t)word(internal,0x10u),(int32_t)word(internal,0x14u));
        }
        audio_uart_font_vector_transform(slot+0x40u,internal);
    }
    uint32_t format=word(slot,0x48u);
    if(error==0 && bit(flags,0u)==0u && format!=0x62697473u && format!=0x636f6d70u) {
        uint32_t mode=(flags>>16u)&0xfu;
        if(mode==0u && bit(flags,12u)!=0u) mode=2u;
        if(bit(flags,2u)!=0u) error=audio_uart_font_render_glyph(slot,mode);
        else audio_uart_font_preset_bitmap(slot,mode,0u);
    }
    return error;
}

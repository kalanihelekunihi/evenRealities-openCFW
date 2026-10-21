/* Native LVGL 0x44c5d4 get_local_style and 0x482868 lv_style_set_prop.
 * Object style records are eight bytes; style values are four bytes and
 * properties one byte in the product's LVGL configuration. */
#include <stdint.h>
extern void *audio_uart_lv_realloc_44f76a(void *,uint32_t);
extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char style_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_style.c";
static const char misc_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_style.c";
static void lv_fatal(void) { for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u; }
static uint16_t rd16(const uint8_t *p) { uint16_t v;__builtin_memcpy(&v,p,2u);return v; }
static uint32_t rd32(const uint8_t *p) { uint32_t v;__builtin_memcpy(&v,p,4u);return v; }
static void wr16(uint8_t *p,uint16_t v) { __builtin_memcpy(p,&v,2u); }
static void wr32(uint8_t *p,uint32_t v) { __builtin_memcpy(p,&v,4u); }

void *audio_uart_page_style_local_44c5d4(void *object,uint32_t selector) {
    uint8_t *obj=(uint8_t *)object;
    uint16_t bits=rd16(obj+0x2au);
    uint32_t count=(bits>>4)&0x3fu;
    uint8_t *entries=(uint8_t *)(uintptr_t)rd32(obj+0x0cu);
    for(uint32_t i=0;i<count;i++) {
        uint32_t tag=rd32(entries+i*8u+4u);
        if((tag&0x01000000u)!=0u && (tag&0x00ffffffu)==selector)
            return (void *)(uintptr_t)rd32(entries+i*8u);
    }
    uint32_t next=(count+1u)&0x3fu;
    wr16(obj+0x2au,(uint16_t)((bits&~0x03f0u)|(next<<4)));
    if(next==0u) {
        audio_uart_lvgl_log(3u,style_path,0x2c2u,"get_local_style",
                            "Asserted at expression: %s","obj->style_cnt != 0");
        lv_fatal();
    }
    entries=(uint8_t *)audio_uart_lv_realloc_44f76a(entries,next*8u);
    wr32(obj+0x0cu,(uint32_t)(uintptr_t)entries);
    if(entries==0) {
        audio_uart_lvgl_log(3u,style_path,0x2c4u,"get_local_style",
                            "Asserted at expression: %s (%s)","obj->styles != NULL","Out of memory");
        lv_fatal();
    }
    uint32_t pos=next-1u;
    while(pos>0u) {
        uint32_t prev=rd32(entries+(pos-1u)*8u+4u);
        if((prev&0x03000000u)!=0u)break;
        __builtin_memcpy(entries+pos*8u,entries+(pos-1u)*8u,8u);
        pos--;
    }
    audio_uart_buffer_zero(entries+pos*8u,8u,0u);
    uint8_t *style=(uint8_t *)audio_uart_lv_heap_alloc(12u);
    wr32(entries+pos*8u,(uint32_t)(uintptr_t)style);
    audio_uart_buffer_zero(style,12u,0u);
    wr32(entries+pos*8u+4u,0x01000000u|(selector&0x00ffffffu));
    return style;
}

void audio_uart_page_style_value_482868(void *style,uint32_t prop,uint32_t value) {
    uint8_t *s=(uint8_t *)style;
    if(s[8u]==0xffu) {
        audio_uart_lvgl_log(3u,misc_path,0x14cu,"lv_style_set_prop",
                            "Cannot set property of constant style");
        return;
    }
    uint8_t property=(uint8_t)prop;
    if(property==0u) {
        audio_uart_lvgl_log(3u,misc_path,0x150u,"lv_style_set_prop",
                            "Asserted at expression: %s","prop != LV_STYLE_PROP_INV");
        lv_fatal();
    }
    uint32_t count=s[8u];
    uint8_t *items=(uint8_t *)(uintptr_t)rd32(s);
    if(items!=0) {
        for(uint32_t i=count;i>0u;i--) {
            if(items[count*4u+i-1u]==property) {
                wr32(items+(i-1u)*4u,value);
                return;
            }
        }
    }
    items=(uint8_t *)audio_uart_lv_realloc_44f76a(items,(count+1u)*5u);
    if(items==0)return;
    wr32(s,(uint32_t)(uintptr_t)items);
    for(uint32_t i=count;i>0u;i--)
        items[(count+1u)*4u+i-1u]=items[count*4u+i-1u];
    count++;
    s[8u]=(uint8_t)count;
    items[count*4u+count-1u]=property;
    wr32(items+(count-1u)*4u,value);
    uint32_t group=property>>2;
    if(group>31u)group=31u;
    wr32(s+4u,rd32(s+4u)|(1u<<group));
}

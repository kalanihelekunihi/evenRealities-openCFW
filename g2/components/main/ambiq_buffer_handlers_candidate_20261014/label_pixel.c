/* Apollo Ambiq label callback, native 0x53fcc4..0x53ffe9. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
extern uint32_t audio_uart_ambiq_color_resolve_4b06a8(uint32_t,uint8_t);
extern void audio_uart_ambiq_label_rect_copy_53fa94(uint32_t *,const uint32_t *);
extern void audio_uart_ambiq_area_move_450bb2(void *,int32_t,int32_t);
extern uint32_t audio_uart_ambiq_label_width_aligned_53faba(uint32_t,uint32_t);
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern uint32_t audio_uart_ambiq_glyph_bitmap_4d5612(uint32_t,uint32_t);
extern void audio_uart_ambiq_label_glyph_blit_53fb18(uint32_t,void *,uint32_t,
    uint32_t,const int32_t *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_ambiq_image_options_init_488918(void *);
extern void audio_uart_ambiq_draw_image_53f42a(void *,const void *,const void *);
extern void audio_uart_ambiq_label_vector_dispatch_53d6ea(void *,void *);
extern void display_driver_gpu_mode_4b0730(uint32_t,uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_ambiq_label_fill_rectangle_4b1ab0(uint32_t,uint32_t,
    uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_nema_cl_get_bound_5144fa(void);
extern void audio_uart_nema_cl_submit_514cf2(uint32_t);
extern void audio_uart_nema_cl_wait_514d00(uint32_t);
extern void audio_uart_nema_cl_rewind_514384(uint32_t);

static const char pixel_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_letter.c";
static const char pixel_function[]="draw_letter_cb";
static const char pixel_both[]=
    "Both fill and glyph draw descriptors are not NULL, use the glyph draw descriptor";
static const char pixel_slow[]=
    "CPU GPU sync required for unaligned bitmap, Slow down the performance!";
static const char pixel_missing[]="Glyph data is NULL";
static uint32_t rd32(const void *p) { return *(const uint32_t *)p; }
static uint16_t rd16(const void *p) { return *(const uint16_t *)p; }
static uint32_t rgb(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16);
}

void audio_uart_ambiq_label_pixel_53fcc4(void *unit,void *glyph,
                                           const void *fill,const void *fill_area) {
    const uint8_t *u=(const uint8_t *)unit;
    uint8_t *g=(uint8_t *)glyph;
    const uint8_t *f=(const uint8_t *)fill;
    const uint8_t *fa=(const uint8_t *)fill_area;
    uint32_t gpu=rd32(u+0x4cu);
    const uint8_t *draw= (const uint8_t *)(uintptr_t)rd32(u+0x48u);
    uint32_t color=0u;
    uint32_t needs_sync=0u;
    if(f==0 && g==0) return;
    if(f!=0 && g!=0)
        audio_uart_lvgl_log(2u,pixel_path,0xa5u,pixel_function,pixel_both);
    if(g==0) {
        color=audio_uart_ambiq_color_resolve_4b06a8(rgb(f+0x21u),f[0x20u]);
    } else {
        color=audio_uart_ambiq_color_resolve_4b06a8(rgb(g+0x14u),g[0x17u]);
        uint32_t format=(uint32_t)g[4u];
        if(format!=0u) {
            if((format>=1u && format<=4u)||format==8u||format==17u||
               format==18u||format==20u||format==24u) {
                uint8_t *header=(uint8_t *)(uintptr_t)rd32(g+0x10u);
                uint8_t *bitmap=(uint8_t *)(uintptr_t)rd32(header);
                uint32_t bitmap_address=rd32(bitmap+0x18u);
                const uint8_t *bitmap_data=(const uint8_t *)(uintptr_t)bitmap_address;
                uint32_t clip[4];
                audio_uart_ambiq_label_rect_copy_53fa94(clip,
                    (const uint32_t *)(uintptr_t)rd32(g+8u));
                audio_uart_ambiq_area_move_450bb2(clip,
                    -(int32_t)rd32(draw+4u),-(int32_t)rd32(draw+8u));
                uint32_t width=rd16(header+6u),height=rd16(header+8u);
                if(0x80000001u<=bitmap_address) g2_norflash_lock_46f65e();
                uint32_t row_mode=(rd16(bitmap_data+0x12u)>>14)==3u;
                uint32_t aligned=row_mode?1u:
                    audio_uart_ambiq_label_width_aligned_53faba(width,header[0xeu]);
                uint32_t compact=(rd32(bitmap+4u)==0x4b239du) &&
                    ((rd16(bitmap_data+0x12u)>>14)==0u||row_mode);
                if(0x80000001u<=bitmap_address) g2_norflash_unlock_46f674();
                if((int8_t)g[4u]==3) compact=0u;
                if(compact && (aligned || (width*height<0x7ffu))) {
                    header[0x14u]|=1u;
                    uint32_t image=audio_uart_ambiq_glyph_bitmap_4d5612(
                        (uint32_t)(uintptr_t)header,0u);
                    *(uint32_t *)g=image;
                    audio_uart_ambiq_label_glyph_blit_53fb18(gpu,
                        (void *)(uintptr_t)image,width,height,(int32_t *)clip,
                        header[0xeu],color,aligned?1u:0u,aligned?row_mode:0u);
                    needs_sync=(0x80000001u<=bitmap_address);
                } else {
                    audio_uart_lvgl_log(2u,pixel_path,0x10du,pixel_function,pixel_slow);
                    header[0x14u]&=(uint8_t)~1u;
                    uint32_t cache=rd32(g+0x2cu);
                    uint32_t image=audio_uart_ambiq_glyph_bitmap_4d5612(
                        (uint32_t)(uintptr_t)header,cache);
                    *(uint32_t *)g=image;
                    if(image==0u) {
                        audio_uart_lvgl_log(2u,pixel_path,0x111u,pixel_function,pixel_missing);
                    } else {
                        uint32_t cache_image=rd32((const void *)(uintptr_t)(cache+0x10u));
                        audio_uart_ambiq_label_glyph_blit_53fb18(gpu,
                            (void *)(uintptr_t)cache_image,width,height,(int32_t *)clip,
                            8u,color,1u,0u);
                        needs_sync=1u;
                    }
                }
            } else if(format==0x19u) {
                uint32_t options[0x6cu/4u];
                audio_uart_ambiq_image_options_init_488918(options);
                options[0x30u/4u]=0u;
                options[0x34u/4u]=0x100u;
                options[0x38u/4u]=0x100u;
                ((uint8_t *)options)[0x50u]=g[0x17u];
                options[0x1cu/4u]=rd32(g);
                audio_uart_ambiq_draw_image_53f42a(unit,options,
                    (const void *)(uintptr_t)rd32(g+8u));
            } else if(format==0x1au) {
                audio_uart_ambiq_label_vector_dispatch_53d6ea(unit,glyph);
            }
        }
    }
    if(f!=0 && fa!=0) {
        display_driver_gpu_mode_4b0730(gpu,0x504u);
        uint32_t clip[4];
        audio_uart_ambiq_label_rect_copy_53fa94(clip,(const uint32_t *)fa);
        audio_uart_ambiq_area_move_450bb2(clip,
            -(int32_t)rd32(draw+4u),-(int32_t)rd32(draw+8u));
        uint32_t height=audio_uart_lv_area_height_4515a4(clip);
        uint32_t width=audio_uart_lv_area_width_451598(clip);
        audio_uart_ambiq_label_fill_rectangle_4b1ab0(clip[0],clip[1],
            width,height,color);
    }
    if(needs_sync) {
        uint8_t *header=(uint8_t *)(uintptr_t)rd32(g+0x10u);
        uint8_t *bitmap=(uint8_t *)(uintptr_t)rd32(header);
        uint32_t bound=audio_uart_nema_cl_get_bound_5144fa();
        uint32_t bitmap_address=rd32(bitmap+0x18u);
        if(0x80000001u<=bitmap_address) g2_norflash_lock_46f65e();
        audio_uart_nema_cl_submit_514cf2(bound);
        audio_uart_nema_cl_wait_514d00(bound);
        if(0x80000001u<=bitmap_address) g2_norflash_unlock_46f674();
        audio_uart_nema_cl_rewind_514384(bound);
    }
}

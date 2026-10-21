/* Apollo Ambiq image entry at 0x53f42a..0x53f545. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
extern void audio_uart_ambiq_draw_image_core_53f548(void *,const void *,void *);

static const char image_source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_img.c";
static const char image_function_name[] = "lv_draw_ambiq_image";
static const char image_blend_error[] =
    "GPU failed, not supported blend mode!";
static const char image_tile_effect_error[] =
    "Set rotation/scale/skew effect to tile image is not supported! We will ignore these parameters.";
static const char image_tile_shape_error[] =
    "The hight and width of tile texture is not power of 2, draw it one by one! ";
static const char image_tile_radius_error[] =
    "Set clip_radius parameter to a tiled image is not supported! ignore it! ";
static const char image_tile_mask_error[] =
    "Set mask to a tiled image is not supported! ignore it! ";

static uint32_t image_read32(const uint8_t *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)(p+offset);
}
static uint32_t image_power_of_two(uint32_t x) {
    return x != 0u && (x & (x-1u)) == 0u;
}
static void image_log(uint32_t line,const char *message) {
    audio_uart_lvgl_log(2u,image_source_path,line,image_function_name,message);
}

void audio_uart_ambiq_draw_image_53f42a(void *unit,const void *descriptor,
                                         void *draw_area) {
    const uint8_t *p=(const uint8_t *)descriptor;
    const uint32_t blend=p[0x51u]&7u;
    if (blend==2u || blend==3u) {
        image_log(0x4au,image_blend_error);
        return;
    }
    const uint32_t transformed=image_read32(p,0x30u)!=0u ||
        image_read32(p,0x34u)!=0x100u ||
        image_read32(p,0x38u)!=0x100u ||
        image_read32(p,0x40u)!=0u ||
        image_read32(p,0x3cu)!=0u;
    const uint32_t tiled=(*(const uint16_t *)(const void *)(p+0x50u)&0x1000u)!=0u;
    if (tiled) {
        if (transformed) image_log(0x55u,image_tile_effect_error);
        const uint32_t dimensions=image_read32(p,0x24u);
        if (!image_power_of_two(dimensions&0xffffu) ||
            !image_power_of_two(dimensions>>16))
            image_log(0x60u,image_tile_shape_error);
        if (image_read32(p,0x2cu)!=0u)
            image_log(0x65u,image_tile_radius_error);
        if (image_read32(p,0x68u)!=0u)
            image_log(0x6au,image_tile_mask_error);
    }
    audio_uart_ambiq_draw_image_core_53f548(unit,descriptor,draw_area);
}

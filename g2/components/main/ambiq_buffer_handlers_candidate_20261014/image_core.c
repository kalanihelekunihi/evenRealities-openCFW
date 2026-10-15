/* Apollo Ambiq image core at 0x53f548..0x53fa5f. Candidate under native comparison. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_uart_ambiq_color_resolve_4b06a8(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_decode_image_4b0f50(const void *,uint32_t,void *,uint32_t);
extern uint32_t audio_uart_ambiq_image_options_4b0d38(uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_mask_options_4b0ea6(uint32_t,uint32_t);
extern void audio_uart_ambiq_image_color_513e4c(uint32_t);
extern uint32_t audio_uart_nema_stencil_save_52266e(uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_nema_stencil_restore_5226b2(uint32_t);
extern void display_driver_gpu_enable_4b0748(uint32_t,uint32_t);
extern void display_driver_gpu_position_4b1b48(int32_t,int32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_uart_lv_rect_set_width_450b6c(void *,int32_t);
extern void audio_uart_lv_rect_set_height_450b76(void *,int32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern void audio_uart_nema_matrix_identity_561810(float *);
extern void audio_uart_nema_matrix_translate_561856(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_scale_5618b8(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_rotate_561964(float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_shear_561902(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_copy_561830(float *,const float *);
extern void audio_uart_nema_matrix_finalize_561b38(float *);
extern void audio_uart_nema_matrix_upload_5226e8(const float *);
extern void audio_uart_nema_matrix_point_561ad4(const float *,float *,float *);
extern void audio_uart_nema_draw_quad_522db4(float,float,float,float,
                                              float,float,float,float)
    __attribute__((pcs("aapcs-vfp")));
extern uint32_t audio_uart_nema_cl_get_bound_5144fa(void);
extern void audio_uart_nema_cl_submit_514cf2(uint32_t);
extern void audio_uart_nema_cl_wait_514d00(uint32_t);
extern void audio_uart_nema_cl_rewind_514384(uint32_t);
extern void audio_uart_lv_image_decoder_close_48908c(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char image_core_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_img.c";
static const char image_core_name[] = "lv_draw_ambiq_image_core";
static const char image_core_open_failed[] = "Failed to open image";
static const char image_core_mask_failed[] =
    "MASK image decode failed. Drawing the image without mask.";
static const char image_core_mask_size[] =
    "GPU limitation, mask size should be same as the texture size or the framebuffer size! draw it without mask.";

static uint32_t image_core_read32(const uint8_t *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)(p+offset);
}
static uint32_t image_core_pow2(uint32_t n) {
    return n!=0u && (n&(n-1u))==0u;
}
static void image_core_log(uint32_t severity,uint32_t line,const char *message) {
    audio_uart_lvgl_log(severity,image_core_path,line,image_core_name,message);
}

void audio_uart_ambiq_draw_image_core_53f548(
        void *unit,const void *descriptor,const int32_t *draw_area) {
    const uint8_t *d=(const uint8_t *)descriptor;
    uint8_t *u=(uint8_t *)unit;
    const uint32_t dimensions=image_core_read32(d,0x24u);
    const uint32_t width=dimensions&0xffffu;
    const uint32_t height=dimensions>>16;
    const uint32_t tiled=(d[0x51u]&0x10u)!=0u;
    const uint32_t tile_one_by_one=tiled &&
        (!image_core_pow2(width) || !image_core_pow2(height));
    const uint32_t mode=(tiled && !tile_one_by_one)?4u:8u;
    const uint32_t transformed=
        image_core_read32(d,0x30u)!=0u ||
        image_core_read32(d,0x34u)!=0x100u ||
        image_core_read32(d,0x38u)!=0x100u ||
        image_core_read32(d,0x40u)!=0u ||
        image_core_read32(d,0x3cu)!=0u;
    uint32_t color=0u;
    audio_queue_copy_bytes(&color,d+0x4cu,3u);
    const uint32_t resolved_color=audio_uart_ambiq_color_resolve_4b06a8(
        color,d[0x4fu]);
    uint8_t decoded[76];
    if ((audio_uart_ambiq_decode_image_4b0f50(
            (const void *)(uintptr_t)image_core_read32(d,0x1cu),
            transformed,decoded,0u)&0xffu)!=1u) {
        image_core_log(3u,0x9bu,image_core_open_failed);
        return;
    }
    audio_queue_copy_bytes(&color,d+0x4cu,3u);
    const uint32_t second_color=audio_uart_ambiq_color_resolve_4b06a8(
        color,d[0x50u]);
    uint32_t flags=audio_uart_ambiq_image_options_4b0d38(
        image_core_read32(decoded,44u),second_color,mode);
    uint8_t mask_decoded[76];
    uint32_t mask_ok=0u;
    uint32_t mask_buffer=0u;
    if (image_core_read32(d,0x68u)!=0u) {
        if ((audio_uart_ambiq_decode_image_4b0f50(
                (const void *)(uintptr_t)image_core_read32(d,0x68u),
                0u,mask_decoded,1u)&0xffu)==1u) {
            mask_ok=1u;
            mask_buffer=image_core_read32(mask_decoded,44u);
            const uint32_t mask_dimensions=
                *(const uint32_t *)(uintptr_t)(mask_buffer+4u);
            if (mask_dimensions!=dimensions) {
                image_core_log(2u,0xb7u,image_core_mask_size);
                mask_buffer=0u;
            }
        } else image_core_log(2u,0xacu,image_core_mask_failed);
    }
    uint32_t mask_flags=0u;
    if (mask_buffer!=0u)
        mask_flags=audio_uart_ambiq_mask_options_4b0ea6(mask_buffer,1u);
    const uint32_t layer=image_core_read32(u,0x48u);
    const uint32_t blend=d[0x51u]&7u;
    uint32_t layer_flags=blend==1u?0x101u:
        (*(const uint8_t *)(uintptr_t)(layer+0x14u)==16u?0x4000501u:0x504u);
    flags|=mask_flags|layer_flags;
    const uint32_t format=(image_core_read32(d,0x20u)>>8)&0xffu;
    if (d[0x4fu]>2u && (format<11u || format>14u)) {
        flags|=0x100000u;
        audio_uart_ambiq_image_color_513e4c(resolved_color);
    }
    const uint32_t stencil=(d[0x51u]&8u)!=0u;
    const uint32_t stencil_state=audio_uart_nema_stencil_save_52266e(
        stencil,stencil,stencil,stencil);
    display_driver_gpu_enable_4b0748(image_core_read32(u,0x4cu),flags);
    if (transformed) {
        float matrix[9],matrix_copy[9];
        audio_uart_nema_matrix_identity_561810(matrix);
        audio_uart_nema_matrix_translate_561856(
            (float)-(int32_t)image_core_read32(d,0x44u),
            (float)-(int32_t)image_core_read32(d,0x48u),matrix);
        audio_uart_nema_matrix_scale_5618b8(
            (float)(int32_t)image_core_read32(d,0x34u)/256.0f,
            (float)(int32_t)image_core_read32(d,0x38u)/256.0f,matrix);
        audio_uart_nema_matrix_rotate_561964(
            (float)(int32_t)image_core_read32(d,0x30u)/10.0f,matrix);
        audio_uart_nema_matrix_shear_561902(
            (float)(int32_t)image_core_read32(d,0x3cu)/10.0f,
            (float)(int32_t)image_core_read32(d,0x40u)/10.0f,matrix);
        audio_uart_nema_matrix_translate_561856(
            (float)(int32_t)image_core_read32(d,0x44u),
            (float)(int32_t)image_core_read32(d,0x48u),matrix);
        audio_uart_nema_matrix_translate_561856(
            (float)(draw_area[0]-*(const int32_t *)(uintptr_t)(layer+4u)),
            (float)(draw_area[1]-*(const int32_t *)(uintptr_t)(layer+8u)),matrix);
        audio_uart_nema_matrix_copy_561830(matrix_copy,matrix);
        audio_uart_nema_matrix_finalize_561b38(matrix);
        audio_uart_nema_matrix_upload_5226e8(matrix);
        float x0=0.0f,y0=0.0f;
        float x1=(float)(int32_t)audio_uart_lv_area_width_451598(draw_area)-1.0f;
        float y1=0.0f;
        float x2=(float)(int32_t)audio_uart_lv_area_width_451598(draw_area)-1.0f;
        float y2=(float)(int32_t)audio_uart_lv_area_height_4515a4(draw_area)-1.0f;
        float x3=0.0f;
        float y3=(float)(int32_t)audio_uart_lv_area_height_4515a4(draw_area)-1.0f;
        audio_uart_nema_matrix_point_561ad4(matrix_copy,&x0,&y0);
        audio_uart_nema_matrix_point_561ad4(matrix_copy,&x1,&y1);
        audio_uart_nema_matrix_point_561ad4(matrix_copy,&x2,&y2);
        audio_uart_nema_matrix_point_561ad4(matrix_copy,&x3,&y3);
        audio_uart_nema_draw_quad_522db4(x0,y0,x1,y1,x2,y2,x3,y3);
    } else if (tile_one_by_one) {
        int32_t tile[4];
        if ((int32_t)audio_uart_lv_area_width_451598(d+0x58u)<0)
            audio_uart_checksum_copy(tile,draw_area,16u);
        else audio_uart_checksum_copy(tile,d+0x58u,16u);
        audio_uart_lv_rect_set_width_450b6c(tile,(int32_t)width);
        audio_uart_lv_rect_set_height_450b76(tile,(int32_t)width);
        const int32_t start_x=tile[0];
        for (;tile[1]<=draw_area[3];tile[1]+=(int32_t)width,tile[3]+=(int32_t)width) {
            for (;tile[0]<=draw_area[2];tile[0]+=(int32_t)width,tile[2]+=(int32_t)width) {
                int32_t intersection[4];
                if (audio_uart_lv_area_intersect_450bcc(intersection,tile,draw_area)!=0u)
                    display_driver_gpu_position_4b1b48(
                        tile[0]-*(const int32_t *)(uintptr_t)(layer+4u),
                        tile[1]-*(const int32_t *)(uintptr_t)(layer+8u));
            }
            tile[0]=start_x;tile[2]=start_x+(int32_t)width-1;
        }
    } else {
        display_driver_gpu_position_4b1b48(
            draw_area[0]-*(const int32_t *)(uintptr_t)(layer+4u),
            draw_area[1]-*(const int32_t *)(uintptr_t)(layer+8u));
    }
    if (stencil) audio_uart_nema_stencil_restore_5226b2(stencil_state);
    const uint32_t command=audio_uart_nema_cl_get_bound_5144fa();
    audio_uart_nema_cl_submit_514cf2(command);
    audio_uart_nema_cl_wait_514d00(command);
    audio_uart_nema_cl_rewind_514384(command);
    audio_uart_lv_image_decoder_close_48908c(decoded);
    if (mask_ok) audio_uart_lv_image_decoder_close_48908c(mask_decoded);
}

/* Complete native4c7b24..4c7e22. Unselected pending native comparisons.
 * Native literal/string4c7e24..4c7e28 is not executable code. */
#include <stdint.h>
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *);
extern void audio_uart_lv_bin_decoder_data_free_4c8210(void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *,const char *,uint32_t);
extern uint32_t audio_uart_lv_bin_decode_compressed_4c8a2c(void *,void *);
extern uint32_t audio_uart_lv_bin_load_indexed_4c8570(void *,void *);
extern uint32_t audio_uart_lv_bin_decode_indexed_4c8256(void *,void *);
extern uint32_t audio_uart_lv_bin_decode_alpha_4c887c(void *,void *);
extern uint32_t audio_uart_lv_bin_decode_rgb_4c8780(void *,void *);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern uint32_t audio_uart_lv_draw_buf_from_image_48b762(void *,const void *);
extern void audio_uart_lv_draw_buf_set_flag_48b750(void *,uint32_t);
extern void *audio_uart_lv_decoder_postprocess_489168(void *,void *);
extern uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void);
extern void *audio_uart_lv_decoder_add_cache_48911a(void *,const void *,void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
uint32_t audio_uart_lv_bin_decoder_open_4c7b24(void *decoder,void *descriptor)
{
    volatile uint32_t *d=descriptor;
    volatile uint8_t *db=descriptor;
    uint32_t result=0u,use_direct=0u;
    if(db[16]==1u) {
        const char *src=(void *)(uintptr_t)d[3];
        if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bin")!=0) return 0u;
        volatile uint32_t *data=audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor);
        if(data==0) return 0u;
        d[18]=(uint32_t)(uintptr_t)data;
        void *file=audio_uart_lv_malloc(12u);
        if(file==0) {audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);return 0u;}
        uint32_t fs=audio_uart_lv_fs_file_open_4c6d9a(file,(void *)(uintptr_t)d[3],2u);
        if((uint8_t)fs!=0u) {
            audio_uart_lvgl_log(2u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c",213u,"lv_bin_decoder_open","Open file failed: %d",(uint8_t)fs);
            audio_uart_lv_heap_free(file);audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);return 0u;
        }
        data[0]=(uint32_t)(uintptr_t)file;
        uint32_t cf=(uint8_t)(d[8]>>8);
        if(d[8]&(1u<<19)) result=audio_uart_lv_bin_decode_compressed_4c8a2c(decoder,descriptor);
        else if(cf-7u<4u) result=db[7]?audio_uart_lv_bin_load_indexed_4c8570(decoder,descriptor):audio_uart_lv_bin_decode_indexed_4c8256(decoder,descriptor);
        else if(cf-11u<4u) result=audio_uart_lv_bin_decode_alpha_4c887c(decoder,descriptor);
        else if(cf==16u||cf==17u||cf==15u||cf==18u||cf==20u||cf==19u) result=audio_uart_lv_bin_decode_rgb_4c8780(decoder,descriptor);
    } else if(db[16]==0u) {
        volatile uint32_t *image=(void *)(uintptr_t)d[3];
        if(image[4]==0u) return 0u;
        result=image[0]>>8;
        uint32_t cf=(uint8_t)result;
        if(d[8]&(1u<<19)) result=audio_uart_lv_bin_decode_compressed_4c8a2c(decoder,descriptor);
        else if(cf-7u<4u) {
            if(audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor)==0) return 0u;
            if(db[7]) {result=audio_uart_lv_bin_load_indexed_4c8570(decoder,descriptor);use_direct=1u;}
            else result=audio_uart_lv_bin_decode_indexed_4c8256(decoder,descriptor);
        } else if(cf-11u<4u && cf!=14u) {
            if(audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor)==0) return 0u;
            result=audio_uart_lv_bin_decode_alpha_4c887c(decoder,descriptor);
        } else {
            uint8_t *data=audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor);
            volatile uint32_t *decoded;
            if(image[0]&(1u<<20)) {decoded=image;result=1u;}
            else {
                decoded=(void *)(data+36u);
                if((uint16_t)image[2]==0u) {
                    uint32_t tmp[7];audio_uart_checksum_copy(tmp,(const void *)image,28u);
                    uint32_t bits=(uint8_t)audio_uart_lv_color_bpp_440f44(cf);
                    uint32_t stride=(uint32_t)((int32_t)(bits*(uint16_t)tmp[1]+7u)>>3);
                    tmp[2]=(tmp[2]&0xffff0000u)|(uint16_t)stride;
                    result=audio_uart_lv_draw_buf_from_image_48b762((void *)decoded,tmp);
                } else result=audio_uart_lv_draw_buf_from_image_48b762((void *)decoded,(const void *)image);
            }
            if((uint8_t)result==1u) {
                d[11]=(uint32_t)(uintptr_t)decoded;
                if((uint16_t)decoded[2]==0u) decoded[2]=(decoded[2]&0xffff0000u)|(uint16_t)d[10];
                use_direct=1u;
            }
        }
    }
    if((uint8_t)result!=1u) {audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);return (uint8_t)result;}
    if(d[11]==0u) return 1u;
    void *decoded=(void *)(uintptr_t)d[11];
    if(d[8]&(1u<<16)) audio_uart_lv_draw_buf_set_flag_48b750(decoded,1u);
    volatile uint32_t *adjusted=audio_uart_lv_decoder_postprocess_489168(descriptor,decoded);
    if(adjusted==0) {audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);return 0u;}
    if((void *)adjusted!=decoded) {
        use_direct=0u;audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);
        volatile uint32_t *data=audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor);data[7]=(uint32_t)(uintptr_t)adjusted;
    }
    d[11]=(uint32_t)(uintptr_t)adjusted;
    if((uint8_t)use_direct!=0u || db[6]!=0u) return 1u;
    if(audio_uart_lv_image_cache_enabled_4d4b24()==0u) return 1u;
    struct { uint32_t size; uint32_t source; uint8_t source_type; uint8_t padding[3]; } key;
    _Static_assert(sizeof(key)==12u,"Native cache key size");
    key.source_type=db[16];key.source=d[3];key.size=((volatile uint32_t *)(uintptr_t)d[11])[3];
    void *entry=audio_uart_lv_decoder_add_cache_48911a(decoder,&key,(void *)(uintptr_t)d[11],(void *)(uintptr_t)d[18]);
    if(entry==0) {audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);return 0u;}
    d[17]=(uint32_t)(uintptr_t)entry;
    volatile uint32_t *data=audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor);data[7]=0u;
    return 1u;
}

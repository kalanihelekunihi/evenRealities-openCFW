#include <stdint.h>
extern void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_tell_4c7018(void *,uint32_t *);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_bin_decompress_image_4c8d8c(void *,void *);
extern uint32_t audio_uart_lv_bin_load_indexed_4c8570(void *,void *);
extern uint32_t audio_uart_lv_bin_decode_indexed_4c8256(void *,void *);
extern uint32_t audio_uart_lv_bin_decode_alpha_4c887c(void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4c7940..4c794c; R0 scratch is not a return contract. */
void audio_uart_lv_bin_memzero_4c7940(void *object,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(object,0u,size);
}
/* Full native4c8a2c..4c8c8a, including statically present post-decode dispatch.
 * Locked decompress_image currently always fails; no codec success implied. */
uint32_t audio_uart_lv_bin_decode_compressed_4c8a2c(void *decoder,void *descriptor)
{
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor);
    volatile uint32_t *compressed=(volatile uint32_t *)((uintptr_t)data+12u);
    void *file_buffer=0;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[]="decode_compressed";
    audio_uart_lv_bin_memzero_4c7940((void *)compressed,16u);
    if(((volatile uint8_t *)descriptor)[16]==1u) {
        void *file=(void *)(uintptr_t)data[0];
        uint32_t length;
        if(audio_uart_lv_fs_file_seek_4c6fba(file,0u,2u)!=0u || audio_uart_lv_fs_file_tell_4c7018(file,&length)!=0u) {
            audio_uart_lvgl_log(2u,source,933u,function,"Failed to get compressed file len");return 0u;
        }
        length-=12u;length-=12u;
        uint32_t count;
        uint32_t result=audio_uart_lv_fs_read_at_4c8d3c(file,12u,(void *)compressed,12u,&count);
        if((uint8_t)result!=0u || count!=12u) {
            audio_uart_lvgl_log(2u,source,944u,function,"Read compressed header failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,12u);return 0u;
        }
        if(compressed[1]!=length) {
            audio_uart_lvgl_log(2u,source,949u,function,"Compressed size mismatch: %u != %u",compressed[1],length);return 0u;
        }
        file_buffer=audio_uart_lv_malloc(length);
        if(file_buffer==0) {audio_uart_lvgl_log(2u,source,955u,function,"No memory for compressed file");return 0u;}
        result=audio_uart_lv_fs_file_read_4c6f46(file,file_buffer,length,&count);
        if((uint8_t)result!=0u || count!=length) {
            audio_uart_lvgl_log(2u,source,964u,function,"Read compressed file failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,length);
            audio_uart_lv_heap_free(file_buffer);return 0u;
        }
        compressed[3]=(uint32_t)(uintptr_t)file_buffer;
    } else if(((volatile uint8_t *)descriptor)[16]==0u) {
        volatile uint32_t *image=(volatile uint32_t *)(uintptr_t)d[3];
        uint32_t length=image[3]-12u;
        audio_uart_lv_grid_copy_454738((void *)compressed,(void *)(uintptr_t)image[4],12u);
        compressed[3]=image[4]+12u;
        if(compressed[1]!=length) {
            audio_uart_lvgl_log(2u,source,982u,function,"Compressed size mismatch: %u != %u",compressed[1],length);return 0u;
        }
    } else {audio_uart_lvgl_log(2u,source,987u,function,"Compressed image only support file or variable");return 0u;}
    uint32_t result=audio_uart_lv_bin_decompress_image_4c8d8c(descriptor,(void *)compressed);
    compressed[3]=0u;
    audio_uart_lv_heap_free(file_buffer);
    if((uint8_t)result!=1u) {audio_uart_lvgl_log(2u,source,995u,function,"Decompress failed");return 0u;}
    volatile uint32_t *image=(volatile uint32_t *)(uintptr_t)d[3];
    if(((volatile uint8_t *)descriptor)[16]==0u && image[4]==0u) return 0u;
    uint8_t cf=(uint8_t)(d[8]>>8u);
    if((uint32_t)cf-7u<4u) {
        if(((volatile uint8_t *)descriptor)[7]!=0u) result=audio_uart_lv_bin_load_indexed_4c8570(decoder,descriptor);
        else result=audio_uart_lv_bin_decode_indexed_4c8256(decoder,descriptor);
    } else if((uint32_t)cf-11u<4u) result=audio_uart_lv_bin_decode_alpha_4c887c(decoder,descriptor);
    else {d[11]=data[8];data[7]=data[8];data[8]=0u;result=1u;}
    return (uint8_t)result;
}

#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_tell_4c7018(void *,uint32_t *);
extern uint32_t audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t,void *,uint32_t,uint32_t,const void *,void *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4c8256..4c8554; literal pool excluded. */
uint32_t audio_uart_lv_bin_decode_indexed_4c8256(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    void *file=(void *)(uintptr_t)data[0];
    uint8_t cf=(uint8_t)(d[8]>>8u);
    uint32_t entries;
    switch(cf) {case 7:entries=2u;break;case 8:entries=4u;break;case 9:entries=16u;break;case 10:entries=256u;break;default:entries=0u;break;}
    uint32_t palette_len=entries*4u;
    void *indexed=0,*palette;
    uintptr_t input;
    uint32_t compressed=(d[8]>>19u)&1u;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[]="decode_indexed";
    if(compressed!=0u) {
        void *decompressed=(void *)(uintptr_t)data[8];
        palette=(void *)(uintptr_t)((volatile uint32_t *)decompressed)[4];
        input=(uintptr_t)palette+palette_len;
    } else if(((volatile uint8_t *)descriptor)[16]==1u) {
        palette=audio_uart_lv_malloc(palette_len);
        if(palette==0) {
            audio_uart_lvgl_log(3u,source,588u,function,"Asserted at expression: %s (%s)","palette != NULL","Out of memory");
            for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if(palette==0) {audio_uart_lvgl_log(3u,source,590u,function,"Out of memory");return 0u;}
        uint32_t count;
        uint32_t result=audio_uart_lv_fs_read_at_4c8d3c(file,12u,palette,palette_len,&count);
        if((uint8_t)result!=0u || count!=palette_len) {
            audio_uart_lvgl_log(2u,source,596u,function,"Read palette failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,palette_len);
            audio_uart_lv_heap_free(palette);return 0u;
        }
        data[1]=(uint32_t)(uintptr_t)palette;
        uint32_t stride=(uint16_t)d[10];
        indexed=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)d[9],d[9]>>16u,cf,stride);
        if(indexed==0) {audio_uart_lvgl_log(3u,source,607u,function,"Draw buffer alloc failed");goto cleanup;}
        input=((volatile uint32_t *)indexed)[4];
        uint32_t length=0u;
        if(audio_uart_lv_fs_file_seek_4c6fba(file,0u,2u)!=0u || audio_uart_lv_fs_file_tell_4c7018(file,&length)!=0u) {
            audio_uart_lvgl_log(2u,source,616u,function,"Failed to get file to size");goto cleanup;
        }
        uint32_t offset=palette_len+12u;length-=offset;
        result=audio_uart_lv_fs_read_at_4c8d3c(file,offset,(void *)input,length,&count);
        if((uint8_t)result!=0u || count!=length) {
            audio_uart_lvgl_log(2u,source,624u,function,"Read indexed image failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,length);goto cleanup;
        }
    } else if(((volatile uint8_t *)descriptor)[16]==0u) {
        volatile uint32_t *image=(volatile uint32_t *)(uintptr_t)d[3];
        palette=(void *)(uintptr_t)image[4];input=(uintptr_t)image[4]+palette_len;
    } else return 0u;
    d[12]=(uint32_t)(uintptr_t)palette;d[13]=entries;
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)d[9],d[9]>>16u,16u,0u);
    if(decoded==0) {audio_uart_lvgl_log(3u,source,647u,function,"No memory for indexed image");goto cleanup;}
    uint32_t out_stride=(uint16_t)((volatile uint32_t *)decoded)[2];
    uintptr_t output=((volatile uint32_t *)decoded)[4];
    for(uint32_t y=0u;y<(d[9]>>16u);++y) {
        audio_uart_lv_bin_decode_indexed_line_4c8c94(cf,(void *)(uintptr_t)d[12],0u,(uint16_t)d[9],(const void *)input,(void *)output);
        input+=(uint16_t)d[10];output+=out_stride;
    }
    d[11]=(uint32_t)(uintptr_t)decoded;data[7]=(uint32_t)(uintptr_t)decoded;
    if(((volatile uint8_t *)descriptor)[16]==1u && compressed==0u) {
        data[1]=(uint32_t)(uintptr_t)palette;audio_uart_font_bitmap_release(indexed);
    }
    return 1u;
cleanup:
    if(((volatile uint8_t *)descriptor)[16]==1u && compressed==0u) {
        audio_uart_lv_heap_free(palette);data[1]=0u;
    }
    if(indexed!=0) audio_uart_font_bitmap_release(indexed);
    return 0u;
}

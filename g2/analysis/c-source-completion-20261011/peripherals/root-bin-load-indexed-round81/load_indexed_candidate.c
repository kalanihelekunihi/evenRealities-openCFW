#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_draw_buf_from_image_48b762(void *,const void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_tell_4c7018(void *,uint32_t *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4c8570..4c8778; saved data/file and fresh header loads retained. */
uint32_t audio_uart_lv_bin_load_indexed_4c8570(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if((d[8]&0x00080000u)!=0u) {
        d[11]=data[8];data[7]=data[8];data[8]=0u;return 1u;
    }
    if(((volatile uint8_t *)descriptor)[16]==0u) {
        volatile uint32_t *image=(volatile uint32_t *)(uintptr_t)d[3];
        volatile uint32_t *decoded;
        if((image[0]&0x00100000u)!=0u) decoded=image;
        else {
            decoded=data+9;
            uint32_t result=audio_uart_lv_draw_buf_from_image_48b762((void *)decoded,(void *)image);
            if((uint8_t)result!=1u) return (uint8_t)result;
        }
        d[11]=(uint32_t)(uintptr_t)decoded;
        if((uint16_t)decoded[2]==0u) decoded[2]=(decoded[2]&0xffff0000u)|(uint16_t)d[10];
        return 1u;
    }
    if(((volatile uint8_t *)descriptor)[16]==1u) {
        uint32_t cf=d[8]>>8u;
        void *file=(void *)(uintptr_t)data[0];
        uint32_t stride=(uint16_t)d[10];
        void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,
            (uint16_t)d[9],d[9]>>16u,(uint8_t)cf,stride);
        if(decoded==0) {
            audio_uart_lvgl_log(3u,source,742u,"load_indexed","Draw buffer alloc failed");return 0u;
        }
        uintptr_t pixels=((volatile uint32_t *)decoded)[4];
        uint32_t palette;
        switch((uint8_t)cf) {case 7:palette=8u;break;case 8:palette=16u;break;case 9:palette=64u;break;case 10:palette=1024u;break;default:palette=0u;break;}
        uint32_t count;
        uint32_t result=audio_uart_lv_fs_read_at_4c8d3c(file,12u,(void *)pixels,palette,&count);
        if((uint8_t)result!=0u || count!=palette) {
            audio_uart_lvgl_log(2u,source,750u,"load_indexed","Read palette failed: %d, with len: %u, expected: %u",
                (uint32_t)(uint8_t)result,count,palette);
            audio_uart_font_bitmap_release(decoded);return 0u;
        }
        uint32_t length=0u;
        if(audio_uart_lv_fs_file_seek_4c6fba(file,0u,2u)!=0u || audio_uart_lv_fs_file_tell_4c7018(file,&length)!=0u) {
            audio_uart_lvgl_log(2u,source,758u,"load_indexed","Failed to get file to size");
            audio_uart_font_bitmap_release(decoded);return 0u;
        }
        uint32_t offset=palette+12u;
        length-=offset;
        result=audio_uart_lv_fs_read_at_4c8d3c(file,offset,(void *)(pixels+palette),length,&count);
        if((uint8_t)result!=0u || count!=length) {
            audio_uart_lvgl_log(2u,source,768u,"load_indexed","Read indexed image failed: %d, with len: %u, expected: %u",
                (uint32_t)(uint8_t)result,count,length);
            audio_uart_font_bitmap_release(decoded);return 0u;
        }
        data[7]=(uint32_t)(uintptr_t)decoded;d[11]=(uint32_t)(uintptr_t)decoded;return 1u;
    }
    audio_uart_lvgl_log(3u,source,778u,"load_indexed","Unknown src type: %d",(uint32_t)((volatile uint8_t *)descriptor)[16]);
    return 0u;
}

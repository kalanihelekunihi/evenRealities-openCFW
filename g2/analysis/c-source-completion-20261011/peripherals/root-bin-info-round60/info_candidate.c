/* Full native4c79d0..4c7b1c. Invocation: unused decoder, descriptor,
 * header. Descriptor src12/src_type16/file20. Header12 bytes.
 * Candidate remains unselected until compiled/native qualification. */
#include <stdint.h>
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
uint32_t audio_uart_lv_bin_decoder_info_4c79d0(void *decoder,void *descriptor,void *header)
{
    (void)decoder;
    volatile uint8_t *dsc=descriptor;
    volatile uint32_t *h=header;
    const char *src=(void *)(uintptr_t)*(volatile uint32_t *)(dsc+12u);
    uint8_t type=dsc[16];
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[]="lv_bin_decoder_info";
    if(type==0u) {
        audio_uart_lv_grid_copy_454738(header,src,12u);
    } else if(type==1u) {
        if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bin") != 0) return 0u;
        uint32_t rn;
        uint32_t res=audio_uart_lv_fs_file_read_4c6f46((void *)(dsc+20u),header,12u,&rn);
        if((uint8_t)res != 0u || rn != 12u) {
            audio_uart_lvgl_log(2u,source,134u,function,"Read file header failed: %d with len: %u, expected: %zu",(uint8_t)res,rn,12u);
            return 0u;
        }
        if(*(volatile uint8_t *)header != 25u) {
            audio_uart_lvgl_log(2u,source,144u,function,"Legacy bin image detected: %s",src);
            uint32_t magic=*(volatile uint8_t *)header;
            h[0]=(h[0]&0xffff00ffu)|(magic<<8);
            h[0]=(h[0]&0xffffff00u)|25u;
        }
        uint32_t flags=h[0]>>16;
        h[0]=(h[0]&0xffffu)|((flags|32u)<<16);
    } else if(type==2u) {
        h[1]=(h[1]&0xffff0000u)|1u;
        h[1]=(h[1]&0xffffu)|0x10000u;
        h[0]=(h[0]&0xffff00ffu)|(14u<<8);
    } else {
        audio_uart_lvgl_log(2u,source,162u,function,"Image get info found unknown src type");
        return 0u;
    }
    if(((h[0]>>8)&255u)==0u) {
        audio_uart_lvgl_log(2u,source,167u,function,"Image color format is unknown");
        return 0u;
    }
    if(*(volatile uint8_t *)header != 25u) {
        uint32_t flags=h[0]>>16;
        h[0]=(h[0]&0xffffu)|((flags&~1u)<<16);
    }
    return 1u;
}

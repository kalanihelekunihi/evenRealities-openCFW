/* Complete native4c7e4c..4c81a2. Unselected pending native comparisons.
 * Arithmetic follows native 32-bit wrapping and unsigned shifts. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern void audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t,void *,uint32_t,uint32_t,const void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
uint32_t audio_uart_lv_bin_decoder_get_area_4c7e4c(void *decoder,void *descriptor,const void *full_area,void *decoded_area)
{
    (void)decoder;
    volatile uint32_t *d=descriptor,*a=decoded_area;
    const volatile uint32_t *full=full_area;
    volatile uint8_t *db=descriptor;
    uint32_t cf=(uint8_t)(d[8]>>8);
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if(!(cf-7u<4u||cf==16u||cf==17u||cf==15u||cf==18u||cf==19u||cf==20u)) {
        audio_uart_lvgl_log(2u,source,405u,"lv_bin_decoder_get_area","CF: %d is not supported",cf);return 0u;
    }
    volatile uint32_t *data=(void *)(uintptr_t)d[18];
    if(data==0) {audio_uart_lvgl_log(3u,source,412u,"lv_bin_decoder_get_area","Unexpected null decoder data");return 0u;}
    void *file=(void *)(uintptr_t)data[0];
    uint32_t bpp=audio_uart_lv_color_bpp_440f44(cf);
    uint32_t width=audio_uart_lv_area_width_451598(full_area);
    uint32_t offset=db[16]==1u?12u:0u;
    volatile uint32_t *decoded;
    if(a[1]==0xe0000001u) {
        uint32_t decoded_cf=cf-7u<4u?16u:cf;
        decoded=audio_uart_lv_draw_buf_reshape_48b196((void *)(uintptr_t)data[16],decoded_cf,width,1u,0u);
        if(decoded==0) {
            if(data[16]!=0u) {audio_uart_font_bitmap_release((void *)(uintptr_t)data[16]);data[16]=0u;}
            decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,width,1u,decoded_cf,0u);
            if(decoded==0) return 0u;
            data[16]=(uint32_t)(uintptr_t)decoded;
        }
        audio_uart_checksum_copy(decoded_area,full_area,16u);a[3]=a[1];
    } else {
        a[1]=a[1]+1u;a[3]=a[3]+1u;decoded=(void *)(uintptr_t)data[16];
    }
    void *img=(void *)(uintptr_t)decoded[4];
    if((int32_t)a[1]>(int32_t)full[3]) return 0u;
    if(cf-7u<4u) {
        uint32_t fraction=a[0]%(8u/bpp);
        uint32_t length=((bpp*width+7u)>>3)+1u;
        offset+=d[13]<<2;
        offset+=(uint16_t)d[10]*a[1];
        offset+=(bpp*a[0])>>3;
        void *buffer;
        if(db[16]==1u) {
            buffer=audio_uart_lv_malloc(length);
            if(buffer==0) {
                audio_uart_lvgl_log(3u,source,463u,"lv_bin_decoder_get_area","Asserted at expression: %s (%s)","buf != NULL","NULL pointer");
                for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
            }
            if(buffer==0) return 0u;
            if((uint8_t)audio_uart_lv_fs_read_at_4c8d3c(file,offset,buffer,length,0)!=0u) {audio_uart_lv_heap_free(buffer);return 0u;}
        } else {
            volatile uint32_t *image=(void *)(uintptr_t)d[3];buffer=(void *)(uintptr_t)(image[4]+offset);
        }
        audio_uart_lv_bin_decode_indexed_line_4c8c94(cf,(void *)(uintptr_t)d[12],fraction,width,buffer,img);
        if(db[16]==1u) audio_uart_lv_heap_free(buffer);
        d[11]=(uint32_t)(uintptr_t)decoded;return 1u;
    }
    if(cf==16u||cf==17u||cf==15u||cf==18u||cf==19u) {
        uint32_t length=(bpp*width)>>3;
        offset+=(uint16_t)d[10]*a[1];offset+=(bpp*a[0])>>3;
        if((uint8_t)audio_uart_lv_fs_read_at_4c8d3c(file,offset,img,length,0)!=0u) return 0u;
        d[11]=(uint32_t)(uintptr_t)decoded;return 1u;
    }
    if(cf==20u) {
        uint32_t length=(uint16_t)decoded[2];
        offset+=(uint16_t)d[10]*a[1];offset+=(16u*a[0])>>3;
        if((uint8_t)audio_uart_lv_fs_read_at_4c8d3c(file,offset,img,length,0)!=0u) return 0u;
        offset=12u+(uint16_t)d[10]*(d[9]>>16);
        offset+=((uint16_t)d[10]/2u)*a[1];offset+=a[0];
        if((uint8_t)audio_uart_lv_fs_read_at_4c8d3c(file,offset,(void *)((uintptr_t)img+length),width,0)!=0u) return 0u;
        d[11]=(uint32_t)(uintptr_t)decoded;return 1u;
    }
    return 0u;
}

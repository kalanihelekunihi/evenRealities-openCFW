#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
/* Native4c93a0..4c947c; signed row bound, unsigned wrap/shift offsets. */
uint32_t audio_uart_lv_bmp_get_area_4c93a0(void *decoder,void *descriptor,const void *full_area,void *decoded_area) {
    (void)decoder;
    volatile uint32_t *d=descriptor,*area=decoded_area;
    const volatile uint32_t *full=full_area;
    volatile uint32_t *state=(void *)(uintptr_t)d[18];
    void *decoded=(void *)(uintptr_t)d[11];
    if(area[1]==0xe0000001u) {
        audio_uart_checksum_copy(decoded_area,full_area,16u);
        area[3]=area[1];
        uint32_t width=audio_uart_lv_area_width_451598(full_area);
        void *reshaped=audio_uart_lv_draw_buf_reshape_48b196(decoded,(uint8_t)(d[8]>>8),width,1u,0u);
        if(reshaped==0) {
            if(decoded!=0) {
                audio_uart_font_bitmap_release(decoded);
                d[11]=0u;
            }
            decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,width,1u,(uint8_t)(d[8]>>8),0u);
            if(decoded==0)return 0u;
        } else decoded=reshaped;
        d[11]=(uint32_t)(uintptr_t)decoded;
    } else {
        area[1]=area[1]+1u;
        area[3]=area[3]+1u;
    }
    if((int32_t)full[3]<(int32_t)area[1])return 0u;
    uint32_t row=state[5]-1u-area[1];
    uint32_t offset=row*state[7]+state[3];
    offset+=(state[6]>>3)*area[0];
    (void)audio_uart_lv_fs_file_seek_4c6fba((void *)state,offset,0u);
    uint32_t width=audio_uart_lv_area_width_451598(full_area);
    uint32_t length=(state[6]>>3)*width;
    void *pixels=(void *)(uintptr_t)((volatile uint32_t *)decoded)[4];
    (void)audio_uart_lv_fs_file_read_4c6f46((void *)state,pixels,length,0);
    return 1u;
}

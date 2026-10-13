/* Native LV startup children from pinned LVGL v9.3 root layout. Every
 * address below is an authenticated offset within RAM0x2006f548. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_array_init_482b00(uint8_t *,uint32_t);
extern void audio_uart_lv_draw_handlers_default_48aa80(void *);
extern void audio_uart_lv_async_init_4d465c(void *);
extern void audio_uart_lv_display_init_4645d8(uint32_t);
extern void audio_uart_lv_anim_init_4d46de(void *);
extern uint32_t audio_uart_lv_image_cache_init_4d4ad4(uint32_t);
extern uint32_t audio_uart_lv_image_header_cache_init_4d4bdc(uint32_t);

void audio_uart_lv_init_memory_48aa60(void)
{
    uint8_t *root=audio_uart_display_lv_root;
    audio_uart_lv_draw_handlers_default_48aa80(root+0xc8u);
    audio_uart_lv_draw_handlers_default_48aa80(root+0xe8u);
    audio_uart_lv_draw_handlers_default_48aa80(root+0x108u);
}
void audio_uart_lv_init_async_49acb0(void)
{
    audio_uart_lv_async_init_4d465c(audio_uart_display_lv_root+0x1d0u);
}
void audio_uart_lv_init_display_464330(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x74u,0x18u);
    audio_uart_lv_display_init_4645d8(1u);
}
void audio_uart_lv_init_indev_4c6d8c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x180u,4u);
}
void audio_uart_lv_init_style_44d32c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x34u,0x20u);
}
void audio_uart_lv_init_anim_48438c(void)
{
    audio_uart_lv_anim_init_4d46de(audio_uart_display_lv_root+0x148u);
}
void audio_uart_lv_init_cache_44b90c(void)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x18u,0x14u);
}
void audio_uart_lv_image_decoder_init_488f4c(uint32_t primary,uint32_t secondary)
{
    audio_uart_lv_array_init_482b00(audio_uart_display_lv_root+0x128u,0x1cu);
    audio_uart_lv_image_cache_init_4d4ad4(primary);
    audio_uart_lv_image_header_cache_init_4d4bdc(secondary);
}

/* Full native4c6d04..4c6d62: lv_span_stack_init, not timer init.
 * LVGL v9.3 snippet allocation is1796 bytes; root offset452.
 * The configured native assert logs and faults atUINT32_MAX forever.
 * Its following allocation-error log is unreachable after that assert. */
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
void audio_uart_lv_span_stack_init_4c6d04(void)
{
    static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\span\\lv_span.c";
    static const char function[] = "lv_span_stack_init";
    void *stack = audio_uart_lv_malloc(1796u);
    *(volatile uint32_t *)(void *)(audio_uart_display_lv_root+452u) = (uint32_t)(uintptr_t)stack;
    if(stack == 0) {
        audio_uart_lvgl_log(3u,source,100u,function,
                           "Asserted at expression: %s (%s)","stack != NULL","Out of memory");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    if(stack == 0) audio_uart_lvgl_log(3u,source,102u,function,"malloc failed for snippet_stack");
}

/* Full native488f40..488f4c: zeroing wrapper; native scratch R0 is void. */
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
void audio_uart_lv_image_memzero_488f40(void *object,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(object,0u,size);
}
/* Full native4890c8..48911a: decoder node, configured assert,28-byte clear. */
extern void *audio_uart_lv_list_prepend_482b12(uint32_t *);
void *audio_uart_lv_image_decoder_create_4890c8(void)
{
    static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_image_decoder.c";
    void *decoder = audio_uart_lv_list_prepend_482b12(
        (uint32_t *)(void *)(audio_uart_display_lv_root+0x128u));
    if(decoder == 0) {
        audio_uart_lvgl_log(3u,source,179u,"lv_image_decoder_create",
                           "Asserted at expression: %s (%s)","decoder != NULL","Out of memory");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    if(decoder == 0) return 0;
    audio_uart_lv_image_memzero_488f40(decoder,28u);
    return decoder;
}
/* Address-only callback declarations: invocation signatures remain a gate. */
uint32_t audio_uart_lv_bin_decoder_info_4c79d0(void *,void *,void *);
uint32_t audio_uart_lv_bin_decoder_open_4c7b24(void *,void *);
uint32_t audio_uart_lv_bin_decoder_get_area_4c7e4c(void *,void *,const void *,void *);
void audio_uart_lv_bin_decoder_close_4c7e28(void *,void *);
/* Full native4c794c..4c79ce: lv_bin_decoder_init, not filesystem init. */
void audio_uart_lv_bin_decoder_init_4c794c(void)
{
    static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[] = "lv_bin_decoder_init";
    static const char name[] = "BIN";
    uint8_t *decoder = audio_uart_lv_image_decoder_create_4890c8();
    if(decoder == 0) {
        audio_uart_lvgl_log(3u,source,100u,function,
                           "Asserted at expression: %s (%s)","decoder != NULL","Out of memory");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    if(decoder == 0) {
        audio_uart_lvgl_log(2u,source,102u,function,"Out of memory");
        return;
    }
    *(volatile uint32_t *)(void *)(decoder+0u) = (uint32_t)(uintptr_t)audio_uart_lv_bin_decoder_info_4c79d0;
    *(volatile uint32_t *)(void *)(decoder+4u) = (uint32_t)(uintptr_t)audio_uart_lv_bin_decoder_open_4c7b24;
    *(volatile uint32_t *)(void *)(decoder+8u) = (uint32_t)(uintptr_t)audio_uart_lv_bin_decoder_get_area_4c7e4c;
    *(volatile uint32_t *)(void *)(decoder+12u) = (uint32_t)(uintptr_t)audio_uart_lv_bin_decoder_close_4c7e28;
    *(volatile uint32_t *)(void *)(decoder+20u) = (uint32_t)(uintptr_t)name;
}

/* Native4c8210..4c8256: full free_decoder_data. Preserve fresh field
 * reads after children: the filesystem close callback may mutate its owner. */
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_font_bitmap_release(void *); /* lv_draw_buf_destroy48b216 */
void audio_uart_lv_bin_decoder_data_free_4c8210(void *descriptor)
{
    volatile uint32_t *dsc = descriptor;
    volatile uint32_t *data = (void *)(uintptr_t)dsc[18];
    if(data == 0) return;
    if(data[0] != 0u) {
        audio_uart_lv_fs_file_close_4c6ee0((void *)(uintptr_t)data[0]);
        audio_uart_lv_heap_free((void *)(uintptr_t)data[0]);
    }
    if(data[7] != 0u) audio_uart_font_bitmap_release((void *)(uintptr_t)data[7]);
    if(data[8] != 0u) audio_uart_font_bitmap_release((void *)(uintptr_t)data[8]);
    audio_uart_lv_heap_free((void *)(uintptr_t)data[1]);
    audio_uart_lv_heap_free((void *)data);
    dsc[18] = 0u;
}
/* Native4c7e28..4c7e4a: full close callback. Decoder argument unused.
 * Saved data owner survives draw-buffer child mutations. */
void audio_uart_lv_bin_decoder_close_4c7e28(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *dsc = descriptor;
    volatile uint32_t *data = (void *)(uintptr_t)dsc[18];
    if(data != 0 && data[16] != 0u) {
        audio_uart_font_bitmap_release((void *)(uintptr_t)data[16]);
        data[16] = 0u;
    }
    audio_uart_lv_bin_decoder_data_free_4c8210(descriptor);
}

/* Full native4c6ee0..4c6f46, LVGL lv_fs_close. File words:
 * file_d0, driver4, cache8; driver cache_size4, close_cb16;
 * cache buffer12. Native result is truncated to8 bits. */
extern void audio_uart_lv_heap_free(void *);
uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *file)
{
    volatile uint32_t *f = file;
    if(f[1] == 0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[4] == 0u) return 9u;
    uint32_t file_data = f[0];
    uint32_t driver = f[1];
    uint32_t callback = ((volatile uint32_t *)(uintptr_t)f[1])[4];
    uint32_t result = ((uint32_t (*)(void *,void *))(uintptr_t)callback)
        ((void *)(uintptr_t)driver,(void *)(uintptr_t)file_data);
    if(((volatile uint32_t *)(uintptr_t)f[1])[1] != 0u && f[2] != 0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[1] != UINT32_MAX &&
           ((volatile uint32_t *)(uintptr_t)f[2])[3] != 0u) {
            audio_uart_lv_heap_free((void *)(uintptr_t)((volatile uint32_t *)(uintptr_t)f[2])[3]);
        }
        audio_uart_lv_heap_free((void *)(uintptr_t)f[2]);
    }
    f[0] = 0u;
    f[1] = 0u;
    f[2] = 0u;
    return (uint8_t)result;
}

/* Full native4c79d0..4c7b1c. Invocation: unused decoder, descriptor,
 * header. Descriptor src12/src_type16/file20. Header12 bytes.
 * Qualified by528 compiled ARM/native comparisons. */
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

extern uint32_t g2_log_module_length(const char *); /* selected44a43c */
extern int32_t audio_uart_font_path_compare(const char *,const char *); /* selected46cacc */
/* Full native454768..454770. */
uint32_t audio_uart_lv_string_length_454768(const char *source)
{
    return g2_log_module_length(source);
}
/* Full native4547be..4547c6. */
int32_t audio_uart_lv_string_compare_4547be(const char *a,const char *b)
{
    return audio_uart_font_path_compare(a,b);
}
/* Full native4c70e4..4c7116. Index0 deliberately excluded by native loop. */
const char *audio_uart_lv_fs_extension_4c70e4(const char *source)
{
    static const char empty[]="";
    uint32_t i=audio_uart_lv_string_length_454768(source);
    while(i != 0u) {
        if((uint8_t)source[i]==46u) return source+i+1u;
        if((uint8_t)source[i]==47u || (uint8_t)source[i]==92u) return empty;
        --i;
    }
    return empty;
}

/* Full native4c6f46..4c6fba. Driver offsets cache_size4/read20/seek28.
 * Cached read is a genuine child provider, not an uncached substitute. */
extern uint32_t audio_uart_lv_fs_read_cached_4c713c(void *,void *,uint32_t,uint32_t *);
uint32_t audio_uart_lv_fs_file_read_4c6f46(void *file,void *buffer,uint32_t size,uint32_t *read_out)
{
    volatile uint32_t *f=file;
    if(read_out != 0) *read_out=0u;
    if(f[1]==0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[5]==0u ||
           ((volatile uint32_t *)(uintptr_t)f[1])[7]==0u) return 9u;
    } else if(((volatile uint32_t *)(uintptr_t)f[1])[5]==0u) return 9u;
    uint32_t count=0u,result;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        result=audio_uart_lv_fs_read_cached_4c713c(file,buffer,size,&count);
    } else {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[5];
        result=((uint32_t (*)(void *,void *,void *,uint32_t,uint32_t *))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,buffer,size,&count);
    }
    if(read_out != 0) *read_out=count;
    return (uint8_t)result;
}

/* Complete native4c713c..4c7326; reconstructed from pinned lv_fs.c and
 * native field offsets, 16-bit partial-copy length and fresh owner reloads.
 * Qualified by2880 bounded compiled ARM/native comparisons. */
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
#define CACHE ((volatile uint32_t *)(uintptr_t)f[2])
#define DRIVER ((volatile uint32_t *)(uintptr_t)f[1])
#define SEEK(pos) ((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)DRIVER[7])((void *)(uintptr_t)f[1],(void *)(uintptr_t)f[0],(pos),0u)
#define READ(buf,len,count) ((uint32_t (*)(void *,void *,void *,uint32_t,uint32_t *))(uintptr_t)DRIVER[5])((void *)(uintptr_t)f[1],(void *)(uintptr_t)f[0],(buf),(len),(count))
uint32_t audio_uart_lv_fs_read_cached_4c713c(void *file,void *out,uint32_t request,uint32_t *read_out)
{
    volatile uint32_t *f=file;
    uint32_t result=0u,position=CACHE[2],start=CACHE[0],end=CACHE[1];
    uint8_t *buffer=(void *)(uintptr_t)CACHE[3];
    uint32_t buffer_size=DRIVER[1];
    if(position>=start && position<=end) {
        uint32_t remaining=end-position+1u;
        uint32_t offset=(end-start)-remaining+1u;
        if(DRIVER[1]==UINT32_MAX && request>remaining) request=remaining-1u;
        if(request<=remaining) {
            audio_uart_lv_grid_copy_454738(out,buffer+offset,request);
            *read_out=request;
        } else {
            audio_uart_lv_grid_copy_454738(out,buffer+offset,remaining);
            (void)SEEK(CACHE[1]+1u);
            uint32_t count=0u;
            if(request-remaining>buffer_size) {
                result=READ((uint8_t *)out+remaining,request-remaining,&count);
            } else {
                result=READ(buffer,buffer_size,&count);
                CACHE[0]=CACHE[1]+1u;
                CACHE[1]=CACHE[0]+count-1u;
                uint32_t chunk=request-remaining;
                if(chunk>=count) chunk=count;
                audio_uart_lv_grid_copy_454738((uint8_t *)out+remaining,buffer,(uint16_t)chunk);
            }
            uint32_t total=remaining+count;
            *read_out=total<request?total:request;
        }
    } else {
        (void)SEEK(CACHE[2]);
        if(request>buffer_size) {
            result=READ(out,request,read_out);
        } else {
            if(buffer==0) {
                CACHE[3]=(uint32_t)(uintptr_t)audio_uart_lv_malloc(buffer_size);
                if(CACHE[3]==0u) {
                    audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_fs.c",600u,"lv_fs_read_cached","Asserted at expression: %s (%s)","file_p->cache->buffer != NULL","Out of memory");
                    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
                }
                buffer=(void *)(uintptr_t)CACHE[3];
            }
            uint32_t count=0u;
            result=READ(buffer,buffer_size,&count);
            CACHE[0]=position;
            CACHE[1]=CACHE[0]+count-1u;
            *read_out=request<count?request:count;
            audio_uart_lv_grid_copy_454738(out,buffer,*read_out);
        }
    }
    if((uint8_t)result==0u) CACHE[2]=CACHE[2]+*read_out;
    return (uint8_t)result;
}
#undef READ
#undef SEEK
#undef DRIVER
#undef CACHE

/* Full native4c81a2..4c8204, literal pool excluded. get_decoder_data.
 * Qualified by16 bounded compiled ARM/native comparisons. */
extern void *audio_uart_lv_heap_alloc(uint32_t); /* selected zeroed44f730 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *descriptor)
{
    volatile uint32_t *dsc=descriptor;
    void *data=(void *)(uintptr_t)dsc[18];
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if(data==0) {
        data=audio_uart_lv_heap_alloc(68u);
        if(data==0) {
            audio_uart_lvgl_log(3u,source,536u,"get_decoder_data","Asserted at expression: %s (%s)","data != NULL","Out of memory");
            for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if(data==0) {
            audio_uart_lvgl_log(3u,source,538u,"get_decoder_data","Out of memory");
            return 0;
        }
        dsc[18]=(uint32_t)(uintptr_t)data;
    }
    return data;
}

/* Complete native4c7b24..4c7e22. Qualified by bounded compiled ARM/native comparisons.
 * Native literal/string4c7e24..4c7e28 is not executable code. */
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

/* Complete native4c7e4c..4c81a2. Qualified by bounded compiled ARM/native comparisons.
 * Arithmetic follows native 32-bit wrapping and unsigned shifts. */
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
extern uint32_t audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t,void *,uint32_t,uint32_t,const void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

/* Complete48b750..48b762: low16 flag mask merged with existing header. */
void audio_uart_lv_draw_buf_set_flag_48b750(void *buffer,uint32_t flags)
{
    volatile uint32_t *b=buffer;
    uint32_t merged=(uint16_t)flags|(b[0]>>16);
    b[0]=(b[0]&0xffffu)|(merged<<16);
}

/* Complete native48b762..48b7a6; following literal pool excluded.
 * Qualified by288 bounded compiled ARM/native comparisons. */
extern uint32_t audio_uart_lv_draw_buf_init_48aef8(void *,uint32_t,uint32_t,uint32_t,uint32_t,void *,uint32_t);
uint32_t audio_uart_lv_draw_buf_from_image_48b762(void *draw_buffer,const void *image)
{
    const volatile uint32_t *src=image;
    uint32_t data_size=src[3];
    void *data=(void *)(uintptr_t)src[4];
    uint32_t stride=(uint16_t)src[2];
    uint32_t cf=(uint8_t)(src[0]>>8);
    uint32_t height=src[1]>>16;
    uint32_t width=(uint16_t)src[1];
    uint32_t result=audio_uart_lv_draw_buf_init_48aef8(draw_buffer,width,height,cf,stride,data,data_size);
    if((uint8_t)result!=1u) return (uint8_t)result;
    uint32_t flags=src[0]>>16;
    volatile uint32_t *dst=draw_buffer;
    dst[0]=(dst[0]&0xffffu)|(flags<<16);
    return (uint8_t)result;
}

/* Complete native48aef8..48affa; qualified by649 bounded native comparisons. */
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_draw_memzero_48aa54(void *,uint32_t);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern void *audio_uart_lv_draw_align_48ab04(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
uint32_t audio_uart_lv_draw_buf_init_48aef8(void *draw_buffer,uint32_t width,uint32_t height,uint32_t cf,uint32_t stride,void *data,uint32_t data_size)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    if(draw_buffer==0) {
        audio_uart_lvgl_log(3u,source,286u,"lv_draw_buf_init","Asserted at expression: %s (%s)","draw_buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(draw_buffer==0) return 0u;
    audio_uart_lv_draw_memzero_48aa54(draw_buffer,28u);
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t required=height*stride;
    if(data_size<required) {
        audio_uart_lvgl_log(2u,source,293u,"lv_draw_buf_init","Data size too small, required: %d, provided: %d",required,data_size);return 0u;
    }
    volatile uint32_t *dst=draw_buffer;
    dst[1]=(dst[1]&0xffff0000u)|(uint16_t)width;
    dst[1]=(dst[1]&0xffffu)|((uint32_t)(uint16_t)height<<16);
    dst[0]=(dst[0]&0xffff00ffu)|((uint32_t)(uint8_t)cf<<8);
    dst[2]=(dst[2]&0xffff0000u)|(uint16_t)stride;
    dst[0]=(uint16_t)dst[0];
    dst[0]=(dst[0]&0xffffff00u)|25u;
    dst[4]=(uint32_t)(uintptr_t)data;dst[5]=(uint32_t)(uintptr_t)data;
    dst[6]=(uint32_t)(uintptr_t)(audio_uart_display_lv_root+0xc8u);dst[3]=data_size;
    if((uint32_t)(uintptr_t)audio_uart_lv_draw_align_48ab04(data,(uint8_t)cf)!=dst[5]) {
        audio_uart_lvgl_log(2u,source,310u,"lv_draw_buf_init","Data is not aligned, ignored");
    }
    return 1u;
}

extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* Complete48aa54..48aa60: native R0 scratch discarded by caller. */
void audio_uart_lv_draw_memzero_48aa54(void *object,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(object,0u,size);
}
/* Complete48ab16..48ab30. Null handler returns null, not original data. */
void *audio_uart_lv_draw_align_ex_48ab16(void *handlers,void *data,uint32_t cf)
{
    volatile uint32_t *h=handlers;
    if(h[2]!=0u) {
        uint32_t callback=h[2];
        return ((void *(*)(void *,uint32_t))(uintptr_t)callback)(data,(uint8_t)cf);
    }
    return 0;
}
/* Complete48ab04..48ab16. Native default handlers root+0xc8. */
void *audio_uart_lv_draw_align_48ab04(void *data,uint32_t cf)
{
    return audio_uart_lv_draw_align_ex_48ab16(audio_uart_display_lv_root+0xc8u,data,(uint8_t)cf);
}

/* Full48aaa2..48aad8 and48aa80..48aaa2. Native comparisons passed.
 * Native48aa80 is handlers initialization, not memory-pool initialization. */
extern void audio_uart_lv_draw_memzero_48aa54(void *,uint32_t);
/* Callback invocation signatures qualified by native body comparisons. */
void *audio_uart_lv_draw_buf_malloc_cb_48b80c(uint32_t,uint32_t);
void audio_uart_lv_draw_buf_free_cb_48b816(void *);
void *audio_uart_lv_draw_buf_align_cb_48b81e(void *,uint32_t);
uint32_t audio_uart_lv_draw_width_stride_cb_48b82a(uint32_t,uint32_t);
void audio_uart_lv_draw_handlers_init_48aaa2(void *object,uint32_t allocate,uint32_t release,uint32_t align,uint32_t invalidate,uint32_t flush,uint32_t stride)
{
    audio_uart_lv_draw_memzero_48aa54(object,32u);
    volatile uint32_t *h=object;
    h[0]=allocate;h[1]=release;h[2]=align;h[3]=invalidate;h[4]=flush;h[5]=stride;
}
void audio_uart_lv_draw_handlers_default_48aa80(void *object)
{
    audio_uart_lv_draw_handlers_init_48aaa2(object,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_malloc_cb_48b80c,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_free_cb_48b816,
        (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_align_cb_48b81e,
        0u,0u,(uint32_t)(uintptr_t)audio_uart_lv_draw_width_stride_cb_48b82a);
}

extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
/* Full48b80c..48b816: native adds seven with32-bit wrap. */
void *audio_uart_lv_draw_buf_malloc_cb_48b80c(uint32_t size,uint32_t cf)
{
    (void)cf;return audio_uart_lv_malloc(size+7u);
}
/* Full48b816..48b81e: void scratch R0 not return API. */
void audio_uart_lv_draw_buf_free_cb_48b816(void *data)
{
    audio_uart_lv_heap_free(data);
}
/* Full48b81e..48b82a: null stays null, otherwise8-byte align/wrap. */
void *audio_uart_lv_draw_buf_align_cb_48b81e(void *data,uint32_t cf)
{
    (void)cf;uint32_t ptr=(uint32_t)(uintptr_t)data;
    if(ptr!=0u) ptr=(ptr+7u)&~7u;
    return (void *)(uintptr_t)ptr;
}
/* Full48b82a..48b840: low-byte format, full child BPP return. */
uint32_t audio_uart_lv_draw_width_stride_cb_48b82a(uint32_t width,uint32_t cf)
{
    uint32_t bits=audio_uart_lv_color_bpp_440f44((uint8_t)cf);
    return (width*bits+7u)>>3;
}

/* Native 0x440f44..0x440fc4, locked s200 2.2.6.10 payload.
 * The native UXTB makes the format ABI explicitly byte-valued. */
uint32_t audio_uart_lv_color_bpp_440f44(uint32_t format)
{
    switch ((uint8_t)format) {
    case 7: case 11: return 1;
    case 8: case 12: return 2;
    case 9: case 13: case 48: return 4;
    case 49: case 50: case 51: return 6;
    case 6: case 10: case 14: case 24: return 8;
    case 52: case 53: return 12;
    case 18: case 20: case 21: case 22: case 23: case 38: return 16;
    case 15: case 19: return 24;
    case 16: case 17: return 32;
    default: return 0;
    }
}

extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
/* Full native4c7364..4c73c2; driver and cache reloaded after callbacks. */
uint32_t audio_uart_lv_fs_seek_cached_4c7364(void *file,uint32_t position,uint32_t whence)
{
    volatile uint32_t *f=file;
    uint32_t result=0u;
    switch((uint8_t)whence) {
    case 0: ((volatile uint32_t *)(uintptr_t)f[2])[2]=position; break;
    case 1: position+=((volatile uint32_t *)(uintptr_t)f[2])[2];
        ((volatile uint32_t *)(uintptr_t)f[2])[2]=position; break;
    case 2: {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[7];
        result=((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position,(uint8_t)whence);
        if((uint8_t)result!=0u) break;
        uint32_t end;
        data=f[0];driver=f[1];callback=((volatile uint32_t *)(uintptr_t)f[1])[8];
        result=((uint32_t (*)(void *,void *,uint32_t *))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,&end);
        if((uint8_t)result==0u) ((volatile uint32_t *)(uintptr_t)f[2])[2]=end;
        break;
    }
    default: break;
    }
    return (uint8_t)result;
}
/* Full native4c6fba..4c7018. Cached seek requires seek and tell callbacks. */
uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *file,uint32_t position,uint32_t whence)
{
    volatile uint32_t *f=file;
    if(f[1]==0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[7]==0u ||
           ((volatile uint32_t *)(uintptr_t)f[1])[8]==0u) return 9u;
    } else if(((volatile uint32_t *)(uintptr_t)f[1])[7]==0u) return 9u;
    uint32_t result;
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u)
        result=audio_uart_lv_fs_seek_cached_4c7364(file,position,(uint8_t)whence);
    else {
        uint32_t data=f[0],driver=f[1];
        uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[7];
        result=((uint32_t (*)(void *,void *,uint32_t,uint32_t))(uintptr_t)callback)
            ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position,(uint8_t)whence);
    }
    return (uint8_t)result;
}
/* Full native4c8d3c..4c8d8c; preserve output clear before seek. */
uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *file,uint32_t position,void *buffer,uint32_t size,uint32_t *read_out)
{
    if(read_out!=0) *read_out=0u;
    uint32_t result=audio_uart_lv_fs_file_seek_4c6fba(file,position,0u);
    if((uint8_t)result!=0u) return (uint8_t)result;
    result|=audio_uart_lv_fs_file_read_4c6f46(file,buffer,size,read_out);
    return (uint8_t)result;
}

extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
/* Full native48b86c..48b8d8; all size arithmetic wraps in 32 bits. */
uint32_t audio_uart_lv_draw_buf_size_48b86c(uint32_t width,uint32_t height,uint32_t cf,uint32_t stride)
{
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t bytes=height*stride;
    uint8_t format=(uint8_t)cf;
    if(format==20u) return bytes+height*(stride>>1u);
    switch(format) {
    case 7: return bytes+8u;
    case 8: return bytes+16u;
    case 9: return bytes+64u;
    case 10: return bytes+1024u;
    default: return bytes;
    }
}
/* Full native48b196..48b216; fresh header loads preserve child mutations. */
void *audio_uart_lv_draw_buf_reshape_48b196(void *draw_buffer,uint32_t cf,uint32_t width,uint32_t height,uint32_t stride)
{
    volatile uint32_t *b=draw_buffer;
    if(b==0) return 0;
    if((uint8_t)cf==0u) cf=b[0]>>8u;
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t size=audio_uart_lv_draw_buf_size_48b86c(width,height,(uint8_t)cf,stride);
    if(b[3]<size) return 0;
    b[0]=(b[0]&0xffff00ffu)|((uint32_t)(uint8_t)cf<<8u);
    b[1]=(b[1]&0xffff0000u)|(uint16_t)width;
    b[1]=(b[1]&0x0000ffffu)|((uint32_t)(uint16_t)height<<16u);
    b[2]=(b[2]&0xffff0000u)|(uint16_t)stride;
    return draw_buffer;
}

/* Full native4d5104..4d5114; native unconditionally dereferences cache. */
uint32_t audio_uart_lv_cache_enabled_4d5104(void *cache)
{
    return ((volatile uint32_t *)cache)[2]!=0u;
}
/* Full native4d4b24..4d4b32; image-cache owner at root+0x134. */
uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void)
{
    uint32_t cache=*(volatile uint32_t *)(void *)(audio_uart_display_lv_root+0x134u);
    return audio_uart_lv_cache_enabled_4d5104((void *)(uintptr_t)cache);
}

/* Full native4c8c94..4c8d3c. Signed x division truncates toward zero;
 * loop width is signed and shift tests use the native low signed byte. */
uint32_t audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t format,void *palette,uint32_t x_bits,uint32_t width_bits,const void *input,void *output)
{
    uint32_t bits,shift;
    int32_t x=(int32_t)x_bits;
    uintptr_t address=(uintptr_t)input;
    switch((uint8_t)format) {
    case 7: bits=1u;address+=(uint32_t)(x/8);shift=7u-(x_bits&7u);break;
    case 8: bits=2u;address+=(uint32_t)(x/4);shift=6u-((x_bits<<1u)&6u);break;
    case 9: bits=4u;address+=(uint32_t)(x/2);shift=4u-((x_bits<<2u)&4u);break;
    case 10: bits=8u;address+=x_bits;shift=0u;break;
    default: return 0u;
    }
    uint32_t mask=(1u<<bits)-1u;
    for(uint32_t i=0u;(int32_t)i<(int32_t)width_bits;++i) {
        uint32_t index=(*(const uint8_t *)address>>shift)&mask;
        ((uint32_t *)output)[i]=((const uint32_t *)palette)[index];
        shift-=bits;
        if((int8_t)(uint8_t)shift<0) {shift=8u-bits;++address;}
    }
    return 1u;
}

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native4c8780..4c884a. Saved decoder data/file ownership survives children. */
uint32_t audio_uart_lv_bin_decode_rgb_4c8780(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    void *file=(void *)(uintptr_t)data[0];
    uint32_t cf=d[8]>>8u;
    uint32_t len=(d[9]>>16u)*(uint16_t)d[10];
    if((uint8_t)cf==20u) len+=(d[9]>>16u)*((uint16_t)d[10]/2u);
    uint32_t stride=(uint16_t)d[10];
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,
        (uint16_t)d[9],d[9]>>16u,(uint8_t)cf,stride);
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if(decoded==0) {
        audio_uart_lvgl_log(3u,source,800u,"decode_rgb","No memory for rgb file read");
        return 0u;
    }
    void *pixels=(void *)(uintptr_t)((volatile uint32_t *)decoded)[4];
    uint32_t count;
    uint32_t result=audio_uart_lv_fs_read_at_4c8d3c(file,12u,pixels,len,&count);
    if((uint8_t)result!=0u || count!=len) {
        audio_uart_lvgl_log(2u,source,809u,"decode_rgb",
            "Read rgb file failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,len);
        audio_uart_font_bitmap_release(decoded);
        return 0u;
    }
    d[11]=(uint32_t)(uintptr_t)decoded;
    data[7]=(uint32_t)(uintptr_t)decoded;
    return 1u;
}

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static uint32_t alpha_lsl(uint32_t value,uint32_t shift)
{
    uint32_t amount=(uint8_t)shift;
    return amount>=32u?0u:value<<amount;
}
/* Full native4c884a..4c887c; byte-valued interpolation, native register shifts. */
uint32_t audio_uart_lv_bin_bit_extend_4c884a(uint32_t value,uint32_t bpp)
{
    if((uint8_t)value==0u) return 0u;
    uint32_t result=value,position=bpp;
    while((uint8_t)position<8u) {
        result|=alpha_lsl((uint8_t)value,8u-position);
        position+=bpp;
    }
    return (uint8_t)result;
}
/* Full native4c887c..4c8a10; literal pool beginning4c8a10 excluded. */
uint32_t audio_uart_lv_bin_decode_alpha_4c887c(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    uint32_t bits=audio_uart_lv_color_bpp_440f44((uint8_t)(d[8]>>8u));
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if((uint8_t)bits==0u) {
        audio_uart_lvgl_log(3u,source,846u,"decode_alpha_only","Error color format: %d",(uint32_t)(uint8_t)(d[8]>>8u));
        return 0u;
    }
    uint32_t row=((uint32_t)(uint16_t)d[10]*8u)/(uint8_t)bits;
    uint32_t out_stride=(row*8u+7u)>>3u;
    uint32_t out_len=row*(d[9]>>16u);
    uint32_t file_len=(uint32_t)(uint16_t)d[10]*(d[9]>>16u);
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,
        (uint16_t)d[9],d[9]>>16u,14u,out_stride);
    if(decoded==0) {
        audio_uart_lvgl_log(3u,source,859u,"decode_alpha_only","Out of memory");
        return 0u;
    }
    uintptr_t pixels=((volatile uint32_t *)decoded)[4];
    if((d[8]&0x00080000u)!=0u) {
        void *decompressed=(void *)(uintptr_t)data[8];
        audio_uart_lv_grid_copy_454738((void *)pixels,(void *)(uintptr_t)((volatile uint32_t *)decompressed)[4],file_len);
    } else if(((volatile uint8_t *)descriptor)[16]==1u) {
        uint32_t count;
        uint32_t result=audio_uart_lv_fs_read_at_4c8d3c((void *)(uintptr_t)data[0],12u,(void *)pixels,file_len,&count);
        if((uint8_t)result!=0u || count!=file_len) {
            audio_uart_lvgl_log(2u,source,872u,"decode_alpha_only",
                "Read header failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,file_len);
            audio_uart_font_bitmap_release(decoded);
            return 0u;
        }
    } else if(((volatile uint8_t *)descriptor)[16]==0u) {
        void *image=(void *)(uintptr_t)d[3];
        audio_uart_lv_grid_copy_454738((void *)pixels,(void *)(uintptr_t)((volatile uint32_t *)image)[4],file_len);
    }
    if((uint8_t)(d[8]>>8u)!=14u) {
        uintptr_t input=pixels+file_len-1u,output=pixels+out_len-1u;
        uint32_t mask=alpha_lsl(1u,bits)-1u,shift=0u;
        for(uint32_t i=0u;i<out_len;++i) {
            uint32_t amount=(uint8_t)shift;
            uint32_t value=amount>=32u?0u:*(uint8_t *)input>>amount;
            value&=mask;
            *(uint8_t *)output=(uint8_t)audio_uart_lv_bin_bit_extend_4c884a((uint8_t)value,(uint8_t)bits);
            shift+=bits;
            if((uint8_t)shift>=8u) {shift=0u;--input;}
            --output;
        }
    }
    data[7]=(uint32_t)(uintptr_t)decoded;
    d[11]=(uint32_t)(uintptr_t)decoded;
    return 1u;
}

/* Both names identify native48b010..48b12c. Canonical selected implementation
 * remains in display_font_bitmap_allocate.c; the entry ABI truncates cf. */
extern void *audio_uart_font_bitmap_allocate(void *,uint32_t,uint32_t,uint8_t,uint32_t);
void *audio_uart_lv_draw_buf_create_ex_48b010(void *handlers,uint32_t width,uint32_t height,uint32_t cf,uint32_t stride)
{
    return audio_uart_font_bitmap_allocate(handlers,width,height,(uint8_t)cf,stride);
}

/* Full native4c7018..4c7064. Cached tell reads cache+8 without a callback. */
uint32_t audio_uart_lv_fs_file_tell_4c7018(void *file,uint32_t *position)
{
    volatile uint32_t *f=file;
    if(f[1]==0u) {*position=0u;return 11u;}
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]==0u &&
       ((volatile uint32_t *)(uintptr_t)f[1])[8]==0u) {*position=0u;return 9u;}
    if(((volatile uint32_t *)(uintptr_t)f[1])[1]!=0u) {
        *position=((volatile uint32_t *)(uintptr_t)f[2])[2];return 0u;
    }
    uint32_t data=f[0],driver=f[1];
    uint32_t callback=((volatile uint32_t *)(uintptr_t)f[1])[8];
    return (uint8_t)((uint32_t (*)(void *,void *,uint32_t *))(uintptr_t)callback)
        ((void *)(uintptr_t)driver,(void *)(uintptr_t)data,position);
}

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_draw_buf_from_image_48b762(void *,const void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_tell_4c7018(void *,uint32_t *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_tell_4c7018(void *,uint32_t *);
extern uint32_t audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t,void *,uint32_t,uint32_t,const void *,void *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native4c8d8c..4c8e78. RLE/LZ4 are disabled in the locked native build;
 * these are native diagnostic/cleanup branches, not substitute codec stubs. */
uint32_t audio_uart_lv_bin_decompress_image_4c8d8c(void *descriptor,void *compressed)
{
    volatile uint32_t *d=descriptor,*c=compressed;
    if(audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor)==0) return 0u;
    uint32_t out_len=c[2],input_len=c[1];
    uint32_t stride=(uint16_t)d[10];
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)d[9],d[9]>>16u,(uint8_t)(d[8]>>8u),stride);
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[]="decompress_image";
    if(decoded==0) {
        audio_uart_lvgl_log(2u,source,1117u,function,"No memory for decompressed image, input: %u, output: %u",input_len,out_len);return 0u;
    }
    if(((volatile uint32_t *)decoded)[3]<out_len) {
        audio_uart_lvgl_log(3u,source,1122u,function,"Decompressed size mismatch: %u > %u",out_len,((volatile uint32_t *)decoded)[3]);
        audio_uart_font_bitmap_release(decoded);return 0u;
    }
    (void)((volatile uint32_t *)decoded)[4];
    if((((volatile uint8_t *)compressed)[0]&15u)==1u)
        audio_uart_lvgl_log(2u,source,1147u,function,"RLE decompress is not enabled");
    else if((((volatile uint8_t *)compressed)[0]&15u)==2u)
        audio_uart_lvgl_log(2u,source,1164u,function,"LZ4 decompress is not enabled");
    else audio_uart_lvgl_log(2u,source,1171u,function,"Unknown compression method: %d",(uint32_t)(((volatile uint8_t *)compressed)[0]&15u));
    audio_uart_font_bitmap_release(decoded);return 0u;
}

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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
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

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_cache_add_4d4eea(void *,const void *,void *);
extern void *audio_uart_font_cache_info(void *);
extern char *audio_uart_font_path_duplicate(const char *);
/* Full native48911a..489168; key source type is a byte at offset8. */
void *audio_uart_lv_decoder_add_cache_48911a(void *decoder,const void *key,void *decoded,void *user_data)
{
    void *cache=(void *)(uintptr_t)*(volatile uint32_t *)(void *)(audio_uart_display_lv_root+0x134u);
    void *entry=audio_uart_lv_cache_add_4d4eea(cache,key,0);
    if(entry==0) return 0;
    volatile uint32_t *data=audio_uart_font_cache_info(entry);
    data[3]=(uint32_t)(uintptr_t)decoded;
    if(((volatile uint8_t *)data)[8]==1u)
        data[1]=(uint32_t)(uintptr_t)audio_uart_font_path_duplicate((const char *)(uintptr_t)data[1]);
    data[5]=(uint32_t)(uintptr_t)user_data;
    data[4]=(uint32_t)(uintptr_t)decoder;
    return entry;
}

#include <stdint.h>
/* Full native 440fc4..440fde: enum ABI is reduced to its low byte. */
uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t format)
{
    uint32_t cf=(uint8_t)format;
    return (cf-7u<=7u || cf==16u || cf-19u<=5u) ? 1u : 0u;
}
/* Full native 48b73c..48b750: only header flags bits 16..31 participate. */
uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *buffer,uint32_t mask)
{
    return ((*(const volatile uint32_t *)buffer >> 16u)&mask)!=0u;
}

#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern uint32_t audio_uart_lv_draw_buf_adjust_stride_48b34e(void *,uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_lv_draw_buf_copy_48ad42(void *,const void *,const void *,const void *);
extern uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t);
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern uint32_t audio_uart_lv_draw_buf_premultiply_48b540(void *);
extern void *audio_uart_lv_draw_buf_duplicate_ex_48b134(void *,const void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native489168..48925a; fresh header loads preserve child-call mutations. */
void *audio_uart_lv_decoder_postprocess_489168(void *descriptor,void *decoded)
{
    if(decoded==0) return 0;
    volatile uint8_t *args=(volatile uint8_t *)descriptor+4u;
    volatile uint32_t *buf=decoded;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_image_decoder.c";
    static const char function[]="lv_image_decoder_post_process";
    if(args[0]!=0u && (uint8_t)(buf[0]>>8u)!=20u) {
        uint32_t expected=audio_uart_font_bitmap_stride((uint16_t)buf[1],(uint8_t)(buf[0]>>8u));
        if((uint16_t)buf[2]!=expected && (uint8_t)audio_uart_lv_draw_buf_adjust_stride_48b34e((void *)buf,expected)!=1u) {
            void *aligned=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)buf[1],buf[1]>>16u,(uint8_t)(buf[0]>>8u),expected);
            if(aligned==0) {audio_uart_lvgl_log(3u,source,258u,function,"No memory for Stride adjust.");return 0;}
            audio_uart_lv_draw_buf_copy_48ad42(aligned,0,(void *)buf,0);buf=aligned;
        }
    }
    if(args[1]!=0u && (uint32_t)((uint8_t)(buf[0]>>8u))-11u>=4u && audio_uart_lv_color_has_alpha_440fc4((uint8_t)(buf[0]>>8u))!=0u && audio_uart_lv_draw_buf_has_flag_48b73c((void *)buf,1u)==0u) {
        if(audio_uart_lv_draw_buf_has_flag_48b73c((void *)buf,32u)==0u) {
            buf=audio_uart_lv_draw_buf_duplicate_ex_48b134(audio_uart_display_lv_root+0x108u,(void *)buf);
            if(buf==0) {audio_uart_lvgl_log(3u,source,282u,function,"No memory for premultiplying.");return 0;}
        }
        audio_uart_lv_draw_buf_premultiply_48b540((void *)buf);
    }
    return (void *)buf;
}

#include <stdint.h>
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
/* Full native48b134..48b196; preserve fresh loads after allocation and flag writes. */
void *audio_uart_lv_draw_buf_duplicate_ex_48b134(void *handlers,const void *source)
{
    const volatile uint32_t *src=source;
    volatile uint32_t *dst=audio_uart_lv_draw_buf_create_ex_48b010(handlers,(uint16_t)src[1],src[1]>>16u,(uint8_t)(src[0]>>8u),(uint16_t)src[2]);
    if(dst==0) return 0;
    uint32_t flags=src[0]>>16u;
    dst[0]=(dst[0]&0xffffu)|(flags<<16u);
    flags=(dst[0]>>16u)|48u;
    dst[0]=(dst[0]&0xffffu)|(flags<<16u);
    uint32_t size;
    if(src[3]<dst[3]) size=src[3];else size=dst[3];
    audio_uart_lv_grid_copy_454738((void *)(uintptr_t)dst[4],(const void *)(uintptr_t)src[4],size);
    return (void *)dst;
}

#include <stdint.h>
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern uint32_t audio_uart_lv_draw_buf_size_48b86c(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_grid_move_45475a(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native48b34e..48b51e; assertions retain native repeated zero-store. */
uint32_t audio_uart_lv_draw_buf_adjust_stride_48b34e(void *buffer,uint32_t stride)
{
    volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_adjust_stride";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,449u,function,"Asserted at expression: %s (%s)","src != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b[4]==0u) {
        audio_uart_lvgl_log(3u,source,450u,function,"Asserted at expression: %s (%s)","src->data != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0 || b[4]==0u) return 0u;
    uint32_t width=(uint16_t)b[1],height=b[1]>>16u;
    if(audio_uart_lv_draw_buf_has_flag_48b73c((void *)b,32u)==0u) return 0u;
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)(b[0]>>8u));
    if((uint16_t)b[2]==stride) return 1u;
    uint32_t minimal=(audio_uart_lv_color_bpp_440f44((uint8_t)(b[0]>>8u))*width+7u)>>3u;
    if(stride<minimal) {audio_uart_lvgl_log(2u,source,477u,function,"New stride is too small. min: %d",minimal);return 0u;}
    uint32_t required=audio_uart_lv_draw_buf_size_48b86c(width,height,(uint8_t)(b[0]>>8u),stride);
    if(b[3]<required) return 0u;
    uint32_t palette;
    if((uint8_t)(b[0]>>8u)==7u) palette=2u;
    else if((uint8_t)(b[0]>>8u)==8u) palette=4u;
    else if((uint8_t)(b[0]>>8u)==9u) palette=16u;
    else if((uint8_t)(b[0]>>8u)==10u) palette=256u;
    else palette=0u;
    uint32_t source_data,destination_data;
    if((uint16_t)b[2]<stride) {
        source_data=b[4]+palette*4u+(uint16_t)b[2]*(height-1u);
        destination_data=b[4]+palette*4u+stride*(height-1u);
        for(uint32_t y=0u;y<height;y++) {
            audio_uart_lv_grid_move_45475a((void *)(uintptr_t)destination_data,(void *)(uintptr_t)source_data,minimal);
            source_data-=(uint16_t)b[2];destination_data-=stride;
        }
    } else {
        source_data=b[4]+palette*4u;destination_data=b[4]+palette*4u;
        for(uint32_t y=0u;y<height;y++) {
            audio_uart_lv_grid_move_45475a((void *)(uintptr_t)destination_data,(void *)(uintptr_t)source_data,minimal);
            source_data+=(uint16_t)b[2];destination_data+=stride;
        }
    }
    b[2]=(b[2]&0xffff0000u)|(uint16_t)stride;
    return 1u;
}

#include <stdint.h>
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
/* Full native439710..4397a6. Forward branch delegates to canonical439be4;
 * reverse preserves byte alignment, four-word blocks and unaligned stores.
 * Compiler helper has no stable R0 return contract. */
void audio_uart_compiler_move_439710(void *destination,const void *source,uint32_t length)
{
    uint32_t d=(uint32_t)(uintptr_t)destination,s=(uint32_t)(uintptr_t)source;
    if(s>=d || d>=s+length) { (void)audio_queue_copy_bytes(destination,source,length);return; }
    s+=length;d+=length;
    while((s&3u)!=0u && length!=0u) {
        --s;--d;*(volatile uint8_t *)(uintptr_t)d=*(const volatile uint8_t *)(uintptr_t)s;--length;
    }
    if((d&3u)==0u) {
        while(length>=16u) {
            uint32_t a=*(const volatile uint32_t *)(uintptr_t)(s-16u);
            uint32_t b=*(const volatile uint32_t *)(uintptr_t)(s-12u);
            uint32_t c=*(const volatile uint32_t *)(uintptr_t)(s-8u);
            uint32_t e=*(const volatile uint32_t *)(uintptr_t)(s-4u);
            s-=16u;d-=16u;
            *(volatile uint32_t *)(uintptr_t)d=a;
            *(volatile uint32_t *)(uintptr_t)(d+4u)=b;
            *(volatile uint32_t *)(uintptr_t)(d+8u)=c;
            *(volatile uint32_t *)(uintptr_t)(d+12u)=e;
            length-=16u;
        }
        while(length>=4u) {
            s-=4u;uint32_t value=*(const volatile uint32_t *)(uintptr_t)s;d-=4u;
            *(volatile uint32_t *)(uintptr_t)d=value;length-=4u;
        }
    } else {
        while(length>=4u) {
            s-=4u;uint32_t value=*(const volatile uint32_t *)(uintptr_t)s;d-=4u;
            if((d&1u)==0u) {
                *(volatile uint16_t *)(uintptr_t)d=(uint16_t)value;
                *(volatile uint16_t *)(uintptr_t)(d+2u)=(uint16_t)(value>>16u);
            } else {
                *(volatile uint8_t *)(uintptr_t)d=(uint8_t)value;
                *(volatile uint16_t *)(uintptr_t)(d+1u)=(uint16_t)(value>>8u);
                *(volatile uint8_t *)(uintptr_t)(d+3u)=(uint8_t)(value>>24u);
            }
            length-=4u;
        }
    }
    while(length!=0u) {
        --s;--d;*(volatile uint8_t *)(uintptr_t)d=*(const volatile uint8_t *)(uintptr_t)s;--length;
    }
}
/* Full native45475a..454768 restores destination after void compiler helper. */
void *audio_uart_lv_grid_move_45475a(void *destination,const void *source,uint32_t length)
{
    audio_uart_compiler_move_439710(destination,source,length);return destination;
}

#include <stdint.h>
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native440f38..440f44; return scratch is not a void API contract. */
void audio_uart_lv_color_zero_440f38(void *color,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(color,0u,size);
}
/* Full native4410b8..4410ee; RGB channels update red, green, blue in that order. */
void audio_uart_lv_color_premultiply_4410b8(void *color)
{
    volatile uint8_t *c=color;
    if(c[3]==255u) return;
    if(c[3]==0u) {audio_uart_lv_color_zero_440f38(color,4u);return;}
    c[2]=(uint8_t)((uint32_t)c[2]*c[3]>>8u);
    c[1]=(uint8_t)((uint32_t)c[1]*c[3]>>8u);
    c[0]=(uint8_t)((uint32_t)c[0]*c[3]>>8u);
}
struct audio_uart_packed_color16 { uint16_t value; } __attribute__((packed));
/* Full native4410ee..441164; packed accesses support native ARGB8565 pixels. */
void audio_uart_lv_color16_premultiply_4410ee(void *color,uint32_t alpha)
{
    volatile struct audio_uart_packed_color16 *c=color;
    if((uint8_t)alpha==255u) return;
    if((uint8_t)alpha==0u) {audio_uart_lv_color_zero_440f38(color,2u);return;}
    uint32_t red=(((uint32_t)(c->value>>11u)*(uint8_t)alpha)>>8u)&31u;
    c->value=(uint16_t)((c->value&0x7ffu)|(red<<11u));
    uint32_t green=(((uint32_t)((c->value>>5u)&63u)*(uint8_t)alpha)>>8u)&63u;
    c->value=(uint16_t)((c->value&0xf81fu)|(green<<5u));
    uint32_t blue=((uint32_t)(*(volatile uint8_t *)color&31u)*(uint8_t)alpha>>8u)&31u;
    c->value=(uint16_t)((c->value&0xffe0u)|blue);
}
/* Full native48b540..48b722, including unsupported-format diagnostic and flags. */
uint32_t audio_uart_lv_draw_buf_premultiply_48b540(void *buffer)
{
    volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_premultiply";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,520u,function,"Asserted at expression: %s (%s)","draw_buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0) return 0u;
    if(((b[0]>>16u)&1u)!=0u) return 0u;
    if(((b[0]>>16u)&32u)==0u) {
        audio_uart_lvgl_log(2u,source,525u,function,"draw buf is not modifiable: 0x%04x",b[0]>>16u);return 0u;
    }
    uint32_t cf=b[0]>>8u;
    if((uint32_t)(uint8_t)cf-7u<4u) {
        uint32_t n=(uint8_t)cf==7u?2u:(uint8_t)cf==8u?4u:(uint8_t)cf==9u?16u:256u;
        uint32_t data=b[4];
        for(uint32_t i=0u;i<n;i++) audio_uart_lv_color_premultiply_4410b8((void *)(uintptr_t)(data+4u*i));
    } else if((uint8_t)cf==16u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],line=b[4];
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {audio_uart_lv_color_premultiply_4410b8((void *)(uintptr_t)pixel);pixel+=4u;}
            line+=stride;
        }
    } else if((uint8_t)cf==20u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],alpha_stride=stride>>1u,line=b[4];
        uint32_t alpha=line+height*stride;
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {
                audio_uart_lv_color16_premultiply_4410ee((void *)(uintptr_t)pixel,*(volatile uint8_t *)(uintptr_t)(alpha+x));pixel+=2u;
            }
            line+=stride;alpha+=alpha_stride;
        }
    } else if((uint8_t)cf==19u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],line=b[4];
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {
                uint32_t alpha=*(volatile uint8_t *)(uintptr_t)(pixel+2u);
                audio_uart_lv_color16_premultiply_4410ee((void *)(uintptr_t)pixel,alpha);pixel+=3u;
            }
            line+=stride;
        }
    } else if((uint32_t)(uint8_t)cf-11u>=4u) {
        audio_uart_lvgl_log(2u,source,589u,function,"draw buf has no alpha, cf: %d",(uint32_t)(uint8_t)cf);
    }
    uint32_t flags=(b[0]>>16u)|1u;
    b[0]=(b[0]&0xffffu)|(flags<<16u);
    return 1u;
}

#include <stdint.h>
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern void *audio_uart_lv_draw_buf_goto_xy_48b2aa(const void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native48ad42..48aef8, including custom-copy dispatch and assertions. */
void audio_uart_lv_draw_buf_copy_48ad42(void *destination,const void *destination_area,const void *source,const void *source_area)
{
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    const volatile uint32_t *handlers=(const volatile uint32_t *)(uintptr_t)d[6];
    if(handlers[7]!=0u) {
        ((void (*)(void *,const void *,const void *,const void *))(uintptr_t)handlers[7])(destination,destination_area,source,source_area);return;
    }
    static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_copy";
    if((uint8_t)(d[0]>>8u)!=(uint8_t)(s[0]>>8u)) {
        audio_uart_lvgl_log(3u,file,235u,function,"Asserted at expression: %s Color format mismatch: %d != %d","dest->header.cf == src->header.cf",(uint32_t)(uint8_t)(d[0]>>8u),(uint32_t)(uint8_t)(s[0]>>8u));
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t width=destination_area==0 ? (uint16_t)d[1] : audio_uart_lv_area_width_451598(destination_area);
    if((destination_area==0 || source_area==0) && (uint32_t)(uint8_t)(d[0]>>8u)-7u<4u) {
        uint32_t palette;
        if((uint8_t)(d[0]>>8u)==7u) palette=2u;
        else if((uint8_t)(d[0]>>8u)==8u) palette=4u;
        else if((uint8_t)(d[0]>>8u)==9u) palette=16u;
        else if((uint8_t)(d[0]>>8u)==10u) palette=256u;
        else palette=0u;
        audio_uart_lv_grid_copy_454738((void *)(uintptr_t)d[4],(void *)(uintptr_t)s[4],palette*4u);
    }
    if((source_area==0 && width!=(uint16_t)s[1]) || (source_area!=0 && width!=audio_uart_lv_area_width_451598(source_area))) {
        audio_uart_lvgl_log(3u,file,250u,function,"Asserted at expression: %s (%s)","0","Source and destination areas have different width");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    const volatile uint32_t *sa=source_area,*da=destination_area;
    uint32_t src=source_area!=0 ? (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(source,sa[0],sa[1]) : (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(source,0u,0u);
    uint32_t dst=destination_area!=0 ? (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(destination,da[0],da[1]) : (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(destination,0u,0u);
    uint32_t y,end;
    if(destination_area!=0) {y=da[1];end=da[3];}
    else {y=0u;end=(d[1]>>16u)-1u;}
    uint32_t dest_stride=(uint16_t)d[2],src_stride=(uint16_t)s[2];
    uint32_t bytes=(width*audio_uart_lv_color_bpp_440f44((uint8_t)(d[0]>>8u))+7u);
    bytes=(bytes>>3u)|((bytes&0x80000000u)!=0u?0xe0000000u:0u);
    while((int32_t)y<=(int32_t)end) {
        audio_uart_lv_grid_copy_454738((void *)(uintptr_t)dst,(void *)(uintptr_t)src,bytes);
        dst+=dest_stride;src+=src_stride;y+=1u;
    }
}

#include <stdint.h>
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native48b2aa..48b34e; address arithmetic wraps in 32 bits. */
void *audio_uart_lv_draw_buf_goto_xy_48b2aa(const void *buffer,uint32_t x,uint32_t y)
{
    const volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,433u,"lv_draw_buf_goto_xy","Asserted at expression: %s (%s)","buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0) return 0;
    uint32_t data=b[4],palette;
    if((uint8_t)(b[0]>>8u)==7u) palette=2u;
    else if((uint8_t)(b[0]>>8u)==8u) palette=4u;
    else if((uint8_t)(b[0]>>8u)==9u) palette=16u;
    else if((uint8_t)(b[0]>>8u)==10u) palette=256u;
    else palette=0u;
    uint32_t address=data+palette*4u+y*(uint16_t)b[2];
    if(x!=0u) address+=(x*audio_uart_lv_color_bpp_440f44((uint8_t)(b[0]>>8u)))>>3u;
    return (void *)(uintptr_t)address;
}

#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void *audio_uart_lv_cache_add_internal_4d51c0(void *,const void *,uint32_t);
extern void *audio_uart_font_cache_acquire_data(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Full native4d4eea..4d4f90; no initializer callback in this cache-add API. */
void *audio_uart_lv_cache_add_4d4eea(void *cache,const void *key,void *user_data)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
    if(cache==0) {
        audio_uart_lvgl_log(3u,source,125u,"lv_cache_add","Asserted at expression: %s (%s)","cache != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(key==0) {
        audio_uart_lvgl_log(3u,source,126u,"lv_cache_add","Asserted at expression: %s (%s)","key != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    void *lock=(void *)((uintptr_t)cache+28u);
    (void)audio_uart_lv_lock_core(lock);
    if(((volatile uint32_t *)cache)[2]==0u) {(void)audio_uart_lv_unlock_core(lock);return 0;}
    void *entry=audio_uart_lv_cache_add_internal_4d51c0(cache,key,(uint32_t)(uintptr_t)user_data);
    if(entry!=0) (void)audio_uart_font_cache_acquire_data(entry);
    (void)audio_uart_lv_unlock_core(lock);
    return entry;
}

#include <stdint.h>
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lv_heap_free(void *);
/* Full native4d4b32..4d4b94 and duplicated4d4c3a..4d4c9c. */
static int32_t source_order(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{
    ak=(uint8_t)ak; bk=(uint8_t)bk;
    if(ak!=bk) return ak>bk ? 1 : -1;
    if(ak==1u) {
        int32_t cmp=audio_uart_lv_string_compare_4547be(
            (const char *)(uintptr_t)a,(const char *)(uintptr_t)b);
        return cmp==0 ? 0 : cmp>0 ? 1 : -1;
    }
    if(ak==0u) return a==b ? 0 : a>b ? 1 : -1;
    return 0;
}
int32_t audio_uart_lv_image_source_compare_4d4b32(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{ return source_order(a,ak,b,bk); }
int32_t audio_uart_lv_image_header_source_compare_4d4c3a(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{ return source_order(a,ak,b,bk); }
/* Full native4d4b94..4d4ba4: image node kind at8,source at4. */
int32_t audio_uart_lv_image_cache_compare_4d4b94(const void *a,const void *b)
{
    const volatile uint8_t *x=a,*y=b;
    return audio_uart_lv_image_source_compare_4d4b32(
        *(const volatile uint32_t *)(const void *)(x+4),x[8],
        *(const volatile uint32_t *)(const void *)(y+4),y[8]);
}
/* Full native4d4c9c..4d4cac: header node kind at4,source at0. */
int32_t audio_uart_lv_image_header_cache_compare_4d4c9c(const void *a,const void *b)
{
    const volatile uint8_t *x=a,*y=b;
    return audio_uart_lv_image_header_source_compare_4d4c3a(
        *(const volatile uint32_t *)(const void *)x,x[4],
        *(const volatile uint32_t *)(const void *)y,y[4]);
}
/* Full native4d4ba4..4d4bca. Saved draw owner and fresh key after child. */
void audio_uart_lv_image_cache_free_4d4ba4(void *entry)
{
    volatile uint8_t *p=entry;
    void *draw=(void *)(uintptr_t)*(volatile uint32_t *)(void *)(p+12);
    if(audio_uart_lv_draw_buf_has_flag_48b73c(draw,16u)!=0u)
        audio_uart_font_bitmap_release(draw);
    if(p[8]==1u) audio_uart_lv_heap_free(
        (void *)(uintptr_t)*(volatile uint32_t *)(void *)(p+4));
}
/* Full native4d4cac..4d4cbc. */
void audio_uart_lv_image_header_cache_free_4d4cac(void *entry)
{
    volatile uint8_t *p=entry;
    if(p[4]==1u) audio_uart_lv_heap_free(
        (void *)(uintptr_t)*(volatile uint32_t *)(void *)p);
}

/* Native image and header cache startup bindings: round104. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern const uintptr_t audio_uart_font_cache_backend_vtable[10];
extern const uintptr_t audio_uart_lv_cache_size_backend_vtable[10];
extern void *audio_uart_lv_cache_create_4d4cd4(const uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_image_cache_compare_4d4b94(const void *,const void *);
extern int32_t audio_uart_lv_image_header_cache_compare_4d4c9c(const void *,const void *);
extern void audio_uart_lv_image_cache_free_4d4ba4(void *);
extern void audio_uart_lv_image_header_cache_free_4d4cac(void *);
/* Native4d5114..4d511c: null is deliberately a no-op. */
void audio_uart_lv_cache_set_name_4d5114(void *cache,const char *name)
{
    if(cache!=0) *(volatile uint32_t *)((uint8_t *)cache+36u)=(uint32_t)(uintptr_t)name;
}
/* Native4d4ad4..4d4b24: image-cache startup, not font init. */
uint32_t audio_uart_lv_image_cache_init_4d4ad4(uint32_t size)
{
    volatile uint32_t *slot=(void *)(audio_uart_display_lv_root+0x134u);
    if(*slot!=0u) return 1u;
    void *cache=audio_uart_lv_cache_create_4d4cd4(
        (const uint32_t *)audio_uart_lv_cache_size_backend_vtable,24u,size,
        (uint32_t)(uintptr_t)audio_uart_lv_image_cache_compare_4d4b94,0u,
        (uint32_t)(uintptr_t)audio_uart_lv_image_cache_free_4d4ba4);
    *slot=(uint32_t)(uintptr_t)cache;
    audio_uart_lv_cache_set_name_4d5114((void *)(uintptr_t)*slot,"IMAGE");
    return *slot!=0u ? 1u : 0u;
}
/* Native4d4bdc..4d4c2c: header-cache startup, not font deinit. */
uint32_t audio_uart_lv_image_header_cache_init_4d4bdc(uint32_t count)
{
    volatile uint32_t *slot=(void *)(audio_uart_display_lv_root+0x138u);
    if(*slot!=0u) return 1u;
    void *cache=audio_uart_lv_cache_create_4d4cd4(
        (const uint32_t *)audio_uart_font_cache_backend_vtable,24u,count,
        (uint32_t)(uintptr_t)audio_uart_lv_image_header_cache_compare_4d4c9c,0u,
        (uint32_t)(uintptr_t)audio_uart_lv_image_header_cache_free_4d4cac);
    *slot=(uint32_t)(uintptr_t)cache;
    audio_uart_lv_cache_set_name_4d5114((void *)(uintptr_t)*slot,"IMAGE_HEADER");
    return *slot!=0u ? 1u : 0u;
}

#include <stdint.h>
extern void *audio_uart_lv_image_decoder_create_4890c8(void);
extern uint32_t audio_uart_lv_bmp_info_4c91e0(void *,void *,void *);
extern uint32_t audio_uart_lv_bmp_open_4c92a8(void *,void *);
extern uint32_t audio_uart_lv_bmp_get_area_4c93a0(void *,void *,const void *,void *);
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_font_bitmap_release(void *);
/* Native 4c94a8..4c94c6; callbacks can mutate descriptor fields. */
void audio_uart_lv_bmp_close_4c94a8(void *decoder,void *descriptor) {
    (void)decoder;
    volatile uint32_t *d=descriptor;
    (void)audio_uart_lv_fs_file_close_4c6ee0((void *)(uintptr_t)d[18]);
    audio_uart_lv_heap_free((void *)(uintptr_t)d[18]);
    if(d[11]!=0u) audio_uart_font_bitmap_release((void *)(uintptr_t)d[11]);
}
/* Native 4c91a8..4c91de is lv_bmp_init, despite legacy assert name. */
void audio_uart_lv_init_assert_4c91a8(void) {
    static const char name[]="BMP";
    volatile uint32_t *d=audio_uart_lv_image_decoder_create_4890c8();
    d[0]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_info_4c91e0;
    d[1]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_open_4c92a8;
    d[2]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_get_area_4c93a0;
    d[3]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_close_4c94a8;
    d[5]=(uint32_t)(uintptr_t)name;
}

#include <stdint.h>
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
static const char bmp_format[]="Not supported bpp: %d";
static const char bmp_function[]="decoder_info";
static const char bmp_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bmp\\lv_bmp.c";
/* Native4c91e0..4c92a8; file type1, packed16-bit dimensions and byte8cf. */
uint32_t audio_uart_lv_bmp_info_4c91e0(void *decoder,void *descriptor,void *header) {
    (void)decoder;
    volatile uint8_t *d=descriptor;
    const char *src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    uint8_t type=d[16];
    if(type!=1u)return 0u;
    if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bmp")!=0)return 0u;
    uint8_t bytes[54];uint32_t width,height;uint16_t bpp;
    (void)audio_uart_lv_fs_file_read_4c6f46((void *)(d+20u),bytes,54u,0);
    audio_uart_lv_grid_copy_454738(&width,bytes+18u,4u);
    audio_uart_lv_grid_copy_454738(&height,bytes+22u,4u);
    volatile uint32_t *h=header;
    h[1]=(h[1]&0xffff0000u)|(width&0xffffu);
    h[1]=(h[1]&0x0000ffffu)|(height<<16);
    audio_uart_lv_grid_copy_454738(&bpp,bytes+28u,2u);
    uint32_t cf;
    switch(bpp) {
    case 16:cf=18u;break;
    case 24:cf=15u;break;
    case 32:cf=16u;break;
    default:audio_uart_lvgl_log(2u,bmp_path,126u,bmp_function,bmp_format,(uint32_t)bpp);return 1u;
    }
    h[0]=(h[0]&0xffff00ffu)|(cf<<8);
    return 1u;
}

#include <stdint.h>
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *,const char *,uint32_t);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char bmp_open_reason[]="Out of memory";
static const char bmp_open_expression[]="dsc->user_data != NULL";
static const char bmp_open_format[]="Asserted at expression: %s (%s)";
static const char bmp_open_function[]="decoder_open";
static const char bmp_open_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bmp\\lv_bmp.c";
/* Native4c92a8..4c93a0; unsigned wrapped row-size arithmetic. */
uint32_t audio_uart_lv_bmp_open_4c92a8(void *decoder,void *descriptor) {
    (void)decoder;volatile uint8_t *d=descriptor;
    if(d[16]!=1u)return 0u;
    const char *src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bmp")!=0)return 0u;
    uint32_t state[8];uint8_t bytes[54];
    audio_uart_lv_basic_box_clear_454746(state,0u,32u);
    src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    if((uint8_t)audio_uart_lv_fs_file_open_4c6d9a(state,src,2u)!=0u)return 0u;
    (void)audio_uart_lv_fs_file_read_4c6f46(state,bytes,54u,0);
    if(bytes[0]!=0x42u||bytes[1]!=0x4du) {
        (void)audio_uart_lv_fs_file_close_4c6ee0(state);return 0u;
    }
    audio_uart_lv_grid_copy_454738(state+3,bytes+10u,4u);
    audio_uart_lv_grid_copy_454738(state+4,bytes+18u,4u);
    audio_uart_lv_grid_copy_454738(state+5,bytes+22u,4u);
    audio_uart_lv_grid_copy_454738(state+6,bytes+28u,2u);
    state[7]=((state[6]*state[4]+31u)>>5)<<2;
    *(volatile uint32_t *)(d+72u)=(uint32_t)(uintptr_t)audio_uart_lv_malloc(32u);
    if(*(volatile uint32_t *)(d+72u)==0u) {
        audio_uart_lvgl_log(3u,bmp_open_path,180u,bmp_open_function,bmp_open_format,bmp_open_expression,bmp_open_reason);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(*(volatile uint32_t *)(d+72u)==0u)return 0u;
    audio_uart_lv_grid_copy_454738((void *)(uintptr_t)*(volatile uint32_t *)(d+72u),state,32u);
    return 1u;
}

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

#include <stdint.h>
extern void *audio_uart_lv_fs_driver_find_4c70b4(uint32_t);
extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char fs_open_null[]="Can't open file: path is NULL";
static const char fs_open_function[]="lv_fs_open";
static const char fs_open_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_fs.c";
static const char fs_open_unknown[]="Can't open file (%s): unknown driver letter";
static const char fs_open_ready[]="Can't open file (%s): driver not ready";
static const char fs_open_missing[]="Can't open file (%s): open function not exists";
static const char fs_open_reason[]="Out of memory";
static const char fs_open_expression[]="file_p->cache != NULL";
static const char fs_open_format[]="Asserted at expression: %s (%s)";
/* Native4c6d9a..4c6ee0. Driver cache UINT32_MAX denotes memory-backed file. */
uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *file,const char *path,uint32_t mode) {
    volatile uint32_t *f=file;
    if(path==0) {audio_uart_lvgl_log(2u,fs_open_path,79u,fs_open_function,fs_open_null);return 11u;}
    const volatile uint8_t *p=(const volatile uint8_t *)path;
    uint8_t letter=p[0];const char *relative=path;
    if(p[0]!=0u) {relative=path+1;if(*(const volatile uint8_t *)relative==':')++relative;}
    volatile uint32_t *driver=audio_uart_lv_fs_driver_find_4c70b4(letter);
    if(driver==0) {audio_uart_lvgl_log(2u,fs_open_path,88u,fs_open_function,fs_open_unknown,path);return 3u;}
    if(driver[2]!=0u) {
        uint32_t cb=driver[2];
        if(((uint32_t (*)(void *))(uintptr_t)cb)((void *)driver)==0u) {
            audio_uart_lvgl_log(2u,fs_open_path,94u,fs_open_function,fs_open_ready,path);return 1u;
        }
    }
    if(driver[3]==0u) {audio_uart_lvgl_log(2u,fs_open_path,100u,fs_open_function,fs_open_missing,path);return 9u;}
    f[1]=(uint32_t)(uintptr_t)driver;
    if(driver[1]==UINT32_MAX) f[0]=(uint32_t)(uintptr_t)file;
    else {
        uint32_t cb=driver[3];
        void *handle=((void *(*)(void *,const char *,uint8_t))(uintptr_t)cb)((void *)driver,relative,(uint8_t)mode);
        if(handle==0||(uintptr_t)handle==UINT32_MAX)return 12u;
        f[0]=(uint32_t)(uintptr_t)handle;
    }
    if(driver[1]!=0u) {
        f[2]=(uint32_t)(uintptr_t)audio_uart_lv_heap_alloc(16u);
        if(f[2]==0u) {
            audio_uart_lvgl_log(3u,fs_open_path,123u,fs_open_function,fs_open_format,fs_open_expression,fs_open_reason);
            for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if(driver[1]==UINT32_MAX) {
            uint32_t buffer=*(const volatile uint32_t *)((const uint8_t *)path+4u);
            ((volatile uint32_t *)(uintptr_t)f[2])[3]=buffer;
            ((volatile uint32_t *)(uintptr_t)f[2])[0]=0u;
            ((volatile uint32_t *)(uintptr_t)f[2])[2]=0u;
            uint32_t end=*(const volatile uint32_t *)((const uint8_t *)path+8u);
            ((volatile uint32_t *)(uintptr_t)f[2])[1]=end;
        } else {
            ((volatile uint32_t *)(uintptr_t)f[2])[0]=UINT32_MAX;
            ((volatile uint32_t *)(uintptr_t)f[2])[1]=UINT32_MAX-1u;
        }
    }
    return 0u;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_ambiq_unit_cell[]; /* RAM200746c0 */
extern void audio_uart_ambiq_buffer_handlers_53d5da(void);
extern void *audio_uart_lv_draw_unit_create_484398(uint32_t);
extern int32_t audio_uart_ambiq_dispatch_4c76a8(void *,void *);
extern int32_t audio_uart_ambiq_evaluate_4c7548(void *,void *);
extern int32_t audio_uart_ambiq_delete_4c74f0(void *);
extern void audio_uart_ambiq_render_thread_4c7700(void *);
extern void *audio_uart_display_surface_alloc(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void *audio_uart_nema_vg_paint_create_515096(void);
extern void *audio_uart_nema_vg_grad_create_51510e(void);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
/* Native hidden structure-return ABI: caller supplies60-byte result inR0. */
extern void audio_uart_nema_cl_create_sized_514278(void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_ambiq_vector_font_init_53d6da(void *);
extern uint32_t audio_uart_lv_thread_init_4d4610(void *,const char *,uint32_t,void (*)(void),uint32_t,void *);
static const char ambiq_name[]="AMBIQ";
static const char ambiq_reason[]="NULL pointer";
static const char ambiq_expression[]="draw_ambiq_unit->cl.bo.base_virt != NULL";
static const char ambiq_format[]="Asserted at expression: %s (%s)";
static const char ambiq_function[]="lv_draw_ambiq_init";
static const char ambiq_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq.c";
static const char ambiq_thread[]="ambiqdraw";
static volatile uint32_t *ambiq_unit(void) {
    return (volatile uint32_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
}
/* Full native4c73d6..4c74ee; legacy group name retained for existing caller. */
void audio_uart_lv_init_group_4c73d6(void) {
    audio_uart_ambiq_buffer_handlers_53d5da();
    audio_uart_ambiq_unit_cell[0]=(uint32_t)(uintptr_t)audio_uart_lv_draw_unit_create_484398(228u);
    ambiq_unit()[3]=(uint32_t)(uintptr_t)audio_uart_ambiq_dispatch_4c76a8;
    ambiq_unit()[4]=(uint32_t)(uintptr_t)audio_uart_ambiq_evaluate_4c7548;
    ambiq_unit()[6]=(uint32_t)(uintptr_t)audio_uart_ambiq_delete_4c74f0;
    ambiq_unit()[1]=(uint32_t)(uintptr_t)ambiq_name;
    void *texture=audio_uart_display_surface_alloc(64u,1u,16u,0u);
    ambiq_unit()[15]=(uint32_t)(uintptr_t)texture;
    ambiq_unit()[16]=0u;
    void *path=audio_uart_nema_vg_path_create_514ebc();ambiq_unit()[17]=(uint32_t)(uintptr_t)path;
    void *paint=audio_uart_nema_vg_paint_create_515096();ambiq_unit()[18]=(uint32_t)(uintptr_t)paint;
    void *grad=audio_uart_nema_vg_grad_create_51510e();ambiq_unit()[19]=(uint32_t)(uintptr_t)grad;
    ambiq_unit()[20]=0u;
    ((volatile uint8_t *)ambiq_unit())[84]=255u;
    ((volatile uint8_t *)ambiq_unit())[85]=255u;
    ((volatile uint8_t *)ambiq_unit())[86]=255u;
    audio_uart_lv_basic_box_clear_454746((uint8_t *)ambiq_unit()+88u,0u,28u);
    audio_uart_lv_basic_box_clear_454746((uint8_t *)ambiq_unit()+116u,0u,16u);
    uint32_t command_list[15];
    audio_uart_nema_cl_create_sized_514278(command_list,102400u);
    audio_uart_checksum_copy((uint8_t *)ambiq_unit()+144u,command_list,60u);
    if(ambiq_unit()[38]==0u) {
        audio_uart_lvgl_log(3u,ambiq_path,87u,ambiq_function,ambiq_format,ambiq_expression,ambiq_reason);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    ambiq_unit()[35]=0u;
    audio_uart_ambiq_vector_font_init_53d6da((void *)ambiq_unit());
    (void)audio_uart_lv_async_init_4d465c((uint8_t *)ambiq_unit()+132u);
    void *unit=(void *)ambiq_unit();
    (void)audio_uart_lv_thread_init_4d4610((uint8_t *)unit+44u,ambiq_thread,40u,(void (*)(void))audio_uart_ambiq_render_thread_4c7700,32768u,unit);
}

#include <stdint.h>
extern int32_t g2_thread_create_dynamic(void (*)(void *),const char *,uint16_t,void *,uint32_t,void **);
extern void audio_task_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char lv_thread_message[]="xTaskCreate failed!";
static const char lv_thread_function[]="lv_thread_init";
static const char lv_thread_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\osal\\lv_freertos.c";
/* Native4d4768..4d477a. Native scratchR0 discarded by caller. */
void audio_uart_lv_thread_trampoline_4d4768(void *cell) {
    volatile uint32_t *t=cell;
    void *argument=(void *)(uintptr_t)t[1];
    uint32_t callback=t[0];
    ((void (*)(void *))(uintptr_t)callback)(argument);
    audio_task_delete(0);
}
/* Native4d4610..4d4650: stackbytes>>2 truncated to16-bit depth. */
uint32_t audio_uart_lv_thread_init_4d4610(void *cell,const char *name,uint32_t priority,void (*callback)(void),uint32_t stackbytes,void *argument) {
    volatile uint32_t *t=cell;
    t[1]=(uint32_t)(uintptr_t)argument;
    t[0]=(uint32_t)(uintptr_t)callback;
    int32_t result=g2_thread_create_dynamic(audio_uart_lv_thread_trampoline_4d4768,name,(uint16_t)(stackbytes>>2),cell,(uint8_t)priority,(void **)((uint8_t *)cell+8u));
    if(result!=1) {
        audio_uart_lvgl_log(3u,lv_thread_path,103u,lv_thread_function,lv_thread_message);return 0u;
    }
    return 1u;
}

#include <stdint.h>
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_nema_cl_destroy_5142f0(void *);
extern uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *);
extern void audio_task_delete(void *);
/* Native4d4650..4d465c; taskdelete return discarded. */
uint32_t audio_uart_lv_thread_delete_4d4650(void *thread) {
    audio_task_delete((void *)(uintptr_t)((volatile uint32_t *)thread)[2]);
    return 1u;
}
/* Native4c74f0..4c752e. No VG destroy calls in native configuration. */
int32_t audio_uart_ambiq_delete_4c74f0(void *unit) {
    volatile uint32_t *u=unit;
    audio_uart_font_bitmap_release((void *)(uintptr_t)u[15]);
    if(u[16]!=0u) audio_uart_font_bitmap_release((void *)(uintptr_t)u[16]);
    audio_uart_nema_cl_destroy_5142f0((uint8_t *)unit+144u);
    ((volatile uint8_t *)unit)[57]=1u;
    if(((volatile uint8_t *)unit)[56]!=0u)
        (void)audio_uart_lv_thread_sync_signal_4d4724((uint8_t *)unit+32u);
    return (int32_t)audio_uart_lv_thread_delete_4d4650((uint8_t *)unit+44u);
}

#include <stdint.h>
extern void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_notify_task(void *,uint32_t,uint32_t,uint32_t,uint32_t *);
/* Native4d4724..4d475c; consume waiter atomically, defer notification. */
uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *cell) {
    volatile uint32_t *s=cell;
    audio_uart_lv_anim_mutex_ensure_4d47fa(cell);
    stock_enter_critical();
    uint32_t waiter=s[2];
    s[2]=0u;
    if(waiter==0u)s[1]=1u;
    stock_exit_critical();
    if(waiter!=0u)(void)audio_notify_task((void *)(uintptr_t)waiter,0u,0u,2u,0);
    return 1u;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM20074efc */
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_cl_buffer_destroy_5140c6(void *);
extern void audio_uart_nema_cl_node_release_514178(void *);
/* Native5142f0..514382; command words are data for the GPU command buffer. */
void audio_uart_nema_cl_destroy_5142f0(void *command_list) {
    volatile uint32_t *cl=command_list;
    if(cl==0) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t root=cl[9];
    if(root!=0u&&(((volatile uint8_t *)cl)[24]&32u)==0u)
        cl=(volatile uint32_t *)(uintptr_t)root;
    do {
        volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        if(context[1]==(uint32_t)(uintptr_t)cl) {
            uint32_t offset=cl[5];uint32_t size=cl[4];
            if((int32_t)size>=(int32_t)(offset+2u)) {
                volatile uint32_t *commands=(void *)(uintptr_t)cl[2];
                commands[offset]=0x50000u;
                commands[offset+1u]=0u;
                cl[6]=cl[6]&~8u;
            }
            cl[6]=cl[6]&~32u;
            context[1]=0u;
        }
        if((((volatile uint8_t *)cl)[24]&16u)!=0u)cl=(void *)(uintptr_t)cl[8];
        else {
            audio_uart_nema_cl_buffer_destroy_5140c6((void *)cl);
            uint32_t root_after=cl[9];uint32_t next=cl[8];
            if(root_after!=0u)audio_uart_nema_cl_node_release_514178((void *)cl);
            cl=(void *)(uintptr_t)next;
        }
    } while(cl!=0);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_lv_pool_free_48429e(void *,void *);
/* Native514050..514070, source-owned pool selector literal addresses. */
void *audio_uart_nema_pool_select_514050(uint32_t pool_id) {
    if(pool_id==2u)return (void *)(uintptr_t)0x20000370u;
    if(pool_id==3u)return (void *)(uintptr_t)0x20000338u;
    return (void *)(uintptr_t)0x20000354u;
}
/* Native5140c6..5140ea; poolfree can mutate the owner. */
void audio_uart_nema_cl_buffer_destroy_5140c6(void *buffer) {
    volatile uint32_t *b=buffer;
    void *pool=audio_uart_nema_pool_select_514050(b[1]);
    void *data=(void *)(uintptr_t)b[2];
    audio_uart_lv_pool_free_48429e(pool,data);
    b[2]=0u;b[3]=0u;b[0]=0u;b[1]=UINT32_MAX;
}
/* Native514178..514184. */
void audio_uart_nema_cl_node_release_514178(void *node) {
    audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000338u,node);
}
/* Native4b127c..4b128a; native scratch return ignored by void API. */
void audio_uart_nema_error_set_4b127c(uint32_t error) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[8]=context[8]|error;
}

#include <stdint.h>
extern int32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t);
/* Native4c7548..4c76a8: return0 on all paths; acceptance changes two bytes. */
int32_t audio_uart_ambiq_evaluate_4c7548(void *unit,void *task) {
    (void)unit;
    volatile uint8_t *t=task;
    switch(t[4]) {
    case 1: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if((d[47]&15u)==4u||(d[47]&15u)==5u||(d[47]&15u)==3u)return 0;
        break;
    }
    case 10: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if((d[67]&15u)==4u||(d[67]&15u)==5u||(d[67]&15u)==3u)return 0;
        break;
    }
    case 6: {
        volatile uint8_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        uint32_t cf=(uint8_t)(*(volatile uint32_t *)(d+32u)>>8);
        if(audio_uart_ambiq_color_format_src_4b05a4(cf)==-1)return 0;
        if((d[81]&7u)==2u||(d[81]&7u)==3u)return 0;
        break;
    }
    case 2:case 3:case 5:case 7:case 8:case 9:case 11:case 13:break;
    default:return 0;
    }
    t[89]=10u;
    t[88]=9u;
    return 0;
}

#include <stdint.h>
/* Native4b05a4..4b064e; format input truncated tobyte. */
int32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t format) {
    switch((uint8_t)format) {
    case 6u:return 9;
    case 7u:return 11;
    case 8u:return 49;
    case 9u:return 53;
    case 10u:return 9;
    case 11u:return 12;
    case 12u:return 48;
    case 13u:return 52;
    case 14u:return 8;
    case 15u:return 57;
    case 16u:return 16;
    case 17u:return 17;
    case 18u:return 4;
    case 20u:return 4;
    case 21u:return 68;
    case 48u:return 18;
    case 49u:return 22;
    case 50u:return 23;
    case 52u:return 76;
    case 53u:return 77;
    default:return -1;
    }
}

#include <stdint.h>
extern void *audio_uart_lv_draw_get_available_task_48463a(void *,void *,uint32_t);
extern void *audio_uart_lv_draw_layer_alloc_buf_484836(void *);
extern uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *);
/* Native4c76a8..4c7700; pinned Ambiq dispatch policy. */
int32_t audio_uart_ambiq_dispatch_4c76a8(void *unit,void *layer) {
    volatile uint8_t *u=unit;
    if(*(volatile uint32_t *)(u+28u))return 0;
    volatile uint8_t *task=audio_uart_lv_draw_get_available_task_48463a(layer,0,9u);
    if(!task)return -1;
    if(!audio_uart_lv_draw_layer_alloc_buf_484836(layer))return -1;
    *(volatile uint32_t *)(task+80u)=2u;
    *(volatile uint32_t *)(task+76u)=(uint32_t)(uintptr_t)unit;
    *(volatile uint32_t *)(u+28u)=(uint32_t)(uintptr_t)task;
    if(u[56])audio_uart_lv_thread_sync_signal_4d4724((void *)(u+32u));
    return 1;
}

#include <stdint.h>
extern void audio_uart_lv_anim_init_4d46de(void *);
extern uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *);
extern void audio_uart_ambiq_execute_unit_4c752e(void *);
extern uint32_t audio_uart_lv_thread_sync_delete_4d475c(void *);
extern uint32_t audio_uart_lv_mutex_delete_4d46c2(void *);
/* Native4c7700..4c7752. All shared field loads retained. */
void audio_uart_ambiq_render_thread_4c7700(void *unit) {
    volatile uint8_t *u=unit;
    audio_uart_lv_anim_init_4d46de((void *)(u+32u));
    u[56]=1u;
    for(;;) {
        while(!*(volatile uint32_t *)(u+28u)&&!u[57])
            audio_uart_lv_thread_sync_wait_4d46e8((void *)(u+32u));
        if(u[57])break;
        audio_uart_ambiq_execute_unit_4c752e((void *)(uintptr_t)*(volatile uint32_t *)(u+28u));
    }
    u[56]=0u;
    audio_uart_lv_thread_sync_delete_4d475c((void *)(u+32u));
    audio_uart_lv_mutex_delete_4d46c2((void *)(u+132u));
}

#include <stdint.h>
extern void audio_uart_ambiq_execute_drawing_4c7752(void *);
extern void audio_uart_lv_draw_dispatch_request_48462e(void);
extern int32_t audio_queue_delete(void *);
/* Native4c752e..4c7548: drawing may mutate the task's draw unit. */
void audio_uart_ambiq_execute_unit_4c752e(void *task) {
    volatile uint8_t *t=task;
    audio_uart_ambiq_execute_drawing_4c7752(task);
    volatile uint8_t *unit=(void *)(uintptr_t)*(volatile uint32_t *)(t+76u);
    *(volatile uint32_t *)(t+80u)=3u;
    *(volatile uint32_t *)(unit+28u)=0u;
    audio_uart_lv_draw_dispatch_request_48462e();
}
/* Native4d475c..4d4768; waiter at word2 intentionally retained. */
uint32_t audio_uart_lv_thread_sync_delete_4d475c(void *cell) {
    volatile uint32_t *s=cell;
    s[1]=0u;
    s[0]=0u;
    return 1u;
}
/* Native4d46c2..4d46de; queue deletion precedes clearing initialized. */
uint32_t audio_uart_lv_mutex_delete_4d46c2(void *cell) {
    volatile uint32_t *s=cell;
    if(!s[0])return 0u;
    audio_queue_delete((void *)(uintptr_t)s[1]);
    s[0]=0u;
    return 1u;
}

#include <stdint.h>
extern void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *);
extern void *receiver_current_task(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_uart_notify_take_455afc(uint32_t,int32_t,uint32_t);
/* Native4d46e8..4d4724: consume pending signal, otherwise register and wait. */
uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *cell) {
    volatile uint32_t *s=cell;
    audio_uart_lv_anim_mutex_ensure_4d47fa(cell);
    uint32_t current=(uint32_t)(uintptr_t)receiver_current_task();
    stock_enter_critical();
    uint32_t pending=s[1];
    s[1]=0u;
    if(!pending)s[2]=current;
    stock_exit_critical();
    if(!pending)audio_uart_notify_take_455afc(0u,1,UINT32_MAX);
    return 1u;
}

#include <stdint.h>
extern void audio_uart_ambiq_area_copy_4c73c4(uint32_t *,const void *);
extern void audio_uart_ambiq_area_move_450bb2(uint32_t *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_ambiq_transform_area_488cda(uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,void *);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern void audio_uart_lv_draw_flush_cache_48abb8(void *,const void *);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *,const void *,uint32_t);
extern void audio_uart_ambiq_draw_fill_53dc38(void *,void *,void *);
extern void audio_uart_ambiq_draw_border_53df00(void *,void *,void *);
extern void audio_uart_ambiq_draw_triangle_53e728(void *,void *);
extern void audio_uart_ambiq_draw_line_53ecfc(void *,void *);
extern void audio_uart_ambiq_draw_arc_53f09c(void *,void *,void *);
extern void audio_uart_ambiq_draw_image_53f42a(void *,void *,void *);
extern void audio_uart_ambiq_draw_layer_53f400(void *,void *,void *);
extern void audio_uart_ambiq_set_resolution_4b0bea(uint32_t,uint32_t);
extern void audio_uart_ambiq_draw_label_53faa6(void *,void *,void *);
extern void audio_uart_ambiq_draw_box_shadow_540036(void *,void *,void *);
extern void audio_uart_ambiq_draw_mask_5409f0(void *,void *,void *);
extern uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t);
extern void audio_uart_lv_draw_invalidate_cache_48ab30(void *,const void *);
/* Native4c7752..4c791a. Wrapped uint32 arithmetic; all input loads volatile.
 * Native type13 intentionally performs no drawing call before submit/flush. */
void audio_uart_ambiq_execute_drawing_4c7752(void *task) {
    volatile uint8_t *t=task;
    volatile uint32_t *layer=(void *)(uintptr_t)*(volatile uint32_t *)(t+72u);
    void *buffer=(void *)(uintptr_t)layer[0];
    uint32_t clip[4],area[4];
    (void)*(volatile uint32_t *)(t+76u);
    audio_uart_ambiq_area_copy_4c73c4(clip,(void *)(t+56u));
    uint32_t y=0u-layer[2],x=0u-layer[1];
    audio_uart_ambiq_area_move_450bb2(clip,x,y);
    audio_uart_ambiq_area_copy_4c73c4(area,(void *)(t+8u));
    if(t[4]==6u) {
        volatile uint32_t *d=(void *)(uintptr_t)*(volatile uint32_t *)(t+84u);
        if(d[12]!=0u||d[13]!=256u||d[14]!=256u||d[16]!=0u||d[15]!=0u) {
            uint32_t w=audio_uart_lv_area_width_451598(area);
            uint32_t h=audio_uart_lv_area_height_4515a4(area);
            uint32_t sy=d[14],sx=d[13],rotation=d[12];
            audio_uart_ambiq_transform_area_488cda(area,w,h,rotation,sx,sy,(void *)(d+17));
            area[0]+=*(volatile uint32_t *)(t+8u);
            area[1]+=*(volatile uint32_t *)(t+12u);
            area[2]+=*(volatile uint32_t *)(t+8u);
            area[3]+=*(volatile uint32_t *)(t+12u);
        }
    }
    y=0u-layer[2];x=0u-layer[1];
    audio_uart_ambiq_area_move_450bb2(area,x,y);
    if(!audio_uart_lv_area_intersect_450bcc((int32_t *)area,(const int32_t *)area,(const int32_t *)clip))return;
    audio_uart_lv_draw_flush_cache_48abb8(buffer,area);
    if((uint8_t)audio_uart_ambiq_bind_buffer_4b092a(buffer,clip,0u)!=1u)return;
    switch(t[4]) {
    case 1:audio_uart_ambiq_draw_fill_53dc38(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 2:audio_uart_ambiq_draw_border_53df00(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 3:audio_uart_ambiq_draw_box_shadow_540036(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 5: {
        volatile uint32_t *b=buffer;
        uint32_t height=b[1]>>16,width=(uint16_t)b[1];
        audio_uart_ambiq_set_resolution_4b0bea(width,height);
        audio_uart_ambiq_draw_label_53faa6(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));
        break;
    }
    case 6:audio_uart_ambiq_draw_image_53f42a(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 7:audio_uart_ambiq_draw_layer_53f400(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 8:audio_uart_ambiq_draw_line_53ecfc(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u));break;
    case 9:audio_uart_ambiq_draw_arc_53f09c(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    case 10:audio_uart_ambiq_draw_triangle_53e728(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u));break;
    case 11:audio_uart_ambiq_draw_mask_5409f0(task,(void *)(uintptr_t)*(volatile uint32_t *)(t+84u),(void *)(t+8u));break;
    default:break;
    }
    audio_uart_ambiq_submit_4b0c8a(1u);
    audio_uart_lv_draw_invalidate_cache_48ab30(buffer,area);
}

#include <stdint.h>
/* Native4c73c4..4c73d6. Forward word copy, including overlapping areas. */
void audio_uart_ambiq_area_copy_4c73c4(uint32_t *destination,const void *source) {
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];
}
/* Native450bb2..450bcc: x1,x2,y1,y2 access ordering and wrapped sums. */
void audio_uart_ambiq_area_move_450bb2(uint32_t *area,uint32_t x,uint32_t y) {
    volatile uint32_t *a=area;
    a[0]=a[0]+x;
    a[2]=a[2]+x;
    a[1]=a[1]+y;
    a[3]=a[3]+y;
}

#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_lv_draw_full_area_48b8d8(void *,void *);
extern void audio_uart_lv_area_set_450b5c(void *,uint32_t,uint32_t,uint32_t,uint32_t);
static void cache_assert(uint32_t line,const char *name,const char *expression) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    audio_uart_lvgl_log(3u,source,line,name,"Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native48ab30..48abb8. Cached handler table; callback freshly reread. */
void audio_uart_lv_draw_invalidate_cache_48ab30(void *buffer,const void *area) {
    volatile uint32_t *b=buffer;
    if(!b)cache_assert(121u,"lv_draw_buf_invalidate_cache","draw_buf != NULL");
    if(!b[6])cache_assert(122u,"lv_draw_buf_invalidate_cache","draw_buf->handlers != NULL");
    volatile uint32_t *h=(void *)(uintptr_t)b[6];
    if(h[3]) {
        uint32_t full[4];
        if(!area){audio_uart_lv_draw_full_area_48b8d8(buffer,full);area=full;}
        uint32_t callback=h[3];
        ((void (*)(void *,const void *))(uintptr_t)callback)(buffer,area);
    }
}
/* Native48abb8..48ac40. Same contract, flush slot at handlerword4. */
void audio_uart_lv_draw_flush_cache_48abb8(void *buffer,const void *area) {
    volatile uint32_t *b=buffer;
    if(!b)cache_assert(143u,"lv_draw_buf_flush_cache","draw_buf != NULL");
    if(!b[6])cache_assert(144u,"lv_draw_buf_flush_cache","draw_buf->handlers != NULL");
    volatile uint32_t *h=(void *)(uintptr_t)b[6];
    if(h[4]) {
        uint32_t full[4];
        if(!area){audio_uart_lv_draw_full_area_48b8d8(buffer,full);area=full;}
        uint32_t callback=h[4];
        ((void (*)(void *,const void *))(uintptr_t)callback)(buffer,area);
    }
}
/* Native48b8d8..48b8f6. Fresh height then width header reads, uint16 zero wraps. */
void audio_uart_lv_draw_full_area_48b8d8(void *buffer,void *area) {
    const volatile uint32_t *b=buffer;
    uint32_t y2=(b[1]>>16)-1u;
    uint32_t x2=(uint16_t)b[1]-1u;
    audio_uart_lv_area_set_450b5c(area,0u,0u,x2,y2);
}

#include <stdint.h>
/* Native450b5c..450b6c; four words written in coordinate order. */
void audio_uart_lv_area_set_450b5c(void *area,uint32_t x1,uint32_t y1,uint32_t x2,uint32_t y2) {
    volatile uint32_t *a=area;
    a[0]=x1;a[1]=y1;a[2]=x2;a[3]=y2;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_ambiq_unit_cell[];
extern void audio_uart_nema_cl_submit_514cf2(void *);
extern int32_t audio_uart_nema_cl_wait_514d00(void *);
extern void audio_uart_nema_cl_unbind_5144ba(void);
extern int32_t audio_uart_nema_power_control_51419a(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_context_unlock_4b0886(void *);
extern uint32_t audio_uart_nema_get_error_4b128a(void);
extern uint32_t audio_uart_nema_vg_get_error_51564c(void);
extern const char *audio_uart_nema_error_interpret_4b0594(uint32_t);
extern const char *audio_uart_nema_vg_error_interpret_4b0584(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Native4c791a..4c7920; mutable default unit cell read once per invocation. */
void *audio_uart_ambiq_default_unit_4c791a(void) {
    return (void *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
}
/* Native4b0c8a..4b0d38. Native power failure returns0 before unlock/errors. */
uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t sync) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_common_end";
    uint8_t *unit=audio_uart_ambiq_default_unit_4c791a();
    if((uint8_t)sync) {
        audio_uart_nema_cl_submit_514cf2(unit+144u);
        audio_uart_nema_cl_wait_514d00(unit+144u);
        audio_uart_nema_cl_unbind_5144ba();
        int32_t power=audio_uart_nema_power_control_51419a(2u,1u);
        if(power) {
            audio_uart_lvgl_log(3u,source,538u,name,"Power control failed: %d\r\n",power);
            return 0u;
        }
    }
    audio_uart_ambiq_context_unlock_4b0886(unit);
    uint32_t error=audio_uart_nema_get_error_4b128a();
    if(error) {
        const char *text=audio_uart_nema_error_interpret_4b0594(error);
        audio_uart_lvgl_log(3u,source,555u,name,"NemaGFX error 0x%lx, %s\r\n",error,text);
    }
    error=audio_uart_nema_vg_get_error_51564c();
    if(error) {
        const char *text=audio_uart_nema_vg_error_interpret_4b0584(error);
        audio_uart_lvgl_log(3u,source,559u,name,"NemaVG error: 0x%lx, %s\r\n",error,text);
    }
    return 1u;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM20074efc */
/* Native4b128a..4b1298: read and clear error on the same saved context. */
uint32_t audio_uart_nema_get_error_4b128a(void) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t error=context[8];
    context[8]=0u;
    return error;
}

#include <stdint.h>
extern uint32_t audio_uart_lv_unlock_core(void *); /* native4d4696 selected */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Native4b0886..4b092a. Decrement/assert BEFORE unlocking, unlike provider. */
uint32_t audio_uart_ambiq_context_unlock_4b0886(void *unit) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_nema_context_unlock";
    if(!unit) {
        audio_uart_lvgl_log(3u,source,295u,name,"Asserted at expression: %s (%s)","unit != NULL","Ambiq GPU draw unit is not initialized!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *count=(void *)((uint8_t *)unit+140u);
    *count=*count-1u;
    if(*count) {
        audio_uart_lvgl_log(3u,source,297u,name,"Asserted at expression: %s (%s)","unit->nema_context_lock_count == 0","Ambiq GPU mutex lock count error!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t result=audio_uart_lv_unlock_core((uint8_t *)unit+132u);
    if((uint8_t)result!=1u)
        audio_uart_lvgl_log(3u,source,301u,name,"Ambiq GPU mutex unlock failed!");
    return (uint8_t)result;
}

#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern int32_t audio_uart_ambiq_color_format_dst_4b064e(uint32_t);
extern uint32_t audio_uart_ambiq_context_lock_4b07de(void *);
extern int32_t audio_uart_nema_power_control_51419a(uint32_t,uint32_t);
extern void *audio_uart_nema_cl_get_bound_5144fa(void);
extern void audio_uart_nema_cl_rewind_514384(void *);
extern void audio_uart_nema_cl_bind_sectored_5143d4(void *,uint32_t);
extern int32_t audio_uart_nema_last_cl_id_51418e(void);
extern uint32_t audio_uart_nema_last_submission_id_514194(void);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_ambiq_blend_clear_4b075e(void *);
extern uint32_t audio_uart_ambiq_context_unlock_4b0886(void *);
extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,uint32_t,int32_t,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_uart_ambiq_clip_change_4b077e(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Native4b092a..4b0b5a; unit cached once, all source/header reads volatile.
 * Null buffer is dereferenced before the later validation, as in native. */
uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *buffer,const void *raw_clip,uint32_t extend) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_common_start";
    volatile uint32_t *b=buffer;
    uint8_t *unit=audio_uart_ambiq_default_unit_4c791a();
    uint32_t bounds[4],clip[4];
    audio_uart_lv_memzero_48949c(bounds,16u);
    bounds[2]=(uint16_t)b[1]-1u;
    bounds[3]=(b[1]>>16)-1u;
    if(!raw_clip)raw_clip=bounds;
    if(!audio_uart_lv_area_intersect_450bcc((int32_t *)clip,raw_clip,(const int32_t *)bounds))return 0u;
    if((int32_t)(clip[2]-clip[0])<1||(int32_t)(clip[3]-clip[1])<1)return 0u;
    if(!buffer||!b[4]||(int32_t)(uint16_t)b[1]<1||(int32_t)(b[1]>>16)<1) {
        audio_uart_lvgl_log(3u,source,332u,name,"Invalid buffer setting!");return 0u;
    }
    int32_t format=audio_uart_ambiq_color_format_dst_4b064e((uint8_t)(b[0]>>8));
    uint32_t data=b[4];
    if(format==-1&&(uint8_t)extend==1u) {
        if((uint8_t)(b[0]>>8)==20u)format=4;
        else if((uint32_t)((uint8_t)(b[0]>>8))-7u<4u) {
            uint32_t count;
            switch((uint8_t)(b[0]>>8)) {
            case 7:count=2u;format=11;break;
            case 8:count=4u;format=49;break;
            case 9:count=16u;format=53;break;
            default:count=256u;format=9;break;
            }
            data+=count*4u;
        }
    }
    if(format==-1) {
        audio_uart_lvgl_log(3u,source,377u,name,"Unsupported layer color format!");return 0u;
    }
    audio_uart_ambiq_context_lock_4b07de(unit);
    int32_t power=audio_uart_nema_power_control_51419a(0u,1u);
    if(power) {
        audio_uart_lvgl_log(3u,source,385u,name,"Power control failed: %d\r\n",power);return 0u;
    }
    void *bound=audio_uart_nema_cl_get_bound_5144fa();
    if(!bound) {
        audio_uart_nema_cl_rewind_514384(unit+144u);
        audio_uart_nema_cl_bind_sectored_5143d4(unit+144u,100u);
    } else if(bound!=unit+144u) {
        audio_uart_ambiq_context_unlock_4b0886(unit);
        audio_uart_lvgl_log(3u,source,399u,name,"Unexpected command list in the context!\r\n");return 0u;
    }
    if(audio_uart_nema_last_cl_id_51418e()<0&&audio_uart_nema_last_submission_id_514194()==0u) {
        audio_uart_lv_basic_box_clear_454746(unit+88u,0u,28u);
        audio_uart_lv_basic_box_clear_454746(unit+116u,0u,16u);
        audio_uart_ambiq_blend_clear_4b075e(unit);
    }
    volatile uint32_t *old=(void *)(unit+88u);
    if(b[4]!=old[4]||(uint16_t)b[1]!=(uint16_t)old[1]||(b[1]>>16)!=(old[1]>>16)
       ||(uint8_t)(b[0]>>8)!=(uint8_t)(old[0]>>8)||(uint16_t)b[2]!=(uint16_t)old[2]) {
        uint32_t stride=(uint16_t)b[2],height=b[1]>>16,width=(uint16_t)b[1];
        audio_uart_nema_bind_tex_4b1298(0u,data,width,height,format,stride,0u);
        audio_uart_checksum_copy(unit+88u,buffer,28u);
    }
    audio_uart_ambiq_clip_change_4b077e(unit,clip,0u);
    return 1u;
}

#include <stdint.h>
/* Native4b064e..4b06a8; destination formats differ from source map. */
int32_t audio_uart_ambiq_color_format_dst_4b064e(uint32_t format) {
    switch((uint8_t)format) {
    case 6:return 9;
    case 11:return 11;
    case 12:return 49;
    case 13:return 53;
    case 14:return 9;
    case 15:return 57;
    case 16:return 16;
    case 17:return 17;
    case 18:return 4;
    case 21:return 68;
    default:return -1;
    }
}

#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
/* Native4b075e..4b077e: NULL chooses default, record clears without callbacks. */
void audio_uart_ambiq_blend_clear_4b075e(void *unit) {
    if(!unit)unit=audio_uart_ambiq_default_unit_4c791a();
    volatile uint8_t *u=unit;
    *(volatile uint32_t *)(u+80u)=0u;
    u[84]=255u;u[85]=255u;u[86]=255u;
}

#include <stdint.h>
/* Native4d555c..4d558e; repeated WORD pattern, not byte-replicating memset.
 * Return is the advanced destination; exact 16/8/4/2/1 store staging. */
void *audio_uart_lv_word_fill_4d555c(void *destination,uint32_t size,uint32_t pattern) {
    volatile uint8_t *p=destination;
    while(size>=16u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        *(volatile uint32_t *)(p+8u)=pattern;
        *(volatile uint32_t *)(p+12u)=pattern;
        p+=16u;size-=16u;
    }
    if(size&8u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        p+=8u;
    }
    if(size&4u){*(volatile uint32_t *)p=pattern;p+=4u;}
    if(size&2u){*(volatile uint16_t *)p=(uint16_t)pattern;p+=2u;}
    if(size&1u){*p=(uint8_t)pattern;p+=1u;}
    return (void *)p;
}
/* Native48949c..4894a2: two consumed arguments; zero pattern imposed. */
void audio_uart_lv_memzero_48949c(void *destination,uint32_t size) {
    (void)audio_uart_lv_word_fill_4d555c(destination,size,0u);
}

#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Native4b07de..4b0886. Only lowbyte success1 increments the lock count. */
uint32_t audio_uart_ambiq_context_lock_4b07de(void *unit) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_nema_context_lock";
    if(!unit) {
        audio_uart_lvgl_log(3u,source,273u,name,"Asserted at expression: %s (%s)","unit != NULL","Ambiq GPU draw unit is not initialized!");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t result=audio_uart_lv_lock_core((uint8_t *)unit+132u);
    if((uint8_t)result!=1u) {
        audio_uart_lvgl_log(3u,source,277u,name,"Ambiq GPU mutex lock failed!");
    } else {
        volatile uint32_t *count=(void *)((uint8_t *)unit+140u);
        *count=*count+1u;
        if(*count!=1u) {
            audio_uart_lvgl_log(3u,source,282u,name,"Asserted at expression: %s (%s)","unit->nema_context_lock_count == 1","Ambiq GPU mutex lock count error!");
            for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
    }
    return (uint8_t)result;
}

#include <stdint.h>
struct audio_uart_nema_error_row { uint32_t code; const char *text; };
/* Native4b0560..4b05a4; source-owned error labels from authenticated tables. */
const char *audio_uart_nema_error_lookup_4b0560(const struct audio_uart_nema_error_row *rows,uint32_t count,uint32_t error) {
    for(uint32_t i=0;i<count;++i) if(rows[i].code==error) return rows[i].text;
    return "UNKNOWN";
}
static const struct audio_uart_nema_error_row vg_rows[] = {
    { 0u, "NO_ERROR" },
    { 1u, "BAD_HANDLE" },
    { 2u, "BAD_BUFFER" },
    { 4u, "INVALID_FILL_RULE" },
    { 8u, "INVALID_PAINT_TYPE" },
    { 16u, "INVALID_VERTEX_DATA" },
    { 32u, "NO_RADIAL_ENABLED" },
    { 64u, "NO_BOUND_CL" },
    { 128u, "INVALID_ARGUMENTS" },
    { 256u, "INVALID_ARC_DATA" },
    { 512u, "CL_FULL" },
    { 1024u, "DRAW_OUT_OF_BOUNDS" },
    { 2048u, "INVALID_MASKING_OBJ" },
    { 4096u, "INVALID_MASKING_FORMAT" },
    { 8192u, "INVALID_LUT_IDX_FORMAT" },
    { 16384u, "COORDS_OUT_OF_RANGE" },
    { 32768u, "EMPTY_TSVG" },
    { 65536u, "NO_BOUND_FONT" },
    { 131072u, "UNSUPPORTED_FONT" },
    { 262144u, "NON_INVERTIBLE_MATRIX" },
    { 524288u, "INVALID_GRAD_STOPS" },
    { 1048576u, "NO_INIT" },
    { 2097152u, "INVALID_STROKE_WIDTH" },
    { 4194304u, "INVALID_OPACITY" },
    { 8388608u, "INVALID_CAP_STYLE" },
    { 16777216u, "INVALID_JOIN_STYLE" },
    { 33554432u, "INVALID_STENCIL_SIZE" },
    { 67108864u, "DEPRECATED_FONT" },
};
const char *audio_uart_nema_vg_error_interpret_4b0584(uint32_t error) { return audio_uart_nema_error_lookup_4b0560(vg_rows,28u,error); }
static const struct audio_uart_nema_error_row gfx_rows[] = {
    { 0u, "NO_ERROR" },
    { 1u, "SYS_INIT_FAILURE" },
    { 2u, "GPU_ABSENT" },
    { 4u, "RB_INIT_FAILURE" },
    { 8u, "NON_EXPANDABLE_CL_FULL" },
    { 16u, "CL_EXPANSION" },
    { 32u, "OUT_OF_GFX_MEMORY" },
    { 64u, "OUT_OF_HOST_MEMORY" },
    { 128u, "NO_BOUND_CL" },
    { 256u, "NO_BOUND_FONT" },
    { 512u, "GFX_MEMORY_INIT" },
    { 1024u, "DRIVER_FAILURE" },
    { 2048u, "MUTEX_INIT" },
    { 4096u, "INVALID_BO" },
    { 8192u, "INVALID_CL" },
    { 16384u, "INVALID_CL_ALIGMENT" },
    { 32768u, "NO_INIT" },
    { 65536u, "INVALID_SECTORED_CL_SIZE" },
};
const char *audio_uart_nema_error_interpret_4b0594(uint32_t error) { return audio_uart_nema_error_lookup_4b0560(gfx_rows,18u,error); }

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_context_cell; /* authenticated RAM0x20074f04 */
/* Native51564c..51565c: saved context, read-and-clear error word. */
uint32_t audio_uart_nema_vg_get_error_51564c(void) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    uint32_t error=context[32];
    context[32]=0u;
    return error;
}
/* Native51565c..51566c: OR error bits into saved context. */
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
/* Native5144ba..5144fa: cached context/list, wrapped signed capacity test. */
void audio_uart_nema_cl_unbind_5144ba(void) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
    if(list) {
        uint32_t used=list[5];
        uint32_t capacity=list[4];
        if((int32_t)capacity >= (int32_t)(used+2u)) {
            volatile uint32_t *commands=(volatile uint32_t *)(uintptr_t)list[2];
            commands[used]=0x50000u;
            commands[used+1u]=0u;
            list[6]=list[6]&~8u;
        }
        list[6]=list[6]&~32u;
    }
    context[1]=0u;
}

#include <stdint.h>
extern uint32_t audio_uart_nema_power_status_47f90c(uint32_t,uint8_t *);
extern uint32_t audio_power_peripheral_on(uint32_t);
extern uint32_t audio_power_peripheral_off(uint32_t);
extern uint32_t audio_uart_nema_get_error_4b128a(void);
extern uint32_t audio_uart_nema_vg_get_error_51564c(void);
extern void audio_uart_nema_reset_last_submission_514184(void);
extern int32_t audio_uart_nema_gpu_reinit_4b11b0(void);
extern void audio_uart_nema_vg_reinit_5224b6(void);
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern volatile uint32_t audio_uart_nema_vg_context_cell;
/* Native51419a..514238. Preserve low-byte policy and ordered error consumption. */
int32_t audio_uart_nema_power_control_51419a(uint32_t state,uint32_t reinit) {
    uint8_t powered;
    uint32_t result=audio_uart_nema_power_status_47f90c(20u,&powered);
    if(result) return result;
    state=(uint8_t)state;
    if(state==0u) {
        if(powered) return 0u;
        result=audio_power_peripheral_on(20u);
        if(result || (uint8_t)reinit==0u) return result;
        (void)audio_uart_nema_get_error_4b128a();
        audio_uart_nema_reset_last_submission_514184();
        audio_uart_nema_gpu_reinit_4b11b0();
        if(audio_uart_nema_get_error_4b128a()) return 1u;
        if(audio_uart_nema_vg_context_cell!=0u) {
            (void)audio_uart_nema_vg_get_error_51564c();
            audio_uart_nema_vg_reinit_5224b6();
            if(audio_uart_nema_vg_get_error_51564c()) return 1u;
        }
        return 0u;
    }
    if(state<=2u) {
        if(!powered) return 0u;
        if(audio_uart_nema_reg_read_51403c(252u)) return 3u;
        return audio_power_peripheral_off(20u);
    }
    return 7u;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_last_submission; /* authenticated RAM20002e08 */
extern const uint32_t audio_uart_nema_register_base; /* authenticated flash78f2f4 */
/* Native514184..514194. */
void audio_uart_nema_reset_last_submission_514184(void) { audio_uart_nema_last_submission=UINT32_MAX; }
uint32_t audio_uart_nema_last_submission_51418e(void) { return audio_uart_nema_last_submission; }
/* Native51403c..514050. Wrapped byte-offset register access. */
uint32_t audio_uart_nema_reg_read_51403c(uint32_t offset) {
    return *(volatile uint32_t *)(uintptr_t)(audio_uart_nema_register_base+offset);
}
void audio_uart_nema_reg_write_514046(uint32_t offset,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(audio_uart_nema_register_base+offset)=value;
}

#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
/* Source-owned configuration recovered from authenticated table6becb0. */
static const uint32_t peripheral_rows[34][4] = {
    { 0x40021004u, 0x1u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x10000000u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x20000000u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x2u, 0x40021008u, 0x1eu },
    { 0x40021004u, 0x4u, 0x40021008u, 0x1eu },
    { 0x40021004u, 0x8u, 0x40021008u, 0x1eu },
    { 0x40021004u, 0x10u, 0x40021008u, 0x1eu },
    { 0x40021004u, 0x20u, 0x40021008u, 0x1e0u },
    { 0x40021004u, 0x40u, 0x40021008u, 0x1e0u },
    { 0x40021004u, 0x80u, 0x40021008u, 0x1e0u },
    { 0x40021004u, 0x100u, 0x40021008u, 0x1e0u },
    { 0x40021004u, 0x200u, 0x40021008u, 0x1e00u },
    { 0x40021004u, 0x400u, 0x40021008u, 0x1e00u },
    { 0x40021004u, 0x800u, 0x40021008u, 0x1e00u },
    { 0x40021004u, 0x1000u, 0x40021008u, 0x1e00u },
    { 0x40021004u, 0x2000u, 0x40021008u, 0x2000u },
    { 0x40021004u, 0x4000u, 0x40021008u, 0x4000u },
    { 0x40021004u, 0x8000u, 0x40021008u, 0x8000u },
    { 0x40021004u, 0x10000u, 0x40021008u, 0x10000u },
    { 0x40021004u, 0x20000u, 0x40021008u, 0x20000u },
    { 0x40021004u, 0x40000u, 0x40021008u, 0x40000u },
    { 0x40021004u, 0x80000u, 0x40021008u, 0x80000u },
    { 0x40021004u, 0x100000u, 0x40021008u, 0x100000u },
    { 0x40021004u, 0x200000u, 0x40021008u, 0x200000u },
    { 0x40021004u, 0x400000u, 0x40021008u, 0x400000u },
    { 0x40021004u, 0x800000u, 0x40021008u, 0x800000u },
    { 0x40021004u, 0x1000000u, 0x40021008u, 0x1000000u },
    { 0x40021004u, 0x2000000u, 0x40021008u, 0x2000000u },
    { 0x40021004u, 0x4000000u, 0x40021008u, 0x4000000u },
    { 0x40021004u, 0x8000000u, 0x40021008u, 0x8000000u },
    { 0x4002100cu, 0x4u, 0x40021010u, 0x4u },
    { 0x4002100cu, 0x40u, 0x40021010u, 0xc0u },
    { 0x4002100cu, 0x80u, 0x40021010u, 0xc0u },
    { 0x4002100cu, 0x400u, 0x40021010u, 0x400u },
};
/* Native47ef18..47ef38. */
uint32_t audio_uart_power_peripheral_descriptor_47ef18(uint32_t *out,uint32_t peripheral) {
    if(!out || peripheral>=34u) return 6u;
    audio_uart_checksum_copy(out,peripheral_rows[peripheral],16u);
    return 0u;
}

#include <stdint.h>
extern uint32_t audio_uart_power_peripheral_descriptor_47ef18(uint32_t *,uint32_t);
/* Native47f90c..47f942: output clear precedes descriptor lookup. */
uint32_t audio_uart_nema_power_status_47f90c(uint32_t peripheral,uint8_t *powered) {
    if(!powered) return 6u;
    *powered=0u;
    uint32_t descriptor[4];
    uint32_t result=audio_uart_power_peripheral_descriptor_47ef18(descriptor,(uint8_t)peripheral);
    if(result) return result;
    uint32_t status=*(volatile uint32_t *)(uintptr_t)descriptor[2];
    *powered=(uint8_t)((status&descriptor[3])!=0u);
    return 0u;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
extern void audio_uart_nema_cl_unbind_5144ba(void);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_nema_child_523c88(void);
extern void audio_uart_nema_child_523304(uint32_t);
extern void audio_uart_nema_child_5138a4(void);
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
extern void audio_uart_nema_child_52296a(uint32_t);
extern void audio_uart_nema_child_52262e(uint32_t);
extern uint32_t audio_uart_nema_child_52261a(void);
/* Native4b11b0..4b127c. Keep fresh context-cell loads across child calls. */
int32_t audio_uart_nema_gpu_reinit_4b11b0(void) {
    if(audio_uart_nema_reg_read_51403c(492u)!=0x86362000u) {
        volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[8]=context[8]|2u;
        return -1;
    }
    audio_uart_nema_cl_unbind_5144ba();
    audio_uart_lv_memzero_48949c((void *)(uintptr_t)audio_uart_nema_context_cell[0],256u);
    audio_uart_nema_child_523c88();
    audio_uart_nema_reg_write_514046(232u,0u);
    audio_uart_nema_reg_write_514046(252u,0u);
    audio_uart_nema_reg_write_514046(904u,1u);
    audio_uart_nema_child_523304(0u);
    audio_uart_nema_child_5138a4();
    audio_uart_nema_child_514846(512u,0u);
    audio_uart_nema_child_514846(516u,UINT32_MAX);
    if(!(audio_uart_nema_child_522602()&(1u<<18))) {
        volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[10]=0u;
    } else {
        audio_uart_nema_child_52296a(7u);
        volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[9]=0u;
        context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        uint32_t a=context[8];
        uint32_t b=context[9];
        audio_uart_nema_child_52262e(a|b);
    }
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[5]=0u;
    uint32_t a=context[3],b=context[4],c=context[7];
    context[6]=a|b|c;
    if(audio_uart_nema_child_52261a()&(1u<<9)) {
        audio_uart_nema_reg_write_514046(884u,0u);
        audio_uart_nema_reg_write_514046(872u,0u);
    }
    return 0;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_capabilities; /* authenticated RAM20074f00 */
extern volatile uint32_t audio_uart_nema_context_cell[];
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
/* Native522602..52261a: zero cache triggers read, then fresh reread. */
uint32_t audio_uart_nema_child_522602(void) {
    if(audio_uart_nema_capabilities==0u)
        audio_uart_nema_capabilities=audio_uart_nema_reg_read_51403c(496u);
    return audio_uart_nema_capabilities;
}
/* Native52261a..522622. */
uint32_t audio_uart_nema_child_52261a(void) { return audio_uart_nema_reg_read_51403c(500u); }
/* Native52296a..522974. */
void audio_uart_nema_child_52296a(uint32_t mode) { audio_uart_nema_child_514846(480u,mode); }
/* Native52262e..52264e: saved context; ordered independent word reads. */
void audio_uart_nema_child_52262e(uint32_t enabled) {
    uint32_t flags=enabled?0x40000000u:0u;
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[3]=flags;
    uint32_t a=context[5];
    uint32_t b=context[4];
    uint32_t c=context[7];
    context[6]=flags|a|b|c;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_register_emit_523e92(uint32_t,uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
extern void audio_uart_nema_cl_unbind_5144ba(void);
static int32_t emit_signed_div(int32_t x,int32_t y) {
    if(y==0) return 0;
    if(x==INT32_MIN && y==-1) return INT32_MIN;
    return x/y;
}
static int32_t emit_space(volatile uint32_t *list) {
    uint32_t delta;
    if(((volatile uint8_t *)list)[24]&32u) {
        uint32_t sector=list[11],used=list[5];
        delta=sector-used+sector*(uint32_t)emit_signed_div((int32_t)used,(int32_t)sector);
    } else { uint32_t capacity=list[4],used=list[5];delta=capacity-used; }
    return (int32_t)delta/2;
}
static void emit_store(uint32_t base,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(base+index*4u)=value;
}
static void emit_pair(volatile uint32_t *list,uint32_t first,uint32_t second) {
    uint32_t used=list[5];
    emit_store(list[2],used,first);
    ++used;
    emit_store(list[2],used,second);
    list[5]=used+1u;
}
/* Native514846..514aec. Full sector/padding/allocation/chaining paths. */
void audio_uart_nema_child_514846(uint32_t reg,uint32_t value) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    volatile uint32_t *list=(void *)(uintptr_t)context[1];
    if(!list) { audio_uart_nema_register_emit_523e92(reg,value);return; }
    list[6]=list[6]&~8u;
    int32_t available=emit_space(list);
    uint32_t flags=list[6];
    if(flags&32u) {
        if(available<=1) {
            ((volatile uint8_t *)context)[249]=0u;
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            audio_uart_nema_sector_rollover_5147b0((void *)(uintptr_t)context[1]);
        }
    } else if(!(flags&2u)) {
        uint32_t used=list[5],capacity=list[4];
        if((int32_t)capacity<(int32_t)(used+2u)) {audio_uart_nema_error_set_4b127c(8u);return;}
    } else {
        uint32_t used=list[5],capacity=list[4];
        if((int32_t)(used+4u)>=(int32_t)capacity) {
            int32_t padding=(int32_t)((uint32_t)emit_space(list)-2u);
            if(padding>0) {
                uint32_t n=(uint32_t)padding;
                for(uint32_t i=0;i<(n&3u);++i) emit_pair(list,0x10000u,0u);
                for(uint32_t i=0;i<(n>>2);++i) {
                    uint32_t k=list[5];
                    emit_store(list[2],k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    uint32_t data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);list[5]=k+1u;
                }
            }
            volatile uint32_t *node=(void *)(uintptr_t)list[8];
            if(!node) {
                node=audio_uart_nema_node_allocate_51416c(60u);
                if(!node) {audio_uart_nema_error_set_4b127c(16u);return;}
                uint32_t desc[4];audio_uart_nema_buffer_create_514070(desc,0u,1024u);
                node[0]=desc[0];node[1]=desc[1];node[2]=desc[2];node[3]=desc[3];
                node[4]=(uint32_t)((int32_t)desc[0]/8)*2u;
                node[5]=0u;node[7]=UINT32_MAX;node[13]=UINT32_MAX;node[14]=UINT32_MAX;node[6]=2u;
                uint32_t data=node[2];
                node[8]=0u;node[9]=0u;node[10]=0u;node[11]=0u;node[12]=0u;
                if(!data) {audio_uart_nema_error_set_4b127c(16u);audio_uart_nema_cl_node_release_514178((void *)node);return;}
                context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
                list=(void *)(uintptr_t)context[1];
                uint32_t root=list[9];node[9]=root?root:(uint32_t)(uintptr_t)list;
                list=(void *)(uintptr_t)context[1];node[6]=list[6]&~12u;
            }
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            list=(void *)(uintptr_t)context[1];
            if(!list) audio_uart_nema_error_set_4b127c(8192u);
            else list[6]=list[6]|4u;
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            list=(void *)(uintptr_t)context[1];
            uint32_t k=list[5];
            emit_store(list[2],k,240u);++k;
            uint32_t address=node[3];emit_store(list[2],k,address);++k;
            uint32_t data=list[2];list[5]=k;
            emit_store(data,k,244u);++k;
            uint32_t capacity_next=node[4];emit_store(list[2],k,capacity_next);list[5]=k+1u;list[8]=(uint32_t)(uintptr_t)node;
            if(!node) audio_uart_nema_error_set_4b127c(8192u);
            else if(((volatile uint8_t *)node)[12]&7u) audio_uart_nema_error_set_4b127c(16384u);
            else {
                if(context[1]) audio_uart_nema_cl_unbind_5144ba();
                while(((volatile uint8_t *)node)[24]&4u) node=(void *)(uintptr_t)node[8];
                context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];context[1]=(uint32_t)(uintptr_t)node;
            }
        }
    }
    context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    list=(void *)(uintptr_t)context[1];
    emit_pair(list,reg,value);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
/* Native523e92..523f0e: cached ring/data/capacity, fresh write-index reads. */
void audio_uart_nema_register_emit_523e92(uint32_t reg,uint32_t value) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t index=ring[4];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    if((int32_t)capacity<(int32_t)(index+2u)) {
        do {
            ring[4]=index;
            *(volatile uint32_t *)(uintptr_t)(data+index*4u)=0x10000u;
            index=ring[4]+1u;
        } while((int32_t)index<(int32_t)capacity && index!=0u);
        ring[4]=0u;
    }
    index=ring[4];
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=reg;
    index=ring[4]+1u;
    if((int32_t)index>=(int32_t)capacity)index=0u;
    ring[4]=index;
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
    index=ring[4]+1u;
    if((int32_t)index>=(int32_t)capacity)index=0u;
    ring[4]=index;
    if(reg&0xff000000u) {
        audio_uart_nema_buffer_flush_5140ea((void *)ring);
        ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
        uint32_t physical=audio_uart_nema_ring_descriptor[2];
        index=ring[4];
        audio_uart_nema_reg_write_514046(236u,(physical+index*4u)|4u);
    }
}

#include <stdint.h>
extern void *audio_uart_lv_pool_allocate_484180(void *,uint32_t);
/* Native51416c..514178, same source pool contract as node-release514178. */
void *audio_uart_nema_node_allocate_51416c(uint32_t size) { return audio_uart_lv_pool_allocate_484180((void *)(uintptr_t)0x20000338u,size); }

#include <stdint.h>
extern void *audio_uart_nema_pool_select_514050(uint32_t);
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *);
extern void audio_ble_privacy_cache_maintenance(const uint32_t *,uint8_t);
/* Native5140ea..51411a: conditional clean, unconditional DSB. */
void audio_uart_nema_buffer_flush_5140ea(void *buffer) {
    volatile uint32_t *b=buffer;
    const volatile uint8_t *pool=audio_uart_nema_pool_select_514050(b[1]);
    if(pool[24]!=0u) {
        uint32_t size=b[0];
        uint32_t physical=b[3];
        uint32_t range[2]={physical,size};
        (void)audio_uart_cache_clean_range_47510e(range);
    }
    __asm__ volatile("dsb sy" ::: "memory");
}
/* Native51411a..514148: conditional invalidate, no extra barrier here. */
void audio_uart_nema_buffer_invalidate_51411a(void *buffer) {
    volatile uint32_t *b=buffer;
    const volatile uint8_t *pool=audio_uart_nema_pool_select_514050(b[1]);
    if(pool[24]!=0u) {
        uint32_t size=b[0];
        uint32_t physical=b[3];
        uint32_t range[2]={physical,size};
        audio_ble_privacy_cache_maintenance(range,0u);
    }
}
/* Native514148..51416c: two fresh base loads; unsigned wrapped interval test. */
uint32_t audio_uart_nema_pool_contains_514148(uint32_t id,uint32_t address,uint32_t size) {
    const volatile uint32_t *pool=audio_uart_nema_pool_select_514050(id);
    uint32_t base_first=pool[5];
    uint32_t base_second=pool[5];
    uint32_t length=pool[4];
    uint32_t end=base_second+length;
    if(address<base_first) return 0u;
    return end>=address+size;
}

#include <stdint.h>
static uint32_t clean_read(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void clean_write(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void clean_barrier(void){__asm__ volatile("dsb sy\n\tisb sy" ::: "memory");}
/* Native47510e..475194: source-owned SCB addresses and native cache policy. */
uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *range) {
    if(!(clean_read(0xe000ed14u)&(1u<<16))) {clean_barrier();return 0u;}
    if(!range) {
        clean_write(0xe000ed84u,0u);
        __asm__ volatile("dsb sy" ::: "memory");
        uint32_t ccsidr=clean_read(0xe000ed80u);
        uint32_t set=(ccsidr>>13)&0x7fffu;
        do {
            uint32_t way=(ccsidr>>3)&0x3ffu;
            do {
                clean_write(0xe000ef6cu,((set<<5)&0x3fe0u)|(way<<30));
                if(way==0u)break;
                --way;
            } while(1);
            if(set==0u)break;
            --set;
        } while(1);
        clean_barrier();
    } else {
        const volatile uint32_t *r=range;
        uint32_t size=r[1];
        uint32_t address=r[0];
        if((int32_t)size>=1) {
            uint32_t remaining=(address&31u)+size;
            __asm__ volatile("dsb sy" ::: "memory");
            do {
                clean_write(0xe000ef68u,address);
                address+=32u;
                remaining-=32u;
            } while((int32_t)remaining>=1);
            clean_barrier();
        }
    }
    return 0u;
}

#include <stdint.h>
extern void *audio_uart_nema_pool_select_514050(uint32_t);
extern void *audio_uart_lv_pool_allocate_484180(void *,uint32_t);
extern void *audio_uart_lv_pool_aligned_allocate_4841d8(void *,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
/* Native514070..5140c6: hidden descriptor output, original full-width pool ID. */
void audio_uart_nema_buffer_create_514070(uint32_t *out,uint32_t id,uint32_t size) {
    void *pool=audio_uart_nema_pool_select_514050(id);
    void *pointer;
    if(((const volatile uint8_t *)pool)[24]!=0u) {
        size=(size+31u)&~31u;
        pointer=audio_uart_lv_pool_aligned_allocate_4841d8(pool,size,32u);
    } else if(id<=2u) pointer=audio_uart_lv_pool_aligned_allocate_4841d8(pool,size,8u);
    else pointer=audio_uart_lv_pool_allocate_484180(pool,size);
    uint32_t descriptor[4]={size,id,(uint32_t)(uintptr_t)pointer,(uint32_t)(uintptr_t)pointer};
    audio_uart_checksum_copy(out,descriptor,16u);
}

#include <stdint.h>
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *audio_uart_lv_tlsf_aligned_allocate_4d0744(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_allocation_size_4d05e4(void *);
/* Native4841d8..484234: locked allocation and fresh accounting/high-water reads. */
void *audio_uart_lv_pool_aligned_allocate_4841d8(void *cell,uint32_t bytes,uint32_t alignment) {
    volatile uint32_t *pool=cell;
    void *result=0;
    if(bytes==0u)return 0;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)==1) {
        result=audio_uart_lv_tlsf_aligned_allocate_4d0744((void *)(uintptr_t)pool[1],alignment,bytes);
        if(result) {
            uint32_t size=audio_uart_lv_allocation_size_4d05e4(result);
            pool[2]=size+pool[2];
            uint32_t high=pool[3];
            uint32_t current=pool[2];
            if(high<current)high=pool[2];else high=pool[3];
            pool[3]=high;
        }
        (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0u,0u);
    }
    return result;
}

#include <stdint.h>
extern uint32_t g2_tlsf_adjust_request(uint32_t,uint32_t);
extern void *g2_tlsf_find_suitable(void *,uint32_t);
extern void *g2_tlsf_block_to_ptr(void *);
extern void *g2_tlsf_align_ptr(void *,uint32_t);
extern void *g2_tlsf_trim_free_leading_4d0444(void *,void *,uint32_t);
extern void *g2_tlsf_prepare_allocation(void *,void *,uint32_t);
extern void g2_file_close_error(const char *,const char *,uint32_t);
/* Native4d0744..4d0802, pinned TLSF alignment policy with native gap16. */
void *audio_uart_lv_tlsf_aligned_allocate_4d0744(void *pool,uint32_t alignment,uint32_t size) {
    uint32_t adjusted=g2_tlsf_adjust_request(size,4u);
    uint32_t requested=g2_tlsf_adjust_request(alignment+adjusted+16u,alignment);
    if(adjusted==0u || alignment<5u)requested=adjusted;
    void *block=g2_tlsf_find_suitable(pool,requested);
    uint32_t minimum=*(const volatile uint32_t *)(uintptr_t)0x78f4c4u;
    uint32_t overhead=*(const volatile uint32_t *)(uintptr_t)0x78f4bcu;
    if(minimum+overhead!=16u)g2_file_close_error("sizeof(block_header_t) == block_size_min + block_header_overhead","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf.c",1149u);
    if(block) {
        void *ptr=g2_tlsf_block_to_ptr(block);
        void *aligned=g2_tlsf_align_ptr(ptr,alignment);
        uint32_t gap=(uint32_t)(uintptr_t)aligned-(uint32_t)(uintptr_t)ptr;
        if(gap!=0u && gap<16u) {
            uint32_t offset=16u-gap;
            if(alignment>=offset)offset=alignment;
            aligned=g2_tlsf_align_ptr((void *)(uintptr_t)((uint32_t)(uintptr_t)aligned+offset),alignment);
            gap=(uint32_t)(uintptr_t)aligned-(uint32_t)(uintptr_t)ptr;
        }
        if(gap) {
            if(gap<16u)g2_file_close_error("gap >= gap_minimum && \"gap size too small\"","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf.c",1173u);
            block=g2_tlsf_trim_free_leading_4d0444(pool,block,gap);
        }
    }
    return g2_tlsf_prepare_allocation(pool,block,adjusted);
}

#include <stdint.h>
extern uint32_t g2_tlsf_block_can_split(void *,uint32_t);
extern void *g2_tlsf_block_split(void *,uint32_t);
extern void g2_tlsf_block_set_prev_free(void *);
extern void *g2_tlsf_block_link_next(void *);
extern void g2_tlsf_block_insert(void *,void *);
/* Native4d0444..4d0484: leading free-block split and original-block reinsertion. */
void *g2_tlsf_trim_free_leading_4d0444(void *pool,void *block,uint32_t size) {
    void *result=block;
    if(g2_tlsf_block_can_split(block,size)!=0u) {
        uint32_t overhead=*(const volatile uint32_t *)(uintptr_t)0x78f4bcu;
        result=g2_tlsf_block_split(block,size-overhead);
        g2_tlsf_block_set_prev_free(result);
        (void)g2_tlsf_block_link_next(block);
        g2_tlsf_block_insert(pool,block);
    }
    return result;
}

#include <stdint.h>
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_list_finalize_514b7c(void *);
extern void audio_uart_nema_submit_523f10(uint32_t);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
static int32_t rollover_divide(int32_t a,int32_t b) {
    if(b==0)return 0;
    if(a==INT32_MIN && b==-1)return INT32_MIN;
    return a/b;
}
/* Native5147b0..514846: preserve native quarter-sector policy and ready1 unconditional submit. */
void audio_uart_nema_sector_rollover_5147b0(void *cell) {
    volatile uint32_t *list=(volatile uint32_t *)cell;
    if(!list) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t flags=((volatile uint8_t *)cell)[24];
    uint32_t used=list[5];
    if(flags&32u) {
        uint32_t sector=list[11];
        int32_t quotient=rollover_divide((int32_t)used,(int32_t)sector);
        if(used-sector*(uint32_t)quotient==0u)return;
    } else if(used==0u)return;
    audio_uart_nema_list_finalize_514b7c(cell);
    if(((volatile uint8_t *)cell)[24]&32u) {
        volatile uint8_t *context=*(volatile uint8_t * volatile *)(uintptr_t)0x20074efcu;
        uint32_t ready=context[249];
        if(ready!=1u) {
            uint32_t capacity=list[10],quarter=capacity>>2,position=list[12];
            if(position!=quarter && position!=(capacity>>1) && position!=quarter*3u && position!=0u && list[13]!=0x00ffffffu)goto after_submit;
        }
        audio_uart_nema_submit_523f10(list[13]);
        list[7]=list[13];
    } else audio_uart_nema_submit_523f10(list[7]);
after_submit:
    if(list[7]==0x00ffffffu && audio_uart_nema_poll_514026(0x00ffffffu)>=0)list[7]=UINT32_MAX;
}

#include <stdint.h>
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
extern uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_chain_finalize_523dba(void *,uint32_t);
static int32_t finalize_divide(int32_t a,int32_t b) {
    if(b==0)return 0;
    if(a==INT32_MIN && b==-1)return INT32_MIN;
    return a/b;
}
static void finalize_flush_sector(volatile uint32_t *list,uint32_t data) {
    uint32_t offset=list[12]*list[11];
    uint32_t physical=list[3]+offset*4u;
    uint32_t descriptor[4];
    descriptor[3]=physical;descriptor[2]=data+offset*4u;
    descriptor[0]=list[11]*4u;descriptor[1]=list[1];
    audio_uart_nema_buffer_flush_5140ea(descriptor);
}
/* Native514b7c..514cf2: sector finalization and chained-buffer flush/link policy. */
void audio_uart_nema_list_finalize_514b7c(void *cell) {
    volatile uint32_t *root=(volatile uint32_t *)cell;
    if(!root) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t flags=root[6],used=root[5];
    if(flags&32u) {
        uint32_t sector=root[11];
        uint32_t residue=used-sector*(uint32_t)finalize_divide((int32_t)used,(int32_t)sector);
        if(residue==0u)return;
        uint32_t offset=sector*root[12];
        uint32_t physical=root[3]+offset*4u;
        if(!(flags&8u)) {
            uint32_t virtual_address=root[2]+offset*4u;
            uint32_t descriptor[4]={root[11]*4u,root[1],virtual_address,physical};
            audio_uart_nema_buffer_flush_5140ea(descriptor);
            root[6]=root[6]|8u;
        }
        uint32_t submitted=audio_uart_nema_reg_read_51403c(328u);
        uint32_t capacity=root[10],sequence=root[13];
        root[14]=submitted;
        if((int32_t)(sequence-submitted)>(int32_t)(capacity-2u))
            (void)audio_uart_nema_poll_514026(submitted+1u);
        root[13]=audio_uart_nema_sector_finalize_523ce0(physical,residue);
        uint32_t position=root[12]+1u;
        capacity=root[10];
        uint32_t next_used;
        if(position>=capacity) {position=0u;next_used=0u;}
        else next_used=root[11]*position;
        root[5]=next_used;root[12]=position;
        return;
    }
    if(used==0u)return;
    volatile uint32_t *list=root;
    for(;;) {
        uint32_t byteflags=((volatile uint8_t *)list)[24];
        uint32_t data=list[2];
        volatile uint32_t *next=(volatile uint32_t *)(uintptr_t)list[8];
        if(byteflags&4u) {
            if(next) {
                uint32_t capacity=list[4],next_used=next[5];
                *(volatile uint32_t *)(uintptr_t)(data+capacity*4u-4u)=next_used;
            }
            flags=list[6]&~8u;list[6]=flags;
            if(flags&32u)finalize_flush_sector(list,data);
            else audio_uart_nema_buffer_flush_5140ea((void *)list);
            list[6]=list[6]|8u;
            list=(volatile uint32_t *)(uintptr_t)list[8];
            if(list)continue;
            break;
        }
        flags=list[6];
        if(flags&8u)break;
        if(flags&32u) {
            /* Native branch re-reads virtual pointer after physical pointer. */
            uint32_t offset=list[12]*list[11];
            uint32_t physical=list[3]+offset*4u;
            uint32_t virtual_address=list[2]+offset*4u;
            uint32_t descriptor[4]={list[11]*4u,list[1],virtual_address,physical};
            audio_uart_nema_buffer_flush_5140ea(descriptor);
        } else audio_uart_nema_buffer_flush_5140ea((void *)list);
        list[6]=list[6]|8u;
        break;
    }
    root[7]=audio_uart_nema_chain_finalize_523dba(cell,root[5]);
}

#include <stdint.h>
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern void g2_file_heap_error_log(const char *);
extern volatile uint32_t audio_uart_nema_last_submission;
/* Native51400a..51403c: exact semaphore-success gate, native fail-stop, signed submission wait. */
void audio_uart_nema_wait_irq_51400a(void) {
    void *handle=*(void * volatile *)(uintptr_t)0x20074814u;
    if(xQueueSemaphoreTake(handle,1000u)!=1) {
        g2_file_heap_error_log("GPU assert!!! nema_wait_irq timeout!!!\n");
        for(;;) {}
    }
}
int32_t audio_uart_nema_poll_514026(uint32_t submission) {
    while((int32_t)audio_uart_nema_last_submission<(int32_t)submission)
        audio_uart_nema_wait_irq_51400a();
    return 0;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void submit_store(uint32_t data,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
}
static uint32_t submit_advance(volatile uint32_t *ring,uint32_t capacity) {
    uint32_t index=ring[4]+1u;
    return (int32_t)index>=(int32_t)capacity?0u:index;
}
static uint32_t submit_pad(volatile uint32_t *ring,uint32_t data,uint32_t capacity,uint32_t index) {
    do {
        ring[4]=index;submit_store(data,index,0x10000u);
        index=ring[4]+1u;
    } while((int32_t)index<(int32_t)capacity && index!=0u);
    return 0u;
}
/* Native523f10..52404a: signed submission gate, ring command/padding/alignment, fresh descriptor after flush. */
void audio_uart_nema_submit_523f10(uint32_t submission) {
    if((int32_t)submission<=0)return;
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t index=ring[4];
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    if((int32_t)capacity<(int32_t)(index+2u)) {index=submit_pad(ring,data,capacity,index);ring[4]=index;}
    index=ring[4];submit_store(data,index,328u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,submission);
    index=submit_advance(ring,capacity);
    if((int32_t)capacity<(int32_t)(index+2u))index=submit_pad(ring,data,capacity,index);
    ring[4]=index;submit_store(data,index,248u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,1u);
    index=submit_advance(ring,capacity);
    if((int32_t)(index+4u)>=(int32_t)capacity)index=submit_pad(ring,data,capacity,index);
    while(index&3u) {
        ring[4]=index;submit_store(data,index,0x10000u);
        index=submit_advance(ring,capacity);
    }
    uint32_t physical=audio_uart_nema_ring_descriptor[2];
    ring[4]=index;submit_store(data,index,0xff0000f0u);
    uint32_t target=physical+(index+4u)*4u;
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,target);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,0xff0000f4u);
    index=submit_advance(ring,capacity);ring[4]=index;submit_store(data,index,audio_uart_nema_ring_descriptor[4]);
    index=submit_advance(ring,capacity);ring[4]=index;
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    physical=audio_uart_nema_ring_descriptor[2];index=ring[4];
    audio_uart_nema_reg_write_514046(236u,(physical+index*4u)|4u);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void packet_store(uint32_t data,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+index*4u)=value;
}
static uint32_t packet_advance(volatile uint32_t *ring,uint32_t capacity) {
    uint32_t index=ring[4]+1u;
    return (int32_t)index>=(int32_t)capacity?0u:index;
}
static uint32_t packet_pad(volatile uint32_t *ring,uint32_t data,uint32_t capacity,uint32_t index) {
    do {
        ring[4]=index;packet_store(data,index,0x10000u);
        index=ring[4]+1u;
    } while((int32_t)index<(int32_t)capacity && index!=0u);
    return 0u;
}
static uint32_t packet_emit(uint32_t physical,uint32_t words) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3],data=audio_uart_nema_ring_descriptor[1];
    uint32_t index=ring[4];
    if((int32_t)(index+4u)>=(int32_t)capacity) {index=packet_pad(ring,data,capacity,index);ring[4]=index;}
    while(((volatile uint8_t *)ring)[16]&3u) {
        index=ring[4];packet_store(data,index,0x10000u);
        index=packet_advance(ring,capacity);ring[4]=index;
    }
    index=ring[4];packet_store(data,index,240u);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,physical);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,0x000200f4u);
    index=packet_advance(ring,capacity);ring[4]=index;packet_store(data,index,words);
    index=packet_advance(ring,capacity);ring[4]=index;
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t current_physical=audio_uart_nema_ring_descriptor[2];index=ring[4];
    audio_uart_nema_reg_write_514046(236u,(current_physical+index*4u)|4u);
    ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    uint32_t sequence=ring[5]+1u;
    if((int32_t)sequence>=0x01000000)sequence=0u;
    ring[5]=sequence;return sequence;
}
/* Native523ce0..523dba and523dba..523e92: packet wrappers with distinct zero-length read policy. */
uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t physical,uint32_t words) {
    if(words==0u)return UINT32_MAX;
    return packet_emit(physical,words);
}
uint32_t audio_uart_nema_chain_finalize_523dba(void *cell,uint32_t words) {
    uint32_t physical=((volatile uint32_t *)cell)[3];
    if(words==0u)return UINT32_MAX;
    return packet_emit(physical,words);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_ring_descriptor[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
static void ring_init_store(uint32_t data,uint32_t offset,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(data+offset)=value;
}
/* Native523bf8..523c88: descriptor always records size; signed positive-size gate. */
int32_t audio_uart_nema_ring_initialize_523bf8(void *cell,uint32_t initialize) {
    volatile uint32_t *ring=cell;
    uint32_t size=ring[0];audio_uart_nema_ring_descriptor[4]=size;
    if((int32_t)size<=0) {audio_uart_nema_error_set_4b127c(4u);return -1;}
    audio_uart_nema_ring_descriptor[0]=(uint32_t)(uintptr_t)cell;
    uint32_t data=ring[2];audio_uart_nema_ring_descriptor[1]=data;
    uint32_t physical=ring[3];
    uint32_t capacity=(uint32_t)((int32_t)size/4)-4u;
    audio_uart_nema_ring_descriptor[2]=physical;audio_uart_nema_ring_descriptor[3]=capacity;
    if(initialize!=0u) {
        ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
        ring[4]=0u;ring[5]=0u;
        uint32_t tail=data+capacity*4u;
        ring_init_store(tail,0u,0xff0000f0u);ring_init_store(tail,4u,physical);
        ring_init_store(tail,8u,0xff0000f4u);ring_init_store(tail,12u,size);
        audio_uart_nema_buffer_flush_5140ea((void *)ring);
        audio_uart_nema_reg_write_514046(328u,0u);
        physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(236u,physical|6u);
        physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(240u,physical);
        size=audio_uart_nema_ring_descriptor[4];audio_uart_nema_reg_write_514046(244u,size);
    }
    return 0;
}
/* Native523c88..523ce0: tail store order differs from first initialization. */
void audio_uart_nema_child_523c88(void) {
    volatile uint32_t *ring=(void *)(uintptr_t)audio_uart_nema_ring_descriptor[0];
    ring[4]=0u;ring[5]=0u;
    uint32_t data=audio_uart_nema_ring_descriptor[1];
    uint32_t capacity=audio_uart_nema_ring_descriptor[3];
    uint32_t tail=data+capacity*4u;
    ring_init_store(tail,0u,0xff0000f0u);
    uint32_t physical=audio_uart_nema_ring_descriptor[2];
    ring_init_store(tail,8u,0xff0000f4u);ring_init_store(tail,4u,physical);
    uint32_t size=audio_uart_nema_ring_descriptor[4];ring_init_store(tail,12u,size);
    audio_uart_nema_buffer_flush_5140ea((void *)ring);
    audio_uart_nema_reg_write_514046(328u,0u);
    physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(236u,physical|6u);
    physical=audio_uart_nema_ring_descriptor[2];audio_uart_nema_reg_write_514046(240u,physical);
    size=audio_uart_nema_ring_descriptor[4];audio_uart_nema_reg_write_514046(244u,size);
}

#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
/* Native522920..52294c: address command precedes zero-count gate, two words per upload. */
void audio_uart_nema_instruction_upload_522920(const uint32_t *words,uint32_t count,uint32_t address) {
    audio_uart_nema_child_514846(196u,address);
    while(count!=0u) {
        const volatile uint32_t *p=words;
        audio_uart_nema_child_514846(200u,p[0]);
        uint32_t second=p[1];words=(void *)((uintptr_t)words+8u);
        audio_uart_nema_child_514846(204u,second);count--;
    }
}
/* Native522956..522960: command464 scalar wrapper. */
void audio_uart_nema_rop_blend_mode_522956(uint32_t value) {audio_uart_nema_child_514846(464u,value);}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
/* Native514384..5143d4: parent redirection, chained rewind and bound-parent update. */
void audio_uart_nema_cl_rewind_514384(void *cell) {
    volatile uint32_t *list=cell;
    if(!list) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t parent=list[9];
    if(parent)list=(volatile uint32_t *)(uintptr_t)parent;
    do {
        parent=list[9];
        if(parent) {
            volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
            if(context[1]==(uint32_t)(uintptr_t)list)context[1]=parent;
        }
        list[5]=0;list[12]=0;
        list[6]=list[6]&~4u;
        list=(volatile uint32_t *)(uintptr_t)list[8];
    }while(list);
}
/* Native514cf2..514d00: context byte precedes the tail-called rollover. */
void audio_uart_nema_cl_submit_514cf2(void *cell) {
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
    context[249]=1;
    audio_uart_nema_sector_rollover_5147b0(cell);
}
/* Native514d00..514d2c: negative ID skips polling; successful poll resets ID. */
int32_t audio_uart_nema_cl_wait_514d00(void *cell) {
    volatile uint32_t *list=cell;
    if(!list){audio_uart_nema_error_set_4b127c(8192u);return -1;}
    uint32_t submission=list[7];
    if((int32_t)submission<0 || audio_uart_nema_poll_514026(submission)>=0)list[7]=UINT32_MAX;
    return 0;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern volatile uint32_t audio_uart_nema_last_submission;
extern volatile uint32_t audio_uart_nema_command_state_20073bf0[];
/* Native51418e..514194. */
int32_t audio_uart_nema_last_cl_id_51418e(void) {return (int32_t)audio_uart_nema_last_submission;}
/* Native514194..51419a: command state offset20, distinct from IRQ completion cell. */
uint32_t audio_uart_nema_last_submission_id_514194(void) {return audio_uart_nema_command_state_20073bf0[5];}
/* Native5144fa..514504: fresh context pointer then bound list word. */
void *audio_uart_nema_cl_get_bound_5144fa(void) {
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)*(volatile uint32_t *)audio_uart_nema_context_cell;
 return (void *)(uintptr_t)context[1];
}

#include <stdint.h>
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
/* Native514278..5142ee: buffer descriptor, signed capacity, full60byte list. */
void audio_uart_nema_cl_create_sized_514278(void *out,uint32_t bytes) {
 uint32_t descriptor[4];
 audio_uart_nema_buffer_create_514070(descriptor,0u,bytes);
 uint32_t row[15];
 row[0]=descriptor[0];row[1]=descriptor[1];row[2]=descriptor[2];row[3]=descriptor[3];
 row[4]=(uint32_t)(((int32_t)descriptor[0]/8)*2);
 row[5]=0;row[6]=0;row[7]=UINT32_MAX;
 row[8]=0;row[9]=0;row[10]=0;row[11]=0;row[12]=0;
 row[13]=UINT32_MAX;row[14]=UINT32_MAX;
 uint32_t *destination=out;
 for(uint32_t i=0;i<15;i++)destination[i]=row[i];
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
static int32_t bind236_div(uint32_t a,uint32_t b) {
 int32_t result;__asm__("sdiv %0, %1, %2":"=r"(result):"r"(a),"r"(b));return result;
}
/* Native5143d4..5144ba: G2 sector negotiation and cached previous-list unbind. */
void audio_uart_nema_cl_bind_sectored_5143d4(void *cell,uint32_t sectors) {
 volatile uint32_t *list=cell;
 if(!list){audio_uart_nema_error_set_4b127c(8192u);return;}
 if(((volatile uint8_t *)list)[12]&7u){audio_uart_nema_error_set_4b127c(16384u);return;}
 uint32_t parent=list[9];if(parent)list=(volatile uint32_t *)(uintptr_t)parent;
 if((int32_t)sectors<2)sectors=2;
 else if((int32_t)sectors>2){
  uint32_t bytes=list[4]*4u;int32_t quotient=bind236_div(bytes,sectors);
  if(quotient<512){
   if(sectors&1u)sectors++;
   while((int32_t)sectors>=4){sectors-=2;quotient=bind236_div(bytes,sectors);if(quotient>=512)break;}
   if(quotient<512){audio_uart_nema_error_set_4b127c(65536u);return;}
  }
 }
 uint32_t bytes=list[4]*4u;uint32_t quotient=(uint32_t)bind236_div(bytes,sectors);
 if(bytes-sectors*quotient){audio_uart_nema_error_set_4b127c(16384u);return;}
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *previous=(volatile uint32_t *)(uintptr_t)context[1];
 if(previous){
  uint32_t used=previous[5],capacity=previous[4];
  if((int32_t)capacity>=(int32_t)(used+2u)){
   uint32_t data=previous[2];
   *(volatile uint32_t *)(uintptr_t)(data+used*4u)=0x00050000u;
   *(volatile uint32_t *)(uintptr_t)(data+4u+used*4u)=0;
   previous[6]=previous[6]&~8u;
  }
  previous[6]=previous[6]&~32u;context[1]=0;
 }
 list[6]=list[6]|32u;list[13]=UINT32_MAX;list[14]=UINT32_MAX;
 uint32_t words=(uint32_t)bind236_div(list[4],sectors);if(words&1u)words--;
 list[11]=words;list[10]=sectors;list[12]=0;
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];context[1]=(uint32_t)(uintptr_t)list;
}

#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
/* Native523304..52330c: command-buffer interrupt control, not immediate register write. */
void audio_uart_nema_child_523304(uint32_t value) {audio_uart_nema_child_514846(248u,value);}

#include <stdint.h>
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
/* Native515096..5150ea: sparse paint initialization; untouched fields preserved. */
void *audio_uart_nema_vg_paint_create_515096(void) {
 volatile uint8_t *paint=audio_uart_nema_node_allocate_51416c(220u);
 if(!paint){audio_uart_nema_vg_set_error_51565c(1u);return (void *)paint;}
 *(volatile uint32_t *)(paint+0)=0;*(volatile uint32_t *)(paint+4)=0;
 paint[44]=0;paint[213]=0;paint[204]=0;
 *(volatile uint32_t *)(paint+48)=0;
 *(volatile uint32_t *)(paint+208)=0x3f800000u;
 *(volatile uint32_t *)(paint+216)=0xff000000u;
 audio_uart_nema_matrix_identity_561810((void *)(paint+52));
 audio_uart_nema_matrix_identity_561810((void *)(paint+8));
 paint[212]=0;return (void *)paint;
}
/* Native51510e..515136: buffer creation precedes unchecked output store. */
void *audio_uart_nema_vg_grad_create_51510e(void) {
 uint32_t *gradient=audio_uart_nema_node_allocate_51416c(16u);uint32_t descriptor[4];
 audio_uart_nema_buffer_create_514070(descriptor,1u,256u);
 gradient[0]=descriptor[0];gradient[1]=descriptor[1];gradient[2]=descriptor[2];gradient[3]=descriptor[3];
 return gradient;
}

#include <stdint.h>
/* Native561810..561830: exact IEEE754 identity words, ordered32bit stores. */
void audio_uart_nema_matrix_identity_561810(void *cell) {
 volatile uint32_t *matrix=cell;
 matrix[0]=0x3f800000u;matrix[1]=0;matrix[2]=0;matrix[3]=0;
 matrix[4]=0x3f800000u;matrix[5]=0;matrix[6]=0;matrix[7]=0;matrix[8]=0x3f800000u;
}

#include <stdint.h>
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
/* Native514ebc..514f34: pre-check absolute store and sparse path initialization. */
void *audio_uart_nema_vg_path_create_514ebc(void) {
 void *cell=audio_uart_nema_node_allocate_51416c(136u);
 uint32_t address=(uint32_t)(uintptr_t)cell;
 *(volatile uint32_t *)(uintptr_t)(address+132u)=0;
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return cell;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)(address+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
 return cell;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_child_52262e(uint32_t);
extern void audio_uart_nema_child_52264e(uint32_t);
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t);
static uint32_t bind243_align4(uint32_t x){x+=3u;return (x+((uint32_t)((int32_t)x>>1)>>30))&~3u;}
static uint32_t bind243_round8(uint32_t x){x+=7u;x+=(uint32_t)((int32_t)x>>2)>>29;return (uint32_t)((int32_t)x>>3);}
/* Native4b1298..4b146c: G2 format strides, context slots and three command pairs. */
void audio_uart_nema_bind_tex_4b1298(uint32_t unit,uint32_t address,uint32_t width,uint32_t height,int32_t format,uint32_t stride,uint32_t flags){
 if((int32_t)unit<0)return;
 uint32_t fmt=(uint32_t)format&127u;
 if(stride==UINT32_MAX){
  stride=width;
  if(flags&16u)stride=bind243_align4(stride);
  if(fmt==18u||fmt==22u||fmt==23u||fmt==78u)stride=bind243_align4(stride);
  if(fmt==76u||fmt==77u){stride+=1u;stride=(stride+(stride>>31))&~1u;}
  switch(fmt){
  case 11u:case 12u:case 39u:case 42u:stride=bind243_round8(stride);break;
  case 18u:stride*=2u;break;
  case 22u:case 23u:case 76u:case 77u:case 78u:stride*=3u;break;
  case 40u:case 43u:case 48u:case 49u:stride=bind243_round8(stride*2u);break;
  case 41u:case 44u:case 52u:case 53u:stride=bind243_round8(stride*4u);break;
  default:{uint32_t factor=4u;switch(fmt){
   case 4u:case 5u:case 6u:case 13u:case 19u:case 29u:case 61u:case 62u:case 63u:case 68u:case 70u:case 71u:case 72u:case 73u:case 74u:case 75u:case 76u:case 77u:factor=2u;break;
   case 7u:case 8u:case 9u:case 12u:case 18u:case 22u:case 23u:case 24u:case 25u:case 26u:case 39u:case 40u:case 48u:case 49u:case 52u:case 53u:case 56u:case 64u:case 65u:case 66u:case 67u:case 69u:case 78u:factor=1u;break;
   case 57u:case 60u:factor=3u;break;
   default:break;}stride*=factor;break;}
  }
 }
 if(unit==0u){
  volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
  if(fmt==18u||fmt==22u||fmt==23u){ctx[8]=1;audio_uart_nema_child_52262e(1u);}
  else if(fmt==76u||fmt==77u){ctx[8]=1;audio_uart_nema_child_52264e(1u);}
  else audio_uart_nema_child_52262e(ctx[9]);
 }
 uint32_t offset=unit*24u;
 volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)(audio_uart_nema_context_cell[0]+offset+56u);
 slot[0]=address;slot[1]=width;slot[2]=height;
 slot[3]=(flags<<16)|((uint32_t)format<<24)|(stride&65535u);
 slot[4]=1;slot[5]=(uint32_t)format;
 volatile uint32_t *packet=audio_uart_nema_cl_get_space_514aec(3u);
 if(packet){
  uint32_t reg=unit*16u;
  packet[0]=reg;packet[1]=address;packet[2]=reg+4u;
  volatile uint32_t *fresh=(volatile uint32_t *)(uintptr_t)(audio_uart_nema_context_cell[0]+offset);
  uint32_t packed=fresh[17];packet[3]=packed;packet[4]=reg+8u;packet[5]=width|(height<<16);
 }
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
/* Native52264e..52266e: dual tiling state, distinct mask from52262e. */
void audio_uart_nema_child_52264e(uint32_t enabled){
 uint32_t flags=enabled?0xc0000000u:0u;
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 context[3]=flags;uint32_t a=context[5];uint32_t b=context[4];uint32_t c=context[7];
 context[6]=flags|a|b|c;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern int32_t audio_uart_nema_extend_bound_514504(uint32_t);
static int32_t space246_div(uint32_t a,uint32_t b){int32_t r;__asm__("sdiv %0, %1, %2":"=r"(r):"r"(a),"r"(b));return r;}
/* Native514aec..514b76: pair reservation with sector rollover or list extension. */
void *audio_uart_nema_cl_get_space_514aec(uint32_t pairs){
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list){audio_uart_nema_error_set_4b127c(128u);return 0;}
 list[6]=list[6]&~8u;
 uint32_t remaining;
 if(((volatile uint8_t *)list)[24]&32u){uint32_t sector=list[11],used=list[5];remaining=sector-used+sector*(uint32_t)space246_div(used,sector);}
 else {uint32_t capacity=list[4],used=list[5];remaining=capacity-used;}
 uint32_t half=(uint32_t)((int32_t)(remaining+(remaining>>31))>>1);
 if(((volatile uint8_t *)list)[24]&32u){
  if((int32_t)half<(int32_t)(pairs+1u)){
   ((volatile uint8_t *)context)[249]=0;
   context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
   audio_uart_nema_sector_rollover_5147b0((void *)(uintptr_t)context[1]);
  }
 }else if((int32_t)(half-2u)<(int32_t)pairs){if(audio_uart_nema_extend_bound_514504(pairs)<0)return 0;}
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 list=(volatile uint32_t *)(uintptr_t)context[1];uint32_t used=list[5],data=list[2];
 uint32_t pointer=data+used*4u;list[5]=used+pairs*2u;return (void *)(uintptr_t)pointer;
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
static int32_t ext247_div(uint32_t a,uint32_t b){int32_t r;__asm__("sdiv %0, %1, %2":"=r"(r):"r"(a),"r"(b));return r;}
static void ext247_store(uint32_t data,uint32_t index,uint32_t v){*(volatile uint32_t *)(uintptr_t)(data+index*4u)=v;}
/* Native514504..5147b0: padding, allocation or reuse, chain packet and rebound tail. */
int32_t audio_uart_nema_extend_bound_514504(uint32_t pairs){
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list){audio_uart_nema_error_set_4b127c(128u);return -1;}
 uint32_t flags=((volatile uint8_t *)list)[24];
 if(!(flags&2u)){audio_uart_nema_error_set_4b127c(8u);return -1;}
 uint32_t delta;
 if(flags&32u){uint32_t sector=list[11],used=list[5];delta=sector-used+sector*(uint32_t)ext247_div(used,sector);}
 else {uint32_t capacity=list[4],used=list[5];delta=capacity-used;}
 int32_t padding=(int32_t)((uint32_t)((int32_t)(delta+(delta>>31))>>1)-2u);
 if(padding>0){
  uint32_t n=(uint32_t)padding;
  for(uint32_t i=0;i<(n&3u);i++){uint32_t k=list[5];ext247_store(list[2],k,65536u);k++;ext247_store(list[2],k,0);list[5]=k+1u;}
  for(uint32_t i=0;i<(n>>2);i++){
   uint32_t k=list[5];ext247_store(list[2],k,65536u);k++;ext247_store(list[2],k,0);k++;
   uint32_t data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);k++;
   data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);k++;
   data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);list[5]=k+1u;
  }
 }
 volatile uint32_t *node=(volatile uint32_t *)(uintptr_t)list[8];
 if(!node){
  node=audio_uart_nema_node_allocate_51416c(60u);if(!node){audio_uart_nema_error_set_4b127c(16u);return -1;}
  uint32_t bytes=(pairs+2u)*8u;uint32_t large=(int32_t)bytes>1024;
  uint32_t desc[4];audio_uart_nema_buffer_create_514070(desc,0u,large?bytes:1024u);
  node[0]=desc[0];node[1]=desc[1];node[2]=desc[2];node[3]=desc[3];node[4]=(uint32_t)((int32_t)desc[0]/8)*2u;
  node[5]=0;node[6]=large?0u:2u;node[9]=0;node[7]=UINT32_MAX;node[13]=UINT32_MAX;node[14]=UINT32_MAX;
  uint32_t data=node[2];node[10]=0;node[11]=0;node[12]=0;node[8]=0;
  if(!data){audio_uart_nema_error_set_4b127c(16u);audio_uart_nema_cl_node_release_514178((void *)node);return -1;}
  context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
  uint32_t root=list[9];node[9]=root?root:(uint32_t)(uintptr_t)list;
  list=(volatile uint32_t *)(uintptr_t)context[1];node[6]=list[6]&~12u;
 }
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list)audio_uart_nema_error_set_4b127c(8192u);else list[6]=list[6]|4u;
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
 uint32_t k=list[5];ext247_store(list[2],k,240u);k++;uint32_t physical=node[3];ext247_store(list[2],k,physical);k++;
 uint32_t data=list[2];list[5]=k;ext247_store(data,k,244u);k++;uint32_t capacity=node[4];ext247_store(list[2],k,capacity);list[5]=k+1u;list[8]=(uint32_t)(uintptr_t)node;
 if(((volatile uint8_t *)node)[12]&7u){audio_uart_nema_error_set_4b127c(16384u);return 0;}
 list=(volatile uint32_t *)(uintptr_t)context[1];
 if(list){uint32_t used=list[5],cap=list[4];if((int32_t)cap>=(int32_t)(used+2u)){data=list[2];ext247_store(data,used,327680u);ext247_store(data+4u,used,0);list[6]=list[6]&~8u;}list[6]=list[6]&~32u;}
 context[1]=0;
 while(((volatile uint8_t *)node)[24]&4u)node=(volatile uint32_t *)(uintptr_t)node[8];
 context[1]=(uint32_t)(uintptr_t)node;return 0;
}

#include <stdint.h>
/* Authenticated native flash78f2f4 register-window base. Placement remains gated. */
const uint32_t audio_uart_nema_register_base=0x40090000u;

#include <stdint.h>
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern volatile uint32_t audio_uart_nema_vg_context_cell;
/* Native514e50..514eba: NULL error precedes all path stores. */
void audio_uart_nema_vg_path_reset_514e50(void *cell) {
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)((uint32_t)(uintptr_t)cell+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
}
/* Native515048..515096: sparse paint reset, two ordered identity calls. */
void audio_uart_nema_vg_paint_reset_515048(void *cell) {
 volatile uint8_t *paint=cell;
 if(!paint){audio_uart_nema_vg_set_error_51565c(1u);return;}
 *(volatile uint32_t *)(paint+0u)=0;*(volatile uint32_t *)(paint+4u)=0;
 paint[44]=0;paint[213]=0;paint[204]=0;
 *(volatile uint32_t *)(paint+48u)=0;
 *(volatile uint32_t *)(paint+208u)=0x3f800000u;
 *(volatile uint32_t *)(paint+216u)=0xff000000u;
 audio_uart_nema_matrix_identity_561810((void *)(paint+52u));
 audio_uart_nema_matrix_identity_561810((void *)(paint+8u));
 paint[212]=0;
}
/* Native515676..5156aa: fresh context loads bracket real matrix calls. */
void audio_uart_nema_vg_state_reset_515676(void) {
 volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 context[445u]=context[144u]&1u;
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 *(volatile uint32_t *)(context+144u)=*(volatile uint32_t *)(context+144u)&~1u;
 audio_uart_nema_matrix_identity_561810((void *)(context+164u));
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 audio_uart_nema_matrix_identity_561810((void *)(context+200u));
}

#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void *audio_uart_display_surface_alloc(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char stencil263_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char stencil263_message[]="Failed to create stencil buffer!";
static const char stencil263_function[]="lv_draw_ambiq_stencil_buffer_adjust";
/* Native4b0b5a..4b0bea: cached unit, fresh framebuffer loads after children. */
uint32_t audio_uart_ambiq_stencil_adjust_4b0b5a(void *cell,uint32_t width,uint32_t height) {
 volatile uint32_t *unit=cell;
 if(!unit)unit=audio_uart_ambiq_default_unit_4c791a();
 void *buffer=(void *)(uintptr_t)unit[16];
 if(buffer) {
  const volatile uint32_t *header=buffer;
  if((uint32_t)(uint16_t)header[1]==width && (header[1]>>16u)==height)return 1u;
 }
 if(!buffer)unit[16]=(uint32_t)(uintptr_t)audio_uart_display_surface_alloc(width,height,14u,0u);
 else {
  void *reshaped=audio_uart_lv_draw_buf_reshape_48b196(buffer,14u,width,height,0u);
  if(!reshaped) {
   audio_uart_font_bitmap_release((void *)(uintptr_t)unit[16]);
   unit[16]=(uint32_t)(uintptr_t)audio_uart_display_surface_alloc(width,height,14u,0u);
  } else unit[16]=(uint32_t)(uintptr_t)reshaped;
 }
 if(unit[16]!=0u)return 1u;
 audio_uart_lvgl_log(3u,stencil263_file,482u,stencil263_function,stencil263_message);
 return 0u;
}

#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void audio_uart_nema_vg_path_reset_514e50(void *);
extern void audio_uart_nema_vg_paint_reset_515048(void *);
extern void audio_uart_nema_vg_state_reset_515676(void);
extern void audio_uart_ambiq_blend_clear_4b075e(void *);
extern uint32_t audio_uart_ambiq_stencil_adjust_4b0b5a(void *,uint32_t,uint32_t);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
typedef struct {uint32_t words[4];} audio_uart_vg_framebuffer_264;
extern void audio_uart_nema_vg_set_framebuffer_5223a2(uint32_t,uint32_t,audio_uart_vg_framebuffer_264);
static const char resolution264_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char resolution264_message[]="Failed to adjust stencil buffer!";
static const char resolution264_function[]="lv_draw_ambiq_vg_start";
/* Native4b0bea..4b0c8a: cached unit, wrapped alignment and by-value descriptor. */
void audio_uart_ambiq_set_resolution_4b0bea(uint32_t width,uint32_t height) {
 volatile uint32_t *unit=audio_uart_ambiq_default_unit_4c791a();
 audio_uart_nema_vg_path_reset_514e50((void *)(uintptr_t)unit[17]);
 audio_uart_nema_vg_paint_reset_515048((void *)(uintptr_t)unit[18]);
 audio_uart_nema_vg_state_reset_515676();
 audio_uart_ambiq_blend_clear_4b075e((void *)unit);
 width=(width+3u)&~3u;height=(height+3u)&~3u;
 uint32_t status=audio_uart_ambiq_stencil_adjust_4b0b5a((void *)unit,width,height);
 if((uint8_t)status!=1u) {
  audio_uart_lvgl_log(3u,resolution264_file,509u,resolution264_function,resolution264_message);
  return;
 }
 audio_uart_vg_framebuffer_264 framebuffer;
 audio_uart_lv_memzero_48949c(&framebuffer,16u);
 framebuffer.words[0]=((volatile uint32_t *)(uintptr_t)unit[16])[3];
 framebuffer.words[2]=((volatile uint32_t *)(uintptr_t)unit[16])[4];
 framebuffer.words[3]=((volatile uint32_t *)(uintptr_t)unit[16])[4];
 audio_uart_nema_vg_set_framebuffer_5223a2(width,height,framebuffer);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_descriptor_200732e8[];
/* Native5155e4..51562e: ordered descriptor writes and signed-to-float dimensions. */
void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t width,uint32_t height,audio_uart_vg_framebuffer_264 framebuffer) {
 volatile uint32_t *d=audio_uart_nema_vg_framebuffer_descriptor_200732e8;
 volatile float *f=(volatile float *)(void *)d;
 d[4]=width;
 float w=(float)(int32_t)width;f[9]=w;f[11]=w;
 float h=(float)(int32_t)height;
 d[0]=framebuffer.words[0];d[1]=framebuffer.words[1];d[2]=framebuffer.words[2];d[3]=framebuffer.words[3];
 d[5]=height;d[7]=0;d[8]=0;d[10]=0;f[12]=h;d[13]=0;f[14]=h;
}
/* Native51562e..515634: address only; no storage initializer inferred. */
void *audio_uart_nema_vg_framebuffer_get_51562e(void) {return (void *)audio_uart_nema_vg_framebuffer_descriptor_200732e8;}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_context_cell_20074f08;
extern void audio_uart_nema_vg_framebuffer_destroy_5155dc(void);
extern void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t,uint32_t,audio_uart_vg_framebuffer_264);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
/* Native5223a2..5223fa: conditional cleanup, by-value store, fresh context reload. */
void audio_uart_nema_vg_set_framebuffer_5223a2(uint32_t width,uint32_t height,audio_uart_vg_framebuffer_264 framebuffer) {
 const volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
 if(context[24u]&1u)audio_uart_nema_vg_framebuffer_destroy_5155dc();
 audio_uart_nema_vg_framebuffer_store_5155e4(width,height,framebuffer);
 context=(void *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
 if((context[16u]&3u)!=0u || (context[20u]&3u)!=0u)audio_uart_nema_vg_set_error_51565c(0x2000000u);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_descriptor_200732e8[];
extern void audio_uart_nema_cl_buffer_destroy_5140c6(void *);
/* Native5155dc..5155e4: fixed framebuffer descriptor uses real destroy contract. */
void audio_uart_nema_vg_framebuffer_destroy_5155dc(void) {
 audio_uart_nema_cl_buffer_destroy_5140c6((void *)audio_uart_nema_vg_framebuffer_descriptor_200732e8);
}

#include <stdint.h>
extern void *audio_uart_font_outline_context(void);
extern void audio_uart_ambiq_vector_font_push_53d8fc(void *);
extern void audio_uart_ambiq_vector_font_allocate_53da54(void *);
extern void audio_uart_ambiq_vector_font_release_53db3c(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char vector270_message[]="unknown event code: %d";
static const char vector270_function[]="lv_draw_ambiq_vector_font_ft_cb";
static const char vector270_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
/* Native53d82c..53d87c: event-code accessor masks bit15; event parameter always loaded. */
void audio_uart_ambiq_vector_font_callback_53d82c(void *event) {
 const volatile uint32_t *e=event;
 uint32_t code=e[2]&~32768u;
 void *data=(void *)(uintptr_t)e[4];
 if(code==36u)audio_uart_ambiq_vector_font_push_53d8fc(data);
 else if(code==40u)audio_uart_ambiq_vector_font_allocate_53da54(data);
 else if(code==41u)audio_uart_ambiq_vector_font_release_53db3c((void *)(uintptr_t)*(volatile uint32_t *)data);
 else audio_uart_lvgl_log(2u,vector270_file,186u,vector270_function,vector270_message,code);
}
/* Native529bf2..529bfe: only callback is stored; two incoming args are unused. */
void audio_uart_font_outline_register_529bf2(uintptr_t callback,uint32_t unused,void *unit) {
 (void)unused;(void)unit;
 volatile uint32_t *context=audio_uart_font_outline_context();
 context[4]=(uint32_t)callback;
}
/* Native53d6da..53d6ea: registers the source callback with the original arguments. */
void audio_uart_ambiq_vector_font_init_53d6da(void *unit) {
 audio_uart_font_outline_register_529bf2((uintptr_t)audio_uart_ambiq_vector_font_callback_53d82c,0u,unit);
}

#include <stdint.h>
extern void audio_uart_ambiq_get_path_buffers_5fa21c(void *,uint32_t *,uint32_t *,void **,void **);
extern void audio_uart_nema_vg_path_destroy_514d98(void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char release272_null[]="NULL pointer";
static const char release272_expression[]="outline != NULL";
static const char release272_message[]="Asserted at expression: %s (%s)";
static const char release272_function[]="lv_ambiq_ft_outline_destroy";
static const char release272_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
/* Native53db3c..53dbd8: fresh glyph loads bracket buffer and path release calls. */
void audio_uart_ambiq_vector_font_release_53db3c(void *cell) {
 volatile uint32_t *glyph=cell;
 if(!glyph) {
  audio_uart_lvgl_log(3u,release272_file,312u,release272_function,release272_message,release272_expression,release272_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t segment_size,data_size;void *segments,*data;
 if(glyph[0]!=0u) {
  audio_uart_ambiq_get_path_buffers_5fa21c((void *)(uintptr_t)glyph[0],&segment_size,&data_size,&segments,&data);
  audio_uart_lv_heap_free(data);audio_uart_lv_heap_free(segments);
 }
 if(glyph[1]!=0u) {
  audio_uart_ambiq_get_path_buffers_5fa21c((void *)(uintptr_t)glyph[1],&segment_size,&data_size,&segments,&data);
  audio_uart_lv_heap_free(data);audio_uart_lv_heap_free(segments);
 }
 if(glyph[0]!=0u) {
  audio_uart_nema_vg_path_destroy_514d98((void *)(uintptr_t)glyph[0]);glyph[0]=0u;
 }
 if(glyph[1]!=0u) {
  audio_uart_nema_vg_path_destroy_514d98((void *)(uintptr_t)glyph[1]);glyph[1]=0u;
 }
 audio_uart_lv_heap_free((void *)glyph);
}

#include <stdint.h>
/* Native5fa21c..5fa236: sequential volatile accesses preserve output/path aliases. */
void audio_uart_ambiq_get_path_buffers_5fa21c(void *path,uint32_t *segment_size,uint32_t *data_size,void **segments,void **data) {
 const volatile uint32_t *p=path;
 *(volatile uint32_t *)segment_size=p[0];
 *(volatile uint32_t *)data_size=p[1];
 *(volatile uint32_t *)(void *)segments=p[2];
 *(volatile uint32_t *)(void *)data=p[3];
}

#include <stdint.h>
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
/* Native514d98..514e0a: reset then release; NULL error bypasses both. */
void audio_uart_nema_vg_path_destroy_514d98(void *cell) {
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)((uint32_t)(uintptr_t)cell+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
 audio_uart_nema_cl_node_release_514178(cell);
}

#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void audio_uart_lv_array_clear_488478(void *);
extern void audio_uart_lv_array_init_external_488440(void *,void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern volatile uint32_t audio_uart_ambiq_vector_current_path_200746c4;
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
extern uint8_t audio_uart_ambiq_vector_path_segments_20073cc0[];
static const char alloc277_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char alloc277_function[]="lv_ambiq_ft_outline_alloc";
static const char alloc277_format[]="Asserted at expression: %s (%s)";
static const char alloc277_memory[]="Out of memory";
static const char alloc277_outline[]="outline != NULL";
static const char alloc277_data[]="data != NULL";
static const char alloc277_segments[]="seg != NULL";
static void alloc277_fail(uint32_t line,const char *expression) {
 audio_uart_lvgl_log(3u,alloc277_file,line,alloc277_function,alloc277_format,expression,alloc277_memory);
 for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native53da54..53db3c: allocator failure is native diagnostic/fail-stop. */
void audio_uart_ambiq_vector_font_allocate_53da54(void *parameter) {
 volatile uint32_t *p=parameter;
 if(p[0]==0u) {
  volatile uint32_t *outline=audio_uart_lv_malloc(8u);
  if(!outline)alloc277_fail(281u,alloc277_outline);
  outline[0]=(uint32_t)(uintptr_t)audio_uart_nema_vg_path_create_514ebc();outline[1]=0u;
  p[0]=(uint32_t)(uintptr_t)outline;
  audio_uart_ambiq_vector_current_path_200746c4=outline[0];
 }
 audio_uart_lv_array_clear_488478(audio_uart_ambiq_vector_path_data_20073cd4);
 audio_uart_lv_array_clear_488478(audio_uart_ambiq_vector_path_segments_20073cc0);
 uint32_t data_size=p[9];uint32_t segment_size=p[8]+1u;
 void *data=audio_uart_lv_malloc(data_size<<2);
 if(!data)alloc277_fail(297u,alloc277_data);
 void *segments=audio_uart_lv_malloc(segment_size);
 if(!segments)alloc277_fail(299u,alloc277_segments);
 audio_uart_lv_array_init_external_488440(audio_uart_ambiq_vector_path_data_20073cd4,data,data_size,4u);
 audio_uart_lv_array_init_external_488440(audio_uart_ambiq_vector_path_segments_20073cc0,segments,segment_size,1u);
}

#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char array278_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char array278_function[]="lv_array_init_from_buf";
static const char array278_format[]="Asserted at expression: %s (%s)";
static const char array278_expression[]="buf != NULL";
static const char array278_null[]="NULL pointer";
/* Native488440..488478: external buffer initialization with ordered sparse stores. */
void audio_uart_lv_array_init_external_488440(void *array,void *buffer,uint32_t count,uint32_t stride) {
 if(!buffer) {
  audio_uart_lvgl_log(3u,array278_file,51u,array278_function,array278_format,array278_expression,array278_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 volatile uint32_t *a=array;
 a[1]=0u;a[2]=count;a[3]=stride;a[0]=(uint32_t)(uintptr_t)buffer;
 ((volatile uint8_t *)array)[16]=0u;
}

#include <stdint.h>
extern uint32_t audio_uart_lv_array_push_488506(void *,const void *);
extern void audio_uart_ambiq_vector_data_pair_53d87c(uint32_t,uint32_t);
extern void *audio_uart_ambiq_vector_array_front_53d6d0(void *);
extern uint32_t audio_uart_ambiq_vector_array_count_53d6cc(void *);
extern void audio_uart_nema_vg_path_shape_514f3c(void *,uint32_t,void *,uint32_t,void *);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern volatile uint32_t audio_uart_ambiq_vector_current_path_200746c4;
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
extern uint8_t audio_uart_ambiq_vector_path_segments_20073cc0[];
static const char push281_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char push281_function[]="lv_ambiq_ft_outline_push";
static const char push281_null[]="NULL pointer";
static const char push281_outline[]="outline != NULL";
static const char push281_assertfull[]="Asserted at expression: %s (%s)";
static const char push281_result[]="res == LV_RESULT_OK";
static const char push281_assert[]="Asserted at expression: %s";
static const char push281_unknown[]="unknown point type: %d";
/* Native53d8fc..53da50: command mapping and post-child segment reloads. */
void audio_uart_ambiq_vector_font_push_53d8fc(void *parameter) {
 volatile uint32_t *p=parameter;
 volatile uint32_t *outline=(void *)(uintptr_t)p[0];
 if(!outline) {
  audio_uart_lvgl_log(3u,push281_file,209u,push281_function,push281_assertfull,push281_outline,push281_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 volatile uint8_t segment=0u;
 uint32_t type=((volatile uint8_t *)parameter)[4];
 switch(type) {
 case 0:segment=0;break;case 1:segment=1;break;case 2:segment=2;break;
 case 3:segment=6;break;case 4:segment=5;break;case 5:segment=0;break;
 default:audio_uart_lvgl_log(3u,push281_file,235u,push281_function,push281_unknown,type);break;
 }
 uint32_t result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_segments_20073cc0,(const void *)&segment);
 if((uint8_t)result!=1u) {
  audio_uart_lvgl_log(3u,push281_file,240u,push281_function,push281_assert,push281_result);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 if(segment==6u || segment==5u) {
  uint32_t y=p[5];uint32_t x=p[4];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(segment==6u) {
  uint32_t y=p[7];uint32_t x=p[6];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(segment!=0u) {
  uint32_t y=p[3];uint32_t x=p[2];audio_uart_ambiq_vector_data_pair_53d87c(x,y);
 }
 if(type==0u || type==5u) {
  void *data=audio_uart_ambiq_vector_array_front_53d6d0(audio_uart_ambiq_vector_path_data_20073cd4);
  uint32_t data_count=audio_uart_ambiq_vector_array_count_53d6cc(audio_uart_ambiq_vector_path_data_20073cd4);
  void *segments=audio_uart_ambiq_vector_array_front_53d6d0(audio_uart_ambiq_vector_path_segments_20073cc0);
  uint32_t segment_count=audio_uart_ambiq_vector_array_count_53d6cc(audio_uart_ambiq_vector_path_segments_20073cc0);
  audio_uart_nema_vg_path_shape_514f3c((void *)(uintptr_t)audio_uart_ambiq_vector_current_path_200746c4,segment_count,segments,data_count,data);
 }
 if(type==5u) {
  outline[1]=(uint32_t)(uintptr_t)audio_uart_nema_vg_path_create_514ebc();
  audio_uart_ambiq_vector_current_path_200746c4=outline[1];
 }
}

#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char access282_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char access282_function[]="lv_array_at";
static const char access282_format[]="Asserted at expression: %s (%s)";
static const char access282_expression[]="array->data != NULL";
static const char access282_null[]="NULL pointer";
/* Native488578..4885b8: count gate precedes data assertion and fresh pointer reload. */
void *audio_uart_lv_array_item_488578(void *array,uint32_t index) {
 const volatile uint32_t *a=array;
 if(index>=a[1])return 0;
 if(a[0]==0u) {
  audio_uart_lvgl_log(3u,access282_file,202u,access282_function,access282_format,access282_expression,access282_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t data=a[0];uint32_t stride=a[3];
 return (void *)(uintptr_t)(data+index*stride);
}
/* Native53d6cc..53d6d0: count only. */
uint32_t audio_uart_ambiq_vector_array_count_53d6cc(void *array) {
 return ((const volatile uint32_t *)array)[1];
}
/* Native53d6d0..53d6da: actual indexed-item contract at zero. */
void *audio_uart_ambiq_vector_array_front_53d6d0(void *array) {
 return audio_uart_lv_array_item_488578(array,0u);
}

#include <stdint.h>
extern uint32_t audio_uart_lv_array_resize_48849c(void *,uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char append284_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char append284_function[]="lv_array_push_back";
static const char append284_format[]="Asserted at expression: %s (%s)";
static const char append284_expression[]="array->data != NULL";
static const char append284_null[]="NULL pointer";
/* Native4883f0..4883fc: consumed void zero-fill wrapper. */
void audio_uart_lv_array_zero_4883f0(void *destination,uint32_t size) {
 audio_uart_lv_basic_box_clear_454746(destination,0u,size);
}
/* Native488506..488578: equality gate, full result, fresh descriptor loads. */
uint32_t audio_uart_lv_array_push_488506(void *array,const void *source) {
 volatile uint32_t *a=array;
 if(a[0]==0u) {
  audio_uart_lvgl_log(3u,append284_file,176u,append284_function,append284_format,append284_expression,append284_null);
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 uint32_t count=a[1];uint32_t capacity=a[2];
 if(count==capacity) {
  uint32_t wanted=a[2]+4u;
  if(audio_uart_lv_array_resize_48849c(array,wanted)==0u)return 0u;
 }
 uint32_t data=a[0];count=a[1];uint32_t stride=a[3];
 void *destination=(void *)(uintptr_t)(data+count*stride);
 if(source)(void)audio_uart_lv_grid_copy_454738(destination,source,a[3]);
 else audio_uart_lv_array_zero_4883f0(destination,a[3]);
 a[1]=a[1]+1u;
 return 1u;
}

#include <stdint.h>
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_vg_path_process_561c68(void *);
/* Native514f3c..514f60: ordered shape stores precede genuine postprocessor. */
void audio_uart_nema_vg_path_shape_514f3c(void *path,uint32_t segment_count,void *segments,uint32_t data_count,void *data) {
 if(!path){audio_uart_nema_vg_set_error_51565c(1u);return;}
 volatile uint32_t *p=path;
 p[2]=(uint32_t)(uintptr_t)segments;p[3]=(uint32_t)(uintptr_t)data;
 p[0]=segment_count;p[1]=data_count;
 audio_uart_nema_vg_path_process_561c68(path);
}

#include <stdint.h>
extern uint32_t audio_uart_lv_array_push_488506(void *,const void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern uint8_t audio_uart_ambiq_vector_path_data_20073cd4[];
static const char pair288_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_vector_font.c";
static const char pair288_function[]="lv_ambiq_ft_data_array_push";
static const char pair288_format[]="Asserted at expression: %s";
static const char pair288_expression[]="res == LV_RESULT_OK";
static void pair288_fail(uint32_t line) {
 audio_uart_lvgl_log(3u,pair288_file,line,pair288_function,pair288_format,pair288_expression);
 for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
/* Native53d87c..53d8fc: both float conversions precede the first append. */
void audio_uart_ambiq_vector_data_pair_53d87c(uint32_t x,uint32_t y) {
 volatile float x_float=(float)(int32_t)x;
 volatile float y_float=(float)(int32_t)y;
 uint32_t result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_data_20073cd4,(const void *)&x_float);
 if((uint8_t)result!=1u)pair288_fail(199u);
 result=audio_uart_lv_array_push_488506(audio_uart_ambiq_vector_path_data_20073cd4,(const void *)&y_float);
 if((uint8_t)result!=1u)pair288_fail(202u);
}

#include <stdint.h>
/* Native514e0c..514e50: sparse path bounds reset, no NULL guard in native. */
void audio_uart_nema_vg_path_bounds_reset_514e0c(void *path) {
 volatile uint32_t *p=path;
 p[4]=0x477fff00u;p[5]=0x477fff00u;p[6]=0xc77fff00u;p[7]=0xc77fff00u;
 p[20]=0u;p[21]=0u;p[9]=0u;p[8]=0u;p[11]=0u;p[10]=0u;
 p[13]=0u;p[12]=0u;p[15]=0u;p[14]=0u;p[22]=0u;p[23]=0u;
 p[16]=0x477fff00u;p[17]=0x477fff00u;p[18]=0xc77fff00u;p[19]=0xc77fff00u;
}

#include <stdint.h>
/* Native math interface consumes angle inS0 and mode inR0; explicit VFP PCS. */
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_core_5094c0(uint32_t,float);
/* Native50968c..509690. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float angle) {
 return audio_uart_float_trig_core_5094c0(1u,angle);
}
/* Native509690..509694. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode0_509690(float angle) {
 return audio_uart_float_trig_core_5094c0(0u,angle);
}

#include <stdint.h>
extern volatile uint32_t audio_uart_float_math_error_cell_20074f14;
/* Native439ca4..439cb2 andshared439cbe..439cc4: consumed void domain store. */
__attribute__((used,noinline)) static void sqrt295_domain_store(void) {
 audio_uart_float_math_error_cell_20074f14=33u;
}
/* Native handler preservesR0..R3; named architectural wrapper keeps that contract. */
__attribute__((naked)) void audio_uart_float_domain_error_439ca4(void) {
 __asm__ volatile("push {r0,r1,r2,r3,lr}\n\tsub sp, #4\n\tbl sqrt295_domain_store\n\tadd sp, #4\n\tpop {r0,r1,r2,r3,pc}");
}
/* Native4397a8..4397c4: explicit architectural FPU instructions, no opcode data. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_sqrt_4397a8(float value) {
 uint32_t status;
 __asm__ volatile("vcmpe.f32 %1, #0.0\n\tvmrs %0, fpscr" : "=r"(status) : "t"(value));
 if(status&0x80000000u) {
  union {uint32_t bits;float value;} result={.bits=0x7fffffffu};
  audio_uart_float_domain_error_439ca4();
  return result.value;
 }
 float result;
 __asm__ volatile("vsqrt.f32 %0, %1" : "=t"(result) : "t"(value));
 return result;
}

#include <stdint.h>
extern void audio_uart_float_domain_error_439ca4(void);
static uint32_t remainder296_lsr(uint32_t value,uint32_t amount) {
 amount&=255u;return amount>=32u?0u:value>>amount;
}
/* Native577c4c..577d08: integer float-bit remainder, native exceptional policy. */
uint32_t audio_uart_float_remainder_bits_577c4c(uint32_t x,uint32_t y) {
 uint32_t sign=x&0x80000000u, twice_y=y<<1;
 int32_t ex=(int32_t)((x>>23)&255u),ey=(int32_t)(twice_y>>24);
 uint32_t mx,my;
 if(ey!=0 && ex!=255 && ey!=255) {
  if(twice_y>=(x<<1))return twice_y==(x<<1)?sign:x;
  my=(0x80000000u|(twice_y<<7))>>8;
  mx=0x80000000u|(x<<8);
 } else if(twice_y!=0u && ex!=255 && ey!=255) {
  if(twice_y>=(x<<1))return twice_y==(x<<1)?sign:x;
  my=twice_y<<8;
  uint32_t leading=(uint32_t)__builtin_clz(my);
  my<<=leading;ey=-(int32_t)leading;my>>=8;
  if(ex!=0)mx=0x80000000u|(x<<8);
  else {
   mx=x<<9;leading=(uint32_t)__builtin_clz(mx);
   mx<<=leading;ex=-(int32_t)leading;
  }
 } else {
  uint32_t result=x;
  uint32_t carry=((uint64_t)(x<<1)+0x1000000u)>>32;
  if(carry)result=0x7fffffffu;
  else {
   uint32_t sum=twice_y+0x1000000u;
   carry=((uint64_t)twice_y+0x1000000u)>>32;
   if(sum!=0u)result=0x7fffffffu;
  }
  if(!carry)audio_uart_float_domain_error_439ca4();
  return result;
 }
 int32_t difference=ex-ey-8;
 while(difference>0) {
  mx=(mx%my)<<8;
  if(mx==0u)return sign;
  difference-=8;
 }
 mx=remainder296_lsr(mx,(uint32_t)(-difference));
 mx%=my;
 if(mx==0u)return sign;
 uint32_t leading=(uint32_t)__builtin_clz(mx);
 mx<<=leading;int32_t exponent=ey+7-(int32_t)leading;
 if(exponent>=0)return (sign|(mx>>8))+((uint32_t)exponent<<23);
 return sign|remainder296_lsr(mx,(uint32_t)(8-exponent));
}
/* Native577c3c..577c4c: S0/S1 inputs toR0/R1 bit core, R0result backtoS0. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_remainder_577c3c(float x,float y) {
 union {float value;uint32_t bits;} a={.value=x},b={.value=y},result;
 result.bits=audio_uart_float_remainder_bits_577c4c(a.bits,b.bits);
 return result.value;
}

#include <stdint.h>
static float trig298_float(uint32_t bits) {union {uint32_t bits;float value;} v={.bits=bits};return v.value;}
static uint32_t trig298_bits(float value) {union {uint32_t bits;float value;} v={.value=value};return v.bits;}
static float trig298_mul(float a,float b) {float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float trig298_add(float a,float b) {float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float trig298_mla(float a,float b,float c) {__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float trig298_neg(float a) {float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static uint32_t trig298_compare(float a,float b) {uint32_t flags;__asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr":"=r"(flags):"t"(a),"t"(b));return flags;}
static uint32_t trig298_integer(float a) {float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(a));return trig298_bits(v);}
static float trig298_fixed14(uint32_t bits) {float a=trig298_float(bits),v;__asm__ volatile("vcvt.f32.s32 %0,%1,#14":"=t"(v):"t"(a));return v;}
/* Native5094c0..50964c plusauthenticatedordinaryconstantpool50964c..50968c.
 * Named architectural float operations preserve native rounding/NaN/flags order. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_core_5094c0(uint32_t mode,float angle) {
 float scaled=trig298_mul(angle,trig298_float(0x3f22f983u));
 uint32_t scaled_bits=trig298_bits(scaled),quadrant;
 float absolute=trig298_float(scaled_bits&0x7fffffffu);
 if(trig298_compare(absolute,trig298_float(0x4f000000u))&0x80000000u) {
  float half=trig298_float((scaled_bits&0x80000000u)|0x3f000000u);
  scaled=trig298_add(half,scaled);quadrant=trig298_integer(scaled);
  if(quadrant!=0u) {
   float fixed=trig298_fixed14(quadrant);
   angle=trig298_mla(angle,fixed,trig298_float(0xc6c90000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc0fda000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xbaa22000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xb3340000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xaec23000u));
  }
 } else {
  uint32_t bits=trig298_bits(angle);
  if(((bits>>23)&255u)==255u) {
   if((bits&0x7fffffu)!=0u)return angle;
   return trig298_float(0x7fffffffu);
  }
  if((bits<<1)==0u)return mode==0u?angle:trig298_float(0x3f800000u);
  scaled=trig298_add(trig298_float((scaled_bits&0x80000000u)|0x3f000000u),scaled);
  scaled_bits=trig298_bits(scaled);
  if((scaled_bits<<1)!=0u) {
   int32_t shift=150-(int32_t)((scaled_bits>>23)&255u);
   if(shift>=24)scaled_bits&=0x80000000u;
   else if(shift>0)scaled_bits=(scaled_bits>>(uint32_t)shift)<<(uint32_t)shift;
   scaled=trig298_float(scaled_bits);
  }
  if((trig298_bits(scaled)<<1)!=0u) {
   float fixed=trig298_mul(scaled,trig298_float(0x38800000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc6c90000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc0fda000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xbaa22000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xb3340000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xaec23000u));
  }
  quadrant=trig298_integer(scaled);
 }
 mode+=(quadrant&3u);
 if(trig298_compare(trig298_float(trig298_bits(angle)&0x7fffffffu),trig298_float(0x39800000u))&0x80000000u) {
  if(mode&1u)angle=trig298_float(0x3f800000u);
 } else {
  float square=trig298_mul(angle,angle);
  if(mode&1u) {
   float v=trig298_mla(trig298_float(0x3d2aa036u),square,trig298_float(0xbab24993u));
   v=trig298_mla(trig298_float(0xbeffffdfu),v,square);
   angle=trig298_mla(trig298_float(0x3f800000u),v,square);
  } else {
   float v=trig298_mla(trig298_float(0x3c088342u),square,trig298_float(0xb94c8c6eu));
   float product=trig298_mul(angle,square);
   v=trig298_mla(trig298_float(0xbe2aaaa1u),v,square);
   angle=trig298_mla(angle,product,v);
  }
 }
 if(mode&2u)angle=trig298_neg(angle);
 return angle;
}

#include <stdint.h>
extern void audio_uart_float_domain_error_439ca4(void);
static float inv300_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t inv300_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static float inv300_add(float a,float b){float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_sub(float a,float b){float v;__asm__ volatile("vsub.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_mul(float a,float b){float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_mla(float a,float b,float c){__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float inv300_neg(float a){float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static float inv300_sqrt(float a){float v;__asm__ volatile("vsqrt.f32 %0,%1":"=t"(v):"t"(a));return v;}
static const uint32_t inv300_angles[8]={0x0u,0x3f060a92u,0x3fc90fdbu,0x3f860a92u,0x3fc90fdbu,0x40060a92u,0x40490fdbu,0x40278d36u};
/* Native55e99c..55ea06 plusordinarycoefficient/anglepool55ea08..55ea40.
 * Native callers' consumed mode domain0..15; larger table indices unqualified. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_core_55e99c(uint32_t mode,float x) {
 uint32_t bits=inv300_bits(x);
 if((int32_t)bits>=(int32_t)0x3e8930a4u) {
  float numerator=inv300_mla(inv300_float(0xbf800000u),inv300_float(0x3fddb3d7u),x);
  float denominator=inv300_add(inv300_float(0x3fddb3d7u),x);
  x=inv300_div(numerator,denominator);mode|=2u;bits=inv300_bits(x);
 }
 if((bits<<1)>=0x73000000u) {
  float square=inv300_mul(x,x);
  float cube=inv300_mul(x,square);
  x=inv300_mla(x,cube,inv300_float(0x3f03d56au));
  float denominator=inv300_mla(inv300_float(0x3f592ab8u),inv300_float(0x3da9942bu),square);
  denominator=inv300_mla(inv300_float(0x3f800000u),denominator,square);
  x=inv300_div(x,denominator);
 }
 uint32_t index=mode>>1;
 if(index&2u)x=inv300_neg(x);
 x=inv300_add(x,inv300_float(inv300_angles[index]));
 if(mode&1u)x=inv300_neg(x);
 return x;
}
/* Native58ec74..58ecb8 withliteral58ecb8: unary inverse-ratio entry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_ratio_58ec74(float x) {
 uint32_t bits=inv300_bits(x),exponent=(bits>>23)&255u;
 if(exponent==0u)return x;
 if(exponent>=153u) {
  if(exponent==255u && (bits&0x7fffffu)!=0u)return x;
  return inv300_float(0x3fc90fdbu|(bits&0x80000000u));
 }
 uint32_t mode=bits>>31;bits&=0x7fffffffu;x=inv300_float(bits);
 if(bits>0x3f800000u){x=inv300_div(inv300_float(0x3f800000u),x);mode+=4u;}
 return audio_uart_float_inverse_core_55e99c(mode,x);
}
/* Native58ecbc..58ed1a withliteral58ed1c: unary inverse-magnitude entry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_magnitude_58ecbc(float x) {
 uint32_t original=inv300_bits(x),mode=((original>>31)!=0u && (original<<1)!=0u)?8u:4u;
 uint32_t bits=original&0x7fffffffu;x=inv300_float(bits);
 if(bits>0x3f800000u) {
  if(bits<=0x7f800000u){audio_uart_float_domain_error_439ca4();return inv300_float(0x7fffffffu);}
  return x;
 }
 float one=inv300_float(0x3f800000u);
 float difference=inv300_sub(one,x);
 float sum=inv300_add(one,x);
 float root=inv300_sqrt(inv300_mul(sum,difference));
 if(bits>0x3f3504f4u){mode^=4u;x=inv300_div(root,x);}
 else x=inv300_div(x,root);
 return audio_uart_float_inverse_core_55e99c(mode,x);
}

#include <stdint.h>
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_core_55e99c(uint32_t,float);
extern void audio_uart_float_domain_error_439ca4(void);
static float angle302_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t angle302_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static float angle302_abs(float a){float v;__asm__ volatile("vabs.f32 %0,%1":"=t"(v):"t"(a));return v;}
static float angle302_add(float a,float b){float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_sub(float a,float b){float v;__asm__ volatile("vsub.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_mul(float a,float b){float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_sqrt(float a){float v;__asm__ volatile("vsqrt.f32 %0,%1":"=t"(v):"t"(a));return v;}
/* Native50969c..509706: mode/sign gates before magnitude ratio andspecialvalues. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_two_input_angle_50969c(float y,float x) {
 uint32_t original_y=angle302_bits(y),original_x=angle302_bits(x);
 y=angle302_abs(y);
 uint32_t mode=original_y>>31;
 uint32_t twice_y=original_y<<1,twice_x=original_x<<1;
 x=angle302_abs(x);
 if(original_x>>31)mode+=12u;
 uint32_t abs_y=original_y&0x7fffffffu,abs_x=original_x&0x7fffffffu;
 if(abs_y<0x7f800000u && abs_x<0x7f800000u) {
  uint32_t reciprocal=twice_x<twice_y;
  if(reciprocal)mode^=4u;
  if(twice_x==0u)return audio_uart_float_inverse_core_55e99c(mode,angle302_float(0u));
  float ratio=reciprocal?angle302_div(x,y):angle302_div(y,x);
  return audio_uart_float_inverse_core_55e99c(mode,ratio);
 }
 if(abs_y==0x7f800000u)mode^=4u;
 if(abs_y>0x7f800000u || abs_x>0x7f800000u)return angle302_float(0x7fffffffu);
 return audio_uart_float_inverse_core_55e99c(mode,angle302_float(twice_x==twice_y?0x3f800000u:0u));
}
/* Native509708..509760 withordinarythreshold509760: signedunaryentry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_signed_509708(float x) {
 uint32_t original=angle302_bits(x),mode=original>>31,bits=original&0x7fffffffu;
 if(bits==0u)return x;
 x=angle302_float(bits);
 if(bits>0x3f800000u) {
  if(bits<=0x7f800000u){audio_uart_float_domain_error_439ca4();return angle302_float(0x7fffffffu);}
  return x;
 }
 float one=angle302_float(0x3f800000u);
 float difference=angle302_sub(one,x),sum=angle302_add(one,x);
 float root=angle302_sqrt(angle302_mul(sum,difference));
 if(bits>0x3f3504f4u){mode^=4u;x=angle302_div(root,x);}
 else x=angle302_div(x,root);
 return audio_uart_float_inverse_core_55e99c(mode,x);
}

#include <stdint.h>
static float tan304_float(uint32_t bits) {union {uint32_t bits;float value;} v={.bits=bits};return v.value;}
static uint32_t tan304_bits(float value) {union {uint32_t bits;float value;} v={.value=value};return v.bits;}
static float tan304_mul(float a,float b) {float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float tan304_add(float a,float b) {float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float tan304_mla(float a,float b,float c) {__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float tan304_neg(float a) {float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static uint32_t tan304_compare(float a,float b) {uint32_t flags;__asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr":"=r"(flags):"t"(a),"t"(b));return flags;}
static uint32_t tan304_integer(float a) {float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(a));return tan304_bits(v);}
static float tan304_fixed14(uint32_t bits) {float a=tan304_float(bits),v;__asm__ volatile("vcvt.f32.s32 %0,%1,#14":"=t"(v):"t"(a));return v;}
static float tan304_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
/* Native563f40..5640ae plusordinaryliteralpool5640b0..5640e4. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_tangent_563f40(float angle) {
 float scaled=tan304_mul(angle,tan304_float(0x3f22f983u));
 uint32_t scaled_bits=tan304_bits(scaled),quadrant;
 float absolute=tan304_float(scaled_bits&0x7fffffffu);
 if(tan304_compare(absolute,tan304_float(0x4f000000u))&0x80000000u) {
  float half=tan304_float((scaled_bits&0x80000000u)|0x3f000000u);
  scaled=tan304_add(half,scaled);quadrant=tan304_integer(scaled);
  if(quadrant!=0u) {
   float fixed=tan304_fixed14(quadrant);
   angle=tan304_mla(angle,fixed,tan304_float(0xc6c90000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc0fda000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xbaa22000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xb3340000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xaec23000u));
  }
 } else {
  uint32_t bits=tan304_bits(angle);
  if(((bits>>23)&255u)==255u) {
   if((bits&0x7fffffu)!=0u)return angle;
   return tan304_float(0x7fffffffu);
  }
  if((bits<<1)==0u)return angle;
  scaled=tan304_add(tan304_float((scaled_bits&0x80000000u)|0x3f000000u),scaled);
  scaled_bits=tan304_bits(scaled);
  if((scaled_bits<<1)!=0u) {
   int32_t shift=150-(int32_t)((scaled_bits>>23)&255u);
   if(shift>=24)scaled_bits&=0x80000000u;
   else if(shift>0)scaled_bits=(scaled_bits>>(uint32_t)shift)<<(uint32_t)shift;
   scaled=tan304_float(scaled_bits);
  }
  if((tan304_bits(scaled)<<1)!=0u) {
   float fixed=tan304_mul(scaled,tan304_float(0x38800000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc6c90000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc0fda000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xbaa22000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xb3340000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xaec23000u));
  }
  quadrant=tan304_integer(scaled);
 }
 if(tan304_compare(tan304_float(tan304_bits(angle)&0x7fffffffu),tan304_float(0x39800000u))&0x80000000u) {
  if(quadrant&1u)return tan304_div(tan304_float(0xbf800000u),angle);
  return angle;
 }
 float square=tan304_mul(angle,angle);
 float denominator=tan304_mla(tan304_float(0xbedbb51eu),square,tan304_float(0x3c1f166du));
 denominator=tan304_mla(tan304_float(0x3f800000u),denominator,square);
 float product=tan304_mul(angle,square);
 float numerator=tan304_mla(angle,product,tan304_float(0xbdc42983u));
 if(quadrant&1u)return tan304_neg(tan304_div(denominator,numerator));
 return tan304_div(numerator,denominator);
}

/* Full Nema path postprocessor 561c68..563954. Admission receipt round317.
 * All ten child providers are source bodies above; no native code payload.
 * FP contraction disabled for recovered nonfused operations. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
/* Full native geometry body; bounded native qualification in rounds306–316. */
#pragma STDC FP_CONTRACT OFF
struct pp306_state {uint8_t flag_start,flag_open,flag_point,arc_command;uint32_t coordinate_cursor,subpath_coordinate_start;float previous_x,previous_y,current_x,current_y,control1_x,control1_y,control2_x,control2_y,last_x,last_y,last_control_x,last_control_y,subpath_start_x,subpath_start_y;uint8_t previous_command,padding[3];};
_Static_assert(sizeof(struct pp306_state)==72,"native72byte state");
_Static_assert(offsetof(struct pp306_state,previous_command)==68,"nativecommandoffset");
extern void audio_uart_nema_vg_path_bounds_reset_514e0c(void *);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_sqrt_4397a8(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode0_509690(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_two_input_angle_50969c(float,float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_tangent_563f40(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_remainder_577c3c(float,float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_ratio_58ec74(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_magnitude_58ecbc(float);
static float pp306_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t pp306_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static uint32_t pp306_fpscr(void){uint32_t v;__asm__ volatile("vmrs %0,fpscr":"=r"(v));return v;}
static int32_t pp306_i32(float f){float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(f));return (int32_t)pp306_bits(v);}
static uint32_t VectorSignedToFloat(int32_t i,uint32_t rounding){(void)rounding;float f=pp306_float((uint32_t)i),v;__asm__ volatile("vcvt.f32.s32 %0,%1":"=t"(v):"t"(f));return pp306_bits(v);}
#define ABS(v) pp306_float(pp306_bits(v)&0x7fffffffu)
#define NAN(v) ((pp306_bits(v)&0x7fffffffu)>0x7f800000u)
#define SUB41(a,b) ((uint8_t)(((uint32_t)(a))>>((b)*8u)))
#define CONCAT44(a,b) (((uint64_t)pp306_bits(a)<<32)|pp306_bits(b))

/* 562c62..562c66 and 562cf4..562cf8 round division before negation. */
static inline float pp309_divide_then_negate(float a, float b)
{
  float result;
  __asm__ volatile("vdiv.f32 %0,%1,%2\n\tvneg.f32 %0,%0"
                   : "=&t"(result) : "t"(a), "t"(b));
  return result;
}
static inline float pp309_cubic_discriminant(float b, float c, float a)
{
  float result, product; float four = 4.0f;
  __asm__ volatile("vmul.f32 %0,%2,%2\n\tvmul.f32 %1,%3,%5\n\tvmls.f32 %0,%1,%4"
                   : "=&t"(result), "=&t"(product)
                   : "t"(b), "t"(c), "t"(a), "t"(four));
  return result;
}
static inline float pp309_cubic_second_root(float b, float root, float denominator)
{
  float result;
  __asm__ volatile("vneg.f32 %0,%1\n\tvsub.f32 %0,%0,%2\n\tvdiv.f32 %0,%0,%3"
                   : "=&t"(result) : "t"(b), "t"(root), "t"(denominator));
  return result;
}
static inline float pp309_conditional_add(float a, float b)
{
  float result;
  __asm__ volatile("vadd.f32 %0,%1,%2" : "=t"(result) : "t"(a), "t"(b));
  return result;
}
/* Native VCMP N condition: unordered is PL, unlike C ordered >=. */
static inline int pp308_negative_compare(float a, float b)
{
  uint32_t flags;
  __asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr"
                   : "=r"(flags) : "t"(a), "t"(b) : "cc");
  return (int)(flags >> 31);
}
static inline int pp308_arc_excludes(float angle, float low, float high)
{
  if (pp308_negative_compare(angle, low)) return 1;
  return pp308_negative_compare(high, angle);
}
void audio_uart_nema_vg_path_process_561c68(void *path)

{
  typedef uint32_t uint;typedef uint8_t byte;typedef uint32_t undefined4;typedef uint64_t ulonglong;
  volatile uint32_t *param_1=path;
  struct pp306_state state;
  undefined4 uVar1;
  volatile float *pfVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  volatile float *pfVar7;
  int iVar8;
  volatile float *pfVar9;
  volatile float *pfVar10;
  volatile float *pfVar11;
  volatile float *pfVar12;
  byte bVar13;
  bool bVar14;
  byte bVar15;
  bool bVar16;
  uint in_fpscr=pp306_fpscr();
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  ulonglong unaff_d9; /* Every live read is dominated by local arc assignments. */
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float local_a8 [6];
  uint local_90;
  float local_8c [8];
  volatile float *local_6c;
  
  audio_uart_nema_vg_path_bounds_reset_514e0c(path);
  audio_uart_lv_memzero_48949c(&state,72u);
  state.flag_start = '\x01';
  state.flag_open = '\x01';
  state.flag_point = 1u;
  uint32_t initial_count = *param_1;
  if (initial_count != 0) {
    uVar3 = *(byte *)param_1[2] & 0xffffff6f;
  }
  if (initial_count != 0 && uVar3 != 1) {
    fVar17 = pp306_float(param_1[4]);
    in_fpscr = in_fpscr & 0xfffffff;
    if (0.0f < fVar17) {
      fVar17 = 0.0f;
    }
    param_1[4] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[5]);
    if (0.0f < fVar17) {
      fVar17 = 0.0f;
    }
    param_1[5] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[6]);
    if (fVar17 < 0.0f) {
      fVar17 = 0.0f;
    }
    param_1[6] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[7]);
    if (fVar17 < 0.0f) {
      fVar17 = 0.0f;
    }
    param_1[7] = pp306_bits(fVar17);
  }
  if (*param_1 != 0) {
    local_90 = 0;
    do {
      bVar13 = *(byte *)(param_1[2] + local_90);
      uVar3 = (uint)bVar13;
      state.previous_x = state.current_x;
      state.previous_y = state.current_y;
      bVar16 = (int)(uVar3 << 0x1b) < 0;
      uVar5 = uVar3 & 0x6f;
      bVar15 = state.previous_command & 0x6f;
      if (uVar5 == 1) {
        if ((state.flag_open == '\x01') && (state.coordinate_cursor != 0)) {
          fVar17 = 0.0f;
          fVar20 = 0.0f;
          if (state.flag_start == '\0') {
            fVar17 = state.subpath_start_x;
            fVar20 = state.subpath_start_y;
          }
          in_fpscr = in_fpscr & 0xfffffff;
          fVar21 = pp306_float(param_1[4]);
          if (pp308_negative_compare(fVar17, fVar21)) fVar21 = fVar17;
          param_1[4] = pp306_bits(fVar21);
          fVar21 = pp306_float(param_1[5]);
          if (pp308_negative_compare(fVar20, fVar21)) fVar21 = fVar20;
          param_1[5] = pp306_bits(fVar21);
          fVar21 = pp306_float(param_1[6]);
          if (!pp308_negative_compare(fVar21, fVar17)) fVar17 = fVar21;
          param_1[6] = pp306_bits(fVar17);
          fVar21 = pp306_float(param_1[7]);
          if (!pp308_negative_compare(fVar21, fVar20)) fVar20 = fVar21;
          param_1[7] = pp306_bits(fVar20);
        }
        state.flag_start = '\0';
        state.flag_point = 1;
        state.subpath_coordinate_start = state.coordinate_cursor;
        uVar3 = param_1[3];
        state.current_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
        if (bVar16) {
          state.current_x = state.last_x + state.current_x;
          state.current_y = state.last_y + *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
        }
        else {
          state.current_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
        }
        state.coordinate_cursor = state.coordinate_cursor + 2;
        state.subpath_start_x = state.current_x;
        state.subpath_start_y = state.current_y;
LAB_00562754:
        state.last_x = state.current_x;
        state.last_y = state.current_y;
        iVar6 = state.coordinate_cursor;
        state.previous_command = bVar13;
      }
      else {
        if (uVar3 == 0 || uVar3 == 0x80) {
          if (state.flag_start == '\x01') {
            state.current_x = 0.0f;
            state.current_y = 0.0f;
          }
          else {
            state.current_x = state.subpath_start_x;
            state.current_y = state.subpath_start_y;
          }
          state.flag_point = 0;
          state.flag_open = '\0';
          goto LAB_00562754;
        }
        if (state.coordinate_cursor == 0) {
          state.flag_start = '\x01';
        }
        state.flag_point = 0;
        if (uVar5 == 6) {
          uVar3 = param_1[3];
          state.control1_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.control2_x = *(volatile float *)(uVar3 + (state.coordinate_cursor + 2) * 4);
          state.control2_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 3) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 4;
          if (bVar16) {
            state.control1_x = state.control1_x + state.last_x;
            state.control1_y = state.control1_y + state.last_y;
            state.control2_x = state.control2_x + state.last_x;
            state.control2_y = state.control2_y + state.last_y;
            state.last_control_x = state.control2_x;
            state.last_control_y = state.control2_y;
            goto LAB_00561f3e;
          }
LAB_00562014:
          state.last_control_x = state.control2_x;
          state.last_control_y = state.control2_y;
LAB_00561edc:
          uVar3 = param_1[3];
          state.current_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.coordinate_cursor = state.coordinate_cursor + 1;
LAB_005620a8:
          state.current_y = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.coordinate_cursor = state.coordinate_cursor + 1;
          goto LAB_00562754;
        }
        if (uVar5 == 5) {
          uVar3 = param_1[3];
          state.control1_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 2;
          state.last_control_x = state.control1_x;
          state.last_control_y = state.control1_y;
          if (!bVar16) goto LAB_00561edc;
          state.control1_x = state.control1_x + state.last_x;
          state.control1_y = state.control1_y + state.last_y;
          state.last_control_x = state.control1_x;
          state.last_control_y = state.control1_y;
LAB_00561f3e:
          uVar3 = param_1[3];
          state.current_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4) + state.last_x;
          state.current_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4) + state.last_y;
          state.coordinate_cursor = state.coordinate_cursor + 2;
          goto LAB_00562754;
        }
        if (uVar5 == 7) {
          if ((bVar15 == 5 || bVar15 == 7) ||
             (state.control1_x = state.last_x, state.control1_y = state.last_y, fVar17 = state.last_x, fVar20 = state.last_y,
             bVar15 == 6 || bVar15 == 8)) {
            state.control1_x = state.last_x * 2.0f - state.last_control_x;
            state.control1_y = state.last_y * 2.0f - state.last_control_y;
            fVar17 = state.control1_x;
            fVar20 = state.control1_y;
          }
LAB_00561f3a:
          state.last_control_y = fVar20;
          state.last_control_x = fVar17;
          if (!bVar16) goto LAB_00561edc;
          goto LAB_00561f3e;
        }
        if (uVar5 == 8) {
          if ((bVar15 == 5 || bVar15 == 7) || (bVar15 == 6 || bVar15 == 8)) {
            state.control1_x = state.last_x * 2.0f - state.last_control_x;
            state.control1_y = state.last_y * 2.0f - state.last_control_y;
          }
          else {
            state.control1_x = state.last_x;
            state.control1_y = state.last_y;
          }
          uVar3 = param_1[3];
          state.control2_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control2_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 2;
          if (!bVar16) goto LAB_00562014;
          state.control2_x = state.control2_x + state.last_x;
          state.control2_y = state.control2_y + state.last_y;
          state.last_control_x = state.control2_x;
          state.last_control_y = state.control2_y;
          goto LAB_00561f3e;
        }
        if ((uVar3 & 0xf) == 9) {
          uVar3 = param_1[3];
          state.control1_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.control2_x = *(volatile float *)(uVar3 + (state.coordinate_cursor + 2) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 3;
          state.last_control_y = state.last_y;
          state.last_control_x = state.last_x;
          state.arc_command = bVar13;
        }
        if (uVar5 == 4) {
          uVar3 = param_1[3];
          state.current_x = state.last_x;
          if (!bVar16) goto LAB_005620a8;
          iVar6 = state.coordinate_cursor * 4;
          state.coordinate_cursor = state.coordinate_cursor + 1;
          state.current_y = state.last_y + *(volatile float *)(uVar3 + iVar6);
          goto LAB_00562754;
        }
        if (uVar5 == 3) {
          state.current_x = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          if (bVar16) {
            state.current_x = state.last_x + state.current_x;
          }
          state.coordinate_cursor = state.coordinate_cursor + 1;
          state.current_y = state.last_y;
          goto LAB_00562754;
        }
        if (uVar5 == 10) {
          iVar6 = state.coordinate_cursor + 1;
          fVar20 = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          uVar3 = in_fpscr & 0xfffffff;
          {
            float pp313_bound = pp306_float(param_1[4]);
            fVar17 = pp313_bound;
            if (pp308_negative_compare(state.current_x, pp313_bound)) {
              fVar17 = state.current_x;
            }
            param_1[4] = pp306_bits(fVar17);
          }
          {
            float pp313_bound = pp306_float(param_1[5]);
            fVar17 = pp313_bound;
            if (pp308_negative_compare(state.current_y, pp313_bound)) {
              fVar17 = state.current_y;
            }
            param_1[5] = pp306_bits(fVar17);
          }
          {
            float pp313_bound = pp306_float(param_1[6]);
            fVar17 = state.current_x;
            if (!pp308_negative_compare(pp313_bound, state.current_x)) {
              fVar17 = pp313_bound;
            }
            uint32_t pp313_xmax = pp306_bits(fVar17);
            pp313_bound = pp306_float(param_1[7]);
            param_1[6] = pp313_xmax;
            fVar17 = state.current_y;
            if (!pp308_negative_compare(pp313_bound, state.current_y)) {
              fVar17 = pp313_bound;
            }
            param_1[7] = pp306_bits(fVar17);
          }
          uVar5 = pp306_i32(fVar20) / 2;
          if (0 < (int)uVar5) {
            if ((int)(uVar5 << 0x1f) < 0) {
              uVar4 = param_1[3];
              state.current_x = *(volatile float *)(uVar4 + iVar6 * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4);
              }
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                uint32_t pp315_ymin = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[6]);
                param_1[5] = pp315_ymin;
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              iVar6 = state.coordinate_cursor + 3;
              state.previous_command = bVar13;
            }
            state.coordinate_cursor = iVar6;
            for (uVar5 = uVar5 >> 1; iVar6 = state.coordinate_cursor, uVar5 != 0; uVar5 = uVar5 - 1) {
              uVar4 = param_1[3];
              state.current_x = *(volatile float *)(uVar4 + state.coordinate_cursor * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 1) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 1) * 4);
              }
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                param_1[5] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[6]);
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              uVar4 = param_1[3];
              fVar17 = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4);
              if (bVar16) {
                state.current_y = pp309_conditional_add(*(volatile float *)(uVar4 + (state.coordinate_cursor + 3) * 4), state.current_y);
                state.current_x = pp309_conditional_add(fVar17, state.current_x);
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 3) * 4);
                state.current_x = fVar17;
              }
              state.coordinate_cursor = state.coordinate_cursor + 4;
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                uint32_t pp314_ymin = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[6]);
                param_1[5] = pp314_ymin;
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              state.previous_command = bVar13;
            }
          }
          state.coordinate_cursor = iVar6;
          in_fpscr = uVar3 | (uint)(state.last_x - state.subpath_start_x == 0.0f) << 0x1e;
          bVar13 = 0;
          if ((byte)(in_fpscr >> 0x1e) != 0) {
            in_fpscr = uVar3 | (uint)(state.last_y - state.subpath_start_y == 0.0f) << 0x1e;
            bVar13 = (byte)(in_fpscr >> 0x1e);
          }
          state.previous_x = state.current_x;
          state.previous_y = state.current_y;
          if (bVar13 == 0) {
            state.current_y = state.subpath_start_y;
            state.current_x = state.subpath_start_x;
            state.last_x = state.subpath_start_x;
            state.last_y = state.subpath_start_y;
            in_fpscr = in_fpscr & 0xfffffff;
            {
              float pp313_bound = pp306_float(param_1[4]);
              fVar17 = pp313_bound;
              if (pp308_negative_compare(state.subpath_start_x, pp313_bound)) {
                fVar17 = state.subpath_start_x;
              }
              param_1[4] = pp306_bits(fVar17);
            }
            {
              float pp313_bound = pp306_float(param_1[5]);
              fVar17 = pp313_bound;
              if (pp308_negative_compare(state.subpath_start_y, pp313_bound)) {
                fVar17 = state.subpath_start_y;
              }
              param_1[5] = pp306_bits(fVar17);
            }
            {
              float pp313_bound = pp306_float(param_1[6]);
              fVar17 = state.subpath_start_x;
              if (!pp308_negative_compare(pp313_bound, state.subpath_start_x)) {
                fVar17 = pp313_bound;
              }
              uint32_t pp313_xmax = pp306_bits(fVar17);
              pp313_bound = pp306_float(param_1[7]);
              param_1[6] = pp313_xmax;
              fVar17 = state.subpath_start_y;
              if (!pp308_negative_compare(pp313_bound, state.subpath_start_y)) {
                fVar17 = pp313_bound;
              }
              param_1[7] = pp306_bits(fVar17);
            }
          }
          state.flag_open = '\0';
          iVar6 = state.coordinate_cursor;
        }
        else {
          fVar17 = state.last_control_x;
          fVar20 = state.last_control_y;
          if (uVar5 != 0xb) goto LAB_00561f3a;
          iVar6 = state.coordinate_cursor + 1;
          fVar20 = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          in_fpscr = in_fpscr & 0xfffffff;
          {
            float pp313_bound = pp306_float(param_1[4]);
            fVar17 = pp313_bound;
            if (pp308_negative_compare(state.current_x, pp313_bound)) {
              fVar17 = state.current_x;
            }
            param_1[4] = pp306_bits(fVar17);
          }
          {
            float pp313_bound = pp306_float(param_1[5]);
            fVar17 = pp313_bound;
            if (pp308_negative_compare(state.current_y, pp313_bound)) {
              fVar17 = state.current_y;
            }
            param_1[5] = pp306_bits(fVar17);
          }
          {
            float pp313_bound = pp306_float(param_1[6]);
            fVar17 = state.current_x;
            if (!pp308_negative_compare(pp313_bound, state.current_x)) {
              fVar17 = pp313_bound;
            }
            uint32_t pp313_xmax = pp306_bits(fVar17);
            pp313_bound = pp306_float(param_1[7]);
            param_1[6] = pp313_xmax;
            fVar17 = state.current_y;
            if (!pp308_negative_compare(pp313_bound, state.current_y)) {
              fVar17 = pp313_bound;
            }
            param_1[7] = pp306_bits(fVar17);
          }
          uVar3 = pp306_i32(fVar20) / 2;
          if (0 < (int)uVar3) {
            if ((int)(uVar3 << 0x1f) < 0) {
              uVar5 = param_1[3];
              state.current_x = *(volatile float *)(uVar5 + iVar6 * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4);
              }
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                uint32_t pp315_ymin = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[6]);
                param_1[5] = pp315_ymin;
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              iVar6 = state.coordinate_cursor + 3;
              state.previous_command = bVar13;
            }
            state.coordinate_cursor = iVar6;
            state.previous_x = state.current_x;
            state.previous_y = state.current_y;
            for (uVar3 = uVar3 >> 1; iVar6 = state.coordinate_cursor, state.current_x = state.previous_x, state.current_y = state.previous_y,
                uVar3 != 0; uVar3 = uVar3 - 1) {
              uVar5 = param_1[3];
              state.current_x = *(volatile float *)(uVar5 + state.coordinate_cursor * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 1) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 1) * 4);
              }
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                param_1[5] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[6]);
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              uVar5 = param_1[3];
              fVar17 = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4);
              if (bVar16) {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 3) * 4) + state.current_y;
                state.current_x = pp309_conditional_add(fVar17, state.current_x);
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 3) * 4);
                state.current_x = fVar17;
              }
              state.coordinate_cursor = state.coordinate_cursor + 4;
              {
                float pp313_bound = pp306_float(param_1[4]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_x, pp313_bound)) {
                  fVar17 = state.current_x;
                }
                param_1[4] = pp306_bits(fVar17);
              }
              {
                float pp313_bound = pp306_float(param_1[5]);
                fVar17 = pp313_bound;
                if (pp308_negative_compare(state.current_y, pp313_bound)) {
                  fVar17 = state.current_y;
                }
                uint32_t pp314_ymin = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[6]);
                param_1[5] = pp314_ymin;
                fVar17 = state.current_x;
                if (!pp308_negative_compare(pp313_bound, state.current_x)) {
                  fVar17 = pp313_bound;
                }
                uint32_t pp313_xmax = pp306_bits(fVar17);
                pp313_bound = pp306_float(param_1[7]);
                param_1[6] = pp313_xmax;
                fVar17 = state.current_y;
                if (!pp308_negative_compare(pp313_bound, state.current_y)) {
                  fVar17 = pp313_bound;
                }
                param_1[7] = pp306_bits(fVar17);
              }
              state.previous_x = state.current_x;
              state.previous_y = state.current_y;
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              state.previous_command = bVar13;
            }
          }
        }
      }
      state.coordinate_cursor = iVar6;
      bVar13 = *(byte *)(param_1[2] + local_90) & 0x6f;
      if (bVar13 == 6 || bVar13 == 8) {
        local_a8[0] = 0.0f;
        local_a8[1] = 0.0f;
        uVar3 = in_fpscr & 0xfffffff;
        {
          float pp313_bound = pp306_float(param_1[4]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(pp313_bound, state.current_x)) {
            fVar17 = state.current_x;
          }
          param_1[4] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[5]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(pp313_bound, state.current_y)) {
            fVar17 = state.current_y;
          }
          param_1[5] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[6]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(state.current_x, pp313_bound)) {
            fVar17 = state.current_x;
          }
          param_1[6] = pp306_bits(fVar17);
        }
        fVar17 = pp306_float(param_1[7]);
        if (!pp308_negative_compare(state.current_y, fVar17)) {
          fVar17 = state.current_y;
        }
        local_a8[2] = pp306_float(param_1[4]);
        param_1[7] = pp306_bits(fVar17);
        local_a8[3] = pp306_float(param_1[5]);
        local_a8[4] = pp306_float(param_1[6]);
        local_a8[5] = pp306_float(param_1[7]);
        local_8c[0] = state.control1_x;
        uVar5 = uVar3 | (uint)(state.control1_x < local_a8[2]) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(state.control1_x) || NAN(local_a8[2])) << 0x1c;
        local_8c[1] = state.control1_y;
        local_8c[2] = state.control2_x;
        local_8c[3] = state.control2_y;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(local_a8[4] < state.control1_x) << 0x1f |
                     (uint)(NAN(local_a8[4]) || NAN(state.control1_x)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(state.control1_y < local_a8[3]) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(state.control1_y) || NAN(local_a8[3])) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(local_a8[5] < state.control1_y) << 0x1f |
                       (uint)(NAN(local_a8[5]) || NAN(state.control1_y)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) {
            uVar3 = in_fpscr & 0xfffffff;
            uVar5 = uVar3 | (uint)(state.control2_x < local_a8[2]) << 0x1f;
            in_fpscr = uVar5 | (uint)(NAN(state.control2_x) || NAN(local_a8[2])) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              in_fpscr = uVar3 | (uint)(local_a8[4] < state.control2_x) << 0x1f |
                         (uint)(NAN(local_a8[4]) || NAN(state.control2_x)) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if (bVar13 == bVar15) {
              uVar3 = in_fpscr & 0xfffffff;
              uVar5 = uVar3 | (uint)(state.control2_y < local_a8[3]) << 0x1f;
              in_fpscr = uVar5 | (uint)(NAN(state.control2_y) || NAN(local_a8[3])) << 0x1c;
              bVar13 = (byte)(uVar5 >> 0x1f);
              bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
              if (bVar13 == bVar15) {
                in_fpscr = uVar3 | (uint)(local_a8[5] < state.control2_y) << 0x1f |
                           (uint)(NAN(local_a8[5]) || NAN(state.control2_y)) << 0x1c;
                bVar15 = (byte)(in_fpscr >> 0x18);
                bVar13 = bVar15 >> 7;
                bVar15 = bVar15 >> 4 & 1;
              }
              if (bVar13 == bVar15) goto LAB_0056385a;
            }
          }
        }
        local_8c[6] = state.current_x;
        local_8c[7] = state.current_y;
        local_8c[4] = state.previous_x;
        pfVar7 = local_8c + 4;
        pfVar12 = local_8c;
        local_8c[5] = state.previous_y;
        pfVar2 = local_a8;
        pfVar9 = local_8c + 2;
        pfVar10 = local_8c + 6;
        pfVar11 = local_a8 + 2;
        iVar6 = 2;
        local_6c = pfVar2;
        do {
          fVar20 = *pfVar7;
          fVar23 = *pfVar12;
          fVar22 = *pfVar9;
          unaff_d9 = CONCAT44(fVar23,fVar22);
          fVar21 = *pfVar10;
          fVar26 = fVar20 * -3.0f + fVar23 * 9.0f + fVar22 * -9.0f + fVar21 * 3.0f;
          iVar8 = 0;
          uVar3 = in_fpscr & 0xfffffff;
          fVar24 = fVar20 * 6.0f + fVar23 * -12.0f + fVar22 * 6.0f;
          fVar17 = fVar20 * -3.0f + fVar23 * 3.0f;
          if (1e-07f <= ABS(fVar26)) {
            fVar17 = pp309_cubic_discriminant(fVar24, fVar17, fVar26);
            uVar3 = uVar3 | (uint)(fVar17 < 1.0000001e-07f) << 0x1f;
            in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
            if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
              fVar17 = audio_uart_float_sqrt_4397a8(fVar17);
              fVar18 = (fVar17 - fVar24) / (fVar26 * 2.0f);
              uVar3 = in_fpscr & 0xfffffff;
              if ((1.0000001e-07f <= fVar18) && (fVar18 < 0.9999999f)) {
                local_a8[0] = fVar18;
                iVar8 = 1;
              }
              fVar17 = pp309_cubic_second_root(fVar24, fVar17, fVar26 * 2.0f);
              uVar5 = uVar3 | (uint)(fVar17 < 1.0000001e-07f) << 0x1f;
              in_fpscr = uVar5 | (uint)NAN(fVar17) << 0x1c;
              if (((byte)(uVar5 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) &&
                 (in_fpscr = uVar3, fVar17 < 0.9999999f)) {
                pfVar2 = local_6c + iVar8;
                iVar8 = iVar8 + 1;
                *pfVar2 = fVar17;
              }
              pfVar2 = (volatile float *)0x0;
              if (iVar8 != 0) goto LAB_005629ce;
            }
          }
          else {
            fVar26 = ABS(fVar24);
            uVar5 = uVar3 | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
            in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              fVar26 = pp309_divide_then_negate(fVar17, fVar24);
              in_fpscr = uVar3 | (uint)(fVar26 < 1.0000001e-07f) << 0x1f | (uint)NAN(fVar26) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar26 < 0.9999999f)) {
              local_a8[0] = fVar26;
              iVar8 = 1;
LAB_005629ce:
              uVar1 = 0;
              if (((uint32_t)iVar8 & 1u) != 0) { /* Native LSL31 sign tests root-count parity. */
                fVar17 = 1.0f - local_a8[0];
                fVar17 = fVar17 * fVar17 * fVar17 * fVar20 +
                         fVar17 * 3.0f * fVar17 * local_a8[0] * fVar23 +
                         fVar17 * 3.0f * local_a8[0] * local_a8[0] * fVar22 +
                         local_a8[0] * local_a8[0] * local_a8[0] * fVar21;
                fVar24 = *pfVar11;
                if (fVar17 <= *pfVar11) {
                  fVar24 = fVar17;
                }
                *pfVar11 = fVar24;
                fVar24 = pfVar11[2];
                uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar17 < fVar24) << 0x1f;
                in_fpscr = uVar3 | (uint)(NAN(fVar17) || NAN(fVar24)) << 0x1c;
                if ((byte)(uVar3 >> 0x1f) != ((byte)(in_fpscr >> 0x1c) & 1)) {
                  fVar17 = fVar24;
                }
                pfVar11[2] = fVar17;
                uVar1 = 1;
              }
              /* Native562a44..562b3a: root count inR7, odd index inR0.
                 Structural research draft; native/C geometry qualification pending. */
              uint loop_pairs = ((uint)iVar8) >> 1;
              iVar8 = (int)uVar1;
              while(loop_pairs != 0) {
              fVar17 = local_a8[iVar8];
              fVar24 = 1.0f - fVar17;
              fVar24 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0f * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0f * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar24 <= *pfVar11) {
                fVar17 = fVar24;
              }
              *pfVar11 = fVar17;
              if (fVar24 < pfVar11[2] || NAN(fVar24) || NAN(pfVar11[2])) {
                fVar24 = pfVar11[2];
              }
              pfVar11[2] = fVar24;
              fVar17 = local_a8[iVar8 + 1];
              fVar24 = 1.0f - fVar17;
              fVar20 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0f * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0f * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar20 <= *pfVar11) {
                fVar17 = fVar20;
              }
              *pfVar11 = fVar17;
              fVar17 = pfVar11[2];
              uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar20 < fVar17) << 0x1f;
              in_fpscr = uVar3 | (uint)(NAN(fVar20) || NAN(fVar17)) << 0x1c;
              if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
                fVar17 = fVar20;
              }
              pfVar11[2] = fVar17;
              iVar8 += 2;
              --loop_pairs;
              } /* Native LE decrements loop counter; no external call. */
            }
          }
          pfVar7 = pfVar7 + 1;
          pfVar11 = pfVar11 + 1;
          pfVar10 = pfVar10 + 1;
          pfVar9 = pfVar9 + 1;
          pfVar12 = pfVar12 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
        param_1[4] = pp306_bits(local_a8[2]);
        param_1[5] = pp306_bits(local_a8[3]);
        param_1[6] = pp306_bits(local_a8[4]);
        param_1[7] = pp306_bits(local_a8[5]);
      }
      else if ((bVar13 == 1 || bVar13 == 2) || (bVar13 == 4 || bVar13 == 3)) {
LAB_00563802:
        in_fpscr = in_fpscr & 0xfffffff;
        {
          float pp313_bound = pp306_float(param_1[4]);
          fVar17 = pp313_bound;
          if (pp308_negative_compare(state.current_x, pp313_bound)) {
            fVar17 = state.current_x;
          }
          param_1[4] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[5]);
          fVar17 = pp313_bound;
          if (pp308_negative_compare(state.current_y, pp313_bound)) {
            fVar17 = state.current_y;
          }
          param_1[5] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[6]);
          fVar17 = state.current_x;
          if (!pp308_negative_compare(pp313_bound, state.current_x)) {
            fVar17 = pp313_bound;
          }
          uint32_t pp313_xmax = pp306_bits(fVar17);
          pp313_bound = pp306_float(param_1[7]);
          param_1[6] = pp313_xmax;
          fVar17 = state.current_y;
          if (!pp308_negative_compare(pp313_bound, state.current_y)) {
            fVar17 = pp313_bound;
          }
          param_1[7] = pp306_bits(fVar17);
        }
      }
      else if (bVar13 == 5 || bVar13 == 7) {
        uVar3 = in_fpscr & 0xfffffff;
        {
          float pp313_bound = pp306_float(param_1[4]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(pp313_bound, state.current_x)) {
            fVar17 = state.current_x;
          }
          param_1[4] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[5]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(pp313_bound, state.current_y)) {
            fVar17 = state.current_y;
          }
          param_1[5] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[6]);
          fVar17 = pp313_bound;
          if (!pp308_negative_compare(state.current_x, pp313_bound)) {
            fVar17 = state.current_x;
          }
          param_1[6] = pp306_bits(fVar17);
        }
        fVar17 = pp306_float(param_1[7]);
        if (!pp308_negative_compare(state.current_y, fVar17)) {
          fVar17 = state.current_y;
        }
        fVar20 = pp306_float(param_1[4]);
        param_1[7] = pp306_bits(fVar17);
        uVar5 = uVar3 | (uint)(state.control1_x < fVar20) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(state.control1_x) || NAN(fVar20)) << 0x1c;
        fVar17 = pp306_float(param_1[5]);
        fVar21 = pp306_float(param_1[6]);
        fVar22 = pp306_float(param_1[7]);
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(fVar21 < state.control1_x) << 0x1f |
                     (uint)(NAN(fVar21) || NAN(state.control1_x)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(state.control1_y < fVar17) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(state.control1_y) || NAN(fVar17)) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(fVar22 < state.control1_y) << 0x1f |
                       (uint)(NAN(fVar22) || NAN(state.control1_y)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) goto LAB_0056385a;
        }
        fVar23 = state.control1_x * 2.0f + state.previous_x * -2.0f;
        fVar24 = (state.current_x * 2.0f + state.control1_x * -2.0f) - fVar23;
        fVar26 = ABS(fVar24);
        bVar16 = NAN(fVar26);
        uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
        bVar14 = SUB41(uVar3 >> 0x1f,0);
        if (bVar14 == bVar16) {
          fVar23 = pp309_divide_then_negate(fVar23, fVar24);
          bVar16 = NAN(fVar23);
          uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar23 < 1.0000001e-07f) << 0x1f;
          bVar14 = SUB41(uVar3 >> 0x1f,0);
        }
        if ((bVar14 == bVar16) && (uVar3 = uVar3 & 0xfffffff, fVar23 < 0.9999999f)) {
          fVar24 = 1.0f - fVar23;
          fVar23 = fVar24 * fVar24 * state.previous_x + fVar24 * 2.0f * fVar23 * state.control1_x +
                   fVar23 * fVar23 * state.current_x;
          if (!pp308_negative_compare(fVar20, fVar23)) {
            fVar20 = fVar23;
          }
          if (!pp308_negative_compare(fVar23, fVar21)) {
            fVar21 = fVar23;
          }
        }
        fVar23 = state.control1_y * 2.0f + state.previous_y * -2.0f;
        fVar24 = (state.current_y * 2.0f + state.control1_y * -2.0f) - fVar23;
        fVar26 = ABS(fVar24);
        uVar5 = (uVar3 & 0xfffffff) | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
        in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          fVar23 = pp309_divide_then_negate(fVar23, fVar24);
          in_fpscr = (uVar3 & 0xfffffff) | (uint)(fVar23 < 1.0000001e-07f) << 0x1f |
                     (uint)NAN(fVar23) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar23 < 0.9999999f)) {
          fVar24 = 1.0f - fVar23;
          fVar23 = fVar24 * fVar24 * state.previous_y + fVar24 * 2.0f * fVar23 * state.control1_y +
                   fVar23 * fVar23 * state.current_y;
          if (!pp308_negative_compare(fVar17, fVar23)) {
            fVar17 = fVar23;
          }
          if (!pp308_negative_compare(fVar23, fVar22)) {
            fVar22 = fVar23;
          }
        }
        param_1[4] = pp306_bits(fVar20);
        param_1[5] = pp306_bits(fVar17);
        param_1[6] = pp306_bits(fVar21);
        param_1[7] = pp306_bits(fVar22);
      }
      else if ((bVar13 & 0xf) == 9) {
        fVar20 = ABS(state.control1_x);
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar20 < 1.0000001e-05f) << 0x1f;
        bVar13 = -(char)((int)in_fpscr >> 0x1f);
        if (bVar13 == 0) {
          fVar17 = ABS(state.control1_y);
          unaff_d9 = (ulonglong)pp306_bits(fVar17);
          in_fpscr = uVar3 | (uint)(fVar17 < 1.0000001e-05f) << 0x1f;
          bVar13 = (byte)(in_fpscr >> 0x1f);
        }
        if (bVar13 != 0) goto LAB_00563802;
        local_a8[5] = state.control2_x;
        fVar26 = state.control2_x * 0.017453292f;
        local_a8[3] = state.last_control_x;
        local_a8[2] = state.last_control_y;
        local_a8[1] = state.last_x;
        local_a8[0] = state.last_y;
        local_a8[4] = (float)audio_uart_float_trig_mode1_50968c(fVar26);
        fVar23 = (float)audio_uart_float_trig_mode0_509690(fVar26);
        fVar28 = local_a8[3] * local_a8[4] + local_a8[2] * fVar23;
        fVar29 = fVar28 / fVar20;
        fVar30 = local_a8[2] * local_a8[4] - local_a8[3] * fVar23;
        fVar31 = local_a8[1] * local_a8[4] + local_a8[0] * fVar23;
        fVar25 = fVar31 / fVar20;
        fVar32 = local_a8[0] * local_a8[4] - local_a8[1] * fVar23;
        fVar21 = fVar29 + fVar25;
        fVar18 = fVar30 / fVar17;
        unaff_d9 = CONCAT44(fVar18,fVar17);
        fVar27 = fVar32 / fVar17;
        fVar22 = fVar18 + fVar27;
        fVar33 = fVar29 - fVar25;
        fVar18 = fVar18 - fVar27;
        fVar24 = fVar33 * fVar33 + fVar18 * fVar18;
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar24 == 0.0f) << 0x1e;
        if ((byte)(in_fpscr >> 0x1e) != 0) goto LAB_0056385a;
        local_8c[0] = 1.0f / fVar24 + -0.25f;
        if (local_8c[0] < 0.0f) {
          local_8c[0] = 0.0f;
          fVar21 = (float)audio_uart_float_sqrt_4397a8(fVar24 * 0.25f);
          fVar20 = fVar20 * fVar21;
          fVar17 = fVar17 * fVar21;
          fVar29 = fVar28 / fVar20;
          fVar30 = fVar30 / fVar17;
          unaff_d9 = CONCAT44(fVar30,fVar17);
          fVar25 = fVar31 / fVar20;
          fVar21 = fVar29 + fVar25;
          fVar27 = fVar32 / fVar17;
          fVar22 = fVar30 + fVar27;
          fVar33 = fVar29 - fVar25;
          fVar18 = fVar30 - fVar27;
        }
        fVar17 = (float)audio_uart_float_sqrt_4397a8(local_8c[0]);
        fVar31 = fVar21 * 0.5f + fVar17 * fVar18;
        fVar32 = fVar22 * 0.5f - fVar17 * fVar33;
        fVar24 = (float)audio_uart_float_two_input_angle_50969c(pp306_float((uint32_t)(unaff_d9>>32)) - fVar32,fVar29 - fVar31);
        fVar28 = pp306_float((uint32_t)unaff_d9);
        fVar30 = (float)audio_uart_float_two_input_angle_50969c(fVar27 - fVar32,fVar25 - fVar31);
        fVar24 = fVar30 * 57.29578f - fVar24 * 57.29578f;
        if (fVar24 < 0.0f) {
          fVar24 = fVar24 + 360.0f;
        }
        bVar13 = state.arc_command >> 6;
        bVar15 = bVar13 & 1;
        if ((int)((uint)state.arc_command << 0x1a) < 0) {
          bVar15 = bVar15 ^ 1;
        }
        if (((180.0f <= fVar24) || (bVar15 == 0)) && ((fVar24 < 180.0f || (bVar15 != 0)))) {
          fVar31 = fVar21 * 0.5f - fVar17 * fVar18;
          fVar32 = fVar22 * 0.5f + fVar17 * fVar33;
        }
        fVar17 = fVar31 * fVar20 * fVar23 + fVar32 * fVar28 * local_a8[4];
        uVar5 = (uVar3 & 0xfffffff) | (uint)(local_a8[5] == 0.0f) << 0x1e;
        fVar21 = fVar31 * fVar20 * local_a8[4] - fVar32 * fVar28 * fVar23;
        local_a8[4] = -1.0f;
        bVar15 = (byte)(uVar5 >> 0x1e);
        if (bVar15 == 0) {
          uVar5 = (uVar3 & 0xfffffff) | (uint)(local_a8[5] == 180.0f) << 0x1e;
          bVar15 = (byte)(uVar5 >> 0x1e);
        }
        if (bVar15 == 0) {
          uVar3 = (uVar5 & 0xfffffff) | (uint)(local_a8[5] == 90.0f) << 0x1e;
          bVar15 = (byte)(uVar3 >> 0x1e);
          if (bVar15 == 0) {
            uVar3 = (uVar5 & 0xfffffff) | (uint)(local_a8[5] == 270.0f) << 0x1e;
            bVar15 = (byte)(uVar3 >> 0x1e);
          }
          fVar29 = -1.0f;
          if (bVar15 == 0) {
            fVar22 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar18 = (float)audio_uart_float_inverse_ratio_58ec74((fVar28 * fVar22) / fVar20);
            fVar18 = -fVar18;
            fVar22 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar30 = (float)audio_uart_float_inverse_ratio_58ec74((fVar28 * fVar22) / fVar20);
            fVar30 = 3.1415927f - fVar30;
            fVar22 = (float)audio_uart_float_trig_mode1_50968c(fVar18);
            fVar23 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar24 = (float)audio_uart_float_trig_mode0_509690(fVar18);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar23 = (fVar21 + fVar20 * fVar22 * fVar23) - fVar28 * fVar24 * fVar25;
            fVar22 = (float)audio_uart_float_trig_mode1_50968c(fVar30);
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar30);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar25 = (fVar21 + fVar20 * fVar22 * fVar24) - fVar28 * fVar25 * fVar27;
            uVar3 = uVar3 & 0xfffffff;
            fVar22 = fVar25;
            fVar24 = fVar18;
            if (fVar25 < fVar23) {
              fVar22 = fVar23;
              fVar24 = fVar30;
              fVar23 = fVar25;
              fVar30 = fVar18;
            }
            fVar18 = (float)audio_uart_float_trig_mode1_50968c(fVar24);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar24 = (float)audio_uart_float_trig_mode0_509690(fVar24);
            fVar27 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar18 = (fVar17 + fVar20 * fVar18 * fVar25 + fVar28 * fVar24 * fVar27) - fVar17;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar18 < 0.0f) << 0x1f | (uint)(fVar18 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar18) << 0x1c;
            fVar25 = fVar23 - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar24 = 1.0f;
            }
            fVar18 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25 + fVar18 * fVar18);
            fVar18 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar25 / fVar18);
            fVar18 = (float)audio_uart_float_remainder_577c3c(fVar24 * fVar18 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar30);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar30 = (float)audio_uart_float_trig_mode0_509690(fVar30);
            fVar27 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar30 = (fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar30 * fVar27) - fVar17;
            uVar5 = (uVar5 & 0xfffffff) | (uint)(fVar30 < 0.0f) << 0x1f | (uint)(fVar30 == 0.0f) << 0x1e
            ;
            uVar3 = uVar5 | (uint)NAN(fVar30) << 0x1c;
            fVar25 = fVar22 - fVar21;
            bVar15 = (byte)(uVar5 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar3 >> 0x1c) & 1)) {
              fVar24 = 1.0f;
            }
            fVar30 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25 + fVar30 * fVar30);
            fVar30 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar25 / fVar30);
            fVar30 = (float)audio_uart_float_remainder_577c3c(fVar24 * fVar30 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar24 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar32 = (float)audio_uart_float_inverse_ratio_58ec74(fVar28 / (fVar24 * fVar20));
            fVar24 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar31 = (float)audio_uart_float_inverse_ratio_58ec74(fVar28 / (fVar24 * fVar20));
            fVar31 = fVar31 + 3.1415927f;
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar32);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar32);
            fVar33 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar24 = fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar27 * fVar33;
            fVar25 = (float)audio_uart_float_trig_mode1_50968c(fVar31);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar33 = (float)audio_uart_float_trig_mode0_509690(fVar31);
            fVar19 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar33 = fVar17 + fVar20 * fVar25 * fVar27 + fVar28 * fVar33 * fVar19;
            uVar3 = uVar3 & 0xfffffff;
            fVar25 = fVar33;
            fVar27 = fVar32;
            if (fVar33 < fVar24) {
              fVar25 = fVar24;
              fVar27 = fVar31;
              fVar24 = fVar33;
              fVar31 = fVar32;
            }
            local_a8[4] = (float)audio_uart_float_trig_mode1_50968c(fVar27);
            fVar32 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar27);
            fVar33 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar19 = fVar24 - fVar17;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar19 < 0.0f) << 0x1f | (uint)(fVar19 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar32 = ((fVar21 + fVar20 * local_a8[4] * fVar32) - fVar28 * fVar27 * fVar33) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar27 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar27 = 1.0f;
            }
            fVar33 = (float)audio_uart_float_sqrt_4397a8(fVar32 * fVar32 + fVar19 * fVar19);
            fVar32 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar32 / fVar33);
            fVar27 = (float)audio_uart_float_remainder_577c3c(fVar27 * fVar32 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar32 = (float)audio_uart_float_trig_mode1_50968c(fVar31);
            fVar33 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar31 = (float)audio_uart_float_trig_mode0_509690(fVar31);
            fVar26 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar19 = fVar25 - fVar17;
            uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar19 < 0.0f) << 0x1f | (uint)(fVar19 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar20 = ((fVar21 + fVar32 * fVar20 * fVar33) - fVar31 * fVar28 * fVar26) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0f;
            }
            fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20 + fVar19 * fVar19);
            fVar20 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar20 / fVar26);
            fVar20 = fVar29 * fVar20 + 6.2831855f;
          }
          else {
            fVar23 = -fVar28;
            fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar23 * fVar23);
            fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar23 / fVar22);
            fVar18 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar28 * fVar28);
            fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar28 / fVar22);
            fVar30 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar25 = -fVar20;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar25 < 0.0f) << 0x1f | (uint)(fVar25 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar25) << 0x1c;
            fVar23 = fVar21 - fVar28;
            fVar22 = fVar21 + fVar28;
            fVar24 = fVar17 - fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar26 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar26 = 1.0f;
            }
            fVar25 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25);
            fVar25 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar25);
            fVar27 = (float)audio_uart_float_remainder_577c3c(fVar26 * fVar25 + 6.2831855f,pp306_float(0x40c90fdbu));
            uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar20 < 0.0f) << 0x1f | (uint)(fVar20 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar20) << 0x1c;
            fVar25 = fVar17 + fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0f;
            }
            fVar20 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20);
            fVar20 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar20);
            fVar20 = fVar29 * fVar20 + 6.2831855f;
          }
        }
        else {
          fVar23 = -fVar20;
          fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar23 * fVar23);
          fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar23 / fVar22);
          fVar18 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
          fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20);
          fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar20 / fVar22);
          fVar30 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
          fVar26 = -fVar28;
          uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar26 < 0.0f) << 0x1f | (uint)(fVar26 == 0.0f) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar26) << 0x1c;
          fVar23 = fVar21 - fVar20;
          fVar22 = fVar21 + fVar20;
          fVar24 = fVar17 - fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0f;
          }
          else {
            fVar20 = 1.0f;
          }
          fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar26 * fVar26);
          fVar26 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar26);
          fVar27 = (float)audio_uart_float_remainder_577c3c(fVar20 * fVar26 + 6.2831855f,pp306_float(0x40c90fdbu));
          uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar28 < 0.0f) << 0x1f | (uint)(fVar28 == 0.0f) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
          fVar25 = fVar17 + fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0f;
          }
          else {
            fVar20 = 1.0f;
          }
          fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar28 * fVar28);
          fVar26 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar26);
          fVar20 = fVar20 * fVar26 + 6.2831855f;
        }
        fVar31 = -1.0f;
        fVar26 = (float)audio_uart_float_remainder_577c3c(fVar20,pp306_float(0x40c90fdbu));
        fVar28 = local_a8[2] - fVar17;
        uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar28 < 0.0f) << 0x1f | (uint)(fVar28 == 0.0f) << 0x1e;
        uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
        fVar29 = local_a8[3] - fVar21;
        bVar15 = (byte)(uVar3 >> 0x18);
        fVar20 = fVar31;
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
          fVar20 = 1.0f;
        }
        fVar28 = (float)audio_uart_float_sqrt_4397a8(fVar29 * fVar29 + fVar28 * fVar28);
        fVar28 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar29 / fVar28);
        fVar20 = (float)audio_uart_float_remainder_577c3c(fVar20 * fVar28 + 6.2831855f,pp306_float(0x40c90fdbu));
        fVar17 = local_a8[0] - fVar17;
        uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar17 < 0.0f) << 0x1f | (uint)(fVar17 == 0.0f) << 0x1e;
        in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
        fVar21 = local_a8[1] - fVar21;
        unaff_d9 = CONCAT44(fVar21,fVar20);
        bVar15 = (byte)(uVar3 >> 0x18);
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
          fVar31 = 1.0f;
        }
        fVar17 = (float)audio_uart_float_sqrt_4397a8(fVar21 * fVar21 + fVar17 * fVar17);
        fVar17 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar21 / fVar17);
        fVar17 = (float)audio_uart_float_remainder_577c3c(fVar31 * fVar17 + 6.2831855f,pp306_float(0x40c90fdbu));
        if ((bVar13 & 1) == 0) {
          unaff_d9 = (ulonglong)pp306_bits(fVar17);
          fVar17 = fVar20;
        }
        bVar16 = false;
        fVar20 = pp306_float((uint32_t)unaff_d9);
        in_fpscr = in_fpscr & 0xfffffff;
        /* 563620..56374e uses N/PL, including unordered outcomes. */
        {
          int wrapped = pp308_negative_compare(fVar17, fVar20);
          float low = wrapped ? fVar17 : fVar20;
          float high = wrapped ? fVar20 : fVar17;
          if (pp308_arc_excludes(fVar18, low, high) != wrapped)
            fVar23 = pp308_negative_compare(local_a8[3], local_a8[1])
                       ? local_a8[3] : local_a8[1];
          if (pp308_arc_excludes(fVar30, low, high) != wrapped)
            fVar22 = pp308_negative_compare(local_a8[1], local_a8[3])
                       ? local_a8[3] : local_a8[1];
          if (pp308_arc_excludes(fVar27, low, high) != wrapped)
            fVar24 = pp308_negative_compare(local_a8[2], local_a8[0])
                       ? local_a8[2] : local_a8[0];
          if (pp308_arc_excludes(fVar26, low, high) != wrapped)
            fVar25 = pp308_negative_compare(local_a8[0], local_a8[2])
                       ? local_a8[2] : local_a8[0];
        }
        {
          float pp313_bound = pp306_float(param_1[4]);
          fVar17 = pp313_bound;
          if (fVar23 < pp313_bound) {
            fVar17 = fVar23;
          }
          param_1[4] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[5]);
          fVar17 = pp313_bound;
          if (fVar24 < pp313_bound) {
            fVar17 = fVar24;
          }
          param_1[5] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[6]);
          fVar17 = pp313_bound;
          if (pp313_bound < fVar23) {
            fVar17 = fVar23;
          }
          param_1[6] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[7]);
          fVar17 = pp313_bound;
          if (pp313_bound < fVar24) {
            fVar17 = fVar24;
          }
          param_1[7] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[4]);
          fVar17 = pp313_bound;
          if (fVar22 < pp313_bound) {
            fVar17 = fVar22;
          }
          param_1[4] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[5]);
          fVar17 = pp313_bound;
          if (fVar25 < pp313_bound) {
            fVar17 = fVar25;
          }
          param_1[5] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[6]);
          fVar17 = pp313_bound;
          if (pp313_bound < fVar22) {
            fVar17 = fVar22;
          }
          param_1[6] = pp306_bits(fVar17);
        }
        {
          float pp313_bound = pp306_float(param_1[7]);
          fVar17 = pp313_bound;
          if (pp313_bound < fVar25) {
            fVar17 = fVar25;
          }
          param_1[7] = pp306_bits(fVar17);
        }
      }
LAB_0056385a:
      local_90 = local_90 + 1;
    } while (local_90 < *param_1);
  }
  float bound_4 = pp306_float(param_1[4]);
  iVar6 = pp306_i32(bound_4);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 - (uint32_t)pp308_negative_compare(bound_4, fVar17),0);
  param_1[4] = uVar3;
  float bound_5 = pp306_float(param_1[5]);
  iVar6 = pp306_i32(bound_5);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 - (uint32_t)pp308_negative_compare(bound_5, fVar17),0);
  param_1[5] = uVar3;
  float bound_6 = pp306_float(param_1[6]);
  iVar6 = pp306_i32(bound_6);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 + (uint32_t)pp308_negative_compare(fVar17, bound_6),0);
  param_1[6] = uVar3;
  float bound_7 = pp306_float(param_1[7]);
  iVar6 = pp306_i32(bound_7);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 + (uint32_t)pp308_negative_compare(fVar17, bound_7),0);
  param_1[7] = uVar3;
  param_1[0x14] = pp306_bits(pp306_float(param_1[6]) - pp306_float(param_1[4]));
  param_1[0x15] = pp306_bits(pp306_float(param_1[7]) - pp306_float(param_1[5]));
  return;
}


#undef ABS
#undef NAN
#undef SUB41
#undef CONCAT44

/* Full native LVGL size clamps; native qualification receipt round319. */
/* Native4408d6..440966/440968..4409f8; source-backed LVGL size clamps.
 * LVGL lv_obj_pos.c969..980; native wrap and signed percentage boundaries retained. */
#include <stdint.h>
static int32_t lv319_resolve(int32_t bound,int32_t reference)
{
 uint32_t raw=(uint32_t)bound;
 int32_t plain=(int32_t)(raw & 0x9fffffffu);
 if((raw & 0x60000000u)==0x20000000u && plain<0x1fffffff){
  int32_t percent=plain>=0x10000000 ? (int32_t)(0x0fffffffu-(uint32_t)plain) : plain;
  int32_t product=(int32_t)((uint32_t)percent*(uint32_t)reference);
  return product/100;
 }
 return bound;
}
static int32_t lv319_clamp(int32_t value,int32_t minimum,int32_t maximum,int32_t reference)
{
 minimum=lv319_resolve(minimum,reference);
 maximum=lv319_resolve(maximum,reference);
 int32_t limited=value<maximum?value:maximum;
 return limited<minimum?minimum:limited;
}
int32_t audio_uart_lv_clamp_width_4408d6(int32_t v,int32_t lo,int32_t hi,int32_t ref)
{return lv319_clamp(v,lo,hi,ref);}
int32_t audio_uart_lv_clamp_height_440968(int32_t v,int32_t lo,int32_t hi,int32_t ref)
{return lv319_clamp(v,lo,hi,ref);}

/* Native LVGL size-refresh leaf contracts; qualification receipt round320. */
/* Complete native style leaves: native selectors agree with pinned LVGL lv_style.h.
 * Area copy43ee94..43eea4 intentionally retains interleaved load/store for overlap. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
int32_t audio_uart_lv_style_width_43eea6(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,1u);}
int32_t audio_uart_lv_style_min_width_43eeb0(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,4u);}
int32_t audio_uart_lv_style_max_width_43eeba(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,5u);}
int32_t audio_uart_lv_style_height_43eec4(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,2u);}
int32_t audio_uart_lv_style_min_height_43eece(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,6u);}
int32_t audio_uart_lv_style_max_height_43eed8(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,7u);}
int32_t audio_uart_lv_style_margin_top_43ef70(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,24u);}
int32_t audio_uart_lv_style_margin_bottom_43ef7a(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,25u);}
int32_t audio_uart_lv_style_margin_left_43ef84(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,26u);}
int32_t audio_uart_lv_style_margin_right_43ef8e(void *object,uint32_t selector)
{return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,27u);}
uint8_t audio_uart_lv_style_base_dir_43efba(void *object,uint32_t selector)
{return (uint8_t)audio_uart_lv_style_property_44bdea(object,selector,39u);}
void audio_uart_lv_area_copy_43ee94(void *destination,const void *source)
{
 volatile uint32_t *d=destination;
 const volatile uint32_t *s=source;
 d[0]=s[0]; d[1]=s[1]; d[2]=s[2]; d[3]=s[3];
}

/* Complete native coordinate getters; qualification receipt round321. */
/* Complete native43fc2a..43fc63 and43feca..43ff43; pinned lv_obj_pos.c.
 * Genuine native null assertion: diagnostic call then faulting volatile word write.
 * No assertion-body placeholder or fabricated successful return. */
#include <stdint.h>
#include <stddef.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_lv_area_copy_43ee94(void *,const void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
static const char lv321_format[]="Asserted at expression: %s (%s)";
static const char lv321_expression[]="obj != NULL";
static const char lv321_message[]="NULL pointer";
static const char lv321_coords_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char lv321_coords_function[]="lv_obj_get_coords";
static const char lv321_content_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char lv321_content_function[]="lv_obj_get_content_coords";
static _Noreturn void lv321_assert_null(uint32_t line,const char *function,const char *file)
{
 audio_uart_lvgl_log(3u,file,line,function,lv321_format,lv321_expression,lv321_message);
 for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
void audio_uart_lv_obj_coords_43fc2a(const void *object,void *area)
{
 if(object==NULL)lv321_assert_null(480u,lv321_coords_function,lv321_coords_file);
 audio_uart_lv_area_copy_43ee94(area,(const uint8_t *)object+20u);
}
void audio_uart_lv_obj_content_coords_43feca(void *object,void *area)
{
 if(object==NULL)lv321_assert_null(579u,lv321_content_function,lv321_content_file);
 audio_uart_lv_obj_coords_43fc2a(object,area);
 volatile uint32_t *a=area;
 uint32_t space=(uint32_t)audio_uart_lv_style_pad_left_43efc6(object,0u,0u,0u);a[0]=a[0]+space;
 space=(uint32_t)audio_uart_lv_style_pad_right_43eff4(object,0u);a[2]=a[2]-space;
 space=(uint32_t)audio_uart_lv_style_pad_top_43f022(object,0u,0u,0u);a[1]=a[1]+space;
 space=(uint32_t)audio_uart_lv_style_pad_bottom_43f050(object,0u);a[3]=a[3]-space;
}

/* Complete native content-sizing helper bodies, source-backed lv_obj_pos.c/lv_style.h. */
#include <stdint.h>
#include <stddef.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
int32_t audio_uart_lv_style_x_43eee2(void *o,uint32_t s){return (int32_t)audio_uart_lv_style_property_44bdea(o,s,8u);}
int32_t audio_uart_lv_style_y_43eeec(void *o,uint32_t s){return (int32_t)audio_uart_lv_style_property_44bdea(o,s,9u);}
uint8_t audio_uart_lv_style_align_43eef6(void *o,uint32_t s){return (uint8_t)audio_uart_lv_style_property_44bdea(o,s,10u);}
uint32_t audio_uart_lv_layout_positioned_43f612(void *o)
{
 if(audio_uart_lv_obj_has_flag_any_43e11c(o,0x60001u))return 0u;
 void *parent=audio_uart_lv_obj_parent_44dca2(o);
 if(parent==NULL)return 0u;
 return (uint16_t)audio_uart_lv_style_property_44bdea(parent,0u,22u)!=0u;
}
int32_t audio_uart_lv_self_width_43ff44(void *o)
{
 int32_t size[2]={0,(int32_t)0xe0000001u};
 (void)audio_uart_lv_obj_event_451670(o,52u,size);
 return size[0];
}
int32_t audio_uart_lv_self_height_43ff5e(void *o)
{
 int32_t size[2]={(int32_t)0xe0000001u,0};
 (void)audio_uart_lv_obj_event_451670(o,52u,size);
 return size[1];
}

/* Complete native area size450b80..450b97 and scrollbar invalidate44f2ca..44f315.
 * Pinned Ambiq LVGL lv_area.c69-77 and lv_obj_scroll.c637-647.
 * Inclusive extents and product wrap modulo2^32; preserve repeated size reads. */
#include <stdint.h>
extern void audio_uart_lv_get_scrollbar_areas_44eb28(void *,int32_t *,int32_t *);
extern void audio_uart_display_invalidate_area(void *,const int32_t *);
uint32_t audio_uart_lv_area_size_450b80(const void *area)
{
 const volatile uint32_t *p=(const volatile uint32_t *)area;
 uint32_t x2=p[2];uint32_t x1=p[0];uint32_t width=x2-x1+1u;
 uint32_t y2=p[3];uint32_t y1=p[1];uint32_t height=y2-y1+1u;
 return height*width;
}
void audio_uart_lv_scrollbar_invalidate_44f2ca(void *object)
{
 int32_t horizontal[4],vertical[4];
 audio_uart_lv_get_scrollbar_areas_44eb28(object,horizontal,vertical);
 if(audio_uart_lv_area_size_450b80(horizontal)==0u && audio_uart_lv_area_size_450b80(vertical)==0u)return;
 if(audio_uart_lv_area_size_450b80(horizontal)!=0u)audio_uart_display_invalidate_area(object,horizontal);
 if(audio_uart_lv_area_size_450b80(vertical)!=0u)audio_uart_display_invalidate_area(object,vertical);
}

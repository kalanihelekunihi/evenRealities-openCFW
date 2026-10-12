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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
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

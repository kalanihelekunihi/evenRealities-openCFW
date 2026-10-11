/* Native dashboard extension load 0x501d5c. All control-flow exits,
 * file effects, 4 KiB cap, nanopb decode and diagnostics are retained.
 * Product buffers/schema and ROM log strings remain typed contracts. */
#include <stdint.h>
#include <stddef.h>

extern volatile uint8_t audio_uart_dashboard_ready; /* *DAT_0050215c */
extern uint8_t audio_uart_dashboard_file_buffer[4096]; /* DAT_00502654 */
extern uint8_t audio_uart_dashboard_decoded[188]; /* DAT_00502660 */
extern const void *audio_uart_dashboard_schema; /* DAT_00502664 */
extern const char audio_uart_dashboard_path[]; /* DAT_0050261c */
extern const char audio_uart_dashboard_mode[]; /* LAB_005020ec */
extern const char audio_uart_dashboard_module[]; /* DAT_0050262c */
extern const char audio_uart_dashboard_source[]; /* DAT_00502628 */
extern const char audio_uart_dashboard_function[]; /* DAT_00502624 */
extern const char audio_uart_dashboard_none[]; /* PTR_s__none__005025e8 */

/* Native ROM literals are independent, not a product-owned pointer table. */
extern const char audio_uart_dashboard_e_absent[],audio_uart_dashboard_c_absent[];
extern const char audio_uart_dashboard_e_open[],audio_uart_dashboard_c_open[];
extern const char audio_uart_dashboard_e_seek_end[],audio_uart_dashboard_c_seek_end[];
extern const char audio_uart_dashboard_e_size[],audio_uart_dashboard_c_size[];
extern const char audio_uart_dashboard_e_seek_set[],audio_uart_dashboard_c_seek_set[];
extern const char audio_uart_dashboard_e_read[],audio_uart_dashboard_c_read[];
extern const char audio_uart_dashboard_e_decode[],audio_uart_dashboard_c_decode[];
extern const char audio_uart_dashboard_e_success[],audio_uart_dashboard_c_success[];
static const char *const audio_uart_dashboard_extended_format[8]={
    audio_uart_dashboard_e_absent,audio_uart_dashboard_e_open,
    audio_uart_dashboard_e_seek_end,audio_uart_dashboard_e_size,
    audio_uart_dashboard_e_seek_set,audio_uart_dashboard_e_read,
    audio_uart_dashboard_e_decode,audio_uart_dashboard_e_success};
static const char *const audio_uart_dashboard_compact_format[8]={
    audio_uart_dashboard_c_absent,audio_uart_dashboard_c_open,
    audio_uart_dashboard_c_seek_end,audio_uart_dashboard_c_size,
    audio_uart_dashboard_c_seek_set,audio_uart_dashboard_c_read,
    audio_uart_dashboard_c_decode,audio_uart_dashboard_c_success};

extern uint32_t audio_uart_pb_file_exists(void); /* selected 0x55876a */
extern void *audio_file_open(const char *,const char *); /* 0x474550 */
extern int32_t audio_file_close(void *); /* selected 0x4745f4 */
extern int32_t audio_file_seek(void *,int32_t,uint32_t); /* 0x474634 */
extern int32_t audio_file_tell(void *); /* 0x474814 */
extern uint32_t audio_file_read(void *,uint32_t,uint32_t,void *); /* 0x474870 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439c04 equivalent */
extern void audio_uart_pb_stream_init(void *,const void *,uint32_t); /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *,const void *,void *); /* 0x490120 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

enum { ABSENT, OPEN_FAIL, SEEK_END_FAIL, SIZE_FAIL, SEEK_SET_FAIL,
       SHORT_READ, DECODE_FAIL, SUCCESS };

static void log0(uint32_t slot,uint8_t level,uint32_t line,uint32_t compact) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_dashboard_module,
                           audio_uart_dashboard_source,
                           audio_uart_dashboard_function,line,
                           audio_uart_dashboard_extended_format[slot]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,
                                    audio_uart_dashboard_compact_format[slot],
                                    audio_uart_dashboard_compact_format[slot]);
}
static void log_path(uint32_t slot,uint8_t level,uint32_t line,uint32_t compact) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,audio_uart_dashboard_module,
                           audio_uart_dashboard_source,
                           audio_uart_dashboard_function,line,
                           audio_uart_dashboard_extended_format[slot],
                           audio_uart_dashboard_path);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact,
                                    audio_uart_dashboard_compact_format[slot],
                                    audio_uart_dashboard_compact_format[slot],
                                    audio_uart_dashboard_path);
}
static void log_size(uint32_t slot,uint32_t line,uint32_t actual,
                     uint32_t expected) {
    if(audio_log_flags()&2u)
        audio_log_extended(1u,audio_uart_dashboard_module,
                           audio_uart_dashboard_source,
                           audio_uart_dashboard_function,line,
                           audio_uart_dashboard_extended_format[slot],
                           actual,expected);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x4800000u,
                                    audio_uart_dashboard_compact_format[slot],
                                    audio_uart_dashboard_compact_format[slot],
                                    actual,expected);
}

uint32_t audio_uart_service_prepare8(void) {
    audio_uart_dashboard_ready=0u;
    if(audio_uart_pb_file_exists()==0u) {
        log_path(ABSENT,2u,0x315u,0x8400000u);
        return UINT32_MAX;
    }
    void *file=audio_file_open(audio_uart_dashboard_path,
                               audio_uart_dashboard_mode);
    if(file==0) {
        log_path(OPEN_FAIL,1u,0x31au,0x4400000u);
        return UINT32_MAX;
    }
    if(audio_file_seek(file,0,2u)!=0) {
        log0(SEEK_END_FAIL,1u,0x31fu,0x4000000u);
        (void)audio_file_close(file);
        return UINT32_MAX;
    }
    uint32_t size=(uint32_t)audio_file_tell(file);
    if(size-1u>=4096u) {
        log_size(SIZE_FAIL,0x326u,size,4096u);
        (void)audio_file_close(file);
        return UINT32_MAX;
    }
    if(audio_file_seek(file,0,0u)!=0) {
        log0(SEEK_SET_FAIL,1u,0x32bu,0x4000000u);
        (void)audio_file_close(file);
        return UINT32_MAX;
    }
    audio_uart_buffer_zero(audio_uart_dashboard_file_buffer,4096u,0u);
    uint32_t count=audio_file_read(audio_uart_dashboard_file_buffer,1u,size,file);
    (void)audio_file_close(file);
    if(count!=size) {
        log_size(SHORT_READ,0x337u,size,count);
        return UINT32_MAX;
    }
    uint32_t source_stream[4],decode_stream[4];
    audio_uart_pb_stream_init(source_stream,audio_uart_dashboard_file_buffer,size);
    (void)audio_queue_copy_bytes(decode_stream,source_stream,16u);
    audio_uart_buffer_zero(audio_uart_dashboard_decoded,188u,0u);
    if(audio_uart_pb_decode(decode_stream,audio_uart_dashboard_schema,
                            audio_uart_dashboard_decoded)==0u) {
        const char *error=(const char *)(uintptr_t)decode_stream[3];
        if(error==0) error=audio_uart_dashboard_none;
        if(audio_log_flags()&2u)
            audio_log_extended(1u,audio_uart_dashboard_module,
                               audio_uart_dashboard_source,
                               audio_uart_dashboard_function,0x342u,
                               audio_uart_dashboard_extended_format[DECODE_FAIL],
                               error);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x4400000u,
                                        audio_uart_dashboard_compact_format[DECODE_FAIL],
                                        audio_uart_dashboard_compact_format[DECODE_FAIL],
                                        error);
        return UINT32_MAX;
    }
    audio_uart_dashboard_ready=1u;
    uint8_t *p=audio_uart_dashboard_decoded;
    uint16_t count_field=*(uint16_t *)(void *)(p+0x38u);
    void *name=*(void **)(void *)(p+0x34u);
    if(audio_log_flags()&2u)
        audio_log_extended(3u,audio_uart_dashboard_module,
                           audio_uart_dashboard_source,
                           audio_uart_dashboard_function,0x34cu,
                           audio_uart_dashboard_extended_format[SUCCESS],
                           p[0x30u],name,count_field,p,p+0x10u);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xd400000u,
                                    audio_uart_dashboard_compact_format[SUCCESS],
                                    audio_uart_dashboard_compact_format[SUCCESS],
                                    p[0x30u],name,count_field,p,p+0x10u);
    return 0u;
}

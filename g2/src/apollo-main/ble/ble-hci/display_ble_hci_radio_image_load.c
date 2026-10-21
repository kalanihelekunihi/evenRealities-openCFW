/* Native 0x52f442: load and parse the EM9305 firmware file into live staging
 * cells.  File contents, heap allocation and device RAM are runtime inputs. */
#include <stdint.h>
extern const char *audio_ble_radio_file_mode_52f3a0(uint32_t);
extern int32_t audio_ble_radio_file_size_52f3f8(void *);
extern void *audio_file_open(const char *,const char *);
extern uint32_t audio_file_read(void *,uint32_t,uint32_t,void *);
extern int32_t audio_file_close(void *);
extern void *file_heap_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern uint32_t audio_ble_radio_header_copy_52f86a(void *,void *);
extern uint32_t audio_ble_radio_records_52f87c(const void *,uint32_t);
extern uint32_t audio_ble_radio_record_data_52f99e(const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="_parseBleFwBinFile";
static const char path[]="firmware/ble_em9305.bin";
static const char open_error[]="Failed to open file: %s, error: %d";
static const char open_compact[]="[srv.em9305]Failed to open file: %s, error: %d";
static const char size_error[]="Failed to get file size";
static const char size_compact[]="[srv.em9305]Failed to get file size";
static const char size_info[]="File size: %ld bytes";
static const char size_info_compact[]="[srv.em9305]File size: %ld bytes";
static const char alloc_error[]="Failed to allocate memory for file buffer, size: %d";
static const char alloc_compact[]="[srv.em9305]Failed to allocate memory for file buffer, size: %d";
static const char read_error[]="Failed to read file, read %zu bytes, expected %ld";
static const char read_compact[]="[srv.em9305]Failed to read file, read %zu bytes, expected %ld";
static const char header_error[]="Failed to read BLE firmware header";
static const char header_compact[]="[srv.em9305]Failed to read BLE firmware header";
static const char header_info[]="BLE firmware header: version=0x%08X, total_length=%d, record_count=%d, erase_pages_size=%d";
static const char header_info_compact[]="[srv.em9305]BLE firmware header: version=0x%08X, total_length=%d, record_count=%d, erase_pages_size=%d";
static const char records_error[]="Failed to read image records";
static const char records_compact[]="[srv.em9305]Failed to read image records";
static const char page_info[]="NvmPage count: %d";
static const char page_info_compact[]="[srv.em9305]NvmPage count: %d";
static const char data_error[]="Failed to read image data";
static const char data_compact[]="[srv.em9305]Failed to read image data";
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
static void close_file(void) {
    if(W(0x20074948u)!=0u) {
        (void)audio_file_close((void *)(uintptr_t)W(0x20074948u));
        W(0x20074948u)=0u;
    }
}
static void free_buffer(void) {
    audio_file_heap_free((void *)(uintptr_t)W(0x2007494cu));
    W(0x2007494cu)=0u;
}
static void error0(uint32_t line,const char *message,const char *compact) {
    if(audio_log_flags()&2u)audio_log_extended(1u,module,source_path,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,compact,compact);
}
uint32_t audio_ble_radio_image_load_52f442(void) {
    const char *mode=audio_ble_radio_file_mode_52f3a0(1u);
    void *file=audio_file_open(path,mode);
    W(0x20074948u)=(uint32_t)(uintptr_t)file;
    if(file==0) {
        if(audio_log_flags()&2u)audio_log_extended(1u,module,source_path,function,0x96u,open_error,path,-1);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04800000u,open_compact,open_compact,path,-1);
        return 0u;
    }
    int32_t size=audio_ble_radio_file_size_52f3f8(file);
    if(size<0) {
        error0(0x9du,size_error,size_compact);
        close_file();return 0u;
    }
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,0xa2u,size_info,size);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,size_info_compact,size_info_compact,size);
    uint32_t rounded=((uint32_t)size+3u)&~3u;
    W(0x20074950u)=rounded;
    uint8_t *buffer=(uint8_t *)file_heap_allocate(rounded);
    W(0x2007494cu)=(uint32_t)(uintptr_t)buffer;
    if(buffer==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source_path,function,0xa8u,alloc_error,rounded);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04400000u,alloc_compact,alloc_compact,rounded);
        close_file();return 0u;
    }
    __builtin_memset(buffer,0,rounded);
    uint32_t n=audio_file_read(buffer,1u,(uint32_t)size,file);
    if(n!=(uint32_t)size) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source_path,function,0xb3u,read_error,n,size);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04800000u,read_compact,read_compact,n,size);
        free_buffer();close_file();return 0u;
    }
    close_file();
    uint32_t header[4];
    if(audio_ble_radio_header_copy_52f86a(buffer,header)==0u) {
        error0(0xbeu,header_error,header_compact);
        free_buffer();return 0u;
    }
    W(0x20074954u)=header[0];
    W(0x20074970u)=header[1];
    W(0x20074968u)=header[3];
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,0xcau,header_info,
                           header[0],header[1],header[2],header[3]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x11000000u,header_info_compact,header_info_compact,
                                    header[0],header[1],header[2],header[3]);
    if(audio_ble_radio_records_52f87c(buffer+16u,header[2])==0u) {
        error0(0xceu,records_error,records_compact);
        free_buffer();return 0u;
    }
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,0xd7u,page_info,header[3]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,page_info_compact,page_info_compact,header[3]);
    if(header[3]!=0u)
        W(0x2007496cu)=(uint32_t)(uintptr_t)(buffer+16u+header[2]*12u);
    if(audio_ble_radio_record_data_52f99e(buffer,header[2])==0u) {
        error0(0xe1u,data_error,data_compact);
        free_buffer();return 0u;
    }
    return 1u;
}

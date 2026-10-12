/* Native 0x52fcfc validates the on-flash EM9305 firmware header. Only its
 * first word is copied to the output; live file handle cell remains runtime. */
#include <stdint.h>
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char *audio_ble_radio_file_mode_52f3a0(uint32_t);
extern int32_t audio_ble_radio_file_size_52f3f8(void *);
extern void *audio_file_open(const char *,const char *);
extern uint32_t audio_file_read(void *,uint32_t,uint32_t,void *);
extern int32_t audio_file_close(void *);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="SVC_Em9305FwReadVersion";
static const char firmware_path[]="firmware/ble_em9305.bin";
static const char null_message[]="Invalid parameter: version is NULL";
static const char null_compact[]="[srv.em9305]Invalid parameter: version is NULL";
static const char open_message[]="Failed to open file: %s, error: %d";
static const char open_compact[]="[srv.em9305]Failed to open file: %s, error: %d";
static const char get_size_message[]="Failed to get file size";
static const char get_size_compact[]="[srv.em9305]Failed to get file size";
static const char size_message[]="File size too small: %ld bytes, need at least %d bytes";
static const char size_compact[]="[srv.em9305]File size too small: %ld bytes, need at least %d bytes";
static const char read_message[]="Failed to read header, read %zu bytes, expected %d";
static const char read_compact[]="[srv.em9305]Failed to read header, read %zu bytes, expected %d";
static const char success_message[]=
    "Header read successfully: version=0x%08X, total_length=%d, record_count=%d, erase_pages_size=%d";
static const char success_compact[]=
    "[srv.em9305]Header read successfully: version=0x%08X, total_length=%d, record_count=%d, erase_pages_size=%d";
static volatile uint32_t *const handle_cell=(volatile uint32_t *)(uintptr_t)0x20074948u;
static void close_current(void) {
    void *file=(void *)(uintptr_t)*handle_cell;
    if(file!=0) {(void)audio_file_close(file);*handle_cell=0u;}
}
static void error_log(uint32_t line,const char *message,const char *compact,
                      uint32_t a,uint32_t b) {
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source_path,function,line,message,a,b);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((a||b)?0x04800000u:0x04000000u,
                                    compact,compact,a,b);
}
uint32_t audio_ble_hci_radio_validate_52fcfc(uint32_t *version) {
    if(version==0) {
        error_log(0x180u,null_message,null_compact,0u,0u);
        return 0u;
    }
    const char *mode=audio_ble_radio_file_mode_52f3a0(1u);
    void *file=audio_file_open(firmware_path,mode);
    *handle_cell=(uint32_t)(uintptr_t)file;
    if(file==0) {
        error_log(0x187u,open_message,open_compact,
                  (uint32_t)(uintptr_t)firmware_path,(uint32_t)-1);
        return 0u;
    }
    int32_t size=audio_ble_radio_file_size_52f3f8(file);
    if(size<0) {
        error_log(0x18eu,get_size_message,get_size_compact,0u,0u);
        close_current();return 0u;
    }
    if((uint32_t)size<16u) {
        error_log(0x195u,size_message,size_compact,(uint32_t)size,16u);
        close_current();return 0u;
    }
    uint32_t header[4];
    uint32_t n=audio_file_read(header,1u,16u,file);
    if(n!=16u) {
        error_log(0x19eu,read_message,read_compact,n,16u);
        close_current();
        return 0u;
    }
    close_current();
    *version=header[0];
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,0x1a8u,
                           success_message,header[0],header[1],header[2],header[3]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x11000000u,success_compact,success_compact,
                                    header[0],header[1],header[2],header[3]);
    return 1u;
}

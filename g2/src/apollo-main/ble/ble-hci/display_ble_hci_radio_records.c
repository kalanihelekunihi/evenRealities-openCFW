/* Native 0x52f87c: decode up to four 12-byte EM9305 image records into
 * four 16-byte live descriptors.  The fifth descriptor is never accepted. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="_readImageRecords";
static const char excess[]="Record count %d exceeds maximum %d";
static const char excess_compact[]="[srv.em9305]Record count %d exceeds maximum %d";
static const char record[]="Em9305ImageRecord_t[%d]: offset=0x%08X, length=%d, address=0x%08X";
static const char record_compact[]="[srv.em9305]Em9305ImageRecord_t[%d]: offset=0x%08X, length=%d, address=0x%08X";
static volatile uint8_t *const descriptors=(volatile uint8_t *)(uintptr_t)0x200731f0u;
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void put(volatile uint8_t *p,uint32_t v) {
    for(uint32_t i=0;i<4u;i++)p[i]=(uint8_t)(v>>(i*8u));
}
uint32_t audio_ble_radio_records_52f87c(const void *input,uint32_t count) {
    if(count>=5u) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source_path,function,0xf9u,excess,count,4u);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04800000u,excess_compact,excess_compact,count,4u);
        return 0u;
    }
    const uint8_t *src=(const uint8_t *)input;
    for(uint32_t i=0;i<count;i++) {
        volatile uint8_t *dst=descriptors+i*16u;
        uint32_t a=word(src+i*12u),b=word(src+i*12u+4u),c=word(src+i*12u+8u);
        put(dst,a);put(dst+4u,b);put(dst+8u,c);put(dst+12u,0u);
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_path,function,0x108u,record,i,a,b,c);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x11000000u,record_compact,record_compact,i,a,b,c);
    }
    for(uint32_t i=count;i<4u;i++) {
        volatile uint8_t *dst=descriptors+i*16u;
        for(uint32_t j=0;j<16u;j++)dst[j]=0u;
    }
    return 1u;
}

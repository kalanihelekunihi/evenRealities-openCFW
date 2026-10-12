/* Native 0x52f3a0 mode strings and 0x52f3f8 seek/tell size helper. */
#include <stdint.h>
extern int32_t audio_file_tell(void *);
extern int32_t audio_file_seek(void *,int32_t,uint32_t);
static const char mode_wplus[]="w+",mode_aplus[]="a+",mode_rplus[]="r+";
static const char mode_a[]="a",mode_w[]="w",mode_r[]="r";
const char *audio_ble_radio_file_mode_52f3a0(uint32_t flags) {
    if((flags&3u)==0u) {
        if((flags<<30u)&0x80000000u) {
            if((flags<<20u)&0x80000000u) return mode_a;
            if((flags<<23u)&0x80000000u)
                return ((flags<<21u)&0x80000000u)?mode_w:mode_a;
            return mode_w;
        }
        return mode_r;
    }
    if((flags<<23u)&0x80000000u)
        return ((flags<<21u)&0x80000000u)?mode_wplus:mode_aplus;
    return mode_rplus;
}
int32_t audio_ble_radio_file_size_52f3f8(void *file) {
    if(file==0) return -1;
    int32_t at=audio_file_tell(file);
    if(at<0) return -1;
    if(audio_file_seek(file,0,2u)!=0) return -1;
    int32_t size=audio_file_tell(file);
    (void)audio_file_seek(file,at,0u);
    return size;
}

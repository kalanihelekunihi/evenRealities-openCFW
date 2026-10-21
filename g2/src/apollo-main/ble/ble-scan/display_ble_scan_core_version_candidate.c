/* Bounded source reduction of IAR scan engine 0x4d1638 for the authenticated
 * BLE version format "%d.%d.%d". Other grammar is the real unresolved engine
 * contract, rather than an invented result. This is not the full scan body. */
#include <stdint.h>

typedef int32_t (*scan_get_fn)(void *,uint32_t,uint32_t);
extern int32_t audio_ble_scan_core_full(scan_get_fn,void *,const char *,
                                        uint32_t **,uint32_t);

static int version_format(const char *f) {
    static const char grammar[]="%d.%d.%d";
    for(unsigned i=0;i<sizeof(grammar);i++)if(f[i]!=grammar[i])return 0;
    return 1;
}

static int32_t read_decimal(scan_get_fn get,void *context,int32_t *result) {
    int32_t c=get(context,0,1),negative=0,any=0;
    if(c=='+'||c=='-') { negative=(c=='-');c=get(context,0,1); }
    uint32_t value=0;
    while(c>='0'&&c<='9') {
        any=1;
        value=value*10u+(uint32_t)(c-'0');
        c=get(context,0,1);
    }
    get(context,(uint32_t)c,0);
    if(!any)return c==-1?-1:0;
    *result=negative?-(int32_t)value:(int32_t)value;
    return 1;
}

int32_t audio_ble_scan_core(scan_get_fn get,void *context,const char *format,
                             uint32_t **arguments,uint32_t mode) {
    if(mode || !version_format(format) || !(*arguments)[0] ||
       !(*arguments)[1] || !(*arguments)[2])
        return audio_ble_scan_core_full(get,context,format,arguments,mode);
    int32_t count=0;
    for(unsigned field=0;field<3;field++) {
        int32_t value=0,status=read_decimal(get,context,&value);
        if(status!=1)return status<0 && count==0?-1:count;
        int32_t *destination=(int32_t *)(uintptr_t)*(*arguments)++;
        *destination=value;
        count++;
        if(field<2) {
            int32_t c=get(context,0,1);
            if(c!='.') { get(context,(uint32_t)c,0);return count; }
        }
    }
    return count;
}

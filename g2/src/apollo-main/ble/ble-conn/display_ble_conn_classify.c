/* Native _isConnParamsFast 0x476db8 and _isConnParamsSlow 0x476fe2. */
#include <stdint.h>
static const uint16_t slow_profile[6]={0u,0u,72u,84u,4u,600u}; /* ROM 0x784ea0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.param";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_connect_params.c";
static const char fast_function[]="_isConnParamsFast";
static const char slow_function[]="_isConnParamsSlow";
static const char profile[]="  new:%d,%d(%d)  slow:%d,%d(%d)";
static const char profile_short[]="[ble.param]  new:%d,%d(%d)  slow:%d,%d(%d)";
static const char interval[]="connInterval = %d(%d) ms";
static const char interval_short[]="[ble.param]connInterval = %d(%d) ms";
static const char latency[]="connLatency = %d";
static const char latency_short[]="[ble.param]connLatency = %d";
static const char timeout[]="supTimeout = %d ms";
static const char timeout_short[]="[ble.param]supTimeout = %d ms";
static const char is_fast[]="is fast mode";
static const char is_fast_short[]="[ble.param]is fast mode";
static const char is_slow[]="is slow mode";
static const char is_slow_short[]="[ble.param]is slow mode";
static uint16_t half(const uint8_t *p,uint32_t n) {return (uint16_t)p[n]|(uint16_t)((uint16_t)p[n+1u]<<8);}
static void log_one(const char *function,uint32_t line,uint32_t prefix,
                    const char *text,const char *short_text,uint32_t value) {
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4u,module,path,function,line,text,value);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(prefix,short_text,short_text,value);
}
static void log_plain(const char *function,uint32_t line,const char *text,const char *short_text) {
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4u,module,path,function,line,text);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_text,short_text);
}
static uint32_t classify(const uint8_t *params,uint32_t threshold,uint32_t slow) {
    const char *function=slow?slow_function:fast_function;
    uint32_t base=slow?0xd7u:0xc6u;
    uint32_t interval_value=half(params,24u),latency_value=half(params,26u),timeout_value=half(params,28u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,base,profile,interval_value,interval_value,
                           latency_value,slow_profile[2],slow_profile[3],slow_profile[4]);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x11800000u,profile_short,profile_short,
                                    interval_value,interval_value,latency_value,
                                    slow_profile[2],slow_profile[3],slow_profile[4]);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,base+3u,interval,
                           (interval_value*1250u)/1000u,24u);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,interval_short,interval_short,
                                    (interval_value*1250u)/1000u,24u);
    log_one(function,base+4u,0x10400000u,latency,latency_short,latency_value);
    log_one(function,base+5u,0x10400000u,timeout,timeout_short,(timeout_value*10000u)/1000u);
    if(interval_value<threshold) {
        log_plain(function,slow?0xe2u:0xceu,is_fast,is_fast_short);
        return 0xa3u;
    }
    log_plain(function,slow?0xdfu:0xd1u,is_slow,is_slow_short);
    return 0xa4u;
}
/* Stock 0x476DB8 (_isConnParamsFast) */
uint32_t audio_ble_is_conn_params_fast(const void *params) {
    return classify((const uint8_t *)params,25u,0u);
}
/* Stock 0x476FE2 (_isConnParamsSlow) */
uint32_t audio_ble_is_conn_params_slow(const void *params) {
    return classify((const uint8_t *)params,72u,1u);
}

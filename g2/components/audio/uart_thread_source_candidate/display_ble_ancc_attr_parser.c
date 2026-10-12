/* Native _anccAttrHandler 0x4bf228. Product ANCC/cache RAM remains typed.
 * This preserves the native two-stage parser and its exact callback order. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* 0x200695c8 */
extern uint8_t audio_ble_ancc_cache[]; /* 0x2006ddd4 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern uint8_t audio_ble_ancc_whitelist_type_4d67b8(const uint8_t *);
extern uint32_t audio_ble_ancc_not_whitelisted_4d71bc(const uint8_t *,const uint8_t *);
extern void audio_ble_ancc_send_complete_4bedac(const uint8_t *,uint32_t);
extern void audio_ble_ancc_reset_state_machine(void);
extern void audio_ble_ancc_attr_callback_4bf06c(uint8_t *);
extern void audio_ble_ancc_perform_action_4beb82(uint32_t,uint32_t,uint32_t);
static const char module[]="ble.ancc";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
static const char fn[]="_anccAttrHandler";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void wr32(uint8_t *p,uint32_t v){for(uint32_t i=0;i<4u;++i)p[i]=(uint8_t)(v>>(i*8u));}
static void log0(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact);
}
static void log1(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact,uint32_t value){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain,value);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,value);
}
static void log2(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact,
                 const uint8_t *a,const uint8_t *b){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain,a,b);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,a,b);
}

uint32_t audio_ble_ancc_attr_handler_4bf228(const uint8_t *input,uint16_t length){
    uint8_t *s=audio_ble_ancc_state;
    uint8_t *cache=audio_ble_ancc_cache;
    uint8_t state=s[10u];
    if(state==0u){
        uint8_t consumed=0u;
        s[0x16u]=input[0u];
        if(s[0x16u]==0u){
            wr32(s+0x18u,rd32(input+1u));consumed=4u;
        }else if(s[0x16u]==1u){
            while(input[(uint8_t)(consumed+1u)]!=0u){
                s[0x31cu+consumed]=input[(uint8_t)(consumed+1u)];
                consumed=(uint8_t)(consumed+1u);
            }
            s[0x31du+consumed]=0u;
            if(input[(uint8_t)(consumed+2u)]==0u){
                uint16_t name_len=rd16(input+(uint8_t)(consumed+3u));
                audio_uart_buffer_zero(cache+0x48u,0x20u,0u);
                audio_queue_copy_bytes(cache+0x48u,input+(uint8_t)(consumed+5u),name_len);
                cache[0x48u+name_len]=0u;
                uint8_t type=(cache[5u]==0u||cache[5u]==1u) ?
                    audio_ble_ancc_whitelist_type_4d67b8(cache+8u) : 2u;
                static const char type_msg[]="appType is %d";
                static const char type_short[]="[ble.ancc]appType is %d";
                log1(4u,0x256u,type_msg,0x10400000u,type_short,type);
                if(type==1u){
                    static const char msg[]="ANCS app(%s) name(%s) not on whitelist, ignore!!!!";
                    static const char short_msg[]="[ble.ancc]ANCS app(%s) name(%s) not on whitelist, ignore!!!!";
                    log2(3u,0x263u,msg,0x0c800000u,short_msg,cache+8u,cache+0x48u);
                    audio_ble_ancc_not_whitelisted_4d71bc(cache+8u,cache+0x48u);
                    audio_uart_buffer_zero(cache,0x2fcu,0u);
                    audio_ble_ancc_reset_state_machine();return 0u;
                }
                if(type==2u||type==3u){
                    if(type==3u){
                        static const char msg[]="ANCS app(%s) name(%s) is on whitelist sched";
                        static const char short_msg[]="[ble.ancc]ANCS app(%s) name(%s) is on whitelist sched";
                        log2(3u,0x25eu,msg,0x0c800000u,short_msg,cache+8u,cache+0x48u);
                    }else{
                        static const char msg[]="ANCS app(%s) name(%s) is on whitelist notify";
                        static const char short_msg[]="[ble.ancc]ANCS app(%s) name(%s) is on whitelist notify";
                        log2(3u,0x259u,msg,0x0c800000u,short_msg,cache+8u,cache+0x48u);
                    }
                    audio_ble_ancc_send_complete_4bedac(cache,0x2fcu);
                    audio_uart_buffer_zero(cache,0x2fcu,0u);
                    static const char reset[]="Resetting state machine after app attribute processing";
                    static const char reset_short[]="[ble.ancc]Resetting state machine after app attribute processing";
                    log0(4u,0x279u,reset,0x10000000u,reset_short);
                    audio_ble_ancc_reset_state_machine();return 0u;
                }
                static const char unknown[]="unknown appType, ignore!!!!";
                static const char unknown_short[]="[ble.ancc]unknown appType, ignore!!!!";
                log0(3u,0x26cu,unknown,0x0c800000u,unknown_short);
                audio_ble_ancc_reset_state_machine();return 0u;
            }
        }else return 0u;
        wr16(s+0xeu,(uint16_t)(rd16(s+0xeu)+(uint16_t)consumed+1u));
        s[10u]=1u;s[0x12u]=0u;wr16(s+0x14u,0u);
        uint16_t n=length<0x201u?length:0u;
        audio_uart_buffer_zero(s+0x35cu,0x200u,0u);
        wr16(s+0x0cu,0u);
        for(uint16_t i=0;i<n;++i){s[0x35cu+rd16(s+0x0cu)]=input[i];wr16(s+0x0cu,(uint16_t)(rd16(s+0x0cu)+1u));}
    }else if(state==2u){
        if((uint32_t)rd16(s+0x0cu)+(uint32_t)length>0x200u){
            s[10u]=0u;wr16(s+0xeu,0u);wr16(s+0x0cu,0u);return 0u;
        }
        for(uint16_t i=0;i<length;++i){s[0x35cu+rd16(s+0x0cu)]=input[i];wr16(s+0x0cu,(uint16_t)(rd16(s+0x0cu)+1u));}
        s[10u]=1u;return 1u;
    }else if(state>2u)return 0u;
    uint16_t count=rd16(s+0x0cu),offset=rd16(s+0xeu);
    if((int32_t)((uint32_t)count-(uint32_t)offset)<3){s[10u]=2u;return 0u;}
    s[0x12u]=s[0x35cu+offset];
    uint16_t attr_len=rd16(s+0x35cu+offset+1u);wr16(s+0x10u,attr_len);
    if((int32_t)(((uint32_t)count-(uint32_t)offset)-3u)<(int32_t)(uint32_t)attr_len){s[10u]=2u;return 0u;}
    wr16(s+0x14u,(uint16_t)(rd16(s+0x14u)+1u));
    wr16(s+0xeu,(uint16_t)(offset+3u));
    audio_ble_ancc_attr_callback_4bf06c(s+8u);
    wr16(s+0xeu,(uint16_t)(rd16(s+0xeu)+rd16(s+0x10u)));
    if(rd16(s+0x14u)<8u)return 1u;
    static const char done[]="Notification attributes processing completed, resetting state machine";
    static const char done_short[]="[ble.ancc]Notification attributes processing completed, resetting state machine";
    log0(4u,0x2bdu,done,0x10000000u,done_short);
    audio_ble_ancc_reset_state_machine();
    audio_ble_ancc_perform_action_4beb82(rd32(s+4u),rd32(s+0x18u),1u);
    return 0u;
}

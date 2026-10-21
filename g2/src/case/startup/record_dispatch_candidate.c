#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Source-owned control-flow reduction of stock parser 0x08001e94.
 * Product messages, the 0x5a copy extent, and downstream transport remain
 * explicit contracts. Addresses below are authenticated RAM literal targets.
 */
#include <stdint.h>
struct case_record_prefix { uint32_t payload,length,command,calculated_crc,received_crc; };
extern uint32_t case_record_scan_prefix(struct case_record_prefix *out);
extern void case_record_log(uint32_t message,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f);
extern void case_record_hex_log(const uint8_t *bytes,uint32_t length);
extern void case_record_forward(const uint8_t *bytes,uint32_t length);
static volatile uint8_t *const input=(volatile uint8_t *)(uintptr_t)0x20000664u;
static volatile uint8_t *const flags=(volatile uint8_t *)(uintptr_t)0x200000f4u;
static volatile uint8_t *const state=(volatile uint8_t *)(uintptr_t)0x2000089cu;
static volatile uint8_t *const seq=(volatile uint8_t *)(uintptr_t)0x200000b4u;
static uint8_t quiet(void){return *(volatile uint8_t *)(uintptr_t)0x200000bfu;}
static void record_clear(void){for(uint32_t i=0;i<0x118u;i++)input[i]=0u;}
static uint32_t read32be(const volatile uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void write32(volatile uint8_t *p,uint32_t v){for(uint32_t i=0;i<4u;i++)p[i]=(uint8_t)(v>>(i*8u));}
static void write16(volatile uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void logline(uint32_t message,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){case_record_log(message,a,b,c,d,e,0);case_record_log(CASE_STRING_ADDR(08002278),0,0,0,0,0,0);}
static uint32_t charging(uint32_t side,const volatile uint8_t *p,uint8_t logs_quiet){
    if(p[3]==6u){
        uint16_t voltage=(uint16_t)(((uint16_t)p[5]<<8)|p[6]);
        uint32_t direction=p[4]&1u;
        int32_t current=p[8] ? -(int32_t)p[9]:(int32_t)p[9];
        uint8_t permits=(uint8_t)(direction!=0u || current<=0);
        if(side==0u){
            uint8_t old=seq[1];seq[1]=(uint8_t)(old*2u);
            if(permits || ((volatile uint32_t *)(uintptr_t)state)[17]<10u)seq[1]=(uint8_t)(old*2u+1u);
            state[0x30]=1u;state[0x2c]=(seq[1]&7u)!=0u;
            uint8_t enabled=(p[4]&1u)!=0u;
            if(state[0x2d]||state[-13])enabled=p[7]>=0x62u;
            state[0x2d]=enabled;
            if(flags[0] && !flags[1])state[0x2d]=0u;
            state[-13]=0u;state[0x2e]=p[7];write16(state+0x32,voltage);
            if(!logs_quiet)logline(CASE_STRING_ADDR(08002320),state[0x2c],direction,voltage,p[7],(uint32_t)current);
        }else{
            uint8_t old=seq[0];seq[0]=(uint8_t)(old*2u);
            if(permits || ((volatile uint32_t *)(uintptr_t)state)[10]<10u)seq[0]=(uint8_t)(old*2u+1u);
            state[0x14]=1u;state[0x10]=(seq[0]&7u)!=0u;
            if(!state[0x11] && state[-14] && p[7]>0x61u && !logs_quiet)logline((CASE_STRING_ADDR(080022bf)+1u),0,0,0,0,0);
            state[0x11]=(state[0x11] || state[-14]) ? (p[7]>=0x62u) : (uint8_t)direction;
            if(flags[0] && !flags[1])state[0x11]=0u;
            state[-14]=0u;state[0x12]=p[7];write16(state+0x16,voltage);
            if(!logs_quiet)logline((CASE_STRING_ADDR(080022eb)+1u),state[0x10],direction,voltage,p[7],(uint32_t)current);
        }
        return 0x13u;
    }else if(p[3]==1u && p[4]==1u){
        if(!logs_quiet)logline(side?CASE_STRING_ADDR(08002354):CASE_STRING_ADDR(08002378),0,0,0,0,0);
        return 0x13u;
    }
    return 0xffu;
}
uint32_t case_record_dispatch_1e94(uint32_t side){
    struct case_record_prefix prefix;
    uint32_t scan=case_record_scan_prefix(&prefix);
    if(scan==0u || scan==2u)return 0xffu;
    const volatile uint8_t *p=(const volatile uint8_t *)(uintptr_t)prefix.payload;
    uint8_t q=quiet();
    if(scan==3u){
        if(!q){logline((CASE_STRING_ADDR(0800225b)+1u),0,0,0,0,0);if(!quiet())case_record_log(CASE_STRING_ADDR(0800227c),prefix.calculated_crc,prefix.received_crc,prefix.length,0,0,0);}
        case_record_hex_log((const uint8_t *)(uintptr_t)p,prefix.length);
        return 0xffu;
    }
    uint32_t result=0xffu;
    switch(prefix.command){
    case 0x46u:flags[side?2u:3u]=(p[4]!=0u);result=0x46u;break;
    case 0x58u:
        if(p[3]==0x20u){
            if(p[9]==2u && p[10]>0x39u){
                state[-4]=2u;state[-3]=p[10];write32(state,read32be(p+12));write32(state+4,read32be(p+16));state[-7]=3u;state[-6]=0u;
                if(!q){case_record_log(CASE_STRING_ADDR(0800d648),2u,0x39u,p[9],p[10],read32be(p+12),read32be(p+16));case_record_log(CASE_STRING_ADDR(08002278),0,0,0,0,0,0);}
            }else if(!q)logline(CASE_STRING_ADDR(080023bc),2u,0x39u,p[9],p[10],0);
        }else if(!q)logline(CASE_STRING_ADDR(0800239c),p[3],0,0,0,0);
        break;
    case 0x59u:if(p[3]==1u && p[4]==0u)result=0x59u;break;
    case 0x5au:
        if((p[3]&7u)==1u){uint8_t sum=0u;uint32_t n=(uint32_t)p[3]-1u;
            for(uint32_t i=0;i<n;i++)sum=(uint8_t)(sum+p[i+4u]);
            if(p[n+4u]==sum){for(uint32_t i=0;i<p[3];i++)((volatile uint8_t *)(uintptr_t)0x2000077cu)[i]=p[i+4u];write32(state+8,0x2000077cu);state[12]=(uint8_t)n;}
        }break;
    case 0x5bu:if(p[3]==1u && p[4]==0u)result=0x5bu;break;
    case 8u:result=8u;break;
    case 7u:result=7u;break;
    case 0u:break;
    case 0x13u:result=charging(side,p,q);break;
    case 0x3eu:if(p[4]==0u || p[4]==4u)result=0x3eu;break;
    default:case_record_forward((const uint8_t *)(uintptr_t)p,prefix.length);break;
    }
    record_clear();return result;
}

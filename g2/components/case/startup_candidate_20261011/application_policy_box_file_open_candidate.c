#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08001574 OTA box file open, bank preparation and chunk fetch.
 * Child flash/file operations retain separate source contracts.
 */
#include <stdint.h>
extern void case_policy_wait(uint32_t); /* 0xa7b0 */
extern uint32_t case_policy_log(uint32_t); /* 0x9170 */
extern void case_policy_ota_checksum(uint8_t *,uint32_t); /* 0x9b70 */
extern uint32_t case_policy_ota_transmit(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x2744 */
extern uint32_t case_policy_parse_probe(uint32_t); /* 0x1e94 */
extern uint32_t case_policy_box_running_bank(void); /* 0x2f46 */
extern uint32_t case_policy_box_erase_bank(void); /* 0x2d48 */
extern uint32_t case_policy_box_copy_sn(void); /* 0x2b4c */
extern uint32_t case_policy_box_apply_file(void); /* 0x2cc0 */
extern uint32_t case_policy_box_write_chunk(uint32_t,uint32_t,uint32_t); /* 0x2e04 */
static volatile uint8_t *const box_lock=(volatile uint8_t *)(uintptr_t)0x200000bcu;
static volatile uint8_t *const quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
static volatile uint8_t *const box=(volatile uint8_t *)(uintptr_t)0x2000087cu;
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void logline(uint32_t a){(void)case_policy_log(a);(void)case_policy_log(CASE_STRING_ADDR(08001794));}
uint32_t case_policy_box_file_open(void)
{
    while(*box_lock!=0u)case_policy_wait(100u);
    *box_lock=1u;
    if(*quiet==0u)logline(CASE_STRING_ADDR(08001778));
    uint8_t query[8]={0x59u,0u,0u,0u,0u,0u,0u,0u};
    case_policy_ota_checksum(query,5u);
    (void)case_policy_ota_transmit(1u,query,5u,1u);
    *box_lock=0u;
    if(case_policy_parse_probe(1u)!=0x59u){if(*quiet==0u)logline(CASE_STRING_ADDR(080017a0));return 0u;}
    case_policy_wait(100u);
    if(*quiet==0u)logline(CASE_STRING_ADDR(080017bc));
    uint32_t bank=case_policy_box_running_bank();
    box[0x18u]=(uint8_t)bank;
    if(bank==0u){if(*quiet==0u)logline(CASE_STRING_ADDR(080017dc));return 0u;}
    if(*quiet==0u)logline(CASE_STRING_ADDR(08001800));
    if(case_policy_box_erase_bank()==0u){if(*quiet==0u)logline(CASE_STRING_ADDR(0800181c));return 0u;}
    if(*quiet==0u)logline(CASE_STRING_ADDR(08001838));
    if(case_policy_box_copy_sn()==0u){if(*quiet==0u)logline(CASE_STRING_ADDR(08001868));return 0u;}
    if(*quiet==0u){logline(CASE_STRING_ADDR(0800184c));logline(CASE_STRING_ADDR(08001884));}
    *box_lock=1u;
    uint32_t offset=0u;
    uint32_t retries=0u;
    uint32_t attempts=0u;
    for(;;){
        uint32_t size=rd32((uint32_t)(uintptr_t)box+0x20u);
        if(size<=offset){
            if(*quiet==0u)logline(CASE_STRING_ADDR(080018b0));
            *box_lock=0u;
            return case_policy_box_apply_file();
        }
        uint32_t length=size-offset<240u?size-offset:240u;
        wr32((uint32_t)(uintptr_t)box+0x28u,0u);
        box[0x2cu]=0u;
        uint8_t packet[12]={0x5au,0u,0u,0x05u,0u,0u,0u,0u,0u,0u,0u,0u};
        packet[8]=(uint8_t)length;
        packet[4]=(uint8_t)offset;packet[5]=(uint8_t)(offset>>8);
        packet[6]=(uint8_t)(offset>>16);packet[7]=(uint8_t)(offset>>24);
        case_policy_ota_checksum(packet,10u);
        (void)case_policy_ota_transmit(1u,packet,10u,1u);
        (void)case_policy_parse_probe(1u);
        if(rd32((uint32_t)(uintptr_t)box+0x28u)!=0u && box[0x2cu]!=0u && case_policy_box_write_chunk(offset,rd32((uint32_t)(uintptr_t)box+0x28u),box[0x2cu])!=0u){
            offset+=box[0x2cu];attempts=0u;
        }else{
            if(*quiet==0u)(void)case_policy_log(rd32((uint32_t)(uintptr_t)box+0x28u)==0u || box[0x2cu]==0u?CASE_STRING_ADDR(080018ac):CASE_STRING_ADDR(080018a8));
            if(rd32((uint32_t)(uintptr_t)box+0x28u)==0u || box[0x2cu]==0u)retries=(retries+1u)&0xffffu;
            uint32_t old=attempts;attempts=(attempts+1u)&0xffu;
            if(old==10u){*box_lock=0u;return 0u;}
        }
        case_policy_wait(20u);
    }
}

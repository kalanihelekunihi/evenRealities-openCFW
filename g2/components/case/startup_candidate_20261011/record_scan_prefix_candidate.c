/* SPDX-License-Identifier: MIT
 * Source-owned parser prefix of stock 0x08001e94. The command dispatch,
 * diagnostics and payload effects remain an explicit whole-body gap.
 */
#include <stdint.h>
struct case_record_prefix {
    uint32_t payload;
    uint32_t length;
    uint32_t command;
    uint32_t calculated_crc;
    uint32_t received_crc;
};
/* 0=no header, 1=valid, 2=bad CRC for 0x5a, 3=bad CRC for other command. */
uint32_t case_record_scan_prefix(struct case_record_prefix *out)
{
    const volatile uint8_t *buffer=(const volatile uint8_t *)(uintptr_t)0x20000664u;
    uint32_t payload=0u,length=0u,checksum=0u;
    for(uint32_t i=0u;i<4u;i++){
        if(buffer[i]==0x5au && buffer[i+1u]==0xa5u && buffer[i+2u]==0xffu){
            payload=0x20000664u+i+4u;
            length=buffer[i+3u];
            checksum=(length-2u)&0xffu;
        }
    }
    if(payload==0u)return 0u;
    const volatile uint8_t *bytes=(const volatile uint8_t *)(uintptr_t)payload;
    for(uint32_t i=0u;i<length;i++)checksum=(checksum+bytes[i])&0xffu;
    uint32_t received=bytes[length],command=bytes[0];
    if(out!=0){
        out->payload=payload;out->length=length;out->command=command;
        out->calculated_crc=checksum;out->received_crc=received;
    }
    if(checksum==received)return 1u;
    return command==0x5au?2u:3u;
}

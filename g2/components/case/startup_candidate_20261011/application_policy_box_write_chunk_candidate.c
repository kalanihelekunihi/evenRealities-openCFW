/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002e04 write a received OTA chunk in 8-byte flash units.
 */
#include <stdint.h>
extern void case_boot_option_prepare(void); /* 0x4bf4 */
extern uint32_t case_boot_option_write(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x4b94 */
extern void case_boot_option_commit_c(void); /* 0x4b20 */
extern uint32_t case_policy_log(uint32_t); /* 0x9170 */
uint32_t case_policy_box_write_chunk(uint32_t offset,uint32_t data,uint32_t count)
{
    volatile const uint8_t *quiet=(volatile const uint8_t *)(uintptr_t)0x200000bfu;
    if(*quiet==0u)(void)case_policy_log(0x08002eb4u);
    if(count==0u)return 1u;
    case_boot_option_prepare();
    volatile const uint8_t *bytes=(volatile const uint8_t *)(uintptr_t)data;
    uint32_t blocks=(count+7u)>>3;
    for(uint32_t i=0u;i<blocks;++i){
        uint32_t high=0u,low=0u;
        for(uint32_t j=8u;j!=0u;--j){
            uint32_t index=i*8u+j-1u;
            uint32_t b=(index<count)?bytes[index]:0xffu;
            high=(high<<8)|(low>>24);
            low=(low<<8)|b;
        }
        if(case_boot_option_write(1u,0x08040000u+offset+i*8u,low,high)!=0u){
            if(*quiet==0u){(void)case_policy_log(0x08002ebcu);(void)case_policy_log(0x08002ed8u);}
            case_boot_option_commit_c();return 0u;
        }
    }
    case_boot_option_commit_c();
    return 1u;
}

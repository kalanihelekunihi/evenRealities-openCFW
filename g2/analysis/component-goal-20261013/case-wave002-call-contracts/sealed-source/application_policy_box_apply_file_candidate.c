#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002cc0 image checksum against OTA file metadata.
 */
#include <stdint.h>
uint32_t case_policy_box_apply_file(void)
{
    volatile const uint8_t *box=(volatile const uint8_t *)(uintptr_t)0x2000087cu;
    volatile const uint8_t *flash=(volatile const uint8_t *)(uintptr_t)0x08040000u;
    uint32_t size=*(volatile const uint32_t *)(uintptr_t)(0x2000087cu+0x20u);
    uint32_t total=0u;
    for(uint32_t offset=0u;offset<size;offset+=4u){
        uint32_t word=((uint32_t)flash[offset]<<24)|((uint32_t)flash[offset+1u]<<16)|
                      ((uint32_t)flash[offset+2u]<<8)|flash[offset+3u];
        total+=word;
    }
    uint32_t expected=*(volatile const uint32_t *)(uintptr_t)(0x2000087cu+0x24u);
    if(*(volatile const uint8_t *)(uintptr_t)0x200000bfu==0u){
        (void)case_policy_log(CASE_STRING_ADDR(08002d1c),total,expected);
        (void)case_policy_log(CASE_STRING_ADDR(08002d44));
    }
    (void)box;
    return total==expected?1u:0u;
}

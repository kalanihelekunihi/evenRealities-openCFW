/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002f60/0x08002f88 identity readers: reverse each 8-byte
 * flash word group into the packet order used by the OTA serial copier.
 */
#include <stdint.h>
void case_policy_box_read_serial(uint8_t *out)
{
    volatile const uint8_t *src=(volatile const uint8_t *)(uintptr_t)0x0803f800u;
    for(uint32_t i=0;i<8u;++i)out[i]=src[7u-i];
}
void case_policy_box_read_identity(uint8_t *out)
{
    volatile const uint8_t *src=(volatile const uint8_t *)(uintptr_t)0x0803f000u;
    for(uint32_t i=0;i<8u;++i){out[i]=src[7u-i];out[8u+i]=src[15u-i];}
}

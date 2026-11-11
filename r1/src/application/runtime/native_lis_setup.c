#include <stdint.h>
#include "lis2dw12_reg.h"
/* Reconstructed native mapping differs from the pinned modern ST power enum.
 * The second read failure does not suppress its write; status addition wraps. */
__attribute__((noinline)) uint32_t r1_lis_power_body(const void *ctx,uint32_t val,volatile uint8_t *frame)
{
 uint32_t status=(uint32_t)lis2dw12_read_reg(ctx,0x20,(uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 frame[0]=(uint8_t)((frame[0]&0xf1u)|((val&1u)<<3)|((val&6u)));
 status=(uint32_t)lis2dw12_write_reg(ctx,0x20,(uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 status=(uint32_t)lis2dw12_read_reg(ctx,0x25,(uint8_t *)(uintptr_t)(frame+4),1);
 frame[4]=(uint8_t)((frame[4]&0xfbu)|((val&8u)>>1));
 return status+(uint32_t)lis2dw12_write_reg(ctx,0x25,(uint8_t *)(uintptr_t)(frame+4),1);
}
__attribute__((noinline)) uint32_t r1_lis_reg17_body(const void *ctx,uint32_t unused,volatile uint8_t *frame)
{
 (void)unused;
 uint32_t status=(uint32_t)lis2dw12_read_reg(ctx,0x17,(uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 frame[0]|=0x40;
 return (uint32_t)lis2dw12_write_reg(ctx,0x17,(uint8_t *)(uintptr_t)frame,1);
}

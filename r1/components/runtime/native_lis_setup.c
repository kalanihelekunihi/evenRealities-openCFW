#include <stdint.h>
extern int32_t lis2dw12_read_reg(const void *,uint8_t,uint8_t *,uint16_t);
extern int32_t lis2dw12_write_reg(const void *,uint8_t,const uint8_t *,uint16_t);
/* Reconstructed native mapping differs from the pinned modern ST power enum.
 * The second read failure does not suppress its write; status addition wraps. */
__attribute__((noinline)) uint32_t r1_lis_power_body(const void *ctx,uint32_t val,volatile uint8_t *frame)
{
 uint32_t status=(uint32_t)lis2dw12_read_reg(ctx,0x20,(uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 frame[0]=(uint8_t)((frame[0]&0xf1u)|((val&1u)<<3)|((val&6u)));
 status=(uint32_t)lis2dw12_write_reg(ctx,0x20,(const uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 status=(uint32_t)lis2dw12_read_reg(ctx,0x25,(uint8_t *)(uintptr_t)(frame+4),1);
 frame[4]=(uint8_t)((frame[4]&0xfbu)|((val&8u)>>1));
 return status+(uint32_t)lis2dw12_write_reg(ctx,0x25,(const uint8_t *)(uintptr_t)(frame+4),1);
}
__attribute__((noinline)) uint32_t r1_lis_reg17_body(const void *ctx,uint32_t unused,volatile uint8_t *frame)
{
 (void)unused;
 uint32_t status=(uint32_t)lis2dw12_read_reg(ctx,0x17,(uint8_t *)(uintptr_t)frame,1);
 if(status)return status;
 frame[0]|=0x40;
 return (uint32_t)lis2dw12_write_reg(ctx,0x17,(const uint8_t *)(uintptr_t)frame,1);
}
#define BRIDGE24(name,body) __attribute__((naked)) uint32_t name(void) { __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\nmov r2,sp\nbl " #body "\npop {r2,r3,r4,r5,r6,pc}\n"); }
BRIDGE24(lis2dw12_data_rate_set,lis2dw12_data_rate_set_body)
BRIDGE24(lis2dw12_filter_path_set,lis2dw12_filter_path_set_body)
BRIDGE24(r1_lis_native_power_mode_set,r1_lis_power_body)
__attribute__((naked)) uint32_t r1_lis_reg17_bit6_enable(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl r1_lis_reg17_body\npop {r3,r4,r5,pc}\n"); }

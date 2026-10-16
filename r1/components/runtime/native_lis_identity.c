#include <stdint.h>
extern uint32_t r1_lis_context[4];
extern uint32_t r1_motion_bus_device;
extern void __aeabi_memclr(void *,uint32_t);
extern int32_t lis2dw12_read_reg(const void *,uint8_t,uint8_t *,uint16_t);
extern uint32_t r1_stock_dispatch_10(uint32_t,uint32_t,void *,uint32_t);
extern uint32_t r1_stock_dispatch_14(uint32_t,uint32_t,void *,uint32_t);
/* Native request records are20 bytes, fully cleared, at caller SP-40. */
__attribute__((naked)) uint32_t r1_motion_bus_read_request(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,lr}\nsub sp,#20\nmov r6,r1\nmov r7,r0\nmov r4,r3\nmov r5,r2\nmovs r1,#20\nmov r0,sp\nbl __aeabi_memclr\nldr r0,=r1_motion_bus_device\nstrh r6,[sp,#2]\nstrb r7,[sp]\nstrh r4,[sp,#16]\nmovs r3,#0\nstr r5,[sp,#12]\nmov r2,sp\nmov r1,r3\nldr r0,[r0]\nbl r1_stock_dispatch_10\ncmp r0,#0\nite eq\nmoveq r0,#1\nmovne r0,#0\nadd sp,#20\npop {r4,r5,r6,r7,pc}\n");
}
__attribute__((naked)) uint32_t r1_motion_bus_write_request(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,lr}\nsub sp,#20\nmov r6,r1\nmov r7,r0\nmov r4,r3\nmov r5,r2\nmovs r1,#20\nmov r0,sp\nbl __aeabi_memclr\nldr r0,=r1_motion_bus_device\nstrh r6,[sp,#2]\nstrb r7,[sp]\nstr r5,[sp,#4]\nstrh r4,[sp,#8]\nmovs r3,#0\nmov r2,sp\nmov r1,r3\nldr r0,[r0]\nbl r1_stock_dispatch_14\ncmp r0,#0\nite eq\nmoveq r0,#1\nmovne r0,#0\nadd sp,#20\npop {r4,r5,r6,r7,pc}\n");
}
__attribute__((naked)) int32_t r1_lis_default_read(void)
{ __asm__ volatile("push {r4,lr}\nmovs r0,#24\nbl r1_motion_bus_read_request\nmovs r0,#0\npop {r4,pc}\n"); }
__attribute__((naked)) int32_t r1_lis_default_write(void)
{ __asm__ volatile("push {r4,lr}\nmovs r0,#24\nbl r1_motion_bus_write_request\nmovs r0,#0\npop {r4,pc}\n"); }
__attribute__((naked)) int32_t r1_lis_device_id_get(void)
{ __asm__ volatile("push {r4,lr}\nmov r2,r1\nmovs r3,#1\nmovs r1,#15\nbl lis2dw12_read_reg\npop {r4,pc}\n"); }
__attribute__((naked)) uint32_t r1_lis2dw12_identity_probe(void)
{
 __asm__ volatile("ldr r0,=r1_lis_context\npush {r3,lr}\nldr r1,[r0]\ncbnz r1,1f\nldr r1,=r1_lis_default_write\nstr r1,[r0]\n1: ldr r1,[r0,#4]\ncbnz r1,2f\nldr r1,=r1_lis_default_read\nstr r1,[r0,#4]\n2: movs r0,#0\nstrb r0,[sp]\nmov r1,sp\nldr r0,=r1_lis_context\nbl r1_lis_device_id_get\nldrb r0,[sp]\npop {r3,pc}\n");
}

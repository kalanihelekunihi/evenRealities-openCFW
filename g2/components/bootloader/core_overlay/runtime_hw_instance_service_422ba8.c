/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader instance register service. */

typedef __UINT8_TYPE__ open_cfw_hws_u8;
typedef __UINT32_TYPE__ open_cfw_hws_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_hw_resource_enter_41bf84(void);
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);
extern void open_cfw_bootloader_mode_disable_route_422364(void);
extern void open_cfw_bootloader_retained_instance_teardown_423700(void);
extern void open_cfw_bootloader_retained_hw_resource_exit_41c17a(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_instance_service_422ba8(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movs r7, r2\n"
        "cmp r4, #0\n"
        "beq 1f\n"
        "ldr r0, [r4]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr.w r2, [pc, #0x824]\n"
        "cmp r0, r2\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 20f\n"
        "2:\n"
        "ldr r5, [r4, #0x28]\n"
        "adds.w r6, r5, #0xb\n"
        "cmp r1, #0\n"
        "beq 3f\n"
        "cmp r1, #2\n"
        "beq 10f\n"
        "blo 10f\n"
        "b 21f\n"
        "3:\n"
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq 4f\n"
        "ldrb r0, [r4, #4]\n"
        "cmp r0, #0\n"
        "bne 4f\n"
        "movs r0, #7\n"
        "b 20f\n"
        "4:\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "bl open_cfw_bootloader_retained_hw_resource_enter_41bf84\n"
        "uxtb r7, r7\n"
        "cmp r7, #0\n"
        "beq 19f\n"
        "ldr r0, [r4, #0x30]\n"
        "ldr.w r1, [pc, #0x838]\n"
        "cmp r0, r1\n"
        "blo 5f\n"
        "ldr.w r0, [pc, #0x834]\n"
        "ldr r0, [r0]\n"
        "and r0, r0, #0xff\n"
        "cmp r0, #0x22\n"
        "blo 5f\n"
        "ldr.w r0, [pc, #0x82c]\n"
        "ldr r1, [r0]\n"
        "movs.w r2, #0x400000\n"
        "lsls r2, r5\n"
        "orrs r1, r2\n"
        "str r1, [r0]\n"
        "5:\n"
        "adds.w r1, r5, #0xb\n"
        "uxtb r1, r1\n"
        "ldrb.w r0, [r4, #0x118]\n"
        "bl open_cfw_bootloader_mode_enable_route_4222f0\n"
        "ldr.w r0, [pc, #0x810]\n"
        "ldr r1, [r4, #8]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x20]\n"
        "ldr r1, [r4, #0xc]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x24]\n"
        "ldr r1, [r4, #0x10]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x28]\n"
        "ldr r1, [r4, #0x14]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x2c]\n"
        "ldr r1, [r4, #0x18]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x30]\n"
        "ldr r1, [r4, #0x1c]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x34]\n"
        "ldr r1, [r4, #0x20]\n"
        "adds.w r2, r0, r5, lsl #12\n"
        "str r1, [r2, #0x38]\n"
        "ldr r1, [r4, #0x24]\n"
        "adds.w r0, r0, r5, lsl #12\n"
        "str r1, [r0, #0x48]\n"
        "movs r0, #0\n"
        "strb r0, [r4, #4]\n"
        "19:\n"
        "movs r0, #0\n"
        "20:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n"
        "10:\n"
        "uxtb r7, r7\n"
        "cmp r7, #0\n"
        "beq 12f\n"
        "ldr.w r0, [pc, #0x7c0]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x20]\n"
        "str r1, [r4, #8]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x24]\n"
        "str r1, [r4, #0xc]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x28]\n"
        "str r1, [r4, #0x10]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x2c]\n"
        "str r1, [r4, #0x14]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x30]\n"
        "str r1, [r4, #0x18]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x34]\n"
        "str r1, [r4, #0x1c]\n"
        "adds.w r1, r0, r5, lsl #12\n"
        "ldr r1, [r1, #0x38]\n"
        "str r1, [r4, #0x20]\n"
        "adds.w r0, r0, r5, lsl #12\n"
        "ldr r0, [r0, #0x48]\n"
        "str r0, [r4, #0x24]\n"
        "movs r0, #1\n"
        "strb r0, [r4, #4]\n"
        "12:\n"
        "ldr r0, [r4, #0x30]\n"
        "ldr.w r1, [pc, #0x768]\n"
        "cmp r0, r1\n"
        "blo 13f\n"
        "ldr.w r0, [pc, #0x764]\n"
        "ldr r0, [r0]\n"
        "and r0, r0, #0xff\n"
        "cmp r0, #0x22\n"
        "blo 13f\n"
        "ldr.w r0, [pc, #0x75c]\n"
        "ldr r1, [r0]\n"
        "movs.w r2, #0x400000\n"
        "lsls r2, r5\n"
        "bics r1, r2\n"
        "str r1, [r0]\n"
        "13:\n"
        "adds.w r1, r5, #0xb\n"
        "uxtb r1, r1\n"
        "ldrb.w r0, [r4, #0x118]\n"
        "bl open_cfw_bootloader_mode_disable_route_422364\n"
        "movs.w r1, #-1\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_retained_instance_teardown_423700\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x734]\n"
        "adds.w r1, r1, r5, lsl #12\n"
        "str r0, [r1, #0x30]\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "bl open_cfw_bootloader_retained_hw_resource_exit_41c17a\n"
        "b 19b\n"
        "21:\n"
        "movs r0, #6\n"
        "b 20b\n");
}
#else
typedef struct { open_cfw_hws_u8 bytes[0x11c]; } open_cfw_hws_instance;
extern open_cfw_hws_u32 open_cfw_hws_host_registers[4][32];
extern open_cfw_hws_u32 open_cfw_hws_host_revision;
extern open_cfw_hws_u32 open_cfw_hws_host_clock;
extern void open_cfw_hws_host_resource_enter(open_cfw_hws_u32 resource);
extern void open_cfw_hws_host_mode_enable(open_cfw_hws_u32 mode, open_cfw_hws_u32 resource);
extern void open_cfw_hws_host_mode_disable(open_cfw_hws_u32 mode, open_cfw_hws_u32 resource);
extern void open_cfw_hws_host_teardown(open_cfw_hws_instance *instance, open_cfw_hws_u32 value);
extern void open_cfw_hws_host_resource_exit(open_cfw_hws_u32 resource);
static open_cfw_hws_u32 open_cfw_hws_read32(const open_cfw_hws_u8 *p)
{ return (open_cfw_hws_u32)p[0]|((open_cfw_hws_u32)p[1]<<8)|((open_cfw_hws_u32)p[2]<<16)|((open_cfw_hws_u32)p[3]<<24); }
static void open_cfw_hws_write32(open_cfw_hws_u8 *p,open_cfw_hws_u32 v)
{ p[0]=(open_cfw_hws_u8)v;p[1]=(open_cfw_hws_u8)(v>>8);p[2]=(open_cfw_hws_u8)(v>>16);p[3]=(open_cfw_hws_u8)(v>>24); }
open_cfw_hws_u32 open_cfw_bootloader_hw_instance_service_422ba8(open_cfw_hws_instance *instance,open_cfw_hws_u32 action,open_cfw_hws_u32 transfer)
{
    open_cfw_hws_u32 index,resource,i;
    if(instance==(open_cfw_hws_instance*)0 || (open_cfw_hws_read32(instance->bytes)&~0xfe000000U)!=0x01ea9e06U)return 2U;
    index=open_cfw_hws_read32(instance->bytes+0x28);resource=(open_cfw_hws_u8)(index+11U);
    if(action>2U)return 6U;
    if(action==0U){
        if((open_cfw_hws_u8)transfer!=0U && instance->bytes[4]==0U)return 7U;
        open_cfw_hws_host_resource_enter(resource);
        if((open_cfw_hws_u8)transfer==0U)return 0U;
        if(open_cfw_hws_read32(instance->bytes+0x30)>=0x0016e361U && (open_cfw_hws_host_revision&0xffU)>=0x22U)open_cfw_hws_host_clock|=0x00400000U<<index;
        open_cfw_hws_host_mode_enable(instance->bytes[0x118],resource);
        for(i=0;i<7U;i++)open_cfw_hws_host_registers[index][i]=open_cfw_hws_read32(instance->bytes+8U+4U*i);
        open_cfw_hws_host_registers[index][18]=open_cfw_hws_read32(instance->bytes+0x24);instance->bytes[4]=0;return 0U;
    }
    if((open_cfw_hws_u8)transfer!=0U){for(i=0;i<7U;i++)open_cfw_hws_write32(instance->bytes+8U+4U*i,open_cfw_hws_host_registers[index][i]);open_cfw_hws_write32(instance->bytes+0x24,open_cfw_hws_host_registers[index][18]);instance->bytes[4]=1;}
    if(open_cfw_hws_read32(instance->bytes+0x30)>=0x0016e361U && (open_cfw_hws_host_revision&0xffU)>=0x22U)open_cfw_hws_host_clock&=~(0x00400000U<<index);
    open_cfw_hws_host_mode_disable(instance->bytes[0x118],resource);open_cfw_hws_host_teardown(instance,0xffffffffU);open_cfw_hws_host_registers[index][4]=0;open_cfw_hws_host_resource_exit(resource);return 0U;
}
#endif

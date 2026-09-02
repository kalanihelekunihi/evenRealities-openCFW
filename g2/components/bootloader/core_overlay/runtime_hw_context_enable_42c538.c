/* SPDX-License-Identifier: MIT */
/* Clean-room hardware-context enable sequence and failure rollback. */
typedef __UINT8_TYPE__ open_cfw_hw_enable_u8;
typedef __UINT32_TYPE__ open_cfw_hw_enable_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_status_route_42c034(void);
extern void open_cfw_bootloader_cmdq_adapter_init_42c3e2(void);
extern void open_cfw_bootloader_retained_status_check_41d246(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_context_enable_42c538(void)
{__asm volatile(
 "push {r2,r3,r4,r5,r6,lr}\nmovs r5,r0\nmovs r4,#0\ncmp r0,#0\nbeq 8f\n"
 "ldr r0,[r0]\nbic r0,r0,#0xfe000000\nldr.w r1,[pc,#0x864]\ncmp r0,r1\nbeq 1f\n"
 "8: movs r0,#2\nb 9f\n"
 "1: ldr r0,[r5]\nubfx r0,r0,#25,#1\ncmp r0,#0\nbeq 2f\nmovs r0,#0\nb 9f\n"
 "2: ldrb r0,[r5,#8]\ncmp r0,#0\nbne 3f\nmovs r1,#0\nb 4f\n3: movs r1,#1\n"
 "4: ldr r0,[r5,#4]\nbl open_cfw_bootloader_hw_status_route_42c034\ncmp r0,#0\nbne 5f\n"
 "movs r0,#9\nb 9f\n"
 "5: ldr r0,[r5,#0xc]\ncmp r0,#0\nbeq 6f\n"
 "movs r0,#0\nstr r0,[r5,#0x24]\nmovs r0,#0\nstr r0,[r5,#0x1c]\n"
 "ldr r6,[pc,#0x15c]\nldr r0,[r5,#4]\nadds.w r0,r6,r0,lsl #12\n"
 "ldr.w r1,[pc,#0x828]\nstr.w r1,[r0,#0x238]\n"
 "movs r0,#0\nstr.w r0,[r5,#0x854]\nmovs r0,#0\nstrb.w r0,[r5,#0x83c]\n"
 "movs r0,#0\nstr.w r0,[r5,#0x838]\nmovs r0,#0\nstr.w r0,[r5,#0x844]\n"
 "movs r0,#0\nstr.w r0,[r5,#0x840]\nmovs r0,#0\nstrb.w r0,[r5,#0x82c]\n"
 "movs r0,#0\nstr.w r0,[r5,#0x830]\nmovs r0,#1\nstrb.w r0,[r5,#0x82d]\n"
 "ldr r2,[r5,#0xc]\nldr r1,[r5,#0x10]\nmovs r0,r5\n"
 "bl open_cfw_bootloader_cmdq_adapter_init_42c3e2\nmovs r4,r0\n"
 "ldr r0,[r5,#4]\nadds.w r6,r6,r0,lsl #12\nmovs r0,#2\nstr.w r0,[r6,#0x210]\n"
 "6: cmp r4,#0\nbne 7f\nldr r6,[pc,#0x100]\nmovs r0,#1\nstr r0,[sp]\n"
 "movs r3,#4\nmovs r2,#6\nldr r0,[r5,#4]\nadds.w r0,r6,r0,lsl #12\n"
 "adds.w r1,r0,#0x248\nmov.w r0,#0x3e8\n"
 "bl open_cfw_bootloader_retained_status_check_41d246\nmovs r4,r0\ncmp r4,#0\nbne 10f\n"
 "ldr r0,[r5]\norrs r0,r0,#0x2000000\nstr r0,[r5]\nb 7f\n"
 "10: ldr r0,[r5,#4]\nadds.w r0,r6,r0,lsl #12\nadds.w r0,r0,#0x11c\n"
 "ldr r1,[r0]\nlsrs r1,r1,#1\nlsls r1,r1,#1\nstr r1,[r0]\n"
 "ldr r0,[r5,#4]\nadds.w r6,r6,r0,lsl #12\nadds.w r0,r6,#0x11c\n"
 "ldr r1,[r0]\nbics r1,r1,#0x10\nstr r1,[r0]\n"
 "7: movs r0,r4\n9: pop {r1,r2,r4,r5,r6,pc}\n");}
#else
typedef struct {
    open_cfw_hw_enable_u32 header;
    open_cfw_hw_enable_u32 instance;
    open_cfw_hw_enable_u8 mode;
    open_cfw_hw_enable_u32 cmdq_present;
    open_cfw_hw_enable_u32 reset_words[7];
    open_cfw_hw_enable_u8 reset_byte;
    open_cfw_hw_enable_u8 ready_byte;
    open_cfw_hw_enable_u32 register_238;
    open_cfw_hw_enable_u32 register_210;
    open_cfw_hw_enable_u32 register_11c;
} open_cfw_hw_enable_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_enable_u32 open_cfw_bootloader_hw_context_enable_42c538_portable(
    open_cfw_hw_enable_model *context,
    open_cfw_hw_enable_u32 status_route_ready,
    open_cfw_hw_enable_u32 cmdq_status,
    open_cfw_hw_enable_u32 wait_status)
{
    open_cfw_hw_enable_u32 index;
    if(context==0 || (context->header&0x01FFFFFFU)!=0x01123456U)return 2U;
    if((context->header&0x02000000U)!=0U)return 0U;
    if(status_route_ready==0U)return 9U;
    if(context->cmdq_present!=0U){
        for(index=0U;index<7U;index++)context->reset_words[index]=0U;
        context->reset_byte=0U;
        context->ready_byte=1U;
        context->register_238=0x00800040U;
        context->register_210=2U;
        if(cmdq_status!=0U)return cmdq_status;
    }
    if(wait_status==0U)context->header|=0x02000000U;
    else context->register_11c&=~0x00000011U;
    return wait_status;
}
#endif

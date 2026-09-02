/* SPDX-License-Identifier: MIT */
/* Clean-room command-queue initialization, enable, and disable adapters. */
typedef __UINT8_TYPE__ open_cfw_cmdqa_u8;
typedef __UINT32_TYPE__ open_cfw_cmdqa_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_init_427794(void);
extern open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_enable_427878(void);
extern open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_disable_4278c8(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_init_42c3e2(void)
{__asm volatile(
 "push {r0, r1, r2, r3, r4, lr}\nmovs r4, r0\nldr r0, [r4, #4]\n"
 "movs r3, #0\nmovs r3, #0\nstr.w r3, [r4, #0x828]\nmovs r3, #0\n"
 "str r3, [r4, #0x20]\nmovs r3, #0\nstr.w r3, [r4, #0x85c]\n"
 "str r2, [sp, #4]\nlsrs r1, r1, #1\nstr r1, [sp]\nmovs r1, #1\n"
 "strb.w r1, [sp, #8]\naddw r2, r4, #0x828\nmov r1, sp\nuxtb r0, r0\n"
 "bl open_cfw_bootloader_cmdq_init_427794\ncmp r0, #0\nbne 1f\n"
 "mov.w r1, #0x100\nstr r1, [r4, #0x20]\n1:\nadd sp, #0x10\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_enable_42c420(void)
{__asm volatile(
 "push {r7, lr}\nldr r1, [r0, #0x24]\ncmp r1, #0\nbne 1f\n"
 "ldr.w r2, [pc, #0x2bc]\nldr r1, [r0, #4]\nadds.w r1, r2, r1, lsl #12\n"
 "ldr.w r1, [r1, #0x22c]\nldr r3, [r0, #4]\nadds.w r2, r2, r3, lsl #12\n"
 "adds.w r2, r2, #0x22c\nstr r2, [r1]\nstr r1, [r1, #4]\n1:\n"
 "ldr.w r0, [r0, #0x828]\nbl open_cfw_bootloader_cmdq_enable_427878\npop {r1, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_disable_42c44e(void)
{__asm volatile(
 "push {r7, lr}\nldr.w r0, [r0, #0x828]\n"
 "bl open_cfw_bootloader_cmdq_disable_4278c8\npop {r1, pc}\n");}
#else
typedef struct open_cfw_cmdqa_config {
 open_cfw_cmdqa_u32 capacity;
 open_cfw_cmdqa_u32 descriptor;
 open_cfw_cmdqa_u8 priority;
} open_cfw_cmdqa_config;
typedef struct open_cfw_cmdqa_state {
 open_cfw_cmdqa_u32 queue_handle;
 open_cfw_cmdqa_u32 active;
 open_cfw_cmdqa_u32 auxiliary;
 open_cfw_cmdqa_u32 *link;
} open_cfw_cmdqa_state;
typedef open_cfw_cmdqa_u32 (*open_cfw_cmdqa_init_fn)(open_cfw_cmdqa_u8,const open_cfw_cmdqa_config *,open_cfw_cmdqa_u32 *);
typedef open_cfw_cmdqa_u32 (*open_cfw_cmdqa_control_fn)(open_cfw_cmdqa_u32);
__attribute__((used,noinline,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_init_42c3e2_portable(open_cfw_cmdqa_state *state,open_cfw_cmdqa_u8 instance,open_cfw_cmdqa_u32 byte_capacity,open_cfw_cmdqa_u32 descriptor,open_cfw_cmdqa_init_fn initialize)
{open_cfw_cmdqa_config config;state->queue_handle=0U;state->active=0U;state->auxiliary=0U;config.capacity=byte_capacity>>1;config.descriptor=descriptor;config.priority=1U;open_cfw_cmdqa_u32 result=initialize(instance,&config,&state->queue_handle);if(result==0U)state->active=0x100U;return result;}
__attribute__((used,noinline,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_enable_42c420_portable(open_cfw_cmdqa_state *state,open_cfw_cmdqa_u32 *hardware_link,open_cfw_cmdqa_control_fn enable)
{if(state->link==(open_cfw_cmdqa_u32 *)0){state->link=hardware_link;hardware_link[0]=(open_cfw_cmdqa_u32)(unsigned long)hardware_link;hardware_link[1]=(open_cfw_cmdqa_u32)(unsigned long)hardware_link;}return enable(state->queue_handle);}
__attribute__((used,noinline,visibility("default")))
open_cfw_cmdqa_u32 open_cfw_bootloader_cmdq_adapter_disable_42c44e_portable(const open_cfw_cmdqa_state *state,open_cfw_cmdqa_control_fn disable)
{return disable(state->queue_handle);}
#endif

/* SPDX-License-Identifier: MIT */
/* Clean-room state, traversal, hardware-normalization, boot, and validation services. */
typedef __UINT32_TYPE__ open_cfw_smalls_u32;
typedef __UINT8_TYPE__ open_cfw_smalls_u8;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_state_adjust_42cdf8(void);
extern void open_cfw_bootloader_clock_config_422364(void);
extern void open_cfw_bootloader_scb_priority_nibble_430280(void);
extern void open_cfw_bootloader_mode_one_apply_42fff2(void);
extern void open_cfw_bootloader_platform_stage_430000(void);
extern void open_cfw_bootloader_platform_prepare_41f612(void);
extern void open_cfw_bootloader_platform_finish_430502(void);
extern void open_cfw_bootloader_address_limit_query_41d792(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_state_update_critical_42cea4(void)
{__asm volatile(
 "push {r2, r3, r4, lr}\nmovs r4, r0\nbl open_cfw_bootloader_critical_enter_41b8ec\n"
 "str r0, [sp]\nldr.w r0, [pc, #0x908]\nstrb r4, [r0]\n"
 "ldr.w r0, [pc, #0x904]\nldrb r0, [r0]\ncmp r0, #0\nbeq 1f\n"
 "movs r0, #1\nldr.w r1, [pc, #0x8fc]\nstrb r0, [r1]\nb 2f\n"
 "1:\nmovs r0, r4\nuxtb r0, r0\nbl open_cfw_bootloader_state_adjust_42cdf8\n"
 "2:\nldr r0, [sp]\nmsr primask, r0\npop {r0, r1, r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_chunked_indirect_visit_42d9f0(void)
{__asm volatile(
 "push {r4, r5, r6, lr}\nmovs r5, r0\nmovs r4, r1\nb 2f\n"
 "1:\nldr r0, [r6]\nldr r0, [r0, #4]\nsubs r4, r4, r0\n"
 "ldr r0, [r6]\nldr r0, [r0, #4]\nadds r5, r0, r5\n"
 "2:\ncmp r4, #0\nbeq 3f\nldr.w r6, [pc, #0x718]\n"
 "movs r0, r5\nldr r1, [r6]\nldr r1, [r1, #0x20]\nblx r1\n"
 "ldr r0, [r6]\nldr r0, [r0, #4]\ncmp r0, r4\nblo 1b\n"
 "3:\npop {r4, r5, r6, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hardware_channel_normalize_42eda0(void)
{__asm volatile(
 "push {r4, lr}\nmovs r4, r0\nldr r1, [r4, #4]\ncmp r0, #0\nbeq 3f\n"
 "ldr r0, [r0]\nbic r0, r0, #0xfe000000\nldr.w r1, [pc, #0x3c8]\n"
 "cmp r0, r1\nbeq 1f\n3:\nmovs r0, #2\nb 4f\n"
 "1:\nldr.w r0, [pc, #0x3c0]\nldr r1, [r0]\nbics r1, r1, #4\nstr r1, [r0]\n"
 "ldr r1, [r0]\nlsrs r1, r1, #1\nlsls r1, r1, #1\nstr r1, [r0]\n"
 "ldr r1, [r0]\nubfx r1, r1, #24, #3\ncmp r1, #3\nbne 2f\n"
 "ldr r1, [r0]\nbics r1, r1, #0x7000000\nstr r1, [r0]\n"
 "2:\nmovs r1, #0xf\nmovs r0, #4\nbl open_cfw_bootloader_clock_config_422364\n"
 "ldr r0, [r4]\nbics r0, r0, #0x2000000\nstr r0, [r4]\nmovs r0, #0\n"
 "4:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_platform_boot_sequence_4301d6(void)
{__asm volatile(
 "push {r7, lr}\nmovs r1, #0x61\nldr r0, [pc, #0x60]\n"
 "bl open_cfw_bootloader_scb_priority_nibble_430280\n"
 "bl open_cfw_bootloader_mode_one_apply_42fff2\n"
 "bl open_cfw_bootloader_platform_stage_430000\n"
 "bl open_cfw_bootloader_platform_prepare_41f612\n"
 "bl open_cfw_bootloader_platform_finish_430502\n"
 "movs r0, #0\npop {r1, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_address_validate_430a60(void)
{__asm volatile(
 "push {r4, r5, r6, lr}\nsub sp, #0x40\nmovs r4, r1\nmovs r5, r0\n"
 "adds r0, r4, r0\nsubs r0, r0, #1\nldr.w r6, [pc, #0x9c]\n"
 "ldr r0, [r6]\ncmp r0, #0\nbne 1f\nmov r1, sp\nmovs r0, #1\n"
 "bl open_cfw_bootloader_address_limit_query_41d792\nldr r0, [sp, #0x2c]\nstr r0, [r6]\n"
 "1:\ncmp.w r5, #0x4000\nbhs 2f\nmovs r0, #0\nb 4f\n"
 "2:\nldr r0, [r6]\ncmp r4, r0\nblo 3f\nmovs r0, #0\nb 4f\n"
 "3:\nmovs r0, #1\n4:\nadd sp, #0x40\npop {r4, r5, r6, pc}\n");}
#else
typedef void (*open_cfw_smalls_byte_fn)(open_cfw_smalls_u8);
typedef void (*open_cfw_smalls_visit_fn)(open_cfw_smalls_u32);
typedef void (*open_cfw_smalls_pair_fn)(open_cfw_smalls_u32,open_cfw_smalls_u32);
typedef void (*open_cfw_smalls_void_fn)(void);

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_state_update_critical_42cea4_portable(
    open_cfw_smalls_u8 value, open_cfw_smalls_u8 active,
    open_cfw_smalls_u8 *state, open_cfw_smalls_u8 *pending,
    open_cfw_smalls_byte_fn adjust)
{*state=value;if(active!=0U)*pending=1U;else adjust(value);}

__attribute__((used,noinline,visibility("default")))
open_cfw_smalls_u32 open_cfw_bootloader_chunked_indirect_visit_42d9f0_portable(
    open_cfw_smalls_u32 address, open_cfw_smalls_u32 length,
    open_cfw_smalls_u32 chunk, open_cfw_smalls_visit_fn visit)
{open_cfw_smalls_u32 calls=0U;while(length!=0U){visit(address);calls++;if(chunk>=length)break;length-=chunk;address+=chunk;}return calls;}

__attribute__((used,noinline,visibility("default")))
open_cfw_smalls_u32 open_cfw_bootloader_hardware_channel_normalize_42eda0_portable(
    open_cfw_smalls_u32 *handle_word, open_cfw_smalls_u32 magic,
    open_cfw_smalls_u32 *control, open_cfw_smalls_pair_fn clock_config)
{open_cfw_smalls_u32 word;if(handle_word==0||((*handle_word)&0x01ffffffU)!=magic)return 2U;word=*control;word&=~5U;if(((word>>24)&7U)==3U)word&=~0x07000000U;*control=word;clock_config(4U,15U);*handle_word&=~0x02000000U;return 0U;}

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_platform_boot_sequence_4301d6_portable(
    open_cfw_smalls_void_fn priority, open_cfw_smalls_void_fn mode,
    open_cfw_smalls_void_fn stage, open_cfw_smalls_void_fn prepare,
    open_cfw_smalls_void_fn finish)
{priority();mode();stage();prepare();finish();}

__attribute__((used,noinline,visibility("default")))
open_cfw_smalls_u32 open_cfw_bootloader_address_validate_430a60_portable(
    open_cfw_smalls_u32 address, open_cfw_smalls_u32 length,
    open_cfw_smalls_u32 limit)
{return address>=0x4000U&&length<limit;}
#endif

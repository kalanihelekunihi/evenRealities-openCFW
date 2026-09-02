/* SPDX-License-Identifier: MIT */
/* Clean-room late runtime wrappers for modes, validation, transfer, and init. */
typedef __UINT32_TYPE__ open_cfw_late_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_apply_42ff00(void);
extern open_cfw_late_u32 open_cfw_bootloader_boolean_route_41d9aa(void);
extern open_cfw_late_u32 open_cfw_bootloader_address_validate_430a60(void);
extern void open_cfw_bootloader_byte_copy_41568c(void);
extern void open_cfw_bootloader_word_transfer_provider_430b10(void);
extern open_cfw_late_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_alignment_dispatch_42e4f4(void);
extern void open_cfw_bootloader_platform_init_41733c(void);
extern void open_cfw_bootloader_platform_route_4174a6(void);
extern void open_cfw_bootloader_platform_finish_417392(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_mode_one_apply_42fff2(void)
{__asm volatile("push {r7, lr}\nmovs r1, #1\nmovs r0, #1\nbl open_cfw_bootloader_mode_apply_42ff00\npop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_boolean_route_status_4303bc(void)
{__asm volatile(
 "push {r7, lr}\nuxtb r1, r1\ncmp r1, #1\nbne 1f\nmovs r1, #1\nb 2f\n"
 "1:\nmovs r1, #0\n2:\nuxtb r1, r1\nbl open_cfw_bootloader_boolean_route_41d9aa\n"
 "cmp r0, #0\nbeq 3f\nmovs.w r0, #-1\nb 4f\n3:\nmovs r0, #0\n4:\npop {r1, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_validated_byte_copy_430a9c(void)
{__asm volatile(
 "push {r4, r5, r6, lr}\nmovs r4, r0\nmovs r5, r1\nmovs r6, r2\n"
 "movs r1, r6\nmovs r0, r5\nbl open_cfw_bootloader_address_validate_430a60\n"
 "cmp r0, #0\nbeq 1f\nmovs r2, r6\nmovs r1, r5\nmovs r0, r4\n"
 "bl open_cfw_bootloader_byte_copy_41568c\nmovs r0, #0\nb 2f\n"
 "1:\nmovs.w r0, #-1\n2:\npop {r4, r5, r6, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_validated_word_transfer_430ac4(void)
{__asm volatile(
 "push {r4, r5, r6, lr}\nmovs r4, r0\nmovs r5, r1\nmovs r6, r2\n"
 "movs r1, r6\nmovs r0, r4\nbl open_cfw_bootloader_address_validate_430a60\n"
 "cmp r0, #0\nbeq 1f\nmovs r2, r6\nmovs r1, r5\nmovs r0, r4\n"
 "bl open_cfw_bootloader_word_transfer_provider_430b10\nmovs r0, #0\nb 2f\n"
 "1:\nmovs.w r0, #-1\n2:\npop {r4, r5, r6, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_word_transfer_critical_430b10(void)
{__asm volatile(
 "push {r3, r4, r5, r6, r7, lr}\nmovs r4, r0\nmovs r5, r1\nmovs r6, r2\n"
 "movs r0, r4\nmov r8, r8\nmov r8, r8\nadds r6, r6, #3\nlsrs r6, r6, #2\n"
 "bl open_cfw_bootloader_critical_save_41b8ec\nmovs r7, r0\nmovs r3, r6\n"
 "movs r2, r4\nmovs r1, r5\nldr r0, [pc, #0xc]\n"
 "bl open_cfw_bootloader_alignment_dispatch_42e4f4\nmovs r0, r7\n"
 "msr primask, r0\npop {r0, r4, r5, r6, r7, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_platform_services_init_43194c(void)
{__asm volatile(
 "push {r7, lr}\nbl open_cfw_bootloader_platform_init_41733c\n"
 "movs r1, #0xff\nmovs r0, #0\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "movs r1, #0xd7\nmovs r0, #1\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "movs r1, #0xd7\nmovs r0, #2\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "movs r1, #0xd7\nmovs r0, #3\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "movs r1, #0xd7\nmovs r0, #4\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "movs r1, #0xd7\nmovs r0, #5\nbl open_cfw_bootloader_platform_route_4174a6\n"
 "bl open_cfw_bootloader_platform_finish_417392\nmovs r0, #0\npop {r1, pc}\n");}
#else
typedef open_cfw_late_u32 (*open_cfw_late_pair_fn)(open_cfw_late_u32,open_cfw_late_u32);
typedef void (*open_cfw_late_copy_fn)(void *,const void *,open_cfw_late_u32);
typedef void (*open_cfw_late_route_fn)(open_cfw_late_u32,open_cfw_late_u32);
typedef void (*open_cfw_late_void_fn)(void);
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_mode_one_apply_42fff2_portable(open_cfw_late_route_fn apply){apply(1U,1U);}
__attribute__((used,noinline,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_boolean_route_status_4303bc_portable(open_cfw_late_u32 object,open_cfw_late_u32 value,open_cfw_late_pair_fn route){return route(object,value==1U?1U:0U)==0U?0U:~0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_validated_byte_copy_430a9c_portable(void *destination,const void *source,open_cfw_late_u32 size,open_cfw_late_pair_fn validate,open_cfw_late_copy_fn copy){if(validate((open_cfw_late_u32)(unsigned long)source,size)==0U)return ~0U;copy(destination,source,size);return 0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_validated_word_transfer_430ac4_portable(void *address,const void *source,open_cfw_late_u32 size,open_cfw_late_pair_fn validate,open_cfw_late_copy_fn transfer){if(validate((open_cfw_late_u32)(unsigned long)address,size)==0U)return ~0U;transfer(address,source,size);return 0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_word_transfer_critical_430b10_portable(open_cfw_late_u32 byte_count,open_cfw_late_pair_fn transfer){return transfer((byte_count+3U)>>2,0x12344321U);}
__attribute__((used,noinline,visibility("default")))
open_cfw_late_u32 open_cfw_bootloader_platform_services_init_43194c_portable(open_cfw_late_void_fn initialize,open_cfw_late_route_fn route,open_cfw_late_void_fn finish){initialize();route(0U,0xffU);for(open_cfw_late_u32 index=1U;index<=5U;index++)route(index,0xd7U);finish();return 0U;}
#endif

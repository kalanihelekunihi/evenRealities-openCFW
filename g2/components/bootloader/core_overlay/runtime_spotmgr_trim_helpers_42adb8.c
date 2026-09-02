/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager register-trim helpers at 0x0042ADB8..0x0042AE9C. */
typedef __UINT32_TYPE__ open_cfw_spotmgr_trim_u32;
#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_spotmgr_trim_enable_42adb8(open_cfw_spotmgr_trim_u32 enabled __attribute__((unused))){__asm volatile(
 "uxtb r0, r0\n" "cmp r0, #0\n" "beq.n .Ltrim_skip_profile\n"
 "ldr.w r0, [pc, #0x8dc]\n" "ldr r1, [r0]\n" "orrs r1, r1, #0x18000\n" "str r1, [r0]\n"
 "ldr.w r0, [pc, #0x8d4]\n" "ldr.w r1, [pc, #0x8d4]\n" "ldr r1, [r1, #0x68]\n" "lsrs r1, r1, #14\n" "ldr r2, [r0]\n" "bfi r2, r1, #0, #6\n" "str r2, [r0]\n"
 ".Ltrim_skip_profile:\n" "ldr.w r1, [pc, #0x8c8]\n" "ldr r0, [r1]\n" "lsls r0, r0, #22\n" "lsrs r0, r0, #22\n" "adds r0, r0, #7\n" "cmp.w r0, #0x400\n" "blo.n .Ltrim_headroom_seven\n"
 "movw r0, #0x3ff\n" "ldr r2, [r1]\n" "lsls r2, r2, #22\n" "lsrs r2, r2, #22\n" "subs r0, r0, r2\n" "ldr.w r2, [pc, #0xbbc]\n" "str r0, [r2]\n" "b.n .Ltrim_accumulate\n"
 ".Ltrim_headroom_seven:\n" "movs r0, #7\n" "ldr.w r2, [pc, #0xbb4]\n" "str r0, [r2]\n"
 ".Ltrim_accumulate:\n" "ldr r2, [r1]\n" "lsrs r3, r2, #10\n" "lsls r3, r3, #10\n" "ldr.w r0, [pc, #0xba8]\n" "ldr r0, [r0]\n" "adds r2, r0, r2\n" "lsls r2, r2, #22\n" "lsrs r2, r2, #22\n" "orrs r2, r3\n" "str r2, [r1]\n" "bx lr\n");}
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_spotmgr_profile_trim_42ae24(open_cfw_spotmgr_trim_u32 enabled __attribute__((unused))){__asm volatile(
 "push {r4}\n" "ldr.w r1, [pc, #0x878]\n" "ldr.w r2, [pc, #0x878]\n" "ldr r3, [r2, #0x68]\n" "lsrs r3, r3, #2\n" "ldr r4, [r1]\n" "bfi r4, r3, #0, #6\n" "str r4, [r1]\n"
 "ldr.w r1, [pc, #0x860]\n" "ldr r2, [r2, #0x68]\n" "ldr r3, [r1]\n" "bfi r3, r2, #15, #2\n" "str r3, [r1]\n" "uxtb r0, r0\n" "cmp r0, #0\n" "beq.n .Lprofile_trim_done\n"
 "ldr.w r1, [pc, #0x858]\n" "ldr r2, [r1]\n" "lsrs r3, r2, #10\n" "lsls r3, r3, #10\n" "ldr.w r0, [pc, #0xb60]\n" "ldr r0, [r0]\n" "subs r2, r2, r0\n" "lsls r2, r2, #22\n" "lsrs r2, r2, #22\n" "orrs r2, r3\n" "str r2, [r1]\n"
 ".Lprofile_trim_done:\n" "pop {r4}\n" "bx lr\n");}
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_spotmgr_trim_restore_42ae6c(void){__asm volatile(
 "ldr.w r0, [pc, #0x83c]\n" "ldrb r0, [r0]\n" "cmp r0, #0\n" "bne.n .Lrestore_done\n"
 "ldr.w r0, [pc, #0x838]\n" "ldr.w r1, [pc, #0x838]\n" "ldr r1, [r1]\n" "ldr r2, [r0]\n" "bfi r2, r1, #0, #7\n" "str r2, [r0]\n"
 "ldr.w r0, [pc, #0xb34]\n" "ldr.w r1, [pc, #0xb34]\n" "ldr r1, [r1]\n" "ldr r2, [r0]\n" "bfi r2, r1, #0, #7\n" "str r2, [r0]\n"
 ".Lrestore_done:\n" "bx lr\n");}
#else
__attribute__((used,noinline,visibility("default"))) open_cfw_spotmgr_trim_u32 open_cfw_spotmgr_replace(open_cfw_spotmgr_trim_u32 old,open_cfw_spotmgr_trim_u32 value,open_cfw_spotmgr_trim_u32 bits){open_cfw_spotmgr_trim_u32 mask=(1U<<bits)-1U;return(old&~mask)|(value&mask);}
__attribute__((used,noinline,visibility("default"))) void open_cfw_bootloader_spotmgr_trim_enable_42adb8(open_cfw_spotmgr_trim_u32 enabled,open_cfw_spotmgr_trim_u32 profile68,open_cfw_spotmgr_trim_u32 offset,open_cfw_spotmgr_trim_u32*control,open_cfw_spotmgr_trim_u32*profile,open_cfw_spotmgr_trim_u32*trim,open_cfw_spotmgr_trim_u32*headroom){if(enabled){*control|=0x18000U;*profile=open_cfw_spotmgr_replace(*profile,profile68>>14,6);}open_cfw_spotmgr_trim_u32 low=*trim&0x3ffU;*headroom=low+7U>=0x400U?0x3ffU-low:7U;*trim=(*trim&~0x3ffU)|((low+offset)&0x3ffU);}
__attribute__((used,noinline,visibility("default"))) void open_cfw_bootloader_spotmgr_profile_trim_42ae24(open_cfw_spotmgr_trim_u32 enabled,open_cfw_spotmgr_trim_u32 profile68,open_cfw_spotmgr_trim_u32 offset,open_cfw_spotmgr_trim_u32*a,open_cfw_spotmgr_trim_u32*b,open_cfw_spotmgr_trim_u32*trim){*a=open_cfw_spotmgr_replace(*a,profile68>>2,6);*b=(*b&~(3U<<15))|((profile68&3U)<<15);if(enabled)*trim=(*trim&~0x3ffU)|(((*trim&0x3ffU)-offset)&0x3ffU);}
__attribute__((used,noinline,visibility("default"))) void open_cfw_bootloader_spotmgr_trim_restore_42ae6c(open_cfw_spotmgr_trim_u32 blocked,open_cfw_spotmgr_trim_u32 x,open_cfw_spotmgr_trim_u32 y,open_cfw_spotmgr_trim_u32*a,open_cfw_spotmgr_trim_u32*b){if(!blocked){*a=open_cfw_spotmgr_replace(*a,x,7);*b=open_cfw_spotmgr_replace(*b,y,7);}}
#endif

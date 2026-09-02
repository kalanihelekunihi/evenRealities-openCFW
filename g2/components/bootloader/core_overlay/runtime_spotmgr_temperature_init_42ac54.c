/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager temperature monitor initialization at 0x0042AC54. */
typedef __UINT32_TYPE__ open_cfw_spotmgr_temp_u32;
#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_spotmgr_temp_u32 open_cfw_bootloader_spotmgr_temperature_init_42ac54(void){
 __asm volatile(
 "push {r5, r6, r7, lr}\n"
 "ldr r0, [pc, #0x94]\n" "ldr r0, [r0]\n" "cmp r0, #0\n" "bne.n .Lbusy\n"
 "ldr r0, [pc, #0x90]\n" "ldr r0, [r0]\n" "cmp r0, #0\n" "bne.n .Lbusy\n"
 "movs r0, #0x1d\n" "bl open_cfw_bootloader_spotmgr_temperature_enable_41bf84\n"
 "cmp r0, #0\n" "beq.n .Lenabled\n" "movs r0, #1\n" "b.n .Lreturn\n"
 ".Lenabled:\n" "mov r0, sp\n" "vldr s0, [pc, #0x40]\n"
 "bl open_cfw_bootloader_spotmgr_temperature_config_41ca2c\n"
 "cmp r0, #0\n" "bne.n .Lconfig_error\n"
 "movs r3, #0\n" "movs r2, #1\n" "ldr r1, [pc, #0xb4]\n"
 "movw r0, #0x9c4\n" "bl open_cfw_bootloader_delay_us_status_change_41d21c\n"
 "cmp r0, #0\n" "beq.n .Lsuccess\n" "movs r0, #4\n" "b.n .Lreturn\n"
 ".Lbusy:\n" "movs r0, #1\n" "b.n .Lreturn\n"
 ".Lconfig_error:\n" "movs r0, #1\n" "b.n .Lreturn\n"
 ".Lsuccess:\n" "movs r0, #0\n"
 ".Lreturn:\n" "pop {r1, r2, r3, pc}\n");}
#else
typedef open_cfw_spotmgr_temp_u32(*open_cfw_spotmgr_temp_enable)(open_cfw_spotmgr_temp_u32,void*);
typedef open_cfw_spotmgr_temp_u32(*open_cfw_spotmgr_temp_config)(float,void*);
typedef open_cfw_spotmgr_temp_u32(*open_cfw_spotmgr_temp_wait)(open_cfw_spotmgr_temp_u32,open_cfw_spotmgr_temp_u32,void*);
__attribute__((used,noinline,visibility("default")))
open_cfw_spotmgr_temp_u32 open_cfw_bootloader_spotmgr_temperature_init_42ac54(
 open_cfw_spotmgr_temp_u32 status0,open_cfw_spotmgr_temp_u32 status1,
 open_cfw_spotmgr_temp_enable enable,open_cfw_spotmgr_temp_config config,
 open_cfw_spotmgr_temp_wait wait,void*context){
 if(status0!=0U||status1!=0U)return 1U;
 if(enable(29U,context)!=0U)return 1U;
 if(config(-40.0f,context)!=0U)return 1U;
 return wait(2500U,0x400083E0U,context)==0U?0U:4U;
}
#endif

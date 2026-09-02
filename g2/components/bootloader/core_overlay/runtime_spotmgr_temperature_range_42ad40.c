/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager temperature range classifier at 0x0042AD40. */
typedef __UINT32_TYPE__ open_cfw_spotmgr_range_u32;
#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default"),pcs("aapcs-vfp")))
open_cfw_spotmgr_range_u32 open_cfw_bootloader_spotmgr_temperature_range_42ad40(float temperature __attribute__((unused))){
 __asm volatile(
 "vmov.f32 s1, #-20.0\n" "vcmp.f32 s0, s1\n" "vmrs apsr_nzcv, fpscr\n" "bpl.n .Lnot_vlow\n"
 "vldr s2, [pc, #0x19c]\n" "vcmp.f32 s0, s2\n" "vmrs apsr_nzcv, fpscr\n" "blt.n .Lnot_vlow\n" "movs r0, #0\n" "b.n .Lreturn\n"
 ".Lnot_vlow:\n" "vcmp.f32 s0, s1\n" "vmrs apsr_nzcv, fpscr\n" "blt.n .Lzero\n" "vcmp.f32 s0, #0\n" "vmrs apsr_nzcv, fpscr\n" "bpl.n .Lzero\n" "movs r0, #1\n" "b.n .Lreturn\n"
 ".Lzero:\n" "vcmp.f32 s0, #0\n" "vmrs apsr_nzcv, fpscr\n" "blt.n .Lbounds\n" "vldr s1, [pc, #0x28c]\n" "vcmp.f32 s0, s1\n" "vmrs apsr_nzcv, fpscr\n" "bpl.n .Lbounds\n" "movs r0, #2\n" "b.n .Lreturn\n"
 ".Lbounds:\n" "vldr s1, [pc, #0x278]\n" "vcmp.f32 s0, s1\n" "vmrs apsr_nzcv, fpscr\n" "blt.n .Linvalid\n" "vldr s1, [pc, #0x2c4]\n" "vcmp.f32 s0, s1\n" "vmrs apsr_nzcv, fpscr\n" "bpl.n .Linvalid\n" "movs r0, #3\n" "b.n .Lreturn\n"
 ".Linvalid:\n" "movs r0, #4\n" ".Lreturn:\n" "bx lr\n");}
#else
__attribute__((used,noinline,visibility("default")))
open_cfw_spotmgr_range_u32 open_cfw_bootloader_spotmgr_temperature_range_42ad40(float t){
 if(t>=-273.0f&&t<-20.0f)return 0U;if(t>=-20.0f&&t<0.0f)return 1U;
 if(t>=0.0f&&t<50.0f)return 2U;if(t>=50.0f&&t<1000.0f)return 3U;return 4U;
}
#endif

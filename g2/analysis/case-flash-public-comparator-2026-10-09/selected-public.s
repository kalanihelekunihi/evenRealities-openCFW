	.syntax	unified
	.eabi_attribute	67, "2.09"	@ Tag_conformance
	.cpu	cortex-m0plus
	.eabi_attribute	6, 12	@ Tag_CPU_arch
	.eabi_attribute	7, 77	@ Tag_CPU_arch_profile
	.eabi_attribute	8, 0	@ Tag_ARM_ISA_use
	.eabi_attribute	9, 1	@ Tag_THUMB_ISA_use
	.eabi_attribute	34, 0	@ Tag_CPU_unaligned_access
	.eabi_attribute	17, 1	@ Tag_ABI_PCS_GOT_use
	.eabi_attribute	20, 1	@ Tag_ABI_FP_denormal
	.eabi_attribute	21, 0	@ Tag_ABI_FP_exceptions
	.eabi_attribute	23, 3	@ Tag_ABI_FP_number_model
	.eabi_attribute	24, 1	@ Tag_ABI_align_needed
	.eabi_attribute	25, 1	@ Tag_ABI_align_preserved
	.eabi_attribute	38, 1	@ Tag_ABI_FP_16bit_format
	.eabi_attribute	18, 4	@ Tag_ABI_PCS_wchar_t
	.eabi_attribute	26, 2	@ Tag_ABI_enum_size
	.eabi_attribute	14, 0	@ Tag_ABI_PCS_R9_use
	.file	"selected-public.c"
	.text
	.globl	HAL_FLASH_Unlock                @ -- Begin function HAL_FLASH_Unlock
	.p2align	2
	.type	HAL_FLASH_Unlock,%function
	.code	16
	.thumb_func
HAL_FLASH_Unlock:                       @ @HAL_FLASH_Unlock
	.fnstart
@ %bb.0:
	ldr	r0, .LCPI0_0
	ldr	r1, [r0, #12]
	cmp	r1, #0
	bmi	.LBB0_2
@ %bb.1:
	movs	r0, #0
	bx	lr
.LBB0_2:
	ldr	r1, .LCPI0_1
	str	r1, [r0]
	ldr	r1, .LCPI0_2
	str	r1, [r0]
	ldr	r0, [r0, #12]
	lsrs	r0, r0, #31
	bx	lr
	.p2align	2
@ %bb.3:
.LCPI0_0:
	.long	1073881096                      @ 0x40022008
.LCPI0_1:
	.long	1164378403                      @ 0x45670123
.LCPI0_2:
	.long	3455027627                      @ 0xcdef89ab
.Lfunc_end0:
	.size	HAL_FLASH_Unlock, .Lfunc_end0-HAL_FLASH_Unlock
	.cantunwind
	.fnend
                                        @ -- End function
	.globl	HAL_FLASH_OB_Unlock             @ -- Begin function HAL_FLASH_OB_Unlock
	.p2align	2
	.type	HAL_FLASH_OB_Unlock,%function
	.code	16
	.thumb_func
HAL_FLASH_OB_Unlock:                    @ @HAL_FLASH_OB_Unlock
	.fnstart
@ %bb.0:
	ldr	r0, .LCPI1_0
	ldr	r1, [r0, #8]
	lsls	r1, r1, #1
	bmi	.LBB1_2
@ %bb.1:
	movs	r0, #1
	bx	lr
.LBB1_2:
	ldr	r1, .LCPI1_1
	str	r1, [r0]
	ldr	r1, .LCPI1_2
	str	r1, [r0]
	ldr	r0, [r0, #8]
	lsls	r0, r0, #1
	lsrs	r0, r0, #31
	bx	lr
	.p2align	2
@ %bb.3:
.LCPI1_0:
	.long	1073881100                      @ 0x4002200c
.LCPI1_1:
	.long	135866939                       @ 0x8192a3b
.LCPI1_2:
	.long	1281191551                      @ 0x4c5d6e7f
.Lfunc_end1:
	.size	HAL_FLASH_OB_Unlock, .Lfunc_end1-HAL_FLASH_OB_Unlock
	.cantunwind
	.fnend
                                        @ -- End function
	.ident	"Apple clang version 21.0.0 (clang-2100.3.34.2)"
	.section	".note.GNU-stack","",%progbits
	.addrsig
	.eabi_attribute	30, 3	@ Tag_ABI_optimization_goals

/* SPDX-License-Identifier: Apache-2.0 */

/* Retain the complete admitted source-only Goodix demo/driver stratum. No
 * archive or binary-library object matches this list. */
SECTION_PROLOGUE(openr1_goodix,,)
{
	KEEP(*gh_drv_config.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_drv_control.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_drv_dump.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_drv_interface.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_demo.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_demo_hook.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_demo_reg_array.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_demo_user.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_agc.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_changeinttime.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_movedetect.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gh_multi_sen_pro.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*goodix_hba_config.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*goodix_hrv_config.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_gh3x2x_port.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_gh3x2x_bind.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_gh3x2x_provider_composer.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_gh3x2x_reconstructed_roots.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_gh3x2x_stubs.c.obj(.text .text.* .rodata .rodata.* .openr1_goodix_api))
} GROUP_LINK_IN(ROMABLE_REGION)

/* SPDX-License-Identifier: Apache-2.0 */

SECTION_PROLOGUE(openr1_reconstructed,,)
{
	KEEP(*rtc_device.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*generic_device_registry.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*software_twi.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*sensor_stream.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*time_calendar.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*r1_model_data.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*quantized_runtime.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gxt310.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*qma6100.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*yhm2710.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*goodix_primitives.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*goodix_heap.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gomore_primitives.c.obj(.text .text.* .rodata .rodata.*))
	KEEP(*gomore_tensor_runtime.c.obj(.text .text.* .rodata .rodata.*))
} GROUP_LINK_IN(ROMABLE_REGION)

/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_MSPI_CONTROL_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_control_41fe28.c"
static open_cfw_mspi_u8 active;static open_cfw_mspi_u32 calls[8],count;static int handle;
open_cfw_mspi_u8 *open_cfw_mspi_host_active(void){return &active;} void *open_cfw_mspi_host_handle(void){return &handle;}
void open_cfw_mspi_host_control(void *h,open_cfw_mspi_u32 mode,open_cfw_mspi_u32 one){calls[count++]=h==&handle;calls[count++]=mode;calls[count++]=one;}
void open_cfw_mspi_fixture_reset(open_cfw_mspi_u32 state){active=(open_cfw_mspi_u8)state;count=0;} open_cfw_mspi_u32 open_cfw_mspi_fixture_active(void){return active;} open_cfw_mspi_u32 open_cfw_mspi_fixture_count(void){return count;} open_cfw_mspi_u32 open_cfw_mspi_fixture_call(open_cfw_mspi_u32 i){return calls[i];}

/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the bounded G2 bootloader MSPI controls. */
typedef __UINT8_TYPE__ open_cfw_mspi_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_u32;
typedef __UINTPTR_TYPE__ open_cfw_mspi_uintptr;
enum { OPEN_CFW_MSPI_HANDLE_WORD=0x200270DCU, OPEN_CFW_MSPI_ACTIVE=0x200271C6U, OPEN_CFW_MSPI_CONTROL_THUMB=0x00426809U };
typedef open_cfw_mspi_u32 (*open_cfw_mspi_control_fn)(void *,open_cfw_mspi_u32,open_cfw_mspi_u32);
#if defined(OPEN_CFW_MSPI_CONTROL_HOST)
open_cfw_mspi_u8 *open_cfw_mspi_host_active(void);
void *open_cfw_mspi_host_handle(void);
void open_cfw_mspi_host_control(void *,open_cfw_mspi_u32,open_cfw_mspi_u32);
#endif
__attribute__((used,noinline)) void open_cfw_bootloader_mspi_enable_41fe28(void)
{
#if defined(OPEN_CFW_MSPI_CONTROL_HOST)
 open_cfw_mspi_u8 *active=open_cfw_mspi_host_active();
 if(*active!=1U){open_cfw_mspi_host_control(open_cfw_mspi_host_handle(),2U,1U);*active=1U;}
#else
 volatile open_cfw_mspi_u8 *active=(volatile open_cfw_mspi_u8 *)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_ACTIVE;
 if(*active!=1U){void *handle=*(void **)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_HANDLE_WORD;(void)((open_cfw_mspi_control_fn)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_CONTROL_THUMB)(handle,2U,1U);*active=1U;}
#endif
}
__attribute__((used,noinline)) void open_cfw_bootloader_mspi_disable_41fe48(void)
{
#if defined(OPEN_CFW_MSPI_CONTROL_HOST)
 open_cfw_mspi_host_control(open_cfw_mspi_host_handle(),0U,1U);*open_cfw_mspi_host_active()=0U;
#else
 void *handle=*(void **)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_HANDLE_WORD;(void)((open_cfw_mspi_control_fn)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_CONTROL_THUMB)(handle,0U,1U);*(volatile open_cfw_mspi_u8 *)(open_cfw_mspi_uintptr)OPEN_CFW_MSPI_ACTIVE=0U;
#endif
}

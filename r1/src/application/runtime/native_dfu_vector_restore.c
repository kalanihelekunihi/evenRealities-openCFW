#include <stdint.h>
#include <nrf_sdm.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
#define DATA(name) __attribute__((section(".r1.dfu.restore." #name),used))
DATA(app_start) const uint32_t r1_dfu_restore_app_start=0x27000u;
DATA(info_ring) const char r1_dfu_restore_info_ring[48]="[RING]Setting vector table to main app: 0x%08x";
DATA(bounds) const uint32_t r1_dfu_restore_bounds[2]={0xc44fcu,0xc441cu};
DATA(info_sdk) const char r1_dfu_restore_info_sdk[44]="Setting vector table to main app: 0x%08x";
DATA(error_ring) const char r1_dfu_restore_error_ring[60]="[RING]Failed running sd_softdevice_vector_table_base_set";
DATA(error_sdk) const char r1_dfu_restore_error_sdk[52]="Failed running sd_softdevice_vector_table_base_set";
/* Use the pinned Nordic S140 C API; its SVCALL declaration owns the
 * architectural supervisor-call ABI and service number. */
static uint32_t vector_set(uint32_t base)
{
 return sd_softdevice_vector_table_base_set(base);
}
uint32_t nrf_dfu_svci_vector_table_unset(void)
{
 uint32_t header=((r1_dfu_restore_bounds[0]-r1_dfu_restore_bounds[1])>>3)<<16;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c400000u,r1_dfu_restore_info_ring,r1_dfu_restore_info_ring,r1_dfu_restore_app_start);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(header+3,r1_dfu_restore_info_sdk,r1_dfu_restore_app_start);
 uint32_t status=vector_set(r1_dfu_restore_app_start);
 if(status){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x04000000u,r1_dfu_restore_error_ring,r1_dfu_restore_error_ring);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(header+1,r1_dfu_restore_error_sdk);
 }
 return status;
}

#define SET_DATA(name) __attribute__((section(".r1.dfu.set." #name),used))
SET_DATA(info_ring) const char r1_dfu_set_info_ring[]="[RING]Setting vector table to bootloader: 0x%08x";
SET_DATA(info_sdk) const char r1_dfu_set_info_sdk[]="Setting vector table to bootloader: 0x%08x";
SET_DATA(missing_ring) const char r1_dfu_set_missing_ring[]="[RING]No bootloader was found";
SET_DATA(missing_sdk) const char r1_dfu_set_missing_sdk[]="No bootloader was found";
#undef SET_DATA
/* Stock 0x78590 snapshots the MBR word, then uses UICR only for its erased
 * sentinel. Do not validate, align or reread the chosen base after logging.
 * SVC19 is architectural; only its modeled boundary is behavior-qualified.
 * See r1/docs/reference/dfu-vector-set-c-review.md. */
uint32_t nrf_dfu_svci_vector_table_set(void)
{
 uint32_t base=*(const volatile uint32_t *)(uintptr_t)0xff8u;
 if(base==UINT32_MAX)
  base=*(const volatile uint32_t *)(uintptr_t)0x10001014u;
 uint32_t header=((r1_dfu_restore_bounds[0]-r1_dfu_restore_bounds[1])>>3)<<16;
 if(base==UINT32_MAX){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04000000u,r1_dfu_set_missing_ring,r1_dfu_set_missing_ring);
  if(r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_0(header+1,r1_dfu_set_missing_sdk);
  return 4;
 }
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000u,r1_dfu_set_info_ring,r1_dfu_set_info_ring,base);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(header+3,r1_dfu_set_info_sdk,base);
 uint32_t status=vector_set(base);
 if(status){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04000000u,r1_dfu_restore_error_ring,r1_dfu_restore_error_ring);
  if(r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_0(header+1,r1_dfu_restore_error_sdk);
 }
 return status;
}

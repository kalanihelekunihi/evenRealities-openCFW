#include <stdint.h>
/* Build-only native control flow. Merge/persistence and identity-report effects
 * are unresolved boundaries, separate from bounded planner/runtime admission. */
extern uint32_t r1_native_nv_recovery_merge_boundary(const void *,uint32_t,uint32_t);
extern uint32_t r1_native_nv_recovery_report_boundary(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
const char r1_nv_dispatch_ring[] __attribute__((section(".r1.nv.dispatch.ring")))="[RING][NV_RECOVER] get data length error: %d, crc: %d";
const char r1_nv_dispatch_sdk[] __attribute__((section(".r1.nv.dispatch.sdk")))="[NV_RECOVER] get data length error: %d, crc: %d";
uint32_t r1_native_nv_recovery_command_dispatch(uint32_t command,uint32_t length,uint32_t crc,const void *body)
{
 if(command!=2)return command;
 if(length==116 && crc)return r1_native_nv_recovery_merge_boundary(body,length,crc);
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04800000,r1_nv_dispatch_ring,r1_nv_dispatch_ring,length,crc);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_2(0x001c0001,r1_nv_dispatch_sdk,length,crc);
 return r1_native_nv_recovery_report_boundary();
}

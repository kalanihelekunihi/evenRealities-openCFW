#include <stdint.h>
/* Authenticated native strings, including their observed padding. */
const char r1_lis_id_ring[28] __attribute__((section(".r1.lis.config.id_ring")))="[RING]LIS2DOC_ID not found";
const char r1_lis_id_sdk[24] __attribute__((section(".r1.lis.config.id_sdk")))="LIS2DOC_ID not found";
const char r1_lis_reset_ring[28] __attribute__((section(".r1.lis.config.reset_ring")))="[RING]LIS2DOC_RESET failed";
const char r1_lis_reset_sdk[24] __attribute__((section(".r1.lis.config.reset_sdk")))="LIS2DOC_RESET failed";
#include "native_lis_context.h"
extern int32_t r1_lis_default_write(void *,uint8_t,const uint8_t *,uint16_t);
extern int32_t r1_lis_default_read(void *,uint8_t,uint8_t *,uint16_t);
extern int32_t r1_lis_device_id_get(const stmdev_ctx_t *,uint8_t *);
extern uint32_t r1_lis_reg17_bit6_enable(const void *);
extern uint32_t r1_lis_native_power_mode_set(const void *,uint32_t);
extern int32_t r1_lis2dw12_fifo_read(uint8_t *,uint32_t);
extern void nrf_delay_ms(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static uint32_t lis_config_log(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,sdk);
 return 0;
}
uint32_t r1_lis2dw12_configure_boundary(uint32_t rate)
{
 volatile struct r1_lis_context_prefix *live=&r1_lis_context;
 live->write=r1_lis_default_write;
 live->read=r1_lis_default_read;
 const stmdev_ctx_t *ctx=(const void *)&r1_lis_context;
 uint8_t identity=0;
 (void)r1_lis_device_id_get(ctx,&identity);
 if(identity!=0x44)return lis_config_log(r1_lis_id_ring,r1_lis_id_sdk);
 (void)lis2dw12_reset_set(ctx,1);
 uint8_t resetting=0;
 for(uint32_t attempt=0;;attempt++){
  (void)lis2dw12_reset_get(ctx,&resetting);
  nrf_delay_ms(2);
  if(attempt>10)return lis_config_log(r1_lis_reset_ring,r1_lis_reset_sdk);
  if(!resetting)break;
 }
 (void)r1_lis_reg17_bit6_enable(ctx);
 (void)lis2dw12_block_data_update_set(ctx,1);
 (void)lis2dw12_full_scale_set(ctx,(lis2dw12_fs_t)2);
 (void)lis2dw12_filter_path_set(ctx,(lis2dw12_fds_t)0);
 (void)lis2dw12_filter_bandwidth_set(ctx,(lis2dw12_bw_filt_t)1);
 (void)lis2dw12_fifo_watermark_set(ctx,31);
 (void)lis2dw12_fifo_mode_set(ctx,(lis2dw12_fmode_t)6);
 (void)r1_lis_native_power_mode_set(ctx,10);
 uint32_t data_rate=rate==50?4u:rate==100?5u:(rate==150 || rate==200)?6u:3u;
 (void)lis2dw12_data_rate_set(ctx,(lis2dw12_odr_t)data_rate);
 nrf_delay_ms(100);
 uint8_t discarded_samples[30]={0};
 (void)r1_lis2dw12_fifo_read(discarded_samples,5);
 return 1;
}

#include <stdint.h>
/* Raw register/stack interfaces follow the observed ARM entry contracts. */
#include <stddef.h>
#include "bma4.h"
extern int8_t r1_bma4_null_pointer_check(const struct bma4_dev *dev);
extern uint32_t r1_bma4_read_regs_boundary(uint32_t reg, uint8_t *data, uint32_t length, struct bma4_dev *dev);
extern uint32_t r1_bma4_write_regs_boundary(uint32_t reg, uint8_t *data, uint32_t length, struct bma4_dev *dev);
extern uint32_t r1_bma_accel_enable_byte(uint32_t byte, uint32_t value);
_Static_assert(offsetof(struct bma4_dev,intf_ptr)==4 && offsetof(struct bma4_dev,delay_us)==44, "native Bosch enable delay fields");
uint32_t r1_bma4_set_accel_enable(uint32_t enabled, struct bma4_dev *dev)
{
 uint8_t value = 0;
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status == 0) {
  status = r1_bma4_read_regs_boundary(0x7d, &value, 1, dev);
  if (status == 0) {
   value = (uint8_t)r1_bma_accel_enable_byte(value, enabled);
   status = r1_bma4_write_regs_boundary(0x7d, &value, 1, dev);
   /* Stock delays even when the write reports failure. */
   volatile struct bma4_dev *live = dev;
   bma4_delay_us_fptr_t delay = live->delay_us;
   void *handle = live->intf_ptr;
   delay(25000, handle);
  }
 }
 return status;
}
extern int8_t r1_bma_validate_accel_parameters(uint8_t odr, uint8_t bandwidth, uint8_t performance);
_Static_assert(sizeof(struct bma4_accel_config)==4 &&
               offsetof(struct bma4_accel_config,perf_mode)==2 &&
               offsetof(struct bma4_accel_config,range)==3 &&
               offsetof(struct bma4_dev,perf_mode_status)==50,
               "native Bosch acceleration configuration fields");
uint32_t r1_bma4_set_accel_config(const struct bma4_accel_config *config, struct bma4_dev *dev)
{
 uint8_t bytes[2] = {0, 0};
 if (r1_bma4_null_pointer_check(dev) != 0 || config == 0)
  return UINT32_MAX;
 const volatile struct bma4_accel_config *live = config;
 uint8_t performance = live->perf_mode;
 uint8_t bandwidth = live->bandwidth;
 uint8_t odr = live->odr;
 uint32_t status = (uint32_t)(int32_t)r1_bma_validate_accel_parameters(odr, bandwidth, performance);
 if (status != 0)
  return status;
 odr = live->odr;
 bandwidth = live->bandwidth;
 performance = live->perf_mode;
 bytes[0] = (uint8_t)((odr & 15u) | ((uint32_t)bandwidth << 4) | ((uint32_t)performance << 7));
 bytes[1] = live->range & 3u;
 status = r1_bma4_write_regs_boundary(0x41, bytes + 1, 1, dev);
 if (status == 0) {
  status = r1_bma4_write_regs_boundary(0x40, bytes, 1, dev);
  const volatile uint8_t *live_byte = bytes;
  ((volatile struct bma4_dev *)dev)->perf_mode_status = *live_byte >> 7;
 }
 return status;
}
extern uint32_t r1_bma_fifo_config_bytes(uint32_t packed, uint32_t config, uint32_t enable);
uint32_t r1_bma4_set_fifo_config(uint32_t config, uint32_t enabled, struct bma4_dev *dev)
{
 uint8_t bytes[2] = {0, 0};
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status != 0)
  return status;
 status = r1_bma4_read_regs_boundary(0x48, bytes, 2, dev);
 if (status != 0)
  return status;
 uint32_t packed = (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8);
 packed = r1_bma_fifo_config_bytes(packed, config, enabled);
 bytes[0] = (uint8_t)packed;
 bytes[1] = (uint8_t)(packed >> 8);
 status = r1_bma4_write_regs_boundary(0x48, bytes, 1, dev);
 if (status == 0) {
  volatile struct bma4_dev *live = dev;
  bma4_delay_us_fptr_t delay = live->delay_us;
  void *handle = live->intf_ptr;
  delay(1000, handle);
  status = r1_bma4_write_regs_boundary(0x49, bytes + 1, 1, dev);
 }
 return status;
}

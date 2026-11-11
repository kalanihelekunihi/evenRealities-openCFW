#include <stdint.h>
#include <stddef.h>
#include "bma4.h"
struct bma4_dev;
extern int8_t r1_bma4_null_pointer_check(const struct bma4_dev *dev);
extern uint32_t r1_bma4_read_regs_boundary(uint32_t reg, uint8_t *data,
                                         uint32_t length, struct bma4_dev *dev);
extern uint32_t r1_bma_power_update_byte(uint32_t byte, uint32_t value);
extern uint32_t r1_bma_feature_address_bytes(uint32_t lo, uint32_t hi,
                                           const struct bma4_dev *dev);
extern uint32_t r1_bma4_read_regs_direct(uint32_t reg, uint8_t *data,
                                       uint32_t length, struct bma4_dev *dev);
uint32_t r1_bma4_write_regs_boundary(uint32_t reg, uint8_t *data,
                                    uint32_t length, struct bma4_dev *dev);
_Static_assert(offsetof(struct bma4_dev,intf_ptr)==4 &&
               offsetof(struct bma4_dev,intf)==8 &&
               offsetof(struct bma4_dev,intf_rslt)==9 &&
               offsetof(struct bma4_dev,bus_write)==40 &&
               offsetof(struct bma4_dev,delay_us)==44 &&
               offsetof(struct bma4_dev,perf_mode_status)==50,
               "native Bosch write context offsets");
uint32_t r1_bma4_write_regs_direct(uint32_t reg, const uint8_t *data,
                                  uint32_t length, struct bma4_dev *dev)
{
 if (r1_bma4_null_pointer_check(dev) != 0 || data == 0)
  return UINT32_MAX;
 volatile struct bma4_dev *live = dev;
 if (live->intf == 0)
  reg &= 0x7f;
 bma4_write_fptr_t write = live->bus_write;
 void *handle = live->intf_ptr;
 BMA4_INTF_RET_TYPE status = write((uint8_t)reg, data, length, handle);
 live->intf_rslt = status;
 if (status != 0)
  return UINT32_MAX - 1;
 uint8_t performance = live->perf_mode_status;
 bma4_delay_us_fptr_t delay = live->delay_us;
 handle = live->intf_ptr;
 delay(performance == 1 ? 2 : 450, handle);
 return 0;
}
uint32_t r1_bma4_set_advance_power_save_boundary(uint32_t enabled,
                                                struct bma4_dev *dev)
{
 uint8_t value = 0;
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status == 0) {
  status = r1_bma4_read_regs_boundary(0x7c, &value, 1, dev);
  if (status == 0) {
   value = (uint8_t)r1_bma_power_update_byte(value, enabled);
   status = r1_bma4_write_regs_boundary(0x7c, &value, 1, dev);
  }
 }
 return status;
}
extern uint32_t r1_bma4_get_advance_power_save(uint8_t *enabled, struct bma4_dev *dev);
uint32_t r1_bma4_feature_chunk_write(uint8_t *data, uint32_t length, struct bma4_dev *dev);
_Static_assert(offsetof(struct bma4_dev,feature_len)==22 && offsetof(struct bma4_dev,read_write_len)==20, "native Bosch feature write limits");
uint32_t r1_bma4_write_regs_boundary(uint32_t reg, uint8_t *data,
                                    uint32_t length, struct bma4_dev *dev)
{
 uint8_t power = 0;
 const volatile uint8_t *live_power = &power;
 if (r1_bma4_null_pointer_check(dev) != 0 || data == 0)
  return UINT32_MAX;
 if (reg != 0x5e)
  return r1_bma4_write_regs_direct(reg, data, length, dev);
 uint32_t status = r1_bma4_get_advance_power_save(&power, dev);
 if (*live_power == 1 && status == 0)
  status = r1_bma4_set_advance_power_save_boundary(0, dev);
 if (length & 1u)
  return UINT32_MAX - 9;
 const volatile struct bma4_dev *live = dev;
 if (live->feature_len < length || status != 0)
  return UINT32_MAX - 9;
 if (live->read_write_len < length)
  status = r1_bma4_feature_chunk_write(data, length, dev);
 else
  status = r1_bma4_write_regs_direct(0x5e, data, length, dev);
 if (status == 0 && *live_power == 1)
  status = r1_bma4_set_advance_power_save_boundary(1, dev);
 return status;
}
uint32_t r1_bma4_feature_address_reset(struct bma4_dev *dev)
{
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status == 0) {
  /* Native context bytes, not copied temporary values: the transport receives
   * the original field addresses and may observe changes between writes. */
  uint8_t *bytes = (uint8_t *)dev;
  status = r1_bma4_write_regs_direct(0x5b, bytes + 23, 1, dev);
  if (status == 0)
   status = r1_bma4_write_regs_direct(0x5c, bytes + 24, 1, dev);
 }
 return status;
}
uint32_t r1_bma4_feature_address_increment(struct bma4_dev *dev)
{
 uint8_t lo = 0, hi = 0;
 uint32_t status = (uint32_t)(int32_t)r1_bma4_null_pointer_check(dev);
 if (status != 0)
  return status;
 if (r1_bma4_read_regs_direct(0x5b, &lo, 1, dev) != 0 ||
     r1_bma4_read_regs_direct(0x5c, &hi, 1, dev) != 0)
  return UINT32_MAX - 1;
 uint32_t address = r1_bma_feature_address_bytes(lo, hi, dev);
 lo = (uint8_t)address;
 hi = (uint8_t)(address >> 8);
 status = r1_bma4_write_regs_direct(0x5b, &lo, 1, dev);
 if (status == 0)
  status = r1_bma4_write_regs_direct(0x5c, &hi, 1, dev);
 return status;
}
/* Ordinary transfer sizes use defined C quotient/remainder arithmetic.
 * A zero size still performs both architectural divisions before any I/O;
 * retaining that primitive avoids C undefined behavior and preserves trapping. */
extern uint32_t r1_arm_unsigned_divide_zero(uint32_t);
static inline uint32_t r1_bma_chunk_divide(uint32_t total,uint32_t size,
                                         uint16_t *remainder)
{
 if (size) {
  *remainder=(uint16_t)(total%size);
  return total/size;
 }
 uint32_t quotient=r1_arm_unsigned_divide_zero(total);
 (void)r1_arm_unsigned_divide_zero(total);
 *remainder=(uint16_t)total;
 return quotient;
}
static inline uint16_t r1_bma_live_chunk_size(const struct bma4_dev *dev)
{
 return *(const volatile uint16_t *)((const uint8_t *)dev + 20);
}
/* Failed iterations are not retried or skipped: later full chunks still run,
 * reusing the offset until both transfer and address increment succeed. */
#define CHUNKS(name,transfer) \
uint32_t name(uint8_t *data, uint32_t total, struct bma4_dev *dev) { \
 uint16_t remainder; \
 uint32_t count = r1_bma_chunk_divide(total, r1_bma_live_chunk_size(dev), &remainder); \
 uint16_t offset = 0; \
 uint32_t status = r1_bma4_feature_address_reset(dev); \
 if (status != 0) return status; \
 for (uint32_t i = 0; i < count; ++i) { \
  status = transfer(0x5e, (uint8_t *)((uintptr_t)data + offset), \
                    r1_bma_live_chunk_size(dev), dev); \
  if (status == 0) { \
   status = r1_bma4_feature_address_increment(dev); \
   if (status == 0) \
    offset = (uint16_t)(offset + r1_bma_live_chunk_size(dev)); \
  } \
 } \
 if (remainder != 0 && status == 0) \
  status = transfer(0x5e, (uint8_t *)((uintptr_t)data + offset), remainder, dev); \
 return status == 0 ? r1_bma4_feature_address_reset(dev) : status; \
}
CHUNKS(r1_bma4_feature_chunk_read_boundary,r1_bma4_read_regs_direct)
CHUNKS(r1_bma4_feature_chunk_write,r1_bma4_write_regs_direct)

#include <stdint.h>
#include "bma4.h"
struct bma4_dev;
extern int8_t r1_bma4_null_pointer_check(const struct bma4_dev *dev);
extern uint32_t r1_bma4_read_regs_boundary(uint32_t, uint8_t *, uint32_t,
                                         struct bma4_dev *);
uint32_t r1_bma4_get_fifo_length(uint16_t *length, struct bma4_dev *dev)
{
 uint8_t bytes[4] = {0, 0, 0, 0};
 if (r1_bma4_null_pointer_check(dev) != 0 || length == 0)
  return UINT32_MAX;
 uint32_t status = r1_bma4_read_regs_boundary(0x24, bytes, 2, dev);
 if (status == 0) {
  bytes[1] &= 0x3f;
  *length = (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
 }
 return status;
}
uint32_t r1_bma_fifo_read_bytes(uint8_t *data, uint32_t length,
                                 struct bma4_dev *dev)
{
 uint16_t available = 0;
 const volatile uint16_t *live_available = &available;
 if (r1_bma4_null_pointer_check(dev) != 0 || data == 0 || length == 0)
  return UINT32_MAX;
 volatile struct bma4_dev *live = dev;
 uint8_t reg = live->intf == 0 ? 0xa6 : 0x26;
 if (r1_bma4_get_fifo_length(&available, dev) != 0)
  return UINT32_MAX - 1;
 if (*live_available == 0)
  return 0;
 if (*live_available > length)
  available = (uint16_t)length;
 bma4_read_fptr_t read = live->bus_read;
 uint16_t request = *live_available;
 void *handle = live->intf_ptr;
 BMA4_INTF_RET_TYPE status = read(reg, data, request, handle);
 live->intf_rslt = status;
 if (status != 0)
  return UINT32_MAX - 1;
 return (uint32_t)(int32_t)(int16_t)*live_available;
}
extern struct bma4_dev r1_bma_context;
extern uint32_t r1_bma4_set_advance_power_save_boundary(uint32_t, struct bma4_dev *);
extern void r1_bma_delay_us(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
extern const char r1_bma_fifo_disable_ring[52], r1_bma_fifo_disable_sdk[48];
extern const char r1_bma_fifo_read_ring[40], r1_bma_fifo_read_sdk[36];
extern const char r1_bma_fifo_enable_ring[52], r1_bma_fifo_enable_sdk[44];
static void r1_bma_fifo_log_failure(const char *ring, const char *sdk, uint32_t status)
{
 if ((r1_structured_log_mode_get() & 1u) ||
     (r1_structured_log_mode_get() & 4u))
  r1_structured_log_format(UINT32_C(0x04400000), ring, ring, status);
 if (r1_structured_log_mode_get() & 2u)
  nrf_log_frontend_std_1(UINT32_C(0x001c0001), sdk, status);
}
uint32_t r1_bma456w_fifo_read(uint8_t *data, uint32_t samples)
{
 if (data == 0 || samples == 0)
  return UINT32_MAX;
 uint32_t status = r1_bma4_set_advance_power_save_boundary(0, &r1_bma_context);
 if (status != 0) {
  r1_bma_fifo_log_failure(r1_bma_fifo_disable_ring, r1_bma_fifo_disable_sdk, status);
  return 0;
 }
 r1_bma_delay_us(450);
 /* Stock wraps the byte request to 16 bits after multiplying by six. */
 uint32_t count = r1_bma_fifo_read_bytes(data, (uint16_t)(samples * 6u),
                                      &r1_bma_context);
 /* Keep the outer native full-word return contract across C callee analysis. */
 const volatile uint32_t *live_count = &count;
 if ((int32_t)*live_count < 0) {
  r1_bma_fifo_log_failure(r1_bma_fifo_read_ring, r1_bma_fifo_read_sdk, *live_count);
  return UINT32_MAX;
 }
 status = r1_bma4_set_advance_power_save_boundary(1, &r1_bma_context);
 if (status != 0) {
  r1_bma_fifo_log_failure(r1_bma_fifo_enable_ring, r1_bma_fifo_enable_sdk, status);
  return 0;
 }
 return (uint32_t)((int32_t)*live_count / 6);
}
const char r1_bma_fifo_disable_ring[52] __attribute__((section(".r1.bma.fifo.disable_ring")))="[RING]BMA456 disable advance power save failed: %d";
const char r1_bma_fifo_disable_sdk[48] __attribute__((section(".r1.bma.fifo.disable_sdk")))="BMA456 disable advance power save failed: %d";
const char r1_bma_fifo_read_ring[40] __attribute__((section(".r1.bma.fifo.read_ring")))="[RING]BMA456 read fifo data failed: %d";
const char r1_bma_fifo_read_sdk[36] __attribute__((section(".r1.bma.fifo.read_sdk")))="BMA456 read fifo data failed: %d";
const char r1_bma_fifo_enable_ring[52] __attribute__((section(".r1.bma.fifo.enable_ring")))="[RING]BMA456 enable advance power save failed: %d";
const char r1_bma_fifo_enable_sdk[44] __attribute__((section(".r1.bma.fifo.enable_sdk")))="BMA456 enable advance power save failed: %d";

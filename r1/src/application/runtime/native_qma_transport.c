#include <stdint.h>
#include <stddef.h>
typedef void (*r1_qma_event)(void);
struct r1_qma_runtime {uint8_t address;uint8_t padding[3];r1_qma_event double_tap,any_motion;};
_Static_assert(sizeof(struct r1_qma_runtime)==12 && offsetof(struct r1_qma_runtime,double_tap)==4 && offsetof(struct r1_qma_runtime,any_motion)==8,"native QMA runtime prefix");
/* Exact cold runtime record; distinct from the sensor-state address at2001e4b0. */
struct r1_qma_runtime r1_qma_runtime __attribute__((section(".r1.qma.runtime"),aligned(4)))={.address=0x12};
extern void r1_rtt_delay_cycles(uint32_t cycles);
/* Retain the native call boundary used by the transport retry path. */
__attribute__((noinline)) uint32_t r1_qma_delay_units(uint32_t units)
{
 if(!units)return 0;
 do {r1_rtt_delay_cycles(64000);} while(--units!=0);
 return UINT32_MAX-1u;
}
extern uint32_t r1_motion_bus_read_request(uint32_t, uint32_t, uint8_t *, uint32_t);
extern uint32_t r1_motion_bus_write_request(uint32_t, uint32_t, const uint8_t *, uint32_t);
uint32_t r1_qma_read_retry(uint32_t reg, uint8_t *data, uint32_t length)
{
 const volatile struct r1_qma_runtime *live = &r1_qma_runtime;
 for (uint32_t attempt = 0; attempt < 5; ++attempt) {
  uint8_t address = live->address;
  if (r1_motion_bus_read_request(address, reg, data, length) != 0)
   return 1;
  (void)r1_qma_delay_units(5);
 }
 return 0;
}
uint32_t r1_qma_write_retry(uint32_t reg, uint32_t value)
{
 const volatile struct r1_qma_runtime *live = &r1_qma_runtime;
 for (uint32_t attempt = 0; attempt < 5; ++attempt) {
  uint8_t address = live->address;
  if (r1_motion_bus_write_request(address, reg, (const uint8_t *)&value, 1) != 0)
   return 1;
 }
 return 0;
}
/* A non-writing read has a defined zero ID, independent of caller scratch. */
uint32_t r1_qma6100_chip_id(void)
{
 uint8_t value=0;
 (void)r1_qma_read_retry(0,&value,1);
 return value;
}
__attribute__((used,noinline)) uint32_t r1_qma_irq_body(volatile uint32_t *status)
{
 *status = 0;
 const volatile uint8_t *bytes = (const volatile uint8_t *)status;
 const volatile struct r1_qma_runtime *live = &r1_qma_runtime;
 for (uint32_t attempt = 0; attempt < 10; ++attempt) {
  uint32_t result = r1_qma_read_retry(9, (uint8_t *)(uintptr_t)status, 4);
  if ((uint8_t)result == 0)
   continue;
  if (((uint32_t)bytes[0] << 29) != 0) {
   r1_qma_event event = live->any_motion;
   if (event != 0)
    event();
  }
  uint32_t shifted = (uint32_t)bytes[1] << 26;
  if ((shifted & UINT32_C(0x80000000)) == 0)
   return shifted;
  r1_qma_event event = live->double_tap;
  if(event)event();
  return 0;
 }
 return 10;
}
/* The IRQ status starts at zero and remains live across read attempts.
 * The motion interrupt consumer discards the provider result. */
uint32_t r1_qma6100_irq_boundary(void)
{
 volatile uint32_t status;
 return r1_qma_irq_body(&status);
}

const char r1_qma_fifo_string_870bc[36] __attribute__((section(".r1.qma.fifo.s870bc")))="[RING]qma6100_read_fifo state error";
const char r1_qma_fifo_string_870e0[32] __attribute__((section(".r1.qma.fifo.s870e0")))="qma6100_read_fifo state error";
const char r1_qma_fifo_string_87100[40] __attribute__((section(".r1.qma.fifo.s87100")))="[RING]qma6100_read_fifo depth(%d) error";
const char r1_qma_fifo_string_87128[36] __attribute__((section(".r1.qma.fifo.s87128")))="qma6100_read_fifo depth(%d) error";
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_0(uint32_t, const char *);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
/* A successful provider which writes no depth byte has defined depth zero. */
uint32_t r1_qma6100_bounded_fifo_read(uint8_t *data,uint32_t capacity)
{
 uint8_t depth_byte=0;
 if (data == 0)
  return UINT32_MAX;
 if (r1_qma_read_retry(0x0e, &depth_byte, 1) != 1) {
  if ((r1_structured_log_mode_get() & 1u) ||
      (r1_structured_log_mode_get() & 4u))
   (void)r1_structured_log_format(UINT32_C(0x04000000),
    r1_qma_fifo_string_870bc, r1_qma_fifo_string_870bc);
  if (r1_structured_log_mode_get() & 2u)
   nrf_log_frontend_std_0(UINT32_C(0x001c0001), r1_qma_fifo_string_870e0);
  return UINT32_MAX;
 }
 uint32_t depth = depth_byte & 0x7fu;
 if (depth > 64) {
  if ((r1_structured_log_mode_get() & 1u) ||
      (r1_structured_log_mode_get() & 4u))
   (void)r1_structured_log_format(UINT32_C(0x04400000),
    r1_qma_fifo_string_87100, r1_qma_fifo_string_87100, depth);
  if (r1_structured_log_mode_get() & 2u)
   nrf_log_frontend_std_1(UINT32_C(0x001c0001), r1_qma_fifo_string_87128, depth);
  return 0;
 }
 if (capacity > depth)
  capacity = depth;
 (void)r1_qma_read_retry(0x3f, data, (uint16_t)(capacity * 6u));
 (void)r1_qma_write_retry(0x3e, 0x87);
 return capacity;
}

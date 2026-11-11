#include <stdint.h>
#include <stddef.h>
#include "bma4.h"
struct bma4_dev;
extern int8_t r1_bma4_null_pointer_check(const struct bma4_dev *dev);
extern void r1_bma_copy_read_bytes(uint8_t *,const uint8_t *,uint32_t,
                                  const volatile struct bma4_dev *);
_Static_assert(offsetof(struct bma4_dev,intf)==8 &&
               offsetof(struct bma4_dev,intf_rslt)==9 &&
               offsetof(struct bma4_dev,dummy_byte)==11 &&
               offsetof(struct bma4_dev,bus_read)==36 &&
               offsetof(struct bma4_dev,intf_ptr)==4,"native read context");
/* Native transport callbacks use full register/result words. The registered
 * pinned Bosch type describes only the low byte; the product adapter itself
 * has this full-word ABI. In particular, a raw 0x100 status is still failure. */
typedef uint32_t (*r1_bma_native_read)(uint32_t,uint8_t *,uint32_t,void *);
typedef uint32_t r1_bma_callback_word __attribute__((may_alias));
__attribute__((used,noinline)) static uint32_t bma_direct_read_body(
 uint32_t reg,uint8_t *data,uint32_t length,struct bma4_dev *dev,uint8_t *buffer)
{
 if(r1_bma4_null_pointer_check(dev)!=0 || data==0)
  return UINT32_MAX;
 volatile struct bma4_dev *live=dev;
 if(live->intf==0)reg|=0x80u;
 uint32_t dummy=live->dummy_byte;
 /* Load the native slot as one word rather than calling through the pinned
  * byte-result prototype or casting one incompatible function type to another. */
 uintptr_t address=*(const volatile r1_bma_callback_word *)
                      ((const uint8_t *)dev+offsetof(struct bma4_dev,bus_read));
 r1_bma_native_read read=(r1_bma_native_read)address;
 void *handle=live->intf_ptr;
 uint32_t status=read(reg,buffer,length+dummy,handle);
 live->intf_rslt=(BMA4_INTF_RET_TYPE)status;
 if(status!=0)return UINT32_MAX-1u;
 r1_bma_copy_read_bytes(data,buffer,length,dev);
 return 0;
}
/* The first 128 bytes remain uninitialized transport scratch. The extra
 * 16-byte reservation makes Clang's C wrapper publish entry SP minus 152,
 * matching stock and the former assembly bridge. The outgoing fifth argument
 * and private saves differ from stock; bounded callback data is unchanged.
 * Keep the generated frame and callback pointer under differential review. */
__attribute__((noinline)) uint32_t r1_bma4_read_regs_direct(
 uint32_t reg,uint8_t *data,uint32_t length,struct bma4_dev *dev)
{
 uint8_t buffer[144];
 return bma_direct_read_body(reg,data,length,dev,buffer);
}
uint32_t r1_bma4_get_advance_power_save(uint8_t *enabled, struct bma4_dev *dev);
extern uint32_t r1_bma4_set_advance_power_save_boundary(uint32_t enabled, struct bma4_dev *dev);
extern uint32_t r1_bma4_feature_chunk_read_boundary(uint8_t *data, uint32_t length, struct bma4_dev *dev);
_Static_assert(offsetof(struct bma4_dev,feature_len)==22 &&
               offsetof(struct bma4_dev,read_write_len)==20,
               "native Bosch feature read limits");
uint32_t r1_bma4_read_regs_boundary(uint32_t reg, uint8_t *data,
                                    uint32_t length, struct bma4_dev *dev)
{
 uint8_t power = 0;
 const volatile uint8_t *live_power = &power;
 if (r1_bma4_null_pointer_check(dev) != 0 || data == 0)
  return UINT32_MAX;
 if (reg != 0x5e)
  return r1_bma4_read_regs_direct(reg, data, length, dev);
 uint32_t status = r1_bma4_get_advance_power_save(&power, dev);
 if (*live_power == 1)
  status = r1_bma4_set_advance_power_save_boundary(0, dev);
 if (length & 1u)
  return UINT32_MAX - 9;
 const volatile struct bma4_dev *live = dev;
 if (live->feature_len < length || status != 0)
  return UINT32_MAX - 9;
 if (live->read_write_len < length)
  status = r1_bma4_feature_chunk_read_boundary(data, length, dev);
 else
  status = r1_bma4_read_regs_direct(0x5e, data, length, dev);
 if (status == 0 && *live_power == 1)
  status = r1_bma4_set_advance_power_save_boundary(1, dev);
 return status;
}
uint32_t r1_bma4_get_advance_power_save(uint8_t *enabled, struct bma4_dev *dev)
{
 uint8_t value = 0;
 if (r1_bma4_null_pointer_check(dev) != 0 || enabled == 0)
  return UINT32_MAX;
 uint32_t status = r1_bma4_read_regs_boundary(0x7c, &value, 1, dev);
 if (status == 0)
  *enabled = value & 1u;
 return status;
}
extern struct bma4_dev r1_bma_context;
extern uint32_t r1_bma_interface_initialize(struct bma4_dev *dev);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
extern const char r1_bma_init_ring[40], r1_bma_init_sdk[36];
extern const char r1_bma_id_ring[40], r1_bma_id_sdk[32];
_Static_assert(offsetof(struct bma4_dev, bus_read) == 36,
               "native Bosch identity transport callback");
uint32_t r1_bma456w_identity_probe(void)
{
 uint8_t chip_id = 0;
 uint32_t status = 0;
 const char *ring = r1_bma_init_ring;
 const char *sdk = r1_bma_init_sdk;
 if (r1_bma_context.bus_read == 0)
  status = r1_bma_interface_initialize(&r1_bma_context);
 if (status == 0) {
  status = r1_bma4_read_regs_boundary(0, &chip_id, 1, &r1_bma_context);
  if (status == 0)
   return chip_id;
  ring = r1_bma_id_ring;
  sdk = r1_bma_id_sdk;
 }
 /* Each mode query is a separate observable call, including short circuiting. */
 if ((r1_structured_log_mode_get() & 1u) ||
     (r1_structured_log_mode_get() & 4u))
  r1_structured_log_format(UINT32_C(0x04400000), ring, ring, status);
 if (r1_structured_log_mode_get() & 2u)
  nrf_log_frontend_std_1(UINT32_C(0x001c0001), sdk, status);
 return 0;
}
const char r1_bma_init_ring[40] __attribute__((section(".r1.bma.id.init_ring")))="[RING]BMA456 interface init failed: %d";
const char r1_bma_init_sdk[36] __attribute__((section(".r1.bma.id.init_sdk")))="BMA456 interface init failed: %d";
const char r1_bma_id_ring[40] __attribute__((section(".r1.bma.id.id_ring")))="[RING]BMA456 read chip id failed: %d";
const char r1_bma_id_sdk[32] __attribute__((section(".r1.bma.id.id_sdk")))="BMA456 read chip id failed: %d";

#include <stdint.h>
#include <stddef.h>
#include "bma4.h"
_Static_assert(sizeof(struct bma4_dev)==52,"pinned ARM BMA layout");
_Static_assert(offsetof(struct bma4_dev,intf_ptr)==4 && offsetof(struct bma4_dev,intf)==8 && offsetof(struct bma4_dev,intf_rslt)==9 && offsetof(struct bma4_dev,variant)==13 && offsetof(struct bma4_dev,read_write_len)==20 && offsetof(struct bma4_dev,bus_read)==36 && offsetof(struct bma4_dev,bus_write)==40 && offsetof(struct bma4_dev,delay_us)==44 && offsetof(struct bma4_dev,perf_mode_status)==50,"native field offsets");
/* Layout matches the pinned API; full native allocation extent remains gated. */
struct bma4_dev r1_bma_context __attribute__((section(".bss.r1.bma.context"),aligned(4)));
uint32_t r1_bma_bus_address __attribute__((section(".r1.bma.bus_address"),aligned(4)))=0x18;
extern uint32_t r1_motion_bus_read_request(uint32_t, uint32_t, uint8_t *, uint32_t);
extern uint32_t r1_motion_bus_write_request(uint32_t, uint32_t, const uint8_t *, uint32_t);
/* Native adapters keep full register/error words, truncate transfer length to
 * 16 bits and load only the address byte from the opaque interface handle. */
uint32_t r1_bma_default_read(uint32_t reg, uint8_t *data, uint32_t length,
                             const void *handle)
{
 uint8_t address = *(const volatile uint8_t *)handle;
 return r1_motion_bus_read_request(address, reg, data, (uint16_t)length)
        ? 0 : UINT32_MAX - 1;
}
uint32_t r1_bma_default_write(uint32_t reg, const uint8_t *data, uint32_t length,
                              const void *handle)
{
 uint8_t address = *(const volatile uint8_t *)handle;
 return r1_motion_bus_write_request(address, reg, data, (uint16_t)length)
        ? 0 : UINT32_MAX - 1;
}
/* SDK callbacks use their declared C types; native ports retain their
 * full-word API. The shared delay has one argument and ignores no hidden word. */
extern void r1_bma_delay_us(uint32_t);
static int8_t r1_bma_registered_read(uint8_t reg,uint8_t *data,uint32_t length,void *handle)
{
 return r1_bma_default_read(reg,data,length,handle)?-2:0;
}
static int8_t r1_bma_registered_write(uint8_t reg,const uint8_t *data,uint32_t length,void *handle)
{
 return r1_bma_default_write(reg,data,length,handle)?-2:0;
}
static void r1_bma_registered_delay(uint32_t us,void *handle)
{
 (void)handle;
 r1_bma_delay_us(us);
}
/* Volatile field stores preserve the native registration order and widths. */
uint32_t r1_bma_interface_initialize(struct bma4_dev *dev)
{
 if (dev == 0)
  return UINT32_MAX;
 volatile struct bma4_dev *live = dev;
 live->intf = BMA4_I2C_INTF;
 live->bus_read = r1_bma_registered_read;
 live->bus_write = r1_bma_registered_write;
 live->intf_ptr = &r1_bma_bus_address;
 live->delay_us = r1_bma_registered_delay;
 live->read_write_len = 64;
 live->variant = 3;
 live->perf_mode_status = 0;
 return 0;
}

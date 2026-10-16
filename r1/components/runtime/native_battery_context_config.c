#include <stdint.h>
/* Only missing slices are defined here. Linker composition reuses the status
 * bytes44/45 and ADC cache at runtime offset16 as their existing storage owners. */
volatile uint8_t r1_battery_device_prefix[44] __attribute__((section(".r1.battery.device.prefix"),aligned(4)))={0};
volatile uint8_t r1_battery_device_tail[22] __attribute__((section(".r1.battery.device.tail")))={0};
volatile uint8_t r1_battery_runtime_prefix[16] __attribute__((section(".r1.battery.runtime.prefix"),aligned(4)))={[0]=255,[3]=255};
struct r1_battery_runtime_tail {uint8_t bytes20_43[24];uint16_t cadence[4][6];};
_Static_assert(sizeof(struct r1_battery_runtime_tail)==72,"recovered runtime tail extent");
volatile struct r1_battery_runtime_tail r1_battery_runtime_tail
 __attribute__((section(".r1.battery.runtime.tail"),aligned(2)))={
 {0},{{38,60,108,480,4350,300},{48,72,144,480,4350,300},
      {38,60,108,480,4350,300},{48,72,144,480,4350,300}}};
void *volatile r1_battery_thread_handle __attribute__((section(".r1.battery.thread"),aligned(4)))=0;
void *volatile r1_low_battery_thread_handle __attribute__((section(".r1.battery.low.thread"),aligned(4)))=0;
volatile uint32_t r1_shared_power_clients __attribute__((section(".r1.battery.power.clients"),aligned(4)))=0;

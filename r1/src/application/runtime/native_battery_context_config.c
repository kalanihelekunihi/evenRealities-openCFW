#include "../board/native_battery_context.h"
/* Native device 0x20016b84 is cold-zeroed. Runtime 0x20006890 has two
 * sentinel bytes and four six-halfword cadence rows in initialized RAM. */
volatile union r1_battery_device_store r1_battery_device_storage
 __attribute__((section(".r1.battery.device"),aligned(4)))={.bytes={0}};
volatile union r1_battery_runtime_store r1_battery_runtime_storage
 __attribute__((section(".r1.battery.runtime"),aligned(4)))={.fields={
 .prefix={[0]=255,[3]=255},.adc=0,.bytes20_43={0},
 .cadence={{38,60,108,480,4350,300},{48,72,144,480,4350,300},
           {38,60,108,480,4350,300},{48,72,144,480,4350,300}}
 }};
void *volatile r1_battery_thread_handle __attribute__((section(".r1.battery.thread"),aligned(4)))=0;
void *volatile r1_low_battery_thread_handle __attribute__((section(".r1.battery.low.thread"),aligned(4)))=0;
volatile uint32_t r1_shared_power_clients __attribute__((section(".r1.battery.power.clients"),aligned(4)))=0;

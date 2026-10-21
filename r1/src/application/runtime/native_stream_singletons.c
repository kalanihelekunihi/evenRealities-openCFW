#include <stdint.h>
#include "../board/native_battery_memory.h"
extern void *r1_stream_object_create(const char *,uint32_t,const void *,uint32_t);
/* These are real provider boundaries, not empty implementations. */
extern uint32_t r1_motion_initialize_entry(uint32_t);
extern uint32_t r1_motion_stream_close_boundary(uint32_t);
extern uint32_t r1_motion_thirty_sample_batch_producer(uint8_t *,uint32_t,uint32_t);
extern uint32_t r1_temperature_pair_read_calibrated(void);
typedef struct {uint32_t (*open)(uint32_t);uint32_t (*close)(uint32_t);uint32_t (*read)(uint8_t *,uint32_t,uint32_t);} r1_sensor_ops;
_Static_assert(sizeof(r1_sensor_ops)==12,"native provider table size");
uint32_t r1_stream_temperature_open(uint32_t context __attribute__((unused))){return 1;}
uint32_t r1_stream_temperature_close(uint32_t context __attribute__((unused))){return 1;}
uint32_t r1_stream_temperature_read(uint8_t *destination,uint32_t length,uint32_t context __attribute__((unused)))
{
 if(!destination || length!=2)return 0;
 uint32_t sample=r1_temperature_pair_read_calibrated();write16(destination,sample);return 2;
}
const r1_sensor_ops r1_stream_acc_ops __attribute__((section(".r1.stream.acc.ops"),aligned(4)))={r1_motion_initialize_entry,r1_motion_stream_close_boundary,r1_motion_thirty_sample_batch_producer};
const r1_sensor_ops r1_stream_temp_ops __attribute__((section(".r1.stream.temp.ops"),aligned(4)))={r1_stream_temperature_open,r1_stream_temperature_close,r1_stream_temperature_read};
const char r1_stream_acc_name[] __attribute__((section(".r1.stream.acc.name")))="acc";
const char r1_stream_temp_name[] __attribute__((section(".r1.stream.temp.name")))="temp";
void *r1_native_accelerometer_singleton(void){return r1_stream_object_create(r1_stream_acc_name,188,&r1_stream_acc_ops,0);}
void *r1_native_temperature_singleton(void){return r1_stream_object_create(r1_stream_temp_name,2,&r1_stream_temp_ops,0);}

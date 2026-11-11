#include <stdint.h>
#include "native_kv_class.h"
#include "native_battery_memory.h"
extern void *volatile r1_device_info_record_kv_handle;
/* Stock 0x73710 under its ordinary void API. Complete reads preserve the
 * ordered field updates; failed/short reads retain initialized zero bytes. */
void r1_kv_dev_info_fields_set(volatile void *data)
{
    const volatile uint8_t *input=data;
    if (!input) return;
    volatile uint8_t record[52]={0};
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,(void *)record,52);
    write32(record+36,read32(input));
    uint32_t kind=input[4];
    write32(record+40,(read32(record+40)&0xfffffffcu)|(kind&3u));
    uint32_t voltage=read16(input+4)>>2;
    write32(record+40,(read32(record+40)&0xffff0003u)|(voltage<<2));
    (void)r1_kv_class_write(r1_device_info_record_kv_handle,(const void *)record,52);
}

/* Authenticated R1 cached-class operations. No flash implementation is implied. */
#include "native_kv_class.h"
#include <string.h>
extern void *volatile r1_health_record_kv_handle;
uint32_t r1_kv_class_read(void *handle,void *destination,uint32_t size)
{
    struct r1_kv_class_view *node=handle;
    if (node->payload_size!=size) return 5;
    r1_kv_port->enter();
    memcpy(destination,node->payload,size);
    r1_kv_port->leave();
    return 0;
}
uint32_t r1_kv_class_write(void *handle,const void *source,uint32_t size)
{
    struct r1_kv_class_view *node=handle;
    if (node->payload_size!=size) return 5;
    r1_kv_port->enter();
    node->flags=(uint16_t)(node->flags|1u);
    memcpy(node->payload,source,size);
    r1_kv_port->leave();
    return 0;
}
uint32_t r1_health_record_read(void *destination)
{ return destination ? r1_kv_class_read(r1_health_record_kv_handle,destination,24):0; }
uint32_t r1_health_record_write(const void *source)
{ return source ? r1_kv_class_write(r1_health_record_kv_handle,source,24):0; }

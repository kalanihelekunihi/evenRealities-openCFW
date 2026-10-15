#include <stdint.h>
#include <string.h>

extern volatile uint8_t r1_structured_log_mode;
struct r1_log_cache_state { uint8_t *buffer; uint32_t capacity, read, write; };
uint8_t r1_structured_log_cache_buffer[8192]
    __attribute__((section(".r1.log.cache_buffer"),aligned(4)));
struct r1_log_cache_state r1_structured_log_cache
    __attribute__((section(".r1.log.cache"),aligned(4))) = { r1_structured_log_cache_buffer,8192,0,0 };
uint8_t r1_structured_log_export_buffer[236]
    __attribute__((section(".r1.log.export_buffer"),aligned(4)));
extern uint32_t r1_structured_log_cache_copy(uint32_t peek,void *buffer,uint32_t bytes);
extern uint32_t r1_conn_field6_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type2(uint32_t connection,const void *buffer,uint32_t bytes);
extern uint32_t r1_event_publish(uint32_t event,const void *argument,uint32_t bytes);

/* 0x41e80: strict admission leaves a second unused byte. Trigger occupancy
 * intentionally uses the pre-copy free-space snapshot. No locking is added. */
void r1_structured_log_cache_append(const void *record,uint32_t bytes)
{
    uint32_t capacity=r1_structured_log_cache.capacity;
    uint32_t read=r1_structured_log_cache.read;
    uint32_t write=r1_structured_log_cache.write;
    uint8_t *buffer=r1_structured_log_cache.buffer;
    if (read>capacity || write>capacity) return;
    uint32_t free_bytes=(write<read ? read-write : capacity-(write-read))-1;
    uint32_t accepted=bytes<free_bytes;
    if (accepted) {
        uint32_t tail=capacity-write;
        if (tail<bytes) {
            memcpy(buffer+write,record,tail);
            memcpy(buffer,(const uint8_t *)record+tail,bytes-tail);
        } else memcpy(buffer+write,record,bytes);
        r1_structured_log_cache.write=tail<=bytes ? bytes-tail : write+bytes;
    }
    if (r1_structured_log_mode & 4u) {
        if (!accepted || capacity-free_bytes>=236u) {
            r1_structured_log_cache_copy(0,r1_structured_log_export_buffer,236);
            uint32_t connection=r1_conn_field6_get();
            r1_ble_tx_queue_dispatch_type2(connection,r1_structured_log_export_buffer,236);
        }
    } else if ((r1_structured_log_mode & 1u) &&
               (!accepted || capacity-free_bytes>=4096u)) {
        r1_event_publish(0x2003,0,0);
    }
}

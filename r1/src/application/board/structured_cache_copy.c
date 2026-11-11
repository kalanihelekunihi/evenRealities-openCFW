#include <stdint.h>
#include <string.h>
#include "cmsis_gcc.h"

struct r1_log_cache_state { uint8_t *buffer; uint32_t capacity, read, write; };
extern struct r1_log_cache_state r1_structured_log_cache;
extern void vPortEnterCritical(void);
extern void vPortExitCritical(void);
uint32_t r1_structured_log_cache_copy(uint32_t peek,void *destination,uint32_t bytes);

/* Stock 0x41d08 and its 0x91490 tail entry use the same cursor admission
 * arithmetic as the copy provider, narrowing the result to 16 bits. */
uint32_t r1_structured_log_cache_available(void)
{
    uint32_t capacity=r1_structured_log_cache.capacity;
    uint32_t read=r1_structured_log_cache.read;
    uint32_t write=r1_structured_log_cache.write;
    if (read>capacity || write>capacity) return 0;
    return (uint16_t)(write<read ?
        capacity-(read-write) : write-read);
}
uint32_t r1_structured_log_cache_count(void)
{ return r1_structured_log_cache_available(); }

/* Stock 0x91460: nonzero all snapshots the available count into the caller's
 * halfword; zero uses the caller-supplied count. Neither branch consumes data. */
uint32_t r1_structured_log_cache_read(void *destination,uint16_t *length,
                                      uint32_t all)
{
    if (!destination || !length) return 0;
    if (all) {
        uint16_t available=(uint16_t)r1_structured_log_cache_available();
        uint32_t copied=r1_structured_log_cache_copy(1,destination,available);
        *length=available;
        return copied;
    }
    return r1_structured_log_cache_copy(1,destination,*length);
}

/* 0x41c5c. Nonzero peek preserves the read cursor. Admission and cached ring
 * values precede the critical section, exactly as in stock. */
uint32_t r1_structured_log_cache_copy(uint32_t peek,void *destination,uint32_t bytes)
{
    uint32_t capacity=r1_structured_log_cache.capacity;
    uint32_t read=r1_structured_log_cache.read;
    uint32_t write=r1_structured_log_cache.write;
    uint8_t *buffer=r1_structured_log_cache.buffer;
    if (read>capacity || write>capacity) return 0;
    uint32_t available=write<read ? capacity-(read-write) : write-read;
    if (bytes>available) return 0;
    uint32_t saved=0;
    if (__get_IPSR()!=0) { saved=__get_BASEPRI(); __set_BASEPRI(64); }
    else vPortEnterCritical();
    uint32_t tail=capacity-read;
    if (tail<bytes) {
        memcpy(destination,buffer+read,tail);
        memcpy((uint8_t *)destination+tail,buffer,bytes-tail);
    } else memcpy(destination,buffer+read,bytes);
    if (peek==0) r1_structured_log_cache.read=tail<=bytes ? bytes-tail : read+bytes;
    if (__get_IPSR()!=0) __set_BASEPRI((uint8_t)saved);
    else vPortExitCritical();
    return 1;
}

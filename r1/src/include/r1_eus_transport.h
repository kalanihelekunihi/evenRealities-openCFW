#ifndef R1_EUS_TRANSPORT_H
#define R1_EUS_TRANSPORT_H
#include <stdint.h>
/* Shared wire contract:247-byte ATT MTU minus3 ATT bytes and5 transport bytes. */
enum {
 R1_EUS_HEADER_SIZE=5,
 R1_EUS_FRAGMENT_PAYLOAD=239,
 R1_EUS_MAX_WIRE_SIZE=R1_EUS_HEADER_SIZE+R1_EUS_FRAGMENT_PAYLOAD,
 R1_EUS_MAX_MESSAGE_SIZE=4096,
 R1_EUS_MAX_COUNTER=R1_EUS_MAX_MESSAGE_SIZE/R1_EUS_FRAGMENT_PAYLOAD,
 R1_EUS_STATIC_CAPACITY=2*R1_EUS_FRAGMENT_PAYLOAD
};
typedef int32_t (*r1_eus_send_callback_t)(uint32_t,const void *,uint32_t);
#endif

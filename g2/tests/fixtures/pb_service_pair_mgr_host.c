#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static uint8_t auth_flag;
static uint8_t controller[0x60];
static uint8_t allocation[0x1a8];
static uint8_t encoded_message[48];
static uint8_t sent_message[512];
static uint32_t sent_length;
static uint32_t send_count;
static uint32_t notify_count;
static int notify_result;
static int encode_result = 1;
static uint32_t free_count;
static uint32_t sequence = 0x1234;
static uint32_t calls[32];
static uint8_t wsf_message[12];
static uint8_t *wsf_allocation = wsf_message;

uint32_t pair_test_encode(void *, const void *, const void *);
int pair_test_send(uint32_t, uint32_t, const void *, uint32_t);
int pair_test_notify(uint32_t, uint32_t, const void *, uint32_t);
void *pair_test_allocate(uint32_t);
void pair_test_free(void *);
uint32_t pair_test_sequence(void);
void pair_test_remove(const void *);
void pair_test_push(const void *, uint32_t, uint32_t);
void pair_test_connection_state(uint32_t);
void pair_test_slave_role(uint32_t);
void pair_test_target_set(const uint8_t *, const uint8_t *, uint32_t);
uint32_t pair_test_auth_mode(uint32_t);
void pair_test_target_copy(uint8_t *, uint8_t *);
int pair_test_link_matches(const uint8_t *);
int pair_test_owner_side(void);
void pair_test_retry_reset(void);
void pair_test_failure_clear(void);
void pair_test_failure_begin(void);
void pair_test_policy_mark(uint32_t);
int pair_test_policy_blocked(uint32_t);
void pair_test_connect_timeout(void);
void pair_test_connect_timeout_cancel(void);
void pair_test_connect_success(void);
void pair_test_policy_reset(void);
void pair_test_throttle_reset(void);
void pair_test_peer_event(uint32_t);
void pair_test_ble_zero(uint32_t);
void pair_test_ble_nonzero(uint32_t);
void pair_test_ring_cleanup(const uint8_t *);
void pair_test_ota_mode(uint32_t);
uint32_t pair_test_device_state(void);
void pair_test_slave_disconnect(uint32_t);
void *pair_test_controller(void);
void *pair_test_wsf_allocate(uint32_t);
void pair_test_wsf_send(uint32_t, void *);

#define OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR ((const void *)0x1234)
#define OPEN_CFW_PB_PAIR_MGR_AUTH_FLAG (&auth_flag)
#define OPEN_CFW_PB_PAIR_MGR_ENCODE(a,b,c) pair_test_encode((a),(b),(c))
#define OPEN_CFW_PB_PAIR_MGR_SEND(a,b,c,d) pair_test_send((a),(b),(c),(d))
#define OPEN_CFW_PB_PAIR_MGR_NOTIFY(a,b,c,d) pair_test_notify((a),(b),(c),(d))
#define OPEN_CFW_PB_PAIR_MGR_ALLOCATE(a) pair_test_allocate((a))
#define OPEN_CFW_PB_PAIR_MGR_FREE(a) pair_test_free((a))
#define OPEN_CFW_PB_PAIR_MGR_SEQUENCE() pair_test_sequence()
#define OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(a) pair_test_remove((a))
#define OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(a,b,c) pair_test_push((a),(b),(c))
#define OPEN_CFW_PB_PAIR_MGR_CONNECTION_STATE_SET(a) pair_test_connection_state((a))
#define OPEN_CFW_PB_PAIR_MGR_SLAVE_ROLE_SET(a) pair_test_slave_role((a))
#define OPEN_CFW_PB_PAIR_MGR_TARGET_SET(a,b,c) pair_test_target_set((a),(b),(c))
#define OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET(a) pair_test_auth_mode((a))
#define OPEN_CFW_PB_PAIR_MGR_TARGET_COPY(a,b) pair_test_target_copy((a),(b))
#define OPEN_CFW_PB_PAIR_MGR_LINK_MATCHES_TARGET(a) pair_test_link_matches((a))
#define OPEN_CFW_PB_PAIR_MGR_OWNER_SIDE() pair_test_owner_side()
#define OPEN_CFW_PB_PAIR_MGR_RETRY_RESET() pair_test_retry_reset()
#define OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR() pair_test_failure_clear()
#define OPEN_CFW_PB_PAIR_MGR_FAILURE_BEGIN() pair_test_failure_begin()
#define OPEN_CFW_PB_PAIR_MGR_POLICY_MARK(a) pair_test_policy_mark((a))
#define OPEN_CFW_PB_PAIR_MGR_POLICY_BLOCKED(a) pair_test_policy_blocked((a))
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT() pair_test_connect_timeout()
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT_CANCEL() pair_test_connect_timeout_cancel()
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_SUCCESS() pair_test_connect_success()
#define OPEN_CFW_PB_PAIR_MGR_POLICY_RESET() pair_test_policy_reset()
#define OPEN_CFW_PB_PAIR_MGR_THROTTLE_RESET() pair_test_throttle_reset()
#define OPEN_CFW_PB_PAIR_MGR_PEER_EVENT(a) pair_test_peer_event((a))
#define OPEN_CFW_PB_PAIR_MGR_BLE_MODE_ZERO(a) pair_test_ble_zero((a))
#define OPEN_CFW_PB_PAIR_MGR_BLE_MODE_NONZERO(a) pair_test_ble_nonzero((a))
#define OPEN_CFW_PB_PAIR_MGR_RING_CLEANUP(a) pair_test_ring_cleanup((a))
#define OPEN_CFW_PB_PAIR_MGR_OTA_MODE_SET(a) pair_test_ota_mode((a))
#define OPEN_CFW_PB_PAIR_MGR_DEVICE_STATE() pair_test_device_state()
#define OPEN_CFW_PB_PAIR_MGR_SLAVE_DISCONNECT(a) pair_test_slave_disconnect((a))
#define OPEN_CFW_PB_PAIR_MGR_CONTROLLER() pair_test_controller()
#define OPEN_CFW_PB_PAIR_MGR_WSF_ALLOCATE(a) pair_test_wsf_allocate((a))
#define OPEN_CFW_PB_PAIR_MGR_WSF_SEND(a,b) pair_test_wsf_send((a),(b))

#include "../../components/apollo_main/core_overlay/pb_service_pair_mgr.c"

uint32_t pair_test_encode(
    void *raw_output, const void *descriptor, const void *message)
{
    open_cfw_pb_pair_mgr_output *output = raw_output;
    uint8_t value = 0xa5;
    assert(descriptor == (const void *)0x1234);
    memcpy(encoded_message, message, sizeof(encoded_message));
    if (!encode_result) return 0;
    return output->write(output, &value, 1);
}

static int pair_test_transport(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    assert(route == 1 && service == 0x80 && length <= sizeof(sent_message));
    memcpy(sent_message, data, length);
    sent_length = length;
    return 0;
}

int pair_test_send(uint32_t a, uint32_t b, const void *c, uint32_t d)
{ ++send_count; return pair_test_transport(a, b, c, d); }
int pair_test_notify(uint32_t a, uint32_t b, const void *c, uint32_t d)
{ ++notify_count; pair_test_transport(a, b, c, d); return notify_result; }
void *pair_test_allocate(uint32_t bytes)
{ assert(bytes == sizeof(allocation)); memset(allocation, 0xcc, bytes); return allocation; }
void pair_test_free(void *pointer)
{ assert(pointer == allocation); ++free_count; }
uint32_t pair_test_sequence(void) { return sequence; }
void pair_test_remove(const void *p) { (void)p; ++calls[0]; }
void pair_test_push(const void *p, uint32_t a, uint32_t d)
{ (void)p; calls[1]++; calls[2] = a; calls[3] = d; }
void pair_test_connection_state(uint32_t v) { calls[4] = v; }
void pair_test_slave_role(uint32_t v) { calls[5] = v; }
void pair_test_target_set(const uint8_t *a, const uint8_t *n, uint32_t l)
{ assert(a && n); calls[6] = l; }
uint32_t pair_test_auth_mode(uint32_t v) { calls[7] = v; return v == 0x5a ? 7 : v; }
void pair_test_target_copy(uint8_t *a, uint8_t *n)
{ for (unsigned i=0;i<6;i++) a[i]=(uint8_t)(i+1); for(unsigned i=0;i<7;i++) n[i]=(uint8_t)(0x20+i); }
int pair_test_link_matches(const uint8_t *a) { (void)a; return (int)calls[8]; }
int pair_test_owner_side(void) { return (int)calls[9]; }
void pair_test_retry_reset(void) { ++calls[10]; }
void pair_test_failure_clear(void) { ++calls[11]; }
void pair_test_failure_begin(void) { ++calls[12]; }
void pair_test_policy_mark(uint32_t v) { calls[13] = v + 1; }
int pair_test_policy_blocked(uint32_t v) { (void)v; return (int)calls[14]; }
void pair_test_connect_timeout(void) { ++calls[15]; }
void pair_test_connect_timeout_cancel(void) { ++calls[16]; }
void pair_test_connect_success(void) { ++calls[17]; }
void pair_test_policy_reset(void) { ++calls[18]; }
void pair_test_throttle_reset(void) { ++calls[19]; }
void pair_test_peer_event(uint32_t v) { calls[20] = v; }
void pair_test_ble_zero(uint32_t v) { calls[21] = v + 1; }
void pair_test_ble_nonzero(uint32_t v) { calls[22] = v + 1; }
void pair_test_ring_cleanup(const uint8_t *a) { calls[23] = a ? a[0] : 0xff; }
void pair_test_ota_mode(uint32_t v) { calls[24] = v; }
uint32_t pair_test_device_state(void) { return calls[25]; }
void pair_test_slave_disconnect(uint32_t v) { calls[26] = v + 1; }
void *pair_test_controller(void) { return calls[27] ? controller : 0; }
void *pair_test_wsf_allocate(uint32_t n) { assert(n == 12); return wsf_allocation; }
void pair_test_wsf_send(uint32_t h, void *m)
{ assert(m == wsf_message); calls[28] = h; }

static void reset_state(void)
{
    auth_flag = 0; memset(controller,0,sizeof(controller));
    memset(encoded_message,0,sizeof(encoded_message)); memset(calls,0,sizeof(calls));
    send_count=notify_count=free_count=sent_length=0; notify_result=0;
    encode_result=1; wsf_allocation=wsf_message;
}

int main(void)
{
    uint8_t payload[40] = {0};
    uint8_t message[48] = {0};
    uint8_t buffer[64];

    reset_state();
    assert(PB_RxSecAuth(0, 0) == 2);
    payload[0]=1; payload[1]=3;
    assert(PB_RxSecAuth(0,payload)==0 && calls[4]==3 && auth_flag==1);
    assert(calls[0]==2 && calls[1]==1 && calls[2]==1 && calls[3]==500);

    reset_state();
    assert(PB_TxEncodeSecAuth(0x42,buffer,sizeof(buffer),message,0)==2);
    payload[0]=9;
    assert(PB_TxEncodeSecAuth(0x42,buffer,sizeof(buffer),message,payload)==0);
    assert(send_count==1 && sent_length==1 && sent_message[0]==0xa5);
    assert(encoded_message[0]==4 && encoded_message[2]==0x42 && encoded_message[4]==3);
    encode_result=0;
    assert(PB_TxEncodeSecAuth(0,buffer,sizeof(buffer),message,payload)==0x2b);

    reset_state();
    assert(PB_TxEncodeNotifySecAuthImpl(1)==0 && notify_count==0);
    auth_flag=1; notify_result=1;
    assert(PB_TxEncodeNotifySecAuthImpl(1)==-1);
    assert(notify_count==1 && free_count==1 && encoded_message[0]==4);
    assert(encoded_message[2]==0x34 && encoded_message[4]==3 && encoded_message[8]==1);

    reset_state();
    assert(PB_RxPipeRoleChange(0,0)==2);
    payload[0]=2; assert(PB_RxPipeRoleChange(0,payload)==0 && calls[5]==2);
    calls[14]=1;
    assert(_PB_RxRingConnectInfoCommon(0,payload,0)==0 && calls[6]==0);
    calls[14]=0; calls[9]=1; payload[0]=1; payload[10]=3;
    assert(PB_RxRingConnectInfo(0,payload)==0 && calls[6]==3);
    assert(calls[12]==1 && calls[15]==1 && calls[13]==2);

    reset_state();
    assert(PB_TxEncodeNotifyRingConnectInfoImpl(2)==0);
    assert(encoded_message[0]==6 && encoded_message[4]==5 && encoded_message[8]==7);
    assert(encoded_message[12]==1 && encoded_message[36]==2 && calls[20]==2);

    reset_state();
    assert(PB_TxEncodeNotifyRingConnectInfo(7)==-1);
    calls[27]=1; controller[0x56]=9;
    assert(PB_TxEncodeNotifyRingConnectInfo(7)==0);
    assert(wsf_message[2]==0xbb && wsf_message[8]==7 && calls[28]==9);

    reset_state();
    payload[4]=0; assert(PB_RxBleConnectParams(0,payload)==0 && calls[21]==1);
    payload[4]=1; assert(PB_RxBleConnectParams(0,payload)==0 && calls[22]==1);
    assert(PB_RxDisconnectInfo(0,0)==2 && calls[19]==1);
    assert(PB_RxDisconnectInfo(0,payload)==0 && calls[10]==1 && calls[2]==0x102);

    reset_state();
    payload[0]=2; payload[2]=6; payload[4]=0x5a; calls[25]=3;
    assert(PB_RxUnpairInfo(0,payload)==0);
    assert(calls[23]==0x5a && calls[24]==1 && calls[26]==1 && calls[18]==1);
    payload[2]=5; assert(PB_RxUnpairInfo(0,payload)==0 && calls[23]==0xff);
    return 0;
}

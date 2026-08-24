#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_cache[5];
static int host_encode_ok;
static int host_role;
static int host_display_active;
static int host_display_left;
static int host_display_right;
static uint32_t host_display_stop;
static uint32_t host_delay_count;
static uint32_t host_kvdb_invalidate;
static uint32_t host_onboarding_reset;
static uint32_t host_file_remove;
static uint32_t host_clean_bonds;
static uint32_t host_format;
static uint32_t host_restart;
static uint32_t host_heartbeat;
static uint32_t host_system_utc;
static int32_t host_system_timezone;
static uint32_t host_peer_sync;
static uint32_t host_persist_utc;
static int32_t host_persist_timezone;
static uint32_t host_send;
static uint32_t host_direct;
static uint32_t host_route;
static uint32_t host_service;
static uint32_t host_length;

int host_display_active_fn(void);
int host_display_left_fn(void);
int host_display_right_fn(void);
int host_role_fn(void);
void host_display_stop_fn(uint32_t, uint32_t, uint32_t, uint32_t);
void host_delay_fn(uint32_t);
void host_kvdb_invalidate_fn(void);
int host_onboarding_reset_fn(uint32_t, const void *);
int host_file_remove_fn(const char *);
void host_clean_bonds_fn(void);
int host_format_fn(void);
void host_restart_fn(void);
void host_heartbeat_fn(uint32_t);
void host_system_time_sync_fn(uint32_t, int32_t);
void host_peer_time_sync_fn(uint32_t);
void host_persist_fn(uint32_t, int8_t);
int host_send_fn(uint32_t, uint32_t, const void *, uint32_t);
int host_direct_fn(uint32_t, uint32_t, const void *, uint32_t);
uint32_t host_encode_fn(void *, const void *, const void *);

#define OPEN_CFW_PB_DEV_SETTING_TIME_CACHE host_cache
#define OPEN_CFW_PB_DEV_SETTING_WHITELIST_PATH "user/notify_whitelist.json"
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_ACTIVE() host_display_active_fn()
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_LEFT_ACTIVE() host_display_left_fn()
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_RIGHT_ACTIVE() host_display_right_fn()
#define OPEN_CFW_PB_DEV_SETTING_ROLE() host_role_fn()
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_STOP() host_display_stop_fn(0, 0, 0, 0)
#define OPEN_CFW_PB_DEV_SETTING_DELAY(ms) host_delay_fn(ms)
#define OPEN_CFW_PB_DEV_SETTING_KVDB_INVALIDATE() host_kvdb_invalidate_fn()
#define OPEN_CFW_PB_DEV_SETTING_ONBOARDING_RESET(i,v) host_onboarding_reset_fn(i,v)
#define OPEN_CFW_PB_DEV_SETTING_FILE_REMOVE(p) host_file_remove_fn(p)
#define OPEN_CFW_PB_DEV_SETTING_CLEAN_BONDS() host_clean_bonds_fn()
#define OPEN_CFW_PB_DEV_SETTING_FILESYSTEM_FORMAT() host_format_fn()
#define OPEN_CFW_PB_DEV_SETTING_RESTART() host_restart_fn()
#define OPEN_CFW_PB_DEV_SETTING_HEARTBEAT_STATE(v) host_heartbeat_fn(v)
#define OPEN_CFW_PB_DEV_SETTING_SYSTEM_TIME_SYNC(u,z) host_system_time_sync_fn(u,z)
#define OPEN_CFW_PB_DEV_SETTING_PEER_TIME_SYNC(v) host_peer_time_sync_fn(v)
#define OPEN_CFW_PB_DEV_SETTING_TIME_PERSIST(u,z) host_persist_fn(u,z)
#define OPEN_CFW_PB_DEV_SETTING_SEND(r,s,d,n) host_send_fn(r,s,d,n)
#define OPEN_CFW_PB_DEV_SETTING_DIRECT_SEND(r,s,d,n) host_direct_fn(r,s,d,n)
#define OPEN_CFW_PB_DEV_SETTING_ENCODE(o,d,m) host_encode_fn(o,d,m)
#include "../../components/apollo_main/core_overlay/pb_service_dev_setting.c"

int host_display_active_fn(void) { return host_display_active; }
int host_display_left_fn(void) { return host_display_left; }
int host_display_right_fn(void) { return host_display_right; }
int host_role_fn(void) { return host_role; }
void host_display_stop_fn(uint32_t a, uint32_t b, uint32_t c, uint32_t d)
{ assert((a|b|c|d)==0); ++host_display_stop; }
void host_delay_fn(uint32_t ms) { assert(ms==500); ++host_delay_count; }
void host_kvdb_invalidate_fn(void) { ++host_kvdb_invalidate; }
int host_onboarding_reset_fn(uint32_t index, const void *value)
{ assert(index==0 && *(const uint8_t *)value==1); ++host_onboarding_reset; return 0; }
int host_file_remove_fn(const char *path)
{ assert(strcmp(path,"user/notify_whitelist.json")==0); ++host_file_remove; return 0; }
void host_clean_bonds_fn(void) { ++host_clean_bonds; }
int host_format_fn(void) { ++host_format; return 0; }
void host_restart_fn(void) { ++host_restart; }
void host_heartbeat_fn(uint32_t connected) { assert(connected==1); ++host_heartbeat; }
void host_system_time_sync_fn(uint32_t utc, int32_t timezone)
{ host_system_utc=utc; host_system_timezone=timezone; }
void host_peer_time_sync_fn(uint32_t mode) { assert(mode==0); ++host_peer_sync; }
void host_persist_fn(uint32_t utc, int8_t timezone)
{ host_persist_utc=utc; host_persist_timezone=timezone; }
int host_send_fn(uint32_t route,uint32_t service,const void *data,uint32_t length)
{ assert(data!=0); ++host_send; host_route=route; host_service=service; host_length=length; return 0; }
int host_direct_fn(uint32_t route,uint32_t service,const void *data,uint32_t length)
{ assert(data!=0); ++host_direct; host_route=route; host_service=service; host_length=length; return 0; }
uint32_t host_encode_fn(void *raw,const void *descriptor,const void *message)
{
    static const uint8_t encoded[]={0xD5,0x80,0x01};
    open_cfw_pb_dev_setting_output *output=raw;
    assert(descriptor==OPEN_CFW_PB_DEV_SETTING_DESCRIPTOR && message!=0);
    return host_encode_ok ? output->write(output,encoded,sizeof(encoded)) : 0;
}

static void reset_host(void)
{
    memset(host_cache,0,sizeof(host_cache));
    host_encode_ok=1; host_role=0; host_display_active=0; host_display_left=0;
    host_display_right=0; host_display_stop=0; host_delay_count=0;
    host_kvdb_invalidate=0; host_onboarding_reset=0; host_file_remove=0;
    host_clean_bonds=0; host_format=0; host_restart=0; host_heartbeat=0;
    host_system_utc=0; host_system_timezone=0; host_peer_sync=0;
    host_persist_utc=0; host_persist_timezone=0; host_send=0; host_direct=0;
    host_route=0; host_service=0; host_length=0;
}

static void test_receive_paths(void)
{
    uint8_t payload[8]={0x78,0x56,0x34,0x12,0xF9};
    reset_host();
    assert(PB_RxRestoreFactory(1,0)==2);
    host_role=1; host_display_active=1; host_display_left=1; host_display_right=1;
    assert(PB_RxRestoreFactory(1,payload)==0);
    assert(host_display_stop==2 && host_delay_count==2);
    assert(host_kvdb_invalidate==1 && host_onboarding_reset==1);
    assert(host_file_remove==1 && host_clean_bonds==1 && host_format==1);
    assert(host_restart==1);
    reset_host();
    assert(PB_RxQuickRestart(2,payload)==0 && host_restart==1);
    assert(PB_RxBaseConnHeartBeat(3,payload)==0 && host_heartbeat==1);
    assert(PB_RxAudControl(4,payload)==0 && PB_RxAudControl(4,0)==2);
    assert(PB_RxTimeSyncInfo(5,payload)==0);
    assert(host_system_utc==0x12345678U && host_system_timezone==-7);
    assert(memcmp(host_cache,payload,5)==0 && host_peer_sync==1 && host_heartbeat==2);
}

typedef int (*host_tx_fn)(uint8_t,void *,uint16_t,uint8_t *,const uint8_t *);
static void test_tx(host_tx_fn fn,uint8_t command,uint16_t tag,int direct)
{
    uint8_t buffer[16]; uint8_t message[24]; uint8_t payload[8]={1};
    reset_host(); memset(message,0xAA,sizeof(message));
    assert(fn(0x5A,0,sizeof(buffer),message,payload)==2);
    assert(fn(0x5A,buffer,sizeof(buffer),0,payload)==2);
    assert(fn(0x5A,buffer,sizeof(buffer),message,0)==2);
    host_encode_ok=0;
    assert(fn(0x5A,buffer,sizeof(buffer),message,payload)==0x2B);
    host_encode_ok=1;
    assert(fn(0x5A,buffer,sizeof(buffer),message,payload)==0);
    assert(message[0]==command && message[2]==0x5A && message[3]==0);
    assert(message[4]==(uint8_t)tag && message[5]==(uint8_t)(tag>>8));
    assert(host_route==1 && host_service==0x80 && host_length==3);
    assert((direct ? host_direct : host_send)==1);
}

int main(void)
{
    uint8_t buffer[16], message[24], payload[8]={1};
    test_receive_paths();
    test_tx(PB_TxEncodeRestoreFactory,0x0D,0x0C,0);
    test_tx(PB_TxEncodeQuickRestart,0x0F,0x0E,0);
    test_tx(PB_TxEncodeBaseConnHeartBeat,0x0E,0x0D,1);
    test_tx(PB_TxEncodeAudControl,0x81,0x81,0);
    reset_host(); host_cache[0]=0xEF; host_cache[1]=0xCD;
    host_cache[2]=0xAB; host_cache[3]=0x89; host_cache[4]=0xF4;
    memset(message,0,sizeof(message));
    assert(PB_TxEncodeTimeSyncInfo(7,buffer,sizeof(buffer),message,payload)==0);
    assert(message[0]==0x80 && message[4]==0x80 && message[13]==0);
    assert(host_persist_utc==0x89ABCDEFU && host_persist_timezone==-12);
    return 0;
}

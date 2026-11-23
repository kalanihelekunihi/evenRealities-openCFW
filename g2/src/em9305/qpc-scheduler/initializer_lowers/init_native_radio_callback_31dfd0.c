#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31dfd0..0x31e458: connection-event-closed handler for the
 * object (+0x24 connection, +44 event state, +8 anchor). It (re)starts the
 * supervision timer (+384, +382 ms) once a packet was seen (+400, flags
 * ((uintptr_t)&em9305_ram_802a2c + 0xcu)/((uintptr_t)&em9305_ram_802a2c + 0x8u)), samples the RSSI (+268/+269, +784/+780 or the
 * ((uintptr_t)&em9305_ram_805160 + 0x18u) hook) and runs the event-end hook (+812). Without traffic the
 * missed-event counter (+402) posts message 0x4701; a peripheral that
 * must terminate (+629/+630, +620, +360) is closed with reason 0x4c. The
 * latency hook ((uintptr_t)&em9305_ram_801a14 + 0x4u) may skip events (role table (uintptr_t)&em9305_ram_8027e0). A pending
 * control PDU (+192) is built (32d64c/323d38) with its instant and
 * queued; a pending data-length/PHY update (+608/+609) runs (uintptr_t)&em9305_ram_8052bc or
 * ((uintptr_t)&em9305_ram_8052bc + 0x4u). Then, for each event until the scheduler (312da4) accepts the
 * next anchor, the event counter (+262) and anchor (+8) advance and a
 * procedure instant (+635: 1 channel map, 0xe, 0x11 connection update,
 * 0x15) is applied; the authenticated-payload counter (+772) may post
 * message 0x6901. Finally the ping timer (+748..+754, +77) may post
 * message 0x6d01. Returns the stock r0 at each exit. */
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,
                                                  uint32_t milliseconds);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task,
                                                     uintptr_t message);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record,
                                                        uint32_t reason);
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_child_32d64c(uintptr_t record);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,
    uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action);
extern uint32_t opencfw_em9305_child_323d38(uintptr_t output,uintptr_t input);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                      uintptr_t packet);
extern uint32_t opencfw_em9305_radio_channels_317ac0(uintptr_t record);
extern void opencfw_em9305_child_322630(uintptr_t record);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,
                                                                 uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t,
                                                            uintptr_t);

typedef uint32_t (*opencfw_em9305_hook1_31dfd0)(uintptr_t);
typedef uint32_t (*opencfw_em9305_hook2_31dfd0)(uintptr_t,uint32_t);
typedef uint32_t (*opencfw_em9305_end_hook_31dfd0)(uint32_t,uint32_t);
typedef uint32_t (*opencfw_em9305_hook3_31dfd0)(uintptr_t,uint32_t,uint32_t);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

/* Connection index of conn in the 912-byte table at *((uintptr_t)&em9305_ram_805c5c + 0x14u). */
static uint32_t conn_index(uintptr_t conn)
{
    return (uint32_t)((int32_t)(conn-r32(((uintptr_t)&em9305_ram_805c5c + 0x14u)))/912);
}

/* Post a 4/8-byte LL message {index, code} to the LL task (((uintptr_t)&em9305_ram_805af0 + 0x28u));
 * returns the allocator result when it fails, else the send result. */
static uint32_t post(uintptr_t conn,uint32_t length,uint32_t code)
{
    uintptr_t message=opencfw_em9305_wsf_event_allocate(length);
    if(message==0u)return 0u;
    w16(message+2u,code);
    uint32_t index=(uint8_t)conn_index(conn);
    w16(message,index);
    return opencfw_em9305_wsf_task_message_send(r8(((uintptr_t)&em9305_ram_805af0 + 0x28u)),message);
}

static uint32_t role_hook(uintptr_t conn,uint32_t value)
{
    opencfw_em9305_hook2_31dfd0 hook=(opencfw_em9305_hook2_31dfd0)(uintptr_t)
        r32((uintptr_t)&em9305_ram_8027e0+r8(conn+321u)*4u);
    return hook(conn,value);
}

/* Apply the procedure instant (+635) at the current event counter. */
static void apply_instant(uintptr_t conn)
{
    uintptr_t timer=conn+384u;
    uint32_t procedure=r8(conn+635u);
    if(procedure==1u){
        if(r16(conn+262u)!=r16(conn+716u))return;
        uint32_t high=r32(conn+712u);
        w32(conn+276u,r32(conn+708u));
        w32(conn+280u,high);
        (void)opencfw_em9305_radio_channels_317ac0(conn);
    }else if(procedure==0xeu){
        if(r16(conn+262u)<r16(conn+726u))return;
    }else if(procedure==0x15u){
        if(r16(conn+262u)==r16(conn+724u))opencfw_em9305_child_322630(conn);
        return;
    }else if(procedure==0x11u){
        if(r16(conn+262u)!=r16(conn+682u))return;
        uint32_t interval=r16(conn+676u);
        uint32_t latency=r16(conn+678u);
        uint32_t timeout=r16(conn+680u);
        uint32_t window=r16(conn+674u);
        uint32_t old_interval=r16(conn+266u);
        uint32_t old_latency=r16(conn+260u);
        uint32_t anchor=r32(conn+24u);
        w16(conn+266u,interval);
        w16(conn+260u,latency);
        uint32_t timeout_ms=(uint16_t)(timeout*10u);
        uint32_t old_timeout=r16(conn+382u);
        w32(conn+32u,interval*1250u);
        w32(conn+24u,window*1250u+anchor);
        w16(conn+382u,timeout_ms);
        uint32_t interval_ms=old_interval+(old_interval>>2)+
                             ((old_interval&3u)!=0u);
        (void)opencfw_em9305_wsf_timer_start_ms(timer,interval_ms+timeout_ms);
        if(old_interval!=r16(conn+266u)||old_latency!=r16(conn+260u)||
           old_timeout!=r16(conn+382u))
            w32(conn+636u,r32(conn+636u)|0x20000u);
    }else{
        return;
    }
    w8(conn+628u,1u);
}

uint32_t opencfw_em9305_radio_cb_31dfd0(uintptr_t object)
{
    uintptr_t conn=r32(object+0x24u);
    uintptr_t seen=conn+400u;
    uintptr_t state=r32(object+44u);
    uintptr_t timer=conn+384u;
    uint32_t received=r8(((uintptr_t)&em9305_ram_802a2c + 0xcu));
    if(r8(seen)!=0u){
        if(received!=0u){
            (void)opencfw_em9305_wsf_timer_start_ms(timer,r16(conn+382u));
            w16(conn+264u,r16(conn+262u));
        }
    }else if((received|r8(((uintptr_t)&em9305_ram_802a2c + 0x8u)))!=0u){
        if(r8(conn+12u)==0x3eu)w8(conn+12u,8u);
        (void)opencfw_em9305_wsf_timer_start_ms(timer,r16(conn+382u));
        uint32_t features=r32(((uintptr_t)&em9305_ram_805a6c + 0x18u));
        if((features&0x100u)==0u&&r8(conn+770u)==1u&&r8(conn+769u)==0u&&
           (features&0x8000u)!=0u)
            w8(conn+772u,opencfw_em9305_radio_record_timing_30c40c(800u,
                                                               r16(conn+266u)));
        w8(seen,1u);
    }
    uint32_t rssi=r8(state+124u);
    w8(conn+268u,rssi);
    if(r8(conn+770u)==1u){
        if(r8(conn+269u)!=0u){
            rssi=0x7fu;
            w8(conn+268u,0x7fu);
        }
        uint32_t mode=r8(conn+769u);
        if(mode==1u){
            ((opencfw_em9305_hook1_31dfd0)(uintptr_t)r32(((uintptr_t)&em9305_ram_805160 + 0x18u)))(conn);
        }else if(mode==0u&&rssi!=0x7fu){
            uint32_t count=r16(conn+780u);
            w32(conn+784u,r32(conn+784u)+(uint32_t)(int32_t)(int8_t)rssi);
            w16(conn+780u,count+1u);
        }
    }
    uintptr_t end_hook=r32(conn+812u);
    if(end_hook!=0u){
        uint32_t index=conn_index(conn);
        /* Stock passes the byte index in r0 and the full quotient in r1. */
        ((opencfw_em9305_end_hook_31dfd0)end_hook)((uint8_t)index,index);
    }
    if((r8(((uintptr_t)&em9305_ram_802a2c + 0xcu))|r8(seen))==0u){
        uint32_t missed=(uint8_t)(r8(conn+402u)-1u);
        w8(conn+402u,missed);
        if(missed==0u)(void)post(conn,4u,0x4701u);
    }
    if(r8(conn+1u)==3u){
        int terminate;
        if(r8(conn+629u)!=0u)terminate=r8(conn+630u)!=0u;
        else terminate=r8(conn+620u)==0u||r32(conn+360u)==0u;
        if(terminate){
            (void)opencfw_em9305_receive_terminate_325c08(conn,0x4cu);
            return opencfw_em9305_wsf_timer_stop(timer);
        }
    }
    uint32_t events=1u;
    uintptr_t latency_hook=r32(((uintptr_t)&em9305_ram_801a14 + 0x4u));
    if(latency_hook!=0u){
        uint32_t pending=(uint16_t)(r16(((uintptr_t)&em9305_ram_802a2c + 0x14u))+r16(((uintptr_t)&em9305_ram_802a2c + 0x18u)));
        uint32_t skipped=((opencfw_em9305_hook3_31dfd0)latency_hook)(conn,pending,
            r16(((uintptr_t)&em9305_ram_802a2c + 0x10u))!=0u);
        if(skipped!=0u){
            uint32_t counter=r16(conn+262u);
            opencfw_em9305_hook2_31dfd0 hook=(opencfw_em9305_hook2_31dfd0)(uintptr_t)
                r32((uintptr_t)&em9305_ram_8027e0+r8(conn+321u)*4u);
            w16(conn+262u,counter+skipped);
            (void)hook(conn,(uint16_t)(skipped-1u));
            events=skipped+1u;
        }
    }
    if(r8(conn+192u)!=0u){
        uint32_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(0xcu);
        if(packet!=0u){
            w8(conn+192u,0u);
            uint32_t offset=opencfw_em9305_child_32d64c(conn);
            if(offset<6u)offset=6u;
            else offset=opencfw_em9305_child_32d64c(conn);
            uint32_t latency=r16(conn+260u);
            uint32_t index=conn_index(conn);
            int32_t step=(int16_t)(offset*(latency+1u));
            uint32_t instant=(uint32_t)(step*(int16_t)r16(conn+846u))+r16(conn+262u);
            w16(conn+682u,instant);
            uint32_t ticks=opencfw_em9305_radio_schedule_313424(0u,(uint8_t)index,
                r32(object+8u),0u,0u);
            uint64_t scaled=(uint64_t)ticks*0x1a36e3u;
            w16(conn+674u,(uint32_t)(scaled>>31));
            (void)opencfw_em9305_child_323d38(packet,conn+672u);
            (void)opencfw_em9305_phy_packet_send_32d32c(conn,packet);
        }
    }
    if(r8(conn+608u)!=0u){
        uint32_t phy=r8(conn+609u);
        w8(conn+608u,0u);
        uintptr_t hook=phy!=0u?r32((uintptr_t)&em9305_ram_8052bc):r32(((uintptr_t)&em9305_ram_8052bc + 0x4u));
        if(hook!=0u)((opencfw_em9305_hook1_31dfd0)hook)(conn);
    }
    uint32_t tx_phy=r8(state+15u);
    if(tx_phy==0u)tx_phy=r8(state+125u);
    uint32_t role=r8(state+12u);
    uint32_t anchor=r32(object+8u);
    w8(state+14u,tx_phy);
    if(role==3u)w8(state+2u,r8(conn+334u+(tx_phy==1u)));
    do{
        uint32_t counter=r16(conn+262u)+1u;
        uint32_t procedure=r8(conn+635u);
        uint32_t interval=r16(conn+266u);
        w16(conn+262u,counter);
        w8(object+0x18u,procedure!=0x11u);
        uint32_t advance=(uint32_t)(uint16_t)events*interval*1250u;
        w32(object+0x14u,advance);
        w32(object+8u,advance+anchor);
        apply_instant(conn);
        if(r8(conn+770u)==1u&&r8(conn+769u)==0u&&(r8(((uintptr_t)&em9305_ram_805a6c + 0x19u))&0x80u)!=0u){
            uint32_t count=(uint8_t)(r8(conn+772u)-1u);
            w8(conn+772u,count);
            if(count==0u)(void)post(conn,8u,0x6901u);
        }
        w8(state+1u,role_hook(conn,0u));
        events++;
    }while(opencfw_em9305_associated_schedule_insert_312da4(object,
               (uintptr_t)opencfw_em9305_init_schedule_compare_318b78)==0u);
    if(r8(conn+748u)==0u)return 0u;
    uint32_t counter=r16(conn+262u);
    if(counter<r16(conn+754u))return counter;
    uint32_t paused=r8(conn+620u);
    if(paused!=0u)return paused;
    if(r8(conn+77u)>=3u){
        w8(conn+748u,0u);
        return 4u;
    }
    uint32_t result=post(conn,4u,0x6d01u);
    uint32_t period=r16(conn+750u);
    if(period==0u){
        w8(conn+748u,0u);
        return result;
    }
    result=r16(conn+262u)+period;
    w16(conn+754u,result);
    return result;
}

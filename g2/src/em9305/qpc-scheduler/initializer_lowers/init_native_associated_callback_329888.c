#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x329888..0x329fd6: connection-event-closed handler for a
 * connection in the central/peripheral associated state (object +0x24
 * connection, +44 event state, +8/+0xc/+0x14/+0x18 anchor and window).
 * After a late wake-up (+217) the events missed since the time alias
 * (30fd34) are taken off the event counter (+262) and the peripheral's
 * accumulated clock drift (+270/+271) is adjusted. It then samples the
 * RSSI (+268/+269, +784/+780 or the ((uintptr_t)&em9305_ram_805160 + 0x18u) hook), resets the timing
 * state on a new connection (+219), restarts the supervision timer (+384,
 * +382 ms; +400 seen, +218/+220), runs the event-end hooks (+812 and
 * *((uintptr_t)&em9305_ram_805c5c + 0x7cu) +0x1c), terminates a peripheral that must stop (reason 0x4c,
 * +629/+630/+620/+360) or after an MIC failure (+633/+632, reason 0x40),
 * runs a pending data-length/PHY hook ((uintptr_t)&em9305_ram_8052bc/((uintptr_t)&em9305_ram_8052bc + 0x4u)), applies a
 * connection update at its instant (+635 == 0x11, 3294fc/32a4c0) and
 * posts a channel-classification report (message 0x6b01, 37 channels of
 * ((uintptr_t)&em9305_ram_805a6c + 0x34u)) when due (+565, +228..+240). Events skipped through the
 * latency hook (((uintptr_t)&em9305_ram_801a14 + 0x4u)) or peripheral latency (+260, +11 bit 4, queued
 * data at +360, instants) advance the counter (role table (uintptr_t)&em9305_ram_8027e0).
 * Then, for each event until the scheduler (312da4) accepts the next
 * anchor, the counter, anchor and window widening (317ebc, guard
 * interval) advance (terminating when the window exceeds half the
 * interval), the procedure instant (+635: 1 channel map, 0xe, 0x11
 * connection update, 0x15 PHY update with TX power ((uintptr_t)&em9305_ram_805c5c + 0x50u) and hook
 * ((uintptr_t)&em9305_ram_8052bc + 0xcu)) is applied, the authenticated-payload counter (+772) may post
 * message 0x6901 and the supervision state (+401) is refreshed. Finally
 * the ping timer (+748..+754, +77) may post message 0x6d01 and the close
 * hook (state +124, when +894) runs. Returns the stock r0 at each exit. */
extern uint32_t opencfw_em9305_associated_time_alias_30fd34(void);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t current,
                                                        uint32_t previous);
extern uint32_t opencfw_em9305_radio_unsigned_divide_30c3a4(uint32_t numerator,
    uint32_t denominator);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,
                                                  uint32_t milliseconds);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record,
                                                        uint32_t reason);
extern uint32_t opencfw_em9305_associated_child_3294fc(uintptr_t record);
extern void opencfw_em9305_associated_child_32a4c0(uintptr_t record,
                                                   uint32_t keep);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task,
                                                     uintptr_t message);
extern uint64_t opencfw_em9305_child_3027f4(uint32_t low,uint32_t high,
                                             uint32_t count);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_radio_channels_317ac0(uintptr_t record);
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t slot,
                                                  uintptr_t input);
extern uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t queue);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,
                                                                 uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t,
                                                            uintptr_t);
extern const uint8_t opencfw_em9305_event_map_3344b0[7];

typedef uint32_t (*opencfw_em9305_hook1_329888)(uintptr_t);
typedef uint32_t (*opencfw_em9305_hook2_329888)(uintptr_t,uint32_t);
typedef uint32_t (*opencfw_em9305_hook3_329888)(uintptr_t,uint32_t,uint32_t);
typedef uint32_t (*opencfw_em9305_hook5_329888)(uintptr_t,uint32_t,uint32_t,
                                               uint32_t,uint32_t);

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

/* Run an index hook: r0 = byte index, r1 = full quotient (stock). */
static void index_hook(uintptr_t conn,uintptr_t hook)
{
    uint32_t index=conn_index(conn);
    ((opencfw_em9305_hook2_329888)hook)((uint8_t)index,index);
}

/* Post a 4/8-byte LL message {index, code}; returns the stock r0. */
static uint32_t post(uintptr_t conn,uint32_t length,uint32_t code)
{
    uintptr_t message=opencfw_em9305_wsf_event_allocate(length);
    if(message==0u)return 0u;
    w16(message+2u,code);
    w16(message,(uint8_t)conn_index(conn));
    return opencfw_em9305_wsf_task_message_send(r8(((uintptr_t)&em9305_ram_805af0 + 0x28u)),message);
}

static uint32_t role_hook(uintptr_t conn,uint32_t value)
{
    opencfw_em9305_hook2_329888 hook=(opencfw_em9305_hook2_329888)(uintptr_t)
        r32((uintptr_t)&em9305_ram_8027e0+r8(conn+321u)*4u);
    return hook(conn,value);
}

/* PHY bit (1, 2, 4, 8) of a PHY value 1..4; the raw shifted word for 2..4. */
static uint32_t phy_word(uint32_t phy)
{
    return phy-2u<3u?0x80402u>>(((phy-2u)&0xffu)*8u):1u;
}

/* PHY value for a PHY bit mask 2..8 (7-entry table), else 1. */
static uint32_t mask_phy(uint32_t mask)
{
    uint32_t index=mask-2u;
    return index<7u?opencfw_em9305_event_map_3344b0[(int8_t)index]:1u;
}

/* Late wake-up: drop the events elapsed since the time alias and, for a
 * peripheral (+321 == 0), adjust the drift byte +270 by the events times
 * the drift step +271 (wrapping modulo 37 below zero). */
static void catch_up(uintptr_t object,uintptr_t conn)
{
    uint32_t alias=opencfw_em9305_associated_time_alias_30fd34();
    uint32_t interval=r16(conn+266u);
    if(opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),alias)==0u)return;
    interval*=1250u;
    if(interval>=opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),alias))
        return;
    uint32_t missed=opencfw_em9305_radio_unsigned_divide_30c3a4(
        opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),alias),interval);
    uint32_t role=r8(conn+321u);
    w16(conn+262u,r16(conn+262u)-missed);
    if(role!=0u)return;
    uint32_t step=missed*r8(conn+271u);
    uint32_t drift=r8(conn+270u);
    if(step<=drift){
        drift-=step;
    }else{
        uint32_t excess=step-drift;
        if(excess<38u){
            drift=37u-excess;
        }else{
            uint32_t q=(excess*0xdd68u)>>21;
            drift=37u-(excess+(uint32_t)((int32_t)(int16_t)q*-37));
        }
    }
    w8(conn+270u,drift);
}

/* PHY update at its instant (+635 == 0x15): new TX/RX PHYs (+723/+722),
 * TX power for the new PHY (+332.., 0x7e = from ((uintptr_t)&em9305_ram_805c5c + 0x50u) +40, hook
 * ((uintptr_t)&em9305_ram_8052bc + 0xcu)), and the limits (317b10) for both directions. */
static void phy_update(uintptr_t conn)
{
    uint32_t tx_word=phy_word(r8(conn+76u));
    uint32_t rx_word=phy_word(r8(conn+77u));
    uint32_t new_tx=r8(conn+723u);
    if(new_tx!=0u&&new_tx!=(tx_word&0xffu)){
        uint32_t index=new_tx-2u;
        uint32_t phy=1u,step=1u,coded=0u;
        if(index<7u){
            phy=opencfw_em9305_event_map_3344b0[(int8_t)index];
            coded=(index&0x7fu)==2u;
        }
        w8(conn+76u,phy);
        if(coded)step=r8(conn+78u)!=1u;
        uint32_t flags=r32(conn+636u);
        int32_t power=*(volatile int8_t *)(conn+332u+phy-step);
        w32(conn+636u,flags|0x200000u);
        w8(conn+66u,(uint32_t)power);
        if(power==0x7e){
            int32_t level=*(volatile int8_t *)(r32(((uintptr_t)&em9305_ram_805c5c + 0x50u))+40u);
            w8(conn+66u,(uint32_t)level);
            w8(conn+331u+phy,(uint32_t)level);
            if(coded)w8(conn+335u,r8(r32(((uintptr_t)&em9305_ram_805c5c + 0x50u))+40u));
            if((r8(conn+548u)&4u)!=0u){
                uintptr_t hook=r32(((uintptr_t)&em9305_ram_8052bc + 0xcu));
                if(hook!=0u)
                    ((opencfw_em9305_hook5_329888)hook)(conn,phy,0u,
                                                        (uint32_t)level,1u);
            }
        }
    }
    uint32_t new_rx=r8(conn+722u);
    if(new_rx!=0u&&new_rx!=(rx_word&0xffu)){
        uint32_t phy=mask_phy(new_rx);
        uint32_t flags=r32(conn+636u);
        w8(conn+77u,phy);
        w32(conn+636u,flags|0x200000u);
    }
    w8(conn+628u,1u);
    w16(conn+592u,opencfw_em9305_radio_limit_317b10(conn,conn+574u));
    w16(conn+590u,opencfw_em9305_radio_limit_317b10(conn,conn+566u));
}

/* Apply the procedure instant (+635) at the current event counter. */
static void apply_instant(uintptr_t conn)
{
    uint32_t procedure=r8(conn+635u);
    if(procedure==1u){
        if(r16(conn+262u)!=r16(conn+716u))return;
        uint32_t high=r32(conn+712u);
        w32(conn+276u,r32(conn+708u));
        w32(conn+280u,high);
        (void)opencfw_em9305_radio_channels_317ac0(conn);
        w8(conn+628u,1u);
    }else if(procedure==0xeu){
        if(r16(conn+262u)==r16(conn+726u))w8(conn+628u,1u);
    }else if(procedure==0x15u){
        if(r16(conn+262u)==r16(conn+724u))phy_update(conn);
    }else if(procedure==0x11u){
        uint32_t counter=r16(conn+262u);
        uint32_t instant=r16(conn+682u);
        if(counter+1u==instant)w8(conn+401u,2u);
        if(counter==instant)opencfw_em9305_associated_child_32a4c0(conn,0u);
    }
}

/* Channel classification report (message 0x6b01): 37 bytes, 0 for a used
 * channel and 3 for an unused one in the map at ((uintptr_t)&em9305_ram_805a6c + 0x34u). */
static void report_channels(uintptr_t object,uintptr_t conn)
{
    if(r8(conn+565u)==0u||r32(conn+240u)==0u)return;
    uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),
                                                             r32(conn+228u));
    if(r32(conn+232u)>=elapsed)return;
    elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(r32(object+8u),
                                                    r32(conn+240u));
    if(elapsed<r32(conn+236u)){
        w32(conn+228u,r32(object+8u));
        uintptr_t message=opencfw_em9305_wsf_event_allocate(0x2au);
        if(message!=0u){
            w16(message+2u,0x6b01u);
            w16(message,(uint8_t)conn_index(conn));
            for(uint32_t channel=0u;channel<37u;channel++){
                uint64_t bits=opencfw_em9305_child_3027f4(r32(((uintptr_t)&em9305_ram_805a6c + 0x34u)),
                    r32(((uintptr_t)&em9305_ram_805a6c + 0x38u)),channel);
                w8(message+4u+channel,((uint32_t)bits&1u)?0u:3u);
            }
            (void)opencfw_em9305_wsf_task_message_send(r8(((uintptr_t)&em9305_ram_805af0 + 0x28u)),message);
        }
    }
    w32(conn+240u,0u);
}

/* Peripheral latency: 1 = no events to skip; 0 = skip *skip events. */
static int latency_skip(uintptr_t conn,uint32_t latency,uint32_t window,
                        uint32_t *skip)
{
    uint32_t instant;
    if((r8(conn+11u)&0x10u)==0u||latency==0u||r8(conn+888u)!=0u||
       r8(conn+216u)==0u||r8(conn+220u)==0u||
       opencfw_em9305_wsf_queue_empty(conn+360u)==0u||r8(conn+1u)==3u)
        return 0;
    uint32_t procedure=r8(conn+635u);
    *skip=window;
    if(procedure==255u)return 0;
    if(procedure==0x11u&&opencfw_em9305_associated_child_3294fc(conn)!=0u){
        instant=r16(conn+682u);
    }else{
        if(procedure==0x11u)procedure=r8(conn+635u);
        if(procedure==0x15u){
            if(r8(conn+634u)==0u)return 1;
            instant=r16(conn+724u);
        }else if(procedure==1u&&r8(conn+626u)==1u){
            instant=r16(conn+716u);
        }else{
            return 1;
        }
    }
    int32_t distance=(int32_t)(instant-r16(conn+262u));
    if((uint16_t)distance>(uint16_t)window+1u)return 0;
    if(distance<2)return 1;
    *skip=(uint32_t)distance-2u;
    return 0;
}

uint32_t opencfw_em9305_associated_callback_329888(uintptr_t object)
{
    uintptr_t conn=r32(object+0x24u);
    uintptr_t state=r32(object+44u);
    uintptr_t timer=conn+384u;
    if(r8(conn+217u)!=0u){
        catch_up(object,conn);
        w8(conn+217u,0u);
    }
    uint32_t rssi=r8(state+132u);
    w8(conn+268u,rssi);
    if(r8(conn+770u)==1u){
        if(r8(conn+269u)!=0u){
            rssi=0x7fu;
            w8(conn+268u,0x7fu);
        }
        uint32_t mode=r8(conn+769u);
        if(mode==1u){
            ((opencfw_em9305_hook1_329888)(uintptr_t)r32(((uintptr_t)&em9305_ram_805160 + 0x18u)))(conn);
        }else if(mode==0u&&rssi!=0x7fu){
            uint32_t count=r16(conn+780u);
            w32(conn+784u,r32(conn+784u)+(uint32_t)(int32_t)(int8_t)rssi);
            w16(conn+780u,count+1u);
        }
    }
    if(r8(conn+219u)!=0u){
        uint32_t counter=r16(conn+262u);
        uint32_t anchor=r32(conn+224u);
        w32(conn+212u,0u);
        w32(conn+204u,0u);
        w8(conn+401u,0u);
        w32(conn+208u,anchor);
        w16(conn+202u,counter+1u);
    }
    uintptr_t seen=conn+400u;
    uint32_t active=r8(conn+220u);
    if(r8(seen)!=0u){
        if(active!=0u)
            (void)opencfw_em9305_wsf_timer_start_ms(timer,r16(conn+382u));
    }else if(active!=0u||r8(conn+218u)!=0u){
        if(r8(conn+12u)==0x3eu)w8(conn+12u,8u);
        (void)opencfw_em9305_wsf_timer_start_ms(timer,r16(conn+382u));
        uint32_t features=r32(((uintptr_t)&em9305_ram_805a6c + 0x18u));
        if((features&0x100u)==0u&&r8(conn+770u)==1u&&r8(conn+769u)==0u&&
           (features&0x8000u)!=0u)
            w8(conn+772u,opencfw_em9305_radio_record_timing_30c40c(800u,
                                                               r16(conn+266u)));
        w8(seen,1u);
    }
    uintptr_t end_hook=r32(conn+812u);
    if(end_hook!=0u)index_hook(conn,end_hook);
    if(r8(conn+1u)==3u){
        int terminate;
        if(r8(conn+629u)!=0u)terminate=r8(conn+630u)!=0u;
        else terminate=r8(conn+620u)==0u||r32(conn+360u)==0u;
        if(terminate)goto terminate;
    }
    {
        uintptr_t table=r32(((uintptr_t)&em9305_ram_805c5c + 0x7cu));
        if(table!=0u){
            uintptr_t hook=r32(table+0x1cu);
            if(hook!=0u)index_hook(conn,hook);
        }
    }
    if(r8(conn+633u)!=0u&&r8(conn+632u)==0u){
        w8(conn+632u,1u);
        (void)opencfw_em9305_receive_terminate_325c08(conn,0x40u);
    }
    if(r8(conn+608u)!=0u){
        uint32_t phy=r8(conn+609u);
        w8(conn+608u,0u);
        uintptr_t hook=phy!=0u?r32((uintptr_t)&em9305_ram_8052bc):r32(((uintptr_t)&em9305_ram_8052bc + 0x4u));
        if(hook!=0u)((opencfw_em9305_hook1_329888)hook)(conn);
    }
    if(r8(conn+635u)==0x11u&&opencfw_em9305_associated_child_3294fc(conn)!=0u&&
       r16(conn+262u)==r16(conn+682u))
        opencfw_em9305_associated_child_32a4c0(conn,1u);
    report_channels(object,conn);
    uint32_t events=r16(conn+262u)-r16(conn+202u);
    uintptr_t latency_hook=r32(((uintptr_t)&em9305_ram_801a14 + 0x4u));
    uint32_t skip,window,latency;
    if(latency_hook!=0u){
        uint32_t pending=(uint16_t)(r16(((uintptr_t)&em9305_ram_805688 + 0x8u))+r16(((uintptr_t)&em9305_ram_805688 + 0x4u)));
        skip=((opencfw_em9305_hook3_329888)latency_hook)(conn,pending,1u);
        latency=r16(conn+260u);
        window=skip+(uint32_t)(uint16_t)r16(conn+846u)*(uint16_t)latency;
    }else{
        latency=r16(conn+260u);
        skip=0u;
        window=latency;
    }
    events++;
    if(r8(conn+217u)!=0u||latency_skip(conn,latency,window,&skip)==0){
        if((uint16_t)skip!=0u){
            opencfw_em9305_hook2_329888 hook=(opencfw_em9305_hook2_329888)(uintptr_t)
                r32((uintptr_t)&em9305_ram_8027e0+r8(conn+321u)*4u);
            w16(conn+262u,r16(conn+262u)+skip);
            (void)hook(conn,(uint16_t)(skip-1u));
            events+=skip;
        }
    }
    do{
        events++;
        uint32_t step=1250u*(uint16_t)events;
        uint32_t advance=step*r16(conn+266u);
        uint32_t counter=r16(conn+262u)+1u;
        uint32_t base=r32(conn+212u)+advance;
        w16(conn+262u,counter);
        uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(base,
                                                                   r16(conn+200u));
        uint32_t interval=r16(conn+266u);
        uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
        if(guard<150u)guard=150u;
        else guard=opencfw_em9305_auxiliary_guard_interval();
        uint32_t span=step*(uint16_t)interval;
        if(widening>=(span>>1)-guard)goto terminate;
        uint32_t anchor=r32(conn+208u);
        uint32_t procedure=r8(conn+635u);
        w32(object+8u,anchor+(span-widening));
        w32(object+0x14u,span);
        w32(object+0xcu,r32(conn+204u)+widening+310u);
        w32(state+100u,r32(conn+204u)+widening*2u);
        w8(object+0x18u,procedure!=0x11u);
        apply_instant(conn);
        if(r8(conn+770u)==1u&&r8(conn+769u)==0u&&(r8(((uintptr_t)&em9305_ram_805a6c + 0x19u))&0x80u)!=0u){
            uint32_t count=(uint8_t)(r8(conn+772u)-1u);
            w8(conn+772u,count);
            if(count==0u)(void)post(conn,8u,0x6901u);
        }
        uint32_t result=role_hook(conn,0u);
        uint32_t supervision=r8(conn+401u);
        w8(state+1u,result);
        if(supervision!=2u){
            uint32_t interval_us=r16(conn+266u)*1250u;
            uint32_t timeout_us=r16(conn+382u)*1000u;
            uint32_t since=(uint8_t)(r8(conn+262u)-r8(conn+202u)+1u);
            uint32_t limit=(uint8_t)(timeout_us/interval_us);
            if(since+1u==limit)w8(conn+401u,1u);
            else if(since>=limit)w8(conn+401u,2u);
        }
    }while(opencfw_em9305_associated_schedule_insert_312da4(object,
               (uintptr_t)opencfw_em9305_init_schedule_compare_318b78)==0u);
    if(r8(conn+748u)!=0u&&r16(conn+262u)>=r16(conn+754u)&&r8(conn+620u)==0u){
        uint32_t period=0u;
        if(r8(conn+77u)<3u){
            (void)post(conn,4u,0x6d01u);
            period=r16(conn+750u);
        }
        if(period==0u)w8(conn+748u,0u);
        else w16(conn+754u,period+r16(conn+262u));
    }
    {
        uint32_t closing=r8(conn+894u);
        if(closing==0u)return 0u;
        uintptr_t hook=r32(state+124u);
        if(hook==0u)return closing;
        return ((opencfw_em9305_hook3_329888)hook)(object,0u,0u);
    }
terminate:
    (void)opencfw_em9305_receive_terminate_325c08(conn,0x4cu);
    return opencfw_em9305_wsf_timer_stop(timer);
}

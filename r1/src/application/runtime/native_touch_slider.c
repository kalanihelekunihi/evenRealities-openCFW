#include "native_touch_slider.h"
#include "../board/native_touch_calibration.h"
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_touch_contact_state[100];
extern volatile uint8_t r1_touch_release_timer_pending,r1_touch_synthetic_flag;
extern void __aeabi_memclr(void *,uint32_t);
extern uint32_t r1_touch_gesture_dispatch_boundary(const void *);
extern void r1_touch_release_timer_callback(uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_model_b210a_check(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
/* Remaining authenticated cells of context0x200067c4. The adjacent timer,
 * calibration, direction and client cells retain their existing owners. */
volatile uint16_t r1_touch_long_press_threshold __attribute__((section(".r1.touch.slider.long_threshold"),aligned(2)))=1000;
volatile uint16_t r1_touch_coordinate_min __attribute__((section(".r1.touch.slider.min"),aligned(2)))=10;
volatile uint16_t r1_touch_coordinate_max __attribute__((section(".r1.touch.slider.max"),aligned(2)))=180;
volatile uint8_t r1_touch_slider_record[4] __attribute__((section(".r1.touch.slider.record"),aligned(4)))={0};
volatile float r1_touch_pressure_reference __attribute__((section(".r1.touch.slider.pressure_reference"),aligned(4)))=240.0f;
volatile float r1_touch_pressure_peak __attribute__((section(".r1.touch.slider.pressure_peak"),aligned(4)))=400.0f;
volatile uint32_t r1_touch_slider_timeout_log_tick __attribute__((section(".r1.touch.slider.timeout_tick"),aligned(4)))=0;
static uint32_t bits(float x){union{float f;uint32_t u;}v={.f=x};return v.u;}
static float floating(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static float sample_float(uint32_t offset){return floating(read32(r1_touch_contact_state+offset));}
/* Defined counterpart of VCVT.U32.F32, including non-finite inputs. */
static uint32_t unsigned_float(float x)
{if(!(x>0.0f))return 0;if(x>=4294967296.0f)return UINT32_MAX;return (uint32_t)x;}
static void dispatch(void)
{(void)r1_touch_gesture_dispatch_boundary((const void *)(uintptr_t)r1_touch_slider_record);}
static void invalid_scale_log(void)
{
 static const char ring[]="[RING]scale_value not initialized! raw_min=%u, scale=%d";
 static const char sdk[]="scale_value not initialized! raw_min=%u, scale=%d";
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint64_t scale=r1_binary32_to_binary64_bits(bits(r1_touch_slider_step));
  (void)r1_structured_log_format(0x04800000,ring,ring,(uint32_t)r1_touch_slider_origin,scale);
 }
 if(r1_structured_log_mode_get()&2u){float scale=r1_touch_slider_step;uint32_t origin=r1_touch_slider_origin;
  (void)nrf_log_frontend_std_2(0x001c0001,sdk,origin,unsigned_float(scale));}
}
static void overflow_log(uint32_t raw)
{
 static const char ring[]="[RING]x coordinate overflow: raw_x=%u, temp_x=%f, clamping to %d";
 static const char sdk[]="x coordinate overflow: raw_x=%u, temp_x=%f, clamping to %d";
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x08c00000,ring,ring,raw,UINT64_C(0x4069000000000000),200u);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_3(0x001c0002,sdk,raw,200,200);
}
static void timeout_log(void)
{
 static const char ring[]="[RING]SLIDER_EVENT_ERROR: press timeout %u ms";
 static const char sdk[]="SLIDER_EVENT_ERROR: press timeout %u ms";
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04400000,ring,ring,read32(r1_touch_contact_state+4));
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0001,sdk,read32(r1_touch_contact_state+4));
}
static int pressure_gate(float input)
{
 float peak=r1_touch_pressure_peak,reference=r1_touch_pressure_reference;
 float delta=peak-reference,portion=delta*0.3f,limit=reference+portion;
 return limit>input;
}
static int interior(uint32_t margin)
{
 uint32_t lower=(uint32_t)r1_touch_coordinate_min+margin;
 uint32_t position=r1_touch_contact_state[25];
 if(position<=lower)return 0;
 return (int32_t)position<(int32_t)((uint32_t)r1_touch_coordinate_max-margin);
}
void r1_touch_slider_state_machine(uint32_t active,uint32_t raw,uint32_t tick,uint32_t opaque,float pressure)
{
 (void)opaque;volatile uint8_t *s=r1_touch_contact_state,*event=r1_touch_slider_record;
 if(raw==65535u)raw=s[37];
 if(pressure>r1_touch_pressure_peak)r1_touch_pressure_peak=pressure;
 float scale=r1_touch_slider_step;
 /* The native HI after VCMP accepts unordered; NaN scales follow the
  * arithmetic path rather than the nonpositive-scale diagnostic. */
 if(scale<=0.0f){invalid_scale_log();return;}
 float x=((float)raw-(float)r1_touch_slider_origin)/scale;
 if(x<0.0f)x=0.0f;
 else if((int32_t)bits(x)>(int32_t)UINT32_C(0x43480000)){x=200.0f;overflow_log(raw);}
 if(x<(float)r1_touch_coordinate_min)r1_touch_coordinate_min=(uint16_t)unsigned_float(x);
 else if(x>(float)r1_touch_coordinate_max)r1_touch_coordinate_max=(uint16_t)unsigned_float(x);
 write32(event,0);
 uint32_t previous0=read32(s+36),previous1=read32(s+40),previous2=read32(s+44);
 write32(s+24,previous0);write32(s+28,previous1);write32(s+32,previous2);
 s[36]=(uint8_t)active;uint32_t position=(uint8_t)unsigned_float(x);s[37]=(uint8_t)position;
 write32(s+40,tick);write32(s+44,bits(pressure));
 if(active==1u){
  if(!s[24]){
   s[93]=0;s[92]=0;s[94]=0;s[95]=0;s[96]=0;
   (void)r1_touch_slider_velocity_filter(position,tick);
   __aeabi_memclr((void *)(uintptr_t)(s+68),24);
   s[8]=0;write32(s+4,0);
   uint32_t initial=read32(s+36),time=read32(s+40),average=read32(s+44);
   write32(s+20,average);write32(s+12,initial);write32(s+16,time);
   uint32_t pending=s[48],released=pending?read32(s+52):0;
   if(pending && released && (uint32_t)(time-released)<=300u){
    s[0]=2;s[48]=0;
    if(r1_touch_release_timer_pending){(void)r1_native_delayed_cancel(r1_touch_release_timer_callback,0);r1_touch_release_timer_pending=0;}
   }else s[0]=1;
   write32(s+56,read32(s+40));s[60]=s[37];event[0]=1;
  }else{
   (void)r1_touch_slider_velocity_filter(position,tick);
   uint32_t start=read32(s+16),now=read32(s+40),elapsed=now-start;write32(s+4,elapsed);
   if(elapsed>=10000u){
    s[48]=0;s[0]=0;
    if((uint32_t)(now-r1_touch_slider_timeout_log_tick)>=10000u){r1_touch_slider_timeout_log_tick=now;timeout_log();}
    event[0]=128;
   }else if(s[8]==0){
    float current=sample_float(44),delta=current-sample_float(32);
    uint32_t current_position=s[37];int32_t movement=(int32_t)current_position-(int32_t)s[13];
    uint32_t distance=(uint32_t)(movement<0?-movement:movement);
    if(distance>=50u && (int32_t)bits(delta)<(int32_t)UINT32_C(0x447a0000)){
     s[8]=1;s[48]=0;s[0]=0;s[49]=0;
     if((uint32_t)(tick-read32(s+56))<100u)return;
     if((uint32_t)(tick-start)<=150u && !pressure_gate(pressure))return;
     write32(s+56,tick);s[60]=(uint8_t)current_position;write32(s+64,bits(current));
     event[0]=movement<0?32:64;event[1]=(uint8_t)distance;event[2]=s[95];
    }else if(elapsed>=r1_touch_long_press_threshold){s[8]=2;s[48]=0;s[0]=0;s[49]=0;event[0]=16;}
   }else if(s[8]==1){
    float delta=sample_float(44)-sample_float(64);int32_t movement=(int32_t)s[37]-(int32_t)s[60];
    uint32_t distance=(uint32_t)(movement<0?-movement:movement);
    (void)r1_model_b210a_check();
    if(distance>=15u && (uint32_t)(tick-read32(s+56))>=100u && (int32_t)bits(delta)<(int32_t)UINT32_C(0x447a0000)
       && ((uint32_t)(tick-read32(s+16))>150u || pressure_gate(pressure))){
     write32(s+56,tick);s[60]=s[37];write32(s+64,read32(s+44));
     event[0]=movement<0?32:64;event[1]=(uint8_t)distance;event[2]=s[95];
    }
   }
  }
 }else if(active==0u){
  if(s[24]){
   event[0]|=2;uint32_t duration=tick-read32(s+16);write32(s+4,duration);
   int32_t movement=(int32_t)position-(int32_t)s[60];uint32_t distance=(uint32_t)(movement<0?-movement:movement);
   float delta=pressure-sample_float(64);uint32_t mode=s[8];
   if(mode==2u){
    s[8]=0;s[48]=0;s[0]=0;s[49]=0;write32(s+52,tick);r1_touch_synthetic_flag=1;dispatch();r1_touch_synthetic_flag=0;return;
   }else if(mode==1u){
    s[8]=0;s[49]=0;write32(s+52,tick);(void)r1_model_b210a_check();
    if(distance>=15u && (int32_t)bits(delta)<(int32_t)UINT32_C(0x447a0000)
       && ((uint32_t)(tick-read32(s+16))>150u || pressure_gate(pressure))){
     write32(s+56,tick);s[60]=s[37];write32(s+64,read32(s+44));
     event[0]|=movement<0?32:64;event[1]=(uint8_t)distance;event[2]=s[95];dispatch();
    }
    uint8_t release[4]={2,0,0,0};r1_touch_synthetic_flag=1;
    (void)r1_touch_gesture_dispatch_boundary(release);r1_touch_synthetic_flag=0;return;
   }else if((uint32_t)(duration-51u)<149u && interior(10)){
    uint32_t release=r1_touch_release_debounce(tick);
    if(s[0]>=2u){s[48]=0;s[0]=0;write32(s+52,tick);event[0]|=8;}
    else{s[48]=1;write32(s+52,tick);}
    event[3]=(uint8_t)release;
   }else if((uint32_t)(duration-200u)<200u && interior(20)){
    s[48]=0;s[0]=0;uint32_t release=r1_touch_release_debounce(tick);write32(s+52,tick);event[0]|=4;event[3]=(uint8_t)release;
   }else write32(s+52,tick);
  }else if(s[48] && (uint32_t)(tick-read32(s+52))>300u && read32(s+4)>50u && interior(10)){
   s[48]=0;s[0]=0;event[0]=4;
  }
 }
 dispatch();
}

/* SPDX-License-Identifier: MIT
 * Recovered common command callback; candidate pending target qualification.
 */
#include <stdint.h>
#include <stddef.h>
struct command_packet { uint32_t reserved; uint16_t command; uint8_t reserved6,ready; uint32_t reserved8,reserved12; uint8_t *payload; uint32_t reserved20,length; };
struct command_state { uint8_t buffer[32]; uint32_t timestamp; uint16_t reply,reserved38; uint32_t mic; uint8_t version_reverse[4],version_wire[4]; uint16_t vad,reserved54; uint32_t gain,request; uint8_t mode; };
_Static_assert(offsetof(struct command_state,gain)==56,"State ABI");
_Static_assert(offsetof(struct command_packet,length)==24,"Packet ABI");
extern struct command_state open_cfw_gx8002_command_state;
extern struct command_packet open_cfw_gx8002_command_response;
extern int open_cfw_gx8002_app_reply(uint32_t,uint32_t,uint32_t);
extern int open_cfw_gx8002_command_enqueue(struct command_packet *);
extern uint32_t open_cfw_gx8002_command_mic(uint32_t);
extern void open_cfw_gx8002_command_gsensor(void);
extern void open_cfw_gx8002_command_direction(uint32_t,uint32_t);
extern void open_cfw_gx8002_command_beamforming(void);
extern int open_cfw_gx8002_command_gain(uint32_t,uint32_t);
extern void open_cfw_gx8002_command_padmux(uint32_t,uint32_t);
extern void open_cfw_gx8002_command_delay(uint32_t,uint32_t);
extern char *strtok(char *,const char *);
extern int printf(const char *,...);
#define LOG(n) extern const char open_cfw_gx8002_callback_##n[]
LOG(mic);LOG(gsensor);LOG(version);LOG(delimiter);LOG(beamforming);LOG(vad_open);LOG(vad_close);LOG(byte);LOG(gain_ok);LOG(gain_fail);LOG(gain_range);LOG(dmic_open);LOG(dmic_init);LOG(dmic_close);LOG(dmic_stop);LOG(delay);LOG(i2s);LOG(mode);
#define S open_cfw_gx8002_command_state
#define R open_cfw_gx8002_command_response
#define PRINT(n) printf(open_cfw_gx8002_callback_##n)
static const uint8_t delay_response=1;
int open_cfw_gx8002_app_command_callback(struct command_packet *packet)
{
    if(packet->command==368){PRINT(mic);if(!S.mic)S.mic=open_cfw_gx8002_command_mic(0);open_cfw_gx8002_app_reply(0,112,S.mic!=0);}
    if(packet->command==369){PRINT(gsensor);open_cfw_gx8002_command_gsensor();open_cfw_gx8002_app_reply(0,113,0);}
    if(packet->command==258){
        PRINT(version);char version[]="0.0.2.3";
        S.version_reverse[3]=(uint8_t)(strtok(version,open_cfw_gx8002_callback_delimiter)[0]-48);
        S.version_reverse[2]=(uint8_t)(strtok(0,open_cfw_gx8002_callback_delimiter)[0]-48);
        S.version_reverse[1]=(uint8_t)(strtok(0,open_cfw_gx8002_callback_delimiter)[0]-48);
        uint8_t last=(uint8_t)(strtok(0,open_cfw_gx8002_callback_delimiter)[0]-48);
        S.version_reverse[0]=last;S.version_wire[3]=last;S.version_wire[0]=S.version_reverse[3];
        /* Preserve the observed version-byte publication before its header. */
        __asm__ volatile ("" ::: "memory");
        R.command=514;S.version_wire[1]=S.version_reverse[2];R.ready=1;S.version_wire[2]=S.version_reverse[1];
        R.payload=S.version_wire;R.length=4;open_cfw_gx8002_command_enqueue(&R);
    }
    if(packet->command==263){PRINT(beamforming);open_cfw_gx8002_app_reply(0,7,1);open_cfw_gx8002_command_direction(0,0);open_cfw_gx8002_command_direction(1,0);open_cfw_gx8002_command_beamforming();}
    if(packet->command==265){PRINT(vad_open);open_cfw_gx8002_app_reply(0,9,1);S.vad=1;}
    if(packet->command==266){PRINT(vad_close);open_cfw_gx8002_app_reply(0,10,1);S.vad=0;}
    if(packet->command==267){
        for(uint32_t i=0;i<packet->length;i++){printf(open_cfw_gx8002_callback_byte,packet->payload[i]);S.gain=packet->payload[i];}
        if(S.gain<=48){
            int result=open_cfw_gx8002_command_gain(2,S.gain);
            if(!result){printf(open_cfw_gx8002_callback_gain_ok,S.gain);open_cfw_gx8002_app_reply(0,11,1);}
            else {printf(open_cfw_gx8002_callback_gain_fail,S.gain);open_cfw_gx8002_app_reply(0,11,0);}
        }else{printf(open_cfw_gx8002_callback_gain_range,S.gain);open_cfw_gx8002_app_reply(0,11,0);}
    }
    if(packet->command==268){PRINT(dmic_open);PRINT(dmic_init);open_cfw_gx8002_command_padmux(0,7);open_cfw_gx8002_command_padmux(1,9);open_cfw_gx8002_app_reply(0,12,1);}
    if(packet->command==269){PRINT(dmic_close);PRINT(dmic_stop);open_cfw_gx8002_command_padmux(0,1);open_cfw_gx8002_command_padmux(1,1);open_cfw_gx8002_command_direction(0,0);open_cfw_gx8002_command_direction(1,0);open_cfw_gx8002_app_reply(0,13,1);}
    if(packet->command==270){PRINT(delay);open_cfw_gx8002_command_delay(0,1);R.command=packet->command;R.ready=1;R.payload=(uint8_t *)&delay_response;R.length=1;open_cfw_gx8002_command_enqueue(&R);}
    if(packet->command==271){PRINT(i2s);S.request=1;S.mode=packet->payload[0];printf(open_cfw_gx8002_callback_mode,S.mode);}
    return 0;
}

/* Source diagnostic definitions, placed by the native linker script. */
const char open_cfw_gx8002_callback_mic[] __attribute__((aligned(1)))="receive misc test cmd\n";
const char open_cfw_gx8002_callback_gsensor[] __attribute__((aligned(1)))="receive gsensor test cmd\n";
const char open_cfw_gx8002_callback_version[] __attribute__((aligned(1)))="receive version req\n";
const char open_cfw_gx8002_callback_delimiter[] __attribute__((aligned(1)))=".";
const char open_cfw_gx8002_callback_beamforming[] __attribute__((aligned(1)))="receive switch bf req\n";
const char open_cfw_gx8002_callback_vad_open[] __attribute__((aligned(1)))="open vad reporting\n";
const char open_cfw_gx8002_callback_vad_close[] __attribute__((aligned(1)))="close vad reporting\n";
const char open_cfw_gx8002_callback_byte[] __attribute__((aligned(1)))="0x%x \n";
const char open_cfw_gx8002_callback_gain_ok[] __attribute__((aligned(1)))="set pga gain %d success\n";
const char open_cfw_gx8002_callback_gain_fail[] __attribute__((aligned(1)))="set pga gain %d fail\n";
const char open_cfw_gx8002_callback_gain_range[] __attribute__((aligned(1)))="set pga gain %d fail，gain range 0~48\n";
const char open_cfw_gx8002_callback_dmic_open[] __attribute__((aligned(1)))="receive open dmic req\n";
const char open_cfw_gx8002_callback_dmic_init[] __attribute__((aligned(1)))="dmic init master\n";
const char open_cfw_gx8002_callback_dmic_close[] __attribute__((aligned(1)))="receive close dmic req\n";
const char open_cfw_gx8002_callback_dmic_stop[] __attribute__((aligned(1)))="dmic close master\n";
const char open_cfw_gx8002_callback_delay[] __attribute__((aligned(1)))="receive set pdm ch delay req\n";
const char open_cfw_gx8002_callback_i2s[] __attribute__((aligned(1)))="receive set i2s status req\n";
const char open_cfw_gx8002_callback_mode[] __attribute__((aligned(1)))="i2s_mode_state %d\n";

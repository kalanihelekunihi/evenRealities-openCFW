/* SPDX-License-Identifier: MIT
 * Recovered application command registration. Pending target qualification.
 */
#include <stdint.h>
#include <stddef.h>
struct app_command {
    uint32_t reserved, command;
    void *buffer;
    uint32_t buffer_bytes, reserved2;
    void (*callback)(void);
    const char *name;
};
_Static_assert(sizeof(struct app_command)==28,"Command ABI");
_Static_assert(offsetof(struct app_command,callback)==20,"Callback ABI");
extern void *memset(void *,int,unsigned long);
extern void open_cfw_gx8002_app_command_callback(void);
extern int open_cfw_gx8002_app_register_command(struct app_command *);
extern uint8_t open_cfw_gx8002_app_command_buffer[32];
#define LABEL(n,t) const char open_cfw_gx8002_command_##n[] __attribute__((aligned(1)))=t
LABEL(mic,"mic status");
LABEL(gsensor,"gsensor status");
LABEL(version,"version");
LABEL(beamforming,"switch bf cmd");
LABEL(vad_open,"open vad reporting");
LABEL(vad_close,"close vad reporting");
LABEL(gain,"set pga gain");
LABEL(dmic_start,"start Dmic cmd");
LABEL(dmic_close,"close Dmic cmd");
LABEL(pdm_delay,"pdm ch delay");
LABEL(i2s_state,"i2s set state");
#define INIT(i,id,n) do { memset(&commands[i],0,sizeof commands[i]); commands[i].command=id; commands[i].callback=open_cfw_gx8002_app_command_callback; commands[i].name=open_cfw_gx8002_command_##n; } while(0)
void open_cfw_gx8002_app_commands(void)
{
    struct app_command commands[11];
    INIT(0,368,mic);INIT(1,369,gsensor);INIT(2,258,version);
    INIT(3,263,beamforming);INIT(4,265,vad_open);INIT(5,266,vad_close);
    INIT(6,267,gain);commands[6].buffer=open_cfw_gx8002_app_command_buffer;commands[6].buffer_bytes=32;
    INIT(7,268,dmic_start);INIT(8,269,dmic_close);INIT(9,270,pdm_delay);
    INIT(10,271,i2s_state);commands[10].buffer=open_cfw_gx8002_app_command_buffer;commands[10].buffer_bytes=32;
    open_cfw_gx8002_app_register_command(&commands[0]);
    open_cfw_gx8002_app_register_command(&commands[1]);
    open_cfw_gx8002_app_register_command(&commands[2]);
    open_cfw_gx8002_app_register_command(&commands[3]);
    open_cfw_gx8002_app_register_command(&commands[4]);
    open_cfw_gx8002_app_register_command(&commands[5]);
    open_cfw_gx8002_app_register_command(&commands[6]);
    open_cfw_gx8002_app_register_command(&commands[7]);
    open_cfw_gx8002_app_register_command(&commands[8]);
    open_cfw_gx8002_app_register_command(&commands[9]);
    open_cfw_gx8002_app_register_command(&commands[10]);
}

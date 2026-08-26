import subprocess,tempfile,textwrap,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/"components/shared/cordio";S=D/"runtime_cordio_dm_conn_slave_leg.c"
class T(unittest.TestCase):
 def test_behavior_and_builds(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include "runtime_cordio_dm_conn_slave_leg.h"
   static unsigned start,stop,connected,advfail,opened,failed,locks,unlocks;static uint8_t a0;
   void open_cfw_cordio_dm_advertising_start_directed(uint8_t t,uint16_t d,uint8_t a,uint8_t*p){start++;assert(t==2&&d==99&&a==1);a0=p[0];}void open_cfw_cordio_dm_advertising_stop_directed(void){stop++;}void open_cfw_cordio_dm_advertising_connected(void){connected++;}void open_cfw_cordio_dm_advertising_connect_failed(void){advfail++;}void open_cfw_cordio_dm_connection_action_opened(void*c,void*m){assert(c&&m);opened++;}void open_cfw_cordio_dm_connection_action_failed(void*c,void*m){assert(c&&m);failed++;}void open_cfw_cordio_wsf_task_lock(void){locks++;}void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
   int main(void){struct open_cfw_cordio_dm_connection_open_message m={0};int c=1;m.advertising_type=2;m.duration=99;m.address_type=1;m.peer_address[0]=7;open_cfw_cordio_dm_connection_slave_legacy_action_accept(&c,&m);assert(start==1&&a0==7);open_cfw_cordio_dm_connection_slave_legacy_action_cancel(&c,&m);open_cfw_cordio_dm_connection_slave_legacy_action_accepted(&c,&m);open_cfw_cordio_dm_connection_slave_legacy_action_failed(&c,&m);assert(stop==1&&connected==1&&advfail==1&&opened==1&&failed==2);open_cfw_cordio_dm_connection_slave_legacy_action_accept(&c,0);open_cfw_cordio_dm_connection_slave_legacy_action_cancel(0,&m);assert(failed==2);open_cfw_cordio_dm_conn_slave_leg_action_table=11;open_cfw_cordio_dm_conn_slave_leg_update_action_table=22;open_cfw_cordio_dm_connection_slave_legacy_initialize();assert(locks==1&&unlocks==1&&open_cfw_cordio_dm_conn_slave_leg_action_sets[2]==11&&open_cfw_cordio_dm_conn_slave_leg_update_action_sets[2]==22);return 0;}
  ''')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"h.c";e=Path(d)/"t";p.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(D),str(S),str(p),"-o",str(e)],check=True);subprocess.run([str(e)],check=True)
   for x in [None,"ACCEPT","CANCEL","ACCEPTED","FAILED","INIT"]:
    c=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(D),"-DOPEN_CFW_DM_CONN_SLAVE_LEG_PRODUCTION=1"]
    if x:c.append(f"-DOPEN_CFW_DM_CONN_SLAVE_LEG_{x}_ONLY=1")
    c += ["-c",str(S),"-o",str(Path(d)/f"{x or 'all'}.o")];subprocess.run(c,check=True)
if __name__=="__main__":unittest.main()

import subprocess,tempfile,textwrap,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/"components/shared/cordio";S=D/"runtime_cordio_dm_conn_master.c"
class T(unittest.TestCase):
 def test_behavior_and_target_builds(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include "runtime_cordio_dm_conn_master.h"
   static struct open_cfw_cordio_dm_conn_slave_control c;static unsigned cancel,privacy,hci,rsp,look,exec,opened,locks,unlocks;
   void open_cfw_cordio_hci_create_connection_cancel(void){cancel++;}
   void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t e,uint8_t p,uint8_t a,uint8_t x){privacy++;assert(e==0x0e&&p==1&&!a&&!x);}
   void open_cfw_cordio_hci_connection_update(uint16_t h,struct open_cfw_cordio_dm_connection_spec*s){hci++;assert(h==9&&s);}
   void open_cfw_cordio_l2c_connection_update_response(uint8_t i,uint16_t h,uint16_t r){rsp++;assert(i==3&&h==9&&!r);}
   struct open_cfw_cordio_dm_conn_slave_control*open_cfw_cordio_dm_connection_control_by_handle(uint16_t h){look++;return h==9?&c:0;}
   void open_cfw_cordio_dm_connection_update_execute(struct open_cfw_cordio_dm_conn_slave_control*x,void*v){struct open_cfw_cordio_dm_conn_master_l2c_indication*m=v;exec++;assert(x==&c&&m->header.event==0x72&&m->identifier==3&&m->connection_spec);}
   uint8_t open_cfw_cordio_dm_connection_open_accept(uint8_t ci,uint8_t ip,uint8_t ah,uint8_t at,uint16_t d,uint8_t me,uint8_t ty,uint8_t*a,uint8_t role){opened++;assert(ci==2&&ip==1&&!ah&&!at&&!d&&!me&&ty==7&&a[0]==8&&!role);return 4;}
   void open_cfw_cordio_wsf_task_lock(void){locks++;}void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
   uint64_t open_cfw_cordio_hci_get_supported_features(void){return 0;}void open_cfw_cordio_l2c_connection_update_request(uint16_t h,struct open_cfw_cordio_dm_connection_spec*s){(void)h;(void)s;}
   int main(void){struct open_cfw_cordio_dm_conn_slave_update_message u={0};struct open_cfw_cordio_dm_conn_master_l2c_indication i={0};struct open_cfw_cordio_dm_connection_spec s={0};uint8_t a[6]={8};c.handle=9;
    open_cfw_cordio_dm_connection_master_action_cancel(&c,&u);assert(cancel==1&&privacy==1);
    open_cfw_cordio_dm_connection_master_action_update(&c,&u);assert(hci==1);
    i.identifier=3;i.connection_spec=&s;open_cfw_cordio_dm_connection_master_action_l2c_indication(&c,&i);assert(rsp==1&&hci==2);
    open_cfw_cordio_dm_connection_master_l2c_indication(3,9,&s);open_cfw_cordio_dm_connection_master_l2c_indication(3,8,&s);assert(look==2&&exec==1);
    assert(open_cfw_cordio_dm_connection_master_open(2,1,7,a)==4&&opened==1);assert(!open_cfw_cordio_dm_connection_master_open(2,1,7,0)&&opened==1);
    open_cfw_cordio_dm_connection_master_set_address_type(6);assert(locks==1&&unlocks==1&&open_cfw_cordio_dm_conn_master_address_type==6);
    open_cfw_cordio_dm_connection_master_action_update(0,&u);open_cfw_cordio_dm_connection_master_action_update(&c,0);open_cfw_cordio_dm_connection_master_action_l2c_indication(0,&i);open_cfw_cordio_dm_connection_master_action_l2c_indication(&c,0);i.connection_spec=0;open_cfw_cordio_dm_connection_master_action_l2c_indication(&c,&i);open_cfw_cordio_dm_connection_master_l2c_indication(3,9,0);assert(hci==2&&rsp==1&&exec==1);return 0;}
  ''')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"h.c";x=Path(d)/"x";p.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(D),str(S),str(p),"-o",str(x)],check=True);subprocess.run([str(x)],check=True)
   for q in [None,"CANCEL","UPDATE","L2C_ACTION","L2C_INDICATION","OPEN","SET_ADDRESS"]:
    c=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(D),"-DOPEN_CFW_DM_CONN_MASTER_PRODUCTION=1"]
    if q:c.append(f"-DOPEN_CFW_DM_CONN_MASTER_{q}_ONLY=1")
    c += ["-c",str(S),"-o",str(Path(d)/f"{q or 'all'}.o")];subprocess.run(c,check=True)
if __name__=="__main__":unittest.main()

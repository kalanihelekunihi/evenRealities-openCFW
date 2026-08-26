import subprocess,tempfile,textwrap,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/"components/shared/cordio";S=D/"runtime_cordio_dm_conn_slave.c"
class T(unittest.TestCase):
 def test_behavior_and_target_builds(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include <string.h>
   #include "runtime_cordio_dm_conn_slave.h"
   static struct open_cfw_cordio_dm_conn_slave_control c;static unsigned hc,lc,look,exec,opened,calls;static uint64_t hf;static unsigned char raw[16];
   static void cb(void*p){calls++;memcpy(raw,p,sizeof(raw));}
   uint64_t open_cfw_cordio_hci_get_supported_features(void){return hf;}
   void open_cfw_cordio_hci_connection_update(uint16_t h,struct open_cfw_cordio_dm_connection_spec*s){hc++;assert(h==9&&s);}
   void open_cfw_cordio_l2c_connection_update_request(uint16_t h,struct open_cfw_cordio_dm_connection_spec*s){lc++;assert(h==9&&s);}
   struct open_cfw_cordio_dm_conn_slave_control*open_cfw_cordio_dm_connection_control_by_handle(uint16_t h){look++;return h==9?&c:0;}
   void open_cfw_cordio_dm_connection_update_execute(struct open_cfw_cordio_dm_conn_slave_control*x,void*m){struct open_cfw_cordio_dm_conn_slave_confirm_message*q=m;exec++;assert(x==&c&&q->header.event==0x73&&q->result==7);}
   uint8_t open_cfw_cordio_dm_connection_open_accept(uint8_t ci,uint8_t ip,uint8_t ah,uint8_t at,uint16_t d,uint8_t me,uint8_t ty,uint8_t*a,uint8_t role){opened++;assert(ci==2&&!ip&&ah==3&&at==4&&d==5&&me==6&&ty==7&&a[0]==8&&role==1);return 3;}
   int main(void){struct open_cfw_cordio_dm_conn_slave_update_message m={0};struct open_cfw_cordio_dm_conn_slave_confirm_message f={0};uint8_t a[6]={8};
    open_cfw_cordio_dm_conn_slave_application_callback=cb;c.handle=9;c.connection_id=2;c.features=2;hf=2;
    open_cfw_cordio_dm_connection_slave_action_update(&c,&m);assert(hc==1&&!lc);
    hf=0;open_cfw_cordio_dm_connection_slave_action_update(&c,&m);assert(lc==1&&c.updating==1);
    open_cfw_cordio_dm_connection_slave_action_update(&c,&m);assert(calls==1&&raw[2]==0x29&&raw[3]==0x0c&&raw[4]==0x0c&&raw[6]==9);
    f.result=0;open_cfw_cordio_dm_connection_slave_action_l2c_confirm(&c,&f);assert(c.updating==0&&calls==1);
    c.updating=1;f.result=7;open_cfw_cordio_dm_connection_slave_action_l2c_confirm(&c,&f);assert(calls==2&&raw[3]==7);
    open_cfw_cordio_dm_connection_slave_l2c_confirm(9,7);open_cfw_cordio_dm_connection_slave_l2c_confirm(8,7);assert(look==2&&exec==1);
    open_cfw_cordio_dm_connection_slave_l2c_reject(9,11);assert(calls==3&&raw[2]==0x77&&raw[4]==11&&raw[6]==9);
    assert(open_cfw_cordio_dm_connection_slave_accept(2,3,4,5,6,7,a)==3&&opened==1);assert(open_cfw_cordio_dm_connection_slave_accept(2,3,4,5,6,7,0)==0&&opened==1);
    open_cfw_cordio_dm_connection_slave_action_update(0,&m);open_cfw_cordio_dm_connection_slave_action_update(&c,0);open_cfw_cordio_dm_connection_slave_action_l2c_confirm(0,&f);open_cfw_cordio_dm_connection_slave_action_l2c_confirm(&c,0);open_cfw_cordio_dm_conn_slave_application_callback=0;open_cfw_cordio_dm_connection_slave_update_callback(&c,1);open_cfw_cordio_dm_connection_slave_l2c_reject(1,1);assert(calls==3);return 0;}
  ''')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"h.c";x=Path(d)/"x";p.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(D),str(S),str(p),"-o",str(x)],check=True);subprocess.run([str(x)],check=True)
   for q in [None,"CALLBACK","UPDATE","CONFIRM","L2C_CONFIRM","L2C_REJECT","ACCEPT"]:
    c=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(D),"-DOPEN_CFW_DM_CONN_SLAVE_PRODUCTION=1"]
    if q:c.append(f"-DOPEN_CFW_DM_CONN_SLAVE_{q}_ONLY=1")
    c += ["-c",str(S),"-o",str(Path(d)/f"{q or 'all'}.o")];subprocess.run(c,check=True)
if __name__=="__main__":unittest.main()

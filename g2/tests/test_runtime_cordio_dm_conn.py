import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORDIO = ROOT / "components/shared/cordio"
SOURCE = CORDIO / "runtime_cordio_dm_conn.c"
INCLUDES = [
    CORDIO,
    ROOT / "third_party/cordio/wsf/include",
    ROOT / "third_party/cordio/ble-host/include",
    ROOT / "third_party/cordio/ble-host/sources/stack/cfg",
    ROOT / "third_party/cordio/ble-host/sources/stack/dm",
]


class CordioDmConnectionSourceTests(unittest.TestCase):
    def test_behavior_bounds_source_only_apis_and_all_target_profiles(self) -> None:
        harness = textwrap.dedent(r'''
            #include <assert.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_dm_conn.h"
            #include "dm_main.h"

            dmCb_t dmCb;
            dmConnAct_t *dmConnActSet[DM_CONN_NUM_ACT_SETS];
            dmFcnIf_t *dmFcnIfTbl[DM_NUM_IDS];
            static unsigned locks, unlocks, allocs, sends, callbacks, sm_calls;
            static unsigned hci_disconnect, hci_features, hci_version, hci_rssi;
            static unsigned hci_reply, hci_reject, hci_data_len, hci_auth, hci_sca;
            static unsigned privacy_events, cte_events, update_actions;
            static uint8_t message[256], public_addr[6] = {9,8,7,6,5,4};
            static void *last_message;

            void BdaCpy(uint8_t *d, const uint8_t *s) { memcpy(d, s, 6); }
            bool_t BdaCmp(const uint8_t *a, const uint8_t *b) { return memcmp(a,b,6) == 0; }
            void WsfTaskLock(void) { locks++; }
            void WsfTaskUnlock(void) { unlocks++; }
            void *WsfMsgAlloc(uint16_t n) { assert(n <= sizeof(message)); allocs++; memset(message,0,sizeof(message)); return message; }
            void WsfMsgSend(wsfHandlerId_t h, void *p) { assert(h == 7 && p == message); sends++; last_message = p; }
            void HciDisconnectCmd(uint16_t h, uint8_t r) { assert(h == 0x1234 && r == 0x13); hci_disconnect++; }
            uint8_t DmHostAddrType(uint8_t t) { return t; }
            uint8_t *HciGetBdAddr(void) { return public_addr; }
            void dmDevPassEvtToDevPriv(uint8_t e,uint8_t p,uint8_t a,bool_t c) { (void)e;(void)p;(void)a;(void)c;privacy_events++; }
            void dmDevPassEvtToConnCte(uint8_t s,dmConnId_t i) { (void)s;(void)i;cte_events++; }
            void dmConnSmExecute(dmConnCcb_t *c,dmConnMsg_t *m) { assert(c && m); sm_calls++; }
            void HciLeRemoteConnParamReqNegReply(uint16_t h,uint8_t r) { (void)h;(void)r;hci_reject++; }
            void HciLeRequestPeerScaCmd(uint16_t h) { (void)h;hci_sca++; }
            void HciReadRssiCmd(uint16_t h) { (void)h;hci_rssi++; }
            void HciLeSetDataLen(uint16_t h,uint16_t o,uint16_t t) { (void)h;(void)o;(void)t;hci_data_len++; }
            void HciLeRemoteConnParamReqReply(uint16_t h,uint16_t a,uint16_t b,uint16_t l,uint16_t s,uint16_t m,uint16_t x) { (void)h;(void)a;(void)b;(void)l;(void)s;(void)m;(void)x;hci_reply++; }
            void HciWriteAuthPayloadTimeout(uint16_t h,uint16_t t) { (void)h;(void)t;hci_auth++; }
            void HciLeReadRemoteFeatCmd(uint16_t h) { (void)h;hci_features++; }
            void HciReadRemoteVerInfoCmd(uint16_t h) { (void)h;hci_version++; }
            uint8_t DmInitPhyToIdx(uint8_t p) { return p == HCI_INIT_PHY_LE_CODED_BIT ? 1U : 0U; }
            void dmEmptyReset(void) {}
            void dmEmptyHandler(wsfMsgHdr_t *m) { (void)m; }
            static void callback(dmEvt_t *e) { assert(e); callbacks++; }
            static void update_action(dmConnCcb_t *c,dmConnMsg_t *m) { assert(c && m); update_actions++; }

            int main(void) {
              uint8_t addr[6]={1,2,3,4,5,6};
              hciConnSpec_t spec={24,40,0,2000,0,0};
              dmConnMsg_t msg; dmConnCcb_t *c; dmConnAct_t actions[4]={update_action,update_action,update_action,update_action};
              dmCb.handlerId=7;
              vendorCcbInitLike();
              for(unsigned i=0;i<DM_CONN_MAX;i++){assert(dmConnCb.ccb[i].handle==0xffff);assert(dmConnCb.ccb[i].role==0xff);assert(!dmConnCb.ccb[i].inUse);}
              assert(dmConnCcbAlloc(NULL)==NULL); c=dmConnCcbAlloc(addr); assert(c&&c->connId==1&&c->inUse&&c->handle==0xffff); assert(dmConnCcbByBdAddr(addr)==c);assert(dmConnCcbById(0)==NULL&&dmConnCcbById(4)==NULL);assert(dmConnNum()==1);
              c->handle=0x1234;c->role=DM_ROLE_MASTER;c->peerAddrType=2;c->localAddrType=3;c->secLevel=4;
              assert(DmConnIdByHandle(0x1234)==1&&DmConnInUse(1));assert(!DmConnInUse(0));assert(DmConnPeerAddrType(1)==2&&DmConnLocalAddrType(1)==3&&DmConnSecLevel(1)==4);assert(DmConnPeerAddr(1)&&DmConnLocalAddr(1)&&DmConnPeerRpa(1)&&DmConnLocalRpa(1));assert(DmConnPeerAddr(0)==NULL&&DmConnLocalRpa(4)==NULL&&DmConnRole(0)==0xff);
              DmConnRegister(DM_CLIENT_ID_APP,callback);DmConnRegister(DM_CLIENT_ID_MAX,callback);memset(&msg,0,sizeof(msg));dmConnExecCback(&msg);assert(callbacks==1);dmConnExecCback(NULL);
              DmConnSetIdle(1,0x20,DM_CONN_BUSY);assert(DmConnCheckIdle(1)==0x20);DmConnSetIdle(1,0x20,DM_CONN_IDLE);assert(DmConnCheckIdle(1)==0);DmConnSetIdle(0,1,DM_CONN_BUSY);assert(DmConnCheckIdle(0)==0);
              DmConnInit();assert(dmFcnIfTbl[DM_ID_CONN]&&dmFcnIfTbl[DM_ID_CONN_2]&&dmFcnIfTbl[DM_ID_CONN_UPD]);assert(dmConnActSet[0]&&dmConnUpdActSet[0]);assert(locks==unlocks);
              unsigned before=allocs;DmConnReadRssi(0);assert(allocs==before);DmConnReadRssi(1);assert(allocs==before+1&&sends);assert(((wsfMsgHdr_t*)last_message)->param==1);
              DmReadRemoteFeatures(1);DmReadRemoteVerInfo(1);assert(hci_features==1&&hci_version==1);
              DmConnUpdate(1,&spec);DmRemoteConnParamReqReply(1,&spec);DmRemoteConnParamReqNegReply(1,0x3b);DmConnSetDataLen(1,100,200);DmWriteAuthPayloadTimeout(1,50);DmConnRequestPeerSca(1);assert(sends>=7);
              DmExtConnSetScanInterval(HCI_INIT_PHY_LE_1M_BIT|HCI_INIT_PHY_LE_CODED_BIT,(uint16_t[]){16,32},(uint16_t[]){8,16});DmExtConnSetConnSpec(HCI_INIT_PHY_LE_1M_BIT|HCI_INIT_PHY_LE_CODED_BIT,(hciConnSpec_t[]){spec,spec});assert(dmConnCb.scanInterval[0]==16&&dmConnCb.scanInterval[1]==32);DmExtConnSetScanInterval(1,NULL,NULL);DmExtConnSetConnSpec(1,NULL);
              dmConnUpdActSet[DM_CONN_ACT_SET_MASTER]=actions;memset(&msg,0,sizeof(msg));msg.hdr.event=DM_CONN_MSG_API_UPDATE_MASTER;dmConnUpdExecute(c,&msg);assert(update_actions==1);msg.hdr.event=0xff;dmConnUpdExecute(c,&msg);assert(update_actions==1);dmConnUpdExecute(NULL,&msg);
              dmConn2Msg_t msg2;memset(&msg2,0,sizeof(msg2));msg2.hdr.param=1;msg2.hdr.event=DM_CONN_MSG_API_READ_RSSI;dmConn2MsgHandler(&msg2.hdr);assert(hci_rssi==1);dmConn2MsgHandler(NULL);dmConn2HciHandler(NULL);dmConnMsgHandler(NULL);dmConnHciHandler(NULL);dmConnUpdMsgHandler(NULL);
              dmConnApiClose_t close_msg={{0},0x13,DM_CLIENT_ID_APP};dmConnSmActClose(c,(dmConnMsg_t*)&close_msg);assert(hci_disconnect==1);
              hciEvt_t event;memset(&event,0,sizeof(event));event.readRssiCmdCmpl.status=0;event.readRssiCmdCmpl.rssi=-20;dmConn2ActRssiRead(c,&event);assert(callbacks==2);
              dmConnCcbDealloc(NULL);dmConnCcbDealloc(c);assert(!c->inUse);return 0;
            }
        ''')
        selectors = [
            "dmConnCmplStates", "dmConnCcbAlloc", "dmConnCcbDealloc", "dmConnCcbByHandle",
            "dmConnCcbByBdAddr", "dmConnCcbById", "dmConnNum", "dmConnExecCback",
            "dmConnOpenAccept", "dmConnSmActNone", "dmConnSmActClose", "dmConnSmActConnOpened",
            "dmConnSmActConnFailed", "dmConnSmActConnClosed", "dmConnSmActHciUpdated",
            "dmConnUpdActNone", "dmConnUpdExecute", "dmConnReset", "dmConnMsgHandler",
            "dmConnHciHandler", "dmConn2MsgHandler", "dmConn2HciHandler", "dmConnUpdMsgHandler",
            "dmConn2ActRssiRead", "dmConn2ActRemoteConnParamReq", "dmConn2ActDataLenChange",
            "dmConn2ActWriteAuthToCmpl", "dmConn2ActAuthToExpired",
            "dmConn2ActReadRemoteFeaturesCmpl", "dmConn2ActReadRemoteVerInfoCmpl",
            "dmConn2ActReqPeerSca", "DmConnInit", "DmConnRegister", "DmConnClose",
            "DmReadRemoteFeatures", "DmReadRemoteVerInfo", "DmConnUpdate", "dmConnSetConnSpec",
            "dmConnSetScanInterval", "DmConnSetScanInterval", "DmExtConnSetScanInterval",
            "DmConnSetConnSpec", "DmExtConnSetConnSpec", "DmConnReadRssi",
            "DmRemoteConnParamReqReply", "DmRemoteConnParamReqNegReply", "DmConnSetDataLen",
            "DmWriteAuthPayloadTimeout", "DmConnRequestPeerSca", "DmConnIdByHandle", "DmConnInUse",
            "DmConnPeerAddrType", "DmConnPeerAddr", "DmConnLocalAddrType", "DmConnLocalAddr",
            "DmConnPeerRpa", "DmConnLocalRpa", "DmConnSecLevel", "DmConnSetIdle",
            "DmConnCheckIdle", "DmConnRole", "vendorCcbInitLike",
        ]
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            harness_path = directory / "harness.c"
            harness_path.write_text(harness)
            executable = directory / "host"
            include_flags = [value for path in INCLUDES for value in ("-I", str(path))]
            subprocess.run([
                "cc", "-std=c11", "-O0", "-fno-stack-protector", "-Wall", "-Wextra", "-Werror",
                "-Wno-unused-parameter", "-DDM_CONN_MAX=3", "-DDM_NUM_ADV_SETS=1",
                "-DDM_NUM_PHYS=2", *include_flags, str(SOURCE), str(harness_path), "-o", str(executable),
            ], check=True)
            subprocess.run([str(executable)], check=True)
            for selector in [None, *selectors]:
                output = directory / f"{selector or 'all'}.o"
                command = [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb", "-mcpu=cortex-m55",
                    "-O2", "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-Wno-unused-parameter", "-DOPEN_CFW_DM_CONN_PRODUCTION=1",
                    "-DDM_CONN_MAX=3", "-DDM_NUM_ADV_SETS=1", "-DDM_NUM_PHYS=2", *include_flags,
                ]
                if selector:
                    command.append(f"-DOPEN_CFW_DM_CONN_{selector}=1")
                command += ["-c", str(SOURCE), "-o", str(output)]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()

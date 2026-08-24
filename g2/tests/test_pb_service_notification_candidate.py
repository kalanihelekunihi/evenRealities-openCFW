#!/usr/bin/env python3
import hashlib,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/apollo_main/core_overlay/pb_service_notification.c";FIXTURE=ROOT/"tests/fixtures/pb_service_notification_host.c"
class PbServiceNotificationCandidateTests(unittest.TestCase):
 def test_host_behavior(self):
  with tempfile.TemporaryDirectory() as d:
   x=Path(d)/"notification";subprocess.run(["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),"-o",str(x)],cwd=ROOT,check=True);subprocess.run([str(x)],check=True)
 def test_selector_builds(self):
  selectors={"BUFFER_WRITE":"open_cfw_pb_service_notification_buffer_write","ZERO":"open_cfw_pb_service_notification_zero","ENCODE":"open_cfw_pb_notification_encode_and_send","DISPATCH":"APP_PbRxNotificationFrameDataProcess","RX_CTRL":"PB_RxNotifCtrl","TX_CTRL":"APP_PbTxEncodeNotifCtrl","TX_COMM_RESP":"APP_PbTxEncodeNotifCommResp","NOTIFY_APP":"APP_PbTxEncodeNotifAppIDNotInWhitelist","RX_WHITELIST_CTRL":"PB_RxNotifWhitelistCtrl","TX_WHITELIST_CTRL":"APP_PbTxEncodeNotifWhitelistCtrl","RX_WHITELIST_CHECK":"PB_RxNotifWhitelistChk","TX_WHITELIST_CHECK":"APP_PbTxEncodeNotifWhitelistChk"}
  with tempfile.TemporaryDirectory() as d:
   for s,e in selectors.items():
    o=Path(d)/(s+".o");subprocess.run(["/usr/bin/clang","-target","thumbv7em-none-eabi","-mthumb","-O2","-ffreestanding","-fno-jump-tables","-fomit-frame-pointer","-fno-builtin","-mno-unaligned-access","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fropi","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-DOPEN_CFW_PB_NOTIFICATION_"+s+"_ONLY=1","-c",str(SOURCE),"-o",str(o)],cwd=ROOT,check=True);out=subprocess.run(["nm",str(o)],check=True,capture_output=True,text=True).stdout;entries={p[2] for l in out.splitlines() if len(p:=l.split())==3 and p[1]=="T"};self.assertEqual(entries,{e})
 def test_source_pin(self):
  b=SOURCE.read_bytes();self.assertEqual(len(b),11668);self.assertEqual(hashlib.sha256(b).hexdigest(),"e99566f9d7cf6c3fd00c4c0cad332600a7e2a6f6c85f55101c409780fb8e31bc")
if __name__=="__main__":unittest.main()

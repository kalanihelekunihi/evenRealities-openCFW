
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void bleDelayedStartCback(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = _DAT_004b7f60;
  fw_event_loop_remove_delayed(_DAT_004b7f60);
  iVar2 = WsfMsgAlloc(0xc);
  if (iVar2 == 0) {
    fw_event_loop_push_delayed(uVar1,0,20000);
  }
  else {
    *(undefined1 *)(iVar2 + 2) = 0xbc;
    WsfMsgSend(*(undefined1 *)(DAT_004b81fc + 0x56),iVar2);
    fw_event_loop_push_delayed(uVar1,0,10000);
  }
  return;
}


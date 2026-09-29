
undefined4 FUN_00596f9e(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  cVar1 = translate_ui_0059db5c();
  if ((cVar1 == '\0') || (cVar1 == '\x02')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = translate_ui_0059db66(cVar1);
      FUN_0043d574(2,DAT_00597028,DAT_00597024,PTR_s_translate_action_heartbeat_005970a0,0xfb,
                   PTR_s_recv_heartbeat__translate_ui_sta_0059709c,cVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar3 = translate_ui_0059db66(cVar1);
      compress_log_output(0x8800000,PTR_s__translate_fsm_recv_heartbeat__t_005970a4,
                          PTR_s__translate_fsm_recv_heartbeat__t_005970a4,cVar1,uVar3);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}


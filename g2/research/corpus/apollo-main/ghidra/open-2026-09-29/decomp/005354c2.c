
void APP_StartServiceDiscovery(byte param_1)

{
  int iVar1;
  ushort *puVar2;
  
  fw_event_loop_remove_delayed(DAT_005355c0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005355d0,DAT_005355cc,DAT_005355c8,0xd9,DAT_005355c4,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_005355d4,DAT_005355d4,param_1);
  }
  iVar1 = FUN_004bb07c(param_1);
  if (iVar1 != 0) {
    FUN_0047b488(iVar1,0);
    FUN_0047b3cc(iVar1,0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005355d0,DAT_005355cc,DAT_005355c8,0xe1,DAT_005355d8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005355dc);
    }
  }
  puVar2 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar2 != (ushort *)0x0) {
    *(undefined1 *)(puVar2 + 1) = 0xa5;
    *puVar2 = (ushort)param_1;
    WsfMsgSend(*DAT_00535598,puVar2);
  }
  return;
}


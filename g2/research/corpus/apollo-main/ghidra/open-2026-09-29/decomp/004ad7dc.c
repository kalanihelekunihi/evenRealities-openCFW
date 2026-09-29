
void CHG_RequestNotifyBatteryInfoFromPeer(void)

{
  char cVar1;
  int iVar2;
  undefined1 local_14;
  undefined1 local_13;
  char local_12;
  undefined1 local_11;
  
  FUN_0043c0e4(&local_14,0xc,0);
  cVar1 = FUN_0045a568();
  local_14 = 4;
  local_13 = 0;
  if (cVar1 == '\x01') {
    local_11 = 2;
  }
  else {
    local_11 = 1;
  }
  local_12 = cVar1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,DAT_004ad9b4,0x18e,DAT_004ad9ac,cVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004ad9b0,DAT_004ad9b0,cVar1);
  }
  FUN_004651e0(0x105,&local_14,0xc,0);
  return;
}


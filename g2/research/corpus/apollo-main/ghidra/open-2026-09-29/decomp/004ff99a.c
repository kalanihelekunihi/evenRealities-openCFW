
void SVC_RingBattery_RequestFromPeer(void)

{
  int iVar1;
  int iVar2;
  undefined1 local_14;
  undefined1 local_13;
  
  FUN_0043c0e4(&local_14,0xc,0);
  local_14 = 6;
  local_13 = 0;
  iVar1 = FUN_004651e0(0x105,&local_14,0xc,0);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ffa50,DAT_004ffa4c,DAT_004ffa60,0x46,DAT_004ffa68);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ffa6c,DAT_004ffa6c);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ffa50,DAT_004ffa4c,DAT_004ffa60,0x44,DAT_004ffa5c,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ffa64,DAT_004ffa64,iVar1);
    }
  }
  return;
}


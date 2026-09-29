
void SVC_RingBattery_Update(byte param_1,char param_2)

{
  int iVar1;
  int iVar2;
  undefined1 local_1c;
  undefined1 local_1b;
  uint local_18;
  undefined1 local_14;
  
  FUN_0043c0e4(&local_1c,0xc,0);
  local_1c = 5;
  local_1b = 8;
  local_18 = (uint)param_1;
  local_14 = param_2 != '\0';
  iVar1 = FUN_00464d1c(0x105,&local_1c,0xc,0);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ffa50,DAT_004ffa4c,DAT_004ffa48,0x24,DAT_004ffa44,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ffa54,DAT_004ffa54,iVar1);
    }
  }
  return;
}



undefined4 FUN_0047432c(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 local_30 [8];
  undefined4 local_10;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  if (*DAT_004744a8 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00474538,DAT_00474534,DAT_00474530,0x191,DAT_0047452c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0047453c,DAT_0047453c);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00474538,DAT_00474534,DAT_00474530,0x194,DAT_00474540);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00474544);
    }
    FUN_0043c0e4(local_30,0x24,0);
    iVar1 = DAT_00474480;
    local_10 = 1;
    local_30[0] = 2;
    iVar3 = osMessageQueuePut(*(undefined4 *)(DAT_00474480 + 0xc),local_30,0,1000);
    if (iVar3 == 0) {
      local_30[0] = 5;
      iVar1 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),local_30,0,1000);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00474538,DAT_00474534,DAT_00474530,0x1a1,DAT_004744e4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004744ec,DAT_004744ec);
        }
        uVar2 = 0xffffffff;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00474538,DAT_00474534,DAT_00474530,0x19b,DAT_00474548);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047454c,DAT_0047454c);
      }
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}


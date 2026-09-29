
undefined4 SmpDbGetPairingDisabledTime(undefined1 param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = smpDbGetRecord(param_1);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,&DAT_00542570,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00542574,&LAB_00542578,3), iVar2 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542a18,param_1,*(undefined4 *)(iVar1 + 0xc),
                     *(undefined2 *)(iVar1 + 8));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00542574,DAT_00542958,DAT_00542a1c,0xe4,DAT_00542a18,param_1,
                         *(undefined4 *)(iVar1 + 0xc),*(undefined2 *)(iVar1 + 8));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00542574,DAT_00542958,DAT_00542a1c,0xe4,DAT_00542a18,param_1,
                       *(undefined4 *)(iVar1 + 0xc),*(undefined2 *)(iVar1 + 8));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00542574,DAT_00542958,DAT_00542a1c,0xe4,DAT_00542a18,param_1,
                     *(undefined4 *)(iVar1 + 0xc),*(undefined2 *)(iVar1 + 8));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00542574,DAT_00542958,DAT_00542a1c,0xe4,DAT_00542a18,param_1,
                   *(undefined4 *)(iVar1 + 0xc),*(undefined2 *)(iVar1 + 8));
    }
  }
  return *(undefined4 *)(iVar1 + 0xc);
}


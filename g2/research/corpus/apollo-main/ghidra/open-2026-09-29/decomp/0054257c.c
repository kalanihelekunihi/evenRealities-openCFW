
undefined1
SmpDbGetFailureCount(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = smpDbGetRecord(param_1);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,&DAT_0054282c,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00542830,&DAT_00542834,3), iVar2 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542a2c,param_1,*(undefined1 *)(iVar1 + 7));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_00542830,DAT_00542958,PTR_s_SmpDbGetFailureCount_00542a30,0x10e,
                         DAT_00542a2c,param_1,*(undefined1 *)(iVar1 + 7));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_00542830,DAT_00542958,PTR_s_SmpDbGetFailureCount_00542a30,0x10e,
                       DAT_00542a2c,param_1,*(undefined1 *)(iVar1 + 7));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_00542830,DAT_00542958,PTR_s_SmpDbGetFailureCount_00542a30,0x10e,
                     DAT_00542a2c,param_1,*(undefined1 *)(iVar1 + 7));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_00542830,DAT_00542958,PTR_s_SmpDbGetFailureCount_00542a30,0x10e,
                   DAT_00542a2c,param_1,*(undefined1 *)(iVar1 + 7),param_4);
    }
  }
  return *(undefined1 *)(iVar1 + 7);
}


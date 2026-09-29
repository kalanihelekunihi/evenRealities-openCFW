
undefined8 SmpDbPairingFailed(undefined1 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = smpDbGetRecord(param_1);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,&DAT_005429fc,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00542a00,&DAT_00542a04,3), iVar2 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542a3c,param_1);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x14d;
            param_3 = DAT_00542a3c;
            FUN_0043d574(4,&DAT_00542a00,DAT_00542958,DAT_00542a40,0x14d,DAT_00542a3c,param_1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0x14d;
          param_3 = DAT_00542a3c;
          FUN_0043d574(3,&DAT_00542a00,DAT_00542958,DAT_00542a40,0x14d,DAT_00542a3c,param_1);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x14d;
        param_3 = DAT_00542a3c;
        FUN_0043d574(2,&DAT_00542a00,DAT_00542958,DAT_00542a40,0x14d,DAT_00542a3c,param_1);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x14d;
      param_3 = DAT_00542a3c;
      FUN_0043d574(1,&DAT_00542a00,DAT_00542958,DAT_00542a40,0x14d,DAT_00542a3c,param_1);
    }
  }
  *(undefined4 *)(iVar1 + 0x10) = *(undefined4 *)(*DAT_00542a28 + 0x10);
  return CONCAT44(param_3,param_2);
}


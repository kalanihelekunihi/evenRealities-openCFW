
undefined4 FUN_00558632(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  
  uVar2 = DAT_005588f8;
  iVar1 = file_opendir(DAT_005588f8);
  if (iVar1 == 0) {
    iVar1 = file_mkdir(uVar2,0);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005588bc,DAT_005588b8,DAT_00558900,0x128,DAT_00558908,uVar2,in_r3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_0055890c,DAT_0055890c,uVar2);
      }
      uVar2 = 0;
    }
    else {
      iVar1 = file_opendir(uVar2);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005588bc,DAT_005588b8,DAT_00558900,0x134,DAT_00558918,uVar2,in_r3);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0055891c,DAT_0055891c,uVar2);
        }
        uVar2 = 0xffffffff;
      }
      else {
        file_closedir();
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005588bc,DAT_005588b8,DAT_00558900,0x130,DAT_00558910,uVar2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00558914,DAT_00558914,uVar2);
        }
        uVar2 = 0;
      }
    }
  }
  else {
    file_closedir();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005588bc,DAT_005588b8,DAT_00558900,0x11f,DAT_005588fc,uVar2,in_r3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00558904,DAT_00558904,uVar2);
    }
    uVar2 = 0;
  }
  return uVar2;
}


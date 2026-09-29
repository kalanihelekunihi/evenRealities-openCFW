
undefined8 FUN_005b23e4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = DAT_005b2d38;
  iVar1 = FUN_005b0c18();
  if ((*(int *)(iVar2 + 0x7c) == 0) || (*(int *)(iVar2 + 0x84) != -1)) {
    if (iVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x4b;
        FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d40,0x4b,DAT_005b2d48);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005b2d4c,DAT_005b2d4c);
      }
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_005897e0();
      if (iVar2 == 0) {
        uVar3 = 1;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_3 = 0x50;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d40,0x50,DAT_005b2d50);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005b3098,DAT_005b3098);
        }
        uVar3 = 0;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x46;
      FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d40,0x46,DAT_005b2d3c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005b2d44,DAT_005b2d44);
    }
    uVar3 = 0;
  }
  return CONCAT44(param_3,uVar3);
}


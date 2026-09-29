
undefined8 FUN_00470d7c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_004710ac;
  iVar2 = FUN_004c0ea8(*DAT_004710ac);
  if (iVar2 == 0) {
    iVar2 = FUN_004c099c(*puVar1,param_1);
    if (iVar2 == 0) {
      iVar2 = FUN_004c0e1e(*puVar1);
      if (iVar2 == 0) {
        FUN_004c32b4(*(undefined4 *)*DAT_0047112c,*(undefined1 *)(param_1 + 8));
        uVar3 = 0;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0x59a;
          FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_0047111c,0x59a,DAT_00471124,param_4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00471128,DAT_00471128);
        }
        uVar3 = 1;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x592;
        FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_0047111c,0x592,DAT_00471124,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00471128,DAT_00471128);
      }
      uVar3 = 1;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x58a;
      FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_0047111c,0x58a,DAT_00471118,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00471120,DAT_00471120);
    }
    uVar3 = 1;
  }
  return CONCAT44(param_2,uVar3);
}


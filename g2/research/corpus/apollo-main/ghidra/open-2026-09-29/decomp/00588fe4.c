
undefined8 FUN_00588fe4(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  if (((param_1 & 0xff) < 3) && ((param_1 & 0xff) != 0)) {
    if (*(int *)(DAT_005893b0 + (param_1 & 0xff) * 8 + 4) == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0xb4;
        param_2 = DAT_005893c0;
        FUN_0043d574(1,DAT_00589364,DAT_00589360,DAT_005893bc,0xb4,DAT_005893c0,param_1 & 0xff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005893c4,DAT_005893c4,param_1 & 0xff);
      }
    }
    else {
      (**(code **)(DAT_005893b0 + (param_1 & 0xff) * 8 + 4))();
      uVar2 = param_1;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar2 = 0xad;
      param_2 = DAT_005893a4;
      FUN_0043d574(1,DAT_00589364,DAT_00589360,DAT_005893bc,0xad,DAT_005893a4,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005893ac,DAT_005893ac,param_1 & 0xff,uVar2,param_2,param_3);
    }
  }
  return CONCAT44(param_2,uVar2);
}


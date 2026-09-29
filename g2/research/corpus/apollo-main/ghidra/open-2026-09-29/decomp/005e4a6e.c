
undefined8 FUN_005e4a6e(uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  
  if (param_1 == 0) goto LAB_005e4b60;
  uVar2 = param_1 >> 2 & 1;
  uVar3 = param_1 >> 3 & 1;
  uVar4 = param_2;
  if (uVar2 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0xe7;
      param_3 = DAT_005e5570;
      param_4 = param_1;
      FUN_0043d574(4,DAT_005e5480,DAT_005e547c,DAT_005e5574,0xe7,DAT_005e5570,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1f < 0) {
LAB_005e4ad6:
      compress_log_output(0x10400000,DAT_005e5578,DAT_005e5578,param_1);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1d < 0) goto LAB_005e4ad6;
    }
    FUN_005e4920();
  }
  if (uVar3 != 0) {
    FUN_005e49b0(param_1 & 1,1,param_2);
  }
  if ((param_1 & 1) == 1 && (uVar2 == 0 && uVar3 == 0)) {
    FUN_005e49b0(1,0,param_2);
  }
  param_2 = uVar4;
  if ((param_1 >> 1 & 1) != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0xf4;
      param_3 = DAT_005e557c;
      FUN_0043d574(4,DAT_005e5480,DAT_005e547c,DAT_005e5574,0xf4,DAT_005e557c,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005e5768,DAT_005e5768);
    }
  }
LAB_005e4b60:
  return CONCAT44(param_3,param_2);
}


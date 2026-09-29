
undefined8 FUN_004fb1fa(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = param_1;
  if (param_1 < 2) {
    for (uVar3 = 0; iVar1 = DAT_004fb718, (int)uVar3 < 2; uVar3 = uVar3 + 1) {
      if (*(int *)(DAT_004fb718 + uVar3 * 4) != 0) {
        if (uVar3 == param_1) {
          uVar2 = FUN_0044104c(0xffffff);
          FUN_0044127e(*(undefined4 *)(iVar1 + uVar3 * 4),uVar2,0);
        }
        else {
          uVar2 = FUN_0044104c(DAT_004fb714);
          FUN_0044127e(*(undefined4 *)(iVar1 + uVar3 * 4),uVar2,0);
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0xa3;
      param_2 = DAT_004fb700;
      param_3 = param_1;
      FUN_0043d574(2,DAT_004fb70c,DAT_004fb708,DAT_004fb704,0xa3,DAT_004fb700,param_1,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004fb710,DAT_004fb710,param_1,uVar4,param_2,param_3);
    }
  }
  return CONCAT44(param_2,uVar4);
}


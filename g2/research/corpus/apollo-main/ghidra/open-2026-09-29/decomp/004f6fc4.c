
undefined4 *
FUN_004f6fc4(uint param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4,
            undefined4 *param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 != (undefined4 *)0x0) {
    *param_2 = 0;
  }
  if (param_3 != (undefined4 *)0x0) {
    *param_3 = 0;
  }
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = 0x240;
  }
  if (param_5 != (undefined4 *)0x0) {
    *param_5 = 0x120;
  }
  iVar2 = DAT_004f7c88;
  piVar1 = DAT_004f7ae0;
  if ((int)param_1 < 0) {
    if (*DAT_004f7ae0 != 0) {
      if (param_2 != (undefined4 *)0x0) {
        uVar3 = FUN_0043fc70(*DAT_004f7ae0);
        *param_2 = uVar3;
      }
      if (param_3 != (undefined4 *)0x0) {
        uVar3 = FUN_0043fce0(*piVar1);
        *param_3 = uVar3;
      }
      if (param_4 != (undefined4 *)0x0) {
        uVar3 = FUN_0043fd9e(*piVar1);
        *param_4 = uVar3;
      }
      if (param_5 != (undefined4 *)0x0) {
        uVar3 = FUN_0043fdda(*piVar1);
        *param_5 = uVar3;
      }
    }
  }
  else if ((param_1 < 0x28) && (*(int *)(DAT_004f7c88 + param_1 * 0x10) != 0)) {
    if (param_2 != (undefined4 *)0x0) {
      uVar3 = FUN_0043fc70(*(undefined4 *)(DAT_004f7c88 + param_1 * 0x10));
      *param_2 = uVar3;
    }
    if (param_3 != (undefined4 *)0x0) {
      uVar3 = FUN_0043fce0(*(undefined4 *)(iVar2 + param_1 * 0x10));
      *param_3 = uVar3;
    }
    if (param_4 != (undefined4 *)0x0) {
      uVar3 = FUN_0043fd9e(*(undefined4 *)(iVar2 + param_1 * 0x10));
      *param_4 = uVar3;
    }
    if (param_5 != (undefined4 *)0x0) {
      uVar3 = FUN_0043fdda(*(undefined4 *)(iVar2 + param_1 * 0x10));
      *param_5 = uVar3;
    }
  }
  return param_4;
}


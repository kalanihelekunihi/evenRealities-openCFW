
undefined4 FUN_005694e0(undefined4 *param_1,undefined4 *param_2,undefined1 param_3)

{
  undefined4 uVar1;
  undefined1 uVar2;
  
  if ((param_1 == (undefined4 *)0x0) || (param_2 == (undefined4 *)0x0)) {
    uVar1 = 6;
  }
  else {
    *(undefined1 *)(param_1 + 5) = 1;
    uVar1 = param_2[1];
    param_1[2] = *param_2;
    param_1[3] = uVar1;
    *(undefined1 *)((int)param_1 + 0x15) = param_3;
    if ((*(char *)((int)param_1 + 0x2a) == '\0') &&
       ((*(char *)((int)param_1 + 0x15) == '\0' || (*(char *)((int)param_1 + 0x29) != '\0')))) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
    *(undefined1 *)(param_1 + 10) = uVar2;
    uVar1 = param_2[1];
    param_1[7] = *param_2;
    param_1[8] = uVar1;
    *param_1 = 0;
    uVar1 = 0;
  }
  return uVar1;
}


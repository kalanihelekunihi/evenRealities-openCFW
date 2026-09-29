
undefined4 FUN_00464008(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 == (int *)0x0) {
    return param_4;
  }
  if (param_1[1] == 0) {
    return param_4;
  }
  bVar1 = *(byte *)((int)param_1 + 0x19);
  if (bVar1 == 0) {
    uVar3 = param_1[3] + 1;
    if ((uint)param_1[2] <= uVar3) {
      uVar3 = 0;
    }
  }
  else if (bVar1 == 2) {
    if (*(char *)((int)param_1 + 0x1a) == '\0') {
      if (param_1[3] == 0) {
        *(undefined1 *)((int)param_1 + 0x1a) = 1;
        uVar3 = param_1[3] + 1;
      }
      else {
        uVar3 = param_1[3] - 1;
      }
    }
    else if ((uint)param_1[3] < param_1[2] - 1U) {
      uVar3 = param_1[3] + 1;
    }
    else {
      *(undefined1 *)((int)param_1 + 0x1a) = 0;
      uVar3 = param_1[3] - 1;
    }
  }
  else {
    if (1 < bVar1) {
      *(undefined1 *)((int)param_1 + 0x1b) = 1;
      *(undefined1 *)(param_1 + 6) = 0;
      return param_4;
    }
    if (param_1[2] - 1U <= (uint)param_1[3]) {
      *(undefined1 *)((int)param_1 + 0x1b) = 1;
      *(undefined1 *)(param_1 + 6) = 0;
      return param_4;
    }
    uVar3 = param_1[3] + 1;
  }
  if ((uint)param_1[2] <= uVar3) {
    uVar3 = 0;
  }
  param_1[3] = uVar3;
  if (((*param_1 != 0) && (iVar2 = FUN_0043e2ea(*param_1), iVar2 != 0)) &&
     (*(int *)(param_1[1] + uVar3 * 4) != 0)) {
    FUN_00498680(*param_1,*(undefined4 *)(param_1[1] + uVar3 * 4));
  }
  return param_4;
}



void FUN_005e1a3c(int param_1,int *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  uint uVar6;
  int local_120 [5];
  int local_10c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  piVar5 = local_120;
  local_120[0] = *param_3 * 4;
  local_120[1] = param_3[1] * 4;
  iVar1 = *param_2;
  local_120[2] = iVar1 * 4;
  iVar2 = param_2[1];
  local_120[3] = iVar2 * 4;
  local_120[4] = *(int *)(param_1 + 0xb4);
  local_10c = *(int *)(param_1 + 0xb8);
  iVar3 = iVar2 * 4 >> 8;
  if ((((local_120[1] >> 8 < *(int *)(param_1 + 0x94)) || (iVar3 < *(int *)(param_1 + 0x94))) ||
      (local_10c >> 8 < *(int *)(param_1 + 0x94))) &&
     (((*(int *)(param_1 + 0x90) <= local_120[1] >> 8 || (*(int *)(param_1 + 0x90) <= iVar3)) ||
      (*(int *)(param_1 + 0x90) <= local_10c >> 8)))) {
    if (local_120[0] + local_120[4] + iVar1 * -8 < 0) {
      iVar1 = (iVar1 * 8 - local_120[4]) + *param_3 * -4;
    }
    else {
      iVar1 = local_120[0] + local_120[4] + iVar1 * -8;
    }
    if (local_120[1] + local_10c + iVar2 * -8 < 0) {
      iVar2 = (iVar2 * 8 - local_10c) + param_3[1] * -4;
    }
    else {
      iVar2 = local_120[1] + local_10c + iVar2 * -8;
    }
    if (iVar1 < iVar2) {
      iVar1 = iVar2;
    }
    uVar4 = 1;
    for (; 0x40 < iVar1; iVar1 = iVar1 >> 2) {
      uVar4 = uVar4 << 1;
    }
    do {
      for (uVar6 = 1; (uVar4 & uVar6) == 0; uVar6 = uVar6 << 1) {
        FUN_005e19ea(piVar5);
        piVar5 = piVar5 + 4;
      }
      FUN_005e17c2(param_1,*piVar5,piVar5[1]);
      piVar5 = piVar5 + -4;
      uVar4 = uVar4 - 1;
    } while (uVar4 != 0);
  }
  else {
    *(int *)(param_1 + 0xb4) = local_120[0];
    *(int *)(param_1 + 0xb8) = local_120[1];
  }
  return;
}


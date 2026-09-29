
undefined4 FUN_0044b7ce(int *param_1,char param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = FUN_0044b7c0(param_1);
  if (iVar1 == 0) {
    for (uVar2 = 0; uVar2 < *(byte *)(param_1 + 2); uVar2 = uVar2 + 1) {
      if (*(char *)(*param_1 + (uint)*(byte *)(param_1 + 2) * 4 + uVar2) == param_2) {
        *param_3 = *(undefined4 *)(*param_1 + uVar2 * 4);
        return 1;
      }
    }
  }
  else {
    iVar1 = *param_1;
    for (iVar3 = 0; *(char *)(iVar1 + iVar3 * 8) != '\0'; iVar3 = iVar3 + 1) {
      if (*(char *)(iVar1 + iVar3 * 8) == param_2) {
        *param_3 = *(undefined4 *)(iVar1 + iVar3 * 8 + 4);
        return 1;
      }
    }
  }
  return 0;
}


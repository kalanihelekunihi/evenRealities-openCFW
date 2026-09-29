
void FUN_100099d4(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  piVar1 = DAT_10009a40;
  iVar2 = *DAT_10009a40;
  iVar3 = *(int *)(param_1 + 4) + iVar2;
  if (((param_1 != iVar3) && (*(short *)(iVar3 + 2) == 0)) && (iVar3 != DAT_10009a40[1])) {
    if (iVar3 == DAT_10009a40[2]) {
      DAT_10009a40[2] = param_1;
    }
    *(undefined4 *)(param_1 + 4) = *(undefined4 *)(iVar3 + 4);
    *(int *)(*(int *)(iVar3 + 4) + iVar2 + 8) = param_1 - iVar2;
  }
  iVar4 = *(int *)(param_1 + 8);
  iVar3 = iVar2 + iVar4;
  if ((param_1 != iVar3) && (*(short *)(iVar3 + 2) == 0)) {
    if (param_1 == piVar1[2]) {
      piVar1[2] = iVar3;
    }
    *(undefined4 *)(iVar3 + 4) = *(undefined4 *)(param_1 + 4);
    *(int *)(iVar2 + *(int *)(param_1 + 4) + 8) = iVar4;
  }
  return;
}



undefined4 FUN_005c28ae(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x3c) != 0) {
    iVar2 = *(int *)(param_1 + 0x2c);
    iVar3 = 0;
    while (((*(int *)(iVar2 + iVar3 * 4) != 0 &&
            (iVar1 = FUN_004547be(*(undefined4 *)(iVar2 + iVar3 * 4),&LAB_005c2ab0), iVar1 != 0)) &&
           (**(char **)(iVar2 + iVar3 * 4) != '\0'))) {
      iVar1 = FUN_005c2608(*(undefined2 *)(*(int *)(param_1 + 0x34) + iVar3 * 2));
      if (iVar1 != 0) {
        return 1;
      }
      iVar3 = iVar3 + 1;
    }
  }
  return 0;
}


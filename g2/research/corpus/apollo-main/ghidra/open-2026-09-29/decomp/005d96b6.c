
void FUN_005d96b6(undefined4 param_1,undefined4 param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  while( true ) {
    if (9 < uVar2) {
      return;
    }
    iVar1 = FUN_0046cacc(DAT_005d9930 + *(int *)(DAT_005d9934 + uVar2 * 4),param_1);
    if (iVar1 == 0) break;
    uVar2 = uVar2 + 1;
  }
  if (*(int *)(param_4 + uVar2 * 4) != 0) {
    return;
  }
  *(undefined4 *)(param_4 + uVar2 * 4) = 1;
  *(undefined4 *)(param_3 + uVar2 * 4) = param_2;
  return;
}


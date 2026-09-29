
bool FUN_005e4f1a(int param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 4) == 0)) {
    bVar1 = true;
  }
  else {
    iVar2 = FUN_0044e498(*(undefined4 *)(param_1 + 4));
    iVar3 = FUN_0044e4bc(*(undefined4 *)(param_1 + 4));
    if (iVar3 + iVar2 < 1) {
      bVar1 = true;
    }
    else {
      bVar1 = iVar3 + iVar2 <= param_2;
    }
  }
  return bVar1;
}


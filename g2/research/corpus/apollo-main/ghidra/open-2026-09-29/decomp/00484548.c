
void FUN_00484548(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  
  bVar4 = false;
  for (iVar1 = FUN_0044fa22(0); iVar1 != 0; iVar1 = FUN_0044fa22(iVar1)) {
    for (iVar3 = *(int *)(iVar1 + 0x2ac); iVar3 != 0; iVar3 = *(int *)(iVar3 + 0x4c)) {
      iVar2 = FUN_0048458e(iVar1,iVar3);
      if (iVar2 != 0) {
        bVar4 = true;
      }
    }
    if (!bVar4) {
      FUN_00484528();
      FUN_0048462e();
    }
  }
  return;
}


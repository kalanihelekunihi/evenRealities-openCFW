
void FUN_0058930a(undefined1 param_1,undefined1 param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    for (uVar2 = 0; uVar2 < 5; uVar2 = uVar2 + 1) {
      iVar3 = DAT_005893ec + uVar2 * 4;
      iVar1 = FUN_005890f6(iVar3,param_1,param_2);
      if (iVar1 != 0) {
        FUN_005890ea(iVar3);
      }
    }
  }
  return;
}


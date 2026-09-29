
int FUN_100060b0(undefined4 param_1)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  
  piVar1 = DAT_100060e0;
  if (0 < *DAT_100060e0) {
    iVar4 = 0;
    puVar3 = DAT_100060e4;
    do {
      iVar2 = FUN_100070ac(*puVar3,param_1);
      if (iVar2 != 0) {
        return iVar2;
      }
      iVar4 = iVar4 + 1;
      puVar3 = puVar3 + 3;
    } while (iVar4 < *piVar1);
  }
  return 0;
}


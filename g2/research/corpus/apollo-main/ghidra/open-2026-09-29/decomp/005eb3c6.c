
undefined4 FUN_005eb3c6(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  
  if ((param_1 != 0) && (*(int *)(param_1 + 0x21c) != 0)) {
    bVar1 = FUN_005eb30c();
    for (bVar4 = 0; bVar4 < bVar1; bVar4 = bVar4 + 1) {
      iVar3 = FUN_0044dce2(*(undefined4 *)(param_1 + 0x21c),bVar4);
      if (iVar3 != 0) {
        uVar2 = DAT_005ebc30;
        if ((*(char *)(param_1 + 0x27c) == '\0') && (bVar4 == *(byte *)(param_1 + 0x279))) {
          uVar2 = 0xffffff;
        }
        uVar2 = FUN_0044104c(uVar2);
        FUN_0044140e(iVar3,uVar2,0);
      }
    }
    FUN_005eb322(param_1);
  }
  return param_4;
}


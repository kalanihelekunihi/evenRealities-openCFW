
undefined4 FUN_005eb322(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if (((param_1 != 0) && (*(int *)(param_1 + 0x220) != 0)) && (*(int *)(param_1 + 0x21c) != 0)) {
    if (*(char *)(param_1 + 0x27c) == '\0') {
      bVar1 = FUN_005eb30c();
      if (*(byte *)(param_1 + 0x279) < bVar1) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(param_1 + 0x21c),*(undefined1 *)(param_1 + 0x279));
        if (iVar2 == 0) {
          FUN_0043ded4(*(undefined4 *)(param_1 + 0x220),1);
        }
        else {
          iVar3 = FUN_0043fce0(*(undefined4 *)(param_1 + 0x21c));
          iVar2 = FUN_0043fce0(iVar2);
          iVar4 = FUN_005eb2ee();
          iVar5 = FUN_0043fc70(*(undefined4 *)(param_1 + 0x21c));
          FUN_0043f09a(*(undefined4 *)(param_1 + 0x220),iVar5 + -0x14,iVar4 + iVar2 + iVar3);
          FUN_0043dfa4(*(undefined4 *)(param_1 + 0x220),1);
        }
      }
      else {
        FUN_0043ded4(*(undefined4 *)(param_1 + 0x220),1);
      }
    }
    else {
      FUN_0043ded4(*(undefined4 *)(param_1 + 0x220),1);
    }
  }
  return param_4;
}


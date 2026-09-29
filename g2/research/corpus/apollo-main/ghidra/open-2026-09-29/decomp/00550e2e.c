
void FUN_00550e2e(int param_1,char param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = service_ancc_message_count_get();
  if (0 < iVar1) {
    if (param_1 < 0) {
      param_1 = 0;
    }
    if (iVar1 <= param_1) {
      param_1 = iVar1 + -1;
    }
    for (iVar4 = 0; (iVar4 < iVar1 && (iVar4 < 10)); iVar4 = iVar4 + 1) {
      iVar3 = *(int *)(DAT_00550ff4 + iVar4 * 4 + 0x10);
      if (iVar3 != 0) {
        if (iVar4 == param_1) {
          uVar2 = FUN_0044104c(0xffffff);
          FUN_0044127e(iVar3,uVar2,0);
        }
        else {
          uVar2 = FUN_0044104c(DAT_00551810);
          FUN_0044127e(iVar3,uVar2,0);
        }
      }
    }
    if (param_2 == '\0') {
      FUN_00550eda(param_1,0,0);
    }
    else {
      FUN_00550eda(param_1,200,0);
    }
  }
  return;
}


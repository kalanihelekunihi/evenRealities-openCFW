
undefined4
ui_onboarding_main_sub_004A859E(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  for (iVar3 = 0; iVar1 = DAT_004a9110, iVar3 < *DAT_004a8e60; iVar3 = iVar3 + 1) {
    if (*(int *)(DAT_004a9110 + iVar3 * 4) != 0) {
      if (iVar3 == param_1) {
        uVar2 = FUN_0044104c(0xffffff);
        FUN_0044127e(*(undefined4 *)(iVar1 + iVar3 * 4),uVar2,0);
      }
      else if (param_2 == '\0') {
        uVar2 = FUN_0044104c(DAT_004a8e5c);
        FUN_0044127e(*(undefined4 *)(iVar1 + iVar3 * 4),uVar2,0);
      }
      else {
        uVar2 = FUN_0044104c(DAT_004a8e58);
        FUN_0044127e(*(undefined4 *)(iVar1 + iVar3 * 4),uVar2,0);
      }
    }
  }
  return param_4;
}


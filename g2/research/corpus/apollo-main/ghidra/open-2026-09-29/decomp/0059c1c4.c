
void FUN_0059c1c4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_0059ba96(param_2,param_3);
  if ((int)param_4[1] >> 1 < 2) {
    iVar2 = 0;
  }
  else {
    iVar2 = ((int)param_4[1] >> 1) + -1;
  }
  FUN_0059b6ac(param_1,iVar2,uVar1);
  FUN_0059b6ac(param_1,*(undefined1 *)(param_4 + 2),1);
  FUN_0059b6ac(param_1,*param_4,8);
  return;
}


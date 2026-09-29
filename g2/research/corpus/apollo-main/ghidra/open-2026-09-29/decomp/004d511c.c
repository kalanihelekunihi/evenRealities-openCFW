
void FUN_004d511c(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = (**(code **)(*param_1 + 0xc))(param_1,param_2,param_3);
  if (iVar1 != 0) {
    iVar2 = FUN_004d5312(iVar1);
    if (iVar2 == 0) {
      (**(code **)(*param_1 + 0x14))(param_1,iVar1,param_3);
      uVar3 = FUN_004d5396(iVar1);
      (*(code *)param_1[6])(uVar3,param_3);
      FUN_004d54da(iVar1);
    }
    else {
      FUN_004d533e(iVar1,1);
      (**(code **)(*param_1 + 0x14))(param_1,iVar1,param_3);
    }
  }
  return;
}


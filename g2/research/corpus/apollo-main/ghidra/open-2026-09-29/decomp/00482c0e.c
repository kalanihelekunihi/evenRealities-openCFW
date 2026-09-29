
void FUN_00482c0e(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (param_1 != 0) {
    iVar1 = FUN_00482cd8(param_1);
    if (iVar1 == param_2) {
      uVar2 = FUN_00482cf0(param_1,param_2);
      *(undefined4 *)(param_1 + 4) = uVar2;
      if (*(int *)(param_1 + 4) == 0) {
        *(undefined4 *)(param_1 + 8) = 0;
      }
      else {
        FUN_00482dae(param_1,*(undefined4 *)(param_1 + 4),0);
      }
    }
    else {
      iVar1 = FUN_00482ce4(param_1);
      if (iVar1 == param_2) {
        uVar2 = FUN_00482cfa(param_1,param_2);
        *(undefined4 *)(param_1 + 8) = uVar2;
        if (*(int *)(param_1 + 8) == 0) {
          *(undefined4 *)(param_1 + 4) = 0;
        }
        else {
          FUN_00482dc2(param_1,*(undefined4 *)(param_1 + 8),0);
        }
      }
      else {
        uVar2 = FUN_00482cfa(param_1,param_2);
        uVar3 = FUN_00482cf0(param_1,param_2);
        FUN_00482dc2(param_1,uVar2,uVar3);
        FUN_00482dae(param_1,uVar3,uVar2);
      }
    }
  }
  return;
}


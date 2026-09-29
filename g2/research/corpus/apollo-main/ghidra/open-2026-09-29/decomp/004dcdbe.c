
void FUN_004dcdbe(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    for (iVar3 = 0; iVar3 < param_1[0x16]; iVar3 = iVar3 + 1) {
      if (param_1[iVar3 + 2] != 0) {
        iVar1 = FUN_0044dce2(param_1[iVar3 + 2],0);
        if (iVar3 == param_1[0x17]) {
          FUN_0044129e(param_1[iVar3 + 2],0x32,0);
          uVar2 = FUN_0044104c(0);
          FUN_0044127e(param_1[iVar3 + 2],uVar2,0);
          if (*(char *)((int)param_1 + 0x6d) == '\0') {
            FUN_0044131c(param_1[iVar3 + 2],0,0);
          }
          else {
            FUN_0044131c(param_1[iVar3 + 2],1,0);
            uVar2 = FUN_0044104c(0xffffff);
            FUN_004412ec(param_1[iVar3 + 2],uVar2,0);
          }
          if (iVar1 != 0) {
            uVar2 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar1,uVar2,0);
          }
        }
        else {
          FUN_0044129e(param_1[iVar3 + 2],0,0);
          FUN_0044131c(param_1[iVar3 + 2],0,0);
          if (iVar1 != 0) {
            uVar2 = FUN_0044104c(DAT_004dd47c);
            FUN_0044140e(iVar1,uVar2,0);
          }
        }
        FUN_00441488(param_1[iVar3 + 2],0xff,0);
      }
    }
  }
  return;
}



void FUN_0056847a(int *param_1,undefined4 *param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar1 = FUN_005682de(param_1,2,param_3,param_4,param_4);
  if (iVar1 == 0) {
    puVar2 = (undefined4 *)(param_1[2] + *param_1 * 8);
    iVar1 = param_1[3];
    iVar3 = *param_1;
    uVar4 = param_2[1];
    *puVar2 = *param_2;
    puVar2[1] = uVar4;
    uVar4 = param_3[1];
    puVar2[2] = *param_3;
    puVar2[3] = uVar4;
    *(undefined1 *)(iVar1 + iVar3) = 0;
    ((undefined1 *)(iVar1 + iVar3))[1] = 1;
    *param_1 = *param_1 + 2;
  }
  *(undefined1 *)(param_1 + 4) = 0;
  return;
}


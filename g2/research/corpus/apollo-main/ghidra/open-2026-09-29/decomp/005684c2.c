
void FUN_005684c2(int *param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  
  iVar1 = FUN_005682de(param_1,3,param_3,param_4,param_4);
  if (iVar1 == 0) {
    puVar2 = (undefined4 *)(param_1[2] + *param_1 * 8);
    puVar4 = (undefined1 *)(param_1[3] + *param_1);
    uVar3 = param_2[1];
    *puVar2 = *param_2;
    puVar2[1] = uVar3;
    uVar3 = param_3[1];
    puVar2[2] = *param_3;
    puVar2[3] = uVar3;
    uVar3 = param_4[1];
    puVar2[4] = *param_4;
    puVar2[5] = uVar3;
    *puVar4 = 2;
    puVar4[1] = 2;
    puVar4[2] = 1;
    *param_1 = *param_1 + 3;
  }
  *(undefined1 *)(param_1 + 4) = 0;
  return;
}


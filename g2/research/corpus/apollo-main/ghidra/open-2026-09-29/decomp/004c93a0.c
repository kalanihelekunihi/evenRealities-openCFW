
undefined8 FUN_004c93a0(undefined4 param_1,int param_2,int param_3,int *param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *local_20;
  
  iVar4 = *(int *)(param_2 + 0x48);
  iVar3 = *(int *)(param_2 + 0x2c);
  if (param_4[1] == DAT_004c94a0) {
    FUN_00439c04(param_4,param_3,0x10);
    param_4[3] = param_4[1];
    uVar1 = FUN_00451598(param_3);
    iVar2 = FUN_0048b196(iVar3,*(uint *)(param_2 + 0x20) >> 8 & 0xff,uVar1,1);
    if (iVar2 == 0) {
      if (iVar3 != 0) {
        FUN_0048b216(iVar3);
        *(undefined4 *)(param_2 + 0x2c) = 0;
      }
      local_20 = (int *)0x0;
      iVar2 = FUN_0048b010(DAT_004c94a4,uVar1,1,*(uint *)(param_2 + 0x20) >> 8 & 0xff);
      if (iVar2 == 0) {
        uVar1 = 0;
        goto LAB_004c9478;
      }
    }
    local_20 = (int *)0x0;
    *(int *)(param_2 + 0x2c) = iVar2;
    iVar3 = iVar2;
  }
  else {
    param_4[1] = param_4[1] + 1;
    param_4[3] = param_4[3] + 1;
    local_20 = param_4;
  }
  if (*(int *)(param_3 + 0xc) < param_4[1]) {
    uVar1 = 0;
  }
  else {
    FUN_004c6fba(iVar4,(*(uint *)(iVar4 + 0x18) >> 3) * *param_4 +
                       ((*(int *)(iVar4 + 0x14) + -1) - param_4[1]) * *(int *)(iVar4 + 0x1c) +
                       *(int *)(iVar4 + 0xc),0);
    iVar2 = FUN_00451598(param_3);
    FUN_004c6f46(iVar4,*(undefined4 *)(iVar3 + 0x10),(*(uint *)(iVar4 + 0x18) >> 3) * iVar2,0);
    uVar1 = 1;
  }
LAB_004c9478:
  return CONCAT44(local_20,uVar1);
}


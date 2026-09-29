
undefined4 * FUN_1000e784(undefined4 param_1,undefined4 param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  FUN_100113c4(param_3,0,0x28);
  param_3[2] = 0;
  param_3[3] = 0;
  param_3[4] = 0;
  param_3[5] = 0;
  *param_3 = param_1;
  param_3[1] = param_2;
  uVar1 = FUN_1000ea74(param_3 + 10);
  param_3[6] = uVar1;
  iVar2 = FUN_1000ea68(uVar1,2);
  iVar2 = (int)(param_3 + 10) + iVar2;
  uVar1 = FUN_1000eb54(iVar2);
  param_3[7] = uVar1;
  iVar3 = FUN_1000eb48(uVar1,2);
  iVar2 = iVar2 + iVar3;
  uVar1 = FUN_1000ec38(iVar2);
  param_3[8] = uVar1;
  iVar3 = FUN_1000ec2c(uVar1,2);
  uVar1 = FUN_1000ed7c(iVar3 + iVar2);
  param_3[9] = uVar1;
  FUN_1000ed2c();
  return param_3;
}


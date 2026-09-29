
void FUN_00567d06(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = *param_1;
  *(undefined4 *)(param_2 + 0x14) = param_1[5];
  *(undefined4 *)(param_2 + 0x18) = param_1[6];
  FUN_0058ed2e(uVar1,param_1 + 7,param_2 + 0x1c);
  return;
}


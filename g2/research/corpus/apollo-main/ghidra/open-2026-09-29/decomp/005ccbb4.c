
void FUN_005ccbb4(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  
  *(undefined4 *)(param_2 + 0x2c) = 1;
  *(undefined4 *)(param_2 + 0x30) = 1;
  uVar1 = FUN_0044f718(*(int *)(param_2 + 0x2c) << 2);
  *(undefined4 *)(param_2 + 0x3c) = uVar1;
  uVar1 = FUN_0044f718(*(int *)(param_2 + 0x30) << 2);
  *(undefined4 *)(param_2 + 0x38) = uVar1;
  **(undefined4 **)(param_2 + 0x3c) = 0x82;
  **(undefined4 **)(param_2 + 0x38) = 0x82;
  uVar1 = FUN_0044f76a(*(undefined4 *)(param_2 + 0x34),
                       *(int *)(param_2 + 0x2c) * *(int *)(param_2 + 0x30) * 4);
  *(undefined4 *)(param_2 + 0x34) = uVar1;
  **(undefined4 **)(param_2 + 0x34) = 0;
  *(undefined4 *)(param_2 + 0x44) = 0xffff;
  *(undefined4 *)(param_2 + 0x40) = 0xffff;
  return;
}


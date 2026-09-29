
undefined8 FUN_00529cf8(undefined4 *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  FUN_004d4666(*(int *)(param_2 + 0x34) + 0x10);
  uVar1 = *(byte *)(param_2 + 0x2c) >> 1 & 1;
  iVar2 = FUN_00529f8e(*(undefined4 *)(param_2 + 0x30),
                       *(undefined4 *)(*(int *)(param_2 + 0x34) + 0xc),*param_1,
                       *(undefined4 *)(*(int *)(param_2 + 0x34) + 8),uVar1,
                       *(undefined4 *)(param_2 + 0x40));
  FUN_004d4696(*(int *)(param_2 + 0x34) + 0x10);
  if (iVar2 != 0) {
    param_1[1] = iVar2;
  }
  return CONCAT44(uVar1,(uint)(iVar2 != 0));
}


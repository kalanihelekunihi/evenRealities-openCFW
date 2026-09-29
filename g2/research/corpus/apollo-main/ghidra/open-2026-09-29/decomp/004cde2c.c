
undefined8 FUN_004cde2c(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  *(undefined4 *)(param_2 + 0x3c) = *(undefined4 *)(param_2 + 0x34);
  lfs_alloc_ckpoint(param_1);
  iVar1 = FUN_004cdd0e(param_1,param_2);
  if (iVar1 == 0) {
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) & 0xffefffff;
    iVar1 = 0;
  }
  return CONCAT44(param_4,iVar1);
}


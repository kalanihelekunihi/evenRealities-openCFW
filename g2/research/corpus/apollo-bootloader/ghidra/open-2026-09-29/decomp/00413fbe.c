
undefined8 FUN_00413fbe(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(param_2 + 0x30) << 0xe < 0) {
    uVar1 = lfs_max(*(undefined4 *)(param_2 + 0x34),*(undefined4 *)(param_2 + 0x2c));
  }
  else {
    uVar1 = *(undefined4 *)(param_2 + 0x2c);
  }
  return CONCAT44(unaff_r7,uVar1);
}



undefined4 lfs_alloc_drop(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_1 + 0x58) = 0;
  *(undefined4 *)(param_1 + 0x5c) = 0;
  lfs_alloc_ckpoint();
  return unaff_r7;
}


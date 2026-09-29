
undefined8 lfs_ctz(uint param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = lfs_npw2((param_1 & -param_1) + 1);
  return CONCAT44(unaff_r7,iVar1 + -1);
}


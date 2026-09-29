
undefined8
FUN_00410c64(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = lfs_tag_type1(*param_1);
  if ((iVar2 == 0) || (iVar2 = FUN_00410af2(param_1 + 1,param_2), iVar2 != 0)) {
    bVar1 = 0;
  }
  else {
    bVar1 = 1;
  }
  return CONCAT44(param_4,(uint)bVar1);
}


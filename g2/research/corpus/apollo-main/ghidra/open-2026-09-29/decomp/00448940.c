
ulonglong FUN_00448940(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = *param_2;
  uStack_c = param_4;
  uVar1 = FUN_004488fc(param_1,&local_10);
  if ((uVar1 & 0xff) == 0) {
    *param_2 = local_10;
  }
  return CONCAT44(local_10,uVar1) & 0xffffffff000000ff;
}


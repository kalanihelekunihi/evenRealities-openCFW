
ulonglong FUN_0054447a(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  uint local_c;
  
  uVar1 = DAT_00544f68;
  local_c = param_4 & 0xffffff00;
  FUN_005443b0(param_1,param_3,param_2,&local_c);
  return CONCAT44(uVar1,local_c) & 0xffffffff000000ff;
}


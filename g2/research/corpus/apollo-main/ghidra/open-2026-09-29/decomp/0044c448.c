
ulonglong FUN_0044c448(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_0044b8ac(param_1,param_2);
  local_18 = CONCAT31(local_18._1_3_,uVar1);
  uVar1 = FUN_0044b8f6(param_1,param_2);
  local_18._0_2_ = CONCAT11(uVar1,(undefined1)local_18);
  FUN_0044b7b4(&local_18,(int)&local_18 + 1,param_3);
  return CONCAT44(local_18,local_18) & 0xffffffff000000ff;
}


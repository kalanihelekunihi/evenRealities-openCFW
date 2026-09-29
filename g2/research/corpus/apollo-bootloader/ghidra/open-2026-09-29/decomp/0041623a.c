
undefined4 bl_runtime_transfer(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  int local_14;
  undefined4 uStack_10;
  
  if ((param_1 == 0) || (param_2 < 0)) {
    local_18 = 0xfffffffc;
  }
  else {
    local_18 = 0xffffffff;
    uStack_10 = param_4;
    iVar1 = FUN_0041602a();
    if (iVar1 == 0) {
      FUN_00418e70(param_1,0,param_2,1,0);
      FUN_00418e70(param_1,0,0,0,&local_18);
    }
    else {
      local_14 = 0;
      FUN_00418fe8(param_1,0,param_2,1,0,&local_14);
      FUN_00418fe8(param_1,0,0,0,&local_18,0);
      if (local_14 != 0) {
        *DAT_0041699c = 0x10000000;
      }
    }
  }
  return local_18;
}


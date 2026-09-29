
undefined8 bl_runtime_submit(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  
  iVar1 = FUN_0041602a();
  local_10 = param_4;
  if (iVar1 == 0) {
    if ((param_1 == 0) || (param_2 == 0)) {
      uVar2 = 0xfffffffc;
    }
    else {
      local_10 = 0;
      iVar1 = FUN_0041937c(param_1,4,param_2,0);
      if (iVar1 == 1) {
        uVar2 = 0;
      }
      else {
        uVar2 = 0xfffffffd;
      }
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(local_10,uVar2);
}


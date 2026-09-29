
undefined8 FUN_00416920(int param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_18;
  
  uVar2 = 0;
  local_18 = param_4;
  iVar1 = FUN_0041602a();
  if (iVar1 == 0) {
    if ((param_1 == 0) || (param_2 == 0)) {
      uVar2 = 0xfffffffc;
    }
    else {
      iVar1 = FUN_0041a114(param_1,param_2,param_4);
      if (iVar1 != 1) {
        if (param_4 == 0) {
          uVar2 = 0xfffffffd;
        }
        else {
          uVar2 = 0xfffffffe;
        }
      }
    }
  }
  else if (((param_1 == 0) || (param_2 == 0)) || (param_4 != 0)) {
    uVar2 = 0xfffffffc;
  }
  else {
    local_18 = 0;
    iVar1 = FUN_0041a3b0(param_1,param_2,&local_18);
    if (iVar1 == 1) {
      if (local_18 != 0) {
        *DAT_0041699c = 0x10000000;
      }
    }
    else {
      uVar2 = 0xfffffffd;
    }
  }
  return CONCAT44(local_18,uVar2);
}


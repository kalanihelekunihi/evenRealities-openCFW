
undefined4 osThreadFlagsSet(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

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
    iVar1 = IRQ_Context();
    if (iVar1 == 0) {
      FUN_00455c48(param_1,0,param_2,1,0);
      FUN_00455c48(param_1,0,0,0,&local_18);
    }
    else {
      local_14 = 0;
      FUN_00455dc0(param_1,0,param_2,1,0,&local_14);
      FUN_00455dc0(param_1,0,0,0,&local_18,0);
      if (local_14 != 0) {
        *DAT_00449bb8 = 0x10000000;
      }
    }
  }
  return local_18;
}


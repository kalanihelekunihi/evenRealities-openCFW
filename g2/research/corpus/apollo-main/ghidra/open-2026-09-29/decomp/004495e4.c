
undefined8 osEventFlagsSet(int param_1,uint param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int local_10;
  
  local_10 = param_4;
  if ((param_1 == 0) || ((param_2 & 0xff000000) != 0)) {
    param_2 = 0xfffffffc;
  }
  else {
    iVar1 = IRQ_Context();
    if (iVar1 == 0) {
      param_2 = FUN_0047ed76(param_1,param_2);
    }
    else {
      local_10 = 0;
      iVar1 = FUN_0047ee4a(param_1,param_2,&local_10);
      if (iVar1 == 0) {
        param_2 = 0xfffffffd;
      }
      else {
        uVar2 = FUN_0047ed64(param_1);
        param_2 = param_2 | uVar2;
        if (local_10 != 0) {
          *DAT_00449bb8 = 0x10000000;
        }
      }
    }
  }
  return CONCAT44(local_10,param_2);
}


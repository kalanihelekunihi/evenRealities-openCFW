
undefined8 osSemaphoreAcquire(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_18;
  undefined4 uStack_14;
  
  uVar2 = 0;
  local_18 = param_3;
  if (param_1 == 0) {
    uVar2 = 0xfffffffc;
  }
  else {
    uStack_14 = param_4;
    iVar1 = IRQ_Context();
    if (iVar1 == 0) {
      iVar1 = FUN_00441c44(param_1,param_2);
      if (iVar1 != 1) {
        if (param_2 == 0) {
          uVar2 = 0xfffffffd;
        }
        else {
          uVar2 = 0xfffffffe;
        }
      }
    }
    else if (param_2 == 0) {
      local_18 = 0;
      iVar1 = FUN_00441da6(param_1,0,&local_18);
      if (iVar1 == 1) {
        if (local_18 != 0) {
          *DAT_00449bb8 = 0x10000000;
        }
      }
      else {
        uVar2 = 0xfffffffd;
      }
    }
    else {
      uVar2 = 0xfffffffc;
    }
  }
  return CONCAT44(local_18,uVar2);
}


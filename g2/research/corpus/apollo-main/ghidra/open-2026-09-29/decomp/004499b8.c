
undefined8 osSemaphoreRelease(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_10;
  
  uVar2 = 0;
  local_10 = param_4;
  if (param_1 == 0) {
    uVar2 = 0xfffffffc;
  }
  else {
    iVar1 = IRQ_Context();
    if (iVar1 == 0) {
      iVar1 = FUN_004417ee(param_1,0,0,0);
      if (iVar1 != 1) {
        uVar2 = 0xfffffffd;
      }
    }
    else {
      local_10 = 0;
      iVar1 = FUN_00441a42(param_1,&local_10);
      if (iVar1 == 1) {
        if (local_10 != 0) {
          *DAT_00449bb8 = 0x10000000;
        }
      }
      else {
        uVar2 = 0xfffffffd;
      }
    }
  }
  return CONCAT44(local_10,uVar2);
}


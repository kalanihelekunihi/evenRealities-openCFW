
undefined8 osTimerDelete(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 local_10;
  
  iVar1 = IRQ_Context();
  local_10 = param_4;
  if (iVar1 == 0) {
    if (param_1 == 0) {
      uVar2 = 0xfffffffc;
    }
    else {
      uVar3 = FUN_0047eb26(param_1);
      local_10 = 0;
      iVar1 = FUN_0047e7b0(param_1,5,0,0);
      if (iVar1 == 1) {
        if ((int)(uVar3 << 0x1f) < 0) {
          vPortFree(uVar3 & 0xfffffffe);
        }
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


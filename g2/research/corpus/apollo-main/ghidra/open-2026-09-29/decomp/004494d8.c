
undefined8 osTimerStop(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    if (param_1 == 0) {
      uVar2 = 0xfffffffc;
    }
    else {
      iVar1 = FUN_0047eaf6(param_1);
      if (iVar1 == 0) {
        uVar2 = 0xfffffffd;
      }
      else {
        param_3 = 0;
        iVar1 = FUN_0047e7b0(param_1,3,0,0,0,param_4);
        if (iVar1 == 1) {
          uVar2 = 0;
        }
        else {
          uVar2 = 0xffffffff;
        }
      }
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(param_3,uVar2);
}


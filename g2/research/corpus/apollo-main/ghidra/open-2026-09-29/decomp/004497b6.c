
undefined8 osMutexAcquire(uint param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = param_1 & 0xfffffffe;
  uVar3 = 0;
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    if (uVar2 == 0) {
      uVar3 = 0xfffffffc;
    }
    else if ((param_1 & 1) == 0) {
      iVar1 = FUN_00441c44(uVar2,param_2);
      if (iVar1 != 1) {
        if (param_2 == 0) {
          uVar3 = 0xfffffffd;
        }
        else {
          uVar3 = 0xfffffffe;
        }
      }
    }
    else {
      iVar1 = FUN_00441750(uVar2,param_2);
      if (iVar1 != 1) {
        if (param_2 == 0) {
          uVar3 = 0xfffffffd;
        }
        else {
          uVar3 = 0xfffffffe;
        }
      }
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return CONCAT44(param_4,uVar3);
}


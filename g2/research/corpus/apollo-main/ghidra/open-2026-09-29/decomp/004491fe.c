
undefined8 osThreadTerminate(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = IRQ_Context();
  if (iVar2 == 0) {
    if (param_1 == 0) {
      uVar3 = 0xfffffffc;
    }
    else {
      cVar1 = FUN_00454b88(param_1);
      if (cVar1 == '\x04') {
        uVar3 = 0xfffffffd;
      }
      else {
        uVar3 = 0;
        FUN_00454aae(param_1);
      }
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return CONCAT44(param_4,uVar3);
}


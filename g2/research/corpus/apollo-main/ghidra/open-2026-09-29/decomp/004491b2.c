
undefined4 osThreadSetPriority(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    if ((param_1 == 0) || (0x37 < param_2 - 1U)) {
      uVar2 = 0xfffffffc;
    }
    else {
      uVar2 = 0;
      FUN_00454c12(param_1,param_2);
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return uVar2;
}


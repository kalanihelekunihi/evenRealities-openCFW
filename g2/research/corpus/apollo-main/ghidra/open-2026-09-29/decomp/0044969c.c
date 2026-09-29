
undefined8 osEventFlagsWait(int param_1,uint param_2,int param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  
  if ((param_1 == 0) || ((param_2 & 0xff000000) != 0)) {
    uVar1 = 0xfffffffc;
  }
  else {
    iVar2 = IRQ_Context();
    if (iVar2 == 0) {
      uVar1 = FUN_0047ebf8(param_1,param_2,-1 < param_3 << 0x1e,param_3 << 0x1f < 0);
      if (param_3 << 0x1f < 0) {
        if ((uVar1 & param_2) != param_2) {
          if (param_4 == 0) {
            uVar1 = 0xfffffffd;
          }
          else {
            uVar1 = 0xfffffffe;
          }
        }
      }
      else if ((param_2 & uVar1) == 0) {
        if (param_4 == 0) {
          uVar1 = 0xfffffffd;
        }
        else {
          uVar1 = 0xfffffffe;
        }
      }
    }
    else if (param_4 == 0) {
      uVar1 = 0xfffffffa;
    }
    else {
      uVar1 = 0xfffffffc;
    }
  }
  return CONCAT44(param_4,uVar1);
}



undefined4 osEventFlagsClear(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((param_1 == 0) || ((param_2 & 0xff000000) != 0)) {
    uVar2 = 0xfffffffc;
  }
  else {
    iVar1 = IRQ_Context();
    if (iVar1 == 0) {
      uVar2 = FUN_0047ed10(param_1,param_2);
    }
    else {
      uVar2 = FUN_0047ed64(param_1);
      iVar1 = FUN_0047ed52(param_1,param_2);
      if (iVar1 == 0) {
        uVar2 = 0xfffffffd;
      }
      else {
        *DAT_00449bb8 = 0x10000000;
      }
    }
  }
  return uVar2;
}


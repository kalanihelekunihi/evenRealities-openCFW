
undefined4 gx8002_snpu_suspend(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_10205ad4;
  if (DAT_10205ad4[0x171] == 0) {
    uVar3 = 0xffffffff;
  }
  else {
    if (*DAT_10205ad4 != 2) {
      iVar2 = gx8002_npu_is_enabled();
      if (iVar2 != 0) {
        gx8002_npu_disable(piVar1[0x171]);
        do {
          iVar2 = gx8002_npu_all_idle(piVar1[0x171]);
        } while (iVar2 == 0);
      }
      func_0x100251ec(0);
      *piVar1 = 2;
    }
    uVar3 = 0;
  }
  return uVar3;
}


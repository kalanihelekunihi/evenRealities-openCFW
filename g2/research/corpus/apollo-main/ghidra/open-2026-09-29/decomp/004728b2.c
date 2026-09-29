
void FUN_004728b2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  int local_14;
  undefined4 uStack_10;
  
  bVar4 = *(char *)(param_1 + 4) != '\0';
  if (bVar4 != (bool)*DAT_00472c20) {
    *DAT_00472c20 = bVar4;
    piVar1 = DAT_00472c24;
    uStack_10 = param_4;
    if (bVar4) {
      iVar2 = osKernelGetTickCount();
      *DAT_00472c24 = iVar2;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472c2c,0x24f,DAT_00472c28);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00472c30,DAT_00472c30);
      }
    }
    else if (*DAT_00472c24 != 0) {
      iVar2 = osKernelGetTickCount();
      iVar2 = iVar2 - *piVar1;
      local_14 = iVar2;
      FUN_0048eb32(DAT_00472c34,1,&local_14);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472c2c,0x253,DAT_00472c38,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00472c3c,DAT_00472c3c,iVar2);
      }
      *piVar1 = 0;
    }
  }
  return;
}


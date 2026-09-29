
undefined4 _nvdbCheckSensorCaldata(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  iVar2 = FUN_0045a568();
  iVar1 = DAT_00509b30;
  if (iVar2 == 1) {
    if ((((*(float *)(DAT_00509b30 + 0x1c) < DAT_00509aec) ||
         (-1 < (int)((uint)(*(float *)(DAT_00509b30 + 0x1c) < DAT_00509af0) << 0x1f))) ||
        (-1 < (int)((uint)(*(float *)(DAT_00509b30 + 0x30) < DAT_00509af4) << 0x1f))) ||
       (*(float *)(DAT_00509b30 + 0x30) < DAT_00509af8)) {
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_2c = DAT_00509b38;
        local_30 = 0xb0;
        FUN_0043d574(2,DAT_00509b0c,DAT_00509b08,DAT_00509b3c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00509b40,DAT_00509b40);
      }
      FUN_00439c04(&local_30,DAT_00509b44,0x24);
      FUN_00439be4(iVar1 + 0x1c,&local_30,0x24);
      uVar3 = 1;
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}


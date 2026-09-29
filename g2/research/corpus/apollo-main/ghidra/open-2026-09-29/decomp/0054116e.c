
undefined4 SVC_FlashDBBlobRead(uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_28;
  uint local_24;
  int local_18;
  
  osKernelGetTickCount();
  local_24 = param_4 & 0xffff;
  local_28 = param_3;
  uVar1 = FUN_0054454a(DAT_005412c8 + (param_1 & 0xff) * 0x8ac,param_2,&local_28);
  if (local_18 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00541268,DAT_00541264,DAT_005412d0,0xf1,DAT_005412cc,param_2,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1f) {
      iVar2 = FUN_0043d0ce();
      if (-1 < iVar2 << 0x1d) goto LAB_005411e8;
    }
    compress_log_output(0x4800000,DAT_005412d4,DAT_005412d4,param_2,uVar1);
  }
LAB_005411e8:
  osKernelGetTickCount();
  return uVar1;
}


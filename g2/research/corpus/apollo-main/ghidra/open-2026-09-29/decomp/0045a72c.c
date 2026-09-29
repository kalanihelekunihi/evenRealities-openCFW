
undefined8 FUN_0045a72c(undefined4 param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = param_2;
  uVar2 = param_3;
  uVar5 = param_4;
  iVar1 = file_heap_allocate(param_3);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0xb1;
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b128,0xb1,DAT_0045b124,param_3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0045b12c,DAT_0045b12c,param_3);
    }
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00439be4(iVar1,param_2,param_3);
    uVar4 = param_4 & 0xffff;
    iVar3 = FUN_00491184(DAT_0045b130,param_1,iVar1,param_3,uVar4,uVar2,uVar5);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        uVar4 = 0xb7;
        FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b128,0xb7,DAT_0045b134);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0045b138,DAT_0045b138);
      }
      file_heap_free(iVar1);
      uVar2 = 0xffffffff;
    }
  }
  return CONCAT44(uVar4,uVar2);
}


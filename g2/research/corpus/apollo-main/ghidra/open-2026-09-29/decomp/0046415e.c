
undefined8 FUN_0046415e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uVar1 = *(undefined4 *)(param_1 + 0x1c);
  iVar2 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar2 << 0x1e < 0) {
    uStack_c = DAT_00464300;
    uStack_10 = 0x1d2;
    FUN_0043d574(4,DAT_004642cc,DAT_004642c8,DAT_00464304);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004641a0;
  }
  compress_log_output(0x10000000,DAT_00464308,DAT_00464308);
LAB_004641a0:
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_00464c36(uVar1,0,0,0);
  }
  return CONCAT44(uStack_c,uStack_10);
}


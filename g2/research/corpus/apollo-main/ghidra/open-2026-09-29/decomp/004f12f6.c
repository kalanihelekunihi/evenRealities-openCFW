
undefined8 FUN_004f12f6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar2 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar2 << 0x1e < 0) {
    uStack_c = DAT_004f1a50;
    uStack_10 = 0x312;
    FUN_0043d574(3,DAT_004f18a0,DAT_004f189c,DAT_004f1a54);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004f1a58,DAT_004f1a58);
  }
  piVar1 = DAT_004f1ef8;
  if (*DAT_004f1ef8 != 0) {
    FUN_0043f09a(*DAT_004f1ef8,0,0);
    FUN_0043f4c0(*piVar1,0x240,0x120);
  }
  *DAT_004f1a5c = 1;
  *DAT_004f1a60 = 0;
  *DAT_004f19f8 = 0;
  FUN_004f1ab8(*DAT_004f1a64);
  return CONCAT44(uStack_c,uStack_10);
}


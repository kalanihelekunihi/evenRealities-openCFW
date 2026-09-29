
undefined8 FUN_0047c084(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  piVar1 = DAT_0047c558;
  iVar3 = param_1;
  if (param_1 == 0) goto LAB_0047c148;
  if (*DAT_0047c558 == -1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar3 = 0x813;
      param_2 = DAT_0047cad4;
      FUN_0043d574(2,DAT_0047c548,DAT_0047c544,DAT_0047cad8);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1f < 0) {
LAB_0047c0d0:
      compress_log_output(0x8000000,DAT_0047cadc,DAT_0047cadc);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1d < 0) goto LAB_0047c0d0;
    }
    FUN_0047c164();
  }
  *piVar1 = *piVar1 + 1;
  *(int *)(param_1 + 0xc4) = *piVar1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    iVar3 = 0x818;
    param_2 = DAT_0047cae0;
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cad8,0x818,DAT_0047cae0,
                 *(undefined4 *)(param_1 + 0xc4),param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047cae4,DAT_0047cae4,*(undefined4 *)(param_1 + 0xc4));
  }
  FUN_00479b74(param_1);
  FUN_0047b730(param_1);
LAB_0047c148:
  return CONCAT44(param_2,iVar3);
}


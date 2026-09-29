
undefined4 FUN_0046d464(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  FUN_0046d29a();
  piVar1 = DAT_0046d648;
  iVar2 = FUN_0046cae0(DAT_0046d64c,4);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0046d624,DAT_0046d620,DAT_0046d658,0x261,DAT_0046d654,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d65c,DAT_0046d65c);
    }
    *DAT_0046d650 = 0;
  }
  else {
    uVar3 = FUN_0046cf56(*piVar1);
    *DAT_0046d650 = uVar3;
  }
  piVar1 = DAT_0046d660;
  iVar2 = FUN_0046cae0(DAT_0046d664,4);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0046d624,DAT_0046d620,DAT_0046d658,0x26b,DAT_0046d66c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d670,DAT_0046d670);
    }
    *DAT_0046d668 = 0;
  }
  else {
    uVar3 = FUN_0046cf56(*piVar1);
    *DAT_0046d668 = uVar3;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0046d624,DAT_0046d620,DAT_0046d658,0x270,DAT_0046d674,*DAT_0046d650,
                 *DAT_0046d668);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_0046d678,DAT_0046d678,*DAT_0046d650,*DAT_0046d668);
  }
  return 0;
}


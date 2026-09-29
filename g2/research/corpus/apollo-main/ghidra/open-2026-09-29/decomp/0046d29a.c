
undefined8 FUN_0046d29a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  
  FUN_0043c0e4(DAT_0046d610,0x5000,0,param_4,param_2,param_3,param_4);
  FUN_0046f65e();
  piVar1 = DAT_0046d614;
  if (*DAT_0046d614 == 0x5a5a5a5a) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x1fe;
      FUN_0043d574(2,DAT_0046d624,DAT_0046d620,DAT_0046d61c,0x1fe,DAT_0046d618,piVar1 + 1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0046d628,DAT_0046d628,piVar1 + 1);
    }
    puVar2 = DAT_0046d62c;
    DAT_0046d62c[6] = piVar1[0xd];
    if ((short)piVar1[0xe] != -1) {
      puVar2[3] = (uint)*(ushort *)(piVar1 + 0xe);
    }
    if (*(short *)((int)piVar1 + 0x3a) != -1) {
      puVar2[4] = (uint)*(ushort *)((int)piVar1 + 0x3a);
    }
    FUN_00439be4(DAT_0046d630,piVar1 + 9,0x10);
    if (*(int *)(puVar2[6] + 0xc) == 0) {
      *DAT_0046d60c = 1;
    }
    else {
      *DAT_0046d60c = 0;
    }
    *puVar2 = DAT_0046d634;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x210;
      FUN_0043d574(2,DAT_0046d624,DAT_0046d620,DAT_0046d61c,0x210,DAT_0046d638);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0046d63c,DAT_0046d63c);
    }
    DAT_0046d62c[6] = 0;
  }
  piVar1 = DAT_0046d640;
  if (*DAT_0046d640 == 0x5a5a5a5a) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x216;
      FUN_0043d574(2,DAT_0046d624,DAT_0046d620,DAT_0046d61c,0x216,DAT_0046d618,piVar1 + 1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0046d628,DAT_0046d628,piVar1 + 1);
    }
    iVar3 = DAT_0046d644;
    *(int *)(DAT_0046d644 + 0x18) = piVar1[0xd];
    if ((short)piVar1[0xe] != -1) {
      *(uint *)(iVar3 + 0xc) = (uint)*(ushort *)(piVar1 + 0xe);
    }
    if (*(short *)((int)piVar1 + 0x3a) != -1) {
      *(uint *)(iVar3 + 0x10) = (uint)*(ushort *)((int)piVar1 + 0x3a);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x21f;
      FUN_0043d574(2,DAT_0046d624,DAT_0046d620,DAT_0046d61c,0x21f,DAT_0046d638);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0046d63c,DAT_0046d63c);
    }
    *(undefined4 *)(DAT_0046d644 + 0x18) = 0;
  }
  FUN_0046f674();
  return CONCAT44(param_2,1);
}


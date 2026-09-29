
undefined8 FUN_0050fc86(char param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 unaff_r5;
  
  if (*DAT_0050fe7c == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x101;
      FUN_0043d574(2,DAT_0050febc,DAT_0050feb8,DAT_0050fedc,0x101,DAT_0050fed8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050fee0,DAT_0050fee0);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (param_1 == '\0') {
      uVar1 = 0;
    }
    else if (param_1 == '\x02') {
      uVar1 = 1;
    }
    else if (param_1 == '\x04') {
      uVar1 = 2;
    }
    else if (param_1 == '\x06') {
      uVar1 = 0;
    }
    else if (param_1 == '\b') {
      uVar1 = 3;
    }
    else if (param_1 == '\v') {
      uVar1 = 0;
    }
    else {
      if (param_1 != '\r') {
        uVar3 = 0xffffffff;
        goto LAB_0050fcfa;
      }
      uVar1 = 0;
    }
    uVar3 = FUN_0050fd1a(uVar1,0);
  }
LAB_0050fcfa:
  return CONCAT44(unaff_r5,uVar3);
}



undefined8 FUN_0052fb58(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  
  pcVar1 = DAT_0053000c;
  if (*DAT_0053000c == '\0') {
    iVar3 = FUN_0052f442();
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x151;
        FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_00530014,0x151,DAT_00530010);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00530018,DAT_00530018);
      }
      uVar2 = 0;
    }
    else {
      *pcVar1 = '\x01';
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x156;
        FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_00530014,0x156,DAT_0053001c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00530020,DAT_00530020);
      }
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_3,uVar2);
}


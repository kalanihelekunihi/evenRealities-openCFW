
undefined8 FUN_00471554(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00471b14;
  if (*DAT_00471b14 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = *DAT_00471ac4;
      param_1 = 0xc5;
      param_2 = DAT_00471b18;
      FUN_0043d574(3,DAT_00471ae0,DAT_00471adc,DAT_00471b1c,0xc5,DAT_00471b18,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00471b20,DAT_00471b20,*DAT_00471ac4,param_1,param_2,param_3)
      ;
    }
    iVar2 = SVC_KvdbWriteLanguage(*DAT_00471ac4 & 0xff);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 200;
        param_2 = DAT_00471b24;
        FUN_0043d574(1,DAT_00471ae0,DAT_00471adc,DAT_00471b1c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00471b28);
      }
    }
    *piVar1 = 0;
  }
  return CONCAT44(param_2,param_1);
}


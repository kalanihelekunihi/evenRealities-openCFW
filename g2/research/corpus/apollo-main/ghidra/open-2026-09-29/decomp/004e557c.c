
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_stop_current_streaming
          (char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*DAT_004e5f90 != 0) {
    if (param_1 == '\0') {
      text_stream_stop_animation(*DAT_004e5f90);
      *DAT_004e607c = 0;
    }
    else {
      text_stream_reset(*DAT_004e5f90);
      FUN_0043c0e4(DAT_004e607c,0x20,0);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_c = _DAT_004e6080;
      uStack_10 = 0x148;
      FUN_0043d574(3,DAT_004e5fa0,DAT_004e5f9c,_DAT_004e6084);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,_DAT_004e61a4,_DAT_004e61a4);
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}


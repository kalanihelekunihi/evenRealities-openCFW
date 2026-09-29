
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_init_text_stream_service
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_004e5f90;
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*DAT_004e5f90 == 0) {
    iVar2 = text_stream_create();
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uStack_c = _DAT_004e5f94;
        uStack_10 = 0x133;
        FUN_0043d574(1,DAT_004e5fa0,DAT_004e5f9c,_DAT_004e5f98);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_004e60e8,_DAT_004e60e8);
      }
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}


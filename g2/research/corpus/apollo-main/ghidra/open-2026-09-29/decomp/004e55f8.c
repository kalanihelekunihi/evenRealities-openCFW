
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_deinit_text_stream_service
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_004e5f90;
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*DAT_004e5f90 != 0) {
    text_stream_destroy(*DAT_004e5f90);
    *piVar1 = 0;
    *DAT_004e60ec = 0;
    *_DAT_004e60f0 = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_Even_AI_text_stream_service_dest_004e60f4;
      uStack_10 = 0x156;
      FUN_0043d574(3,DAT_004e5fa0,DAT_004e5f9c,PTR_s_even_ai_deinit_text_stream_servi_004e60f8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__even_ai_ui_Even_AI_text_stream_s_004e60fc,
                          PTR_s__even_ai_ui_Even_AI_text_stream_s_004e60fc);
    }
  }
  FUN_0043c0e4(DAT_004e607c,0x20,0);
  return CONCAT44(uStack_c,uStack_10);
}


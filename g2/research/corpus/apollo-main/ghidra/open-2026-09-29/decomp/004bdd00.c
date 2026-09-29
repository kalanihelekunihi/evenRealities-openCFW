
undefined4 APP_EvenOtaHandlerInit(undefined1 param_1)

{
  undefined1 *puVar1;
  undefined4 unaff_r7;
  
  puVar1 = DAT_004bde14;
  DAT_004bde14[1] = param_1;
  *puVar1 = 0;
  puVar1[2] = 0;
  puVar1[3] = 0;
  semantic_OtaResetExportState();
  return unaff_r7;
}


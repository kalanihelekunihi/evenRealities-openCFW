
undefined4 translate_ui_0059e1d0(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    unaff_r7 = *(undefined4 *)(DAT_0059e5cc + 0x24);
    APP_PbTranslateTxEncodeModeSwitch(&stack0xfffffff8);
  }
  return unaff_r7;
}


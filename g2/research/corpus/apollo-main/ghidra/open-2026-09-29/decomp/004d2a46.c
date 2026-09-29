
undefined4 DmHandlerInit(undefined1 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004d2ae8;
  *(undefined1 *)(DAT_004d2ae8 + 0xc) = param_1;
  *(undefined1 *)(iVar1 + 0x16) = 0;
  *(undefined1 *)(iVar1 + 0x10) = 0;
  FUN_005367e4(DAT_004d2af8);
  return unaff_r7;
}


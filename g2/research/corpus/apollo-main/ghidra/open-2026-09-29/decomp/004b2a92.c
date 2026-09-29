
undefined4 appSlaveLegAdvTypeChanged(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004b2dc8;
  *(undefined1 *)(DAT_004b2dc8 + 0x5b) = 0;
  *(undefined1 *)(iVar1 + 0x57) = 0;
  appSlaveLegAdvStart();
  return unaff_r7;
}


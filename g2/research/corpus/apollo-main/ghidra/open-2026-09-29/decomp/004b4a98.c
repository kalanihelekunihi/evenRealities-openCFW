
undefined4 HciDrvIntService(void)

{
  undefined4 unaff_r7;
  
  *DAT_004b4d94 = *DAT_004b4d94 + 1;
  WsfSetEvent(*DAT_004b4da4,1);
  return unaff_r7;
}


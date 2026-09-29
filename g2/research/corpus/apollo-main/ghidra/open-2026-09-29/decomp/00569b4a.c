
undefined4 hciCoreResetStart(void)

{
  undefined4 unaff_r7;
  
  HciResetCmd();
  HciVscUpdateBDAddress();
  return unaff_r7;
}


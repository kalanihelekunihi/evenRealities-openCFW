
undefined4 AppScanStop(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = appMasterScanMode();
  if (iVar1 != 0) {
    *(undefined1 *)(DAT_00503460 + 0x9c) = 0;
    FUN_0055bb1e();
  }
  return unaff_r7;
}


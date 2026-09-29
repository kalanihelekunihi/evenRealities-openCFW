
uint AppAdvStop(void)

{
  int iVar1;
  uint unaff_r7;
  
  iVar1 = appSlaveAdvMode();
  if (iVar1 != 0) {
    unaff_r7 = unaff_r7 & 0xffffff00;
    FUN_004b43fc(1,&stack0xfffffff8);
  }
  return unaff_r7;
}


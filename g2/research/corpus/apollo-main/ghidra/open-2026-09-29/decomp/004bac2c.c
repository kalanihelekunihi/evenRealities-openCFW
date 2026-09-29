
undefined4 DmAdvInit(void)

{
  undefined4 unaff_r7;
  
  WsfTaskLock();
  *DAT_004bacc0 = PTR_DAT_004bacbc;
  dmAdvInit();
  *DAT_004bacc4 = 0;
  WsfTaskUnlock(0);
  return unaff_r7;
}


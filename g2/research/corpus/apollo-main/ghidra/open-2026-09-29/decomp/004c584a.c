
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 DmPhyInit(void)

{
  undefined4 unaff_r7;
  
  WsfTaskLock();
  *(undefined4 *)(_DAT_004c5870 + 0x24) = _DAT_004c586c;
  HciSetLeSupFeat(0x900,0,1);
  WsfTaskUnlock();
  return unaff_r7;
}


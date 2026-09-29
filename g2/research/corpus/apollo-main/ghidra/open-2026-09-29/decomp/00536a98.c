
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 DmConnMasterInit(void)

{
  undefined4 unaff_r7;
  
  WsfTaskLock();
  *(undefined4 *)(_DAT_00536abc + 4) = _DAT_00536ab8;
  *(undefined4 *)(_DAT_00536ac4 + 4) = _DAT_00536ac0;
  WsfTaskUnlock();
  return unaff_r7;
}


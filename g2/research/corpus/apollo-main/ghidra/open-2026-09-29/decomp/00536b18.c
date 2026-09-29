
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 DmConnSlaveInit(void)

{
  undefined4 unaff_r7;
  
  WsfTaskLock();
  *(undefined4 *)(_DAT_00536b34 + 8) = _DAT_00536b30;
  *(undefined4 *)(_DAT_00536b3c + 8) = _DAT_00536b38;
  WsfTaskUnlock();
  return unaff_r7;
}


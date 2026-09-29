
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 DmPrivInit(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  WsfTaskLock();
  iVar1 = _DAT_004d2930;
  *(undefined4 *)(_DAT_004d2930 + 0x18) = _DAT_004d2934;
  *(undefined4 *)(iVar1 + 0x3c) = _DAT_004d2938;
  WsfTaskUnlock();
  return unaff_r7;
}


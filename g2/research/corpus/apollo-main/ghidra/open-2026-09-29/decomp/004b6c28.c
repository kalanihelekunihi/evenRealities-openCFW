
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 DmConnInit(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  WsfTaskLock();
  iVar1 = _DAT_004b7438;
  *(undefined **)(_DAT_004b7438 + 0xc) = PTR_PTR_004b743c;
  *(undefined **)(iVar1 + 0x10) = PTR_PTR_004b7440;
  *(undefined **)(iVar1 + 0x38) = PTR_PTR_004b7444;
  *_DAT_004b744c = PTR_PTR_004b7448;
  *DAT_004b71d0 = _DAT_004b7450;
  WsfTaskUnlock();
  return unaff_r7;
}



void FUN_00442114(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = ulSetInterruptMask();
  iVar2 = FUN_0045504c();
  if (iVar2 != 0) {
    *DAT_0044221c = 0x10000000;
  }
  vClearInterruptMask(uVar1);
  return;
}


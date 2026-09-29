
/* WARNING: Removing unreachable block (ram,0x0041c9b8) */

ulonglong FUN_0041c990(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  if ((*DAT_0041cbf4 & 0x1f) >> 3 == 2) {
    uVar2 = 1;
  }
  else {
    iVar1 = FUN_0041c2d8(0x14,&stack0xfffffff8);
    if (iVar1 == 0) {
      uVar2 = FUN_0041cd60();
    }
    else {
      uVar2 = 1;
    }
  }
  return CONCAT44(unaff_r7,uVar2) & 0xffffff00ffffffff;
}


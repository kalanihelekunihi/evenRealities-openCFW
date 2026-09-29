
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 device_mgr_fn_004c69f4(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    if ((*(int *)(DAT_004c6ca0 + 4) < 0x50) && (*(int *)(DAT_004c6ca0 + 8) < 0x10cc)) {
      *_DAT_004c6ce0 = 0;
    }
    else {
      *_DAT_004c6ce0 = *_DAT_004c6ce0 + 1;
    }
  }
  else if (*(int *)(DAT_004c6ca0 + 4) < 100) {
    *_DAT_004c6ce0 = 0;
  }
  else {
    *_DAT_004c6ce0 = *_DAT_004c6ce0 + 1;
  }
  if (*_DAT_004c6ce0 < 5) {
    *(undefined1 *)(DAT_004c6ca0 + 0x14) = 0;
  }
  else {
    *_DAT_004c6ce0 = 5;
    *(undefined1 *)(DAT_004c6ca0 + 0x14) = 1;
  }
  return unaff_r7;
}


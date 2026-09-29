
undefined4 HAL_FLASH_Unlock(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_08004b88;
  uVar2 = 1;
  if (*(int *)(DAT_08004b88 + 0x14) << 1 < 0) {
    *(undefined4 *)(DAT_08004b88 + 0xc) = DAT_08004b8c;
    *(undefined4 *)(iVar1 + 0xc) = DAT_08004b90;
    if (-1 < *(int *)(iVar1 + 0x14) << 1) {
      uVar2 = 0;
    }
  }
  return uVar2;
}


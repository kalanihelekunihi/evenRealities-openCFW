
undefined4 HAL_FLASH_OB_Unlock(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_08004c10;
  uVar2 = 0;
  if (*(int *)(DAT_08004c10 + 0x14) < 0) {
    *(undefined4 *)(DAT_08004c10 + 8) = DAT_08004c14;
    *(undefined4 *)(iVar1 + 8) = DAT_08004c18;
    if (*(int *)(iVar1 + 0x14) < 0) {
      uVar2 = 1;
    }
  }
  return uVar2;
}


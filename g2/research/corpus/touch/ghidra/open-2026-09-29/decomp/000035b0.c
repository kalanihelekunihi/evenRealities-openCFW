
undefined4 touch_storage_02b0_context_operation(void)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*DAT_000035d8 == '\0') {
    uVar1 = 1;
  }
  else {
    iVar2 = touch_eeprom_57e0_erase_adapter(DAT_000035dc);
    uVar1 = 0;
    if (iVar2 != 0) {
      if (iVar2 == DAT_000035e0) {
        uVar1 = 0;
      }
      else {
        uVar1 = 3;
      }
    }
  }
  return uVar1;
}


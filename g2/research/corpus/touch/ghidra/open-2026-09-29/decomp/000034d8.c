
undefined4 touch_storage_01d8_initialize(void)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = DAT_00003514;
  if (*DAT_0000350c == '\0') {
    *(undefined4 *)(DAT_00003514 + 8) = DAT_00003510;
    iVar2 = touch_eeprom_5738_initialize_adapter(iVar2,DAT_00003518);
    if ((iVar2 == 0) || (iVar2 == DAT_0000351c)) {
      *DAT_0000350c = '\x01';
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}


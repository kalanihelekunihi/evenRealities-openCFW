
undefined4 touch_storage_0220_read(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    uVar1 = 4;
  }
  else if ((uint)(param_1 + param_3) < 0x101) {
    if (*DAT_0000355c == '\0') {
      uVar1 = 1;
    }
    else {
      iVar2 = touch_eeprom_5778_read_adapter();
      uVar1 = 0;
      if (iVar2 != 0) {
        if (iVar2 == DAT_00003564) {
          uVar1 = 0;
        }
        else {
          uVar1 = 2;
        }
      }
    }
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}


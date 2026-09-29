
undefined4 touch_config_read_adapter(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    uVar1 = 4;
  }
  else if ((uint)(param_1 + param_3) < 0x101) {
    if (*DAT_000035a4 == '\0') {
      uVar1 = 1;
    }
    else {
      iVar2 = Cy_Em_EEPROM_Read();
      uVar1 = 0;
      if (iVar2 != 0) {
        if (iVar2 == DAT_000035ac) {
          uVar1 = 0;
        }
        else {
          uVar1 = 3;
        }
      }
    }
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}


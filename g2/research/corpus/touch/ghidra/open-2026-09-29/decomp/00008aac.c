
undefined4 Cy_Em_EEPROM_Read(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00008adc;
  if (((param_3 != 0) && ((uint)(param_3 + param_1) <= *(uint *)(param_4 + 8))) && (param_2 != 0)) {
    if (*(char *)(param_4 + 0xd) == '\0') {
      uVar1 = ReadExtendedMode();
    }
    else {
      uVar1 = ReadSimpleMode();
    }
  }
  return uVar1;
}


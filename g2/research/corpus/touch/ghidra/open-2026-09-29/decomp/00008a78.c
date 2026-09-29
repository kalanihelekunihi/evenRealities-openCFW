
undefined4 touch_eeprom_5778_read_adapter(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00008aa8;
  if (((param_3 != 0) && ((uint)(param_3 + param_1) <= *(uint *)(param_4 + 8))) && (param_2 != 0)) {
    if (*(char *)(param_4 + 0xd) == '\0') {
      uVar1 = touch_eeprom_4fe0_read_extended();
    }
    else {
      uVar1 = touch_eeprom_4b44_read_simple();
    }
  }
  return uVar1;
}


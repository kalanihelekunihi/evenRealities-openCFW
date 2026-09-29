
undefined4
touch_eeprom_4b44_read_simple(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (*(code *)(*(undefined4 **)(param_4 + 0x1c))[5])
                    (**(undefined4 **)(param_4 + 0x1c),*(int *)(param_4 + 0x10) + param_1,param_3,
                     param_2);
  uVar2 = 0;
  if (iVar1 != 0) {
    uVar2 = DAT_00007e64;
  }
  return uVar2;
}


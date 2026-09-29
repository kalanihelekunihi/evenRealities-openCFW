
undefined4 touch_eeprom_4f20_validate(int *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = param_1[2];
  uVar1 = DAT_00008288;
  if ((((iVar2 != 0) && (*param_1 != 0)) && (*(byte *)(param_1 + 1) < 2)) &&
     (((*(byte *)((int)param_1 + 7) < 2 && (*(byte *)((int)param_1 + 6) < 2)) &&
      ((*(byte *)((int)param_1 + 5) != 0 && (*(byte *)((int)param_1 + 5) < 0xb)))))) {
    uVar1 = touch_eeprom_4f00_physical_bytes(param_2,param_1);
    iVar2 = (*(code *)(*(undefined4 **)(param_2 + 0x1c))[10])
                      (**(undefined4 **)(param_2 + 0x1c),iVar2,uVar1);
    uVar1 = DAT_00008288;
    if (iVar2 != 0) {
      uVar1 = 0;
    }
  }
  return uVar1;
}


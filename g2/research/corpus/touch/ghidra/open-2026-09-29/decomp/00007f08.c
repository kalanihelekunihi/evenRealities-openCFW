
undefined4 touch_eeprom_4c08_write_range(undefined4 param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = (*(code *)(*(undefined4 **)(param_3 + 0x1c))[0xb])
                    (**(undefined4 **)(param_3 + 0x1c),param_1,*(undefined2 *)(param_3 + 2));
  uVar3 = (uint)*(ushort *)(param_3 + 2);
  if ((uint)*(ushort *)(param_3 + 2) < *(uint *)(param_3 + 4)) {
    uVar3 = *(uint *)(param_3 + 4);
  }
  if (*(char *)(param_3 + 0xf) == '\0') {
    uVar2 = 0;
  }
  else if ((iVar1 == 0) ||
          (iVar1 = (*(code *)(*(undefined4 **)(param_3 + 0x1c))[7])
                             (**(undefined4 **)(param_3 + 0x1c),param_1,uVar3), uVar2 = DAT_00007f68
          , iVar1 == 0)) {
    iVar1 = (*(code *)(*(undefined4 **)(param_3 + 0x1c))[6])
                      (**(undefined4 **)(param_3 + 0x1c),param_1,uVar3,param_2);
    uVar2 = 0;
    if (iVar1 != 0) {
      uVar2 = DAT_00007f68;
    }
  }
  return uVar2;
}


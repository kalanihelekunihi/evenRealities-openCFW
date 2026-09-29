
void touch_eeprom_560c_write_row(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  int extraout_r1;
  uint extraout_r1_00;
  uint uVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  
  iVar1 = DAT_00008988;
  puVar3 = &stack0xffffffe0 + DAT_00008988;
  puVar4 = &stack0xffffffe0 + DAT_00008988;
  if ((*(char *)(param_3 + 0xd) == '\0') &&
     (uVar2 = *(uint *)(param_3 + 4), *(ushort *)(param_3 + 2) < uVar2)) {
    __aeabi_uidivmod(param_1,uVar2);
    (*(code *)(*(undefined4 **)(param_3 + 0x1c))[5])
              (**(undefined4 **)(param_3 + 0x1c),param_1 - extraout_r1,uVar2,puVar3);
    __aeabi_uidivmod(param_1,*(undefined4 *)(param_3 + 4));
    memcpy(&stack0xffffffe0 + (extraout_r1_00 & 0xfffffffc) + iVar1,param_2,
           *(undefined2 *)(param_3 + 2));
    touch_eeprom_4c08_write_range(param_1 - extraout_r1,puVar4,param_3);
    return;
  }
  touch_eeprom_4c08_write_range(param_1,param_2,param_3);
  return;
}


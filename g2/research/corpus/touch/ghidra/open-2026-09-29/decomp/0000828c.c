
void touch_eeprom_4f8c_geometry(int param_1)

{
  short sVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = (*(code *)(*(undefined4 **)(param_1 + 0x1c))[2])
                    (**(undefined4 **)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x10));
  if (*(char *)(param_1 + 0xd) == '\0') {
    iVar3 = __aeabi_uidiv(*(int *)(param_1 + 8) + -1,uVar2);
    uVar4 = (uVar2 & 0xffff) * (iVar3 + 1);
    uVar5 = uVar4 & 0xffff;
    *(short *)(param_1 + 2) = (short)uVar4;
    if (*(uint *)(param_1 + 4) < uVar5) {
      uVar5 = *(uint *)(param_1 + 4);
    }
    *(short *)(param_1 + 2) = (short)uVar5;
    if ((uVar5 & 0xffff) < 0x80) {
      *(undefined2 *)(param_1 + 2) = 0x80;
    }
    sVar1 = __aeabi_uidiv(*(ushort *)(param_1 + 2) - 1,uVar2);
    *(short *)(param_1 + 2) = (short)uVar2 * (sVar1 + 1);
  }
  else {
    *(short *)(param_1 + 2) = (short)uVar2;
  }
  return;
}


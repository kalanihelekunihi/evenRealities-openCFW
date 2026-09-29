
int touch_eeprom_568c_initialize(undefined4 *param_1,short *param_2,undefined4 *param_3)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_00008a34;
  if (((param_2 != (short *)0x0) && (param_1 != (undefined4 *)0x0)) &&
     (param_3 != (undefined4 *)0x0)) {
    memset(param_2,0,0x20);
    *(undefined4 **)(param_2 + 0xe) = param_3;
    *(undefined4 *)(param_2 + 8) = param_1[2];
    *(undefined1 *)((int)param_2 + 0xd) = *(undefined1 *)(param_1 + 1);
    *(undefined4 *)(param_2 + 4) = *param_1;
    uVar2 = (*(code *)param_3[3])(*param_3);
    *(undefined4 *)(param_2 + 2) = uVar2;
    touch_eeprom_4f8c_geometry(param_2);
    if (*(char *)((int)param_2 + 0xd) == '\x01') {
      param_2[10] = param_2[1];
    }
    else {
      param_2[10] = (ushort)param_2[1] >> 1;
    }
    param_2[0xb] = param_2[10] + -0x10;
    sVar1 = __aeabi_uidiv(*(int *)(param_2 + 4) + -1);
    *param_2 = sVar1 + 1;
    iVar3 = touch_eeprom_4f20_validate(param_1,param_2);
    iVar4 = iVar3;
    if ((iVar3 == 0) && (iVar4 = DAT_00008a34, *(char *)((int)param_1 + 7) != '\0')) {
      if (*(char *)((int)param_2 + 0xd) == '\0') {
        *(undefined1 *)(param_2 + 6) = *(undefined1 *)((int)param_1 + 5);
        *(undefined1 *)(param_2 + 7) = *(undefined1 *)((int)param_1 + 6);
      }
      else {
        *(undefined1 *)(param_2 + 6) = 1;
        *(undefined1 *)(param_2 + 7) = 0;
      }
      *(undefined1 *)((int)param_2 + 0xf) = *(undefined1 *)((int)param_1 + 7);
      DefineLastWrittenRow(param_2);
      iVar4 = iVar3;
    }
  }
  return iVar4;
}


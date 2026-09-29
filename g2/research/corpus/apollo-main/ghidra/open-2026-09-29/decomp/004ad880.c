
undefined4 charger_get_local_battery_info(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_004ad97c;
  if (param_1 == (undefined4 *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    *param_1 = *(undefined4 *)(DAT_004ad97c + 4);
    if (*(int *)(iVar1 + 4) == 0x5d) {
      if (*(char *)(iVar1 + 0x15) == '\x01') {
        *param_1 = 0x5e;
      }
    }
    else if (*(int *)(iVar1 + 4) == 0x5e) {
      if (*(char *)(iVar1 + 0x15) == '\x01') {
        *param_1 = 0x60;
      }
      else {
        *param_1 = 0x5f;
      }
    }
    else if (*(int *)(iVar1 + 4) == 0x5f) {
      if (*(char *)(iVar1 + 0x15) == '\x01') {
        *param_1 = 0x62;
      }
      else {
        *param_1 = 0x61;
      }
    }
    else if (*(int *)(iVar1 + 4) == 0x60) {
      *param_1 = 99;
    }
    else if (0x60 < *(int *)(iVar1 + 4)) {
      *param_1 = 100;
    }
    *(bool *)(param_1 + 1) = *(int *)(iVar1 + 0xc) < 0;
    uVar2 = 0;
  }
  return uVar2;
}


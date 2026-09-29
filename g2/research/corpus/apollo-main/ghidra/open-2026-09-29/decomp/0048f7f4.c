
undefined4 FUN_0048f7f4(int param_1,char param_2,int param_3)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = *(byte *)(param_3 + 0x16) & 0xf;
  if ((*(byte *)(param_3 + 0x16) & 0xf) == 0) {
    if ((param_2 == '\0') || (param_2 == -1)) {
      uVar1 = FUN_004901cc(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 - 1 < 3) {
    if ((param_2 == '\0') || (param_2 == -1)) {
      uVar1 = FUN_004901d6(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 == 4) {
    if ((param_2 == '\x05') || (param_2 == -1)) {
      uVar1 = FUN_00490190(param_1,*(undefined4 *)(param_3 + 0x1c));
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 == 5) {
    if ((param_2 == '\x01') || (param_2 == -1)) {
      uVar1 = FUN_004901ac(param_1,*(undefined4 *)(param_3 + 0x1c));
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 == 6) {
    if (param_2 == '\x02') {
      uVar1 = FUN_00490358(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 == 7) {
    if (param_2 == '\x02') {
      uVar1 = FUN_004903ea(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 - 8 < 2) {
    if (param_2 == '\x02') {
      uVar1 = FUN_0049048c(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else if (uVar2 == 0xb) {
    if (param_2 == '\x02') {
      uVar1 = FUN_0049053c(param_1,param_3);
    }
    else {
      uVar1 = DAT_00490354;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar1 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar1;
      uVar1 = 0;
    }
  }
  else {
    uVar1 = DAT_00490488;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar1;
    uVar1 = 0;
  }
  return uVar1;
}


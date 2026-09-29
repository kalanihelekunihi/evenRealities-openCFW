
void FUN_005ca9cc(int param_1,int param_2,undefined4 param_3,int *param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int local_84;
  int local_80;
  int local_7c;
  int local_78;
  int local_74;
  int local_70;
  undefined1 auStack_6c [48];
  int local_3c;
  int iStack_2c;
  undefined4 local_28;
  
  iVar5 = param_1;
  iStack_2c = param_2;
  local_28 = param_3;
  FUN_005c6fbc(auStack_6c);
  FUN_00452b0e(param_1,0,auStack_6c);
  iVar7 = 0;
  iVar6 = 0;
  if ((char)local_28 == '\0') {
    iVar7 = FUN_005c9d84(param_1,0x50000);
    iVar1 = FUN_005c9e88(param_1,0x50000);
  }
  else {
    iVar6 = FUN_005c9d84(param_1,0x20000);
    iVar1 = FUN_005c9e88(param_1,0x20000);
  }
  if ((((*(char *)(iVar5 + 0x3c) == '\x02') || (*(char *)(iVar5 + 0x3c) == '\x04')) ||
      (*(char *)(iVar5 + 0x3c) == '\x01')) || (*(char *)(iVar5 + 0x3c) == '\0')) {
    iVar1 = FUN_005c9de8(param_1,0);
    iVar2 = FUN_005c9db6(param_1,0);
    iVar2 = iVar1 + iVar2;
    local_78 = FUN_005c9dc0(param_1,0);
    local_78 = iVar1 + local_78;
    iVar3 = FUN_005c9dd4(param_1,0);
    iVar3 = iVar1 + iVar3;
    iVar4 = FUN_005c9dca(param_1,0);
    iVar1 = iVar1 + iVar4;
    local_70 = FUN_005c9dd4(param_1,0x50000);
    local_7c = FUN_005c9dca(param_1,0x50000);
    local_80 = FUN_005c9db6(param_1,0x50000);
    local_74 = FUN_005c9dc0(param_1,0x50000);
    if (*(char *)(iVar5 + 0x3c) == '\x02') {
      iVar8 = (local_3c / 2 + *(int *)(param_1 + 0x1c)) - iVar3;
      iVar4 = local_80 + iVar2 + *(int *)(param_1 + 0x18);
    }
    else if (*(char *)(iVar5 + 0x3c) == '\x04') {
      iVar8 = iVar1 + local_3c / 2 + *(int *)(param_1 + 0x14);
      iVar4 = local_80 + iVar2 + *(int *)(param_1 + 0x18);
    }
    else if (*(char *)(iVar5 + 0x3c) == '\x01') {
      iVar8 = local_70 + iVar3 + *(int *)(param_1 + 0x14);
      iVar4 = iVar2 + local_3c / 2 + *(int *)(param_1 + 0x18);
    }
    else {
      iVar8 = local_7c + iVar1 + *(int *)(param_1 + 0x14);
      iVar4 = (local_3c / 2 + *(int *)(param_1 + 0x20)) - local_78;
    }
    if ((*(char *)(iVar5 + 0x3c) == '\0') || (*(char *)(iVar5 + 0x3c) == '\x04')) {
      if ((char)local_28 == '\0') {
        iVar7 = -iVar7;
      }
      else {
        iVar6 = -iVar6;
      }
    }
    local_84 = iVar7;
    if ((char)local_28 != '\0') {
      local_84 = iVar6;
    }
    iVar6 = (*(uint *)(iVar5 + 0x48) & 0x7fff) - 1;
    if ((*(char *)(iVar5 + 0x3c) == '\x02') || (*(char *)(iVar5 + 0x3c) == '\x04')) {
      iVar7 = (*(int *)(param_1 + 0x20) - local_78) - local_74;
      if ((iVar6 != param_2) && (iVar4 = iVar7, param_2 != 0)) {
        iVar5 = FUN_0043fdda(param_1);
        iVar4 = iVar7 - (((((iVar5 - iVar2) - local_78) - local_80) - local_74) * param_2) / iVar6;
      }
      *param_4 = iVar8 + -1;
      param_4[1] = iVar4;
      *param_5 = *param_4 - local_84;
      param_5[1] = iVar4;
    }
    else {
      if (iVar6 == param_2) {
        iVar8 = (*(int *)(param_1 + 0x1c) - iVar1) - local_7c;
      }
      else if (param_2 != 0) {
        iVar7 = FUN_0043fd9e(param_1);
        iVar8 = (((((iVar7 - iVar3) - iVar1) - local_70) - local_7c) * param_2) / iVar6 + iVar8;
      }
      *param_4 = iVar8;
      param_4[1] = iVar4;
      *param_5 = iVar8;
      param_5[1] = local_84 + param_4[1];
    }
  }
  else if ((*(char *)(iVar5 + 0x3c) == '\x10') || (*(char *)(iVar5 + 0x3c) == '\b')) {
    FUN_0043feca(param_1,&local_7c);
    iVar2 = FUN_00451598(&local_7c);
    iVar3 = FUN_004515a4(&local_7c);
    if (iVar2 / 2 < iVar3 / 2) {
      iVar2 = FUN_00451598(&local_7c);
    }
    else {
      iVar2 = FUN_004515a4(&local_7c);
    }
    iVar2 = iVar2 / 2;
    local_84 = iVar2 + local_7c;
    local_80 = iVar2 + local_78;
    iVar3 = *(int *)(iVar5 + 0x54) * 10 +
            (uint)(*(int *)(iVar5 + 0x50) * param_2 * 10) / ((*(uint *)(iVar5 + 0x48) & 0x7fff) - 1)
    ;
    if (*(char *)(iVar5 + 0x3c) == '\b') {
      iVar2 = iVar2 - local_3c;
      if ((char)local_28 == '\0') {
        iVar6 = iVar7;
      }
      iVar6 = iVar2 - iVar6;
    }
    else {
      iVar2 = iVar2 - local_3c;
      if ((char)local_28 == '\0') {
        iVar6 = iVar7;
      }
      iVar6 = iVar6 + iVar2;
    }
    *param_4 = iVar1 + iVar2 + local_84;
    param_4[1] = local_80;
    FUN_004513ae(param_4,iVar3,0x100,0x100,&local_84,0);
    *param_5 = iVar1 + iVar6 + local_84;
    param_5[1] = local_80;
    FUN_004513ae(param_5,iVar3,0x100,0x100,&local_84,0);
  }
  return;
}


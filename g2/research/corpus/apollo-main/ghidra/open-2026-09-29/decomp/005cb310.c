
undefined4
FUN_005cb310(int param_1,undefined4 param_2,int param_3,int param_4,int param_5,uint param_6,
            undefined4 *param_7)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  char local_28;
  
  for (iVar1 = FUN_00482ce4(param_1 + 0x2c); iVar1 != 0; iVar1 = FUN_00482cfa(param_1 + 0x2c,iVar1))
  {
    if ((*(int *)(iVar1 + 0xc) <= param_5) && (param_5 <= *(int *)(iVar1 + 0x10))) {
      local_28 = (char)param_2;
      if (local_28 == '\0') {
        FUN_005caede(param_1,param_4,*(undefined4 *)(iVar1 + 8),0x50000);
      }
      else {
        FUN_005caede(param_1,param_3,*(undefined4 *)(iVar1 + 4),0x20000);
      }
    }
    if ((param_6 & 0xff) == *(uint *)(iVar1 + 0x14)) {
      if ((int)((uint)*(byte *)(iVar1 + 0x34) << 0x1f) < 0) {
        iVar3 = *(int *)(param_3 + 0x30);
      }
      else {
        iVar3 = *(int *)(param_4 + 0x30);
      }
      uVar2 = param_7[1];
      *(undefined4 *)(iVar1 + 0x24) = *param_7;
      *(undefined4 *)(iVar1 + 0x28) = uVar2;
      if (iVar3 << 0x1f < 0) {
        if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
          iVar3 = iVar3 + 1;
        }
        else {
          iVar3 = iVar3 + -1;
        }
      }
      *(int *)(iVar1 + 0x1c) = iVar3;
    }
    if ((param_6 & 0xff) == *(uint *)(iVar1 + 0x18)) {
      if (*(int *)(iVar1 + 0x34) << 0x1e < 0) {
        iVar3 = *(int *)(param_3 + 0x30);
      }
      else {
        iVar3 = *(int *)(param_4 + 0x30);
      }
      uVar2 = param_7[1];
      *(undefined4 *)(iVar1 + 0x2c) = *param_7;
      *(undefined4 *)(iVar1 + 0x30) = uVar2;
      if (iVar3 << 0x1f < 0) {
        if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
          iVar3 = iVar3 + -1;
        }
        else {
          iVar3 = iVar3 + 1;
        }
      }
      *(int *)(iVar1 + 0x20) = iVar3;
    }
  }
  return param_2;
}


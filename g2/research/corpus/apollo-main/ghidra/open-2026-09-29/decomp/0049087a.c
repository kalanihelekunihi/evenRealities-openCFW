
bool FUN_0049087a(int *param_1)

{
  byte bVar1;
  int iVar2;
  ushort uVar3;
  undefined1 auStack_30 [40];
  
  bVar1 = *(byte *)((int)param_1 + 0x16);
  if ((bVar1 & 0xc0) == 0) {
    if ((bVar1 & 0x30) == 0) {
      return false;
    }
    if ((bVar1 & 0x30) == 0x20) {
      return *(short *)param_1[8] == 0;
    }
    if ((bVar1 & 0x30) == 0x30) {
      return *(short *)param_1[8] == 0;
    }
    if (((bVar1 & 0x30) == 0x10) && (param_1[8] != 0)) {
      iVar2 = FUN_00490678(param_1[8]);
      return iVar2 == 0;
    }
    if (*(int *)(*param_1 + 8) != 0) {
      return false;
    }
    if ((bVar1 & 0xf) < 6) {
      uVar3 = 0;
      while( true ) {
        if (*(ushort *)((int)param_1 + 0x12) <= uVar3) {
          return true;
        }
        if (*(char *)(param_1[7] + (uint)uVar3) != '\0') break;
        uVar3 = uVar3 + 1;
      }
      return false;
    }
    if ((bVar1 & 0xf) == 6) {
      return *(short *)param_1[7] == 0;
    }
    if ((bVar1 & 0xf) == 7) {
      return *(char *)param_1[7] == '\0';
    }
    if ((bVar1 & 0xf) == 0xb) {
      return *(short *)((int)param_1 + 0x12) == 0;
    }
    if (((bVar1 & 0xf) == 8) || ((bVar1 & 0xf) == 9)) {
      iVar2 = FUN_004d9384(auStack_30,param_1[9],param_1[7]);
      while( true ) {
        if (iVar2 == 0) {
          return true;
        }
        iVar2 = FUN_0049087a(auStack_30);
        if (iVar2 == 0) break;
        iVar2 = FUN_004d93d8(auStack_30);
      }
      return false;
    }
  }
  else {
    if ((bVar1 & 0xc0) == 0x80) {
      return param_1[7] == 0;
    }
    if ((bVar1 & 0xc0) == 0x40) {
      if ((bVar1 & 0xf) == 10) {
        return *(int *)param_1[7] == 0;
      }
      if (*(int *)(*param_1 + 0xc) == DAT_004910bc) {
        return *(int *)param_1[7] == 0;
      }
      return *(int *)(*param_1 + 0xc) == 0;
    }
  }
  return false;
}


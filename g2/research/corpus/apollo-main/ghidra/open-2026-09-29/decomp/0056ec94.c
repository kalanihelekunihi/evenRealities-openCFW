
undefined1 smpProcRcvKey(int param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  bool bVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  bVar2 = false;
  uVar4 = 0;
  cVar1 = *(char *)(param_3 + 8);
  if (cVar1 == '\x06') {
    FUN_00542a44(param_2 + 4);
  }
  else if (cVar1 == '\a') {
    *(ushort *)(param_2 + 0x1c) =
         (ushort)*(byte *)(param_3 + 10) * 0x100 + (ushort)*(byte *)(param_3 + 9);
    FUN_00439be4(param_2 + 0x14,param_3 + 0xb,8);
    if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
      uVar3 = 2;
    }
    else {
      uVar3 = 1;
    }
    *(undefined1 *)(param_2 + 0x1f) = uVar3;
    *(undefined1 *)(param_2 + 0x1e) = 2;
    bVar2 = true;
  }
  else if (cVar1 == '\b') {
    FUN_00542a44(param_2 + 4);
  }
  else if (cVar1 == '\t') {
    *(byte *)(param_2 + 0x1a) = *(byte *)(param_3 + 9);
    FUN_004d293c(param_2 + 0x14,param_3 + 10);
    *(undefined1 *)(param_2 + 0x1e) = 4;
    bVar2 = true;
  }
  else if (cVar1 == '\n') {
    FUN_00542a44(param_2 + 4);
    *(undefined1 *)(param_2 + 0x1e) = 8;
    bVar2 = true;
  }
  if ((*(char *)(param_1 + 0x3f) == '\x06') || (*(char *)(param_1 + 0x3f) == '\b')) {
    *(char *)(param_1 + 0x3f) = *(char *)(param_1 + 0x3f) + '\x01';
  }
  else if ((param_4 << 0x1e < 0) && (*(char *)(param_1 + 0x3f) == '\a')) {
    *(undefined1 *)(param_1 + 0x3f) = 8;
  }
  else if ((param_4 << 0x1d < 0) &&
          ((*(char *)(param_1 + 0x3f) == '\a' || (*(char *)(param_1 + 0x3f) == '\t')))) {
    *(undefined1 *)(param_1 + 0x3f) = 10;
  }
  else {
    uVar4 = 1;
  }
  if (bVar2) {
    *(undefined1 *)(param_2 + 2) = 0x2f;
    DmSmpCbackExec(param_2);
  }
  return uVar4;
}


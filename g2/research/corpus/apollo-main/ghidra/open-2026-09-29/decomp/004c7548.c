
longlong FUN_004c7548(undefined4 param_1,int param_2,undefined4 param_3,uint param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  cVar1 = *(char *)(param_2 + 4);
  if (cVar1 == '\x01') {
    iVar2 = *(int *)(param_2 + 0x54);
    if ((((*(byte *)(iVar2 + 0x2f) & 0xf) != 4) && ((*(byte *)(iVar2 + 0x2f) & 0xf) != 5)) &&
       ((*(byte *)(iVar2 + 0x2f) & 0xf) != 3)) {
      *(undefined1 *)(param_2 + 0x59) = 10;
      *(undefined1 *)(param_2 + 0x58) = 9;
    }
  }
  else if (cVar1 == '\x02') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\x03') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\x05') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\x06') {
    iVar3 = *(int *)(param_2 + 0x54);
    iVar2 = FUN_004b05a4(*(uint *)(iVar3 + 0x20) >> 8 & 0xff);
    if (((iVar2 != -1) && ((*(byte *)(iVar3 + 0x51) & 7) != 2)) &&
       ((*(byte *)(iVar3 + 0x51) & 7) != 3)) {
      *(undefined1 *)(param_2 + 0x59) = 10;
      *(undefined1 *)(param_2 + 0x58) = 9;
    }
  }
  else if (cVar1 == '\a') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\b') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\t') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\n') {
    iVar2 = *(int *)(param_2 + 0x54);
    if ((((*(byte *)(iVar2 + 0x43) & 0xf) != 4) && ((*(byte *)(iVar2 + 0x43) & 0xf) != 5)) &&
       ((*(byte *)(iVar2 + 0x43) & 0xf) != 3)) {
      *(undefined1 *)(param_2 + 0x59) = 10;
      *(undefined1 *)(param_2 + 0x58) = 9;
    }
  }
  else if (cVar1 == '\v') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  else if (cVar1 == '\r') {
    *(undefined1 *)(param_2 + 0x59) = 10;
    *(undefined1 *)(param_2 + 0x58) = 9;
  }
  return (ulonglong)param_4 << 0x20;
}


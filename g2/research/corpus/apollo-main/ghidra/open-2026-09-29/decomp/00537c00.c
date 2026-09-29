
undefined1 smpGetScSecLevel(int param_1)

{
  char cVar1;
  undefined1 uVar2;
  
  if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
    if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
      cVar1 = *(char *)(param_1 + 0x24);
    }
    else {
      cVar1 = *(char *)(param_1 + 0x2b);
    }
    if (cVar1 == '\x10') {
      uVar2 = 3;
    }
    else {
      uVar2 = 2;
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}


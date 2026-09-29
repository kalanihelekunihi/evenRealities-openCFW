
bool attsPendIndNtfHandle(int param_1,int param_2)

{
  byte bVar1;
  byte bVar2;
  bool bVar3;
  
  if (*(char *)(param_2 + 8) == '\x1d') {
    bVar3 = *(short *)(param_1 + 0x28) != 0;
  }
  else {
    bVar1 = 0;
    for (bVar2 = 0; bVar2 < 10; bVar2 = bVar2 + 1) {
      if (*(short *)(param_1 + (uint)bVar2 * 2 + 0x2a) != 0) {
        if (*(short *)(param_1 + (uint)bVar2 * 2 + 0x2a) == *(short *)(param_2 + 2)) {
          return true;
        }
        bVar1 = bVar1 + 1;
      }
    }
    bVar3 = 9 < bVar1;
  }
  return bVar3;
}


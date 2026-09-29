
void attsSetPendNtfHandle(int param_1,undefined2 param_2)

{
  byte bVar1;
  
  bVar1 = 0;
  while( true ) {
    if (9 < bVar1) {
      return;
    }
    if (*(short *)(param_1 + (uint)bVar1 * 2 + 0x2a) == 0) break;
    bVar1 = bVar1 + 1;
  }
  *(undefined2 *)(param_1 + (uint)bVar1 * 2 + 0x2a) = param_2;
  return;
}


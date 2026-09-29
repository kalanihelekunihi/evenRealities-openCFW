
void attcSetPendWriteCmd(int param_1)

{
  bool bVar1;
  
  bVar1 = false;
  while( true ) {
    if (bVar1) {
      return;
    }
    if (*(short *)(param_1 + 0x2a) == 0) break;
    bVar1 = true;
  }
  *(undefined2 *)(param_1 + 0x2a) = *(undefined2 *)(param_1 + 0xc);
  return;
}



void attsClearPrepWrites(int param_1)

{
  int iVar1;
  
  while (iVar1 = WsfQueueDeq(DAT_00535448 + (uint)*(byte *)(param_1 + 0x24) * 8 + 0x238), iVar1 != 0
        ) {
    WsfBufFree(iVar1);
  }
  return;
}


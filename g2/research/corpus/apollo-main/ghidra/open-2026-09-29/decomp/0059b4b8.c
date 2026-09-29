
int FUN_0059b4b8(int *param_1)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = 0;
  iVar5 = 0;
  puVar3 = (uint *)(param_1 + 2);
  if (0 < *param_1) {
    do {
      uVar2 = *puVar3;
      iVar1 = 0x800;
      if (0 < (int)uVar2) {
        iVar1 = *(ushort *)(DAT_0059b694 + (uint)*(byte *)(param_1 + 1) * 0x10 + uVar2 * 2 + -2) +
                0x800;
        if ((uVar2 & 3) != 0) {
          do {
            loopEnd();
          } while( true );
        }
        if (uVar2 >> 2 != 0) {
          do {
            loopEnd();
          } while( true );
        }
      }
      iVar5 = iVar5 + 1;
      puVar3 = puVar3 + 1;
      iVar4 = iVar4 + (iVar1 + 0x7ff >> 0xb);
    } while (iVar5 < *param_1);
  }
  return iVar4;
}


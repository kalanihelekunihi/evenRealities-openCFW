
int FUN_100042e8(void)

{
  int *piVar1;
  int iVar2;
  uint in_r3;
  
  iVar2 = FUN_10004020();
  piVar1 = DAT_10004328;
  if (iVar2 != -1) {
    FUN_10003274(DAT_10004328[in_r3 + 0xda],0x1a0);
    *(int *)(*piVar1 + 0x3a0) = 0x101 << (in_r3 & 0x3f);
    iVar2 = 0;
  }
  return iVar2;
}



int FUN_0049207a(int param_1,ushort *param_2)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = 0;
  uVar1 = FUN_0049174e(*param_2);
  *param_2 = uVar1;
  for (uVar2 = 1; -1 < (char)uVar2; uVar2 = uVar2 - 1) {
    *(char *)(param_1 + iVar3) = (char)((int)(uint)*param_2 >> ((uVar2 & 0x1f) << 3));
    iVar3 = iVar3 + 1;
  }
  return iVar3;
}


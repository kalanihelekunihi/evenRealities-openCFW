
uint touch_sub_2f3c(int param_1,int param_2)

{
  byte bVar1;
  ushort uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = *(ushort *)(param_1 + 0x2c);
  bVar1 = *(byte *)(*(int *)(param_2 + 8) + 0x4d);
  iVar3 = touch_sub_2f20(*(undefined2 *)(*(int *)(param_2 + 8) + 0x3c));
  if ((uint)bVar1 + (uint)uVar2 < iVar3 + 1U >> 2) {
    uVar4 = 0;
  }
  else {
    uVar4 = 2;
  }
  return uVar4 | 8;
}


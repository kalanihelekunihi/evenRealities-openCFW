
uint touch_sub_422e(int param_1,int param_2)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
  cVar1 = *(char *)(iVar4 + 0x7b);
  uVar5 = 0;
  for (uVar3 = (uint)*(ushort *)(iVar4 + 0x80);
      uVar3 < (uint)*(ushort *)(iVar4 + 0x80) + (uint)*(ushort *)(iVar4 + 0x82); uVar3 = uVar3 + 1)
  {
    uVar2 = touch_sub_3ff8(cVar1 == '\a',uVar3,param_2);
    uVar5 = uVar5 | uVar2;
  }
  return uVar5;
}


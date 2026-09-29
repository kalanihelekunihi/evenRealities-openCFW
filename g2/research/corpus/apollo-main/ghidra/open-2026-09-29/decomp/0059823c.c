
ulonglong FUN_0059823c(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = -(param_2 >> 0x14);
  iVar3 = iVar1 + 0x41e;
  if (iVar3 != 0 && param_2 >> 0x14 < 0x41f) {
    uVar4 = UnsignedSaturate(iVar3,7);
    UnsignedDoesSaturate(iVar3,7);
    return (ulonglong)((param_2 << 0xb | 0x80000000 | param_1 >> 0x15) >> (uVar4 & 0xff));
  }
  uVar4 = iVar1 + 0x43e;
  if (-0x21 < iVar3) {
    uVar2 = param_2 << 0xb | 0x80000000 | param_1 >> 0x15;
    return CONCAT44(uVar2 >> (uVar4 & 0xff),
                    ((param_1 << 0xb) >> (uVar4 & 0xff)) + (uVar2 << (0x20 - uVar4 & 0xff)));
  }
  return CONCAT44(~((int)param_2 >> 0x1f),~((int)param_2 >> 0x1f));
}


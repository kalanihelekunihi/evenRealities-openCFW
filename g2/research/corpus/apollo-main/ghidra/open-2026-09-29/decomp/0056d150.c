
undefined4 smpGetPkBit(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)(param_1 + 0x48);
  if (((uint)*(byte *)(*(int *)(iVar1 + 0x14) + (0xf - (*(byte *)(iVar1 + 3) >> 3) & 0xff) + 0x20) &
      1 << (uint)*(byte *)(iVar1 + 3) % 8) == 0) {
    uVar2 = 0x80;
  }
  else {
    uVar2 = 0x81;
  }
  return uVar2;
}


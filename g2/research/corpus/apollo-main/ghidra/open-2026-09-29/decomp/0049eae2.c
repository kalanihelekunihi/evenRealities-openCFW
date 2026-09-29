
longlong FUN_0049eae2(char param_1,uint param_2)

{
  uint uVar1;
  ushort uVar2;
  uint local_10;
  uint local_c;
  
  local_c = DAT_0049efac[1];
  local_10 = CONCAT31((int3)((uint)*DAT_0049efac >> 8),param_1);
  uVar1 = param_2;
  if (param_1 == '\x03') {
    uVar2 = FUN_0045a568();
    uVar1 = param_2 & 0xffff | (uint)uVar2 << 0x10;
  }
  local_c = uVar1;
  FUN_00464d1c(0x107,&local_10,8,0);
  return (ulonglong)local_10 << 0x20;
}


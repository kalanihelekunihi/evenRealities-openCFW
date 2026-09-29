
byte WsfOsSetNextHandler(undefined4 param_1)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = DAT_0052bac4;
  bVar1 = *(byte *)(DAT_0052bac4 + 0x3d);
  *(char *)(DAT_0052bac4 + 0x3d) = *(char *)(DAT_0052bac4 + 0x3d) + '\x01';
  *(undefined4 *)(iVar2 + (uint)bVar1 * 4) = param_1;
  return bVar1;
}


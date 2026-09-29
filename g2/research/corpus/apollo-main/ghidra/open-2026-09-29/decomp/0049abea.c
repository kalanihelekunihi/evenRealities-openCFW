
undefined8 FUN_0049abea(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  if ((*(byte *)(param_1 + 0x5c) & 0x3f) >> 5 != 0) {
    bVar2 = 8;
  }
  if ((*(byte *)(param_1 + 0x5c) & 0x7f) >> 6 != 0) {
    bVar2 = bVar2 | 1;
  }
  iVar1 = FUN_00499360(param_1,0);
  if (((iVar1 == 0x3fffffff) && (iVar1 = FUN_0049936a(param_1,0), iVar1 == 0x1fffffff)) &&
     ((*(ushort *)(param_1 + 0x2a) & 0xfff) >> 0xb == 0)) {
    bVar2 = bVar2 | 2;
  }
  return CONCAT44(param_4,(uint)bVar2);
}



undefined4
FUN_0041d294(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  
  *param_1 = *DAT_0041d890;
  param_1[1] = *DAT_0041d894;
  param_1[2] = *DAT_0041d898;
  param_1[3] = *DAT_0041d89c;
  param_1[4] = *DAT_0041d8a0;
  puVar1 = DAT_0041d8a4;
  param_1[5] = *DAT_0041d8a4;
  param_1[6] = 1;
  param_1[0xb] = (uint)*(ushort *)(DAT_0041d8a8 + ((*puVar1 & 0xf) >> 2) * 2) << 10;
  iVar2 = DAT_0041d8ac;
  param_1[8] = (uint)*(ushort *)(DAT_0041d8ac + (*puVar1 & 3) * 6) << 10;
  param_1[9] = (uint)*(ushort *)((*puVar1 & 3) * 6 + iVar2 + 2) << 10;
  param_1[10] = (uint)*(ushort *)(iVar2 + (*puVar1 & 3) * 6 + 4) << 10;
  param_1[0xc] = *DAT_0041d8b0 & 0xff;
  FUN_0041f9e6(10);
  puVar1 = DAT_0041d8b4;
  param_1[0xc] = param_1[0xc] | (*DAT_0041d8b4 & 0xf) << 8;
  FUN_0041f9e6(10);
  param_1[0xd] = (*puVar1 & 0xff) >> 4;
  FUN_0041f9e6(10);
  puVar1 = DAT_0041d8b8;
  param_1[0xd] = param_1[0xd] | (*DAT_0041d8b8 & 0xf) << 4;
  FUN_0041f9e6(10);
  param_1[0xe] = *puVar1 & 0xf0;
  FUN_0041f9e6(10);
  param_1[0xe] = param_1[0xe] | (*DAT_0041d8bc & 0xff) >> 4;
  FUN_0041f9e6(10);
  param_1[0xf] = *DAT_0041d8c0 << 0x18;
  FUN_0041f9e6(10);
  param_1[0xf] = param_1[0xf] | (*DAT_0041d8c4 & 0xff) << 0x10;
  FUN_0041f9e6(10);
  param_1[0xf] = param_1[0xf] | (*DAT_0041d8c8 & 0xff) << 8;
  FUN_0041f9e6(10);
  param_1[0xf] = param_1[0xf] | *DAT_0041d8cc & 0xff;
  FUN_0041f9e6(10);
  return param_4;
}


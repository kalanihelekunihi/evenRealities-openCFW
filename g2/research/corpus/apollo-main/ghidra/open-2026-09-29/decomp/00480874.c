
undefined4
FUN_00480874(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  
  *param_1 = *DAT_00480e70;
  param_1[1] = *DAT_00480e74;
  param_1[2] = *DAT_00480e78;
  param_1[3] = *DAT_00480e7c;
  param_1[4] = *DAT_00480e80;
  puVar1 = DAT_00480e84;
  param_1[5] = *DAT_00480e84;
  param_1[6] = 1;
  param_1[0xb] = (uint)*(ushort *)(DAT_00480e88 + ((*puVar1 & 0xf) >> 2) * 2) << 10;
  iVar2 = DAT_00480e8c;
  param_1[8] = (uint)*(ushort *)(DAT_00480e8c + (*puVar1 & 3) * 6) << 10;
  param_1[9] = (uint)*(ushort *)((*puVar1 & 3) * 6 + iVar2 + 2) << 10;
  param_1[10] = (uint)*(ushort *)(iVar2 + (*puVar1 & 3) * 6 + 4) << 10;
  param_1[0xc] = *DAT_00480e90 & 0xff;
  FUN_00491102(10);
  puVar1 = DAT_00480e94;
  param_1[0xc] = param_1[0xc] | (*DAT_00480e94 & 0xf) << 8;
  FUN_00491102(10);
  param_1[0xd] = (*puVar1 & 0xff) >> 4;
  FUN_00491102(10);
  puVar1 = DAT_00480e98;
  param_1[0xd] = param_1[0xd] | (*DAT_00480e98 & 0xf) << 4;
  FUN_00491102(10);
  param_1[0xe] = *puVar1 & 0xf0;
  FUN_00491102(10);
  param_1[0xe] = param_1[0xe] | (*DAT_00480e9c & 0xff) >> 4;
  FUN_00491102(10);
  param_1[0xf] = *DAT_00480ea0 << 0x18;
  FUN_00491102(10);
  param_1[0xf] = param_1[0xf] | (*DAT_00480ea4 & 0xff) << 0x10;
  FUN_00491102(10);
  param_1[0xf] = param_1[0xf] | (*DAT_00480ea8 & 0xff) << 8;
  FUN_00491102(10);
  param_1[0xf] = param_1[0xf] | *DAT_00480eac & 0xff;
  FUN_00491102(10);
  return param_4;
}


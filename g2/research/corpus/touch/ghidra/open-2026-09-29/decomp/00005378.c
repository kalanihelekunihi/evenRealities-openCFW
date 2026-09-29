
void touch_config_2078_build(int *param_1)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  int iVar5;
  uint local_128 [5];
  undefined4 local_114;
  undefined4 local_10c;
  undefined4 local_100;
  undefined4 local_f8;
  uint local_c8;
  uint local_c4;
  uint local_c0;
  
  iVar5 = param_1[2];
  memset(local_128,0,0x100);
  uVar3 = DAT_0000551c;
  uVar2 = DAT_00005518;
  local_128[0] = DAT_00005518;
  local_128[1] = 0x10000000;
  local_114 = 0x31;
  local_10c = 0x10000;
  local_100 = 0xf00;
  local_f8 = 0x101;
  local_c8 = DAT_0000551c;
  local_c4 = DAT_0000551c;
  local_c0 = DAT_0000551c;
  puVar4 = (uint *)param_1[9];
  *puVar4 = DAT_00005518;
  puVar4[1] = 0x10000000;
  puVar4[2] = 0;
  puVar4[3] = 0;
  puVar4[4] = 0;
  puVar4[5] = 0x31;
  puVar4[6] = 0;
  puVar4[7] = 0x10000;
  puVar4[10] = 0xf00;
  puVar4[0xc] = 0x101;
  puVar4[0xe] = 0;
  puVar4[0xf] = 0;
  puVar4[0x10] = 0;
  puVar4[0x12] = 0;
  puVar4[0x13] = 0;
  puVar4[0x14] = 0;
  puVar4[0x15] = 0;
  puVar4[0x16] = 0;
  puVar4[0x17] = 0;
  puVar4[0x18] = uVar3;
  puVar4[0x19] = uVar3;
  puVar4[0x1a] = uVar3;
  puVar4[0x1b] = 0;
  *puVar4 = (*(byte *)(iVar5 + 0x71) & 3) << 0x10 | uVar2;
  uVar2 = *(byte *)(*param_1 + 0x37) & 7 | 0x10000000;
  puVar4[1] = uVar2;
  puVar4[1] = uVar2 | (*(byte *)(*param_1 + 0x38) & 1) << 8;
  if (*(ushort *)(iVar5 + 0x44) == 0) {
    uVar2 = 0x100;
  }
  else {
    uVar2 = (*(ushort *)(iVar5 + 0x44) & 0xf) << 8;
  }
  puVar4[2] = uVar2;
  if (*(ushort *)(iVar5 + 0x42) == 0) {
    uVar3 = 1;
  }
  else {
    uVar3 = *(ushort *)(iVar5 + 0x42) & 0xff;
  }
  puVar4[2] = uVar2 | uVar3;
  puVar4[2] = uVar2 | uVar3 | (*(byte *)(*param_1 + 0x36) & 1) << 0xc;
  uVar2 = *(ushort *)(iVar5 + 0x30) & 0xfff;
  puVar4[3] = uVar2;
  puVar4[3] = uVar2 | (uint)*(ushort *)(iVar5 + 0x32) << 0x10 & DAT_00005520;
  puVar4[5] = (uint)*(byte *)(iVar5 + 0x53);
  bVar1 = *(byte *)(param_1[2] + 0x4d);
  puVar4[6] = (uint)bVar1;
  uVar2 = (uint)bVar1 | (*(ushort *)(param_1[2] + 0x40) & 0xf) << 0x10;
  puVar4[6] = uVar2;
  puVar4[6] = uVar2 | (*(ushort *)(param_1[2] + 0x3e) & 0x1f) << 8;
  puVar4[8] = *(ushort *)(param_1[2] + 0x3c) & 0xfff | (*(byte *)(param_1[2] + 0x4e) & 0xf) << 0x10;
  puVar4[9] = 0;
  puVar4[0xb] = (uint)*(byte *)(param_1[2] + 0x4f) | (uint)*(byte *)(param_1[2] + 0x50) << 0x10;
  puVar4[10] = (uint)*(byte *)(iVar5 + 0x54) << 8;
  puVar4[0x11] = 6;
  puVar4[0x11] = (*(byte *)(param_1[2] + 0x51) - 1) * 0x10000 & DAT_00005524 | 6;
  touch_config_1fbc_load_profiles(param_1);
  touch_config_1de4_load_mapping(param_1);
  return;
}


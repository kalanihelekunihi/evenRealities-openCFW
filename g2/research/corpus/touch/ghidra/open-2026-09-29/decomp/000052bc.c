
void touch_config_1fbc_load_profiles(int param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  
  puVar1 = DAT_00005368;
  iVar2 = *(int *)(param_1 + 0x24);
  uVar3 = DAT_00005368[1];
  uVar4 = DAT_00005368[2];
  puVar5 = DAT_00005368 + 3;
  *(undefined4 *)(iVar2 + 0x90) = *DAT_00005368;
  *(undefined4 *)(iVar2 + 0x94) = uVar3;
  *(undefined4 *)(iVar2 + 0x98) = uVar4;
  uVar3 = puVar1[4];
  uVar4 = puVar1[5];
  *(undefined4 *)(iVar2 + 0x9c) = *puVar5;
  *(undefined4 *)(iVar2 + 0xa0) = uVar3;
  *(undefined4 *)(iVar2 + 0xa4) = uVar4;
  *(undefined4 *)(iVar2 + 0xa8) = puVar1[6];
  uVar3 = puVar1[8];
  uVar4 = puVar1[9];
  *(undefined4 *)(iVar2 + 0xac) = puVar1[7];
  *(undefined4 *)(iVar2 + 0xb0) = uVar3;
  *(undefined4 *)(iVar2 + 0xb4) = uVar4;
  uVar3 = puVar1[0xb];
  uVar4 = puVar1[0xc];
  *(undefined4 *)(iVar2 + 0xb8) = puVar1[10];
  *(undefined4 *)(iVar2 + 0xbc) = uVar3;
  *(undefined4 *)(iVar2 + 0xc0) = uVar4;
  *(undefined4 *)(iVar2 + 0xc4) = puVar1[0xd];
  uVar3 = puVar1[0xf];
  uVar4 = puVar1[0x10];
  *(undefined4 *)(iVar2 + 200) = puVar1[0xe];
  *(undefined4 *)(iVar2 + 0xcc) = uVar3;
  *(undefined4 *)(iVar2 + 0xd0) = uVar4;
  uVar3 = puVar1[0x12];
  uVar4 = puVar1[0x13];
  *(undefined4 *)(iVar2 + 0xd4) = puVar1[0x11];
  *(undefined4 *)(iVar2 + 0xd8) = uVar3;
  *(undefined4 *)(iVar2 + 0xdc) = uVar4;
  *(undefined4 *)(iVar2 + 0xe0) = puVar1[0x14];
  puVar1 = DAT_0000536c;
  if (*(char *)(*(int *)(param_1 + 8) + 0x5a) == '\x01') {
    uVar3 = DAT_0000536c[1];
    uVar4 = DAT_0000536c[2];
    puVar5 = DAT_0000536c + 3;
    *(undefined4 *)(iVar2 + 0x90) = *DAT_0000536c;
    *(undefined4 *)(iVar2 + 0x94) = uVar3;
    *(undefined4 *)(iVar2 + 0x98) = uVar4;
    uVar3 = puVar1[4];
    uVar4 = puVar1[5];
    *(undefined4 *)(iVar2 + 0x9c) = *puVar5;
    *(undefined4 *)(iVar2 + 0xa0) = uVar3;
    *(undefined4 *)(iVar2 + 0xa4) = uVar4;
    *(undefined4 *)(iVar2 + 0xa8) = puVar1[6];
  }
  puVar1 = DAT_00005370;
  if (*(char *)(*(int *)(param_1 + 8) + 0x5b) == '\x01') {
    uVar3 = DAT_00005370[1];
    uVar4 = DAT_00005370[2];
    puVar5 = DAT_00005370 + 3;
    *(undefined4 *)(iVar2 + 0xac) = *DAT_00005370;
    *(undefined4 *)(iVar2 + 0xb0) = uVar3;
    *(undefined4 *)(iVar2 + 0xb4) = uVar4;
    uVar3 = puVar1[4];
    uVar4 = puVar1[5];
    *(undefined4 *)(iVar2 + 0xb8) = *puVar5;
    *(undefined4 *)(iVar2 + 0xbc) = uVar3;
    *(undefined4 *)(iVar2 + 0xc0) = uVar4;
    *(undefined4 *)(iVar2 + 0xc4) = puVar1[6];
  }
  if (*(char *)(*(int *)(param_1 + 8) + 0x75) == '\x05') {
    *(uint *)(iVar2 + 0xbc) = *(uint *)(iVar2 + 0xbc) | 0x100;
  }
  puVar1 = DAT_00005374;
  if (*(char *)(*(int *)(param_1 + 8) + 0x5c) == '\x01') {
    uVar3 = DAT_00005374[1];
    uVar4 = DAT_00005374[2];
    puVar5 = DAT_00005374 + 3;
    *(undefined4 *)(iVar2 + 200) = *DAT_00005374;
    *(undefined4 *)(iVar2 + 0xcc) = uVar3;
    *(undefined4 *)(iVar2 + 0xd0) = uVar4;
    uVar3 = puVar1[4];
    uVar4 = puVar1[5];
    *(undefined4 *)(iVar2 + 0xd4) = *puVar5;
    *(undefined4 *)(iVar2 + 0xd8) = uVar3;
    *(undefined4 *)(iVar2 + 0xdc) = uVar4;
    *(undefined4 *)(iVar2 + 0xe0) = puVar1[6];
  }
  return;
}


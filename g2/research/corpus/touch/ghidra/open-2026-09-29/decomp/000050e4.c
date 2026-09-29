
undefined4 touch_config_1de4_load_mapping(int param_1)

{
  uint uVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  undefined4 local_50 [15];
  
  iVar5 = *(int *)(param_1 + 8);
  iVar4 = *(int *)(param_1 + 0x24);
  memcpy(local_50,DAT_00005184,0x38);
  for (uVar3 = 0; uVar3 < 0xe; uVar3 = uVar3 + 1) {
    *(undefined1 *)(iVar5 + 99 + uVar3) = 0xff;
  }
  *(undefined1 *)(iVar5 + 0x68) = 0;
  cVar2 = *(char *)(*(int *)(param_1 + 8) + 0x74);
  if (cVar2 == '\x01') {
    if (*(char *)(iVar5 + 99) == -1) {
      *(undefined1 *)(iVar5 + 99) = 1;
      cVar2 = '\x02';
    }
  }
  else if (cVar2 == '\x02') {
    if (*(char *)(iVar5 + 100) == -1) {
      *(undefined1 *)(iVar5 + 100) = 1;
    }
    else {
      cVar2 = '\x01';
    }
  }
  else {
    cVar2 = '\x01';
  }
  if (*(char *)(iVar5 + 0x6b) == -1) {
    *(char *)(iVar5 + 0x6b) = cVar2;
    cVar2 = cVar2 + '\x01';
  }
  *(char *)(*(int *)(param_1 + 8) + 0x62) = cVar2;
  for (uVar3 = 0; uVar3 < 0xe; uVar3 = uVar3 + 1) {
    uVar1 = (uint)*(byte *)(iVar5 + 99 + uVar3);
    if (uVar1 != 0xff) {
      *(undefined4 *)(iVar4 + 0x70 + uVar1 * 4) = local_50[uVar3];
    }
  }
  return 0;
}


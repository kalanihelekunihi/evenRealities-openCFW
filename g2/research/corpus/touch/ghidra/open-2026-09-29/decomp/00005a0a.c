
void touch_state_270a_update_lanes(int *param_1)

{
  ushort uVar1;
  char *pcVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  uint uVar7;
  
  pcVar2 = (char *)param_1[10];
  iVar4 = param_1[1];
  iVar5 = *param_1;
  *(byte *)(iVar5 + 0x23) = *(byte *)(iVar5 + 0x23) & 0xfe;
  for (uVar3 = 0;
      uVar3 <= (uint)*(ushort *)(param_1 + 0xe) * 2 &&
      (uint)*(ushort *)(param_1 + 0xe) * 2 - uVar3 != 0; uVar3 = uVar3 + 1) {
    uVar1 = *(ushort *)(iVar5 + 8);
    bVar6 = 1;
    if ((uVar3 & 1) == 0) {
      uVar1 = *(ushort *)(iVar5 + 10);
    }
    else {
      bVar6 = 2;
    }
    if ((bVar6 & *(byte *)(iVar4 + 6)) == 0) {
      uVar7 = (uint)*(ushort *)(iVar5 + 0x1e);
    }
    else {
      uVar7 = -(uint)*(ushort *)(iVar5 + 0x1e);
    }
    if (*pcVar2 != '\0') {
      *pcVar2 = *pcVar2 + -1;
    }
    if ((uint)*(ushort *)(iVar4 + 4) <= uVar7 + uVar1) {
      *pcVar2 = *(char *)(iVar5 + 0x20);
      *(byte *)(iVar4 + 6) = *(byte *)(iVar4 + 6) & ~bVar6;
    }
    if (*pcVar2 == '\0') {
      *(byte *)(iVar4 + 6) = *(byte *)(iVar4 + 6) | bVar6;
    }
    if ((bVar6 & *(byte *)(iVar4 + 6)) != 0) {
      *(byte *)(iVar5 + 0x23) = *(byte *)(iVar5 + 0x23) | 1;
    }
    if ((uVar3 & 1) != 0) {
      iVar4 = iVar4 + 10;
    }
    pcVar2 = pcVar2 + 1;
  }
  return;
}


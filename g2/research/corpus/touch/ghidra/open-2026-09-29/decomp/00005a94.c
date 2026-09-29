
void touch_select_2794_update(int *param_1)

{
  ushort uVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  char *pcVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  undefined1 *local_38;
  byte local_34;
  undefined1 auStack_30 [24];
  
  pcVar5 = (char *)param_1[10];
  iVar6 = param_1[1];
  iVar4 = *param_1;
  uVar1 = *(ushort *)(param_1 + 0xe);
  local_38 = auStack_30;
  local_34 = 0;
  if ((int)((uint)*(byte *)(iVar4 + 0x23) << 0x1f) < 0) {
    uVar8 = (uint)*(ushort *)(iVar4 + 8) - (uint)*(ushort *)(iVar4 + 0x1e);
  }
  else {
    uVar8 = (uint)*(ushort *)(iVar4 + 8) + (uint)*(ushort *)(iVar4 + 0x1e);
  }
  if (*pcVar5 != '\0') {
    *pcVar5 = *pcVar5 + -1;
  }
  bVar3 = false;
  uVar7 = (uint)uVar1;
  while (uVar7 != 0) {
    bVar2 = uVar8 < *(ushort *)(iVar6 + 4);
    *(bool *)(iVar6 + 6) = bVar2;
    bVar3 = (bool)(bVar3 | bVar2);
    iVar6 = iVar6 + 10;
    uVar7 = uVar7 - 1;
  }
  if (!bVar3) {
    *pcVar5 = *(char *)(iVar4 + 0x20);
    *(byte *)(iVar4 + 0x23) = *(byte *)(iVar4 + 0x23) & 0xfe;
  }
  if (*pcVar5 == '\0') {
    *(byte *)(iVar4 + 0x23) = *(byte *)(iVar4 + 0x23) | 1;
  }
  else if (bVar3) {
    iVar6 = param_1[1];
    uVar8 = (uint)uVar1;
    while (uVar8 != 0) {
      *(undefined1 *)(iVar6 + 6) = 0;
      iVar6 = iVar6 + 10;
      uVar8 = uVar8 - 1;
    }
  }
  if (((int)((uint)*(byte *)(iVar4 + 0x23) << 0x1f) < 0) &&
     (*(char *)((int)param_1 + 0x7b) == '\x02')) {
    touch_select_15cc_peak(&local_38,param_1);
  }
  if ((param_1[0x1c] & 0xffU) != 0) {
    touch_state_172a_sync_records(&local_38,param_1);
  }
  *(byte *)(*param_1 + 0x28) = local_34;
  for (uVar8 = 0; uVar8 < local_34; uVar8 = uVar8 + 1) {
    memcpy(*(int *)(*param_1 + 0x24) + uVar8 * 8,local_38 + uVar8 * 8,8);
  }
  return;
}


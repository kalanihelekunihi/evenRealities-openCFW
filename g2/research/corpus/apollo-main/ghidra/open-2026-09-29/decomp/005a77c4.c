
void af_cjk_align_edge_points(int param_1,byte param_2)

{
  bool bVar1;
  ushort *puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  iVar3 = param_1 + (uint)param_2 * 0x544;
  uVar5 = *(uint *)(iVar3 + 0x40);
  uVar4 = uVar5 + *(int *)(iVar3 + 0x38) * 0x2c;
  if (((param_2 == 0) && ((int)((uint)*(byte *)(param_1 + 0xab8) << 0x1f) < 0)) ||
     ((param_2 == 1 && ((int)((uint)*(byte *)(param_1 + 0xab8) << 0x1e) < 0)))) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  for (; uVar5 < uVar4; uVar5 = uVar5 + 0x2c) {
    iVar3 = *(int *)(uVar5 + 0x24);
    if (bVar1) {
      do {
        puVar2 = *(ushort **)(iVar3 + 0x24);
        while( true ) {
          if (param_2 == 0) {
            *(undefined4 *)(puVar2 + 8) = *(undefined4 *)(uVar5 + 8);
            *puVar2 = *puVar2 | 4;
          }
          else {
            *(undefined4 *)(puVar2 + 10) = *(undefined4 *)(uVar5 + 8);
            *puVar2 = *puVar2 | 8;
          }
          if (puVar2 == *(ushort **)(iVar3 + 0x28)) break;
          puVar2 = *(ushort **)(puVar2 + 0x10);
        }
        iVar3 = *(int *)(iVar3 + 0x10);
      } while (iVar3 != *(int *)(uVar5 + 0x24));
    }
    else {
      iVar6 = *(int *)(uVar5 + 8) - *(int *)(uVar5 + 4);
      do {
        puVar2 = *(ushort **)(iVar3 + 0x24);
        while( true ) {
          if (param_2 == 0) {
            *(int *)(puVar2 + 8) = iVar6 + *(int *)(puVar2 + 8);
            *puVar2 = *puVar2 | 4;
          }
          else {
            *(int *)(puVar2 + 10) = iVar6 + *(int *)(puVar2 + 10);
            *puVar2 = *puVar2 | 8;
          }
          if (puVar2 == *(ushort **)(iVar3 + 0x28)) break;
          puVar2 = *(ushort **)(puVar2 + 0x10);
        }
        iVar3 = *(int *)(iVar3 + 0x10);
      } while (iVar3 != *(int *)(uVar5 + 0x24));
    }
  }
  return;
}


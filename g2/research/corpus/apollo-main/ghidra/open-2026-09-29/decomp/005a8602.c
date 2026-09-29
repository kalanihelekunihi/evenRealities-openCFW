
void af_glyph_hints_align_edge_points(int param_1,byte param_2)

{
  int iVar1;
  ushort *puVar2;
  uint uVar3;
  uint uVar4;
  ushort *puVar5;
  
  param_1 = param_1 + (uint)param_2 * 0x544;
  uVar3 = *(uint *)(param_1 + 0x34);
  uVar4 = *(int *)(param_1 + 0x2c) * 0x2c + uVar3;
  if (param_2 == 0) {
    for (; uVar3 < uVar4; uVar3 = uVar3 + 0x2c) {
      iVar1 = *(int *)(uVar3 + 0xc);
      if (iVar1 != 0) {
        puVar2 = *(ushort **)(uVar3 + 0x24);
        puVar5 = *(ushort **)(uVar3 + 0x28);
        while( true ) {
          *(undefined4 *)(puVar2 + 8) = *(undefined4 *)(iVar1 + 8);
          *puVar2 = *puVar2 | 4;
          if (puVar2 == puVar5) break;
          puVar2 = *(ushort **)(puVar2 + 0x10);
        }
      }
    }
  }
  else {
    for (; uVar3 < uVar4; uVar3 = uVar3 + 0x2c) {
      iVar1 = *(int *)(uVar3 + 0xc);
      if (iVar1 != 0) {
        puVar2 = *(ushort **)(uVar3 + 0x24);
        puVar5 = *(ushort **)(uVar3 + 0x28);
        while( true ) {
          *(undefined4 *)(puVar2 + 10) = *(undefined4 *)(iVar1 + 8);
          *puVar2 = *puVar2 | 8;
          if (puVar2 == puVar5) break;
          puVar2 = *(ushort **)(puVar2 + 0x10);
        }
      }
    }
  }
  return;
}


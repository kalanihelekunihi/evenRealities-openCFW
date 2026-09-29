
void af_glyph_hints_save(int param_1,int param_2)

{
  byte *pbVar1;
  undefined1 *puVar2;
  byte *pbVar3;
  undefined4 *puVar4;
  
  pbVar3 = *(byte **)(param_1 + 0x1c);
  pbVar1 = pbVar3 + *(int *)(param_1 + 0x18) * 0x28;
  puVar4 = *(undefined4 **)(param_2 + 4);
  puVar2 = *(undefined1 **)(param_2 + 8);
  for (; pbVar3 < pbVar1; pbVar3 = pbVar3 + 0x28) {
    *puVar4 = *(undefined4 *)(pbVar3 + 0x10);
    puVar4[1] = *(undefined4 *)(pbVar3 + 0x14);
    if ((int)((uint)*pbVar3 << 0x1f) < 0) {
      *puVar2 = 0;
    }
    else if ((int)((uint)*pbVar3 << 0x1e) < 0) {
      *puVar2 = 2;
    }
    else {
      *puVar2 = 1;
    }
    puVar4 = puVar4 + 2;
    puVar2 = puVar2 + 1;
  }
  return;
}


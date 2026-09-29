
undefined4
gx8002_irq_compact_entry
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined1 *puVar6;
  undefined4 auStack_78 [8];
  undefined4 auStack_58 [16];
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_c = param_1;
  uStack_10 = param_2;
  uStack_14 = param_3;
  uStack_18 = param_4;
  puVar5 = auStack_58;
  for (uVar2 = 0; uVar2 < 0x35; uVar2 = uVar2 + 4) {
    *puVar5 = *(undefined4 *)(uVar2 + 0x48);
    puVar5 = puVar5 + 1;
  }
  puVar3 = auStack_78;
  puVar5 = auStack_78;
  puVar4 = auStack_78;
  for (uVar2 = 0; uVar2 < 0x1d; uVar2 = uVar2 + 4) {
    *puVar3 = *(undefined4 *)(uVar2 + 0x41c);
    puVar3 = puVar3 + 1;
  }
  iVar1 = (*(uint *)(DAT_100255bc + 0xb00) & 0x1ff) - 0x20;
  uVar2 = *(uint *)(DAT_100255c0 + iVar1 * 8);
  if (uVar2 != 0) {
    (*(code *)(uVar2 & 0xfffffffe))(iVar1,*(undefined4 *)(DAT_100255c0 + iVar1 * 8 + 4));
  }
  for (uVar2 = 0; uVar2 < 0x1d; uVar2 = uVar2 + 4) {
    *(undefined4 *)(uVar2 + 0x400) = *puVar5;
    puVar5 = puVar5 + 1;
  }
  puVar6 = (undefined1 *)((int)puVar4 + 0x20);
  puVar5 = (undefined4 *)((int)puVar4 + 0x20);
  for (uVar2 = 0; uVar2 < 0x35; uVar2 = uVar2 + 4) {
    *(undefined4 *)(uVar2 + 0x48) = *puVar5;
    puVar5 = puVar5 + 1;
  }
  return *(undefined4 *)(puVar6 + 0x38);
}


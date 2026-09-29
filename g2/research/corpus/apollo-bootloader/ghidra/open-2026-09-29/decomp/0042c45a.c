
void hw_descriptor_publish_42c45a(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_0042c6e8;
  iVar3 = *(int *)(param_1 + 4);
  uVar4 = *(int *)(param_1 + 0x850) + 1;
  puVar2 = (undefined4 *)
           (*(int *)(param_1 + 0x854) +
           (uVar4 - *(uint *)(param_1 + 0x848) * (uVar4 / *(uint *)(param_1 + 0x848))) * 0x20);
  *(undefined4 *)(DAT_0042c6e8 + iVar3 * 0x1000 + 0x128) = *puVar2;
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x2c4) = puVar2[1];
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x218) = 0;
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x21c) = puVar2[2];
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x220) = puVar2[3];
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x218) = puVar2[4];
  *(undefined4 *)(iVar1 + iVar3 * 0x1000 + 0x120) = puVar2[5];
  return;
}


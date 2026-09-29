
undefined8 FUN_004bfdf4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 *puVar5;
  
  iVar4 = *(int *)(param_1 + 4);
  uVar3 = *(int *)(param_1 + 0x850) + 1;
  puVar5 = (undefined4 *)
           (*(int *)(param_1 + 0x854) +
           (uVar3 - *(uint *)(param_1 + 0x848) * (uVar3 / *(uint *)(param_1 + 0x848))) * 0x18);
  iVar2 = FUN_004c44bc(4,*(int *)(param_1 + 4) + 0x10U & 0xff);
  iVar1 = DAT_004c0990;
  if (iVar2 == 0) {
    *(undefined4 *)(DAT_004c0990 + iVar4 * 0x1000 + 0x100) = 0;
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x108) = *puVar5;
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x10c) = puVar5[1];
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x110) = puVar5[2];
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x100) = puVar5[3];
    iVar2 = 0;
  }
  return CONCAT44(param_4,iVar2);
}


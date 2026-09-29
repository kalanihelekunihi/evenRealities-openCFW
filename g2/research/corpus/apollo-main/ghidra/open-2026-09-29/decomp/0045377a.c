
undefined8 FUN_0045377a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  uStack_28 = param_1;
  uStack_24 = param_2;
  uStack_20 = param_3;
  uStack_1c = param_4;
  for (uVar5 = 0; iVar1 = DAT_00454168, uVar5 < *(uint *)(*(int *)(DAT_00454168 + 0x10) + 0x260);
      uVar5 = uVar5 + 1) {
    if (*(char *)(*(int *)(DAT_00454168 + 0x10) + uVar5 + 0x240) == '\0') {
      for (uVar6 = 0; uVar6 < *(uint *)(*(int *)(iVar1 + 0x10) + 0x260); uVar6 = uVar6 + 1) {
        if (((*(char *)(*(int *)(iVar1 + 0x10) + uVar6 + 0x240) == '\0') && (uVar5 != uVar6)) &&
           (iVar4 = FUN_00450f00(*(int *)(iVar1 + 0x10) + uVar5 * 0x10 + 0x40,
                                 *(int *)(iVar1 + 0x10) + uVar6 * 0x10 + 0x40), iVar4 != 0)) {
          FUN_00450d8e(&uStack_28,*(int *)(iVar1 + 0x10) + uVar5 * 0x10 + 0x40,
                       *(int *)(iVar1 + 0x10) + uVar6 * 0x10 + 0x40);
          uVar2 = FUN_00450b80(&uStack_28);
          iVar4 = FUN_00450b80(*(int *)(iVar1 + 0x10) + uVar5 * 0x10 + 0x40);
          iVar3 = FUN_00450b80(*(int *)(iVar1 + 0x10) + uVar6 * 0x10 + 0x40);
          if (uVar2 < (uint)(iVar3 + iVar4)) {
            FUN_004530fc(*(int *)(iVar1 + 0x10) + uVar5 * 0x10 + 0x40,&uStack_28);
            *(undefined1 *)(*(int *)(iVar1 + 0x10) + uVar6 + 0x240) = 1;
          }
        }
      }
    }
  }
  return CONCAT44(uStack_24,uStack_28);
}


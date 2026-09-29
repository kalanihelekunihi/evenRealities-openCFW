
undefined4 FUN_005b7556(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined2 auStack_30 [2];
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  iVar1 = DAT_005b7604;
  FUN_0043c0e4(auStack_30,0x24,0);
  if ((*(int *)(iVar1 + 0x1c) == 0) || (*(int *)(iVar1 + 0x24) == 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    FUN_0058c426(*(undefined4 *)(iVar1 + 0x24),200,0);
    if ((*(int *)(iVar1 + 0x2c) != 0) &&
       (iVar3 = FUN_0043e0e0(*(undefined4 *)(iVar1 + 0x2c),1), iVar3 == 0)) {
      FUN_0058c426(*(undefined4 *)(iVar1 + 0x2c),200,0);
    }
    FUN_0058c238(*(undefined4 *)(iVar1 + 8),200,0);
    if (*(char *)(iVar1 + 0x8d) != '\0') {
      FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x20),1);
    }
    auStack_30[0] = 300;
    uStack_2c = 0;
    uStack_28 = 0;
    uStack_24 = 0;
    uStack_20 = 0;
    uStack_1c = 0x240;
    uStack_18 = FUN_0043fd9e(*(undefined4 *)(iVar1 + 0x7c));
    uStack_14 = 0x120;
    uStack_10 = FUN_0043fdda(*(undefined4 *)(iVar1 + 0x7c));
    FUN_005b7704(*(undefined4 *)(iVar1 + 0x1c),auStack_30,PTR_FUN_005b7518_1_005b7680);
    *(undefined1 *)(iVar1 + 0x98) = 1;
    uVar2 = 0;
  }
  return uVar2;
}


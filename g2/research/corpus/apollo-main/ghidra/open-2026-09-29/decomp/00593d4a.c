
void FUN_00593d4a(undefined4 param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined4 local_9c [32];
  
  FUN_0043c0e4(local_9c,0x80,0);
  uVar5 = FUN_00593c34(local_9c,0x20,param_1);
  for (uVar6 = 0; uVar4 = DAT_005947c0, iVar3 = DAT_005947b8, iVar2 = DAT_00594330,
      uVar1 = DAT_00594304, uVar6 < uVar5; uVar6 = uVar6 + 1) {
    FUN_004b4728(uVar6 * 9 + DAT_005947b8,DAT_005947bc,local_9c[uVar6]);
    *(undefined1 *)(uVar6 * 9 + iVar3 + 8) = 0x20;
  }
  if (uVar5 == 0) {
    FUN_0047da78(*(undefined4 *)(DAT_00594330 + 0x24));
    FUN_0047da78(&DAT_00593e08);
    FUN_004733ee(*(undefined4 *)(iVar2 + 0x24));
    FUN_004733ee(&DAT_00593e08);
  }
  else {
    FUN_0047da78(*(undefined4 *)(DAT_00594330 + 0x20),DAT_00594304,DAT_005947c0,uVar5 * 9,
                 DAT_005947b8);
    FUN_0047da78(&DAT_00593e08);
    FUN_004733ee(*(undefined4 *)(iVar2 + 0x20),uVar1,uVar4,uVar5 * 9,iVar3);
    FUN_004733ee(&DAT_00593e08);
  }
  return;
}


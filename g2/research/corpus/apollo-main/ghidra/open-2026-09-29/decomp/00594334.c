
void FUN_00594334(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  undefined1 auStack_3c [20];
  undefined1 local_28;
  
  iVar1 = DAT_005947e8;
  uVar3 = FUN_00454f38(DAT_005947e8,0x28,0);
  uVar2 = DAT_005947ec;
  FUN_004733ee(DAT_005947ec);
  FUN_0047da78(uVar2);
  uVar2 = DAT_005947f0;
  FUN_0044b728(DAT_005947f0,0x80,DAT_00594810,DAT_0059480c,0x14,DAT_00594808,DAT_00594804,
               DAT_00594800,DAT_005947fc,DAT_005947f8,DAT_005947f4);
  FUN_004733ee(&DAT_0059449c,uVar2);
  FUN_0047da78(uVar2);
  FUN_0047da78(&DAT_005944a0);
  for (uVar6 = 0; uVar4 = DAT_0059481c, uVar6 < uVar3; uVar6 = uVar6 + 1) {
    FUN_0043c0e4(auStack_3c,0x15,0);
    iVar7 = *(int *)(iVar1 + uVar6 * 0x24);
    FUN_0044b5a0(auStack_3c,*(undefined4 *)(uVar6 * 0x24 + iVar1 + 4),0x14);
    local_28 = 0;
    uVar4 = *(undefined4 *)(iVar7 + 0x30);
    uVar5 = FUN_005942c8(*(undefined1 *)(uVar6 * 0x24 + iVar1 + 0xc));
    FUN_0044b728(uVar2,0x80,DAT_00594818,*(undefined4 *)(iVar1 + uVar6 * 0x24 + 8),0x14,auStack_3c,
                 uVar5,*(undefined4 *)(uVar6 * 0x24 + iVar1 + 0x10),uVar4,
                 (uint)*(ushort *)(uVar6 * 0x24 + iVar1 + 0x20) << 2,
                 *(undefined2 *)(uVar6 * 0x24 + iVar1 + 0x20));
    FUN_004733ee(&DAT_0059449c,uVar2);
    FUN_0047da78(uVar2);
    FUN_0047da78(&DAT_005944a0);
  }
  FUN_004733ee(DAT_0059481c);
  FUN_0047da78(uVar4);
  uVar3 = uxTaskGetNumberOfTasks();
  if (0x28 < uVar3) {
    FUN_004733ee(DAT_00594820,0x28);
  }
  return;
}


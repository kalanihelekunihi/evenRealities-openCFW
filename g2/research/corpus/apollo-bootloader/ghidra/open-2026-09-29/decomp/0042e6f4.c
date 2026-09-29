
undefined8 FUN_0042e6f4(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = 0xffffffff;
  uVar8 = param_1;
  FUN_0041b3e4(0);
  puVar2 = DAT_0042e888;
  uVar7 = *DAT_0042e888;
  FUN_0041b3fc();
  puVar1 = DAT_0042e85c;
  if ((param_1 & 0xff000000) == 0xff000000) {
    uVar7 = param_1 & 0xffffff;
  }
  iVar4 = FUN_004166aa(*DAT_0042e85c,0xffffffff);
  if (iVar4 != 0) {
    uVar8 = 0xb8;
    param_2 = DAT_0042e88c;
    elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e890,0xb8,DAT_0042e88c,param_3,param_4);
  }
  for (iVar4 = 0; iVar3 = DAT_0042e894, iVar4 < 0x40; iVar4 = iVar4 + 1) {
    if (*(int *)(DAT_0042e894 + iVar4 * 4) != 0) {
      if (uVar7 < *(uint *)(DAT_0042e894 + iVar4 * 4 + 0x200)) {
        *(uint *)(DAT_0042e894 + iVar4 * 4 + 0x200) =
             *(int *)(DAT_0042e894 + iVar4 * 4 + 0x200) - uVar7;
      }
      else {
        *(undefined4 *)(DAT_0042e894 + iVar4 * 4 + 0x200) = 0;
      }
      if (*(int *)(iVar3 + iVar4 * 4 + 0x200) == 0) {
        uVar5 = *(undefined4 *)(iVar3 + iVar4 * 4);
        *(undefined4 *)(iVar3 + iVar4 * 4) = 0;
        event_callback_enqueue_42e686(uVar5,*(undefined4 *)(iVar3 + iVar4 * 4 + 0x100),1);
      }
    }
  }
  for (iVar4 = 0; iVar4 < 0x40; iVar4 = iVar4 + 1) {
    if ((*(int *)(DAT_0042e894 + iVar4 * 4) != 0) &&
       (*(uint *)(DAT_0042e894 + iVar4 * 4 + 0x200) < uVar6)) {
      uVar6 = *(uint *)(DAT_0042e894 + iVar4 * 4 + 0x200);
    }
  }
  iVar4 = FUN_00416710(*puVar1);
  if (iVar4 != 0) {
    uVar8 = 0xd5;
    param_2 = DAT_0042e898;
    elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e890);
  }
  if ((uVar6 != 0x7fffffff) && (uVar6 != 0)) {
    FUN_0041b3e4();
    *puVar2 = uVar6;
    FUN_0041b3fc();
    iVar4 = bl_runtime_submit(*DAT_0042e850,uVar6);
    if (iVar4 != 0) {
      uVar8 = 0xe1;
      param_2 = DAT_0042e89c;
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e890,0xe1,DAT_0042e89c,uVar6,iVar4);
    }
    uVar5 = FUN_004160e8();
    *DAT_0042e8a0 = uVar5;
  }
  return CONCAT44(param_2,uVar8);
}


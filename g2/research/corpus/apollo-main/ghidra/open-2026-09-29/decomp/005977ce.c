
undefined8 td_state_sync(undefined4 *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  iVar1 = DAT_00597c08;
  iVar2 = DAT_00597c08 + 0x9b9c;
  if (param_1 == (undefined4 *)0x0) {
    uVar3 = 0xffffffff;
  }
  else {
    FUN_00439be4(iVar2,DAT_00597c08 + 0x9560,0x63c);
    uVar7 = *(uint *)(iVar1 + 0x9ba4);
    if (10 < uVar7) {
      uVar7 = 10;
    }
    *(undefined4 *)(iVar1 + 0x9560) = *param_1;
    *(undefined4 *)(iVar1 + 0x9564) = param_1[1];
    *(uint *)(iVar1 + 0x9568) = (uint)*(ushort *)(param_1 + 2);
    if (10 < *(uint *)(iVar1 + 0x9568)) {
      *(undefined4 *)(iVar1 + 0x9568) = 10;
    }
    *(undefined1 *)(iVar1 + 0xa1d9) = 1;
    for (uVar8 = 0; uVar8 < *(uint *)(iVar1 + 0x9568); uVar8 = uVar8 + 1) {
      iVar4 = uVar8 * 0x90 + iVar1;
      iVar6 = 0;
      for (uVar5 = 0; uVar5 < uVar7; uVar5 = uVar5 + 1) {
        if (*(int *)(iVar2 + uVar5 * 0x90 + 0x9c) == param_1[uVar8 * 0x22 + 3]) {
          iVar6 = uVar5 * 0x90 + iVar2 + 0x9c;
          break;
        }
      }
      FUN_00439be4(iVar4 + 0x95fc,param_1 + uVar8 * 0x22 + 3,0x88);
      if (iVar6 == 0) {
        *(undefined1 *)(iVar4 + 0x9688) = 0;
        *(undefined4 *)(iVar4 + 0x9684) = 0;
      }
      else {
        if ((*(char *)(iVar4 + 0x9682) == '\x01') || (*(char *)(iVar4 + 0x9682) == '\x02')) {
          *(undefined4 *)(iVar4 + 0x9684) = *(undefined4 *)(iVar6 + 0x88);
        }
        else {
          *(undefined4 *)(iVar4 + 0x9684) = 0;
        }
        if (*(char *)(iVar4 + 0x9682) == '\x02') {
          *(undefined1 *)(iVar4 + 0x9688) = *(undefined1 *)(iVar6 + 0x8c);
        }
        else {
          *(undefined1 *)(iVar4 + 0x9688) = 0;
        }
      }
    }
    uVar3 = 0;
  }
  return CONCAT44(iVar2,uVar3);
}



/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005b30c8(char param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  int iVar2;
  ushort *puVar3;
  short *psVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  ushort *puVar10;
  
  iVar9 = _DAT_005b3514;
  puVar3 = (ushort *)FUN_005b43e8();
  psVar4 = (short *)func_0x005b4766();
  puVar10 = (ushort *)0x0;
  if (param_1 == '\x03') {
    if (*_DAT_005b3518 == '\x01') {
      if (*psVar4 != 0) {
        puVar10 = (ushort *)(psVar4 + 1);
      }
    }
    else if (((*puVar3 != 0) && (*(int *)(iVar9 + 0x84) != -1)) &&
            (*(int *)(iVar9 + 0x84) < (int)(uint)*puVar3)) {
      puVar10 = puVar3 + *(int *)(iVar9 + 0x84) * 0x44 + 5;
    }
    FUN_0043ded4(*(undefined4 *)(iVar9 + 4),1);
  }
  else if (param_1 == '\0') {
    if (*psVar4 != 0) {
      puVar10 = (ushort *)(psVar4 + 1);
    }
  }
  else if (param_1 == '\x01') {
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      param_2 = 0x1de;
      FUN_0043d574(3,PTR_s_conversate_ui_005b3528,PTR_s_D__01_workspace_s200_ap510b_iar__005b3524,
                   PTR_s_conversate_ui_action_display_loa_005b3558,0x1de,
                   PTR_s_already_in_loading__return_005b3554,param_4);
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__conversate_ui_already_in_loadin_005b355c,
                          PTR_s__conversate_ui_already_in_loadin_005b355c);
    }
    goto LAB_005b3246;
  }
  uVar5 = FUN_0043de82(*_DAT_005b3530);
  *(undefined4 *)(iVar9 + 0xc) = uVar5;
  FUN_0043f4c0(*(undefined4 *)(iVar9 + 0xc),0x240,0x120);
  FUN_0043f09a(*(undefined4 *)(iVar9 + 0xc),0,0);
  FUN_0044129e(*(undefined4 *)(iVar9 + 0xc),0,0);
  FUN_0044131c(*(undefined4 *)(iVar9 + 0xc),0,0);
  FUN_0044146a(*(undefined4 *)(iVar9 + 0xc),0,0);
  func_0x005b22bc(*(undefined4 *)(iVar9 + 0xc),0,0);
  FUN_0043dfa4(*(undefined4 *)(iVar9 + 0xc),0x10);
  uVar5 = FUN_00499416(*(undefined4 *)(iVar9 + 0xc));
  FUN_0043f4c0(uVar5,0x240,0x3fffffff);
  FUN_0043f6b8(uVar5,9,0,0);
  uVar6 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar5,uVar6,0);
  FUN_0044143e(uVar5,*_DAT_005b3538,0);
  FUN_0044145a(uVar5,2,0);
  FUN_00499678(uVar5,0);
  puVar1 = PTR_s_ID_CONVERSATE_START_005b3548;
  uVar6 = FUN_00460084(PTR_s_ID_CONVERSATE_START_005b3548);
  uVar6 = FUN_0045fffe(puVar1,uVar6);
  iVar2 = _DAT_005b354c;
  iVar7 = FUN_0044b728(_DAT_005b354c,200,0x5b34b0,uVar6);
  if (puVar10 != (ushort *)0x0) {
    *(undefined1 *)(iVar2 + iVar7) = 10;
    puVar1 = PTR_s_ID_CONVERSATE_PREP_NOTES_NAME_005b3550;
    iVar7 = iVar7 + 1;
    uVar6 = FUN_00460084(PTR_s_ID_CONVERSATE_PREP_NOTES_NAME_005b3550);
    uVar6 = FUN_0045fffe(puVar1,uVar6);
    iVar8 = FUN_0044b728(iVar2 + iVar7,200 - iVar7,uVar6,puVar10);
    iVar7 = iVar8 + iVar7;
  }
  *(undefined1 *)(iVar2 + iVar7) = 0;
  FUN_0049942e(uVar5,iVar2);
  FUN_0058c238(*(undefined4 *)(iVar9 + 0xc),0xfa,0);
LAB_005b3246:
  return (ulonglong)param_2 << 0x20;
}


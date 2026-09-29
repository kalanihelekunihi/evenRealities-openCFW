
void FUN_0043d574(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  bool bVar1;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  undefined1 *puVar8;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38 [4];
  undefined4 uStack_28;
  
  uVar6 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar6 = getCurrentExceptionNumber();
    uVar6 = uVar6 & 0x1ff;
  }
  if (uVar6 == 0) {
    uStack_28 = param_4;
    if (5 < param_1) {
      if (*DAT_0043daa0 == 0) {
        local_38[0] = 0x23c;
        local_3c = DAT_0043dc94;
        local_40 = DAT_0043dab8;
        FUN_0043d574(0,PTR_DAT_0043da8c,DAT_0043da88,DAT_0043dc94,0x23c,DAT_0043daac);
        do {
          FUN_0044b0ae();
        } while( true );
      }
      (*(code *)*DAT_0043daa0)(DAT_0043dab8,DAT_0043dc94,0x23c);
    }
    pbVar2 = DAT_0043da70;
    if ((((DAT_0043da70[0xf1] != 0) && (param_1 <= *DAT_0043da70)) &&
        (uVar6 = FUN_0043d4b0(param_2), param_1 <= uVar6)) &&
       (iVar3 = FUN_0044b63a(param_2,pbVar2 + 1), iVar3 != 0)) {
      uVar6 = FUN_0044a43c(param_2);
      iVar7 = 0;
      FUN_0043c0e4(&local_40,6,0);
      FUN_0043c0e4(local_38,0x10,0);
      puVar8 = &stack0x00000008;
      FUN_0043d416();
      iVar3 = DAT_0043dc8c;
      if (pbVar2[0xf5] != 0) {
        iVar4 = elog_strcpy(0,DAT_0043dc8c,&DAT_0043d978);
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,*(undefined4 *)(DAT_0043dca4 + (uint)param_1 * 4));
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = get_fmt_enabled(param_1,1);
      if (iVar3 != 0) {
        iVar3 = elog_strcpy(iVar7,DAT_0043dc8c + iVar7,
                            *(undefined4 *)(DAT_0043dca8 + (uint)param_1 * 4));
        iVar7 = iVar3 + iVar7;
      }
      iVar4 = get_fmt_enabled(param_1,2);
      iVar3 = DAT_0043dc8c;
      if (iVar4 != 0) {
        iVar4 = elog_strcpy(iVar7,DAT_0043dc8c + iVar7,param_2);
        iVar4 = iVar4 + iVar7;
        if (uVar6 < 0x10) {
          FUN_0043c0e4(local_38,0xf - uVar6,0x20);
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,local_38);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043d9e8);
        iVar7 = iVar7 + iVar4;
      }
      iVar4 = get_fmt_enabled(param_1,0x1c);
      iVar3 = DAT_0043dc8c;
      if (iVar4 != 0) {
        iVar4 = elog_strcpy(iVar7,DAT_0043dc8c + iVar7,&DAT_0043d9ec);
        iVar4 = iVar4 + iVar7;
        iVar7 = get_fmt_enabled(param_1,4);
        if (iVar7 != 0) {
          uVar5 = FUN_0044aaa8();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
          iVar7 = get_fmt_enabled(param_1,0x18);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043d9e8);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = get_fmt_enabled(param_1,8);
        if (iVar7 != 0) {
          uVar5 = FUN_0044ab14();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
          iVar7 = get_fmt_enabled(param_1,0x10);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043d9e8);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = get_fmt_enabled(param_1,0x10);
        if (iVar7 != 0) {
          uVar5 = FUN_0044ab1c();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043da60);
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = FUN_0043da0a(param_1,0x20,param_3);
      if (((iVar3 != 0) || (iVar3 = FUN_0043da0a(param_1,0x40,param_4), iVar3 != 0)) ||
         (iVar3 = FUN_0043d9f0(param_1,0x80,param_5), iVar3 != 0)) {
        iVar3 = DAT_0043dc8c;
        iVar4 = elog_strcpy(iVar7,DAT_0043dc8c + iVar7,&DAT_0043da64);
        iVar4 = iVar4 + iVar7;
        iVar7 = FUN_0043da0a(param_1,0x20,param_3);
        if (iVar7 != 0) {
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,param_3);
          iVar4 = iVar7 + iVar4;
          iVar7 = FUN_0043da0a(param_1,0x40,param_4);
          if (iVar7 == 0) {
            iVar7 = FUN_0043d9f0(param_1,0x80,param_5);
            if (iVar7 != 0) {
              iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043d9e8);
              iVar4 = iVar7 + iVar4;
            }
          }
          else {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043da68);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = FUN_0043d9f0(param_1,0x80,param_5);
        if (iVar7 != 0) {
          FUN_0044b728(&local_40,5,&DAT_0043da6c,param_5);
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&local_40);
          iVar4 = iVar7 + iVar4;
          iVar7 = FUN_0043da0a(param_1,0x40,param_4);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043d9e8);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = FUN_0043da0a(param_1,0x40,param_4);
        if (iVar7 != 0) {
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,param_4);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043da74);
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = DAT_0043dc8c;
      iVar4 = FUN_0044b76c(DAT_0043dc8c + iVar7,0x400 - iVar7,param_6,puVar8);
      if (((uint)(iVar4 + iVar7) < 0x401) && (-1 < iVar4)) {
        iVar4 = iVar4 + iVar7;
      }
      else {
        iVar4 = 0x400;
      }
      if (0x400 < iVar4 + 5U) {
        iVar4 = 0x3fb;
      }
      if (pbVar2[0x20] != 0) {
        *(undefined1 *)(iVar3 + iVar4) = 0;
        iVar7 = FUN_0044b63a(iVar3,pbVar2 + 0x20);
        if (iVar7 == 0) {
          FUN_0043d438();
          return;
        }
      }
      if (pbVar2[0xf5] != 0) {
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,DAT_0043dcac);
        iVar4 = iVar7 + iVar4;
      }
      iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_0043da80);
      FUN_0044aa80(iVar3,iVar7 + iVar4,param_1);
      FUN_0043d438();
    }
  }
  return;
}


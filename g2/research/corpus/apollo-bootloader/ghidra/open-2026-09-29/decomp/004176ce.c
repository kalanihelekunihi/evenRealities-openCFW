
void elog_output(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
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
      if (*DAT_00417be8 == 0) {
        local_38[0] = 0x23c;
        local_3c = DAT_00417c14;
        local_40 = DAT_00417c00;
        elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417c14,0x23c,DAT_00417bf4);
        do {
          FUN_0041ac8a();
        } while( true );
      }
      (*(code *)*DAT_00417be8)(DAT_00417c00,DAT_00417c14,0x23c);
    }
    pbVar2 = DAT_00417bcc;
    if ((((DAT_00417bcc[0xf1] != 0) && (param_1 <= *DAT_00417bcc)) &&
        (uVar6 = FUN_0041760a(param_2), param_1 <= uVar6)) &&
       (iVar3 = FUN_00415ffa(param_2,pbVar2 + 1), iVar3 != 0)) {
      uVar6 = FUN_0041b120(param_2);
      iVar7 = 0;
      FUN_0041560c(&local_40,6,0);
      FUN_0041560c(local_38,0x10,0);
      puVar8 = &stack0x00000008;
      FUN_00417570();
      iVar3 = DAT_00417c10;
      if (pbVar2[0xf5] != 0) {
        iVar4 = elog_strcpy(0,DAT_00417c10,&DAT_00417ad0);
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,*(undefined4 *)(DAT_00417c18 + (uint)param_1 * 4));
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = get_fmt_enabled(param_1,1);
      if (iVar3 != 0) {
        iVar3 = elog_strcpy(iVar7,DAT_00417c10 + iVar7,
                            *(undefined4 *)(DAT_00417c1c + (uint)param_1 * 4));
        iVar7 = iVar3 + iVar7;
      }
      iVar4 = get_fmt_enabled(param_1,2);
      iVar3 = DAT_00417c10;
      if (iVar4 != 0) {
        iVar4 = elog_strcpy(iVar7,DAT_00417c10 + iVar7,param_2);
        iVar4 = iVar4 + iVar7;
        if (uVar6 < 0x10) {
          FUN_0041560c(local_38,0xf - uVar6,0x20);
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,local_38);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417b40);
        iVar7 = iVar7 + iVar4;
      }
      iVar4 = get_fmt_enabled(param_1,0x1c);
      iVar3 = DAT_00417c10;
      if (iVar4 != 0) {
        iVar4 = elog_strcpy(iVar7,DAT_00417c10 + iVar7,&DAT_00417b44);
        iVar4 = iVar4 + iVar7;
        iVar7 = get_fmt_enabled(param_1,4);
        if (iVar7 != 0) {
          uVar5 = FUN_0041a6aa();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
          iVar7 = get_fmt_enabled(param_1,0x18);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417b40);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = get_fmt_enabled(param_1,8);
        if (iVar7 != 0) {
          uVar5 = FUN_0041a6f0();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
          iVar7 = get_fmt_enabled(param_1,0x10);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417b40);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = get_fmt_enabled(param_1,0x10);
        if (iVar7 != 0) {
          uVar5 = FUN_0041a6f8();
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,uVar5);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417bb8);
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = FUN_00417b62(param_1,0x20,param_3);
      if (((iVar3 != 0) || (iVar3 = FUN_00417b62(param_1,0x40,param_4), iVar3 != 0)) ||
         (iVar3 = FUN_00417b48(param_1,0x80,param_5), iVar3 != 0)) {
        iVar3 = DAT_00417c10;
        iVar4 = elog_strcpy(iVar7,DAT_00417c10 + iVar7,&DAT_00417bbc);
        iVar4 = iVar4 + iVar7;
        iVar7 = FUN_00417b62(param_1,0x20,param_3);
        if (iVar7 != 0) {
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,param_3);
          iVar4 = iVar7 + iVar4;
          iVar7 = FUN_00417b62(param_1,0x40,param_4);
          if (iVar7 == 0) {
            iVar7 = FUN_00417b48(param_1,0x80,param_5);
            if (iVar7 != 0) {
              iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417b40);
              iVar4 = iVar7 + iVar4;
            }
          }
          else {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417bc0);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = FUN_00417b48(param_1,0x80,param_5);
        if (iVar7 != 0) {
          FUN_0041b218(&local_40,5,&DAT_00417bc4,param_5);
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&local_40);
          iVar4 = iVar7 + iVar4;
          iVar7 = FUN_00417b62(param_1,0x40,param_4);
          if (iVar7 != 0) {
            iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417b40);
            iVar4 = iVar7 + iVar4;
          }
        }
        iVar7 = FUN_00417b62(param_1,0x40,param_4);
        if (iVar7 != 0) {
          iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,param_4);
          iVar4 = iVar7 + iVar4;
        }
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417bc8);
        iVar7 = iVar7 + iVar4;
      }
      iVar3 = DAT_00417c10;
      iVar4 = FUN_0041b25c(DAT_00417c10 + iVar7,0x400 - iVar7,param_6,puVar8);
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
        iVar7 = FUN_00415ffa(iVar3,pbVar2 + 0x20);
        if (iVar7 == 0) {
          FUN_00417592();
          return;
        }
      }
      if (pbVar2[0xf5] != 0) {
        iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,DAT_00417c20);
        iVar4 = iVar7 + iVar4;
      }
      iVar7 = elog_strcpy(iVar4,iVar3 + iVar4,&DAT_00417bd0);
      FUN_0041a692(iVar3,iVar7 + iVar4,param_1);
      FUN_00417592();
    }
  }
  return;
}


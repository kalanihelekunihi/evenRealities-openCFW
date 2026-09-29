
undefined4 FUN_004b092a(uint *param_1,undefined1 *param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  undefined1 auStack_2c [8];
  int local_24;
  int local_20;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  iVar1 = FUN_004c791a();
  FUN_0048949c(auStack_2c,0x10);
  local_24 = (param_1[1] & 0xffff) - 1;
  local_20 = (param_1[1] >> 0x10) - 1;
  if (param_2 == (undefined1 *)0x0) {
    param_2 = auStack_2c;
  }
  iVar2 = FUN_00450bcc(&local_3c,param_2,auStack_2c);
  if (iVar2 == 0) {
    return 0;
  }
  if ((local_34 - local_3c < 1) || (local_30 - local_38 < 1)) {
    return 0;
  }
  if ((((param_1 == (uint *)0x0) || (param_1[4] == 0)) || ((param_1[1] & 0xffff) == 0)) ||
     (param_1[1] >> 0x10 == 0)) {
    FUN_0044d25c(3,DAT_004b1054,0x14c,DAT_004b1074,DAT_004b1070);
    return 0;
  }
  iVar2 = FUN_004b064e(*param_1 >> 8 & 0xff);
  uVar6 = param_1[4];
  if ((iVar2 != -1) || (param_3 != '\x01')) goto LAB_004b0a20;
  if ((*param_1 & 0xffff) >> 8 == 0x14) {
    iVar2 = 4;
    goto LAB_004b0a20;
  }
  if (3 < ((*param_1 & 0xffff) >> 8) - 7) goto LAB_004b0a20;
  uVar3 = (*param_1 & 0xffff) >> 8;
  if (uVar3 == 7) {
    iVar5 = 2;
    iVar2 = 0xb;
  }
  else if (uVar3 < 7) {
LAB_004b0a16:
    iVar5 = 0x100;
    iVar2 = 9;
  }
  else if (uVar3 == 9) {
    iVar5 = 0x10;
    iVar2 = 0x35;
  }
  else {
    if (8 < uVar3) goto LAB_004b0a16;
    iVar5 = 4;
    iVar2 = 0x31;
  }
  uVar6 = uVar6 + iVar5 * 4;
LAB_004b0a20:
  if (iVar2 == -1) {
    FUN_0044d25c(3,DAT_004b1054,0x179,DAT_004b1074,DAT_004b1078);
    uVar4 = 0;
  }
  else {
    FUN_004b07de(iVar1);
    iVar5 = FUN_0051419a(0,1);
    if (iVar5 == 0) {
      iVar5 = FUN_005144fa();
      if (iVar5 == 0) {
        FUN_00514384(iVar1 + 0x90);
        FUN_005143d4(iVar1 + 0x90,100);
      }
      else if (iVar5 != iVar1 + 0x90) {
        FUN_004b0886(iVar1);
        FUN_0044d25c(3,DAT_004b1054,399,DAT_004b1074,DAT_004b1080);
        return 0;
      }
      iVar5 = FUN_0051418e();
      if ((iVar5 < 0) && (iVar5 = FUN_00514194(), iVar5 == 0)) {
        FUN_00454746(iVar1 + 0x58,0,0x1c);
        FUN_00454746(iVar1 + 0x74,0,0x10);
        FUN_004b075e(iVar1);
      }
      if ((((param_1[4] != *(uint *)(iVar1 + 0x68)) ||
           ((param_1[1] & 0xffff) != (*(uint *)(iVar1 + 0x5c) & 0xffff))) ||
          (param_1[1] >> 0x10 != *(uint *)(iVar1 + 0x5c) >> 0x10)) ||
         (((*param_1 & 0xffff) >> 8 != (*(uint *)(iVar1 + 0x58) & 0xffff) >> 8 ||
          ((param_1[2] & 0xffff) != (*(uint *)(iVar1 + 0x60) & 0xffff))))) {
        FUN_004b1298(0,uVar6,param_1[1] & 0xffff,param_1[1] >> 0x10,iVar2,param_1[2] & 0xffff,0);
        FUN_00439c04(iVar1 + 0x58,param_1,0x1c);
      }
      FUN_004b077e(iVar1,&local_3c,0);
      uVar4 = 1;
    }
    else {
      FUN_0044d25c(3,DAT_004b1054,0x181,DAT_004b1074,DAT_004b107c,iVar5);
      uVar4 = 0;
    }
  }
  return uVar4;
}


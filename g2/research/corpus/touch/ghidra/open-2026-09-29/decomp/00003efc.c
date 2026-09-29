
char gesture_policy_helper_0bfc(int param_1,undefined1 param_2,undefined4 param_3)

{
  byte bVar1;
  undefined1 uVar2;
  char cVar3;
  uint uVar4;
  uint extraout_r1;
  uint extraout_r1_00;
  uint extraout_r1_01;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  
  if (param_1 == 0) {
    return '\0';
  }
  bVar1 = *(byte *)(param_1 + 0x48);
  iVar7 = (bVar1 + 6) * 8;
  *(undefined1 *)(iVar7 + param_1) = param_2;
  *(undefined4 *)(param_1 + iVar7 + 4) = param_3;
  __aeabi_idivmod(bVar1 + 1,3);
  *(char *)(param_1 + 0x48) = (char)extraout_r1;
  if (*(byte *)(param_1 + 0x49) < 3) {
    *(byte *)(param_1 + 0x49) = *(byte *)(param_1 + 0x49) + 1;
  }
  if (*(byte *)(param_1 + 0x49) < 2) {
    return '\0';
  }
  __aeabi_idivmod((extraout_r1 & 0xff) + 1,3);
  __aeabi_idivmod((extraout_r1 & 0xff) + 2,3);
  iVar7 = (uint)*(byte *)(((extraout_r1_01 & 0xff) + 6) * 8 + param_1) -
          (uint)*(byte *)(((extraout_r1_00 & 0xff) + 6) * 8 + param_1);
  if (iVar7 < 4) {
    if (iVar7 < -3) {
      iVar6 = -1;
    }
    else {
      iVar6 = 0;
    }
  }
  else {
    iVar6 = 1;
  }
  iVar5 = (int)*(char *)(param_1 + 0x4b);
  if (iVar5 != 0) {
    if (iVar6 == 0) goto LAB_00003f96;
    if (iVar5 != iVar6) {
      *(undefined1 *)(param_1 + 0x4a) = 0;
      logger_stub(DAT_00004044,iVar5,iVar6,DAT_00004040);
    }
  }
  if (iVar6 != 0) {
    *(char *)(param_1 + 0x4b) = (char)iVar6;
  }
LAB_00003f96:
  iVar6 = *(int *)(param_1 + ((extraout_r1_01 & 0xff) + 6) * 8 + 4);
  iVar5 = *(int *)(param_1 + ((extraout_r1_00 & 0xff) + 6) * 8 + 4);
  uVar8 = iVar6 - iVar5;
  if (iVar6 == iVar5) {
    cVar3 = *(char *)(param_1 + 0x4a);
    if (cVar3 == '\0') {
      cVar3 = '\x01';
    }
  }
  else {
    uVar4 = __aeabi_uidiv((iVar7 + (iVar7 >> 0x1f) ^ iVar7 >> 0x1f) * 100 + (uVar8 >> 1),uVar8);
    if (0xff < uVar4) {
      uVar4 = 0xff;
    }
    if (*(byte *)(param_1 + 0x4a) == 0) {
      *(char *)(param_1 + 0x4a) = (char)uVar4;
    }
    else {
      uVar2 = __aeabi_idiv((uVar4 & 0xff) * 4 + (uint)*(byte *)(param_1 + 0x4a) * 6,10);
      *(undefined1 *)(param_1 + 0x4a) = uVar2;
    }
    logger_stub(DAT_00004048,uVar4 & 0xff,*(undefined1 *)(param_1 + 0x4a),iVar7,uVar8,DAT_00004040);
    cVar3 = *(char *)(param_1 + 0x4a);
  }
  return cVar3;
}



int FUN_004cc04a(int param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;
  char *pcVar8;
  int local_40;
  char *local_3c;
  int local_38;
  int local_30;
  undefined4 *local_2c;
  undefined4 local_28;
  
  iVar6 = DAT_004ccb74;
  pcVar8 = (char *)*param_3;
  *(undefined4 *)(param_2 + 0x18) = *(undefined4 *)(param_1 + 0x20);
  *(undefined4 *)(param_2 + 0x1c) = *(undefined4 *)(param_1 + 0x24);
  local_30 = param_1;
  local_2c = param_3;
  local_28 = param_4;
  if (*pcVar8 == '\0') {
    return -0x16;
  }
LAB_004cc07c:
  do {
    while( true ) {
      iVar2 = FUN_004cae98(iVar6);
      if (iVar2 == 2) {
        iVar2 = FUN_00541b52(pcVar8,&DAT_004cc1d4);
        pcVar8 = pcVar8 + iVar2;
      }
      iVar2 = FUN_00541b30(pcVar8,&DAT_004cc1d4);
      if ((iVar2 != 1) || (iVar3 = FUN_004751c8(pcVar8,&DAT_004cc1f0,1), iVar3 != 0)) break;
      pcVar8 = pcVar8 + 1;
    }
    if ((iVar2 == 2) && (iVar3 = FUN_004751c8(pcVar8,&DAT_004cc1f4,2), iVar3 == 0)) {
      return -0x16;
    }
    pcVar7 = pcVar8 + iVar2;
    iVar3 = 1;
    while( true ) {
      iVar5 = FUN_00541b52(pcVar7,&DAT_004cc1d4);
      pcVar7 = pcVar7 + iVar5;
      iVar5 = FUN_00541b30(pcVar7,&DAT_004cc1d4);
      if (iVar5 == 0) break;
      if ((iVar5 != 1) || (iVar4 = FUN_004751c8(pcVar7,&DAT_004cc1f0,1), iVar4 != 0)) {
        if ((iVar5 == 2) && (iVar4 = FUN_004751c8(pcVar7,&DAT_004cc1f4,2), iVar4 == 0)) {
          iVar3 = iVar3 + -1;
          if (iVar3 == 0) {
            pcVar8 = pcVar7 + 2;
            goto LAB_004cc07c;
          }
        }
        else {
          iVar3 = iVar3 + 1;
        }
      }
      pcVar7 = pcVar7 + iVar5;
    }
    if (*pcVar8 == '\0') {
      return iVar6;
    }
    *local_2c = pcVar8;
    iVar3 = FUN_004cae98(iVar6);
    if (iVar3 != 2) {
      return -0x14;
    }
    iVar3 = FUN_004caeb0(iVar6);
    if (iVar3 != 0x3ff) {
      uVar1 = FUN_004caeb0(iVar6);
      iVar6 = FUN_004cb3c8(local_30,param_2,DAT_004cc1dc,DAT_004ccb70 | (uint)uVar1 << 10,
                           param_2 + 0x18);
      if (iVar6 < 0) {
        return iVar6;
      }
      FUN_004cae3e(param_2 + 0x18);
    }
    while( true ) {
      local_40 = local_30;
      local_3c = pcVar8;
      local_38 = iVar2;
      iVar6 = FUN_004cb968(local_30,param_2,param_2 + 0x18,0x78000000,iVar2,local_28,DAT_004ccb7c,
                           &local_40);
      if (iVar6 < 0) {
        return iVar6;
      }
      if (iVar6 != 0) break;
      if (*(char *)(param_2 + 0x17) == '\0') {
        return -2;
      }
    }
    pcVar8 = pcVar8 + iVar2;
  } while( true );
}


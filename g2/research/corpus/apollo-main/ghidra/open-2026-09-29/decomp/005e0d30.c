
int FUN_005e0d30(int param_1,int param_2,int param_3,int param_4,undefined4 param_5,
                undefined4 param_6,undefined4 param_7,char param_8)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  code *pcVar5;
  uint uVar6;
  int local_28;
  int local_24;
  int iStack_20;
  
  uVar4 = *(undefined4 *)(param_1 + 4);
  if ((param_4 == 0) || (*(uint *)(param_1 + 0x18) < (uint)(param_4 + param_3))) {
    return 6;
  }
  iStack_20 = param_4;
  iVar1 = FT_Stream_Seek(uVar4,param_3 + *(int *)(param_1 + 0x14));
  if (iVar1 != 0) {
    return iVar1;
  }
  iVar1 = FT_Stream_ExtractFrame(uVar4,param_4,&local_24);
  if (iVar1 != 0) {
    return iVar1;
  }
  local_28 = local_24;
  uVar6 = local_24 + param_4;
  if ((param_2 == 1) || (param_2 == 2)) {
LAB_005e0da0:
    iVar1 = FUN_005e08d0(param_1,&local_28,uVar6,0);
  }
  else if ((param_2 == 6) || (param_2 == 7)) {
LAB_005e0db0:
    iVar1 = FUN_005e08d0(param_1,&local_28,uVar6,1);
  }
  else {
    if (param_2 == 8) goto LAB_005e0da0;
    if (param_2 == 9) goto LAB_005e0db0;
    if (param_2 == 0x11) goto LAB_005e0da0;
    if (param_2 == 0x12) goto LAB_005e0db0;
    iVar1 = 0;
  }
  if (iVar1 != 0) goto LAB_005e0e88;
  pcVar5 = DAT_005e1484;
  if (param_2 != 1) {
    if (param_2 == 2) {
LAB_005e0e1a:
      uVar2 = (uint)*(ushort *)(*(int *)(param_1 + 0xc) + 2);
      uVar3 = (uVar2 + 7 >> 3) * (uint)**(ushort **)(param_1 + 0xc);
      pcVar5 = DAT_005e1488;
      if ((**(ushort **)(param_1 + 0xc) * uVar2 + 7 >> 3 < uVar3) &&
         (uVar3 - (uVar6 - local_28) == 0)) {
        pcVar5 = DAT_005e1484;
      }
    }
    else {
      pcVar5 = DAT_005e1488;
      if ((param_2 != 5) && (pcVar5 = DAT_005e1484, param_2 != 6)) {
        if (param_2 == 7) goto LAB_005e0e1a;
        pcVar5 = DAT_005e148c;
        if (param_2 == 8) {
          if (uVar6 < local_28 + 1U) goto LAB_005e0e88;
          local_28 = local_28 + 1;
        }
        else if (param_2 != 9) {
          if (param_2 - 0x11U < 3) {
            iVar1 = 7;
          }
          else {
            iVar1 = 8;
          }
          goto LAB_005e0e88;
        }
      }
    }
  }
  if (((*(char *)(param_1 + 0x11) != '\0') || (iVar1 = FUN_005e0818(param_1,param_8), iVar1 == 0))
     && (param_8 == '\0')) {
    iVar1 = (*pcVar5)(param_1,local_28,uVar6,param_5,param_6,param_7);
  }
LAB_005e0e88:
  FT_Stream_ReleaseFrame(uVar4,&local_24);
  return iVar1;
}


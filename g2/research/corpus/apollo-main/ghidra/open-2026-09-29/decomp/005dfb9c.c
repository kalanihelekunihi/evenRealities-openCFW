
uint FUN_005dfb9c(int param_1,char param_2,uint param_3,short *param_4,ushort *param_5)

{
  int iVar1;
  ushort uVar2;
  short sVar3;
  ushort uVar4;
  int iVar5;
  int *piVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint local_38;
  uint local_34;
  short *local_30;
  uint local_2c;
  uint local_28;
  
  uVar7 = *(undefined4 *)(param_1 + 0x68);
  piVar6 = *(int **)(param_1 + 0x228);
  if (param_2 == '\0') {
    iVar1 = 0xd8;
    iVar5 = *(int *)(param_1 + 0x330);
    iVar8 = *(int *)(param_1 + 0x2cc);
  }
  else {
    iVar1 = 0x128;
    iVar5 = *(int *)(param_1 + 0x334);
    iVar8 = *(int *)(param_1 + 0x2d0);
  }
  uVar9 = iVar8 + iVar5;
  uVar2 = *(ushort *)(param_1 + iVar1 + 0x22);
  local_34 = param_3;
  local_30 = param_4;
  if (uVar2 != 0) {
    if (param_3 < uVar2) {
      if ((iVar5 + param_3 * 4 + 4 <= uVar9) && (local_38 = FT_Stream_Seek(uVar7), local_38 == 0)) {
        uVar2 = FT_Stream_ReadUShort(uVar7,&local_38);
        *param_5 = uVar2;
        if (local_38 == 0) {
          sVar3 = FT_Stream_ReadUShort(uVar7,&local_38);
          *local_30 = sVar3;
          local_2c = 0;
          if (local_38 == 0) goto LAB_005dfc06;
        }
      }
    }
    else {
      iVar5 = iVar5 + (uVar2 - 1) * 4;
      if ((iVar5 + 4U <= uVar9) && (local_38 = FT_Stream_Seek(uVar7,iVar5), local_38 == 0)) {
        uVar4 = FT_Stream_ReadUShort(uVar7,&local_38);
        *param_5 = uVar4;
        if (local_38 == 0) {
          iVar5 = iVar5 + (local_34 - uVar2) * 2;
          if (uVar9 < iVar5 + 6U) {
            local_2c = 0;
            *local_30 = 0;
          }
          else {
            local_2c = FT_Stream_Seek(uVar7,iVar5 + 4);
            local_38 = local_2c;
            if (local_2c == 0) {
              sVar3 = FT_Stream_ReadUShort(uVar7,&local_38);
              *local_30 = sVar3;
              local_2c = (uint)(local_38 != 0);
            }
          }
          goto LAB_005dfc06;
        }
      }
    }
  }
  *local_30 = 0;
  local_2c = 0;
  *param_5 = 0;
LAB_005dfc06:
  if (piVar6 != (int *)0x0) {
    local_28 = (uint)*param_5;
    local_2c = (uint)*local_30;
    if (param_2 == '\0') {
      if (*piVar6 != 0) {
        (*(code *)*piVar6)(param_1,local_34,&local_28);
      }
      if (piVar6[1] != 0) {
        (*(code *)piVar6[1])(param_1,local_34,&local_2c);
      }
    }
    else {
      if (piVar6[3] != 0) {
        (*(code *)piVar6[3])(param_1,local_34,&local_28);
      }
      if (piVar6[4] != 0) {
        (*(code *)piVar6[4])(param_1,local_34,&local_2c);
      }
    }
    *param_5 = (ushort)local_28;
    *local_30 = (short)local_2c;
  }
  return local_2c;
}


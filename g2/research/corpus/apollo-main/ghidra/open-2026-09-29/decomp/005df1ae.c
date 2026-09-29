
int FUN_005df1ae(int param_1,int param_2,short *param_3,undefined4 param_4)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  ushort uVar5;
  short sVar6;
  int local_40;
  int local_3c [2];
  uint local_34;
  uint local_30;
  int local_2c;
  undefined4 uStack_28;
  
  sVar6 = 0;
  bVar1 = false;
  bVar2 = false;
  bVar3 = false;
  local_2c = *(int *)(param_1 + 0xc) + 0xc;
  uStack_28 = param_4;
  local_40 = FT_Stream_Seek(param_2,local_2c);
  if (local_40 == 0) {
    local_40 = 0;
    for (uVar5 = 0; uVar5 < *(ushort *)(param_1 + 4); uVar5 = uVar5 + 1) {
      local_40 = FT_Stream_ReadFields(param_2,DAT_005dfb7c,local_3c);
      if (local_40 != 0) {
        *(ushort *)(param_1 + 4) = uVar5 - 1;
        break;
      }
      iVar4 = 0;
      if ((local_34 <= *(uint *)(param_2 + 4)) &&
         (((local_30 <= *(int *)(param_2 + 4) - local_34 || (local_3c[0] == DAT_005dfb80)) ||
          (local_3c[0] == DAT_005dfb84)))) {
        sVar6 = sVar6 + 1;
        if ((local_3c[0] == DAT_005dfb88) || (local_3c[0] == DAT_005dfb8c)) {
          bVar1 = true;
          if (local_30 < 0x36) {
            return 0x8e;
          }
          local_40 = FT_Stream_Seek(param_2,local_34 + 0xc);
          if (local_40 != 0) {
            return local_40;
          }
          FT_Stream_ReadULong(param_2,&local_40);
          if (local_40 != 0) {
            return local_40;
          }
          iVar4 = FT_Stream_Seek(param_2,local_2c + (uVar5 + 1) * 0x10);
          if (iVar4 != 0) {
            return iVar4;
          }
        }
        else if (local_3c[0] == DAT_005dfb78) {
          bVar2 = true;
        }
        else if (local_3c[0] == DAT_005dfb74) {
          bVar3 = true;
        }
      }
      local_40 = iVar4;
    }
    *param_3 = sVar6;
    if (sVar6 == 0) {
      local_40 = 2;
    }
    else if ((bVar1) || ((bVar2 && (bVar3)))) {
      local_40 = 0;
    }
    else {
      local_40 = 0x8e;
    }
  }
  return local_40;
}


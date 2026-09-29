
int FT_Raccess_Get_HeaderInfo(undefined4 param_1,int param_2,int param_3,int *param_4,uint *param_5)

{
  bool bVar1;
  short sVar2;
  uint uVar3;
  bool bVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int local_40;
  byte local_3c [32];
  int *piStack_1c;
  
  piStack_1c = param_4;
  local_40 = FT_Stream_Seek(param_2,param_3);
  if ((local_40 == 0) && (local_40 = FT_Stream_Read(param_2,local_3c,0x10), local_40 == 0)) {
    if ((local_3c[0] < 0x80) &&
       (((local_3c[4] < 0x80 && (local_3c[8] < 0x80)) && (local_3c[0xc] < 0x80)))) {
      *param_5 = (uint)local_3c[1] << 0x10 | (uint)local_3c[0] << 0x18 | (uint)local_3c[2] << 8 |
                 (uint)local_3c[3];
      uVar3 = (uint)local_3c[7] |
              (uint)local_3c[5] << 0x10 | (uint)local_3c[4] << 0x18 | (uint)local_3c[6] << 8;
      uVar5 = (uint)local_3c[0xb] |
              (uint)local_3c[9] << 0x10 | (uint)local_3c[8] << 0x18 | (uint)local_3c[10] << 8;
      uVar6 = (uint)local_3c[0xf] |
              (uint)local_3c[0xd] << 0x10 | (uint)local_3c[0xc] << 0x18 | (uint)local_3c[0xe] << 8;
      if (uVar3 == 0) {
        local_40 = 2;
      }
      else {
        if ((int)*param_5 < (int)uVar3) {
          if ((int)(uVar3 - uVar5) < (int)*param_5) {
            return 2;
          }
        }
        else if ((int)(*param_5 - uVar6) < (int)uVar3) {
          return 2;
        }
        if (((((int)(0x7fffffff - uVar5) < (int)*param_5) ||
             ((int)(0x7fffffff - uVar6) < (int)uVar3)) ||
            (((int)((0x7fffffff - *param_5) - uVar5) < param_3 ||
             (((int)((0x7fffffff - uVar3) - uVar6) < param_3 ||
              (*(uint *)(param_2 + 4) < uVar5 + *param_5 + param_3)))))) ||
           (*(uint *)(param_2 + 4) < uVar6 + uVar3 + param_3)) {
          local_40 = 2;
        }
        else {
          *param_5 = param_3 + *param_5;
          param_3 = param_3 + uVar3;
          local_40 = FT_Stream_Seek(param_2,param_3);
          if (local_40 == 0) {
            local_3c[0x1f] = local_3c[0xf] + 1;
            local_40 = FT_Stream_Read(param_2,local_3c + 0x10,0x10);
            if (local_40 == 0) {
              bVar1 = true;
              bVar4 = true;
              for (iVar7 = 0; iVar7 < 0x10; iVar7 = iVar7 + 1) {
                if (local_3c[iVar7 + 0x10] != 0) {
                  bVar1 = false;
                }
                if (local_3c[iVar7 + 0x10] != local_3c[iVar7]) {
                  bVar4 = false;
                }
              }
              if (bVar1 || bVar4) {
                local_40 = FT_Stream_Skip(param_2,8);
                sVar2 = FT_Stream_ReadUShort(param_2,&local_40);
                iVar7 = (int)sVar2;
                if (local_40 == 0) {
                  if (iVar7 < 0) {
                    local_40 = 2;
                  }
                  else {
                    local_40 = FT_Stream_Seek(param_2,iVar7 + param_3);
                    if (local_40 == 0) {
                      *param_4 = iVar7 + param_3;
                      local_40 = 0;
                    }
                  }
                }
              }
              else {
                local_40 = 2;
              }
            }
          }
        }
      }
    }
    else {
      local_40 = 2;
    }
  }
  return local_40;
}


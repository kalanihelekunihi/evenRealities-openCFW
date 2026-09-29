
undefined4 FUN_00504d2c(int param_1,byte *param_2,byte param_3)

{
  byte bVar1;
  byte *pbVar2;
  byte bVar3;
  byte local_48;
  byte local_47;
  byte local_46;
  byte local_44;
  byte local_43;
  byte local_42;
  uint local_40;
  short local_3a;
  short local_38;
  short local_36;
  short local_34;
  short local_32;
  short local_30;
  short local_2e;
  
  pbVar2 = param_2 + 1;
  local_40 = 0;
  if (param_3 == 1) {
    bVar3 = 1;
    bVar1 = *param_2 >> 2 & 3;
    if ((*param_2 >> 2 & 3) == 0) {
      local_48 = param_2[2];
      local_47 = param_2[3];
      local_46 = param_2[4];
      local_44 = param_2[8];
      local_43 = param_2[9];
      local_42 = param_2[10];
      bVar1 = param_2[0xe];
    }
    else if (bVar1 == 2) {
      if ((param_2[2] & 0xf) < 8) {
        local_48 = param_2[2] & 0xf;
      }
      else {
        local_48 = (param_2[2] & 0xf) - 0x10;
      }
      if (param_2[2] >> 4 < 8) {
        local_47 = param_2[2] >> 4;
      }
      else {
        local_47 = (param_2[2] >> 4) - 0x10;
      }
      if ((param_2[3] & 0xf) < 8) {
        local_46 = param_2[3] & 0xf;
      }
      else {
        local_46 = (param_2[3] & 0xf) - 0x10;
      }
      if ((param_2[8] & 0xf) < 8) {
        local_44 = param_2[8] & 0xf;
      }
      else {
        local_44 = (param_2[8] & 0xf) - 0x10;
      }
      if (param_2[8] >> 4 < 8) {
        local_43 = param_2[8] >> 4;
      }
      else {
        local_43 = (param_2[8] >> 4) - 0x10;
      }
      if ((param_2[9] & 0xf) < 8) {
        local_42 = param_2[9] & 0xf;
      }
      else {
        local_42 = (param_2[9] & 0xf) - 0x10;
      }
      if ((param_2[0xe] & 0xf) < 8) {
        bVar1 = param_2[0xe] & 0xf;
      }
      else {
        bVar1 = (param_2[0xe] & 0xf) - 0x10;
      }
    }
    else {
      if (1 < bVar1) {
        return 0xfffffff5;
      }
      if ((param_2[2] & 0x1f) < 0x10) {
        local_48 = param_2[2] & 0x1f;
      }
      else {
        local_48 = (param_2[2] & 0x1f) - 0x20;
      }
      if ((byte)((param_2[3] & 3) << 3 | param_2[2] >> 5) < 0x10) {
        local_47 = (param_2[3] & 3) << 3 | param_2[2] >> 5;
      }
      else {
        local_47 = ((param_2[3] & 3) << 3 | param_2[2] >> 5) - 0x20;
      }
      if ((param_2[3] & 0x7f) >> 2 < 0x10) {
        local_46 = (byte)(((uint)param_2[3] << 0x19) >> 0x1b);
      }
      else {
        local_46 = (byte)(((uint)param_2[3] << 0x19) >> 0x1b) - 0x20;
      }
      if ((param_2[8] & 0x1f) < 0x10) {
        local_44 = param_2[8] & 0x1f;
      }
      else {
        local_44 = (param_2[8] & 0x1f) - 0x20;
      }
      if ((byte)((param_2[9] & 3) << 3 | param_2[8] >> 5) < 0x10) {
        local_43 = (param_2[9] & 3) << 3 | param_2[8] >> 5;
      }
      else {
        local_43 = ((param_2[9] & 3) << 3 | param_2[8] >> 5) - 0x20;
      }
      if ((param_2[9] & 0x7f) >> 2 < 0x10) {
        local_42 = (byte)(((uint)param_2[9] << 0x19) >> 0x1b);
      }
      else {
        local_42 = (byte)(((uint)param_2[9] << 0x19) >> 0x1b) - 0x20;
      }
      if ((param_2[0xe] & 0x1f) < 0x10) {
        bVar1 = param_2[0xe] & 0x1f;
      }
      else {
        bVar1 = (param_2[0xe] & 0x1f) - 0x20;
      }
    }
  }
  else {
    if (param_3 == 0) {
      return 0xfffffff5;
    }
    if (param_3 == 3) {
      bVar3 = 4;
      bVar1 = *param_2 >> 2 & 3;
      if ((*param_2 >> 2 & 3) == 0) {
        return 0xfffffff5;
      }
      if (bVar1 == 2) {
        if ((param_2[5] & 0xf) < 8) {
          local_48 = param_2[5] & 0xf;
        }
        else {
          local_48 = (param_2[5] & 0xf) - 0x10;
        }
        if (param_2[5] >> 4 < 8) {
          local_47 = param_2[5] >> 4;
        }
        else {
          local_47 = (param_2[5] >> 4) - 0x10;
        }
        if ((param_2[6] & 0xf) < 8) {
          local_46 = param_2[6] & 0xf;
        }
        else {
          local_46 = (param_2[6] & 0xf) - 0x10;
        }
        if ((param_2[0xb] & 0xf) < 8) {
          local_44 = param_2[0xb] & 0xf;
        }
        else {
          local_44 = (param_2[0xb] & 0xf) - 0x10;
        }
        if (param_2[0xb] >> 4 < 8) {
          local_43 = param_2[0xb] >> 4;
        }
        else {
          local_43 = (param_2[0xb] >> 4) - 0x10;
        }
        if ((param_2[0xc] & 0xf) < 8) {
          local_42 = param_2[0xc] & 0xf;
        }
        else {
          local_42 = (param_2[0xc] & 0xf) - 0x10;
        }
        if ((param_2[0xf] & 0xf) < 8) {
          bVar1 = param_2[0xf] & 0xf;
        }
        else {
          bVar1 = (param_2[0xf] & 0xf) - 0x10;
        }
      }
      else {
        if (1 < bVar1) {
          return 0xfffffff5;
        }
        if ((param_2[6] & 0x1f) < 0x10) {
          local_48 = param_2[6] & 0x1f;
        }
        else {
          local_48 = (param_2[6] & 0x1f) - 0x20;
        }
        if ((byte)((param_2[7] & 3) << 3 | param_2[6] >> 5) < 0x10) {
          local_47 = (param_2[7] & 3) << 3 | param_2[6] >> 5;
        }
        else {
          local_47 = ((param_2[7] & 3) << 3 | param_2[6] >> 5) - 0x20;
        }
        if ((param_2[7] & 0x7f) >> 2 < 0x10) {
          local_46 = (byte)(((uint)param_2[7] << 0x19) >> 0x1b);
        }
        else {
          local_46 = (byte)(((uint)param_2[7] << 0x19) >> 0x1b) - 0x20;
        }
        if ((param_2[0xc] & 0x1f) < 0x10) {
          local_44 = param_2[0xc] & 0x1f;
        }
        else {
          local_44 = (param_2[0xc] & 0x1f) - 0x20;
        }
        if ((byte)((param_2[0xd] & 3) << 3 | param_2[0xc] >> 5) < 0x10) {
          local_43 = (param_2[0xd] & 3) << 3 | param_2[0xc] >> 5;
        }
        else {
          local_43 = ((param_2[0xd] & 3) << 3 | param_2[0xc] >> 5) - 0x20;
        }
        if ((param_2[0xd] & 0x7f) >> 2 < 0x10) {
          local_42 = (byte)(((uint)param_2[0xd] << 0x19) >> 0x1b);
        }
        else {
          local_42 = (byte)(((uint)param_2[0xd] << 0x19) >> 0x1b) - 0x20;
        }
        if ((param_2[0xf] & 0x7f) >> 2 < 0x10) {
          bVar1 = (byte)((param_2[0xf] & 0x7f) >> 2);
        }
        else {
          bVar1 = (char)((param_2[0xf] & 0x7f) >> 2) - 0x20;
        }
      }
    }
    else {
      if (2 < param_3) {
        if (param_3 != 4) {
          return 0xfffffff5;
        }
        bVar3 = 8;
        bVar1 = *param_2 >> 2 & 3;
        if ((*param_2 >> 2 & 3) != 0) {
          if (bVar1 == 2) {
            if (param_2[6] >> 4 < 8) {
              local_48 = param_2[6] >> 4;
            }
            else {
              local_48 = (param_2[6] >> 4) - 0x10;
            }
            if ((param_2[7] & 0xf) < 8) {
              local_47 = param_2[7] & 0xf;
            }
            else {
              local_47 = (param_2[7] & 0xf) - 0x10;
            }
            if (param_2[7] >> 4 < 8) {
              local_46 = param_2[7] >> 4;
            }
            else {
              local_46 = (param_2[7] >> 4) - 0x10;
            }
            if (param_2[0xc] >> 4 < 8) {
              local_44 = param_2[0xc] >> 4;
            }
            else {
              local_44 = (param_2[0xc] >> 4) - 0x10;
            }
            if ((param_2[0xd] & 0xf) < 8) {
              local_43 = param_2[0xd] & 0xf;
            }
            else {
              local_43 = (param_2[0xd] & 0xf) - 0x10;
            }
            if (param_2[0xd] >> 4 < 8) {
              local_42 = param_2[0xd] >> 4;
            }
            else {
              local_42 = (param_2[0xd] >> 4) - 0x10;
            }
            if (param_2[0xf] >> 4 < 8) {
              bVar1 = param_2[0xf] >> 4;
            }
            else {
              bVar1 = (param_2[0xf] >> 4) - 0x10;
            }
            goto LAB_00504da6;
          }
          if (1 < bVar1) {
            return 0xfffffff5;
          }
        }
        return 0xfffffff5;
      }
      bVar3 = 2;
      bVar1 = *param_2 >> 2 & 3;
      if ((*param_2 >> 2 & 3) == 0) {
        local_48 = param_2[5];
        local_47 = param_2[6];
        local_46 = param_2[7];
        local_44 = param_2[0xb];
        local_43 = param_2[0xc];
        local_42 = param_2[0xd];
        bVar1 = param_2[0xf];
      }
      else if (bVar1 == 2) {
        if (param_2[3] >> 4 < 8) {
          local_48 = param_2[3] >> 4;
        }
        else {
          local_48 = (param_2[3] >> 4) - 0x10;
        }
        if ((param_2[4] & 0xf) < 8) {
          local_47 = param_2[4] & 0xf;
        }
        else {
          local_47 = (param_2[4] & 0xf) - 0x10;
        }
        if (param_2[4] >> 4 < 8) {
          local_46 = param_2[4] >> 4;
        }
        else {
          local_46 = (param_2[4] >> 4) - 0x10;
        }
        if (param_2[9] >> 4 < 8) {
          local_44 = param_2[9] >> 4;
        }
        else {
          local_44 = (param_2[9] >> 4) - 0x10;
        }
        if ((param_2[10] & 0xf) < 8) {
          local_43 = param_2[10] & 0xf;
        }
        else {
          local_43 = (param_2[10] & 0xf) - 0x10;
        }
        if (param_2[10] >> 4 < 8) {
          local_42 = param_2[10] >> 4;
        }
        else {
          local_42 = (param_2[10] >> 4) - 0x10;
        }
        if (param_2[0xe] >> 4 < 8) {
          bVar1 = param_2[0xe] >> 4;
        }
        else {
          bVar1 = (param_2[0xe] >> 4) - 0x10;
        }
      }
      else {
        if (1 < bVar1) {
          return 0xfffffff5;
        }
        if ((param_2[4] & 0x1f) < 0x10) {
          local_48 = param_2[4] & 0x1f;
        }
        else {
          local_48 = (param_2[4] & 0x1f) - 0x20;
        }
        if ((byte)((param_2[5] & 3) << 3 | param_2[4] >> 5) < 0x10) {
          local_47 = (param_2[5] & 3) << 3 | param_2[4] >> 5;
        }
        else {
          local_47 = ((param_2[5] & 3) << 3 | param_2[4] >> 5) - 0x20;
        }
        if ((param_2[5] & 0x7f) >> 2 < 0x10) {
          local_46 = (byte)(((uint)param_2[5] << 0x19) >> 0x1b);
        }
        else {
          local_46 = (byte)(((uint)param_2[5] << 0x19) >> 0x1b) - 0x20;
        }
        if ((param_2[10] & 0x1f) < 0x10) {
          local_44 = param_2[10] & 0x1f;
        }
        else {
          local_44 = (param_2[10] & 0x1f) - 0x20;
        }
        if ((byte)((param_2[0xb] & 3) << 3 | param_2[10] >> 5) < 0x10) {
          local_43 = (param_2[0xb] & 3) << 3 | param_2[10] >> 5;
        }
        else {
          local_43 = ((param_2[0xb] & 3) << 3 | param_2[10] >> 5) - 0x20;
        }
        if ((param_2[0xb] & 0x7f) >> 2 < 0x10) {
          local_42 = (byte)(((uint)param_2[0xb] << 0x19) >> 0x1b);
        }
        else {
          local_42 = (byte)(((uint)param_2[0xb] << 0x19) >> 0x1b) - 0x20;
        }
        if ((byte)((param_2[0xf] & 3) << 3 | param_2[0xe] >> 5) < 0x10) {
          bVar1 = (param_2[0xf] & 3) << 3 | param_2[0xe] >> 5;
        }
        else {
          bVar1 = ((param_2[0xf] & 3) << 3 | param_2[0xe] >> 5) - 0x20;
        }
      }
    }
  }
LAB_00504da6:
  if ((*param_2 & 0x7f) >> 6 != 0) {
    if (((*pbVar2 & bVar3) == 0) || (*(char *)(param_1 + 0x2c) == '\0')) {
      local_3a = (short)DAT_00505ed8;
      local_38 = local_3a;
      local_36 = local_3a;
    }
    else {
      local_3a = (short)(char)local_48 + *(short *)(param_1 + 0x1e);
      local_38 = *(short *)(param_1 + 0x20) + (short)(char)local_47;
      local_36 = *(short *)(param_1 + 0x22) + (short)(char)local_46;
      local_40 = 1;
      *(short *)(param_1 + 0x1e) = local_3a;
      *(short *)(param_1 + 0x20) = local_38;
      *(short *)(param_1 + 0x22) = local_36;
    }
  }
  if ((*param_2 & 0x3f) >> 5 != 0) {
    if (((*pbVar2 >> 4 & bVar3) == 0) || (*(char *)(param_1 + 0x2d) == '\0')) {
      local_34 = (short)DAT_00505ed8;
      local_32 = local_34;
      local_30 = local_34;
    }
    else {
      if ((*param_2 & 0x7f) >> 6 != 0) {
        local_48 = local_44;
      }
      local_34 = (short)(char)local_48 + *(short *)(param_1 + 0x24);
      if ((*param_2 & 0x7f) >> 6 != 0) {
        local_47 = local_43;
      }
      local_32 = (short)(char)local_47 + *(short *)(param_1 + 0x26);
      if ((*param_2 & 0x7f) >> 6 != 0) {
        local_46 = local_42;
      }
      local_30 = (short)(char)local_46 + *(short *)(param_1 + 0x28);
      local_40 = local_40 | 2;
      *(short *)(param_1 + 0x24) = local_34;
      *(short *)(param_1 + 0x26) = local_32;
      *(short *)(param_1 + 0x28) = local_30;
    }
  }
  local_2e = -0x80;
  if (((*param_2 & 0x60) == 0x60) &&
     ((((*pbVar2 & bVar3) != 0 || ((*pbVar2 >> 4 & bVar3) != 0)) &&
      (*(char *)(param_1 + 0x2e) != '\0')))) {
    local_2e = (short)(char)bVar1 + *(short *)(param_1 + 0x2a);
    local_40 = local_40 | 8;
    *(short *)(param_1 + 0x2a) = local_2e;
  }
  if (*(int *)(param_1 + 0x18) != 0) {
    (**(code **)(param_1 + 0x18))(&local_40);
  }
  return 0;
}


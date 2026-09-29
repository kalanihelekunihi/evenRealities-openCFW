
int FUN_0059b852(int param_1,uint param_2,undefined4 param_3,int param_4,int *param_5,int param_6,
                undefined1 *param_7)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  float fVar10;
  uint uVar11;
  uint uVar12;
  sbyte local_58;
  byte local_57;
  float *local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  
  iVar1 = FUN_0059b80c(param_2,param_3,&local_58);
  iVar7 = 0;
  local_3c = *(int *)(DAT_0059c178 + param_2 * 4) * (param_1 + 1);
  iVar8 = 0;
  local_40 = 0;
  local_44 = 0;
  uVar9 = 0;
  if (param_6 == 0) {
    param_6 = 0x7fffffff;
  }
  else {
    param_6 = param_6 << 0xb;
  }
  local_50 = DAT_0059c17c + iVar1 * 0x800;
  iVar1 = 0;
  local_4c = 0;
  local_38 = param_4;
  do {
    local_54 = (float *)(local_38 + iVar1 * 4);
    local_48 = local_3c + 2 >> (1U - local_4c & 0xff);
    local_57 = (byte)param_2;
    while( true ) {
      iVar2 = *param_5;
      if (local_48 <= *param_5) {
        iVar2 = local_48;
      }
      if ((iVar2 <= iVar1) || (param_6 < iVar7)) break;
      iVar2 = FUN_0059b6a0(local_57);
      if (iVar2 == 0) {
        fVar10 = 0.375;
      }
      else {
        fVar10 = 0.5;
      }
      uVar5 = 0;
      uVar12 = (uint)(0.0 < ABS(*local_54) + fVar10) * (int)(ABS(*local_54) + fVar10);
      uVar11 = (uint)(0.0 < ABS(local_54[1]) + fVar10) * (int)(ABS(local_54[1]) + fVar10);
      iVar2 = -((int)~-(uint)(uVar12 == 0) >> 0x1f) - ((int)~-(uint)(uVar11 == 0) >> 0x1f);
      uVar4 = (uVar11 | uVar12) >> 2;
      iVar7 = iVar7 + iVar2 * 0x800;
      if (uVar4 != 0) {
        uVar5 = 0;
        if (local_58 != 0) {
          uVar5 = 1;
          iVar7 = iVar7 + (uint)*(ushort *)
                                 (DAT_0059c180 + 0x20 + (uint)*(byte *)(local_50 + uVar9 * 4) * 0x22
                                 ) + -0x1000;
          if (uVar12 == 1) {
            iVar8 = iVar8 + 1;
          }
          iVar8 = iVar8 + (uint)(uVar11 == 1) + 2;
        }
        uVar4 = uVar4 >> local_58;
        uVar6 = uVar5;
        if (uVar4 != 0) {
          while( true ) {
            uVar5 = uVar5 + 1;
            iVar7 = iVar7 + (uint)*(ushort *)
                                   (DAT_0059c180 + 0x20 +
                                   (uint)*(byte *)(local_50 + uVar9 * 4 + uVar6) * 0x22);
            uVar4 = uVar4 >> 1;
            if (uVar4 == 0) break;
            uVar6 = uVar5;
            if (2 < uVar5) {
              uVar6 = 3;
            }
          }
        }
        iVar7 = iVar7 + uVar5 * 0x1000;
        uVar12 = uVar12 >> (uVar5 & 0xff);
        uVar11 = uVar11 >> (uVar5 & 0xff);
        if (2 < uVar5) {
          uVar5 = 3;
        }
      }
      iVar7 = iVar7 + (uint)*(ushort *)
                             (DAT_0059c180 + (uint)*(byte *)(local_50 + uVar9 * 4 + uVar5) * 0x22 +
                             (uVar12 + uVar11 * 4) * 2);
      if ((iVar2 != 0) && (iVar7 <= param_6)) {
        local_44 = iVar1 + 2;
        local_40 = iVar7;
      }
      if (uVar5 < 2) {
        iVar2 = (uVar5 + 1) * (uVar12 + uVar11) + 1;
      }
      else {
        iVar2 = uVar5 + 0xc;
      }
      iVar1 = iVar1 + 2;
      local_54 = local_54 + 2;
      uVar9 = iVar2 + uVar9 * 0x10 & 0xff;
    }
    param_2 = (uint)local_57;
    local_4c = local_4c + 1;
    local_50 = local_50 + 0x400;
  } while (local_4c < 2);
  *param_5 = local_44;
  if (param_7 != (undefined1 *)0x0) {
    if ((local_58 == 0) || (local_40 + iVar8 * 0x800 <= param_6)) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
    *param_7 = uVar3;
  }
  if (param_6 == 0x7fffffff) {
    local_40 = local_40 + iVar8 * 0x800;
  }
  return (int)(local_40 + 0x7ff + ((uint)(local_40 + 0x7ff >> 10) >> 0x15)) >> 0xb;
}


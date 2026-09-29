
undefined8 FUN_005e01ea(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  byte *pbVar7;
  uint uVar8;
  uint local_28;
  undefined4 local_24;
  undefined4 uStack_20;
  
  *(undefined4 *)(param_1 + 0x2f0) = 0;
  *(undefined4 *)(param_1 + 0x2f4) = 0;
  *(undefined1 *)(param_1 + 0x2f8) = 0;
  *(undefined4 *)(param_1 + 0x2fc) = 0;
  local_28 = param_2;
  local_24 = param_3;
  uStack_20 = param_4;
  iVar3 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0e98,param_2,&local_28);
  if (iVar3 == 0) {
    *(undefined1 *)(param_1 + 0x2f8) = 2;
    iVar3 = 0;
  }
  else {
    iVar4 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0e9c,param_2,&local_28);
    iVar3 = 0;
    if (iVar4 != 0) {
      iVar3 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0ea0,param_2,&local_28);
    }
    if (iVar3 == 0) {
      *(undefined1 *)(param_1 + 0x2f8) = 1;
    }
  }
  iVar4 = 0;
  if ((iVar3 != 0) &&
     (iVar4 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0ea4,param_2,&local_28), iVar4 == 0)) {
    *(undefined1 *)(param_1 + 0x2f8) = 3;
  }
  if (iVar4 == 0) {
    if (local_28 < 8) {
      iVar4 = 3;
    }
    else {
      uVar5 = *(undefined4 *)(param_2 + 8);
      uVar6 = *(byte *)(param_1 + 0x2f8) - 1;
      if (uVar6 < 2) {
        iVar4 = FT_Stream_ExtractFrame(param_2,local_28,param_1 + 0x2f0);
        if (iVar4 == 0) {
          *(uint *)(param_1 + 0x2f4) = local_28;
          pbVar7 = *(byte **)(param_1 + 0x2f0);
          uVar8 = (uint)pbVar7[1] << 0x10 | (uint)*pbVar7 << 0x18;
          uVar6 = (uint)pbVar7[7] |
                  (uint)pbVar7[5] << 0x10 | (uint)pbVar7[4] << 0x18 | (uint)pbVar7[6] << 8;
          if ((((uVar8 == 0x20000) || (CONCAT11(pbVar7[2],pbVar7[3]) == 0x200)) ||
              (uVar8 == 0x30000)) || (CONCAT11(pbVar7[2],pbVar7[3]) == 0x300)) {
            if (uVar6 < 0x10000) {
              if (local_28 < uVar6 * 0x30 + 8) {
                uVar6 = (local_28 - 8) / 0x30;
              }
              *(uint *)(param_1 + 0x2fc) = uVar6;
              goto LAB_005e0422;
            }
            iVar4 = 3;
          }
          else {
            iVar4 = 2;
          }
        }
      }
      else {
        if (uVar6 != 2) {
LAB_005e0422:
          *(undefined4 *)(param_1 + 0x338) = 0;
          *(undefined4 *)(param_1 + 0x33c) = 0;
          if (*(char *)(param_1 + 0x2f8) == '\x03') {
            *(undefined4 *)(param_1 + 0x338) = uVar5;
            *(uint *)(param_1 + 0x33c) = local_28;
          }
          else if (*(char *)(param_1 + 0x2f8) != '\0') {
            iVar4 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0ea8,param_2,&local_24);
            iVar3 = 0;
            if (iVar4 != 0) {
              iVar3 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0eac,param_2,&local_24);
            }
            iVar4 = 0;
            if (iVar3 != 0) {
              iVar4 = (**(code **)(param_1 + 0x204))(param_1,DAT_005e0eb0,param_2,&local_24);
            }
            if (iVar4 == 0) {
              *(undefined4 *)(param_1 + 0x338) = *(undefined4 *)(param_2 + 8);
              *(undefined4 *)(param_1 + 0x33c) = local_24;
            }
          }
          if (*(int *)(param_1 + 0x33c) == 0) {
            *(undefined4 *)(param_1 + 0x2fc) = 0;
          }
          iVar4 = 0;
          goto LAB_005e02a2;
        }
        iVar4 = FT_Stream_EnterFrame(param_2,8);
        if (iVar4 == 0) {
          sVar1 = FT_Stream_GetUShort(param_2);
          sVar2 = FT_Stream_GetUShort(param_2);
          uVar6 = FT_Stream_GetULong(param_2);
          FT_Stream_ExitFrame(param_2);
          if (sVar1 == 0) {
            iVar4 = 2;
          }
          else if (((sVar2 == 1) || (sVar2 == 3)) && (uVar6 < 0x10000)) {
            if (local_28 < uVar6 * 4 + 8) {
              uVar6 = local_28 - 8 >> 2;
            }
            iVar4 = FT_Stream_Seek(param_2,*(int *)(param_2 + 8) + -8);
            if (iVar4 == 0) {
              *(uint *)(param_1 + 0x2f4) = uVar6 * 4 + 8;
              iVar4 = FT_Stream_ExtractFrame
                                (param_2,*(undefined4 *)(param_1 + 0x2f4),param_1 + 0x2f0);
              if (iVar4 == 0) {
                *(uint *)(param_1 + 0x2fc) = uVar6;
                goto LAB_005e0422;
              }
            }
          }
          else {
            iVar4 = 3;
          }
        }
      }
    }
  }
  if (iVar4 != 0) {
    if (*(int *)(param_1 + 0x2f0) != 0) {
      FT_Stream_ReleaseFrame(param_2,param_1 + 0x2f0);
    }
    *(undefined4 *)(param_1 + 0x2f4) = 0;
    *(undefined1 *)(param_1 + 0x2f8) = 0;
  }
LAB_005e02a2:
  return CONCAT44(local_28,iVar4);
}


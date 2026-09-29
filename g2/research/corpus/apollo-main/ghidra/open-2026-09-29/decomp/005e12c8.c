
undefined8
FUN_005e12c8(int param_1,undefined4 *param_2,uint param_3,undefined4 param_4,undefined4 param_5,
            short *param_6)

{
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined4 *local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  iVar6 = 0;
  iVar3 = *(int *)(*(int *)(param_1 + 0x300) + (int)param_2 * 4);
  param_6[1] = 0;
  *param_6 = 0;
  iVar3 = *(int *)(param_1 + 0x2f0) + iVar3 * 4;
  uVar7 = (uint)*(byte *)(iVar3 + 0xb) |
          (uint)*(byte *)(iVar3 + 9) << 0x10 | (uint)*(byte *)(iVar3 + 8) << 0x18 |
          (uint)*(byte *)(iVar3 + 10) << 8;
  local_2c = param_3;
  uStack_28 = param_4;
  do {
    local_30 = param_2;
    if (*(uint *)(param_1 + 0x10) < param_3) {
      iVar3 = 6;
LAB_005e147e:
      return CONCAT44(local_30,iVar3);
    }
    if ((*(uint *)(param_1 + 0x33c) <= uVar7) ||
       (*(int *)(param_1 + 0x33c) - uVar7 < param_3 * 4 + 0xc)) {
      iVar3 = 3;
      goto LAB_005e147e;
    }
    iVar3 = FT_Stream_Seek(param_4,uVar7 + *(int *)(param_1 + 0x338) + param_3 * 4 + 4);
    if ((iVar3 != 0) || (iVar3 = FT_Stream_EnterFrame(param_4,8), iVar3 != 0)) goto LAB_005e147e;
    uVar4 = FT_Stream_GetULong(param_4);
    uVar5 = FT_Stream_GetULong(param_4);
    FT_Stream_ExitFrame(param_4);
    if (uVar4 == uVar5) {
      iVar3 = 0x9d;
      goto LAB_005e147e;
    }
    if (((uVar5 < uVar4) || (uVar5 - uVar4 < 8)) || (*(int *)(param_1 + 0x33c) - uVar7 < uVar5)) {
      iVar3 = 3;
      goto LAB_005e147e;
    }
    iVar3 = FT_Stream_Seek(param_4,uVar4 + uVar7 + *(int *)(param_1 + 0x338));
    if ((iVar3 != 0) || (iVar3 = FT_Stream_EnterFrame(param_4,uVar5 - uVar4), iVar3 != 0))
    goto LAB_005e147e;
    sVar1 = FT_Stream_GetUShort(param_4);
    sVar2 = FT_Stream_GetUShort(param_4);
    iVar3 = FT_Stream_GetULong(param_4);
    if (iVar3 != DAT_005e1490) {
      if (iVar3 == DAT_005e1494) {
LAB_005e1430:
        iVar3 = 2;
      }
      else if (iVar3 == DAT_005e1498) {
        iVar3 = 7;
      }
      else {
        if ((iVar3 == DAT_005e149c) || (iVar3 == DAT_005e14a0)) goto LAB_005e1430;
        iVar3 = 7;
      }
LAB_005e143a:
      FT_Stream_ExitFrame(param_4);
      if (iVar3 == 0) {
        local_30 = &local_2c;
        FUN_005dfb9c(param_1,0,param_3,(int)&local_2c + 2);
        param_6[2] = sVar1;
        param_6[3] = *param_6 - sVar2;
        param_6[4] = (short)((int)((uint)*(ushort *)(*(int *)(param_1 + 0x58) + 0xc) *
                                  (local_2c & 0xffff)) / (int)(uint)*(ushort *)(param_1 + 0xb2));
      }
      goto LAB_005e147e;
    }
    if (3 < iVar6) {
      iVar3 = 3;
      goto LAB_005e143a;
    }
    param_3 = FT_Stream_GetUShort(param_4);
    FT_Stream_ExitFrame(param_4);
    iVar6 = iVar6 + 1;
  } while( true );
}



undefined8 tt_face_load_loca(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint local_20;
  undefined4 uStack_1c;
  
  local_20 = param_3;
  uStack_1c = param_4;
  uVar2 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f9508,param_2,param_1 + 0x2b0);
  if ((uVar2 & 0xff) == 0x8e) {
    *(undefined4 *)(param_1 + 0x2b0) = 0;
    *(undefined4 *)(param_1 + 0x2b4) = 0;
  }
  else {
    if (uVar2 != 0) goto LAB_005f9190;
    if (*(int *)(*(int *)(param_1 + 0x80) + 0x34) == 0) {
      *(undefined4 *)(param_1 + 0x2b4) = *(undefined4 *)(param_2 + 8);
    }
    else {
      *(undefined4 *)(param_1 + 0x2b4) = 0;
    }
  }
  iVar3 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f950c,param_2,&local_20);
  if (iVar3 == 0) {
    if (*(short *)(param_1 + 0xd2) == 0) {
      iVar3 = 1;
      if (0x1ffff < local_20) {
        local_20 = DAT_005f9514;
      }
      *(uint *)(param_1 + 0x2d4) = local_20 >> 1;
    }
    else {
      iVar3 = 2;
      if (0x3ffff < local_20) {
        local_20 = DAT_005f9510;
      }
      *(uint *)(param_1 + 0x2d4) = local_20 >> 2;
    }
    if ((*(int *)(param_1 + 0x2d4) != *(int *)(param_1 + 0x10) + 1) &&
       (*(uint *)(param_1 + 0x2d4) <= *(uint *)(param_1 + 0x10))) {
      uVar5 = *(int *)(param_1 + 0x10) + 1 << iVar3;
      uVar6 = *(uint *)(param_1 + 0x9c);
      uVar7 = uVar6 + (uint)*(ushort *)(param_1 + 0x98) * 0x10;
      uVar2 = 0x7fffffff;
      bVar1 = false;
      for (; uVar6 < uVar7; uVar6 = uVar6 + 0x10) {
        uVar4 = *(int *)(uVar6 + 8) - *(int *)(param_2 + 8);
        if ((0 < (int)uVar4) && ((int)uVar4 < (int)uVar2)) {
          bVar1 = true;
          uVar2 = uVar4;
        }
      }
      if (!bVar1) {
        uVar2 = *(int *)(param_2 + 4) - *(int *)(param_2 + 8);
      }
      if (uVar2 < uVar5) {
        if (*(int *)(param_1 + 0x2d4) == 0) {
          iVar3 = 0;
        }
        else {
          iVar3 = *(int *)(param_1 + 0x2d4) + -1;
        }
        *(int *)(param_1 + 0x10) = iVar3;
      }
      else {
        *(int *)(param_1 + 0x2d4) = *(int *)(param_1 + 0x10) + 1;
        local_20 = uVar5;
      }
    }
    uVar2 = FT_Stream_ExtractFrame(param_2,local_20,param_1 + 0x2d8);
  }
  else {
    uVar2 = 0x90;
  }
LAB_005f9190:
  return CONCAT44(local_20,uVar2);
}


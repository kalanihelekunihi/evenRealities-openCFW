
void Ins_IUP(int *param_1)

{
  byte bVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int local_34;
  int local_30;
  int local_2c;
  uint local_28;
  
  if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
     (*(char *)((int)param_1 + 0x267) != '\0')) {
    if (((char)param_1[0x9a] != '\0') && (*(char *)((int)param_1 + 0x269) != '\0')) {
      return;
    }
    if ((int)((uint)*(byte *)(param_1 + 0x5d) << 0x1f) < 0) {
      *(undefined1 *)(param_1 + 0x9a) = 1;
    }
    else {
      *(undefined1 *)((int)param_1 + 0x269) = 1;
    }
  }
  if (*(short *)((int)param_1 + 0x9a) != 0) {
    if ((int)((uint)*(byte *)(param_1 + 0x5d) << 0x1f) < 0) {
      bVar1 = 8;
      local_34 = param_1[0x27];
      local_30 = param_1[0x28];
      local_2c = param_1[0x29];
    }
    else {
      bVar1 = 0x10;
      local_34 = param_1[0x27] + 4;
      local_30 = param_1[0x28] + 4;
      local_2c = param_1[0x29] + 4;
    }
    local_28 = (uint)*(ushort *)(param_1 + 0x26);
    sVar2 = 0;
    uVar3 = 0;
    do {
      uVar7 = (uint)*(ushort *)(param_1[0x2b] + sVar2 * 2) - (uint)*(ushort *)(param_1 + 0x2c);
      uVar4 = uVar3;
      if (*(ushort *)(param_1 + 0x26) <= uVar7) {
        uVar7 = *(ushort *)(param_1 + 0x26) - 1;
      }
      for (; (uVar4 <= uVar7 && ((*(byte *)(param_1[0x2a] + uVar4) & bVar1) == 0));
          uVar4 = uVar4 + 1) {
      }
      uVar5 = uVar4;
      uVar8 = uVar4;
      if (uVar4 <= uVar7) {
        while (uVar6 = uVar5, uVar5 = uVar6 + 1, uVar5 <= uVar7) {
          if ((*(byte *)(param_1[0x2a] + uVar5) & bVar1) != 0) {
            _iup_worker_interpolate(&local_34,uVar8 + 1,uVar6,uVar8,uVar5);
            uVar8 = uVar5;
          }
        }
        if (uVar8 == uVar4) {
          _iup_worker_shift(&local_34,uVar3,uVar7,uVar8);
        }
        else {
          _iup_worker_interpolate(&local_34,uVar8 + 1 & 0xffff,uVar7,uVar8,uVar4);
          if (uVar4 != 0) {
            _iup_worker_interpolate(&local_34,uVar3,uVar4 - 1,uVar8,uVar4);
          }
        }
      }
      sVar2 = sVar2 + 1;
      uVar3 = uVar5;
    } while (sVar2 < *(short *)((int)param_1 + 0x9a));
  }
  return;
}


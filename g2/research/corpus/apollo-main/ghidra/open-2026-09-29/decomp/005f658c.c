
undefined4 Ins_SHPIX(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 local_18;
  
  if ((((short)param_1[0x57] == 0) || (*(short *)((int)param_1 + 0x15e) == 0)) ||
     ((short)param_1[0x58] == 0)) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  local_18 = param_4;
  if (param_1[4] < param_1[0x4d] + 1) {
    if (*(char *)((int)param_1 + 0x235) != '\0') {
      param_1[3] = 0x86;
    }
  }
  else {
    uVar2 = TT_MulFix14(*param_2,(int)*(short *)((int)param_1 + 0x12e));
    uVar3 = TT_MulFix14(*param_2,(int)(short)param_1[0x4c]);
    while (0 < param_1[0x4d]) {
      param_1[7] = param_1[7] + -1;
      uVar4 = *(uint *)(param_1[6] + param_1[7] * 4);
      if ((uVar4 & 0xffff) < (uint)*(ushort *)(param_1 + 0x1d)) {
        if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
           (*(char *)((int)param_1 + 0x267) != '\0')) {
          if ((bVar1) ||
             ((((char)param_1[0x9a] == '\0' || (*(char *)((int)param_1 + 0x269) == '\0')) &&
              ((((char)param_1[0x8d] != '\0' && ((short)param_1[0x4c] != 0)) ||
               ((int)((uint)*(byte *)(param_1[0x21] + (uVar4 & 0xffff)) << 0x1b) < 0)))))) {
            local_18 = 1;
            Move_Zp2_Point(param_1,uVar4 & 0xffff,0,uVar3);
          }
        }
        else {
          local_18 = 1;
          Move_Zp2_Point(param_1,uVar4 & 0xffff,uVar2,uVar3);
        }
      }
      else if (*(char *)((int)param_1 + 0x235) != '\0') {
        param_1[3] = 0x86;
        return local_18;
      }
      param_1[0x4d] = param_1[0x4d] + -1;
    }
  }
  param_1[0x4d] = 1;
  param_1[8] = param_1[7];
  return local_18;
}


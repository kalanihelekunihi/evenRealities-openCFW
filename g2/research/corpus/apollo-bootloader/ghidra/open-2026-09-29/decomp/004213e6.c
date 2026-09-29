
int FUN_004213e6(byte param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar3 = 0;
  uVar5 = *DAT_00421570 >> 4 & 1;
  uVar1 = *DAT_00421570 >> 3 & 1;
  uVar6 = (*DAT_00421574 & 0xfffffff) >> 0x1b;
  if (param_4 == 0) {
    iVar3 = 6;
  }
  else {
    if (param_1 == 0) {
      if (uVar5 == 0) {
        uVar4 = 0x200;
      }
      else {
        uVar4 = 0x40;
      }
    }
    else if (param_1 == 2) {
      uVar4 = 0x40;
    }
    else if (param_1 < 2) {
      if (uVar1 == 0) {
        uVar4 = 0x600;
      }
      else {
        uVar4 = 0x2c0;
      }
    }
    else if (param_1 == 4) {
      uVar4 = 0x200;
    }
    else if (param_1 < 4) {
      uVar4 = 0x2c0;
    }
    else {
      if (param_1 != 5) {
        return 6;
      }
      uVar4 = 0x600;
    }
    if (uVar4 < (uint)(param_3 + param_2)) {
      iVar3 = 5;
    }
    else {
      if (param_1 == 0) {
        if (uVar5 == 0) {
          iVar2 = FUN_004213d8();
          iVar2 = iVar2 * 4 + 0x42000000;
        }
        else {
          if (uVar6 == 0) {
            return 9;
          }
          iVar2 = DAT_00421578 + param_2 * 4;
        }
      }
      else if (param_1 == 2) {
        if (uVar6 == 0) {
          return 9;
        }
        iVar2 = DAT_00421578 + param_2 * 4;
      }
      else if (param_1 < 2) {
        if (uVar1 == 0) {
          iVar2 = FUN_004213da();
          iVar2 = DAT_00421580 + iVar2 * 4;
        }
        else {
          if (uVar6 == 0) {
            return 9;
          }
          iVar2 = DAT_0042157c + param_2 * 4;
        }
      }
      else if (param_1 == 4) {
        iVar2 = param_2 * 4 + 0x42000000;
      }
      else if (param_1 < 4) {
        if (uVar6 == 0) {
          return 9;
        }
        iVar2 = DAT_0042157c + param_2 * 4;
      }
      else if (param_1 == 5) {
        iVar2 = DAT_00421580 + param_2 * 4;
      }
      else {
        iVar3 = 6;
        iVar2 = param_4;
      }
      if (iVar3 == 0) {
        FUN_0041d28a(iVar2,param_4,param_3);
      }
    }
  }
  return iVar3;
}


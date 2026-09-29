
undefined4 FUN_005e2052(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  short *psVar2;
  int *piVar3;
  int local_110;
  int local_10c;
  int local_108;
  int local_104;
  int local_100;
  int local_fc;
  int local_f8;
  int local_f4;
  undefined1 auStack_f0 [136];
  int local_68;
  int local_64;
  int local_60;
  int local_5c;
  undefined1 auStack_34 [20];
  int local_20;
  int local_1c;
  undefined4 local_18;
  undefined4 local_14;
  
  psVar2 = (short *)param_2[1];
  piVar3 = (int *)*param_2;
  if (param_1 == 0) {
    uVar1 = 6;
  }
  else if ((int)((uint)*(byte *)(param_2 + 2) << 0x1f) < 0) {
    if (psVar2 == (short *)0x0) {
      uVar1 = 0x14;
    }
    else if ((psVar2[1] == 0) || (*psVar2 < 1)) {
      uVar1 = 0;
    }
    else if ((*(int *)(psVar2 + 6) == 0) || (*(int *)(psVar2 + 2) == 0)) {
      uVar1 = 0x14;
    }
    else if ((int)psVar2[1] == *(short *)(*(int *)(psVar2 + 6) + *psVar2 * 2 + -2) + 1) {
      FUN_00439c04(auStack_34,psVar2,0x14);
      if ((int)((uint)*(byte *)(param_2 + 2) << 0x1e) < 0) {
        if (param_2[3] == 0) {
          return 0;
        }
        local_18 = param_2[3];
        local_14 = param_2[7];
      }
      else {
        if (piVar3 == (int *)0x0) {
          return 6;
        }
        if ((piVar3[1] == 0) || (*piVar3 == 0)) {
          return 0;
        }
        if (piVar3[3] == 0) {
          return 6;
        }
        if (piVar3[2] < 0) {
          local_20 = piVar3[3];
        }
        else {
          local_20 = piVar3[3] + piVar3[2] * (*piVar3 + -1);
        }
        local_1c = piVar3[2];
        local_18 = 0;
        local_14 = 0;
      }
      FT_Outline_Get_CBox(psVar2,&local_110);
      if ((((local_110 < -0x1000000) || (DAT_005e263c <= local_108)) || (local_10c < -0x1000000)) ||
         (DAT_005e263c <= local_104)) {
        uVar1 = 0x14;
      }
      else {
        local_110 = local_110 >> 6;
        local_10c = local_10c >> 6;
        local_108 = local_108 + 0x3f >> 6;
        local_104 = local_104 + 0x3f >> 6;
        if ((int)((uint)*(byte *)(param_2 + 2) << 0x1e) < 0) {
          if ((int)((uint)*(byte *)(param_2 + 2) << 0x1d) < 0) {
            FUN_00439c04(&local_100,param_2 + 8,0x10);
          }
          else {
            local_100 = DAT_005e2640;
            local_fc = DAT_005e2640;
            local_f8 = 0x7fff;
            local_f4 = 0x7fff;
          }
        }
        else {
          local_100 = 0;
          local_fc = 0;
          local_f8 = piVar3[1];
          local_f4 = *piVar3;
        }
        local_68 = local_100;
        if (local_100 < local_110) {
          local_68 = local_110;
        }
        local_60 = local_fc;
        if (local_fc < local_10c) {
          local_60 = local_10c;
        }
        local_64 = local_f8;
        if (local_108 < local_f8) {
          local_64 = local_108;
        }
        local_5c = local_f4;
        if (local_104 < local_f4) {
          local_5c = local_104;
        }
        if ((local_68 < local_64) && (local_60 < local_5c)) {
          uVar1 = FUN_005e1f44(auStack_f0);
        }
        else {
          uVar1 = 0;
        }
      }
    }
    else {
      uVar1 = 0x14;
    }
  }
  else {
    uVar1 = 0x13;
  }
  return uVar1;
}


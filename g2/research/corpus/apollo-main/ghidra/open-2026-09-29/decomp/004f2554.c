
void FUN_004f2554(int param_1,int param_2,int param_3)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  undefined4 *puVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int local_7c;
  undefined4 local_78;
  undefined4 local_6c;
  undefined4 local_5c;
  undefined4 local_4c;
  
  piVar3 = DAT_004f2b98;
  piVar2 = DAT_004f2b94;
  piVar1 = DAT_004f27f8;
  if ((*DAT_004f27f8 != 0) && (*DAT_004f306c != 0)) {
    if (*DAT_004f2b98 < *DAT_004f2b94) {
      iVar6 = FUN_0043e2ea(*DAT_004f27f8);
      piVar5 = DAT_004f2ba4;
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3074,0x515,DAT_004f307c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004f3080,DAT_004f3080);
        }
      }
      else {
        iVar6 = (((*piVar2 - *piVar3) + 0x1b) / 0x1c) * -0x1c;
        if (*DAT_004f2ba4 != 0) {
          if (((0 < param_1) && (*DAT_004f2ba0 <= iVar6)) || ((param_1 < 0 && (-1 < *DAT_004f2ba0)))
             ) {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3074,0x520,DAT_004f3120);
            }
            iVar6 = FUN_0043d0ce();
            if ((-1 < iVar6 << 0x1f) && (iVar6 = FUN_0043d0ce(), -1 < iVar6 << 0x1d)) {
              return;
            }
            compress_log_output(0x10000000,DAT_004f3124,DAT_004f3124);
            return;
          }
          FUN_00450500(*piVar1,DAT_004f2e98);
          *piVar5 = 0;
          FUN_0043f142(*piVar1,*DAT_004f2b9c);
        }
        if (param_1 < 1) {
          if (100 < param_2) {
            param_3 = param_3 << 1;
          }
          iVar7 = ((((param_3 + 0x1b) / 0x1c) * 0x1c + *DAT_004f2ba0) / 0x1c) * 0x1c;
          if (0 < iVar7) {
            iVar7 = 0;
          }
        }
        else {
          if (100 < param_2) {
            param_3 = param_3 << 1;
          }
          iVar7 = ((*DAT_004f2ba0 + ((param_3 + 0x1b) / 0x1c) * -0x1c) / 0x1c) * 0x1c;
          if (iVar7 < iVar6) {
            iVar7 = iVar6;
          }
        }
        if (iVar7 == *DAT_004f2ba0) {
          if (*piVar5 == 0) {
            if ((param_1 < 0) && (-1 < *DAT_004f2ba0)) {
              FUN_004f2318();
            }
            else if ((0 < param_1) && (*DAT_004f2ba0 <= iVar6)) {
              FUN_004f23e4();
            }
          }
        }
        else {
          *DAT_004f2ba0 = iVar7;
          FUN_004503d6(&local_7c);
          puVar4 = DAT_004f2b9c;
          local_7c = *piVar1;
          local_78 = DAT_004f31bc;
          FUN_004506ce(&local_7c,*DAT_004f2b9c,iVar7);
          local_4c = 200;
          local_5c = DAT_004f2e9c;
          *DAT_004f2cd8 = 1;
          local_6c = DAT_004f31c0;
          FUN_00450408(&local_7c);
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3074,0x562,DAT_004f31c4,*puVar4,iVar7,
                         param_2);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_004f3360,DAT_004f3360,*puVar4,iVar7,param_2);
          }
        }
      }
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3074,0x510,DAT_004f3070);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f3078,DAT_004f3078);
      }
    }
  }
  return;
}


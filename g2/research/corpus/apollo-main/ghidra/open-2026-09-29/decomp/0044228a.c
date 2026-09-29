
undefined8 FUN_0044228a(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  
  iVar4 = DAT_00442cd8;
  iVar5 = 0;
  do {
    if (*DAT_00442cd4 <= iVar5) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7a;
        param_3 = DAT_00442cfc;
        FUN_0043d574(2,DAT_00442cf4,DAT_00442cf0,DAT_00442cec,0x7a,DAT_00442cfc,param_1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) ||
         (iVar4 = FUN_0043d0ce(), iVar6 = param_2, uVar7 = param_3, iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00442d00,DAT_00442d00,param_1);
        iVar6 = param_2;
        uVar7 = param_3;
      }
LAB_00442452:
      return CONCAT44(uVar7,iVar6);
    }
    if ((*(int *)(DAT_00442cd8 + iVar5 * 0x10) == param_1) &&
       (*(int *)(iVar5 * 0x10 + DAT_00442cd8 + 8) != 0)) {
      iVar6 = param_2;
      uVar7 = param_3;
      if (*(char *)(*(int *)(iVar5 * 0x10 + DAT_00442cd8 + 0xc) + 0xb) == '\0') {
        uVar8 = param_4;
        iVar3 = FUN_0045bbf4();
        piVar1 = DAT_00442cdc;
        if (iVar3 == 0) {
          (**(code **)(iVar5 * 0x10 + iVar4 + 8))
                    (param_2,param_3,param_4,*(undefined4 *)(*DAT_00442cdc + 0x1c));
          if (param_2 == 2) {
            *DAT_00442ce0 = 1;
            FUN_0045f3c8(*piVar1,*(undefined4 *)(iVar4 + iVar5 * 0x10 + 0xc));
          }
        }
        else if ((**(int **)(iVar5 * 0x10 + iVar4 + 0xc) == 0x30) &&
                ((**(code **)(iVar5 * 0x10 + iVar4 + 8))
                           (param_2,param_3,param_4,*(undefined4 *)(*DAT_00442cdc + 0x1c),iVar6,
                            uVar7,uVar8), param_2 == 2)) {
          *DAT_00442ce0 = 1;
          FUN_0045f3c8(*piVar1,*(undefined4 *)(iVar4 + iVar5 * 0x10 + 0xc));
        }
      }
      else if (((*(char *)(*(int *)(iVar5 * 0x10 + DAT_00442cd8 + 0xc) + 0xb) == '\x01') &&
               (iVar3 = FUN_0045bbf4(), piVar1 = DAT_00442cdc, iVar3 == 0)) &&
              ((**(code **)(iVar5 * 0x10 + iVar4 + 8))
                         (param_2,param_3,param_4,*(undefined4 *)(*DAT_00442cdc + 0x20)),
              param_2 == 2)) {
        *DAT_00442ce0 = 2;
        piVar2 = DAT_00442ce4;
        *DAT_00442ce4 = *(int *)(iVar4 + iVar5 * 0x10);
        FUN_0045f3c8(*piVar1,*(undefined4 *)(iVar5 * 0x10 + iVar4 + 0xc));
        if ((*piVar2 == 7) || (*piVar2 == 4)) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            iVar6 = 0x6c;
            uVar7 = DAT_00442ce8;
            FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442cec,0x6c,DAT_00442ce8,*piVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00442cf8,DAT_00442cf8,*piVar2);
          }
          FUN_0045fe32(*piVar2,1);
        }
        FUN_0045f876(*piVar1,**(undefined4 **)(iVar4 + iVar5 * 0x10 + 0xc));
      }
      goto LAB_00442452;
    }
    iVar5 = iVar5 + 1;
  } while( true );
}


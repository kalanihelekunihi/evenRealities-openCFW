
undefined1 FUN_0054418e(undefined4 *param_1,uint param_2,undefined1 *param_3,uint param_4)

{
  undefined1 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 uVar4;
  undefined1 uStack_88;
  undefined1 auStack_87 [3];
  undefined4 local_84;
  int local_80;
  char local_78;
  char local_77;
  int local_70;
  int local_28;
  uint uStack_20;
  
  uVar4 = 0;
  uStack_20 = param_4;
  FUN_0043c0e4(&uStack_88,0x10,0);
  if (param_2 != param_1[3] * (param_2 / (uint)param_1[3])) {
    FUN_004733ee(DAT_00544b6c);
    uVar2 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00544b70,*param_1,uVar2);
    FUN_004733ee(DAT_00544ce0,DAT_00544cdc,DAT_00544cd8);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_3 == (undefined1 *)0x0) {
    FUN_004733ee(DAT_00544b6c);
    uVar2 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00544b70,*param_1,uVar2);
    FUN_004733ee(DAT_00544ce0,DAT_00544ce4,DAT_00544cd8);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iVar3 = FUN_00543cc0(param_1,param_2);
  if ((iVar3 == 0) ||
     (((param_4 & 0xff) != 0 && (((param_4 & 0xff) == 0 || (*(int *)(iVar3 + 0x14) == -1)))))) {
    FUN_00585a12(param_1,param_2,&uStack_88,0x10);
    param_3[1] = 0;
    param_3[2] = 0;
    *(uint *)(param_3 + 4) = param_2;
    *(undefined4 *)(param_3 + 8) = local_84;
    if ((*(int *)(param_3 + 8) == DAT_00544ce8) && ((local_80 == -1 || (local_80 == 0)))) {
      *param_3 = 1;
      *(int *)(param_3 + 0xc) = local_80;
      uVar1 = FUN_005858a8(&uStack_88,4);
      param_3[1] = uVar1;
      uVar1 = FUN_005858a8(auStack_87,4);
      param_3[2] = uVar1;
      if ((param_4 & 0xff) == 0) {
        iVar3 = FUN_00543cc0(param_1,*(undefined4 *)(param_3 + 4));
        if (iVar3 == 0) {
          *(undefined4 *)(param_3 + 0x14) = 0xffffffff;
          *(undefined4 *)(param_3 + 0x10) = 0;
          FUN_00543c48(param_1,param_3);
        }
      }
      else {
        *(undefined4 *)(param_3 + 0x10) = 0;
        *(int *)(param_3 + 0x14) = *(int *)(param_3 + 4) + 0x10;
        if (param_3[1] == '\x01') {
          *(int *)(param_3 + 0x10) = param_1[3] + -0x10;
        }
        else if (param_3[1] == '\x02') {
          *(int *)(param_3 + 0x10) = param_1[3] + -0x10;
          local_28 = *(int *)(param_3 + 4) + 0x10;
          do {
            FUN_00544000(param_1,&local_78);
            if (((local_77 == '\0') && (local_78 != '\x01')) && (local_78 != '\x05')) {
              *(undefined4 *)(param_3 + 0x10) = 0;
              uVar4 = 2;
              break;
            }
            *(int *)(param_3 + 0x14) = local_70 + *(int *)(param_3 + 0x14);
            *(int *)(param_3 + 0x10) = *(int *)(param_3 + 0x10) - local_70;
            local_28 = FUN_00543f8c(param_1,param_3,&local_78);
          } while (local_28 != -1);
          iVar3 = FUN_005859a0(param_1,*(undefined4 *)(param_3 + 0x14),
                               param_1[3] + *(int *)(param_3 + 4));
          if (*(int *)(param_3 + 0x14) != iVar3) {
            *(int *)(param_3 + 0x14) = iVar3;
            *(int *)(param_3 + 0x10) = *(int *)(param_3 + 4) + (param_1[3] - iVar3);
          }
        }
        FUN_00543c48(param_1,param_3);
      }
    }
    else {
      *param_3 = 0;
      *(undefined4 *)(param_3 + 0xc) = 0xffffffff;
      uVar4 = 8;
    }
  }
  else {
    FUN_00439be4(param_3,iVar3,0x18);
    uVar4 = 0;
  }
  return uVar4;
}


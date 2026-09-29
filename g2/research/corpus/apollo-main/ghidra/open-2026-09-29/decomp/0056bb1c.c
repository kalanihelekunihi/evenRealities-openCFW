
undefined8 attcDiscProcCharDecl(undefined4 *param_1,uint param_2,byte *param_3)

{
  ushort uVar1;
  int iVar2;
  ushort uVar3;
  byte *pbVar4;
  byte bVar5;
  undefined4 *puVar6;
  uint uVar7;
  
  uVar1 = (ushort)param_3[1] * 0x100 + (ushort)*param_3;
  uVar3 = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
  pbVar4 = param_3 + 5;
  if (*(char *)((int)param_1 + 0x13) != -1) {
    *(ushort *)(param_1[1] + (uint)*(byte *)((int)param_1 + 0x13) * 2) = uVar1 - 1;
    *(undefined1 *)((int)param_1 + 0x13) = 0xff;
  }
  if ((uVar1 < uVar3) && (uVar3 <= *(ushort *)(param_1 + 4))) {
    puVar6 = (undefined4 *)*param_1;
    uVar7 = param_2;
    for (bVar5 = 0; bVar5 < *(byte *)(param_1 + 3); bVar5 = bVar5 + 1) {
      if ((*(short *)(param_1[1] + (uint)bVar5 * 2) == 0) &&
         (iVar2 = attcUuidCmp(*puVar6,pbVar4,param_2 & 0xff), iVar2 != 0)) {
        *(ushort *)(param_1[1] + (uint)bVar5 * 2) = uVar3;
        if (((int)(uint)bVar5 < (int)(*(byte *)(param_1 + 3) - 1)) &&
           ((int)((uint)*(byte *)(puVar6[1] + 4) << 0x1d) < 0)) {
          *(byte *)((int)param_1 + 0x13) = bVar5 + 1;
        }
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c1e8,&DAT_0056bc14,3), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c1e8,DAT_0056c34c,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c1e8,DAT_0056c1e8,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if (iVar2 == 0) {
                iVar2 = FUN_004c9c50();
                if ((iVar2 == 0) ||
                   (iVar2 = FUN_0044b610(&DAT_0056be24,&DAT_0056bcfc,3), iVar2 != 0)) {
                  WsfTrace(DAT_0056c1e8,DAT_0056c358,uVar3);
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  uVar7 = 0x185;
                  param_3 = DAT_0056c358;
                  FUN_0043d574(4,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x185,DAT_0056c358,uVar3);
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                uVar7 = 0x185;
                param_3 = DAT_0056c358;
                FUN_0043d574(3,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x185,DAT_0056c358,uVar3);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              uVar7 = 0x185;
              param_3 = DAT_0056c358;
              FUN_0043d574(2,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x185,DAT_0056c358,uVar3);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar7 = 0x185;
            param_3 = DAT_0056c358;
            FUN_0043d574(1,&DAT_0056bc18,DAT_0056c1f4,DAT_0056c35c,0x185,DAT_0056c358,uVar3);
          }
        }
        break;
      }
      puVar6 = puVar6 + 1;
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,&DAT_0056be28,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c34c,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c1e8,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) ||
               (iVar2 = FUN_0044b610(&DAT_0056be24,&DAT_0056be2c,3), uVar7 = param_2, iVar2 != 0)) {
              WsfTrace(DAT_0056c34c,DAT_0056c368,uVar3);
              uVar7 = param_2;
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            uVar7 = param_2;
            if (iVar2 << 0x1e < 0) {
              uVar7 = 0x18e;
              param_3 = DAT_0056c368;
              FUN_0043d574(4,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x18e,DAT_0056c368,uVar3);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          uVar7 = param_2;
          if (iVar2 << 0x1e < 0) {
            uVar7 = 0x18e;
            param_3 = DAT_0056c368;
            FUN_0043d574(3,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x18e,DAT_0056c368,uVar3);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        uVar7 = param_2;
        if (iVar2 << 0x1e < 0) {
          uVar7 = 0x18e;
          param_3 = DAT_0056c368;
          FUN_0043d574(2,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x18e,DAT_0056c368,uVar3);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      uVar7 = param_2;
      if (iVar2 << 0x1e < 0) {
        uVar7 = 0x18e;
        param_3 = DAT_0056c368;
        FUN_0043d574(1,&DAT_0056be24,DAT_0056c1f4,DAT_0056c35c,0x18e,DAT_0056c368,uVar3);
      }
    }
  }
  return CONCAT44(param_3,uVar7);
}



void FUN_005c1aae(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined1 auStack_24 [8];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  cVar2 = FUN_004516f8(DAT_005c213c,param_2);
  if (cVar2 == '\x01') {
    iVar4 = FUN_00450286(param_2);
    iVar5 = *param_2;
    if ((iVar4 == 0x1b) && (iVar6 = FUN_005c28ae(iVar5), iVar6 != 0)) {
      if (*(int *)(iVar5 + 0x3c) == 0) {
        uVar7 = 0;
      }
      else {
        uVar7 = FUN_0043fe70(iVar5);
        uVar7 = uVar7 / *(uint *)(iVar5 + 0x3c);
      }
      FUN_004519fa(param_2,uVar7);
    }
    if (iVar4 == 0x32) {
      FUN_005c2904(iVar5);
    }
    else if (iVar4 == 0x31) {
      FUN_005c2904(iVar5);
    }
    else if (iVar4 == 1) {
      uVar8 = FUN_004518d8(param_2);
      FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
      FUN_00452ef8();
      cVar2 = FUN_00452f00();
      if ((cVar2 == '\x01') || (cVar2 == '\x03')) {
        FUN_00452f5e(uVar8,auStack_24);
        iVar4 = FUN_005c2622(iVar5,auStack_24);
        *(undefined4 *)(iVar5 + 0x40) = 0xffff;
        if (iVar4 == 0xffff) {
          *(undefined4 *)(iVar5 + 0x40) = 0xffff;
        }
        else {
          iVar6 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + iVar4 * 2));
          if ((iVar6 == 0) &&
             (iVar6 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + iVar4 * 2)), iVar6 == 0)
             ) {
            *(int *)(iVar5 + 0x40) = iVar4;
            FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
          }
        }
      }
      if ((((*(int *)(iVar5 + 0x40) != 0xffff) &&
           (iVar4 = FUN_005c25fe(*(undefined2 *)
                                  (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)), iVar4 == 0
           )) && (iVar4 = FUN_005c2608(*(undefined2 *)
                                        (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
                 iVar4 == 0)) &&
         ((iVar4 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)
                               ), iVar4 == 0 &&
          (iVar4 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)
                               ), iVar4 == 0)))) {
        local_28 = *(undefined4 *)(iVar5 + 0x40);
        FUN_00451670(iVar5,0x23,&local_28);
      }
    }
    else if (iVar4 == 2) {
      if (*(int *)(iVar5 + 0x40) != 0xffff) {
        uVar8 = FUN_004518d8(param_2);
        cVar2 = FUN_00452f00(uVar8);
        if ((cVar2 == '\x01') || (cVar2 == '\x03')) {
          FUN_00452f5e(uVar8,auStack_24);
          iVar4 = FUN_005c2622(iVar5,auStack_24);
          if (iVar4 != *(int *)(iVar5 + 0x40)) {
            FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
            *(undefined4 *)(iVar5 + 0x40) = 0xffff;
          }
        }
      }
    }
    else if (iVar4 == 0xb) {
      if (*(int *)(iVar5 + 0x40) != 0xffff) {
        iVar4 = FUN_005c2612(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
        if ((iVar4 != 0) &&
           (iVar4 = FUN_005c25f4(*(undefined2 *)
                                  (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)), iVar4 == 0
           )) {
          iVar4 = FUN_005c2618(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2))
          ;
          if ((iVar4 == 0) || ((int)((uint)*(byte *)(iVar5 + 0x44) << 0x1f) < 0)) {
            *(ushort *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2) =
                 *(ushort *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2) | 0x100;
          }
          else {
            *(ushort *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2) =
                 *(ushort *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2) & 0xfeff;
          }
          if ((int)((uint)*(byte *)(iVar5 + 0x44) << 0x1f) < 0) {
            FUN_005c287c(iVar5,*(undefined4 *)(iVar5 + 0x40));
          }
        }
        iVar4 = FUN_005c25fe(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
        if ((((iVar4 == 1) ||
             (iVar4 = FUN_005c2608(*(undefined2 *)
                                    (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
             iVar4 == 1)) &&
            (iVar4 = FUN_005c25f4(*(undefined2 *)
                                   (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
            iVar4 == 0)) &&
           (iVar4 = FUN_005c25d6(*(undefined2 *)
                                  (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)), iVar4 == 0
           )) {
          local_2c = *(undefined4 *)(iVar5 + 0x40);
          cVar2 = FUN_00451670(iVar5,0x23,&local_2c);
          if (cVar2 != '\x01') {
            return;
          }
        }
      }
      FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
    }
    else if (iVar4 == 9) {
      if (((*(int *)(iVar5 + 0x40) != 0xffff) &&
          (iVar4 = FUN_005c25ea(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)
                               ), iVar4 == 0)) &&
         ((iVar4 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)
                               ), iVar4 == 0 &&
          (iVar4 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)
                               ), iVar4 == 0)))) {
        local_30 = *(undefined4 *)(iVar5 + 0x40);
        FUN_00451670(iVar5,0x23,&local_30);
      }
    }
    else if (iVar4 == 3) {
      FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
      *(undefined4 *)(iVar5 + 0x40) = 0xffff;
    }
    else if (iVar4 == 0x13) {
      if (*(int *)(iVar5 + 0x38) != 0) {
        iVar4 = FUN_004518d8(param_2);
        cVar2 = FUN_00452f00(iVar4);
        if (iVar4 == 0) {
          FUN_00452edc(0);
          cVar2 = FUN_00452f00();
        }
        FUN_0043e1be(iVar5);
        cVar3 = FUN_0044d5a4();
        if (*(int *)(iVar5 + 0x40) == 0xffff) {
          if ((cVar2 == '\x02') || ((cVar2 == '\x04' && (cVar3 != '\0')))) {
            uVar7 = 0;
            if ((int)((uint)*(byte *)(iVar5 + 0x44) << 0x1f) < 0) {
              while ((uVar7 < *(uint *)(iVar5 + 0x38) &&
                     (((iVar4 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                       iVar4 != 0 ||
                       (iVar4 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                       iVar4 != 0)) ||
                      (iVar4 = FUN_005c25e0(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                      iVar4 == 0))))) {
                uVar7 = uVar7 + 1;
              }
            }
            else {
              while ((uVar7 < *(uint *)(iVar5 + 0x38) &&
                     ((iVar4 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                      iVar4 != 0 ||
                      (iVar4 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                      iVar4 != 0))))) {
                uVar7 = uVar7 + 1;
              }
            }
            *(uint *)(iVar5 + 0x40) = uVar7;
          }
          else {
            *(undefined4 *)(iVar5 + 0x40) = 0xffff;
          }
        }
      }
    }
    else if ((iVar4 != 0x14) && (iVar4 != 0x15)) {
      if (iVar4 == 0x11) {
        FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
        iVar4 = FUN_004519a0(param_2);
        if (iVar4 == 0x13) {
          if (*(int *)(iVar5 + 0x40) == 0xffff) {
            *(undefined4 *)(iVar5 + 0x40) = 0;
          }
          else {
            *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + 1;
          }
          if (*(uint *)(iVar5 + 0x38) <= *(uint *)(iVar5 + 0x40)) {
            *(undefined4 *)(iVar5 + 0x40) = 0;
          }
          iVar4 = *(int *)(iVar5 + 0x40);
          do {
            iVar6 = FUN_005c25d6(*(undefined2 *)
                                  (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
            if ((iVar6 == 0) &&
               (iVar6 = FUN_005c25f4(*(undefined2 *)
                                      (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
               iVar6 == 0)) goto LAB_005c210c;
            *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + 1;
            if (*(uint *)(iVar5 + 0x38) <= *(uint *)(iVar5 + 0x40)) {
              *(undefined4 *)(iVar5 + 0x40) = 0;
            }
          } while (*(int *)(iVar5 + 0x40) != iVar4);
          *(undefined4 *)(iVar5 + 0x40) = 0xffff;
        }
        else if (iVar4 == 0x14) {
          if (*(int *)(iVar5 + 0x40) == 0xffff) {
            *(undefined4 *)(iVar5 + 0x40) = 0;
          }
          if (*(int *)(iVar5 + 0x40) == 0) {
            *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x38) + -1;
          }
          else if (*(int *)(iVar5 + 0x40) != 0) {
            *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + -1;
          }
          iVar4 = *(int *)(iVar5 + 0x40);
          do {
            iVar6 = FUN_005c25d6(*(undefined2 *)
                                  (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
            if ((iVar6 == 0) &&
               (iVar6 = FUN_005c25f4(*(undefined2 *)
                                      (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
               iVar6 == 0)) goto LAB_005c210c;
            if (*(int *)(iVar5 + 0x40) == 0) {
              *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x38) + -1;
            }
            else {
              *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + -1;
            }
          } while (*(int *)(iVar5 + 0x40) != iVar4);
          *(undefined4 *)(iVar5 + 0x40) = 0xffff;
        }
        else if (iVar4 == 0x12) {
          iVar4 = FUN_005c1638(iVar5,0);
          if (*(int *)(iVar5 + 0x40) == 0xffff) {
            *(undefined4 *)(iVar5 + 0x40) = 0;
            do {
              iVar4 = FUN_005c25d6(*(undefined2 *)
                                    (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
              if ((iVar4 == 0) &&
                 (iVar4 = FUN_005c25f4(*(undefined2 *)
                                        (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
                 iVar4 == 0)) goto LAB_005c210c;
              *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + 1;
            } while (*(uint *)(iVar5 + 0x40) < *(uint *)(iVar5 + 0x38));
            *(undefined4 *)(iVar5 + 0x40) = 0xffff;
          }
          else {
            iVar6 = FUN_00451598(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10);
            iVar6 = *(int *)(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10) + (iVar6 >> 1);
            uVar7 = *(uint *)(iVar5 + 0x40);
            while ((uVar7 < *(uint *)(iVar5 + 0x38) &&
                   ((((*(int *)(*(int *)(iVar5 + 0x30) + uVar7 * 0x10 + 4) <=
                       *(int *)(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10 + 4) ||
                      (iVar6 < *(int *)(*(int *)(iVar5 + 0x30) + uVar7 * 0x10))) ||
                     (iVar4 + *(int *)(*(int *)(iVar5 + 0x30) + uVar7 * 0x10 + 8) < iVar6)) ||
                    ((iVar9 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                     iVar9 != 0 ||
                     (iVar9 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + uVar7 * 2)),
                     iVar9 != 0))))))) {
              uVar7 = uVar7 + 1;
            }
            if (uVar7 < *(uint *)(iVar5 + 0x38)) {
              *(uint *)(iVar5 + 0x40) = uVar7;
            }
          }
        }
        else if (iVar4 == 0x11) {
          iVar4 = FUN_005c1638(iVar5,0);
          if (*(int *)(iVar5 + 0x40) == 0xffff) {
            *(undefined4 *)(iVar5 + 0x40) = 0;
            do {
              iVar4 = FUN_005c25d6(*(undefined2 *)
                                    (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2));
              if ((iVar4 == 0) &&
                 (iVar4 = FUN_005c25f4(*(undefined2 *)
                                        (*(int *)(iVar5 + 0x34) + *(int *)(iVar5 + 0x40) * 2)),
                 iVar4 == 0)) goto LAB_005c210c;
              *(int *)(iVar5 + 0x40) = *(int *)(iVar5 + 0x40) + 1;
            } while (*(uint *)(iVar5 + 0x40) < *(uint *)(iVar5 + 0x38));
            *(undefined4 *)(iVar5 + 0x40) = 0xffff;
          }
          else {
            iVar6 = FUN_00451598(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10);
            iVar6 = *(int *)(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10) + (iVar6 >> 1);
            iVar9 = *(int *)(iVar5 + 0x40);
            while ((sVar1 = (short)iVar9, -1 < sVar1 &&
                   ((((*(int *)(*(int *)(iVar5 + 0x30) + *(int *)(iVar5 + 0x40) * 0x10 + 4) <=
                       *(int *)(*(int *)(iVar5 + 0x30) + sVar1 * 0x10 + 4) ||
                      (iVar6 < *(int *)(*(int *)(iVar5 + 0x30) + sVar1 * 0x10) - iVar4)) ||
                     (*(int *)(*(int *)(iVar5 + 0x30) + sVar1 * 0x10 + 8) < iVar6)) ||
                    ((iVar10 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar5 + 0x34) + sVar1 * 2)),
                     iVar10 != 0 ||
                     (iVar10 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar5 + 0x34) + sVar1 * 2)),
                     iVar10 != 0))))))) {
              iVar9 = iVar9 + -1;
            }
            if (-1 < sVar1) {
              *(int *)(iVar5 + 0x40) = (int)sVar1;
            }
          }
        }
LAB_005c210c:
        FUN_005c27b8(iVar5,*(undefined4 *)(iVar5 + 0x40));
      }
      else if (iVar4 == 0x1d) {
        FUN_005c215c(param_2);
      }
      else if ((iVar4 == 0x29) && (*(int *)(iVar5 + 0x44) << 0x1e < 0)) {
        FUN_005c2ac8(iVar5);
      }
    }
  }
  return;
}



void APP_BleServerDiscCback(undefined1 param_1,byte param_2)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  undefined2 *puVar4;
  char cVar5;
  
  if (param_2 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar2 = DmConnRole(param_1);
      FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x121,DAT_005360a0,uVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar2 = DmConnRole(param_1);
      compress_log_output(0x10400000,DAT_005360b0,DAT_005360b0,uVar2);
    }
    iVar3 = DmConnRole(param_1);
    piVar1 = DAT_005360b4;
    if (iVar3 == 0) {
      *(undefined1 *)(*DAT_005360b4 + 0x57) = 0;
      FUN_00532eb4(param_1,5,*piVar1);
    }
    else {
      *(undefined1 *)(*DAT_005360b4 + 0x57) = 0;
      FUN_00532eb4(param_1,8,*piVar1 + 0x2a);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x131,DAT_005360b8,
                   *(undefined1 *)(*DAT_005360b4 + 0x57));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005360bc,DAT_005360bc,*(undefined1 *)(*DAT_005360b4 + 0x57)
                         );
    }
  }
  else if (param_2 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x13b,DAT_005360c8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005360cc,DAT_005360cc);
    }
    iVar3 = DmConnRole(param_1);
    if (iVar3 == 0) {
      FUN_00503ea8(param_1);
    }
  }
  else if (param_2 < 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x135,DAT_005360c0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005360c4,DAT_005360c4);
    }
    FUN_005336e0(param_1);
  }
  else {
    if (param_2 != 4) {
      if (param_2 < 4) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x148,DAT_005360d0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_005360d4,DAT_005360d4);
        }
        piVar1 = DAT_005360b4;
        *(undefined1 *)(*DAT_005360b4 + 0x5a) = 0;
        iVar3 = DmConnRole(param_1);
        if (iVar3 == 0) {
          *(undefined1 *)(*piVar1 + 0x57) = 0;
          GattDiscover(param_1,*DAT_005360d8);
          return;
        }
        *(undefined1 *)(*piVar1 + 0x57) = 0;
        GattDiscover(param_1,*DAT_005360dc);
        return;
      }
      if (param_2 == 6) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x210,DAT_0053616c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00536170,DAT_00536170);
        }
        iVar3 = DmConnRole(param_1);
        if (iVar3 == 0) {
          FUN_00533474(param_1,6,2,DAT_00536120,5,*DAT_005360b4);
          return;
        }
        FUN_00533474(param_1,6,4,DAT_00536168,8,*DAT_005360b4 + 0x2a);
        return;
      }
      if (5 < param_2) {
        if (param_2 != 8) {
          if (7 < param_2) {
            return;
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x234,DAT_00536184);
          }
          iVar3 = FUN_0043d0ce();
          if ((-1 < iVar3 << 0x1f) && (iVar3 = FUN_0043d0ce(), -1 < iVar3 << 0x1d)) {
            return;
          }
          compress_log_output(0x10000000,DAT_00536188,DAT_00536188);
          return;
        }
        FUN_0053303c(param_1,8);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x223,DAT_00536174);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00536178,DAT_00536178);
        }
        iVar3 = DmConnRole(param_1);
        piVar1 = DAT_0053613c;
        if (iVar3 == 0) {
          Thread_SendEvtToRingTask(4);
          return;
        }
        if (*DAT_0053613c == 0) {
          return;
        }
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x22e,DAT_0053617c,
                       *(undefined2 *)*piVar1,*(undefined2 *)(*piVar1 + 2),
                       *(undefined2 *)(*piVar1 + 4),*(undefined2 *)(*piVar1 + 6),
                       *(undefined2 *)(*piVar1 + 8));
        }
        iVar3 = FUN_0043d0ce();
        if ((-1 < iVar3 << 0x1f) && (iVar3 = FUN_0043d0ce(), -1 < iVar3 << 0x1d)) {
          return;
        }
        compress_log_output(0x11400000,DAT_00536180,DAT_00536180,*(undefined2 *)*piVar1,
                            *(undefined2 *)(*piVar1 + 2),*(undefined2 *)(*piVar1 + 4),
                            *(undefined2 *)(*piVar1 + 6),*(undefined2 *)(*piVar1 + 8));
        return;
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        uVar2 = DmConnRole(param_1);
        FUN_0043d574(2,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x16e,DAT_005360e0,
                     *(undefined1 *)(*DAT_005360b4 + 0x57),uVar2,0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        uVar2 = DmConnRole(param_1);
        compress_log_output(0x8c00000,DAT_005360e4,DAT_005360e4,
                            *(undefined1 *)(*DAT_005360b4 + 0x57),uVar2,0);
      }
      *(char *)(*DAT_005360b4 + 0x57) = *(char *)(*DAT_005360b4 + 0x57) + '\x01';
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar2 = DmConnRole(param_1);
      FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x19d,DAT_005360e8,
                   *(undefined1 *)(*DAT_005360b4 + 0x57),uVar2,0,param_2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar2 = DmConnRole(param_1);
      compress_log_output(0x11000000,DAT_005360ec,DAT_005360ec,*(undefined1 *)(*DAT_005360b4 + 0x57)
                          ,uVar2,0,param_2);
    }
    if ((param_2 == 4) || (param_2 == 8)) {
      iVar3 = DmConnRole(param_1);
      piVar1 = DAT_005360b4;
      if ((iVar3 == 1) && (*(char *)(*DAT_005360b4 + 0x57) == '\x01')) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1b1,DAT_005360f8);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005360fc,DAT_005360fc);
        }
        *(undefined1 *)(*piVar1 + 0x5a) = 0;
      }
      piVar1 = DAT_005360b4;
      if (param_2 == 4) {
        *(char *)(*DAT_005360b4 + 0x57) = *(char *)(*DAT_005360b4 + 0x57) + '\x01';
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1bd,DAT_00536100,
                       *(undefined1 *)(*piVar1 + 0x57),1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_00536104,DAT_00536104,*(undefined1 *)(*piVar1 + 0x57),1)
          ;
        }
      }
      iVar3 = DmConnRole(param_1);
      piVar1 = DAT_005360b4;
      if (iVar3 == 0) {
        if (*(char *)(*DAT_005360b4 + 0x57) == '\x01') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            uVar2 = DmConnRole(param_1);
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1c7,DAT_00536108,
                         *(undefined1 *)(*piVar1 + 0x57),uVar2,0);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            uVar2 = DmConnRole(param_1);
            compress_log_output(0x10c00000,DAT_0053610c,DAT_0053610c,*(undefined1 *)(*piVar1 + 0x57)
                                ,uVar2,0);
          }
          APP_BleRingSvcDiscover(param_1,*DAT_0053609c);
        }
        else if (*(char *)(*DAT_005360b4 + 0x57) == '\x02') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1cf,DAT_00536110);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00536114,DAT_00536114);
          }
          puVar4 = (undefined2 *)*piVar1;
          for (cVar5 = '\x05'; cVar5 != '\0'; cVar5 = cVar5 + -1) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1d4,DAT_00536118,*puVar4);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0053611c,DAT_0053611c,*puVar4);
            }
            puVar4 = puVar4 + 1;
          }
          FUN_0053303c(param_1,4);
          FUN_00533474(param_1,6,2,DAT_00536120,5,*piVar1);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uVar2 = FUN_004b8128();
          FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1e4,DAT_00536124,
                       *(undefined1 *)(*DAT_005360b4 + 0x57),1,uVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          uVar2 = FUN_004b8128();
          compress_log_output(0x10c00000,DAT_00536128,DAT_00536128,
                              *(undefined1 *)(*DAT_005360b4 + 0x57),1,uVar2);
        }
        piVar1 = DAT_005360b4;
        if (*(char *)(*DAT_005360b4 + 0x57) == '\x01') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1e7,DAT_0053612c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00536130,DAT_00536130);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(3,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1eb,DAT_00536134);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_00536138,DAT_00536138);
          }
          iVar3 = APP_BleAnccSvcDiscover(param_1,*DAT_0053613c);
          if (iVar3 == 0) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(2,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1ef,DAT_00536148);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_0053614c,DAT_0053614c);
            }
            *(char *)(*piVar1 + 0x57) = *(char *)(*piVar1 + 0x57) + '\x01';
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1ed,DAT_00536140);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_00536144,DAT_00536144);
            }
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1fc,DAT_00536150,
                         *(undefined1 *)(*piVar1 + 0x57),1);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_00536154,DAT_00536154,*(undefined1 *)(*piVar1 + 0x57),
                                1);
          }
        }
        if (*(char *)(*piVar1 + 0x57) == '\x02') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x203,DAT_00536110);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00536114,DAT_00536114);
          }
          FUN_0053303c(param_1,4);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x205,DAT_00536158);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0053615c,DAT_0053615c);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x207,DAT_00536160);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00536164,DAT_00536164);
          }
          FUN_00533474(param_1,6,4,DAT_00536168,8,*piVar1 + 0x2a);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005360ac,DAT_005360a8,DAT_005360a4,0x1a3,DAT_005360f0,
                     *(undefined1 *)(*DAT_005360b4 + 0x57));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005360f4,DAT_005360f4,
                            *(undefined1 *)(*DAT_005360b4 + 0x57));
      }
      *(char *)(*DAT_005360b4 + 0x57) = *(char *)(*DAT_005360b4 + 0x57) + '\x01';
    }
  }
  return;
}



void FUN_004f6a10(void)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  char *pcVar5;
  short *psVar6;
  int iVar7;
  char local_28;
  undefined4 local_27;
  
  piVar2 = DAT_004f6fb8;
  *DAT_004f6fb8 = 0;
  piVar3 = DAT_004f7164;
  if (((*DAT_004f7164 != 0) &&
      (iVar7 = ui_common_api_fn_00509dfa(*DAT_004f7164), piVar4 = DAT_004f7168, iVar7 == 0)) &&
     (*DAT_004f7168 == 1)) {
    FUN_0043c0e4(&local_28,10,0);
    FUN_0043c0e4(&local_28,10,0);
    ui_common_api_fn_00509e14(*piVar3,&local_28,5);
    psVar6 = DAT_004f7170;
    pcVar5 = DAT_004f716c;
    piVar1 = DAT_004f6d20;
    if (local_28 == '\n') {
      if (*DAT_004f716c == '\0') {
        if (*DAT_004f7170 != 0) {
          if (*DAT_004f6d20 < 0) {
            FUN_004f7ae4(0);
          }
          else {
            FUN_004f7ae4(*DAT_004f6d20);
          }
        }
      }
      else if ((*DAT_004f716c == '\x02') && (-1 < *DAT_004f6d20)) {
        FUN_004f7cb0(*DAT_004f6d20);
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f7178,0x652,DAT_004f7174,*pcVar5,
                       *DAT_004f6d20);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004f717c,DAT_004f717c,*pcVar5,*DAT_004f6d20);
        }
      }
    }
    else if (local_28 == 'D') {
      if (*DAT_004f716c == '\0') {
        if (*DAT_004f7170 != 0) {
          if (*DAT_004f6d20 < 0) {
            FUN_004f7ae4(0);
          }
          else {
            FUN_004f7ae4(*DAT_004f6d20);
          }
        }
      }
      else if ((*DAT_004f716c == '\x02') && (-1 < *DAT_004f6d20)) {
        iVar7 = FUN_004f61a0(2);
        if (iVar7 != 0) {
          FUN_004f6282(2);
        }
        FUN_004f7c10(*piVar1 + 1);
      }
    }
    else if (local_28 == 'E') {
      if (*DAT_004f716c == '\0') {
        if (*DAT_004f7170 != 0) {
          if (*DAT_004f6d20 < 0) {
            FUN_004f7ae4(0);
          }
          else {
            FUN_004f7ae4(*DAT_004f6d20);
          }
        }
      }
      else if ((*DAT_004f716c == '\x02') && (-1 < *DAT_004f6d20)) {
        iVar7 = FUN_004f61a0(1);
        if (iVar7 != 0) {
          FUN_004f6282(1);
        }
        FUN_004f7c10(*piVar1 + -1);
      }
    }
    else if (local_28 != 'F') {
      if (local_28 == 'G') {
        if ((local_27 & 0xff) == 0) {
          *(undefined1 *)(DAT_004f7170 + 0x1727) = local_27._1_1_;
          psVar6[0x1724] = local_27._2_2_;
          piVar1 = DAT_004f73f0;
          if (((*piVar4 == 1) && (*piVar3 != 0)) && ((*piVar2 == 0 && (*DAT_004f73f0 != 0)))) {
            *piVar2 = 2;
            if ((*psVar6 == 0) || (*DAT_004f716c == '\0')) {
              FUN_004fb1a4(*piVar1,1);
            }
            FUN_004fac74(*piVar1);
            if (*piVar2 == 2) {
              *piVar2 = 0;
            }
          }
          *(undefined1 *)(psVar6 + 0x1727) = 0;
          psVar6[0x1724] = 0;
        }
        else if (((((local_27 & 0xff) == 1) && (*piVar4 == 1)) && (*piVar3 != 0)) &&
                (*DAT_004f73f0 != 0)) {
          FUN_004f74f8(0,100,DAT_004f73f4);
        }
      }
      else if (local_28 == 'H') {
        if (*DAT_004f716c == '\x02') {
          FUN_004f7b84();
        }
        else if (*DAT_004f716c == '\0') {
          FUN_004faf20();
        }
      }
      else if (local_28 == 'I') {
        FUN_004e8a90();
        *piVar4 = 0;
        *piVar2 = 0;
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004f6d3c,DAT_004f6d38,DAT_004f7178,0x683,DAT_004f7478,local_28);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004f7620,DAT_004f7620,local_28);
        }
      }
    }
  }
  return;
}


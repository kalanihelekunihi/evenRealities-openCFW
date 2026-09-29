
undefined4 FUN_0052f442(void)

{
  int *piVar1;
  uint *puVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 in_r3;
  undefined4 local_28;
  undefined4 local_24;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  uStack_18 = in_r3;
  uVar4 = FUN_0052f3a0(1);
  uVar7 = DAT_0052fcf0;
  piVar1 = DAT_0052fcec;
  iVar5 = file_open(DAT_0052fcf0,uVar4);
  *piVar1 = iVar5;
  if (*piVar1 == 0) {
    iVar5 = -1;
  }
  else {
    iVar5 = 0;
  }
  if (iVar5 == 0) {
    iVar5 = FUN_0052f3f8(*piVar1);
    if (iVar5 < 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0x9d,DAT_0052ff54);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0052ff58);
      }
      if (*piVar1 != 0) {
        file_close(*piVar1);
        *piVar1 = 0;
      }
      uVar7 = 0;
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xa2,DAT_0052ff5c,iVar5);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0052ff60,DAT_0052ff60,iVar5);
      }
      puVar2 = DAT_0052ff64;
      *DAT_0052ff64 = iVar5 + 3U & 0xfffffffc;
      piVar3 = DAT_0052ff68;
      iVar6 = file_heap_allocate(*puVar2);
      *piVar3 = iVar6;
      if (*piVar3 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xa8,DAT_0052ff6c,*puVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0052ff70,DAT_0052ff70,*puVar2);
        }
        if (*piVar1 != 0) {
          file_close(*piVar1);
          *piVar1 = 0;
        }
        uVar7 = 0;
      }
      else {
        FUN_0043c0e4(*piVar3,*puVar2,0);
        iVar6 = file_read(*piVar3,1,iVar5,*piVar1);
        if (iVar6 == iVar5) {
          if (*piVar1 != 0) {
            file_close(*piVar1);
            *piVar1 = 0;
          }
          iVar5 = FUN_0052f86a(*piVar3,&local_28);
          if (iVar5 == 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xbe,DAT_0052ff7c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_0052ff80,DAT_0052ff80);
            }
            file_heap_free(*piVar3);
            *piVar3 = 0;
            uVar7 = 0;
          }
          else {
            *DAT_0052ff84 = local_28;
            *DAT_0052ff88 = local_24;
            *DAT_0052ff8c = local_1c;
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xca,DAT_0052ff90,local_28,
                           local_24,local_20,local_1c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x11000000,DAT_0052ff94,DAT_0052ff94,local_28,local_24,local_20,
                                  local_1c);
            }
            iVar5 = FUN_0052f87c(*piVar3 + 0x10,local_20);
            if (iVar5 == 0) {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xce,DAT_0052ff98);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_0052ff9c,DAT_0052ff9c);
              }
              file_heap_free(*piVar3);
              *piVar3 = 0;
              uVar7 = 0;
            }
            else {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xd7,DAT_0052ffa0,local_1c);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_0052ffa4,DAT_0052ffa4,local_1c);
              }
              if (local_1c != 0) {
                *DAT_0052ffa8 = local_20 * 0xc + 0x10 + *piVar3;
              }
              iVar5 = FUN_0052f99e(*piVar3,local_20);
              if (iVar5 == 0) {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xe1,DAT_0052ffac);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x4000000,DAT_0052ffb0,DAT_0052ffb0);
                }
                file_heap_free(*piVar3);
                *piVar3 = 0;
                uVar7 = 0;
              }
              else {
                uVar7 = 1;
              }
            }
          }
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0xb3,DAT_0052ff74,iVar6,iVar5);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_0052ff78,DAT_0052ff78,iVar6,iVar5);
          }
          file_heap_free(*piVar3);
          *piVar3 = 0;
          if (*piVar1 != 0) {
            file_close(*piVar1);
            *piVar1 = 0;
          }
          uVar7 = 0;
        }
      }
    }
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ff48,0x96,DAT_0052fcf4,uVar7,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0052fcf8,DAT_0052fcf8,uVar7,iVar5);
    }
    uVar7 = 0;
  }
  return uVar7;
}


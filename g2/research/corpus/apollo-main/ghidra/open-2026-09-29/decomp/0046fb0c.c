
int FUN_0046fb0c(undefined4 param_1,int param_2,int *param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_40 [4];
  undefined4 local_3c;
  undefined4 local_38;
  uint local_34;
  undefined1 auStack_30 [16];
  undefined4 uStack_20;
  
  puVar2 = DAT_00470014;
  local_3c = 0;
  local_38 = 0;
  local_34 = 0;
  iVar4 = 0;
  while ((iVar4 == 0 && (*(char *)(DAT_00470668 + 0xc) != '\0'))) {
    iVar4 = 1;
  }
  if (iVar4 == 1) {
    iVar3 = -1;
  }
  else {
    uStack_20 = param_4;
    iVar3 = FUN_004c0812(param_1,DAT_00470014);
    if (iVar3 == 0) {
      iVar3 = FUN_004c26e0(*puVar2,0,0);
      if (iVar3 == 0) {
        local_3c = 0x100;
        local_38 = DAT_004706d8;
        local_34 = local_34 & 0xffffff00;
        iVar3 = FUN_004c08a8(*puVar2,&local_3c);
        if (iVar3 == 0) {
          if (param_2 == 0) {
            iVar3 = FUN_004c099c(*puVar2,DAT_00470744);
          }
          else {
            iVar3 = FUN_004c099c(*puVar2,param_2);
          }
          if (iVar3 == 0) {
            iVar3 = FUN_004c0e1e(*puVar2);
            if (iVar3 == 0) {
              FUN_0046f6ba(0);
              FUN_004c32b4(param_1,0x10);
              FUN_00480eee(0x67,auStack_40);
              FUN_00439c04(auStack_30,DAT_00470758,0x10);
              iVar3 = FUN_004c0f78(*puVar2,0x12,auStack_30);
              if ((iVar3 == 0) && (iVar3 = FUN_004c0f78(*puVar2,0x15,0), iVar3 == 0)) {
                iVar3 = am_hal_mspi_interrupt_clear(*puVar2,0x1a80);
                if (iVar3 == 0) {
                  iVar3 = FUN_004c2328(*puVar2,0x1a80);
                  if (iVar3 == 0) {
                    FUN_0046f4c2(0x15,4);
                    FUN_0046f4a4(0x15);
                    FUN_00473934();
                    iVar3 = DAT_00470668;
                    *(undefined4 *)(DAT_00470668 + iVar4 * 0x10) = param_1;
                    if (param_2 == 0) {
                      bVar1 = *(byte *)(DAT_00470860 + 8);
                    }
                    else {
                      bVar1 = *(byte *)(param_2 + 8);
                    }
                    *(uint *)(iVar4 * 0x10 + iVar3 + 4) = (uint)bVar1;
                    *(undefined4 *)(iVar4 * 0x10 + iVar3 + 8) = *puVar2;
                    *(undefined1 *)(iVar4 * 0x10 + iVar3 + 0xc) = 1;
                    *param_3 = iVar3 + iVar4 * 0x10;
                    iVar4 = FUN_0043d0ce();
                    if (iVar4 << 0x1e < 0) {
                      FUN_0043d574(3,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x27a,DAT_00470864);
                    }
                    iVar4 = FUN_0043d0ce();
                    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                      compress_log_output(0xc000000,DAT_00470868,DAT_00470868);
                    }
                    iVar3 = 0;
                  }
                  else {
                    iVar4 = FUN_0043d0ce();
                    if (iVar4 << 0x1e < 0) {
                      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x269,DAT_00470858);
                    }
                    iVar4 = FUN_0043d0ce();
                    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                      compress_log_output(0x4000000,DAT_0047085c,DAT_0047085c);
                    }
                    iVar3 = 1;
                  }
                }
                else {
                  iVar3 = 1;
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x246,DAT_00470750);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_00470754,DAT_00470754);
              }
              FUN_004c0f24(*puVar2);
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x23f,DAT_00470748);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_0047074c,DAT_0047074c);
            }
            FUN_004c0f24(*puVar2);
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x233,DAT_004706dc);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00470740,DAT_00470740);
          }
          FUN_004c0f24(*puVar2);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004706d0,0x22a,DAT_0047066c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004706d4,DAT_004706d4);
        }
        iVar3 = 1;
      }
    }
  }
  return iVar3;
}


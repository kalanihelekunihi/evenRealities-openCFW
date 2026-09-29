
undefined4 load_touch_firmware_from_package(void)

{
  bool bVar1;
  int *piVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int local_34;
  int local_30;
  undefined4 local_2c;
  int local_28;
  int local_24;
  undefined4 local_20;
  uint local_1c;
  
  FUN_0043c0e4(&local_34,0x10,0);
  bVar1 = false;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x2e9,DAT_005610dc,DAT_005610ac);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005610ec,DAT_005610ec,DAT_005610ac);
  }
  piVar3 = DAT_005610f0;
  uVar4 = DAT_005610ac;
  iVar5 = file_open(DAT_005610ac,&DAT_00560a64);
  *piVar3 = iVar5;
  if (*piVar3 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x2ee,DAT_005610b8,uVar4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005610bc,DAT_005610bc,uVar4);
    }
    return 0xffffffff;
  }
  iVar6 = file_read(&local_24,1,0x10,*piVar3);
  iVar5 = DAT_005610c8;
  if (iVar6 != 0x10) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x2f5,DAT_005610c0,iVar6);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005610c4,DAT_005610c4,iVar6);
    }
    if (*piVar3 != 0) {
      file_close(*piVar3);
      *piVar3 = 0;
    }
    return 0xffffffff;
  }
  if (local_24 != DAT_005610c8) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x2fc,DAT_005610cc,local_24,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005610d0,DAT_005610d0,local_24,iVar5);
    }
    if (*piVar3 != 0) {
      file_close(*piVar3);
      *piVar3 = 0;
    }
    return 0xffffffff;
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x301,DAT_005610f4,local_20,local_1c);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_005610f8,DAT_005610f8,local_20,local_1c);
  }
  uVar7 = 0;
  do {
    if (local_1c <= uVar7) {
LAB_00560c18:
      piVar2 = DAT_0056108c;
      if (!bVar1) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x316,DAT_00561710);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00561714,DAT_00561714);
        }
        if (*piVar3 != 0) {
          file_close(*piVar3);
          *piVar3 = 0;
        }
        return 0xffffffff;
      }
      iVar5 = file_heap_allocate(local_30);
      *piVar2 = iVar5;
      if (*piVar2 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x31e,DAT_00561718,local_30);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0056171c,DAT_0056171c,local_30);
        }
        if (*piVar3 != 0) {
          file_close(*piVar3);
          *piVar3 = 0;
        }
        return 0xffffffff;
      }
      iVar5 = file_seek(*piVar3,local_2c,0);
      if (iVar5 != 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x326,DAT_00561720,iVar5);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00561724,DAT_00561724,iVar5);
        }
        free_touch_firmware_memory();
        if (*piVar3 != 0) {
          file_close(*piVar3);
          *piVar3 = 0;
        }
        return 0xffffffff;
      }
      iVar5 = file_read(*piVar2,1,local_30,*piVar3);
      if (iVar5 != local_30) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x32f,DAT_00561728,iVar5,local_30);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0056172c,DAT_0056172c,iVar5,local_30);
        }
        free_touch_firmware_memory();
        if (*piVar3 != 0) {
          file_close(*piVar3);
          *piVar3 = 0;
        }
        return 0xffffffff;
      }
      if (*piVar3 != 0) {
        file_close(*piVar3);
        *piVar3 = 0;
      }
      iVar5 = semantic_TouchCrc32(*piVar2,local_30);
      piVar3 = DAT_00561090;
      if (iVar5 != local_28) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x33b,DAT_00561730,iVar5,local_28);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00561734,DAT_00561734,iVar5,local_28);
        }
        free_touch_firmware_memory();
        return 0xffffffff;
      }
      *DAT_00561090 = local_30 + -4;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x342,DAT_00561738,local_30,*piVar3);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_0056173c,DAT_0056173c,local_30,*piVar3);
      }
      return 0;
    }
    iVar5 = file_read(&local_34,1,0x10,*piVar3);
    if (iVar5 != 0x10) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x307,DAT_00561104,uVar7,iVar5);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_00561108,DAT_00561108,uVar7,iVar5);
      }
      if (*piVar3 != 0) {
        file_close(*piVar3);
        *piVar3 = 0;
      }
      return 0xffffffff;
    }
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005610e8,DAT_005610e4,DAT_005610e0,0x30d,DAT_005610fc,uVar7,local_34,
                   local_30,local_2c,local_28);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x11400000,DAT_00561100,DAT_00561100,uVar7,local_34,local_30,local_2c,
                          local_28);
    }
    if (local_34 == 3) {
      bVar1 = true;
      goto LAB_00560c18;
    }
    uVar7 = uVar7 + 1;
  } while( true );
}



/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00511c24(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 auStack_30 [4];
  undefined4 uStack_2c;
  undefined4 uStack_28;
  float fStack_24;
  float fStack_20;
  float afStack_1c [4];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_00439c04(&fStack_24,PTR_DAT_005124f4,0x18);
  if (*PTR_DAT_005124f8 == '\x01') {
    iVar1 = FUN_00511990(&fStack_24,&fStack_20,afStack_1c,auStack_30);
    if (iVar1 == DAT_00512388) {
      iVar1 = func_0x0043c150(&fStack_24,0);
      if (iVar1 != 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2ac,
                       PTR_s_ERROR__nrf_fuel_gauge_init__d_0051259c,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__nrf_fuel_gau_005125a0,
                              PTR_s__npmx_driver_ERROR__nrf_fuel_gau_005125a0,iVar1);
        }
      }
      uStack_28 = *(undefined4 *)PTR_DAT_005125a4;
      iVar1 = FUN_0055f74c(5,&uStack_28);
      if (iVar1 == 0) {
        uStack_2c = *_DAT_00512614;
        iVar1 = FUN_0055f74c(6,&uStack_2c);
        if (iVar1 == 0) {
          iVar1 = FUN_00511b74(auStack_30[0]);
          if (iVar1 == 0) {
            FUN_00512892();
            *_DAT_00512620 = 1;
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2c9,
                           PTR_s_Fuel_gauge_initialized_00512624);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__npmx_driver_Fuel_gauge_initiali_00512628,
                                  PTR_s__npmx_driver_Fuel_gauge_initiali_00512628);
            }
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2ca,
                           PTR_s_v0__f_i0__f_t0__f_0051262c,(double)fStack_24,(double)fStack_20,
                           (double)afStack_1c[0]);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10c00000,PTR_s__npmx_driver__v0__f_i0__f_t0__f_00512630,
                                  PTR_s__npmx_driver__v0__f_i0__f_t0__f_00512630);
            }
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2cb,
                           PTR_s_Version___s_00512638,*_DAT_00512634);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10400000,PTR_s__npmx_driver__Version___s_0051263c,
                                  PTR_s__npmx_driver__Version___s_0051263c,*_DAT_00512634);
            }
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2cc,
                           PTR_s_Build_date___s_00512640,*_DAT_00512998);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10400000,_DAT_0051282c,_DAT_0051282c,*_DAT_00512998);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2c2,
                           DAT_00512618,iVar1);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_0051261c,DAT_0051261c,iVar1);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,700,
                         DAT_0051260c,iVar1);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00512610,DAT_00512610,iVar1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2b3,
                       DAT_0051260c,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00512610,DAT_00512610,iVar1);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2a6,
                     DAT_00512594,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_get_adc_00512598,
                            PTR_s__npmx_driver_ERROR__npmx_get_adc_00512598,iVar1);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00512408,DAT_00512404,PTR_s_initialize_fuel_gauge_0051258c,0x2a0,
                   PTR_s_ERROR__Wrong_fuel_gauge_variant_00512588);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_ERROR__Wrong_fuel_g_00512590,
                          PTR_s__npmx_driver_ERROR__Wrong_fuel_g_00512590);
    }
  }
  return;
}


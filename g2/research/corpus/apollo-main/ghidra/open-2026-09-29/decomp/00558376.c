
undefined4 FUN_00558376(int param_1)

{
  undefined1 *puVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  byte bVar5;
  char cStack_8c;
  byte bStack_8b;
  undefined1 auStack_8a [6];
  undefined1 auStack_84 [120];
  
  if (param_1 == 0) {
    FUN_00558148();
    uVar3 = 0;
  }
  else {
    FUN_00439be4(&cStack_8c,param_1,0x80);
    if (5 < bStack_8b) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0xe1,
                     PTR_s_widget_count__u_exceeds_max__u__c_005588c4,bStack_8b,5);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__dashboard_layout_widget_count___005588cc,
                            PTR_s__dashboard_layout_widget_count___005588cc,bStack_8b,5);
      }
      bStack_8b = 5;
    }
    if ((bStack_8b == 0) || (cStack_8c != '\x01')) {
      if ((cStack_8c == '\0') || ((cStack_8c == '\x01' || (cStack_8c == '\x02')))) {
        for (bVar5 = 0; bVar2 = bStack_8b, bVar5 < bStack_8b; bVar5 = bVar5 + 1) {
          iVar4 = FUN_00558030(auStack_8a[bVar5]);
          if (iVar4 == 0) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(2,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0xf9,
                           PTR_s_invalid_widget_order__u___d__fal_005588e0,bVar5,auStack_8a[bVar5]);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x8800000,PTR_s__dashboard_layout_invalid_widget_005588e4,
                                  PTR_s__dashboard_layout_invalid_widget_005588e4,bVar5,
                                  auStack_8a[bVar5]);
            }
            FUN_00558148();
            return 0xffffffff;
          }
        }
        for (; bVar2 < 5; bVar2 = bVar2 + 1) {
          auStack_8a[bVar2] = 0;
        }
        iVar4 = FUN_00558050(auStack_84);
        puVar1 = DAT_005588a8;
        if (iVar4 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(2,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0x107,
                         PTR_s_invalid_watchface_cfg__kind__d___005588e8,auStack_84[0]);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__dashboard_layout_invalid_watchf_005588ec,
                                PTR_s__dashboard_layout_invalid_watchf_005588ec,auStack_84[0]);
          }
          FUN_00558148();
          uVar3 = 0xffffffff;
        }
        else {
          FUN_00439be4(DAT_005588a8,&cStack_8c,0x80);
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0x110,
                         PTR_s_dashboard_layout_set__base_pos___005588f0,*puVar1,puVar1[1],puVar1[8]
                        );
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xcc00000,PTR_s__dashboard_layout_dashboard_layo_005588f4,
                                PTR_s__dashboard_layout_dashboard_layo_005588f4,*puVar1,puVar1[1],
                                puVar1[8]);
          }
          uVar3 = 0;
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0xf0,
                       PTR_s_invalid_base_pos__d__fallback_to_005588d8,cStack_8c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__dashboard_layout_invalid_base_p_005588dc,
                              PTR_s__dashboard_layout_invalid_base_p_005588dc,cStack_8c);
        }
        FUN_00558148();
        uVar3 = 0xffffffff;
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005588bc,DAT_005588b8,PTR_s_dashboard_layout_set_005588c8,0xe7,
                     PTR_s_invalid_layout__CENTER_not_allow_005588d0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__dashboard_layout_invalid_layout_005588d4,
                            PTR_s__dashboard_layout_invalid_layout_005588d4);
      }
      FUN_00558148();
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}


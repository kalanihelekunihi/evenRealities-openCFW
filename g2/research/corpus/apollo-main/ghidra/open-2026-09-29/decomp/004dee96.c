
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int * FUN_004dee96(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  short sStack_830;
  short sStack_82e;
  short sStack_82c;
  short sStack_82a;
  byte bStack_828;
  byte bStack_827;
  byte bStack_826;
  byte bStack_825;
  undefined4 uStack_824;
  undefined1 uStack_820;
  undefined1 auStack_81f [2051];
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                   PTR_s_common_text_create_004df968,0x6d,_DAT_004df850,param_1,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,_DAT_004df854,_DAT_004df854,param_1,param_2);
    }
    piVar2 = (int *)0x0;
  }
  else {
    FUN_00439c04(&sStack_830,param_2,0x814);
    if (0x240 < sStack_830) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x76,
                     PTR_s_common_text_create__x_position___004df96c,(int)sStack_830);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004df970,
                            PTR_s__common_text_container_common_te_004df970,(int)sStack_830);
      }
      sStack_830 = 0x240;
    }
    if (0x120 < sStack_82e) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x7c,
                     PTR_s_common_text_create__y_position___004df974,(int)sStack_82e);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004df978,
                            PTR_s__common_text_container_common_te_004df978,(int)sStack_82e);
      }
      sStack_82e = 0x120;
    }
    if (0x240 < sStack_82c) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x82,
                     PTR_s_common_text_create__width__d_>_5_004dfa10,(int)sStack_82c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfa14,
                            PTR_s__common_text_container_common_te_004dfa14,(int)sStack_82c);
      }
      sStack_82c = 0x240;
    }
    if (0x120 < sStack_82a) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x88,
                     PTR_s_common_text_create__height__d_>_2_004dfa18,(int)sStack_82a);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfa1c,
                            PTR_s__common_text_container_common_te_004dfa1c,(int)sStack_82a);
      }
      sStack_82a = 0x120;
    }
    if (5 < bStack_828) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x8e,
                     PTR_s_common_text_create__border_width_004dfa20,bStack_828);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfa24,
                            PTR_s__common_text_container_common_te_004dfa24,bStack_828);
      }
      bStack_828 = 5;
    }
    if (0x10 < bStack_827) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x94,
                     PTR_s_common_text_create__border_color_004dfa28,bStack_827);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfb5c,
                            PTR_s__common_text_container_common_te_004dfb5c,bStack_827);
      }
      bStack_827 = 0x10;
    }
    if (10 < bStack_826) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0x9a,
                     PTR_s_common_text_create__border_radiu_004dfb60,bStack_826);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfb64,
                            PTR_s__common_text_container_common_te_004dfb64,bStack_826);
      }
      bStack_826 = 10;
    }
    if (0x20 < bStack_825) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0xa0,
                     PTR_s_common_text_create__padding__d_>_004dfb68,bStack_825);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_text_container_common_te_004dfb6c,
                            PTR_s__common_text_container_common_te_004dfb6c,bStack_825);
      }
      bStack_825 = 0x20;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                   PTR_s_common_text_create_004df968,0xa6,
                   PTR_s_common_text_create__creating_tex_004dfb70,(int)sStack_830,(int)sStack_82e,
                   (int)sStack_82c,(int)sStack_82a);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11000000,PTR_s__common_text_container_common_te_004dfb74,
                          PTR_s__common_text_container_common_te_004dfb74,(int)sStack_830,
                          (int)sStack_82e,(int)sStack_82c,(int)sStack_82a);
    }
    piVar2 = (int *)file_heap_allocate(0x828);
    if (piVar2 == (int *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_create_004df968,0xae,
                     PTR_s_common_text_create__failed_to_al_004dfc98);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__common_text_container_common_te_004dfc9c,
                            PTR_s__common_text_container_common_te_004dfc9c);
      }
      piVar2 = (int *)0x0;
    }
    else {
      FUN_0043c0e4(piVar2,0x828,0);
      *(undefined1 *)((int)piVar2 + 0x13) = 0;
      piVar2[5] = 0;
      piVar2[7] = (int)sStack_82a + (uint)bStack_825 * -2;
      piVar2[0x208] = param_3;
      piVar2[0x209] = param_4;
      iVar1 = ui_common_api_fn_00509c1c();
      piVar2[6] = iVar1;
      if (piVar2[6] == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                       PTR_s_common_text_create_004df968,0xbf,
                       PTR_s_common_text_create__failed_to_cr_004dfca0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__common_text_container_common_te_004dfca4,
                              PTR_s__common_text_container_common_te_004dfca4);
        }
        file_heap_free(piVar2);
        piVar2 = (int *)0x0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                       PTR_s_common_text_create_004df968,0xc3,
                       PTR_s_common_text_create__FIFO_queue_c_004dfca8);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__common_text_container_common_te_004dfcac,
                              PTR_s__common_text_container_common_te_004dfcac);
        }
        iVar1 = FUN_0043de82(param_1);
        *piVar2 = iVar1;
        if (*piVar2 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                         PTR_s_common_text_create_004df968,200,
                         PTR_s_common_text_create__failed_to_cr_004dfcb0);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__common_text_container_common_te_004dfcb4,
                                PTR_s__common_text_container_common_te_004dfcb4);
          }
          ui_common_api_fn_00509c96(piVar2[6]);
          file_heap_free(piVar2);
          piVar2 = (int *)0x0;
        }
        else {
          FUN_0043f506(*piVar2,(int)sStack_82c);
          FUN_0043f568(*piVar2,(int)sStack_82a);
          FUN_0043f0e0(*piVar2,(int)sStack_830);
          FUN_0043f142(*piVar2,(int)sStack_82e);
          FUN_0044e368(*piVar2,3);
          FUN_0044e3ca(*piVar2,0xc);
          FUN_0044129e(*piVar2,0,0);
          FUN_0044146a(*piVar2,bStack_826,0);
          if (bStack_828 == 0) {
            FUN_0044131c(*piVar2,0,0);
          }
          else {
            FUN_0044131c(*piVar2,bStack_828,0);
            uVar3 = FUN_004df7f2(bStack_827);
            uVar4 = FUN_0044104c(uVar3);
            FUN_004412ec(*piVar2,uVar4,0);
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                           PTR_s_common_text_create_004df968,0xdd,
                           PTR_s_common_text_create__border_enabl_004dfe3c,bStack_828,uVar3);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10800000,PTR_s__common_text_container_common_te_004dfe40,
                                  PTR_s__common_text_container_common_te_004dfe40,bStack_828,uVar3);
            }
          }
          FUN_0044120e(*piVar2,bStack_825,0);
          FUN_0044121c(*piVar2,bStack_825,0);
          FUN_0044122a(*piVar2,bStack_825,0);
          FUN_00441238(*piVar2,bStack_825,0);
          uVar3 = FUN_0044104c(0xffffff);
          FUN_0044127e(*piVar2,uVar3,0x10000);
          FUN_0044129e(*piVar2,0xb4,0x10000);
          FUN_00441164(*piVar2,4,0x10000);
          iVar1 = FUN_0043de82(*piVar2);
          piVar2[1] = iVar1;
          if (piVar2[1] == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                           PTR_s_common_text_create_004df968,0xf0,
                           PTR_s_common_text_create__failed_to_cr_004dfe44);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__common_text_container_common_te_004dfe48,
                                  PTR_s__common_text_container_common_te_004dfe48);
            }
            FUN_0044d7b8(*piVar2);
            ui_common_api_fn_00509c96(piVar2[6]);
            file_heap_free(piVar2);
            piVar2 = (int *)0x0;
          }
          else {
            FUN_0043f506(piVar2[1],(int)sStack_82c + (uint)bStack_825 * -2);
            FUN_0043f568(piVar2[1],0x3fffffff);
            FUN_0043f0e0(piVar2[1],0);
            FUN_0043f142(piVar2[1],0);
            FUN_0044129e(piVar2[1],0,0);
            FUN_0044131c(piVar2[1],0,0);
            FUN_004dee64(piVar2[1],0,0);
            FUN_0043dfa4(piVar2[1],0x10);
            iVar1 = FUN_00499416(piVar2[1]);
            piVar2[2] = iVar1;
            if (piVar2[2] == 0) {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                             PTR_s_common_text_create_004df968,0x103,
                             PTR_s_common_text_create__failed_to_cr_004dfe4c);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x4000000,_DAT_004dffc8,_DAT_004dffc8);
              }
              FUN_0044d7b8(*piVar2);
              ui_common_api_fn_00509c96(piVar2[6]);
              file_heap_free(piVar2);
              piVar2 = (int *)0x0;
            }
            else {
              FUN_0049942e(piVar2[2],auStack_81f);
              FUN_0043f506(piVar2[2],(int)sStack_82c + (uint)bStack_825 * -2);
              FUN_00499678(piVar2[2],0);
              FUN_0044143e(piVar2[2],*_DAT_004dffcc,0);
              uVar3 = FUN_0044104c(uStack_824);
              FUN_0044140e(piVar2[2],uVar3,0);
              FUN_0044145a(piVar2[2],uStack_820,0);
              FUN_0044b5a0(piVar2 + 8,auStack_81f,0x7ff);
              *(undefined1 *)((int)piVar2 + 0x81f) = 0;
              FUN_0043f66c(param_1);
              FUN_004df858(piVar2);
              FUN_0044ea04(*piVar2,0,0);
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                             PTR_s_common_text_create_004df968,0x11f,_DAT_004dffd0,(int)sStack_830,
                             (int)sStack_82e);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0xc800000,_DAT_004dffd4,_DAT_004dffd4,(int)sStack_830,
                                    (int)sStack_82e);
              }
            }
          }
        }
      }
    }
  }
  return piVar2;
}


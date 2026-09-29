
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int * FUN_004dbede(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  short sStack_30;
  short sStack_2e;
  ushort uStack_2c;
  ushort uStack_2a;
  byte bStack_28;
  uint uStack_24;
  byte bStack_20;
  uint uStack_1c;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x34,
                   _DAT_004dca18,param_1,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__common_image_container_Invalid_p_004dca28,
                          PTR_s__common_image_container_Invalid_p_004dca28,param_1,param_2);
    }
    piVar2 = (int *)0x0;
  }
  else {
    FUN_00439c04(&sStack_30,param_2,0x1c);
    if (0x240 < sStack_30) {
      sStack_30 = 0x240;
    }
    if (0x120 < sStack_2e) {
      sStack_2e = 0x120;
    }
    if (uStack_2c < 0x14) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x41,
                     PTR_s_common_image_create__width__d_<_2_004dca2c,uStack_2c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__common_image_container_common_i_004dca30,
                            PTR_s__common_image_container_common_i_004dca30,uStack_2c);
      }
      piVar2 = (int *)0x0;
    }
    else if (uStack_2c < 0x121) {
      if (uStack_2a < 0x14) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x4a,
                       PTR_s_common_image_create__height__d_<_004dcba8,uStack_2a);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__common_image_container_common_i_004dcbac,
                              PTR_s__common_image_container_common_i_004dcbac,uStack_2a);
        }
        piVar2 = (int *)0x0;
      }
      else if (uStack_2a < 0x91) {
        if (5 < bStack_28) {
          bStack_28 = 5;
        }
        if (0xff < uStack_24) {
          uStack_24 = 0xff;
        }
        if (0x20 < bStack_20) {
          bStack_20 = 0x20;
        }
        if (0xff < uStack_1c) {
          uStack_1c = 0xff;
        }
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x62,
                       PTR_s_Creating_image_container__pos__d_004dcbb8,(int)sStack_30,(int)sStack_2e
                       ,uStack_2c,uStack_2a,bStack_28,uStack_24,bStack_20,uStack_1c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x12000000,PTR_s__common_image_container_Creating_004dcbbc,
                              PTR_s__common_image_container_Creating_004dcbbc,(int)sStack_30,
                              (int)sStack_2e,uStack_2c,uStack_2a,bStack_28,uStack_24,bStack_20,
                              uStack_1c);
        }
        piVar2 = (int *)file_heap_allocate(0x48);
        if (piVar2 == (int *)0x0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x67,
                         PTR_s_Failed_to_allocate_handle_memory_004dcbc0);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__common_image_container_Failed_t_004dcbc4,
                                PTR_s__common_image_container_Failed_t_004dcbc4);
          }
          piVar2 = (int *)0x0;
        }
        else {
          FUN_0043c0e4(piVar2,0x48,0);
          *(ushort *)(piVar2 + 0x10) = uStack_2c;
          *(ushort *)((int)piVar2 + 0x42) = uStack_2a;
          piVar2[0x11] = (uint)uStack_2a * (uint)uStack_2c;
          iVar1 = file_heap_allocate(piVar2[0x11]);
          piVar2[2] = iVar1;
          if (piVar2[2] == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x74,
                           PTR_s_Failed_to_allocate_image_buffer___004dcbc8,piVar2[0x11]);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4400000,PTR_s__common_image_container_Failed_t_004dcbcc,
                                  PTR_s__common_image_container_Failed_t_004dcbcc,piVar2[0x11]);
            }
            file_heap_free(piVar2);
            piVar2 = (int *)0x0;
          }
          else {
            FUN_0043c0e4(piVar2[2],piVar2[0x11],0);
            iVar1 = file_heap_allocate(piVar2[0x11]);
            piVar2[3] = iVar1;
            if (piVar2[3] == 0) {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x7d
                             ,PTR_s_Failed_to_allocate_rev_buffer____004dcbd0,piVar2[0x11]);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x4400000,PTR_s__common_image_container_Failed_t_004dcbd4,
                                    PTR_s__common_image_container_Failed_t_004dcbd4,piVar2[0x11]);
              }
              file_heap_free(piVar2[2]);
              file_heap_free(piVar2);
              piVar2 = (int *)0x0;
            }
            else {
              FUN_0043c0e4(piVar2[3],piVar2[0x11],0);
              if ((*(byte *)(piVar2 + 2) & 3) != 0) {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  FUN_0043d574(2,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,
                               0x86,PTR_s_Image_buffer_not_4_byte_aligned__004dcbd8,piVar2[2]);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x8400000,PTR_s__common_image_container_Image_bu_004dcbdc,
                                      PTR_s__common_image_container_Image_bu_004dcbdc,piVar2[2]);
                }
              }
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x8a
                             ,PTR_s_Image_buffer_allocated___p__size_004dcbe0,piVar2[2],piVar2[0x11]
                            );
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10800000,PTR_s__common_image_container_Image_bu_004dcbe4,
                                    PTR_s__common_image_container_Image_bu_004dcbe4,piVar2[2],
                                    piVar2[0x11]);
              }
              iVar1 = FUN_0043de82(param_1);
              *piVar2 = iVar1;
              if (*piVar2 == 0) {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,
                               0x8f,PTR_s_Failed_to_create_container_objec_004dcbe8);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x4000000,PTR_s__common_image_container_Failed_t_004dcbec,
                                      PTR_s__common_image_container_Failed_t_004dcbec);
                }
                file_heap_free(piVar2[3]);
                file_heap_free(piVar2[2]);
                file_heap_free(piVar2);
                piVar2 = (int *)0x0;
              }
              else {
                FUN_0043f09a(*piVar2,(int)sStack_30,(int)sStack_2e);
                FUN_0043f4c0(*piVar2,uStack_2c,uStack_2a);
                uVar3 = func_0x004dcc80(uStack_1c);
                FUN_0044127e(*piVar2,uVar3,0);
                FUN_0044129e(*piVar2,0,0);
                FUN_0044131c(*piVar2,bStack_28,0);
                if (bStack_28 != 0) {
                  uVar3 = func_0x004dcc80(uStack_24);
                  FUN_004412ec(*piVar2,uVar3,0);
                }
                FUN_0044146a(*piVar2,bStack_20,0);
                FUN_004dbeac(*piVar2,0,0);
                piVar2[9] = piVar2[9] & 0xffffff00U | 0x19;
                piVar2[9] = piVar2[9] & 0xffff00ffU | 0x600;
                piVar2[9] = piVar2[9] & 0xffff;
                piVar2[0xb] = piVar2[0xb] & 0xffff0000U | (uint)uStack_2c;
                piVar2[10] = piVar2[10] & 0xffff0000U | (uint)uStack_2c;
                piVar2[10] = piVar2[10] & 0xffffU | (uint)uStack_2a << 0x10;
                piVar2[0xc] = piVar2[0x11];
                piVar2[0xd] = piVar2[2];
                piVar2[0xe] = 0;
                piVar2[0xf] = 0;
                iVar1 = FUN_00498668(*piVar2);
                piVar2[1] = iVar1;
                if (piVar2[1] == 0) {
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,
                                 0xbf,PTR_s_Failed_to_create_image_object_004dcbf0);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0x4000000,PTR_s__common_image_container_Failed_t_004dcbf4,
                                        PTR_s__common_image_container_Failed_t_004dcbf4);
                  }
                  FUN_0044d7b8(*piVar2);
                  file_heap_free(piVar2[3]);
                  file_heap_free(piVar2[2]);
                  file_heap_free(piVar2);
                  piVar2 = (int *)0x0;
                }
                else {
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,
                                 0xcd,PTR_s_Image_container_created_successf_004dcbf8,piVar2);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0x10400000,PTR_s__common_image_container_Image_co_004dcbfc,
                                        PTR_s__common_image_container_Image_co_004dcbfc,piVar2);
                  }
                }
              }
            }
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x4e,
                       PTR_s_common_image_create__height__d_>_004dcbb0,uStack_2a,0x90,0x90);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8c00000,PTR_s__common_image_container_common_i_004dcbb4,
                              PTR_s__common_image_container_common_i_004dcbb4,uStack_2a,0x90,0x90);
        }
        piVar2 = (int *)0x0;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_image_container_004dca24,DAT_004dca20,_DAT_004dca1c,0x46,
                     PTR_s_common_image_create__width__d_>___004dca34,uStack_2c,0x120,0x120);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8c00000,PTR_s__common_image_container_common_i_004dca38,
                            PTR_s__common_image_container_common_i_004dca38,uStack_2c,0x120,0x120);
      }
      piVar2 = (int *)0x0;
    }
  }
  return piVar2;
}


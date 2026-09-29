
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 pt_production_mode_orchestrate(int param_1,undefined4 param_2,int param_3,uint param_4)

{
  char cVar1;
  uint *puVar2;
  byte *pbVar3;
  byte bVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint auStack_1c [4];
  
  pbVar3 = _DAT_00570750;
  auStack_1c[3] = param_4;
  if (((param_1 == 0) || (param_3 == 0)) || ((param_4 & 0xff) < 4)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,_DAT_00570434,0x35d,DAT_0056fdac,_DAT_00570434);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0056fdb0,DAT_0056fdb0,_DAT_00570434);
    }
    uVar6 = 0xffffffff;
  }
  else {
    cVar1 = *(char *)(param_3 + 4);
    if (cVar1 == '\x01') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        auStack_1c[0] = (uint)*(byte *)(param_3 + 8);
        FUN_0043d574(3,DAT_0056fbe8,DAT_0056fbe4,_DAT_00570434,0x366,_DAT_0057053c,
                     *(undefined1 *)(param_3 + 7));
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc800000,_DAT_00570540,_DAT_00570540,*(undefined1 *)(param_3 + 7),
                            *(undefined1 *)(param_3 + 8));
      }
      if (*(char *)(param_3 + 8) == '\0') {
        osDelay(1000);
        FUN_0044b0ae();
      }
    }
    else if (cVar1 == '\x06') {
      auStack_1c[0] = *(uint *)PTR_PTR_00570548;
      auStack_1c[1] = *(undefined4 *)(PTR_PTR_00570548 + 4);
      auStack_1c[2] = *(undefined4 *)(PTR_PTR_00570548 + 8);
      for (uVar7 = 0; uVar7 < 3; uVar7 = uVar7 + 1) {
        iVar5 = file_open(auStack_1c[uVar7],0x56fd94);
        if (iVar5 == 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,DAT_0056fbe8,DAT_0056fbe4,_DAT_00570434,0x3a5,
                         PTR_s_File_does_not_exist__skip_deleti_0057054c,auStack_1c[uVar7]);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__pt_protocol_procsr_File_does_no_00570550,
                                PTR_s__pt_protocol_procsr_File_does_no_00570550,auStack_1c[uVar7]);
          }
        }
        else {
          file_close();
          iVar5 = file_remove(auStack_1c[uVar7]);
          if (iVar5 == 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0056fbe8,DAT_0056fbe4,_DAT_00570434,0x39c,
                           PTR_s_Successfully_deleted_file___s_0057055c,auStack_1c[uVar7]);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__pt_protocol_procsr_Successfully_00570560,
                                  PTR_s__pt_protocol_procsr_Successfully_00570560,auStack_1c[uVar7])
              ;
            }
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,_DAT_00570434,0x3a0,
                           PTR_s_Failed_to_delete_file___s_00570554,auStack_1c[uVar7]);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,PTR_s__pt_protocol_procsr_Failed_to_de_00570558,
                                  PTR_s__pt_protocol_procsr_Failed_to_de_00570558,auStack_1c[uVar7])
              ;
            }
          }
        }
      }
    }
    else if (cVar1 == '\v') {
      osDelay(1000);
      FUN_0044b0ae();
    }
    else if (cVar1 == '\x13') {
      FUN_004ac798();
    }
    else if (cVar1 == '>') {
      if (*(char *)(param_1 + 4) == '\0') {
        *_DAT_00570544 = 0;
        osDelay(2000);
        FUN_0044b0ae();
      }
    }
    else if (cVar1 == 'T') {
      if (*_DAT_00570564 != '\0') {
        *_DAT_00570564 = '\0';
        puVar2 = _DAT_00570568;
        semantic_OtaFrameDispatch(0xc1,_DAT_0057056c,*_DAT_00570568 & 0xffff);
        *puVar2 = 0;
      }
    }
    else if (cVar1 == 'f') {
      func_0x00542d4c();
    }
    else if (cVar1 == 'l') {
      *_DAT_00570750 = 0;
      bVar4 = FUN_0058f486();
      *pbVar3 = bVar4 | *pbVar3;
      bVar4 = FUN_0058f490();
      *pbVar3 = bVar4 | *pbVar3;
    }
    uVar6 = 0;
  }
  return uVar6;
}


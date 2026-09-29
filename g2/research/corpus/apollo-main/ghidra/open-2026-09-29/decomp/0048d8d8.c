
undefined4 FUN_0048d8d8(char *param_1,short param_2)

{
  short sVar1;
  uint *puVar2;
  char *pcVar3;
  char *pcVar4;
  int *piVar5;
  undefined *puVar6;
  short sVar7;
  int iVar8;
  
  if (*param_1 != -0x56) {
    return 10;
  }
  if ((param_1[3] == '\0') && (param_2 == 8)) {
    return 0;
  }
  *DAT_0048e0c8 = param_1[2];
  puVar6 = PTR_LAB_0048d87c_1_0048e104;
  pcVar3 = DAT_0048e0c4;
  if (((*DAT_0048e0c4 != '\0') && (1 < (byte)param_1[5])) && (param_1[2] == *DAT_0048e0cc)) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,99,
                   PTR_s_error_send_ignore__packetNum_____0048e0d0,param_1[5],param_1[2]);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__ota_tran_error_send_ignore__pac_0048e0d8,
                          PTR_s__ota_tran_error_send_ignore__pac_0048e0d8,param_1[5],param_1[2]);
    }
    return 0;
  }
  if (param_1[6] == -0x40) {
    *DAT_0048e0dc = 1;
    puVar2 = DAT_0048e0c0;
    *DAT_0048e0c0 = (byte)param_1[3] - 2;
    sVar1 = *(short *)(param_1 + *puVar2 + 8);
    sVar7 = FUN_0049acd4(param_1 + 8,*puVar2,0);
    if (sVar7 == sVar1) {
      if ((((byte)param_1[7] & 0x3f) >> 5 == 0) && (*DAT_0048e0e0 != 0)) {
        (*(code *)*DAT_0048e0e0)(param_1[6],param_1 + 8,*puVar2 & 0xffff);
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0x75,DAT_0048e0e4)
        ;
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0048e0e8,DAT_0048e0e8);
      }
      *pcVar3 = '\x01';
      *DAT_0048e0cc = param_1[2];
      semantic_OtaNotifyStatus3(param_1[6]);
    }
    if ((param_1[6] == -0x40) && (param_1[8] == '\x02')) {
      *puVar2 = 0;
      piVar5 = DAT_0048e0ec;
      *DAT_0048e0ec = 0;
      *pcVar3 = '\0';
      pcVar4 = DAT_0048e0cc;
      *DAT_0048e0cc = '\0';
      *piVar5 = *DAT_0048e0f0;
      if (*piVar5 == 0) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0x87,
                       PTR_s_Malloc_failed__0048e0f4);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__ota_tran_Malloc_failed__0048e0f8,
                              PTR_s__ota_tran_Malloc_failed__0048e0f8);
        }
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0x88,
                       PTR_s_OTA_ReplyNoResourcesToAPP_0048e0fc);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__ota_tran_OTA_ReplyNoResourcesTo_0048e100,
                              PTR_s__ota_tran_OTA_ReplyNoResourcesTo_0048e100);
        }
        *pcVar3 = '\x01';
        *pcVar4 = param_1[2];
        semantic_OtaNotifyStatus5(param_1[6]);
        return 4;
      }
      FUN_0043c0e4(*piVar5,0x1020,0);
    }
  }
  else if (param_1[6] == -0x3f) {
    fw_event_loop_remove_delayed(PTR_LAB_0048d87c_1_0048e104);
    *pcVar3 = '\0';
    piVar5 = DAT_0048e0ec;
    puVar2 = DAT_0048e0c0;
    if ((*DAT_0048e0ec == 0) && ((byte)param_1[5] < (byte)param_1[4])) {
      return 4;
    }
    if (0x1020 < *DAT_0048e0c0 + (uint)(byte)param_1[3]) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0xa2,
                     PTR_s_Buffer_overflow___g_totalLenRx___0048e108,*puVar2,param_1[3],param_1[5],
                     param_1[4]);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x5000000,PTR_s__ota_tran_Buffer_overflow___g_to_0048e10c,
                            PTR_s__ota_tran_Buffer_overflow___g_to_0048e10c,*puVar2,param_1[3],
                            param_1[5],param_1[4]);
      }
      *puVar2 = 0;
      *pcVar3 = '\x01';
      *DAT_0048e0cc = param_1[2];
      semantic_OtaNotifyStatus3(param_1[6]);
      return 4;
    }
    FUN_00439be4(*DAT_0048e0ec + *DAT_0048e0c0,param_1 + 8,param_1[3]);
    *puVar2 = *puVar2 + (uint)(byte)param_1[3];
    if ((byte)param_1[5] < (byte)param_1[4]) {
      fw_event_loop_push_delayed(puVar6,0,0x5dc);
      return 0;
    }
    *puVar2 = *puVar2 - 2;
    sVar1 = *(short *)(*piVar5 + *puVar2);
    sVar7 = FUN_0049acd4(*piVar5,*puVar2,0);
    if (sVar7 != sVar1) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0xc1,
                     PTR_s_rx_totalLength____d_0048e118,*puVar2);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__ota_tran_rx_totalLength____d_0048e11c,
                            PTR_s__ota_tran_rx_totalLength____d_0048e11c,*puVar2);
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0xc2,
                     PTR_s_rx_crc___0x_x_0x_x__0048e120,sVar1,sVar7);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__ota_tran_rx_crc___0x_x_0x_x__0048e124,
                            PTR_s__ota_tran_rx_crc___0x_x_0x_x__0048e124,sVar1,sVar7);
      }
      if (*piVar5 != *DAT_0048e0f0) {
        file_heap_free(*piVar5);
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,199,
                     PTR_s_OTA_ReplyCrcErrorToAPP_0048e128);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__ota_tran_OTA_ReplyCrcErrorToAPP_0048e12c,
                            PTR_s__ota_tran_OTA_ReplyCrcErrorToAPP_0048e12c);
      }
      *puVar2 = 0;
      *pcVar3 = '\x01';
      *DAT_0048e0cc = param_1[2];
      semantic_OtaNotifyStatus3(param_1[6]);
      return 1;
    }
    if (*DAT_0048e0e0 != 0) {
      (*(code *)*DAT_0048e0e0)(param_1[6],*piVar5,*puVar2 & 0xffff);
    }
    if (*piVar5 != *DAT_0048e0f0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0xd0,
                     PTR_s_free_pDataBuf___0x_x_0048e110,*piVar5);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__ota_tran_free_pDataBuf___0x_x_0048e114,
                            PTR_s__ota_tran_free_pDataBuf___0x_x_0048e114,*piVar5);
      }
      file_heap_free(*piVar5);
    }
    *piVar5 = 0;
    *puVar2 = 0;
  }
  else if (param_1[6] == -0x3e) {
    *DAT_0048e0dc = 1;
    puVar2 = DAT_0048e0c0;
    *DAT_0048e0c0 = (byte)param_1[3] - 2;
    sVar1 = *(short *)(param_1 + *puVar2 + 8);
    sVar7 = FUN_0049acd4(param_1 + 8,*puVar2,0);
    if (sVar7 == sVar1) {
      if ((((byte)param_1[7] & 0x3f) >> 5 == 0) && (*DAT_0048e0e0 != 0)) {
        (*(code *)*DAT_0048e0e0)(param_1[6],param_1 + 8,*puVar2 & 0xffff);
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0048e0b8,DAT_0048e0b4,PTR_s_OTA_ReceivePacket_0048e0d4,0xe3,DAT_0048e0e4)
        ;
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0048e0e8,DAT_0048e0e8);
      }
      *pcVar3 = '\x01';
      *DAT_0048e0cc = param_1[2];
      semantic_OtaNotifyStatus3(param_1[6]);
    }
  }
  return 0;
}



undefined8 smpSendPkt(int param_1,int param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (*(char *)(param_1 + 0x3c) == '\0') {
    L2cDataReq(6,*(undefined2 *)(param_1 + 0x38),
               *(undefined1 *)(DAT_00537d08 + (uint)*(byte *)(param_2 + 8)),param_2,param_2,param_3,
               param_4);
  }
  else {
    iVar2 = param_2;
    if (*(int *)(param_1 + 0x34) != 0) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,&DAT_00537cfc,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,PTR_DAT_00537ea0,4), iVar1 != 0))
        {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,DAT_00537eb0,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00537d00,&DAT_00537d04,3), iVar1 != 0))
              {
                WsfTrace(PTR_DAT_00537ea0,PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc,
                         *(undefined1 *)(*(int *)(param_1 + 0x34) + 8));
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                iVar2 = 0x255;
                param_3 = PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc;
                FUN_0043d574(4,&DAT_00537d00,DAT_00537eac,PTR_s_smpSendPkt_00537ed0,0x255,
                             PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc,
                             *(undefined1 *)(*(int *)(param_1 + 0x34) + 8));
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              iVar2 = 0x255;
              param_3 = PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc;
              FUN_0043d574(3,&DAT_00537d00,DAT_00537eac,PTR_s_smpSendPkt_00537ed0,0x255,
                           PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc,
                           *(undefined1 *)(*(int *)(param_1 + 0x34) + 8));
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0x255;
            param_3 = PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc;
            FUN_0043d574(2,&DAT_00537d00,DAT_00537eac,PTR_s_smpSendPkt_00537ed0,0x255,
                         PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc,
                         *(undefined1 *)(*(int *)(param_1 + 0x34) + 8));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0x255;
          param_3 = PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc;
          FUN_0043d574(1,&DAT_00537d00,DAT_00537eac,PTR_s_smpSendPkt_00537ed0,0x255,
                       PTR_s_smpSendPkt_packet_discarded_cmd__00537ecc,
                       *(undefined1 *)(*(int *)(param_1 + 0x34) + 8));
        }
      }
      WsfMsgFree(*(undefined4 *)(param_1 + 0x34));
    }
    *(int *)(param_1 + 0x34) = param_2;
    param_2 = iVar2;
  }
  return CONCAT44(param_3,param_2);
}


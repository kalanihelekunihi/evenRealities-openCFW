
undefined8 dmConn2MsgHandler(undefined2 *param_1,uint param_2,uint param_3)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = dmConnCcbById((char)*param_1);
  if (iVar2 != 0) {
    bVar1 = *(byte *)(param_1 + 1);
    if (bVar1 == 0x21) {
      HciReadRssiCmd(*(undefined2 *)(iVar2 + 0xc));
    }
    else if (0x20 < bVar1) {
      if (bVar1 == 0x23) {
        HciLeRemoteConnParamReqNegReply(*(undefined2 *)(iVar2 + 0xc),*(undefined1 *)(param_1 + 2));
      }
      else if (bVar1 < 0x23) {
        param_3 = (uint)(ushort)param_1[6];
        param_2 = (uint)(ushort)param_1[5];
        HciLeRemoteConnParamReqReply
                  (*(undefined2 *)(iVar2 + 0xc),param_1[2],param_1[3],param_1[4],param_2,param_3,
                   param_1[7]);
      }
      else if (bVar1 == 0x25) {
        HciWriteAuthPayloadTimeout(*(undefined2 *)(iVar2 + 0xc),param_1[2]);
      }
      else if (bVar1 < 0x25) {
        HciLeSetDataLen(*(undefined2 *)(iVar2 + 0xc),param_1[2],param_1[3]);
      }
      else if (bVar1 == 0x26) {
        HciLeRequestPeerScaCmd(*(undefined2 *)(iVar2 + 0xc));
      }
    }
  }
  return CONCAT44(param_3,param_2);
}


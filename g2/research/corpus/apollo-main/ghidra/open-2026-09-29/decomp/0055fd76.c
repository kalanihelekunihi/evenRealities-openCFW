
undefined8
semantic_TouchValidateReply(uint param_1,char *param_2,undefined1 *param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  
  *param_3 = 0;
  if ((param_1 < 7) || (*param_2 != '\x01')) {
    *param_3 = 0;
    bVar1 = 0xaa;
  }
  else {
    iVar2 = semantic_TouchFramePayloadLength(param_2);
    if ((param_1 < iVar2 + 7U) || (0xf < iVar2 + 7U)) {
      *param_3 = 0;
      bVar1 = 3;
    }
    else {
      iVar3 = semantic_TouchFrameHasTerminator(param_2,iVar2);
      if (iVar3 == 0) {
        *param_3 = 0;
        bVar1 = 4;
      }
      else {
        iVar3 = semantic_TouchFrameChecksum(param_2,iVar2);
        iVar2 = semantic_TouchFrameChecksum16(param_2,iVar2);
        if (iVar3 == iVar2) {
          bVar1 = semantic_TouchFrameCommand(param_2);
          *param_3 = 1;
        }
        else {
          *param_3 = 0;
          bVar1 = 8;
        }
      }
    }
  }
  return CONCAT44(param_4,(uint)bVar1);
}


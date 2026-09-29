
undefined8 attcDataCback(uint param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined *puVar3;
  
  puVar3 = param_2;
  iVar2 = attcCcbByHandle(param_1 & 0xffff,0);
  if ((iVar2 != 0) && (((uint)param_2 & 0xffff) != 0)) {
    bVar1 = *(byte *)(param_3 + 8);
    if (bVar1 < 0x1a) {
      attcProcRsp(iVar2,(uint)param_2 & 0xffff,param_3);
    }
    else if ((bVar1 == 0x1b) || (bVar1 == 0x1d)) {
      attcProcInd(iVar2,(uint)param_2 & 0xffff,param_3);
    }
    else if (bVar1 == 0x23) {
      attcProcMultiVarNtf(iVar2,(uint)param_2 & 0xffff,param_3);
    }
    else {
      iVar2 = FUN_004c9c50(iVar2);
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00531b90,&DAT_00531328,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00531b90,DAT_00531b90,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00531b90,DAT_00531b18,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0053132c,&DAT_005315a8,3), iVar2 != 0))
              {
                WsfTrace(DAT_00531b90,PTR_s_attc_unknown_opcode_0x_02x_00531ba4,bVar1);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                param_1 = 0x20c;
                puVar3 = PTR_s_attc_unknown_opcode_0x_02x_00531ba4;
                FUN_0043d574(4,&DAT_0053132c,DAT_00531abc,PTR_s_attcDataCback_00531ba8,0x20c,
                             PTR_s_attc_unknown_opcode_0x_02x_00531ba4,bVar1);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              param_1 = 0x20c;
              puVar3 = PTR_s_attc_unknown_opcode_0x_02x_00531ba4;
              FUN_0043d574(3,&DAT_0053132c,DAT_00531abc,PTR_s_attcDataCback_00531ba8,0x20c,
                           PTR_s_attc_unknown_opcode_0x_02x_00531ba4,bVar1);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_1 = 0x20c;
            puVar3 = PTR_s_attc_unknown_opcode_0x_02x_00531ba4;
            FUN_0043d574(2,&DAT_0053132c,DAT_00531abc,PTR_s_attcDataCback_00531ba8,0x20c,
                         PTR_s_attc_unknown_opcode_0x_02x_00531ba4,bVar1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x20c;
          puVar3 = PTR_s_attc_unknown_opcode_0x_02x_00531ba4;
          FUN_0043d574(1,&DAT_0053132c,DAT_00531abc,PTR_s_attcDataCback_00531ba8,0x20c,
                       PTR_s_attc_unknown_opcode_0x_02x_00531ba4,bVar1,param_4);
        }
      }
    }
  }
  return CONCAT44(puVar3,param_1);
}


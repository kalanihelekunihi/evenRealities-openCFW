
void smpL2cDataCback(undefined2 param_1,ushort param_2,int param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 local_30;
  undefined *local_2c;
  uint local_28;
  uint local_24;
  uint local_20;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar2 = smpCcbByHandle(param_1);
  if (iVar2 != 0) {
    bVar1 = *(byte *)(param_3 + 8);
    if ((((bVar1 == 0) || (0xe < bVar1)) || (param_2 != *(byte *)(DAT_00537d08 + (uint)bVar1))) ||
       ((bVar1 != *(byte *)(iVar2 + 0x3f) && (bVar1 != 5)))) {
      iVar3 = FUN_004c9c50();
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537ea0,&DAT_005375f0,3), iVar3 != 0)) {
        iVar3 = FUN_004c9c50();
        if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537ea0,PTR_DAT_00537ea0,4), iVar3 != 0))
        {
          iVar3 = FUN_004c9c50();
          if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537ea0,DAT_00537eb0,4), iVar3 != 0)) {
            iVar3 = FUN_004c9c50();
            if (iVar3 == 0) {
              iVar3 = FUN_004c9c50();
              if ((iVar3 == 0) || (iVar3 = FUN_0044b610(&DAT_005375f4,&DAT_005375f8,3), iVar3 != 0))
              {
                local_30 = (uint)*(byte *)(iVar2 + 0x3f);
                WsfTrace(PTR_DAT_00537ea0,PTR_s_unexpected_packet_cmd__d_len__d__00537ea4,bVar1,
                         param_2);
              }
            }
            else {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_20 = (uint)*(byte *)(iVar2 + 0x3f);
                local_24 = (uint)param_2;
                local_28 = (uint)bVar1;
                local_2c = PTR_s_unexpected_packet_cmd__d_len__d__00537ea4;
                local_30 = 0x77;
                FUN_0043d574(4,&DAT_005375f4,DAT_00537eac,PTR_s_smpL2cDataCback_00537ea8);
              }
            }
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_20 = (uint)*(byte *)(iVar2 + 0x3f);
              local_24 = (uint)param_2;
              local_28 = (uint)bVar1;
              local_2c = PTR_s_unexpected_packet_cmd__d_len__d__00537ea4;
              local_30 = 0x77;
              FUN_0043d574(3,&DAT_005375f4,DAT_00537eac,PTR_s_smpL2cDataCback_00537ea8);
            }
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_20 = (uint)*(byte *)(iVar2 + 0x3f);
            local_24 = (uint)param_2;
            local_28 = (uint)bVar1;
            local_2c = PTR_s_unexpected_packet_cmd__d_len__d__00537ea4;
            local_30 = 0x77;
            FUN_0043d574(2,&DAT_005375f4,DAT_00537eac,PTR_s_smpL2cDataCback_00537ea8);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_20 = (uint)*(byte *)(iVar2 + 0x3f);
          local_24 = (uint)param_2;
          local_28 = (uint)bVar1;
          local_2c = PTR_s_unexpected_packet_cmd__d_len__d__00537ea4;
          local_30 = 0x77;
          FUN_0043d574(1,&DAT_005375f4,DAT_00537eac,PTR_s_smpL2cDataCback_00537ea8);
        }
      }
    }
    else {
      if (bVar1 == 5) {
        local_30 = CONCAT13(*(undefined1 *)(param_3 + 9),0x70000);
      }
      else {
        local_30 = CONCAT13(local_30._3_1_,0x60000);
      }
      local_30 = CONCAT22(local_30._2_2_,(ushort)*(byte *)(iVar2 + 0x3d));
      local_2c = (undefined *)param_3;
      smpSmExecute(iVar2,&local_30);
    }
  }
  return;
}



undefined4
gx8002_pack_message(ushort param_1,ushort param_2,int param_3,ushort param_4,char param_5,
                   uint param_6,ushort *param_7)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint local_6c;
  uint local_68;
  uint local_64;
  uint local_60;
  uint local_5c;
  uint local_58;
  uint local_54;
  uint local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined1 auStack_44 [32];
  
  if ((param_6 == 0) || (param_7 == (ushort *)0x0)) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar4 = (uint)param_4;
    if (param_5 != '\0') {
      param_4 = param_4 + 4;
    }
    if (param_4 < 0x11) {
      local_48 = *DAT_0057c634;
      local_6c = param_6;
      FUN_00439be4(param_6,&local_48,4);
      *(ushort *)(param_6 + 4) = param_1 & 0xff | param_2 & 0xff00;
      pcVar1 = DAT_0057c638;
      *(char *)(param_6 + 6) = *DAT_0057c638;
      *pcVar1 = *pcVar1 + '\x01';
      *(bool *)(param_6 + 7) = param_5 != '\0';
      *(ushort *)(param_6 + 8) = param_4;
      if (((param_3 != 0) && ((short)uVar4 != 0)) &&
         (FUN_00439be4(param_6 + 0xe,param_3,uVar4 & 0xffff), param_5 != '\0')) {
        local_6c = FUN_0058faac(param_3,uVar4 & 0xffff);
        FUN_00439be4((uVar4 & 0xffff) + param_6 + 0xe,&local_6c,4);
      }
      FUN_00439be4(auStack_44,param_6,0xe);
      uVar2 = FUN_0058faac(auStack_44,10);
      *(undefined4 *)(param_6 + 10) = uVar2;
      *param_7 = param_4 + 0xe;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_4c = *(undefined4 *)(param_6 + 10);
        local_50 = (uint)*(ushort *)(param_6 + 8);
        local_54 = (uint)*(byte *)(param_6 + 7);
        local_58 = (uint)*(byte *)(param_6 + 6);
        local_5c = (uint)*(byte *)(param_6 + 4);
        local_60 = (uint)(*(ushort *)(param_6 + 4) >> 8);
        local_64 = (uint)*(ushort *)(param_6 + 4);
        local_68 = (uint)*param_7;
        local_6c = DAT_0057c63c;
        FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057c62c,0x7a);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_58 = *(undefined4 *)(param_6 + 10);
        local_5c = (uint)*(ushort *)(param_6 + 8);
        local_60 = (uint)*(byte *)(param_6 + 7);
        local_64 = (uint)*(byte *)(param_6 + 6);
        local_68 = (uint)*(byte *)(param_6 + 4);
        local_6c = (uint)(*(ushort *)(param_6 + 4) >> 8);
        compress_log_output(0x12000000,DAT_0057c998,DAT_0057c998,*param_7,
                            *(undefined2 *)(param_6 + 4));
      }
      uVar2 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_68 = (uint)param_4;
        local_6c = DAT_0057c628;
        FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c62c,0x57);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0057c630,DAT_0057c630,param_4);
      }
      uVar2 = 0xfffffffe;
    }
  }
  return uVar2;
}


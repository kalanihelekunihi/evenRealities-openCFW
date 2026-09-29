
void FUN_0800680c(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  undefined1 local_18;
  undefined3 uStack_17;
  
  uVar1 = DAT_080068b4;
  uVar2 = param_2 - 2;
  uStack_17 = (undefined3)((uint)param_4 >> 8);
  local_18 = 0x5a;
  case_write_controller_blocking(DAT_080068b8,&local_18,1,DAT_080068b4);
  local_18 = 0xa5;
  case_write_controller_blocking(DAT_080068b8,&local_18,1,uVar1);
  local_18 = 0xff;
  case_write_controller_blocking(DAT_080068b8,&local_18,1,uVar1);
  _local_18 = CONCAT31(uStack_17,(char)param_2);
  case_write_controller_blocking(DAT_080068b8,&local_18,1,uVar1);
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1 & 0xffff) {
    _local_18 = CONCAT31(uStack_17,*(undefined1 *)(param_1 + uVar3));
    case_write_controller_blocking(DAT_080068b8,&local_18,1,DAT_080068b4);
    uVar2 = (uint)*(byte *)(param_1 + uVar3) + (uVar2 & 0xff);
  }
  _local_18 = CONCAT31(uStack_17,(char)uVar2);
  case_write_controller_blocking(DAT_080068b8,&local_18,1,DAT_080068b4);
  if (*(char *)(DAT_080068bc + 0x19) == '\0') {
    if (*(char *)(DAT_080068c0 + 7) == '\0') {
      g2_log_printf(s_____02x____080068c4,uVar2 & 0xff);
    }
    log_hex_buffer(param_1,param_2);
  }
  return;
}


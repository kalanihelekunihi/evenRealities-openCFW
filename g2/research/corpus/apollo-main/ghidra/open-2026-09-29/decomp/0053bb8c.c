
void bq27427_configure_from_params(int *param_1)

{
  bool bVar1;
  char *pcVar2;
  int iVar3;
  char *pcVar4;
  char local_c0;
  byte local_bf;
  char local_9c;
  byte local_9b;
  char local_78;
  byte local_77;
  char local_54;
  byte local_53;
  char local_30;
  byte local_2f;
  
  pcVar4 = &local_c0;
  FUN_0048949c(&local_9c,0x24);
  pcVar2 = DAT_0053c1cc;
  local_9c = *DAT_0053c1cc;
  local_9b = (byte)DAT_0053c1cc[1] >> 5;
  FUN_0048949c(&local_c0,0x24);
  local_c0 = pcVar2[0x10];
  local_bf = (byte)pcVar2[0x11] >> 5;
  FUN_0048949c(&local_30,0x24);
  local_30 = pcVar2[0x18];
  local_2f = (byte)pcVar2[0x19] >> 5;
  FUN_0048949c(&local_54,0x24);
  local_54 = pcVar2[0x28];
  local_53 = (byte)pcVar2[0x29] >> 5;
  FUN_0048949c(&local_78,0x24);
  local_78 = pcVar2[0x30];
  local_77 = (byte)pcVar2[0x31] >> 5;
  iVar3 = bq27427_unseal();
  if (-1 < iVar3) {
    if ((0 < param_1[1]) && (0 < *param_1)) {
      bq27427_read_dm_block(&local_9c);
      bq27427_update_dm_block(&local_9c,0,param_1[1]);
      bq27427_update_dm_block(&local_9c,1,*param_1);
      bq27427_update_dm_block(&local_9c,4,3);
    }
    if (0 < param_1[2]) {
      if ((local_9c == local_c0) && (local_9b == local_bf)) {
        bVar1 = true;
      }
      else {
        bVar1 = false;
      }
      if (bVar1) {
        pcVar4 = &local_9c;
      }
      else {
        bq27427_read_dm_block(&local_c0);
      }
      bq27427_update_dm_block(pcVar4,2,param_1[2]);
    }
    bq27427_read_dm_block(&local_30);
    bq27427_update_dm_block(&local_30,3,0x2b);
    bq27427_read_dm_block(&local_54);
    bq27427_read_dm_block(&local_78);
    bq27427_update_dm_block(&local_78,6,0x28);
    bq27427_write_dm_block(&local_9c);
    bq27427_write_dm_block(&local_c0);
    bq27427_write_dm_block(&local_30);
    bq27427_write_dm_block(&local_78);
    bq27427_seal();
  }
  return;
}


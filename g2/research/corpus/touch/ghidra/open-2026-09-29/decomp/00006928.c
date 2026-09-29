
void msclp_scan_register_prepare(undefined4 param_1,int *param_2)

{
  int iVar1;
  uint *puVar2;
  
  puVar2 = (uint *)**(undefined4 **)(*param_2 + 8);
  *puVar2 = *puVar2 | 0x80000000;
  puVar2[0x48] = DAT_00006974;
  puVar2[0x40] = DAT_00006978;
  msclp_register_config_write(puVar2,6,param_1,puVar2[0x40]);
  iVar1 = DAT_0000697c;
  *(uint *)((int)puVar2 + DAT_0000697c) = *(uint *)((int)puVar2 + DAT_0000697c) | 6;
  *(uint *)((int)puVar2 + iVar1) = *(uint *)((int)puVar2 + iVar1) | 1;
  puVar2[0xe00] = 1;
  return;
}



/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 semantic_device_context_init(void)

{
  undefined4 *puVar1;
  uint uVar2;
  uint uVar3;
  undefined4 in_r3;
  undefined4 uStack_10;
  
  puVar1 = _DAT_004a3800;
  *_DAT_004a3800 = PTR_semantic_bus_read_1_004a3804;
  puVar1[1] = PTR_semantic_bus_write_1_004a3808;
  puVar1[2] = 0;
  puVar1[3] = PTR_FUN_00491102_1_004a380c;
  uStack_10 = in_r3;
  uVar2 = func_0x00504784(puVar1);
  uStack_10 = CONCAT13(uStack_10._3_1_,1);
  uVar3 = func_0x0050655c(puVar1,0,&uStack_10);
  puVar1[6] = PTR_DRV_IMUDataParserCallback_1_004a3810;
  semantic_filter_init(_DAT_004a3814);
  return CONCAT44(uStack_10,uVar2 | uVar3);
}


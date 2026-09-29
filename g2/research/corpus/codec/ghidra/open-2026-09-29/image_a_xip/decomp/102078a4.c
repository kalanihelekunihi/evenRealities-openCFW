
void gx8002_lvp_system_initialize(void)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined *puVar5;
  byte abStack_10 [4];
  
  gx8002_cache_initialize();
  gx8002_dma_initialize();
  gx8002_console_initialize(1,0x1c200);
  uVar1 = func_0x10024940();
  if (uVar1 < 2) {
    gx8002_printf(PTR_s__LVP_Low_Power_Voice_Preprocess_10207a08);
    gx8002_printf(PTR_s__LVP_Copyright__C__2001_2020_Nat_10207a0c);
    gx8002_printf(PTR_s__LVP_ALL_RIGHTS_RESERVED__10207a10);
    gx8002_printf(PTR_s__LVP_Board_Model____s__10207a18,PTR_s_grus_gx8002b_dev_1v_10207a14);
    gx8002_printf(PTR_s__LVP_MCU_Version____s__10207a20,PTR_DAT_10207a1c);
    gx8002_printf(PTR_s__LVP_Release_Ver___0x_x__10207a28,uRam10207a24);
    gx8002_printf(PTR_s__LVP_Build_Date_____s__10207a30,PTR_s_2026_03_26__17_07_25_10207a2c);
    uVar2 = func_0x1002475c(0,0,0x5dc000,0x800);
    iVar3 = func_0x100247e0(uVar2,2);
    if ((iVar3 == iRam10207a34) || (iVar3 == iRam10207a38)) {
      gx8002_printf(PTR_s__LVP_Flash_vendor___s__10207a40,PTR_DAT_10207a3c);
    }
    puVar5 = PTR_sys_esmt_10207a48;
    if (((uint)(iRam10207a44 + iVar3) < 2) ||
       (puVar5 = PTR_sys_zbit_1_10207a70, iVar3 == iRam10207a6c)) {
      gx8002_printf(PTR_s__LVP_Flash_vendor___s__10207a40,puVar5);
    }
    uVar4 = func_0x100247d4(uVar2);
    gx8002_printf(PTR_s__LVP_Flash_type____s__10207a4c,uVar4);
    gx8002_printf(PTR_s__LVP_Flash_ID_____x__10207a50,iVar3);
    uVar2 = func_0x100247e0(uVar2,3);
    gx8002_printf(PTR_s__LVP_Flash_size____d_Byte__10207a54,uVar2);
    uVar2 = func_0x10025210(10);
    gx8002_printf(PTR_s__LVP_CPU_Freq____d_Hz__fix__10207a58,uVar2);
    uVar2 = func_0x10025210(6);
    gx8002_printf(PTR_s__LVP_SRAM_Freq____d_Hz__10207a5c,uVar2);
    uVar2 = func_0x10025210(0xc);
    gx8002_printf(PTR_s__LVP_NPU_Freq____d_Hz__10207a60,uVar2);
    uVar2 = func_0x10025210(0xd);
    gx8002_printf(PTR_s__LVP_FLASH_Freq____d_Hz__10207a64,uVar2);
    iVar3 = func_0x10024710();
    if (iVar3 == 2) {
      gx8002_printf(PTR_s__LVP_enable_bypass_core_Ldo_10207a68);
    }
    else {
      func_0x10024810(8,abStack_10);
      if ((abStack_10[0] & 0xf) < 0xc) {
        iVar3 = (int)*(short *)(PTR_sys_trim_millivolts_10207a74 + (abStack_10[0] & 0xf) * 2);
      }
      else {
        iVar3 = -1;
      }
      gx8002_printf(PTR_s__LVP_Ldo_Trim____d_mV__10207a78,iVar3);
    }
    LvpPrintMaxKwsList();
    gx8002_gpio_initialize();
    gx8002_board_pin_initialize();
    gx8002_rtc_init();
    gx8002_rtc_set_tick(0);
    gx_rtc_start_tick();
  }
  func_0x100257e8();
  func_0x100254e4();
  gx8002_device_list_init();
  gx8002_dw_spi_probe();
  gx8002_power_initialize();
  return;
}


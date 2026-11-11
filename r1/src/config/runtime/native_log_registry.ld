/* Share the native constant IDs with SDK callers. Aliases must be defined
 * inside this output section so they relocate with the table. */
SECTIONS
{
 .log_const_data 0 : ALIGN(4)
 {
  __start_log_const_data = .;
  m_nrf_log_peer_manager_gcm_logs_data_const = . + 0;
  m_nrf_log_peer_manager_gscm_logs_data_const = . + 8;
  m_nrf_log_peer_manager_im_logs_data_const = . + 16;
  m_nrf_log_nrf_ble_gatt_logs_data_const = . + 24;
  m_nrf_log_peer_manager_pds_logs_data_const = . + 32;
  m_nrf_log_peer_manager_pdb_logs_data_const = . + 40;
  m_nrf_log_peer_manager_logs_data_const = . + 48;
  m_nrf_log_peer_manager_handler_logs_data_const = . + 56;
  m_nrf_log_peer_manager_smd_logs_data_const = . + 64;
  m_nrf_log_peer_manager_sm_logs_data_const = . + 72;
  m_nrf_log_clock_logs_data_const = . + 80;
  m_nrf_log_CLOCK_logs_data_const = . + 88;
  m_nrf_log_GPIOTE_logs_data_const = . + 96;
  m_nrf_log_PRS_logs_data_const = . + 104;
  m_nrf_log_UART_logs_data_const = . + 112;
  m_nrf_log_UARTE_logs_data_const = . + 120;
  m_nrf_log_TWIM_logs_data_const = . + 128;
  m_nrf_log_WDT_logs_data_const = . + 136;
  m_nrf_log_RTC_logs_data_const = . + 144;
  m_nrf_log_SAADC_logs_data_const = . + 152;
  m_nrf_log_SPIM_logs_data_const = . + 160;
  m_nrf_log_TIMER_logs_data_const = . + 168;
  m_nrf_log_NFCT_logs_data_const = . + 176;
  m_nrf_log_PDM_logs_data_const = . + 184;
  m_nrf_log_PWM_logs_data_const = . + 192;
  m_nrf_log_app_button_logs_data_const = . + 200;
  m_nrf_log_nrf_fstorage_logs_data_const = . + 208;
  m_nrf_log_pwr_mgmt_logs_data_const = . + 216;
  m_nrf_log_app_logs_data_const = . + 224;
  m_nrf_log_nrf_sdh_logs_data_const = . + 232;
  m_nrf_log_nrf_sdh_ble_logs_data_const = . + 240;
  m_nrf_log_nrf_sdh_soc_logs_data_const = . + 248;
  KEEP(*(.r1.log.modules))
  KEEP(*(.log_const_data_peer_manager_ast))
  KEEP(*(.log_const_data_sortlist))
  __stop_log_const_data = .;
 }
 .log_dynamic_data 0 : ALIGN(4)
 {
  __start_log_dynamic_data = .;
  KEEP(*(.r1.log.dynamic))
  __stop_log_dynamic_data = .;
 }
 /DISCARD/ :
 {
  *(.log_const_data_peer_manager_gcm)
  *(.log_const_data_peer_manager_gscm)
  *(.log_const_data_peer_manager_im)
  *(.log_const_data_nrf_ble_gatt)
  *(.log_const_data_peer_manager_pds)
  *(.log_const_data_peer_manager_pdb)
  *(.log_const_data_peer_manager)
  *(.log_const_data_peer_manager_handler)
  *(.log_const_data_peer_manager_smd)
  *(.log_const_data_peer_manager_sm)
  *(.log_const_data_clock)
  *(.log_const_data_CLOCK)
  *(.log_const_data_GPIOTE)
  *(.log_const_data_PRS)
  *(.log_const_data_UART)
  *(.log_const_data_UARTE)
  *(.log_const_data_TWIM)
  *(.log_const_data_WDT)
  *(.log_const_data_RTC)
  *(.log_const_data_SAADC)
  *(.log_const_data_SPIM)
  *(.log_const_data_TIMER)
  *(.log_const_data_NFCT)
  *(.log_const_data_PDM)
  *(.log_const_data_PWM)
  *(.log_const_data_app_button)
  *(.log_const_data_nrf_fstorage)
  *(.log_const_data_pwr_mgmt)
  *(.log_const_data_app)
  *(.log_const_data_nrf_sdh)
  *(.log_const_data_nrf_sdh_ble)
  *(.log_const_data_nrf_sdh_soc)
 }
 .r1_log_unmapped 0 : { *(.log_const_data* .log_dynamic_data*) }
}
ASSERT(SIZEOF(.log_const_data) == 34 * 8, "update log registry ownership for changed module inventory")
ASSERT(SIZEOF(.log_dynamic_data) == 34 * 4, "log order map must cover all constant records")
ASSERT(SIZEOF(.r1_log_unmapped) == 0, "unmapped SDK log module metadata")

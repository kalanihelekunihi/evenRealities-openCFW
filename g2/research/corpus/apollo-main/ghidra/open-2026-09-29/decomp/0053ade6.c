
longlong bq25180_apply_defaults(void)

{
  uint unaff_r7;
  
  DRV_Bq25180SetChargeEnabled(0);
  DRV_Bq25180SetTsEnabled(0);
  DRV_Bq25180SetFastchargeCurrent(0x5b);
  DRV_Bq25180SetInputCurrentLimit(1000);
  DRV_Bq25180SetPrechargeRatio(2);
  DRV_Bq25180SetTerminationPercent(10);
  DRV_Bq25180SetBatteryOvercurrent(0);
  DRV_Bq25180SetSystemVoltage(1);
  DRV_Bq25180SetBatteryRegulationVoltage(0x1130);
  DRV_Bq25180SetVindpm(1);
  DRV_Bq25180SetBatteryUnderVoltage_lockout(0xaf0);
  DRV_Bq25180SetPrechargeThreshold(0xaf0);
  DRV_Bq25180SetSystemMode(0);
  DRV_Bq25180SetVdppmEnabled(0);
  DRV_Bq25180SetSafetyTimer(1);
  DRV_Bq25180SetWatchdog(0);
  DRV_Bq25180SetTsAutoEnabled(0);
  bq25180_mask_events(0x7f);
  DRV_Bq25180SetChargeEnabled(1);
  return (ulonglong)unaff_r7 << 0x20;
}


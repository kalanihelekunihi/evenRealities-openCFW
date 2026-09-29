
void gx8002_uart_stage1_bringup(undefined4 param_1,undefined4 param_2)

{
  if (*piRam10000618 == 0) {
    *puRam1000061c = 0;
    gx8002_uart_stage1_pmu_dispatch(0x10,1);
    gx8002_uart_stage1_pmu_dispatch(0x11,1);
    gx8002_uart_stage1_pmu_dispatch(0x12,1);
    gx8002_uart_stage1_beacon(param_2,param_1);
    return;
  }
  gx8002_uart_stage1_beacon(0x1c200,0);
  return;
}


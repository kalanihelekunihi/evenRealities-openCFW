
longlong service_algo_process
                   (undefined4 param_1,undefined4 param_2,undefined2 *param_3,undefined2 *param_4)

{
  undefined2 uVar1;
  
  algo_front_data_preprocess(param_1,param_2);
  uVar1 = SVC_SSRProcess(param_1,param_2);
  *param_3 = uVar1;
  uVar1 = service_algo_source_angle(param_1,param_2);
  *param_4 = uVar1;
  return ZEXT48(param_4) << 0x20;
}


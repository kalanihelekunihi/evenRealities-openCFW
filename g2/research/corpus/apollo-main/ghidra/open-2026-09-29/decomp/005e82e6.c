
undefined * semantic_terminal_host_status_name(byte param_1)

{
  undefined *puVar1;
  
  puVar1 = PTR_s_HOST_STATUS_NO_HOST_005e8c3c;
  if (((param_1 != 0) && (puVar1 = PTR_s_HOST_STATUS_STREAMING_005e8c44, param_1 != 2)) &&
     (puVar1 = PTR_s_HOST_STATUS_OFFLINE_005e8c40, 1 < param_1)) {
    puVar1 = PTR_s_HOST_STATUS_UNKNOWN_005e8e40;
  }
  return puVar1;
}



undefined4
service_audio_current_recording_path
          (byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 < 2) {
    service_audio_format_recording_path
              (param_1,*(undefined2 *)(DAT_0057b40c + (uint)param_1 * 0xc + 8),param_2,param_3);
  }
  return param_4;
}


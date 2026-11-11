/* Registered configuration-stop callback, native R1 0x6a4b2..0x6a4d7.
 * Separate full expressions preserve the observed sensor-query order; C
 * function-argument evaluation order cannot express that requirement.
 */
#ifndef R1_NATIVE_CONFIG_STOP_H
#define R1_NATIVE_CONFIG_STOP_H
void gh3x2x_config_set_stop_hook(void)
{
    Gh3x2xIntPinTriggerModePro();
    GH3x2xSlotTimeInfo();
#if (__DRIVER_LIB_MODE__ == __DRV_LIB_WITH_ALGO__)
    GU8 temperature = GH3X2X_GetTempEnableFlag();
    GU8 capacitance = GH3X2X_GetCapEnableFlag();
    GU8 gsensor = GH3X2X_GetGsensorEnableFlag();
    GH3X2X_AlgoSensorEnable(gsensor, capacitance, temperature);
#endif
}
#endif

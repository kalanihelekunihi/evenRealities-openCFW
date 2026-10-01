# Alternate calibration packet selection

For record byte123 equal7, original7BC0 selects descriptor word44 plus20 plus44 times the saved input packet index. Instructions7BFE..7C04 restore that index toR1 before the alternate branch, so this selection does not rely on6AC0 R1 preservation. These648 fixtures vary saved packet indices0/1 and also control6AC0 R1 to the same values, supplying distinct packet offsets while retaining the nonzero state path and arithmetic checks from1503.

The independent model checks output arithmetic against the selected packet word20, state status, hardware control clear and frame restoration. Arbitrary pointer safety remains unresolved. Other record modes select descriptor word40 plus28 times the saved input packet index. Physical behavior and helper clobbers remain unresolved. No canonical admission or C implementation.

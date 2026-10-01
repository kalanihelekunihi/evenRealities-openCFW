# Startup with original configuration table selection

Original 52BC now executes inside original 5378, using authenticated initialized context and copying authenticated table bytes into the original output buffer. The context selects the alternate first row; its 28 bytes are explicitly checked. Original scratch clear and row validator remain active. All inherited startup assertions and exact remaining boundary sequence pass through arrival at 3D50.

50E4 remains controlled, as do other configuration/activation, storage and later application dependencies. Synthetic MMIO and external clock tables remain explicit. Physical meaning and global ownership remain unresolved. No canonical admission or C implementation.

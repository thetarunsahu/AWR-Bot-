# Firmware Workspace

Microcontroller / motor-controller firmware will live here once the physical control hardware is frozen.

Likely responsibilities:

- receive high-level velocity or wheel commands,
- drive motors safely,
- read encoders,
- implement command timeout / watchdog,
- expose battery / fault state,
- support emergency stop behaviour.

Exact firmware architecture depends on the final controller and motor-driver hardware.

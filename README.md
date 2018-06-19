# Raspberry Pi Hardware Interface

Software to control step motors attached to a Raspberry Pi, consisting of 3 components:
- Web interface to send movement commands to Pi and display current rotational offset of the motors
- Logic engine to handle client/server style communication between the web interface and the drivers on the Pi
- Drivers to control the step motors on the Pi

See User Guide.txt for installation details or docs folder for implementation details

Implemented:
- Sending/queueing movement commands and receiving/displaying positional status works
- Commands and positional data can be sent/received asynchronously, with the logic engine handling queueing, threading, etc
- Some error handling implemented, motors can't rotate over 90 degrees for safety

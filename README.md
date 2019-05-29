# apa102_multiplexer

## Compile & Flash FPGA

in `integration_tests` directory perform:

```
source ../venv/bin/activate
PYTHONPATH=.. python3 it_apa102.py --programmer USB-Blaster --permanent
```

## Setup

Create `/etc/modprobe.d/spidev.conf` with content:

```
options spidev bufsiz=262144
```

Executing User should be in `spi` group.


Install package `wiringpi`.

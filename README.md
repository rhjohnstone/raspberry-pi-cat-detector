# Table of Contents

## Overview

This is The Cat Doorbell (version 2.0). I had lots of fun designing and building it. I am writing this in case
someone else might find it useful. For example, this could easily be adapted for dogs.

## The Problem(s)

We have a cat that likes to go out on our enclosed patio. When he is ready to come in, he will stand next to the door
and yell (meow). We then open the door and let him in. No problem.

But, he frequently stays out long enough for us to forget. More than once he was outside yelling and we were oblivious.
That's problem #1.

It is also complicated by the fact that he likes to yell anyway. He will lay on the ground wallowing and yelling just
for the fun of it. That causes "false alarms". We would think he wants in and all he really would be doing is enjoying
life. Frustrating (although I think it amuses the cat). That's problem #2.

Somehow, we needed a device that would:

- Alert us when he wanted inside (fix Problem #1)
- Make sure he wanted inside (fix Problem #2)

Clearly, we needed at Cat Doorbell.

## Basic Logic

The Doorbell listens for a cat and then looks for it. The Doorbell is always listening, but it doesn't look for a
cat until it hears meowing. If dark outside, an LED strip will be used to illuminate the process.

## Logic Detail

This is essentially a small state machine. The Doorbell listens passively for the sound of a cat meowing. When it hears
that sound, it enables a camera. If the on-board light sensor detects darkness, an LED strip will be turned on. For 45
seconds the Doorbell uses the camera in an attempt to identify a cat. If no cat is identified, the Doorbell goes back
to passively listening. If dark, the light is then turned off. If a cat is identified during the 45-second window,
a text message is sent to me. The system then pauses for 2 minutes for me to open the door. If dark, the LED light
stays on until after the 2-minute pause is over. The Doorbell then goes back to listening.

## Geeky Hardware Details

(See the parts list and pictures below for all the components I mention)

### The Raspberry Pi
The heart of the Doorbell is a Raspberry Pi 4B. It sits in a weatherproof junction box next to our patio door. The only
physical connection is a power cable run from inside the house.

### Junction Box Door
The junction box has a clear plexiglass door so the camera can "see". There are also 4 tiny holes drilled into the
underside of the door. These allow the microphone to "hear".

### Wi-Fi

The RPi has Wi-Fi enabled. It is connected to our home network.

### Temperature Precautions
Although the Doorbell is never in direct sunlight, I took some precautions for the Summer heat (I live in Tennessee).
Attached to the RPi motherboard is a special heatsink/fan combination to help regulate temperature. It uses physical
pins #4 (power), #6 (ground) and #8 (GPIO #14). Fan control has been enabled via `raspi-config`.

### Light Sensor
Next to the RPi inside the junction box, is the light sensor. Technically, it is a photo resistor, but I'll refer to it
as "light sensor"). It is connected to physical pins #1 (for 3.3v power), #3 (GPIO #2), and #9 (ground). The light
sensor is encased in a small project box with holes dremeled in it to allow for connections and sensor exposure. The
small box containing the sensor is secured to the inside of the main junction box by strips of magnetic tape
(see pics below).

### USB Camera and Microphone
We use USB for our camera and microphone. Space is tight, so the USB connection is via a right-angle adapter. Here we
connect a little board that is a combination camera/microphone. The board is mounted on the lid of little project box.
The project box fits the width of the junction box exactly. The camera/mic board is secured to the lid with 3 nylon
screws. Coiled inside the project box is the excess USB cable. On the sides of the little box are small dremeled
apertures for cable access.

### LED Strip
Also mounted on the project box I just mentioned is an LED light strip. The strip itself is encased in a small strip of
aluminum trough which is secured to the project box lid with a couple Nylon screws and bolts. The actual LED strip
itself is secured inside the trough with double-sided tape. Snapped on top of the aluminum trough is a light diffuser
(opaque plastic strip). The LED strip is attached to the RPi via 3-pin modular connector. The modular connector is
attached to another modular connector which is directly attached to pins on the RPi. The physical pin used to control
the LED strip #19 (GPIO 10). The strip is powered by physical pin #2 (5V power). Physical pin #14 (ground) is attached
to LED strip's ground connector.

### Power Cable

Like I mentioned before, the only physical connection to the RPi from the outside is power. There are a few things
to mention concerning it. To begin with, inside the house, the cable is attached to the actual power supply using a
USB-C female adapter. The adapter is attached to the cable with wire joiners. At the Doorbell end, the cable enters
the junction box through a weatherproof cable "glad" (icky name). Inside the junction box wire joiners are used to
connect to a male USB-C adapter. Due to space constraints, the RPi USB-C connection goes via a right-angle adapter.

## Wiring

## Fritzing Diagram

## Parts List

1. RPi 4b
2. [RPi Heat Sink and Fan Adapter](https://www.amazon.com/gp/product/B091L1XKL6/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
3. Junction Box
4. Project Box
5. [Dremel Tool](https://www.amazon.com/Dremel-7350-5-3-6v-Rotary-Tool/dp/B08YKH9JRH/ref=sr_1_9?crid=294P32W1GG817&keywords=dremel%2Btool%2Bkit&qid=1696687687&sprefix=dremel%2Caps%2C147&sr=8-9&th=1)
6. [Dremel Bits](https://www.amazon.com/Mars-Rock-Carbide-Compatible-Accessories-Attachments/dp/B0B5TWSRCV/ref=sr_1_10?crid=294P32W1GG817&keywords=dremel%2Btool%2Bkit&qid=1696687809&sprefix=dremel%2Caps%2C147&sr=8-10&th=1)
7. Breadboard Jumper Wires
8. Wire Joiners
9. Wire Stripper
10. Mini Screwdriver Kit
11. Drill
12. 2-Conductor Cable
13. Drill Bits
14. Phillips Head Drill Bit
15. Microphone/Camera Board
16. USB Right Angle Converter
17. USB-C right Angel Converter
18. LED Strip
19. LED Strip Light Diffuser
20. Double Sided Adhesive Tape
21. Wire
22. 3-Pin Connectors
23. Cable Gland (what size?)
24. Female USB-C to Wire Adapter
25. Male USB-C to Wire Adapter
26. RPi 4 USB-C Power Supply
27. Wiring Clips
28. Nylon Screws and Bolts
29. Light Sensor
30. Magnetic Tape
31. Wood Screws
32. Small Project Box

## Pictures 





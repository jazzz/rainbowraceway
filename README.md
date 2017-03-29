Running:
- connect RFID reader on USB port (need to add support for UART serial)
- connect neopixel lights on GPIO 18, common ground with raspberry's ground
- git clone https://github.com/Margravegit/rainbowraceway.git
- apt-get install scons
- sudo scons (only the first time, run from the root folder of the project to build the lirabries)
- cd python/rainbow
- sudo python RFIDtest.py

TO DO LIST:

(!!!!) - MUST BE READY, PRONTO!

(!!!) - Necessary for a fully functional proof of concept

(!!) - Necessary for a full working game

(!) - Extras/quality of life stuff

-----------------------------------

(!!!!) Pot interfacing

(!!!) Single-trike (no communication with track/base/trikes required) Powerup list (placeholder numbers and names)
- Green shell (plushie): Slows down the trike to 20% for 6 seconds
- Red shell (plushie): Slows down the trike to 5% for 6 seconds
- Banana (throwable pad): Slows down the trike to 0% for 3 seconds
- Mushroom (fixed pad): Speeds up the trike to 100% for 3 seconds
- Gold mushroom (fixed pad): Speeds up the trike to 80% for 10 seconds

Race modes
(!!) - 50cc, 100cc, 150cc (top speed limit on the trikes: 40%, 50%, 60%, all powerups enabled)
(!) - Time trial mode (top speed limit 80%, limited to three uses of mushroom powerup on button press, rest of powerups are disabled)
(!) - Star mode (no speed limit, mushrooms disabled, rest of powerups are enabled)
(!) - Battle mode (no track checkpoints, after being hit 3 times trike powers down and player is out, all powerups enabled)
(!!) - Admin mode (no speed limit, no powerups)

(!) Multi-trike (communication with track/base/trikes required) Powerup list (placeholder numbers)
- Lightning bolt (fixed pad): Slows down every other trike to 20% for 6 seconds
- Blue shell (fixed pad): Slows down the trike on first place to 5% for 6 seconds
- Star (fixed pad): Speeds up the trike to 80% for 10 seconds, immune to negative effects for 10 seconds

(!!) Admin cards
- Set up admin cards for quick testing:
    -Set basic colour scheme
    -Set maximum speed
    -Disable further powerup reading

(!!) Remote disabling
- Stop a trike via command from wifi base
- Stop a trike when it leaves the track area (wifi based? GPS tracking?)

(!!) Tag list editing
- Set up easy interface for adding new cards (start reading mode->compare tag with lists->input type->add card to correct list)

(!) Communication with track/base/trikes
- Powerups (bolt, blue shell, mushroom)
- Race Start/checkpoint/finish detection
- Track music/lightning/other effects
- Random powerups
- Powerup cooldown and reactivation

(-) User colour schemes
- Load a custom colour scheme when a user scans his own personal card
- Make some web UI for high-tier backers to edit the colour scheme

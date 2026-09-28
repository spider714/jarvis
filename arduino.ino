/*
   FACE ACCESS SYSTEM
   Arduino UNO + Relay

   Serial commands from Python:

   ON
   OFF

   Relay:
   ON  = access granted
   OFF = access denied / safe state
*/

const int RELAY_PIN = 7;

// Change this if your relay is active LOW
const bool RELAY_ACTIVE_LOW = true;

// --------------------------------------------------
// RELAY ON
// --------------------------------------------------

void relayOn()
{

    if (RELAY_ACTIVE_LOW)
    {
        digitalWrite(
            RELAY_PIN,
            LOW);
    }
    else
    {
        digitalWrite(
            RELAY_PIN,
            HIGH);
    }
}

// --------------------------------------------------
// RELAY OFF
// --------------------------------------------------

void relayOff()
{

    if (RELAY_ACTIVE_LOW)
    {
        digitalWrite(
            RELAY_PIN,
            HIGH);
    }
    else
    {
        digitalWrite(
            RELAY_PIN,
            LOW);
    }
}

// --------------------------------------------------
// SETUP
// --------------------------------------------------

void setup()
{

    pinMode(
        RELAY_PIN,
        OUTPUT);

    // Safe default:
    // relay OFF
    relayOff();

    Serial.begin(9600);

    Serial.println(
        "FACE ACCESS ARDUINO READY");
}

// --------------------------------------------------
// LOOP
// --------------------------------------------------

void loop()
{

    if (Serial.available() > 0)
    {

        String command =
            Serial.readStringUntil('\n');

        command.trim();

        if (command == "ON")
        {

            relayOn();

            Serial.println(
                "RELAY ON");
        }

        else if (command == "OFF")
        {

            relayOff();

            Serial.println(
                "RELAY OFF");
        }
    }
}
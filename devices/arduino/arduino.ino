/**
 * @file arduino.cpp
 * @brief Arduino-based command-driven control system for stepper motors and pneumatic cylinders in a microfluidic system.
 *
 * This program is tailored for a Microfluidic System requiring precise control of stepper motors and pneumatic cylinders. 
 * The system provides a serial command interface for dynamic control, enabling rotation and homing of motors, 
 * extension and retraction of cylinders, and toggling of LEDs.
 *
 * @details
 * - Stepper motors are smoothly controlled using the AccelStepper library, allowing configurable speed and acceleration for precise movements.
 * - Pneumatic cylinders are actuated using digital I/O signals for valves, with feedback from position sensors for reliable operation.
 * - Commands are transmitted over the serial port, and detailed feedback is provided upon task completion for monitoring and debugging.
 * - The system supports modularity and scalability, making it suitable for automation tasks in microfluidic applications.
 *
 * @author [Haoran Yu]
 * @version 1.0
 * @date [04.12.2024]
 */

// Include necessary libraries
#include <Arduino.h>
#include <AccelStepper.h>

// Pin definitions for motor control
#define stepPin1 26       ///< Step pin for motor 1
#define dirPin1 28        ///< Direction pin for motor 1
#define nable1 24         ///< Enable pin for motor 1

#define stepPin2 46       ///< Step pin for motor 2
#define dirPin2 48        ///< Direction pin for motor 2
#define nable2 A8         ///< Enable pin for motor 2

// Pin definitions for solenoid valves
#define valve1Pin1 16     ///< Pin 1 for solenoid valve 1 controlling extension
#define valve1Pin2 17     ///< Pin 2 for solenoid valve 1 controlling retraction
#define valve2Pin1 23     ///< Pin 1 for solenoid valve 2 controlling extension
#define valve2Pin2 25     ///< Pin 2 for solenoid valve 2 controlling retraction

// Pin definitions for LEDs
#define LED1 10           ///< LED 1 control pin
#define LED2 9            ///< LED 2 control pin

// Signal pins for motor homing
#define SIGNAL1 18        ///< Signal pin for motor 1 homing
#define SIGNAL2 19        ///< Signal pin for motor 2 homing

// Signal pins for cylinder actuation
#define SIGNAL_C1_EX 15   ///< Signal pin for cylinder 1 extend
#define SIGNAL_C1_RE 14   ///< Signal pin for cylinder 1 retract
#define SIGNAL_C2_EX 2    ///< Signal pin for cylinder 2 extend
#define SIGNAL_C2_RE 3    ///< Signal pin for cylinder 2 retract

// Common constants
const int microSteps = 8;           ///< Microsteps for stepper motors
const int numBottlesTable1 = 2;     ///< Number of bottle slots for motor 1
const int numBottlesTable2 = 6;     ///< Number of bottle slots for motor 2

// Offset steps between home position and working position
const int motor1_home_offset = 267; ///< Home offset for motor 1 (60 degrees)
const int motor2_home_offset = 133; ///< Home offset for motor 2 (30 degrees)

/**
 * @class Motor
 * @brief Represents a motor controlled via AccelStepper, with capabilities for rotation and homing.
 * 
 * This class manages motor movement for applications requiring precise positioning.
 * It includes homing routines, rotation logic, and integration with sensors for positional feedback.
 */
class Motor {
public:
    AccelStepper& stepper;   ///< Reference to the AccelStepper object controlling the motor.
    const int stepPin;       ///< GPIO pin for the step signal.
    const int dirPin;        ///< GPIO pin for the direction signal.
    const int sensorPin;     ///< GPIO pin for the sensor to detect if the motor is homed.
    const int enablePin;     ///< GPIO pin for enabling/disabling the motor driver.
    const int numBottles;    ///< Number of slots/bottles for rotation calculations.
    const int home_offset;   ///< Offset steps to align the motor to the working position after homing.
    
    // Command state
    bool isActive;           ///< Indicates if the motor is currently active (true if moving).
    bool isHoming;           ///< Indicates if the motor is currently performing a homing sequence.
    int numRotations;        ///< Tracks the number of completed rotations.
    int homingPhase;         ///< Tracks the current phase of the homing sequence.

    int motorID;             ///< Unique identifier for the motor (useful for debugging or multi-motor systems).
    
    /**
     * @brief Constructor for the Motor class.
     * 
     * @param _stepper Reference to the AccelStepper instance.
     * @param _motorID Identifier for the motor.
     * @param _stepPin GPIO pin for the step signal.
     * @param _dirPin GPIO pin for the direction signal.
     * @param _sensorPin GPIO pin for the home sensor.
     * @param _enablePin GPIO pin for the enable signal.
     * @param _numBottles Number of slots/bottles for rotation logic.
     * @param _home_offset Offset in steps to align to the working position after homing.
     */
    Motor(AccelStepper& _stepper, 
          int _motorID, 
          int _stepPin, 
          int _dirPin, 
          int _sensorPin, 
          int _enablePin, 
          int _numBottles,
          int _home_offset) 
        : stepper(_stepper),
          motorID(_motorID),
          stepPin(_stepPin),
          dirPin(_dirPin),
          sensorPin(_sensorPin), 
          enablePin(_enablePin), 
          numBottles(_numBottles),
          home_offset(_home_offset),
          isActive(false),
          isHoming(false),
          numRotations(1),
          homingPhase(0) {}

public:
    /**
     * @brief Initializes the motor pins and AccelStepper configuration.
     * 
     * Sets up the GPIO pins for the motor, configures stepper acceleration/speed, and enables the motor driver.
     */
    virtual void init() {
        pinMode(stepPin, OUTPUT);
        pinMode(dirPin, OUTPUT);
   
        pinMode(enablePin, OUTPUT);
        pinMode(sensorPin, INPUT);
        
        digitalWrite(enablePin, LOW);
        
        stepper.setMaxSpeed(200);
        stepper.setAcceleration(100);
    }

    /**
     * @brief Rotates the motor to the next bottle position.
     * 
     * Divides one full rotation into equal steps based on `numBottles`.
     * Handles rotation correction on the last position to ensure precise alignment.
     * 
     * @note If the motor is currently active, this function will not initiate a new rotation.
     */
    void rotate() {
        if (isActive) return;
        
        // Calculate steps for rotation
        int steps_per_rotation = 200 * microSteps / numBottles;
        int steps_per_rotation_correction = 200 * microSteps - steps_per_rotation * (numBottles - 1);
        
        if (numRotations == numBottles) {
            stepper.move(steps_per_rotation_correction);
            numRotations = 1;
        } else {
            stepper.move(steps_per_rotation);
            numRotations++;
        }
        
        isActive = true;
        isHoming = false;
    }

    /**
     * @brief Executes the homing sequence to find the motor's zero position.
     * 
     * The motor moves away from the sensor if triggered, then seeks the home position.
     * Once the home position is detected, it applies an offset to align to the working position.
     * 
     * @details Three-phase process:
     * 1. Move away from sensor if triggered
     * 2. Find home position
     * 3. Apply home offset
     *
     * @note This function is called repeatedly in the loop until homing is complete.
     */
    void home() {
        if (!isActive) {
            // Start homing sequence
            isActive = true;
            isHoming = true;
            
            if (digitalRead(sensorPin)) {
                // If sensor triggered, first move away 
                homingPhase = 1;
                stepper.move(10000);
            } else {
                // If sensor not triggered, go straight to finding home 
                homingPhase = 2;
                stepper.move(-10000);
            }
        } else {
            // Continue homing sequence
            if (homingPhase == 1 && !digitalRead(sensorPin)) {
                // Moved away from sensor, now to find home 
                stepper.move(-10000);
                homingPhase = 2;
            } 
            else if (homingPhase == 2 && digitalRead(sensorPin)) {
                // Found home
                // Now add offset to reach working position
                stepper.move(home_offset);
                homingPhase = 3;
            }
            else if (homingPhase == 3 && stepper.distanceToGo() == 0) {
                // Found working position 
                stepper.stop();
                stepper.setCurrentPosition(0);

                // Reset all the states
                isActive = false;
                isHoming = false;
                numRotations = 1;
                homingPhase = 0;

                // Send back the feedback message
                String message = "Motor" + String(motorID) + " Homing Completed";
                Serial.println(message);
            }
        }
    }

    /**
     * @brief Updates the motor's state and executes ongoing movements.
     * 
     * Handles the stepper motor updates during motion or homing. If the motor reaches its target,
     * it updates the state and prints debug information.
     * 
     * @note This function should be called frequently in the main loop to ensure smooth operation.
     */
    void update() {
        if (isActive) {
            stepper.run();
            if (isHoming) {
                home();  // Continue homing sequence
            } else if (stepper.distanceToGo() == 0) {
                isActive = false;
                String message = "Motor" + String(motorID) + " Rotation Finished";
                Serial.println(message);
            }
        }
    }
};

/**
 * @class Cylinder
 * @brief Represents a pneumatic cylinder controlled via solenoid valves with extend and retract functionality.
 * 
 * This class provides methods to control the extension and retraction of a pneumatic cylinder, monitor its state, 
 * and manage its positioning through input signals.
 */
class Cylinder {
public:
  const int valvePin1;   ///< GPIO pin for the solenoid valve controlling extension.
  const int valvePin2;   ///< GPIO pin for the solenoid valve controlling retraction.
  const int signalEx;    ///< GPIO pin for the sensor to detect if the cylinder is fully extended.
  const int signalRe;    ///< GPIO pin for the sensor to detect if the cylinder is fully retracted.

  int cylinderID;        ///< Unique identifier for the cylinder (useful for debugging or multi-cylinder systems).
  bool isActive;         ///< Indicates if the cylinder is currently moving (true if extending/retracting).
  bool isExtending;      ///< Indicates if the cylinder is in the process of extending.
  bool isRetracting;     ///< Indicates if the cylinder is in the process of retracting.

  /**
   * @brief Constructor for the Cylinder class.
   * 
   * @param _valvePin1 GPIO pin for controlling the extension solenoid valve.
   * @param _valvePin2 GPIO pin for controlling the retraction solenoid valve.
   * @param _signalEx GPIO pin for the extension position signal.
   * @param _signalRe GPIO pin for the retraction position signal.
   * @param _cylinderID Unique identifier for the cylinder.
   */
  Cylinder(int _valvePin1,
           int _valvePin2,
           int _signalEx,
           int _signalRe,
           int _cylinderID)
          :valvePin1(_valvePin1),
           valvePin2(_valvePin2),
           signalEx(_signalEx),
           signalRe(_signalRe),
           cylinderID(_cylinderID),
           isActive(false),
           isExtending(false),
           isRetracting(false) {}

public:
  /**
   * @brief Initializes the cylinder by setting up GPIO pins and resetting valve states.
   * 
   * Configures the solenoid valve pins as outputs and position signal pins as inputs.
   * Resets the valves to their default inactive states.
   */
  virtual void init() {
    pinMode(valvePin1, OUTPUT);
    pinMode(valvePin2, OUTPUT);

    pinMode(signalEx, INPUT);
    pinMode(signalRe, INPUT);

    // Reset Pin value
    digitalWrite(valvePin1, LOW);
    digitalWrite(valvePin2, LOW);
  }

  /**
   * @brief Initiates the extension of the cylinder.
   * 
   * Activates the solenoid valve connected to `valvePin1` to extend the cylinder.
   * Updates the state to indicate the extension process has started.
   * 
   * @note If the cylinder is already active, this function does nothing.
   */
  void extend() {
    if (isActive) return;

    // Send signal to actuate
    digitalWrite(valvePin1, HIGH);
    
    isActive = true;
    isExtending = true;
  }

  /**
   * @brief Initiates the retraction of the cylinder.
   * 
   * Activates the solenoid valve connected to `valvePin2` to retract the cylinder.
   * Updates the state to indicate the retraction process has started.
   * 
   * @note If the cylinder is already active, this function does nothing.
   */
  void retract() {
    if (isActive) return;

    // Send signal to actuate
    digitalWrite(valvePin2, HIGH);

    isActive = true;
    isRetracting = true;
  }
 
  /**
   * @brief Homes the cylinder by ensuring it is in its default position.
   * 
   * If the cylinder is not already extended, it initiates the extension process.
   * Otherwise, it logs a message indicating the cylinder is already in place.
   * 
   * Resets the solenoid valves to their default inactive states.
   */
  void home() {
    // Reset Pin value
    digitalWrite(valvePin1, LOW);
    digitalWrite(valvePin2, LOW);

    if (!digitalRead(signalEx)) {
      Serial.println("Not in place");
      extend();
    }
    else {
      Serial.println("Already in place");
    }
  }

  /**
   * @brief Updates the state of the cylinder based on input signals.
   * 
   * Monitors the extension and retraction signals to determine when the cylinder 
   * has reached its target position. If a target is reached, the state is updated,
   * and the solenoid valves are reset.
   * 
   * Logs messages to the serial monitor upon completion of extension or retraction.
   */
  void update() {
    if (isActive) {
      if (digitalRead(signalEx) && isExtending) {
        String message = "Cylinder" + String(cylinderID) + " Extension Finished";
        Serial.println(message);

        // Reset Pin value
        digitalWrite(valvePin1, LOW);
        
        isActive = false;
        isExtending = false;
      }
      else if (digitalRead(signalRe) && isRetracting) {
        String message = "Cylinder" + String(cylinderID) + " Retraction Finished";
        Serial.println(message);

        // Reset Pin value
        digitalWrite(valvePin2, LOW);
        
        isActive = false;
        isRetracting = false;
      }
    }
  }
};

// Define instances for stepper motors
AccelStepper stepper1(AccelStepper::DRIVER, stepPin1, dirPin1);
AccelStepper stepper2(AccelStepper::DRIVER, stepPin2, dirPin2);

// Create motor instances
Motor motor1(stepper1, 1, stepPin1, dirPin1, SIGNAL1, nable1, numBottlesTable1, motor1_home_offset);
Motor motor2(stepper2, 2, stepPin2, dirPin2, SIGNAL2, nable2, numBottlesTable2, motor2_home_offset);

// Create cylinder instances
Cylinder cylinder1(valve1Pin1, valve1Pin2, SIGNAL_C1_EX, SIGNAL_C1_RE, 1);
Cylinder cylinder2(valve2Pin1, valve2Pin2, SIGNAL_C2_EX, SIGNAL_C2_RE, 2);

// Define function pointer type for commands
typedef void (*CommandFunction)();

/**
 * @brief Command functions mapped to specific actions.
 */
void led1On() { digitalWrite(LED1, HIGH); } ///< Turns LED1 on.
void led1Off() { digitalWrite(LED1, LOW); } ///< Turns LED1 off.
void led2On() { digitalWrite(LED2, HIGH); } ///< Turns LED2 on.
void led2Off() { digitalWrite(LED2, LOW); } ///< Turns LED2 off.
void motor1Rotate() { motor1.rotate(); } ///< Rotates motor1.
void motor1Home() { motor1.home(); } ///< Homes motor1.
void motor2Rotate() { motor2.rotate(); } ///< Rotates motor2.
void motor2Home() { motor2.home(); } ///< Homes motor2.
void cylinder1Extend() { cylinder1.extend(); } ///< Extends cylinder1.
void cylinder1Retract() { cylinder1.retract(); } ///< Retracts cylinder1.
void cylinder1Home() { cylinder1.home(); } ///< Homes cylinder1.
void cylinder2Extend() { cylinder2.extend(); } ///< Extends cylinder2.
void cylinder2Retract() { cylinder2.retract(); } ///< Retracts cylinder2.
void cylinder2Home() { cylinder2.home(); } ///< Homes cylinder2.

/**
 * @struct Command
 * @brief Structure to map command names to their respective functions.
 */
struct Command {
    const char* name;
    CommandFunction function;
};

/**
 * @brief Array of commands used for command lookup.
 * 
 * Each command maps a string (received over serial) to a specific function.
 */
const Command commands[] = {
    {"LED1 on", led1On},
    {"LED1 off", led1Off},
    {"LED2 on", led2On},
    {"LED2 off", led2Off},
    {"motor1 rotate", motor1Rotate},
    {"motor1 home", motor1Home},
    {"motor2 rotate", motor2Rotate},
    {"motor2 home", motor2Home},
    {"cylinder1 extend", cylinder1Extend},
    {"cylinder1 retract", cylinder1Retract},
    {"cylinder1 home", cylinder1Home},
    {"cylinder2 extend", cylinder2Extend},
    {"cylinder2 retract", cylinder2Retract},
    {"cylinder2 home", cylinder2Home},
    {NULL, NULL}  // Sentinel to mark the end of the array
};

/**
 * @brief Executes the command received over serial.
 * 
 * This function looks up the received command in the `commands` array and executes
 * the corresponding function. If the command is not found, it prints an error message.
 * 
 * @param cmd The command string received over serial.
 */
void executeCommand(const char* cmd) {
    for (int i = 0; commands[i].name != NULL; i++) {
        if (strcmp(cmd, commands[i].name) == 0) {
            commands[i].function();
            return;
        }
    }
    Serial.println("Unknown command");
}

void setup() {
    Serial.begin(9600);
    
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);

    motor1.init();
    motor2.init();

    cylinder1.init();
    cylinder2.init();
}

void loop() {
    if (Serial.available() > 0) {
        String cmd = Serial.readStringUntil('\n'); 

        // Remove any trailing whitespace or non-printable characters
        cmd.trim();

        // // Debug print the received command
        // Serial.print("Received command: '");
        // Serial.print(cmd);
        // Serial.print("'\n");

        executeCommand(cmd.c_str());
    }

    motor1.update();
    motor2.update();

    cylinder1.update();
    cylinder2.update();

}
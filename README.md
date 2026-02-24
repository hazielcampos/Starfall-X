# Starfall X 💫
`Octobots x Starline`

### Description:
**Starfall X** is an autonomous mobile robot that uses artificial vision algorithms to avoid obstacles, follow tracks and solve WRO: Future Engineers 2026 challenges.

All the software and mechanics were designed under the *KISS method (Keep It Simple - Stupid)* so we tried to keep the electronics and mechanics clean and the software the more simple possible without loosing stability and functionality of the robot.

I like to see our robot as the representation of our robotics team, the software is divided by nodes, each node is responsible of an specific task and there's always the supervisor who does nothing but when a node crash or get stopped the supervisor kick him in his face and make it work again (just like our coach), and the mechanics part... well there's not much but it works, just like our budget lol.

## Electronics 🪫
The electronics are designed to be the simplest possible to avoid failures and common problems during the runs.
For the main controller of the robot, the brain, we use an **Raspberry PI 5 with 8GB of ram**.

> ***Why we choose that SBC?***
We choose the PI 5 bc it has a powerful processor to handle all the nodes and the artificial vision algorithms.
Also it is the most modern platform from raspberry and it is not as expensive as a jetson nano lol.
***And what about the 8GB?***
that was a very strategic decision and it was because we already have one.

Connected to the PI 5 using usb and serial we decided to integrate an MCU to handle real time operations with RTOS, so the best choice for that was the **ESP32 WROOM V1**

> ***Why esp32?***
We are using the ESP32 WROOM V1 because it is powerful, cheap and easy to use, we can code it with arduino and it has all the capabilities to control the robot actuator, we can handle precise PWM to control the servo without jitter and the motor pwm and it was easy to integrate with the raspberry using the usb c port.

## Software 💻

Lets talk about the software.
We used a node based architecture to ensure parallelism, scalability and stability.

**Decisions we made about the software:**
We decided to use and cam only based navigation system, we use the camera of the robot and the visual signals of the track to count turns, avoid obstacles and follow the paths avoiding the walls.

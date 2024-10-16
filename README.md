# Rock-Paper-Scissors Tournament with ESP32CAM

This project is an advanced Rock-Paper-Scissors game that uses an **ESP32CAM** module with camera integration and a graphical user interface (GUI). Players can sign up and participate in a tournament, where each match is conducted using real-time image processing to detect hand gestures (Rock, Paper, or Scissors). The game also includes an **AI mode** where players can compete against an AI that learns and improves over time.

## Features

- **ESP32CAM Integration**: Uses the ESP32CAM module to capture images of players’ hand gestures in real-time.
- **Tournament Mode**: Multiple players can sign up and compete in a tournament. The system processes each game and determines winners based on hand gestures.
- **AI Mode**: Play against an AI that adapts and learns from your moves, becoming more challenging as you play.
- **GUI Interface**: A user-friendly interface for signing up, playing games, and tracking tournament progress.
- **Image Processing**: The camera captures players' hand gestures, and image recognition algorithms determine the winner.
  
### Hardware Setup

1. **ESP32CAM Setup**: Connect the ESP32CAM module to your system and flash it with the appropriate firmware for image capturing.
2. **Camera Positioning**: Place the camera so that it can clearly capture players' hands during the game.


### Game Modes

- **Tournament Mode**: 
    - Players sign up through the GUI and compete in a series of matches. The ESP32CAM captures the players’ hand gestures, and image recognition determines the winner of each round.
  
- **AI Mode**:
    - Players can choose to play against an AI opponent. The AI becomes more challenging over time by learning the player's patterns and strategies.

## Future Improvements

- **Enhanced AI**: Further improve AI learning capabilities to detect more complex patterns.
- **Multiplayer over the network**: Add network functionality to enable players to compete remotely.
- **Mobile App**: Create a mobile app for easier access and gameplay.

---

Let me know if you need any adjustments!

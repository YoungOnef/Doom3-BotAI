# Doom3-BotAI

AI implementation for a bot in Doom 3. The bot AI involves various functionalities, including visportals for handling visibility, automatic lights placement, and Python bot API analysis. The project aims to create an interactive and dynamic bot that can navigate the game environment, shoot players, collect ammo, and move between different points on the map.

## Project Components

### Visportals
![image](https://github.com/YoungOnef/Doom3-BotAI/assets/72264732/776ce655-46d4-48e4-90e9-707b55944da2)


The implementation includes vertical and horizontal visportals that determine the size and position of bricks containing visportal textures with visibility properties.
- The code efficiently determines whether the visportal is vertical or horizontal and calculates its size accordingly.
- Green visportals represent loaded parts of the rooms, while red visportals represent parts of the rooms that are not loaded.

### Automatic Lights
![image](https://github.com/YoungOnef/Doom3-BotAI/assets/72264732/fd152d97-7c62-4b1f-983e-80a4aac3846c)


The algorithm intelligently places lights near walls around specific locations.
- A frequency value can be defined for lights; if not specified, it defaults to 3.
- Lights are spawned next to walls with a frequency of 3.

### Python Bot API Analysis
![image](https://github.com/YoungOnef/Doom3-BotAI/assets/72264732/3487be59-eff2-4eda-875e-08ecb14bcb37)


The bot is equipped with various states that enable it to perform different actions within the game environment.
- The states include jumping, shooting, finding and collecting ammo, and moving towards specified labels.
- The bot interface relies on other libraries, such as botlib.py, to communicate with the game code and execute actions effectively.

The visual representations provide insights into the efficient functioning of the Doom 3 bot AI.


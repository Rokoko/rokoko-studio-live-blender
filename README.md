# Rokoko Studio Live Plugin for Blender

This plugin lets you stream your animation data from Rokoko Studio directly into Blender. It also allows you to easily record and retarget animations.

### Requirements
 - Blender **2.80** or higher

### Installation
 - Download the plugin: **[Rokoko Studio Live for Blender](https://github.com/RokokoElectronics/rokoko-studio-blender-plugin/archive/master.zip)**
 - In Blender go to Edit > Preferences
 - In Preferences go to Add-ons > Install
 - Select the downloaded zip file and install it
 - Enable "Rokoko Studio Live for Blender" by checking the checkbox next to it
 - Done!
 
### Usage
 - Please visit this link for the full documentation: https://rokoko.freshdesk.com/support/solutions/folders/47000761699

#### Retargeting Guide:
   [<img src="https://img.youtube.com/vi/Od8Ecr70A4Q/maxresdefault.jpg" width="50%">](https://youtu.be/Od8Ecr70A4Q)
 
### Changelog

#### 1.1.1
- Added Retargeting panel
    - This allows you to easily retarget any animation from one character to another
    - It uses our auto detect system to automatically find matching bones between the two characters
- Added the functionality to save, import and export custom naming schemes
- Added recording timer
- Reworked saving of recordings
    - This resulted in heavily improved processing speeds of recorded animations
    - Recordings no longer need to be split
    - Recorded animations are now using euler angles instead of quaternion
      - This allows for easier editing and better continuity of the animation
- Added patch that fixes the slow import of FBX animations in Blender 2.80 to 2.82
    - This means that as long as you have this plugin enabled, you will get very fast FBX animation imports
    - We submitted this patch to Blender officially and it got accepted, so it is included by default in Blender 2.83 and higher (fast imports for everyone, hooray!)

#### 1.0.0
 - First version of Rokoko Studio Live for Blender
 - Character animation and recording
 - Face animation and recording
 - Virtual production animation and recording
 - Studio Command API support.
 - Auto-updater

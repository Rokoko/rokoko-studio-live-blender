<h1 align="center">Rokoko Studio Live Plugin for Blender</h1>

[Rokoko Studio](https://www.rokoko.com/en/products/studio) is a powerful and intuitive software for recording, visualizing and exporting motion capture.

This plugin lets you stream your animation data from Rokoko Studio directly into Blender. It also allows you to easily record and retarget animations.

---

## Requirements
- Blender **2.80** or higher
- For livestreaming data: Rokoko Studio 1.18.0b or higher or Studio 2
- An internet connection during the installation to get the required libraries

## Features
- Live stream data:
    - Up to five actors that can all include both body, face (52 blendshapes) and finger data at the same time
    - Camera data
    - Props data
- Control Rokoko Studio from within Blender
- Easily retarget motion capture animations

## Installation
- Download the latest version [here](https://github.com/Rokoko/rokoko-studio-live-blender/archive/refs/heads/master.zip)
- In Blender go to Edit > Preferences > Addons > Install.. and then select the downloaded zip file
  - First time installation can take a while
- To use the plugin, press N and select the Rokoko panel
 
---

## Getting Started for Streaming

### Make sure the model is ready for Studio Live
The character in Blender has to be in T-pose:

  <img src="https://i.imgur.com/p4uVZBx.png" height="450"/>

**For SmartGloves:** Make sure that the character's hands and fingers are posed as close as possible to the following pose to get the best 
possible retargeting of finger animation. All fingers should be straight and the thumb should be rotated 45 degrees away from the other fingers.

  <img src="https://i.imgur.com/9I13bHI.png"/>

### Enabling Rokoko Studio Live
- In Rokoko Studio go to settings and click on **Studio Live** in the dropdown menu and enable the Blender data stream. You can customize the streaming address and port by clicking the wrench icon at the top left

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47009137268/original/iUPhbfdu2-FVfsBHs_RlWeqyhekQX9_Lbw.png" height="500" /> &nbsp;&nbsp;&nbsp;
  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47011953744/original/CxBalqeKrhgesFhgEf69gr4fVNxx3p0ZcQ.gif"/>

### Receiving the Data in Blender
- In the 3D view press N or the little arrow on the right side, then select the "Rokoko" tab and press "Start Receiver" to start receiving data from Rokoko Studio

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47010394035/original/F9BVdJ-P3GjPAqGsOno-it18A0lvyF3n3A.png"/> &nbsp;&nbsp;&nbsp;
  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47010394045/original/1E4Pt708FhhoGngovjP7V3CYVaNgNG_J_w.png"/> &nbsp;&nbsp;&nbsp;
  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47010394056/original/Um5r_amKNoEJaF8vjF1JgQwVyjztGDtJ5w.png"/>

### Streaming Character Data
- After starting the receiver select the armature that you want to animate
- Go into the object category and open the "Rokoko Studio Live Setup" panel
- In the actor field select the Smartsuit that you want to use for this armature
- Fill all bone fields by pressing “Auto Detect” and check if all bones are correctly filled in and fill in missing bones if necessary
- Ensure that the selected armature is in T-Pose and then press “Set as T-Pose”

  <img src="https://i.imgur.com/ydn6cAi.gif"/>

- Done! Your armature should be animated by the live data:

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47011948259/original/JDKx_BMV2iDNhqyEk1nsNqsm8zQt2YbT5g.gif" height="500"/>

- Optional: In order to improve animation performance enable “Hide Meshes during Play” in the receiver panel

  <img src="https://i.imgur.com/HESveWD.png"/>

- If you experience any lag while using the plugin, close the window that shows key frames (e.g. timeline or action editor). Blender will run much smoother as the panel takes a lot of resources.

### Streaming Face and Prop Data
- This uses the exact same workflow as streaming character data
- Just select the face mesh for face data or the object for prop data and then follow the steps above
- Done! Your face mesh or prop should now be animated by the live data

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47011946440/original/-2ES8ffaPb-jANEBaZWpLzvoy6gDB_FPXQ.gif" height="400"/> &nbsp;&nbsp;&nbsp;
  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47011950531/original/LB3AZ4q5IIPOX-WF1mYuuRqeNsWsGY_hgw.gif" height="400"/>

- Note for prop data: After selecting the prop data you can turn on "Use Custom Scale" and change the animation scale for this prop, to make sure it fits your Blender project

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47011950790/original/vpwUqdfTZJcBryvKjJmUfV0BXKT3kX__eQ.PNG"/>

---

## Retargeting
In order to retarget an animation in Blender you will need to do the following:

- Open the Retargeting panel

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47029758599/original/gt30hHJ2JCfKDmmALDxjffiHbYjqFMQFmg.png"/>

- Select an armature with an animation as the source armature, select an armature that should receive the animation as the target armature and then press "Build Bone List"

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47029758649/original/AuSYaHVCMTAQmTYRX8JHohflx4B6tu7EVQ.png"/>

- Check if the bones got filled in correctly and fix any incorrect or missing bones

  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/47029758669/original/O_kTjk6qEKnNr_jOmvMXa2OI5d561ttBqA.png"/>

- Select "Auto Scale" if the armatures differ in size or resize them manually
- In "Use Pose:" select the pose that should be used for retargeting
- Important: Make sure that both armature are in the same pose for correct retargeting
- Press "Retarget Animation"
- Done!

   [<img src="https://img.youtube.com/vi/Od8Ecr70A4Q/maxresdefault.jpg" width="50%">](https://youtu.be/Od8Ecr70A4Q)

---
 
## Changelog

#### 1.4.0
- Added support for Blender 3.0/3.1 and Rokoko Studio 2
- Fully reworked login
  - Login now works via browser for easier use
- Retargeting: Added support for multiple target bones per source bone

#### 1.3.0
- Added support for Blender 2.93
- Fixed login email being case-sensitive
- Added a popup with a download link in case the user is missing a Windows library

#### 1.2.1
- Fixed login issue when using a Blender UI language other than English

#### 1.2.0
- Added support for the new [Rokoko Smartgloves](https://www.rokoko.com/products/smartgloves)
- Fixed an issue with the auto-updater which caused updates to fail
 
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

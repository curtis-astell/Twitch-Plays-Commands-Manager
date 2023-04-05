Twitch Plays Commands Manager

The Twitch Plays Commands Manager utilizes the expanded Twitch Plays code made by DougDoug and DDarknut. With this program, you can easily
create custom commands and macros for different games without needing any prior coding knowledge. This guide will go over the different parts of the program
and show you how to get started.

* The Login Window:
  
  Initially you will be greeted by the login window, prompting you to enter stream info.
  
  * On the left hand side is an entry for "Twitch Channel". Here you can enter the name of the channel you're streaming from.
    It is not case sensitive. 
  * On the right you will see two other text entries. The first is for your YouTube Channel ID. You can find this by clicking
    your YouTube profile picture -> Settings -> Advanced Settings. This is necessary to connect to a YouTube stream.
  * Beneath that is an entry for YouTube Stream URL. This is only needed if you're testing an unlisted stream. Otherwise, leave it as None.
  * Finally, you can click on either "Connect Twitch Stream" or "Connect YouTube Stream". Clicking either of these tells the program which type 
    of stream you're planning on hosting.
    
* Main Grid Window:

  Next you'll see the main window, with a grid of games, as well as some buttons at the top.
  
  * In the very top left is the Options button. Clicking this lets you adjust some basic stream settings.
  * To the right of that is the Add Game button. Clicking this will prompt you to type the title of the game you're going to create commands for.
  * In the middle of the screen is a grid of games. Clicking any of them will reveal a hidden menu for each. These menus contain the following buttons:
     - Game Title: You can click "Change Title" to rename a game
     - Cover Art Directory: Clicking "Change Art" will open the windows file explorer, allowing you to change a games cover art
     - Chat Commands: Clicking "Modify Commands" will open the Commands Manager window, which is where you will create commands and the associated macros
     - Link Game to Stream: Clicking the corresponding link button will open the Stream Link window, which will attempt to link to your livestream, and will then process incoming messages for you.
     - Delete Game: Clicking delete will remove the game and its associated commands from the program. Doing this is permanent.

* Chat Commands Manager:

  If you click on the Modify Commands button for a game, a window to customize that games commands will open. For this tutorial, open the Commands Manager for Pokemon Red Version.
  
  * In the top left is a "Save Commands" button.
  * The left table beneath the button is your Message table. Each line represents a command that the program recognizes. For Pokemon Red you should see commands like, "up", "down", "start" and so on. Click through these messages, and notice how the table on the right displays new information.
  * The right table is a list of your macros for the selected command. Each recognized command can have 10 macros associated with it. If you have "up" selected in the Message table, you'll notice the Commands table has one row with the values, "Press Key", "w", "0.5". This means that if a user types in the word "up" into your stream chat, the program will proceed to press the "w" key for 0.5 seconds. The first column of the commands table contains a drop down menu with the following values:
      - "Press Key", which presses and releases the key listed under "Keystroke" for the amount of seconds written under "Duration"
      - "Hold Key", which presses the key listed under "Keystroke" indefinitely.
      - "Release Key", which releases the key listed under "Keystroke". This is useful for letting go of a held key.
      - "Move Mouse", which moves the mouse. Under "Direction" you can write "up", "down", "left", or "right". The mouse will be moved the amount of pixels listed under the "Duration" column.

  A list of all the keycodes will be at the end of this guide.

* Stream Link Window:
  
  When you click the link stream button, a small black window will open and attempt to connect to your livestream. If you've entered the information to the Login Window correctly, you shouldn't have any problems. That said, this window should alert you to any issues or problems with the stream, including issues with macros if it recognizes a command but can't implement it. Beyond that, there's not any interactivity to be had with the Stream Link Window. To disconnect it, simply close the window and the Main Grid will open back up again.
  
* Options Window: 

  If you want to adjust your stream settings this is the place to do it. You can adjust the following parameters:
  
  * Message Rate: This controls how fast we process incoming Twitch Chat messages. It's the number of seconds it will take to handle all messages in the queue. Twitch delivers messages in "batches", rather than one at a time, so we process the messages over duration of "Message Rate", rather than processing the entire batch at once. Keep in mind that a smaller number means we go through the message queue faster, but we will run out of messages faster and activity might "stagnate" while waiting for a new batch. A higher number means we go through the queue slower, and messages are more evenly spread out, but delay from the viewers' perspective is higher. Setting this to 0 will disable the queue and handle all messages immediately. However, the wait for another batch of messages is far more pronounced.
  * Max Queue Length: This limits the number of commands that will be processed in the previously mentioned "batch" of messages. Lowering this value is helpful for games where too many inputs would hinder gameplay. Raising this value is good for creating total chaos.
  * Max Workers: This is the maximum number of threads you can process at a time.

* Keycodes:

  For a keystroke to be valid it has to be written out in the proper formatting. It's worth noting that none of the keystrokes in this program are case sensitive.
  Here is a list:

    - Alphabetical: Can be written out as is. For example, "A" or "W" and so on.
    - Arrow Keys: Left_Arrow, Right_Arrow, Up_Arrow, Down_Arrow
    - Numbers: Need to be spelled out. "Four" is valid, "4" is not.
    - F Keys: Written out as is. For example, "F1" or "F5" and so on.
    - Numpad: "Numpad_" followed by the key name. For example, "Numpad_0" or "Numpad_Enter". Keys like + or - need to be written as "Numpad_Plus" and "Numpad_Minus".
    - Mouse: Left_Mouse, Right_Mouse, Middle_Mouse for your clicks. Mouse_Wheel_Up and Mouse_Wheel_Down for your scroll wheel.
    
    - Miscellaneous/Special Characters:
      - MINUS
      - EQUALS
      - BACKSPACE
      - APOSTROPHE
      - SEMICOLON
      - TAB
      - CAPSLOCK
      - ENTER
      - LEFT_CONTROL
      - LEFT_ALT
      - LEFT_SHIFT
      - RIGHT_SHIFT
      - TILDE
      - PRINTSCREEN
      - NUM_LOCK
      - SPACE
      - DELETE
      - COMMA
      - PERIOD
      - BACKSLASH
      - FORWARDSLASH
      - LEFT_BRACKET
      - RIGHT_BRACKET

#!/bin/bash
# prompts for a search term
# - if windows is closed, cancel is clicked, or ESC is pressed, nothing happens
# - if user does not enter any text and presses enter (or clicks "ok"), then it just opens a random page provided by google's "i'm feeling lucky" button
# - if user is enters some text, it opens the first result for a search of that term

# sorry it's all one line.. it was originally inside of the i3 config file, but i3 complained because it was too complicated :(

t=$(zenity --entry --title="Google search..." --text="Ask the oracle"); if [ $? -eq 0 ]; then if [ "x$t" == "x" ]; then google-chrome --new-tab "https://google.com/search?btnI"; else google-chrome --new-tab "https://google.com/search?q=$t&btnI"; fi; fi;

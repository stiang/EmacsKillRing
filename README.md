### Emacs Kill Ring for Sublime Text 2

This is an adaption of the [EmacsKillRing][1] for Sublime Text 2. It was created 
for the ST2 alpha, so it may need some adjustments to work with the final release.

I don’t know who the original author is, but (s)he did most of the hard work, I
mostly adapted the code to conform to the new API and added region highlighting
when a mark has been set.

Please note that I am not very familiar with Python, so there may be extremely
silly bugs. I’d be happy to include your improvements.

#### Usage

Copy EmacsKillRing.py to your Packages/User folder, then add some key-bindings for
the new commands, like so:

    { "keys": ["ctrl+w"], "command": "expand_selection", "args": {"to": "word"} },
    { "keys": ["ctrl+k"], "command": "emacs_kill_line" },
    { "keys": ["ctrl+y"], "command": "paste" },
    { "keys": ["ctrl+u"], "command": "prev_view" },
    { "keys": ["ctrl+i"], "command": "next_view" },
    { "keys": ["ctrl+shift+y"], "command": "emacs_yank_choice" },
    { "keys": ["ctrl+space"], "command": "emacs_set_mark" },
    { "keys": ["ctrl+w"], "command": "emacs_kill_to_mark" },
    { "keys": ["alt+w"], "command": "emacs_kill_ring_save" },
    { "keys": ["ctrl+g"], "command": "cancel_mark" }


[1]: http://sublime-text-community-packages.googlecode.com/svn/pages/EmacsKillRing.html
[2]: http://www.sublimetext.com/2
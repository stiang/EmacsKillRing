#
# emacs-style killbuffer commands; kill, and yank
# 


import sublime_plugin, sublime, re

#
# An implementation of the emacs kill ring.
#
class KillRing:
  def __init__(self):
    # constructs the killring, a list acting basically 
    # as a stack. Items are added to it, and currently not removed.
    self.killRing = [""]
    # the last kill position remembers where the last kill happened; if
    # the user moves the cursor or changes buffer, then killing starts a 
    # new kill ring entry
    self.LastKillPosition = -1
    
  def peek(self):
    # returns the top of the kill ring; what will
    # be inserted on a basic yank.
    return self.killRing[-1]
    
  def new(self):
    # starts a new entry in the kill ring.
    self.killRing.append("")
    
    
  def append(self, content):
    # appends killed data to the current entry. 
    # Also updates the windows clipboard with 
    # everything in this kill entry
    self.killRing[-1] = self.killRing[-1] + content
    sublime.set_clipboard(self.killRing[-1])
 
  def choices(self):
    # tuples of integers with kill-ring entries. 
    # Used by the yank choice command
    choiceArr = []
    for i in range(1,len(self.killRing)):
      choiceArr.append( (i,self.killRing[i]) )
    choiceArr.append( ("clipboard", "Windows Clipboard: " + sublime.get_clipboard()))
    return choiceArr
    
  def get(self, idx):
    # gets a numbered entry in the kill ring
    return self.killRing[idx]

#
# An implementation of the system of marks in emacs buffers
#
class Marks:
  def __init__(self):
    self.innerMarks = {}
    
  def setMark(self, view):
    self.clearMark(view)
    s = view.sel()[0]
    viewName = self.viewIdentifier(view)
    point = s.begin()
    self.innerMarks[viewName] = s.begin()
    sublime.status_message("Set mark at char %s in %s" % (point, viewName))
    
  def viewIdentifier(self, view):
    id = view.file_name()
    if id == None:
      id = "<?unknown?>" # unlikely to be a filename
    return id
    
  def clearMark(self, view):
    # if we've cut, we want to unset the mark
    # on this buffer
    s = view.sel()[0]
    viewName = self.viewIdentifier(view)
    view.erase_regions('set-mark-region')
    if viewName in self.innerMarks:
      del self.innerMarks[viewName]
    
  def selectMark(self, view):
    s = view.sel()[0]
    viewName = self.viewIdentifier(view)
    if viewName in self.innerMarks:
      start = min(s.begin(), self.innerMarks[viewName])
      end = max(s.end(), self.innerMarks[viewName])
      region = sublime.Region(start, end)
      return region
    
  def killMark(self, view):
    global marks
    region = self.selectMark(view)
    if region:
      view.sel().add(region)
      view.run_command("emacs_kill_region")
      self.clearMark(view)
    
  def copyMark(self, view):
    global marks
    global killRing
    region = self.selectMark(view)
    content = view.substr(region)
    killRing.new()
    killRing.append(content)
    print content
    self.clearMark(view)    

#
# Base class for Emacs selection commands. 
#
# Only enabled if there is exactly one selection.
#
class EmacsSelectionCommand(sublime_plugin.TextCommand):
  def run(self, view, **args):
    print "Not appropriate in base class"

  def isEnabled(self, view, args):
    # disable kill for multi-selection. Too much of a headache!
    if len(self.view.sel()) != 1:
      return False
    return True
    
  
#
# the global killring and mark collection
#  
killRing = KillRing()
marks = Marks()

def expandSelectionForKill(view, begin, end):
  """Returns a selection that will be cut; basically, 
  the 'select what to kill next' command."""
  
  # the emacs kill-line command either cuts 
  # until the end of the current line, or if 
  # the cursor is already at the end of the 
  # line, will kill the EOL character. Will 
  # not do anything at EOF
  
  if  atEOL(view, end):
    # select the EOL char
    selection = sublime.Region(begin, end+1)
    return selection
    
  elif atEOF(view, end):
    # at the end of file, do nothing; the 
    # selection is just the initial selection
    return sublime.Region(begin, end)
    
  else:
    # mid-string -- extend to EOL
    current = end
    while not atEOF(view, current) and not atEOL(view, current):
      current = current+1
    selection = sublime.Region(begin,current)
    return selection

def atEOL(view, point):
  nextChar = view.substr(point)
  return  nextChar == "\n"

def atEOF(view, point):
  nextChar = view.substr(point)
  return ord(nextChar) == 0

  

#
# Kill Line
#
class EmacsKillLineCommand(EmacsSelectionCommand):
        
  def isEnabled(self, edit, args):
    if EmacsSelectionCommand.isEnabled(self, edit, args) == False:
      return False
      
    # if we are at the end of the file, we can't kill.
    s = self.view.sel()[0]
    charAfterPoint = self.view.substr(s.end())
    if ord(charAfterPoint) == 0:
      # EOF
      return False
      
    return True

  def run(self, edit, **args):
    global killRing

    s = self.view.sel()[0]
    
    if killRing.LastKillPosition != s.begin() or killRing.LastKillPosition != s.end():
      # we've moved the cursor, meaning we can't 
      # continue to use the same kill buffer
      killRing.new()
       
    expanded = expandSelectionForKill(self.view, s.begin(), s.end())
    killRing.LastKillPosition = expanded.begin()
    killRing.append(self.view.substr(expanded))
    # self.view.erase(expanded)
    self.view.erase(edit, expanded)

#
# Kill region
#
class EmacsKillRegionCommand(EmacsSelectionCommand):
        
  def isEnabled(self, edit, args):
    if EmacsSelectionCommand.isEnabled(self, edit, args) == False:
      return False
      
    # if we are at the end of the file, we can't kill.
    s = self.view.sel()[0]
    charAfterPoint = self.view.substr(s.end())
    if ord(charAfterPoint) == 0:
      # EOF
      return False
      
    return True

  def run(self, edit, **args):
    global killRing

    s = self.view.sel()[0]
    
    if killRing.LastKillPosition != s.begin() or killRing.LastKillPosition != s.end():
      # we've moved the cursor, meaning we can't 
      # continue to use the same kill buffer
      killRing.new()
       
    killRing.LastKillPosition = s.begin()
    killRing.append(self.view.substr(s))
    self.view.erase(edit, s)
    
#
# Yank any clip from the kill ring
# 
class EmacsYankChoiceCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    # choose from the yank-buffer using the quick panel
    global killRing
    choices = killRing.choices()
    names = [name for (idx, name) in choices]
    idx = ["%s" % idx for (idx, name) in choices]
    #print "YANK CHOICE IN " + view.fileName()
    #self.view.window().show_quick_panel("", "emacsYank", idx, names)
    sublime.status_message("NOT YET IMPLEMENTED")
#
# Yank the most recent kill, or 
# if an argument is specified, 
# that numbered kill ring entry
#
class EmacsYankCommand(sublime_plugin.TextCommand):
 
  def run(self, edit, **args):
    global killRing
    
    if len(args) == 0:
      # no arguments means the command 
      # is being called directly
      valueToYank = sublime.getClipboard()
    elif args[0] == "clipboard":
      # the user has chosen to yank windows clipboard.
      valueToYank = sublime.getClipboard()
    else:
      # an argument means it's been called from 
      # the EmacsYankChoiceCommand
      idx = int(args[0])
      valueToYank = killRing.get(idx)
    
    for s in self.view.sel():
      self.view.erase(s)
      self.view.insert(s.begin(), valueToYank)
            
    # once we've yanked, we definitely don't want to
    # reuse the old kill buffer
    killRing.LastKillPosition = -1
    
#
# Set a mark in the current view
#
class EmacsSetMarkCommand(EmacsSelectionCommand):
  def run(self, edit, **args):
    global marks
    marks.setMark(self.view)
            
#
# Kill between the current cursor and the mark
#
class EmacsKillToMarkCommand(EmacsSelectionCommand):
  def run(self, edit, **args):
    global marks
    viewName = marks.viewIdentifier(self.view)

    # HACK: Since I have mapped this to ctrl-w, only kill if a mark 
    # is active, otherwise select word. This was done here since I 
    # don't think it's possible to create a custom context.
    # 
    # If you don't like this behavior, just remove the if statement
    # and keep the "marks.killMark(self.view)" line.
    if viewName in marks.innerMarks:
      marks.killMark(self.view)
    else:
      self.view.run_command("expand_selection", {"to": "word"})

#
# Kill between the current cursor and the mark
#
class EmacsKillRingSaveCommand(EmacsSelectionCommand):
  def run(self, edit, **args):
    global marks
    marks.copyMark(self.view)

#
# Remove any existing marks
#
class CancelMarkCommand(EmacsSelectionCommand):
  def run(self, edit, **args):
    global marks
    marks.clearMark(self.view)

#
# If a mark has been set, color the region between the mark and the point
#
class EmacsMarkDetector(sublime_plugin.EventListener):
  global marks
  def __init__(self, *args, **kwargs):
    sublime_plugin.EventListener.__init__(self, *args, **kwargs)
   
  def on_selection_modified(self, view):
    point = view.sel()[0].end()
    viewName = marks.viewIdentifier(view)
    if viewName in marks.innerMarks:
      mark = marks.innerMarks[viewName]
      view.add_regions('set-mark-region', [sublime.Region(mark, point)], 'string')


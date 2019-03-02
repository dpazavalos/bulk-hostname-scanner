# Threaded File Handler

Multi Thread file opener and destroyer. Best used with temp files to be opened but not kept

Spins a thread to send a pipe command through webbrowser.open (to allow os default handling), 
waits a few seconds, and begins trying to delete file. Thread closes once file is deleted or 
cannot be found    

##  Usage

```
>>> from threaded_file_handler import TFH
>>> file_handler = TFH()
>>> file_handler.handle('whatever.file')
# File is open. TFH waits a few seconds, and then'll delete it
```

 * handle(file_path) - 
File handler. Threads dedicated file handler to open and cleanup temp file, given a string path to
the file. Call and forget

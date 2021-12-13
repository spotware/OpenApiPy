# Console Sample

This is the console sample for Spotware OpenApiPy Python package.

It uses a single thread which is the Python main execution thread for both getting user inputs and sending/receiving messages to/from API.

Because it uses only the Python main execution thread the user input command has a time out, and if you don't enter your command on that specific time period it will block for few seconds and then it starts accepting user command again.

This sample uses [inputimeout](https://pypi.org/project/inputimeout/) Python package, you have to install it before running the sample. 

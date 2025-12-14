# Linux Tools

A collection of personal scripts to automate tasks and simplify life on Linux.

## About This Project

This repository contains a variety of scripts that I've created to help with my daily command-line tasks. They range from simple file operations to more complex system interactions.

## Available Scripts

This section will be updated as new scripts are added.

*   **cab.py**: A tool for recording system audio and saving it as an MP3 file. It can also remove silence from the beginning and end of the recording.

## Usage

To use a script, simply make it executable and run it from your terminal:

```bash
chmod +x ./script_name.py
./script_name.py [arguments]
```

### cab.py Example

To record audio and save it, you can use the following command:

```bash
./cab.py --file_name my_recording.mp3
```

To also remove silence from the recording, add the `--remove_silence` flag:

```bash
./cab.py --file_name my_recording.mp3 --remove_silence
```

For more detailed instructions, please refer to the comments within each script file.

## Contributing

While this is a personal project, suggestions and improvements are welcome. Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

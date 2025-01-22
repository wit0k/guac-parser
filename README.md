# guac-parser
This Proof of Concept (PoC) script enables the parsing of the Guacamole protocol, which includes a stream of recorded session replay. 
Consequently, it provides the capability to extract screenshots, triggered by progress indicators based on the percentage of completion, from the recording. 
Additionally, it includes functionality for replaying the recording within an integrated viewer.
![main_flow](https://github.com/user-attachments/assets/68a175e8-14bb-4c01-b85d-797a9723d00f)

### Usage
The main class supports following parameters:
<code>
    :param StreamURL:
        A URL pointing to a Guacamole (.guac) recording stream containing the session recording.
    :param ScreenCaptureProgressTriggers:
        A list of percentages representing the progress points of the current recording at which to take screen captures.
    :param debug_mode:
        Indicates whether debug mode is enabled.
    :param ReplayRecording:
        Opens a viewer window and plays the accelerated stream recording.
    :param ScreenCapturePrefix:
        A prefix for the dumped screenshot files.
    :param CreateScreenshots:
        Enables the dumping of screenshots.
</code>

A basic usage example:
<code>
recording_rebuild = GuacRecordingRebuilder(StreamURL='https://tria.ge/241210-scgfgstkgj/behavioral1/logs/vnc.guac')
recording_rebuild.start()
pprint.pprint(recording_rebuild.cache)
</code>

### Result

<code>{
    'screenshots': [
        {
            '1_screen.jpg': <PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E251E10>,
            'ScreenCapturePrefix': None,
            'session_url': 'https://tria.ge/241210-scgfgstkgj/'
        },
        {
            '1535_screen.jpg': <PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E6F0910>,
            'ScreenCapturePrefix': None,
            'session_url': 'https://tria.ge/241210-scgfgstkgj/'
        },
        {
            '1726_screen.jpg': <PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E6F0A10>,
            'ScreenCapturePrefix': None,
            'session_url': 'https://tria.ge/241210-scgfgstkgj/'
        }
    ]
}</code>

A potential use-case could be (it's just an exmaple):
- Parsing several GUAC urls, and representing them if form of a collage (example below):
![collage](https://github.com/user-attachments/assets/213b14ba-f4a0-4f7f-94a4-871f2b8882af)

Such could be obtained by instantiating a test/PoC class **ImageCollage** with the results of **recording_rebuild.cache**, like:

<code>**ImageCollage**(screenshots).**create_self_contained_image_collage_html**()</code>

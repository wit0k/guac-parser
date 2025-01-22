# guac-parser
Apache Guacamole (guac) session recording parser. A PoC script facilitating the parsing of guacamole protocol containing the stream of recorded session replay.

![main_flow](https://github.com/user-attachments/assets/68a175e8-14bb-4c01-b85d-797a9723d00f)

### Usage

<code>recording_rebuild = GuacRecordingRebuilder(StreamURL='https://tria.ge/241210-scgfgstkgj/behavioral1/logs/vnc.guac')
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
}
</code>

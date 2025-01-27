# guac-parser

The Proof of Concept (PoC) script enables the parsing of the Guacamole protocol, which includes a stream of recorded session replay. Consequently, providing the capability to extract screenshots, triggered by progress indicators based on the percentage of completion, from the recording progress. Additionally, it includes functionality for replaying the recording within an integrated viewer.

![main_flow](https://github.com/user-attachments/assets/68a175e8-14bb-4c01-b85d-797a9723d00f)

**Remark**: Python 3.13.1t (Free-threading) is recommended

### Key Features
- **Portable**: Extensible design allows for easy addition of new instruction types.
- **Instruction Parsing**: Decodes the Guacamole session recording (guac) instructions stream.
- **Screenshot Dumping**: Extracts screenshots from the session recording stream, capturing the visual behavior at specified progress points.
- **Recording Replay**: Enables the replay of the entire detonation session in a built-in viewer (BETA – currently supports single session only).

### To Do:
- **Offline Replay**: Add the capability to create MP4 videos from the recording stream for easier sharing, review, or auditing.
- **AI support**: A model to analyze and summarize activities from screen shots


### Usage
The main class supports following parameters:
<code>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;StreamURL:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;URL&nbsp;pointing&nbsp;to&nbsp;a&nbsp;Guacamole&nbsp;(.guac)&nbsp;recording&nbsp;stream&nbsp;containing&nbsp;the&nbsp;session&nbsp;recording.<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ScreenCaptureProgressTriggers:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;list&nbsp;of&nbsp;percentages&nbsp;representing&nbsp;the&nbsp;progress&nbsp;points&nbsp;of&nbsp;the&nbsp;current&nbsp;recording&nbsp;at&nbsp;which&nbsp;to&nbsp;take&nbsp;screen&nbsp;captures.<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;debug_mode:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Indicates&nbsp;whether&nbsp;debug&nbsp;mode&nbsp;is&nbsp;enabled.<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ReplayRecording:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opens&nbsp;a&nbsp;viewer&nbsp;window&nbsp;and&nbsp;plays&nbsp;the&nbsp;accelerated&nbsp;stream&nbsp;recording. [EXPERIMENTAL]<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ScreenCapturePrefix:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;prefix&nbsp;for&nbsp;the&nbsp;dumped&nbsp;screenshot&nbsp;files.<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;CreateScreenshots:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables&nbsp;the&nbsp;dumping&nbsp;of&nbsp;screenshots.<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;SessionObj:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;HTTP&nbsp;Requests&nbsp;session&nbsp;object&nbsp;to&nbsp;use&nbsp;(possibly&nbsp;with&nbsp;initialized&nbsp;headers,&nbsp;cookies&nbsp;etc.)<br>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;SessionObj:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;logger&nbsp;object<br>
</code>

A basic usage example:
<code>
recording_rebuild = GuacRecordingRebuilder(StreamURL='https://tria.ge/241210-scgfgstkgj/behavioral1/logs/vnc.guac')
recording_rebuild.start()
pprint.pprint(recording_rebuild.cache)
</code>

### Result

<code>
&nbsp;&nbsp;&nbsp;&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'screenshots': [
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'1_screen.jpg': &lt;PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E251E10&gt;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ScreenCapturePrefix': None,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'session_url': 'https://tria.ge/241210-scgfgstkgj/'
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'1535_screen.jpg': &lt;PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E6F0910&gt;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ScreenCapturePrefix': None,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'session_url': 'https://tria.ge/241210-scgfgstkgj/'
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'1726_screen.jpg': &lt;PIL.Image.Image image mode=RGB size=1280x720 at 0x2058E6F0A10&gt;,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ScreenCapturePrefix': None,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'session_url': 'https://tria.ge/241210-scgfgstkgj/'
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]
&nbsp;&nbsp;&nbsp;&nbsp;}
</code>

### Example Use-cases

- Storing Casual Screenshots Over Long Session Recording for Audit Purposes
- Processing Screenshots with AI to Detect and Alert Specific Behavior
- Visual representation of URL analysis through an image collage:
![collage](https://github.com/user-attachments/assets/213b14ba-f4a0-4f7f-94a4-871f2b8882af)

  Could be obtained by instantiating a test class **ImageCollage** with the results of **screenshots = recording_rebuild.cache['screenshots']**, like:
  <code>**ImageCollage**(screenshots).**create_self_contained_image_collage_html**()</code>

- ... [ Let me know if you have any other ideas ]
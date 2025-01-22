# guac-parser
This Proof of Concept (PoC) script enables the parsing of the Guacamole protocol, which includes a stream of recorded session replay. 
Consequently, it provides the capability to extract screenshots, triggered by progress indicators based on the percentage of completion, from the recording. 
Additionally, it includes functionality for replaying the recording within an integrated viewer.
![main_flow](https://github.com/user-attachments/assets/68a175e8-14bb-4c01-b85d-797a9723d00f)

### Usage
The main class supports following parameters:
<code>
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;StreamURL:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;URL&nbsp;pointing&nbsp;to&nbsp;a&nbsp;Guacamole&nbsp;(.guac)&nbsp;recording&nbsp;stream&nbsp;containing&nbsp;the&nbsp;session&nbsp;recording.
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ScreenCaptureProgressTriggers:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;list&nbsp;of&nbsp;percentages&nbsp;representing&nbsp;the&nbsp;progress&nbsp;points&nbsp;of&nbsp;the&nbsp;current&nbsp;recording&nbsp;at&nbsp;which&nbsp;to&nbsp;take&nbsp;screen&nbsp;captures.
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;debug_mode:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Indicates&nbsp;whether&nbsp;debug&nbsp;mode&nbsp;is&nbsp;enabled.
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ReplayRecording:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opens&nbsp;a&nbsp;viewer&nbsp;window&nbsp;and&nbsp;plays&nbsp;the&nbsp;accelerated&nbsp;stream&nbsp;recording.
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;ScreenCapturePrefix:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;prefix&nbsp;for&nbsp;the&nbsp;dumped&nbsp;screenshot&nbsp;files.
&nbsp;&nbsp;&nbsp;&nbsp;:param&nbsp;CreateScreenshots:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables&nbsp;the&nbsp;dumping&nbsp;of&nbsp;screenshots.
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


A potential use-case could be (it's just an exmaple):
- Parsing several GUAC urls, and representing them if form of a collage (example below):
![collage](https://github.com/user-attachments/assets/213b14ba-f4a0-4f7f-94a4-871f2b8882af)

Such could be obtained by instantiating a test/PoC class **ImageCollage** with the results of **recording_rebuild.cache**, like:

<code>**ImageCollage**(screenshots).**create_self_contained_image_collage_html**()</code>

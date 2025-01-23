########################################################################################################################
# Requirements for Free-threading.
# CPython has experimental support for a build of Python called free threading where the global interpreter lock (GIL) is disabled.
# Free-threaded execution allows for full utilization of the available processing power by running threads in parallel on available CPU cores
# Python >= 3.13.1
# pip >= 24.3.1
########################################################################################################################
import base64
import logging
import time
import hashlib
from enum import verify

# import urllib.request
import requests
import tkinter as tk
import numpy as np  # Causes issues on 3.13.1
import threading
# import imageio.v2 as iio
from datetime import datetime, UTC
# from encodings.johab import codec
from queue import Queue, Empty
from io import BytesIO
from PIL import ImageFile, Image, ImageTk
from math import floor
from typing import Callable, List, Any, Dict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)
ImageFile.LOAD_TRUNCATED_IMAGES = True

from collections import OrderedDict

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(funcName)s - %(message)s',
                    handlers=[logging.StreamHandler()])

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3',
}

""" Helper Functions """
def to_int(_bytes) -> int:
    # return int.from_bytes(_bytes, byteorder='little')
    return int(_bytes.decode())

def to_str(_bytes) -> str:
    if _bytes is None:
        return 'None'
    elif isinstance(_bytes, bytes):
        return _bytes.decode()
    else:
        return str(_bytes)

def to_datetime_utc(_in: int):
    return datetime.fromtimestamp(_in / 1000, UTC)

def to_seconds(_in: int):
    return _in // 1000

def round_number(_in):
    return round(_in)

def ulist(_list, keep_the_last_duplicate=True):
    nlist = []
    _i = -1
    for _e in _list:
        _i += 1
        if _e.id not in [_ne.id for _ne in nlist]:
            nlist.append(_e)

        else:  # _e.id in [_id for _id in nlist]:
            for e_to_rm in nlist:
                if e_to_rm.id == _e.id:
                    nlist.remove(e_to_rm)
            nlist.append(_e)

    return nlist

""" Configuration / Handlers """
Instruction_Handlers = OrderedDict()
Instruction_Handlers.update({
        'i': {},
        'size': {
            'arguments': {'layer_index': [to_int], 'width': [to_int], 'height': [to_int]}},
        'end': {
            'arguments': {'stream_index': [to_int]}},
        'sync': {
            'arguments': {'timestamp': [to_int, to_seconds]}},
        'img': {
            'arguments': {
                'stream_index': [to_int],
                'channelMask': [to_int],
                'layer': [to_int],
                'mimetype': [to_str],
                'x': [to_int],
                'y': [to_int],
            }
        },
        'blob': {
            'arguments': {
                'stream_index': [to_int],
                'data': None,
            },
        },
        'custom': {
            'arguments': {
                'data': None,
            },
        },
    })

""" GUAC Classes """
class default_layer(object):
    DEFAULT_LAYER_WIDTH = 640
    DEFAULT_LAYER_HEIGHT = 480

class guac_instruction(object):
    id = None
    opcode_len = None
    opcode = b''
    data = b''

    def __init__(self):
        pass

    def get_data(self, size=None):
        if self.opcode == b'blob':
            if size:
                return base64.b64decode(self.data.decode())[:size]
            else:
                return base64.b64decode(self.data.decode())
        else:
            return self.data

    def __repr__(self):
        row = {'id': self.id, 'opcode': self.opcode.decode()}
        for name, handlers in Instruction_Handlers[self.opcode.decode()].get('arguments', {}).items():
            row.update({name: getattr(self, name)})

        return str(row)

    def __str__(self):
        return self.__repr__()

class guac_recording_frame(object):
    buffer = None
    x = 0
    y = 0
    width = 0
    height = 0
    layer_index = 0
    mimetype = None
    timestamp = None
    elements = None

    def __init__(self, buffer=None, layer: default_layer = None):

        if layer is None: layer = default_layer()
        if buffer is None: buffer = b''
        if self.elements is None: self.elements = []
        self.logger = logging
        self.buffer = buffer
        self.default_layer = layer

    def add_blob(self, _bytes: bytes):
        self.buffer += _bytes

    def get_buffer(self, raw=False, size=None):

        try:
            if raw == True:
                return self.buffer if size is None else self.buffer[:size]
            else:
                return base64.b64decode(self.buffer.decode()) if size is None else base64.b64decode(
                    self.buffer.decode())[:size]
        except Exception as msg:
            self.logger.error(' [-] Unable to get the buffer. Exception: %s' % str(msg))
            return None

    def save(self, name_prefix):
        try:
            with Image.open(BytesIO(self.get_buffer())) as img:
                image_name = '%s_blob.jpg' % name_prefix
                img.save('screenshots/%s' % image_name)
        except Exception as msg:
            self.logger.error(' [-] Unable to save the image. Exception: %s' % str(msg))
            with open('screenshots/%s_last_frame.png.err' % name_prefix, 'wb') as err_file:
                err_file.write(self.get_buffer())

    def is_complete(self):
        if b'end' in self.elements:
            return True
        else:
            return False

    def is_synced(self):
        if b'sync' in self.elements:
            return True
        else:
            return False

    def size(self):
        return len(self.get_buffer(raw=True))

    def img(self):
        return Image.open(BytesIO(self.get_buffer()))

    def np(self):
        return np.array(self.img())

    def __repr__(self):
        row = {}
        row.update({
            'opcodes': list(map(bytes.decode, self.elements)),
            'x': getattr(self, 'x'),
            'y': getattr(self, 'y'),
            'width': getattr(self, 'width'),
            'height': getattr(self, 'height'),
            'layer_index': getattr(self, 'layer_index'),
            'mimetype': getattr(self, 'mimetype'),
            'timestamp': getattr(self, 'timestamp'),
        })

        return str(row)

    def build(self, inst_obj: guac_instruction):

        if inst_obj.opcode in [b'i', b'end', b'img', b'blob', b'size', b'custom', b'sync']:
            if inst_obj.opcode in self.elements and inst_obj.opcode not in [b'blob', b'custom', b'sync']:
                self.logger.error(
                    'Exception: The instruction opcode %s is already part of the frame...' % inst_obj.opcode.decode())
                raise Exception(
                    'Exception: The instruction opcode %s is already part of the frame...' % inst_obj.opcode.decode())
            else:
                self.elements.append(inst_obj.opcode)
        else:
            self.logger.error('Unsupported instruction: %s' % inst_obj.opcode.decode())
            raise Exception('Unsupported instruction: %s' % inst_obj.opcode.decode())

        if inst_obj.opcode in [b'blob']:
            self.add_blob(_bytes=inst_obj.data)

        if inst_obj.opcode in [b'sync']:
            self.timestamp = getattr(inst_obj, 'timestamp')

        if inst_obj.opcode in [b'img']:
            try:
                self.layer_index = getattr(inst_obj, 'layer')
                self.mimetype = getattr(inst_obj, 'mimetype')
                self.x = getattr(inst_obj, 'x')
                self.y = getattr(inst_obj, 'y')
            except Exception as msg:
                pass

        if inst_obj.opcode in [b'size']:
            self.layer_index = getattr(inst_obj, 'layer_index')
            self.width = getattr(inst_obj, 'width')
            self.height = getattr(inst_obj, 'height')
            self.default_layer.DEFAULT_LAYER_WIDTH = self.width
            self.default_layer.DEFAULT_LAYER_HEIGHT = self.height
            pass

        if inst_obj.opcode in [b'end']:
            if self.width == 0 or self.height == 0:
                self.width = self.default_layer.DEFAULT_LAYER_WIDTH
                self.height = self.default_layer.DEFAULT_LAYER_HEIGHT

class ScreenCaptureTrigger(object):
    on_percent_of_progress = None
    duration = None
    elapsed_seconds = None
    time_s = None

    def __init__(self, on_percent_of_progress, total_duration, elapsed_seconds, time_s):
        self.on_percent_of_progress = on_percent_of_progress
        self.duration = total_duration
        self.elapsed_seconds = elapsed_seconds
        self.time_s = time_s

        md5_hash = hashlib.md5()
        md5_hash.update(str('%s, %s, %s, %s' % (
        self.on_percent_of_progress, self.elapsed_seconds, self.duration, self.time_s)).encode('utf-8'))
        self.id = md5_hash.hexdigest()

    def __repr__(self):
        return '%s, %s, %s, %s' % (
        self.on_percent_of_progress, self.elapsed_seconds, self.duration, self.time_s)

class GuacRecordingRebuilder:

    cache = None

    def __init__(self, StreamURL: str, CreateScreenshots=True, ScreenCaptureProgressTriggers=[4, 50, 99],
                 ScreenCapturePrefix=None, ReplayRecording=False, debug_mode: bool = False,
                 SessionObj=None):
        """
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
        """
        self.debug_mode = debug_mode
        if self.debug_mode == True:
            logging.basicConfig(level=logging.INFO)

        if self.cache is None: self.cache = {
            'screenshots': []
        }

        self.logger = logging
        self.url = StreamURL
        self.queue = Queue()
        self.elements = [] if debug_mode else None
        self._stop_processing_event = threading.Event()
        self._stop_rebuild_event = threading.Event()
        self.lock = threading.Lock()
        self.rebuilt_objects = []
        self._is_running = False
        self.ScreenCaptureProgressTriggers = ScreenCaptureProgressTriggers
        self.ReplayRecording = ReplayRecording
        self.CreateScreenshots = CreateScreenshots
        self.ScreenCapturePrefix = ScreenCapturePrefix

        if SessionObj is None:
            self.SessionObj = requests.Session()
        else:
            self.SessionObj = SessionObj

    def parse_stream_chunk(self, chunk: bytes):
        """ Parses guac instructions from bytes/chunks taken from the network stream

        # Reference: https://guacamole.apache.org/doc/gug/guacamole-protocol.html
         - The Guacamole protocol consists of instructions. Each instruction is a comma-delimited list followed by a terminating
         semicolon, where the first element of the list is the instruction opcode, and all following elements are the arguments
         for that instruction.

         OPCODE,ARG1,ARG2,ARG3,...;

         - Each element of the list has a positive decimal integer length prefix separated by the value of the element by a period.
         This length denotes the number of Unicode characters in the value of the element, which is encoded in UTF-8

         LENGTH.VALUE

        Example:

        4.size,1.0,4.1024,3.768; -> LENGTH.<OPCODE>,LENGTH.<VALUE_OF_LAYER_INDEX>,LENGTH.<VALUE_OF_WIDTH>,LENGTH.<VALUE_OF_HEIGHT>;
        """
        instructions = []

        try:
            # Pull all instructions (as they are separated by semicolon)
            raw_instructions = chunk.split(b';')

            incomplete_inst_index = None
            inst_index = -1

            # Determine incomplete instruction (if any)
            # - Proper instruction ends on semicolon, hence if last instruction is complete,
            #   the raw_instructions should end on '', else the last instruction is incomplete
            if b'' != raw_instructions[-1]:
                incomplete_inst_index = len(raw_instructions) - 1
            else:
                if len(raw_instructions) == 1 and b';' not in chunk:
                    incomplete_inst_index = 0
                else:
                    # Remove last empty string (indicating completeness of the last instruction)
                    raw_instructions = raw_instructions[:-1]

            # Parse complete instructions
            for inst_bytes in raw_instructions:
                inst_index += 1

                # Handle incomplete instruction
                if incomplete_inst_index is not None:
                    if inst_index == incomplete_inst_index:
                        return instructions, inst_bytes

                # Create empty instruction object
                inst_obj = guac_instruction()

                # Get instruction arguments
                args = inst_bytes.split(b',')
                # WORKAROUND: The custom's data may contain multiple comma characters, hence breaking the parsing, we need to fix it
                if b'custom' in inst_bytes:
                    # The first argument (at index 0) is the opcode len and opcode name, the rest is JSON data
                    args = [args[0], b','.join(args[1:])]

                i = -1
                opcode_parsed = None
                # Iterate over all arguments for given instruction buffer (the first arg indicates the opcode)
                for arg in args:
                    arg_params = arg.split(b'.')
                    if opcode_parsed is None:  # Get the opcode
                        inst_obj.opcode = arg_params[1]
                        inst_obj.opcode_len = to_int(arg_params[0])
                        opcode_parsed = True
                        continue

                    i += 1

                    # Pull instruction details according to given instruction names and pass them via handlers (if any)
                    if inst_obj.opcode.decode() in Instruction_Handlers.keys():
                        try:
                            opcode_arguments = list(
                                Instruction_Handlers[inst_obj.opcode.decode()].get('arguments', {}).keys())
                            arg_name = opcode_arguments[i] if len(opcode_arguments) >= i else None
                        except Exception:
                            raise Exception(
                                "Exception: Unsupported Instruction: %s. Review instruction's handlers, the mapping at index: %s is missing..." % (
                                inst_obj.opcode.decode(), i))

                        handlers = Instruction_Handlers[inst_obj.opcode.decode()].get('arguments', {}).get(arg_name,
                                                                                                           None)
                        value = arg_params[1]

                        if handlers is not None:
                            for handler in handlers:
                                value = handler(value)
                                pass

                        # Dynamically update instruction object attributes
                        setattr(inst_obj, arg_name, value)

                instructions.append(inst_obj)

            # Return complete instructions, no need to lookup the stream anymore
            return instructions, b''

        except Exception as msg:
            self.logger.error('Exception: %s' % msg)
            return instructions, b''

    def parse_stream_instructions(self, url: str = None, dump_raw_stream: bool = False):

        inst_count = 0

        if url is None: url = self.url
        self.logger.info('[+] Process instructions from stream: %s' % url)
        last_inst_id = None
        raw_stream_fobj = None

        if dump_raw_stream:
            raw_stream_fobj = open(r'raw_stream.bin', 'wb')

        # req = urllib.request.Request(url)
        # req.add_header('Authorization', headers['Authorization'])
        # req.add_header('User-agent', headers['User-agent'])
        # with urllib.request.urlopen(req, timeout=120) as response:
        with self.SessionObj.get(url, stream=True, verify=False, timeout=120) as response:
            response.raise_for_status()
            if response.status_code == 200:
                chunk_size = 4096
                unprocessed_chunk = b''
                inst_count = -1
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        if dump_raw_stream:
                            raw_stream_fobj.write(chunk)
                            continue
                        try:
                            instructions, unprocessed_chunk = self.parse_stream_chunk(
                                chunk=chunk if unprocessed_chunk == b'' else unprocessed_chunk + chunk)

                            for inst in instructions:
                                inst_count += 1
                                inst.id = inst_count
                                self.enqueue_instruction(inst)

                        except Exception as msg:
                            print('Failed to extend instructions queue: Error: ', str(msg))
                    else:
                        self.logger.info('The chunk is empty, exiting stream...')
                        break
            else:
                print(f"Failed to retrieve stream: {response.status_code}")

        if raw_stream_fobj is not None:
            raw_stream_fobj.close()

        self.logger.info(' [-] Event (_stop_processing_event) -> No more instructions in the stream...')
        self.logger.info(' [-] %s instructions enqueued...' % inst_count)
        self._stop_processing_event.set()

    def enqueue_instruction(self, inst: guac_instruction):
        if inst is None:
            raise ValueError("Cannot insert None element")

        try:
            with self.lock:
                # self.logger.debug(' [-] Adding instruction -> inst.id: %s' % inst.id)
                self.queue.put(inst)
                if self.debug_mode:
                    self.elements.append(inst)
        except Exception as e:
            if self.debug_mode:
                print(f"Error inserting element: {e}")
            raise

    def rebuild_instructions(self, create_screenshots=True, trigger_screenshot_on_progress=None, replay_recording=None):
        """
        # Reference: https://guacamole.apache.org/doc/gug/guacamole-protocol.html
        # Documentation:
        - All drawing operations in the Guacamole protocol affect a layer, and each layer has an integer index which identifies it.
        When this integer is negative, the layer is not visible, and can be used for storage or caching of image data.
        In this case, the layer is referred to within the code and within documentation as a “buffer”. Layers are created
        automatically when they are first referenced in an instruction

        - There is one main layer which is always present called the “default layer”. This layer has an index of 0.
        - Resizing this layer resizes the entire remote display. Other layers default to the size of the default layer upon creation,
        while buffers are always created with a size of 0x0, automatically resizing themselves to fit their contents.

        - Non-buffer layers can be moved and nested within each other. In this way, layers provide a simple means of hardware-accelerated
        compositing. If you need a window to appear above others, or you have some object which will be moving or
        you need the data beneath it automatically preserved, a layer is a good way of accomplishing this.
        If a layer is nested within another layer, its position is relative to that of its parent. When the parent is moved or
        reordered, the child moves with it. If the child extends beyond the parents bounds, it will be clipped.

        /**
         * A single frame of Guacamole session data. Each frame is made up of the set
         * of instructions used to generate that frame, and the timestamp as dictated
         * by the "sync" instruction terminating the frame. Optionally, a frame may
         * also be associated with a snapshot of Guacamole client state, such that the
         * frame can be rendered without replaying all previous frames.
         *
         * @private
         * @constructor
         * @param {!number} timestamp
         *     The timestamp of this frame, as dictated by the "sync" instruction which
         *     terminates the frame.
         *
         * @param {!number} start
         *     The byte offset within the blob of the first character of the first
         *     instruction of this frame.
         *
         * @param {!number} end
         *     The byte offset within the blob of character which follows the last
         *     character of the last instruction of this frame.
         */
        Guacamole.SessionRecording._Frame = function _Frame(timestamp, start, end) {
            /**
             * Whether this frame should be used as a keyframe if possible. This value
             * is purely advisory. The stored clientState must eventually be manually
             * set for the frame to be used as a keyframe. By default, frames are not
             * keyframes.
             *
             * @type {!boolean}
             * @default false
             */
             this.keyframe = false;

             -----------------------
             IF first frame -> keyframe = false
             timestamp -> int(sync.timestamp)
        """
        default_layer_obj = default_layer()
        frames = []

        if trigger_screenshot_on_progress is None: trigger_screenshot_on_progress = self.ScreenCaptureProgressTriggers
        if replay_recording is None: replay_recording = self.ReplayRecording
        if create_screenshots is None: create_screenshots = self.CreateScreenshots

        self._is_running = True
        self.logger.info('[+] Start rebuilding instructions...')
        g_frame = None

        # Stops when GuacStreamProcessingThread is complete (no more instructions in the stream), and queue is empty and the rebuilding stop event has been set
        while self._is_running:
            try:
                inst_obj = self.queue.get(block=False)

                if self.debug_mode:
                    self.logger.error(inst_obj)

                if g_frame is None: g_frame = guac_recording_frame(layer=default_layer_obj)

                if g_frame.is_complete():
                    if inst_obj.opcode not in g_frame.elements:
                        g_frame.build(inst_obj=inst_obj)
                    else:
                        self.logger.debug(g_frame)
                        frames.append(g_frame)

                        # Start fresh
                        g_frame = guac_recording_frame(layer=default_layer_obj)
                        g_frame.build(inst_obj=inst_obj)
                else:
                    g_frame.build(inst_obj=inst_obj)

                self.queue.task_done()

            except Empty:
                # When GuacStreamProcessingThread is complete (no more instructions in the stream), and the queue was processed / is empty
                # - Assume the operation is complete, and the _stop_rebuild_event can be set, so the loop can exit
                if self._stop_processing_event.is_set():
                    self.logger.warning('Event (_stop_rebuild_event) -> No more instructions to process...')
                    self._stop_rebuild_event.set()
                    self._is_running = False
                else:
                    # logger.debug(' [-] Waiting for new instructions to process...')
                    pass

            except Exception as e:
                self.logger.error(f"Exception: Unexpected error in rebuild thread: {e}")
                if len(self.queue.queue) == 0:
                    self._is_running = False

        def create_screenshot_trigger(total_duration, elapsed_seconds, time_s):
            if elapsed_seconds == 0:
                return ScreenCaptureTrigger(0, elapsed_seconds, total_duration, time_s)

            return ScreenCaptureTrigger(floor((elapsed_seconds / total_duration) * 100), elapsed_seconds,
                                        total_duration, time_s)

        self.logger.info(' [-] Start processing frames...')
        canvas, root, start_time, end_time, duration, screen_capture_triggers = None, None, None, None, None, None

        # Create a canvas to display images
        root = tk.Tk()  # Create the main window
        root.title("GUAC Stream Player")
        canvas = tk.Canvas(root, width=default_layer_obj.DEFAULT_LAYER_WIDTH,
                               height=default_layer_obj.DEFAULT_LAYER_HEIGHT)
        canvas.pack()
        canvas.delete("all")
        root.state("zoomed")  # Maximize the window

        # Get timestamps from all frames that have it
        frames_timestamps = [f.timestamp for f in frames if f.timestamp is not None]

        # Create a list of screen capture triggers corresponding to percentage of progress indicated in trigger_screenshot_on_progress
        if len(frames_timestamps) > 2:
            start_time = frames_timestamps[0]  # First frame
            end_time = frames_timestamps[-1]  # Last frame
            duration = end_time - start_time  # Duration (in seconds)

            self.logger.info(' [-] The recording duration: %s seconds' % duration)
            if isinstance(trigger_screenshot_on_progress, list):
                self.logger.info(' [-] Processing on-progress triggers...')
                if len(trigger_screenshot_on_progress) > 0:
                    screen_capture_triggers = []
                    # triggers = []
                    for ft in frames_timestamps:
                        screen_capture_triggers.append(
                            create_screenshot_trigger(duration, duration - (end_time - ft), ft))

                    # Not effective, must be a better way, but i am tired
                    new = []
                    screen_capture_triggers = ulist(screen_capture_triggers)
                    processed_triggers = []
                    end_processing_triggers = False
                    for _progress_percentage in trigger_screenshot_on_progress:
                        if end_processing_triggers: break
                        for _cur_progress in screen_capture_triggers:
                            if _progress_percentage not in processed_triggers:
                                if _cur_progress.on_percent_of_progress >= _progress_percentage:
                                    new.append(_cur_progress)
                                    processed_triggers.append(_progress_percentage)
                                    if len(processed_triggers) == len(trigger_screenshot_on_progress):
                                        end_processing_triggers = True
                                        break

                    # Keep only those triggers that are as close as possible to user indicated trigger on progress percentage
                    screen_capture_triggers = new

        name_prefix = -1
        base_image = None
        create_new_base = True
        stop_capturing_screenshots = False
        for frame in frames:
            name_prefix += 1
            if create_new_base:
                base_image = Image.new('RGBA', (frame.width, frame.height))
                canvas.config(width=frame.width, height=frame.height)
                create_new_base = False

            # Resize the base image (if necessary)
            base_image_width, base_image_height = base_image.size
            if frame.width != base_image_width or frame.height != base_image_height:
                base_image = base_image.resize((frame.width, frame.height))
                canvas.config(width=frame.width, height=frame.height)

            # Insert frame/image into x, y position
            base_image.paste(frame.img(), (frame.x, frame.y))

            # Recording replay |& screenshot creation
            if frame.is_synced() and frame.is_complete():
                if replay_recording:
                    photo = ImageTk.PhotoImage(base_image)
                    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                    canvas.image = photo  # Keep a reference to prevent garbage collection
                    canvas.update()

                if create_screenshots:
                    dump_screenshot = False
                    if not stop_capturing_screenshots:
                        if screen_capture_triggers is not None:
                            if len(screen_capture_triggers) > 0:
                                for _trigger in screen_capture_triggers:
                                    if frame.timestamp >= _trigger.time_s:
                                        dump_screenshot = True
                                        try:
                                            # Remove a trigger from the list, since it was satisfied
                                            screen_capture_triggers = screen_capture_triggers[1:]
                                        except Exception:
                                            # Just in case set it to empty list on error
                                            screen_capture_triggers = []

                                        if len(screen_capture_triggers) == 0: stop_capturing_screenshots = True
                                        break
                        else:
                            dump_screenshot = True

                        if dump_screenshot:
                            try:
                                if self.ScreenCapturePrefix:
                                    image_name = '%s_%s_screen.jpg' % (self.ScreenCapturePrefix, name_prefix)
                                else:
                                    image_name = '%s_screen.jpg' % name_prefix

                                base_image = base_image.convert("RGB")
                                base_image.save('screenshots/%s' % image_name)
                                self.cache.get('screenshots', []).append({image_name: base_image, 'ScreenCapturePrefix': self.ScreenCapturePrefix, 'session_url': self.url.replace('behavioral1/logs/vnc.guac', '')})

                            except Exception as msg:
                                self.logger.error(' [-] Unable to save the image. Exception: %s' % str(msg))

                create_new_base = False
                # time.sleep(0.01)

        # End
        self.stop()

    def start(self):
        if self._is_running:
            raise RuntimeError("Rebuilding thread is already running")
        self._stop_rebuild_event.clear()
        self._stop_processing_event.clear()

        self.rebuild_thread = threading.Thread(
            target=self.rebuild_instructions,
            name="GuacRecordingRebuilderThread"
        )

        self.stream_processing_thread = threading.Thread(
            target=self.parse_stream_instructions,
            name="GuacStreamProcessingThread"
        )

        self.stream_processing_thread.daemon = False
        self.rebuild_thread.daemon = False

        self.rebuild_thread.start()
        self.stream_processing_thread.start()

        # Make sure it exits after the rebuilt only
        self.rebuild_thread.join()

        return self.cache

    def stop(self):

        self.logger.info('[+] GuacRecordingRebuilder -> Stop initiated...')
        self.logger.info(' [-] _stop_rebuild_event -> %s' % self._stop_rebuild_event.is_set())
        self.logger.info(' [-] _stop_processing_event -> %s' % self._stop_processing_event.is_set())

        if not self._is_running:
            return
        else:
            print(' [-] GuacRecordingRebuilder is still running...')
            print(' [-] Something is wrong?')
            return

""" Helper Classes """
class ImageCollage(object):
    def __init__(self, images):
        self.images = images

    def create_self_contained_image_collage_html(self, images=None, output_file: str = "collage.html", thumbnails_size: tuple = (200, 200)) -> str:
        """
        Creates a self-contained HTML file with an image collage from a list of PIL images.
        """

        if images is None: images = self.images

        def create_sharp_thumbnail(img: Image.Image, size: tuple) -> Image.Image:
            """
            Creates a sharp thumbnail while maintaining aspect ratio
            """
            # Convert to RGB if image is in RGBA mode
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Calculate aspect ratio
            aspect = img.width / img.height

            if aspect > 1:
                # Width is greater than height
                new_width = size[0]
                new_height = int(size[0] / aspect)
            else:
                # Height is greater than width
                new_height = size[1]
                new_width = int(size[1] * aspect)

            # Resize with high-quality settings
            return img.resize((new_width, new_height),
                              resample=Image.Resampling.LANCZOS,
                              reducing_gap=3.0)

        css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f0f0f0;
            }
            .collage {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                gap: 20px;
                padding: 20px;
            }
            .image-card {
                position: relative;
                background: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .image-card:nth-child(3n+1) { background: #f0f7ff; }
            .image-card:nth-child(3n+2) { background: #f0fff7; }
            .image-card:nth-child(3n+3) { background: #fff7f0; }
            .image-card:hover {
                transform: scale(1.02);
            }
            .thumbnail-container {
                width: 100%;
                height: auto;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #fafafa;
                border-radius: 4px;
                overflow: hidden;
            }
            .thumbnail {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                cursor: pointer;
                image-rendering: -webkit-optimize-contrast;  /* For webkit browsers */
                image-rendering: crisp-edges;               /* For Firefox */
            }
            .buttons {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }
            .btn {
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                background: #007bff;
                color: white;
                cursor: pointer;
                text-decoration: none;
                font-size: 12px;
                flex: 1;
                text-align: center;
            }
            .btn:hover {
                background: #0056b3;
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.9);
                z-index: 1000;
            }
            .modal-content {
                max-width: 90%;
                max-height: 90%;
                margin: auto;
                display: block;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
            }
            .close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }
            .image-info {
                margin-top: 8px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
        </style>
        """

        javascript = """
        <script>
            function showModal(imgData) {
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                modal.style.display = "block";
                modalImg.src = imgData;
            }
    
            function closeModal() {
                document.getElementById('imageModal').style.display = "none";
            }
            function OpenPage(url) {
                window.open(url, '_blank');;
            }
            
            
            
            function downloadImage(imgData, index, name_prefix) {
                const link = document.createElement('a');
                link.href = imgData;
                // link.download = `image_${index}.png`;
                link.download = `image_${name_prefix}_${index}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
    
            window.onclick = function(event) {
                const modal = document.getElementById('imageModal');
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        </script>
        """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Image Collage (by wit0k)</title>
            {css}
        </head>
        <body>
            <div class="collage">
        """

        idx = 0
        for img_dict in images:
            idx += 1
            # idx = list(img_dict.keys())[0]
            img = list(img_dict.values())[0]
            ScreenCapturePrefix = list(img_dict.values())[1]
            session_url = list(img_dict.values())[2]

            # Create sharp thumbnail
            thumb = create_sharp_thumbnail(img, thumbnails_size)

            # Get image dimensions
            original_size = f"{img.width}x{img.height}"
            thumb_size = f"{thumb.width}x{thumb.height}"

            # Convert both original and thumbnail to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG", quality=100)
            img_str = base64.b64encode(buffered.getvalue()).decode()

            thumb_buffered = BytesIO()
            thumb.save(thumb_buffered, format="PNG", quality=100)
            thumb_str = base64.b64encode(thumb_buffered.getvalue()).decode()

            html_content += f"""
                <div class="image-card">
                    <div class="thumbnail-container">
                        <img src="data:image/png;base64,{thumb_str}" 
                             class="thumbnail"
                             onclick="showModal('data:image/png;base64,{img_str}')"
                             alt="Image {idx}">
                    </div>
                    <div class="buttons">
                        <button class="btn" onclick="OpenPage('{session_url}')">
                            Session
                        </button>
                        <button class="btn" onclick="downloadImage('data:image/png;base64,{img_str}', {idx}, '{ScreenCapturePrefix}')">
                            Download
                        </button>
                    </div>
                </div>
            """

        html_content += f"""
            </div>
    
            <!-- Modal -->
            <div id="imageModal" class="modal">
                <span class="close" onclick="closeModal()">&times;</span>
                <img id="modalImage" class="modal-content">
            </div>
    
            {javascript}
        </body>
        </html>
        """

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

@dataclass
class ThreadResult:
    """Data class to store thread execution results"""
    result: Any
    error: Exception = None
    start_time: datetime = None
    end_time: datetime = None

    @property
    def duration(self) -> float:
        """Calculate execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

class ThreadManager:
    """Manages thread execution and result collection with named parameters"""

    def __init__(self, max_threads: int = 10):
        self.max_threads = max_threads
        self.results: List[ThreadResult] = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        )

    def _execute_and_store(self, func: Callable) -> None:
        """Execute function with named parameters and store its result thread-safely"""
        thread_result = ThreadResult(
            result=None
        )
        thread_result.start_time = datetime.fromtimestamp(datetime.now().timestamp(), UTC)

        try:
            thread_result.result = func()
        except Exception as e:
            thread_result.error = e

        finally:
            thread_result.end_time = datetime.fromtimestamp(datetime.now().timestamp(), UTC)
            with self._lock:
                self.results.append(thread_result)

    def execute_batch(self, tasks: List[Callable]) -> List[ThreadResult]:
        """
        Execute function with different named parameter sets using thread pool
        """
        self.results.clear()

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all tasks
            futures = [
                executor.submit(self._execute_and_store, task.start)
                for task in tasks
            ]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        # Sort results by start time
        self.results.sort(key=lambda x: x.start_time)
        return self.results

    def get_successful_results(self) -> List[ThreadResult]:
        """Get only successful executions"""
        return [r for r in self.results if r.error is None]

    def get_failed_results(self) -> List[ThreadResult]:
        """Get only failed executions"""
        return [r for r in self.results if r.error is not None]

if __name__ == "__main__":

    screenshots = []
    max_threads = 7

    # Blindly chosen examples
    overview_hatching_urls = [
        'https://tria.ge/250120-xvfn5atqbq',
        'https://tria.ge/250120-xt2j7strf1',
        'https://tria.ge/250120-xtwc7atrfx',
        'https://tria.ge/250120-xtbnsatpfq',
        'https://tria.ge/241210-scgfgstkgj',
        'https://tria.ge/250119-nxw98awjey',
        'https://tria.ge/250119-nxfx8swjds',
        'https://tria.ge/250119-nn5j8swlfm',
        'https://tria.ge/250119-nmyqaswlbm',
        'https://tria.ge/250119-nl92yavnhy',
        'https://tria.ge/250119-nl39dsvnht',
        'https://tria.ge/250119-nlqnasvngw',
        'https://tria.ge/250119-njhjxawkdk'
    ]

    logging.info('[+] Initiating multi-threaded processing (max_threads: %s)...' % max_threads)
    logging.info(' [-] Populating tasks to execute...')

    guac_uri = 'behavioral1/logs/vnc.guac'
    tasks = []
    for overview_url in overview_hatching_urls:
        api_base_end = overview_url[9:].index('/') + 9
        api_base = overview_url[:api_base_end]
        session_id = overview_url[api_base_end+1:]
        guac_url = '%s/%s/%s' % (api_base, session_id, guac_uri)

        tasks.append(
            GuacRecordingRebuilder(**{
                'debug_mode': False,
                'StreamURL': guac_url,
                'CreateScreenshots': True,
                'ScreenCaptureProgressTriggers': [99],
                'ScreenCapturePrefix': session_id,
                'ReplayRecording': False,
            })
        )

    manager = ThreadManager(max_threads=max_threads)

    logging.info(' [-] Going to process %s recording URLs...' % len(tasks))
    results = manager.execute_batch(tasks)

    logging.info('[+] Retrieving screenshots from workers...')
    for result in manager.get_successful_results():
        if result.result:
            if isinstance(result.result, dict):
                screenshots.extend(result.result.get('screenshots', []))

    logging.info('[+] Crafting the collage...')
    output_path = ImageCollage(screenshots).create_self_contained_image_collage_html()



import ctypes
import multiprocessing
import os
import time


import numpy as np

from fastapi_video_streaming.video_sources.tisgrabber import tisgrabber as tis
from fastapi_video_streaming.video_sources.video_source import VideoSource


class TisCameraCapture:
    def __init__(self, image_provider_key: str, config: dict):
        config_file = config["device_config_file"]
        fps = config["fps"]
        self.waiting_time_ms = int(1 / fps * 2000)
        tisgrabber_path = os.path.join(
            os.path.dirname(__file__), "tisgrabber", "tisgrabber_x64.dll"
        )
        self.ic = ctypes.cdll.LoadLibrary(tisgrabber_path)
        tis.declareFunctions(self.ic)
        self.ic.IC_InitLibrary(0)
        if os.path.exists(config_file):
            self.hGrabber = self.ic.IC_LoadDeviceStateFromFile(None, tis.T(config_file))
        else:
            self.hGrabber = self.ic.IC_ShowDeviceSelectionDialog(None)
            # 指定のコンフィグファイルが存在しなかった場合は，GUIでの設定を強制する
            config["show_config_gui"] = True
            self.ic.IC_MsgBox(
                tis.T("Configuration file not found. Required to configure on GUI."),
                tis.T("Config not found"),
            )
        if not self.ic.IC_IsDevValid(self.hGrabber):
            self.ic.IC_MsgBox(tis.T("No device opened"), tis.T("Simple Live Video"))
            exit(1)
        # config にて show_config_gui=Trueの場合，Viewerありでストリーミングを開始し，撮影設定及び設定内容の保存
        if config["show_config_gui"]:
            self.ic.IC_StartLive(self.hGrabber, 1)
            self.ic.IC_ShowPropertyDialog(self.hGrabber)
            self.ic.IC_SaveDeviceStateToFile(self.hGrabber, tis.T(config_file))
            self.ic.IC_MsgBox(
                tis.T("Configuration saved to {}".format(config_file)),
                tis.T("Simple Live Video"),
            )
            self.ic.IC_StopLive(self.hGrabber)

        # Viewerなしでストリーミングを開始
        self.ic.IC_StartLive(self.hGrabber, 0)

        while True:
            if (
                self.ic.IC_SnapImage(self.hGrabber, self.waiting_time_ms)
                == tis.IC_SUCCESS
            ):
                self.Width = ctypes.c_long()
                self.Height = ctypes.c_long()
                BitsPerPixel = ctypes.c_int()
                colorformat = ctypes.c_int()
                self.ic.IC_GetImageDescription(
                    self.hGrabber, self.Width, self.Height, BitsPerPixel, colorformat
                )
                self.bpp = int(BitsPerPixel.value / 8.0)
                self.buffer_size = (
                    self.Width.value * self.Height.value * BitsPerPixel.value
                )
                return None
            else:
                time.sleep(1 / 1000)

    def read(self):
        while True:
            if (
                self.ic.IC_SnapImage(self.hGrabber, self.waiting_time_ms)
                == tis.IC_SUCCESS
            ):
                imagePtr = self.ic.IC_GetImagePtr(self.hGrabber)
                imagedata = ctypes.cast(
                    imagePtr, ctypes.POINTER(ctypes.c_ubyte * self.buffer_size)
                )
                img = np.ndarray(
                    buffer=imagedata.contents,
                    dtype=np.uint8,
                    shape=(self.Height.value, self.Width.value, self.bpp),
                )
                img = np.flipud(img)
                return img
            else:
                time.sleep(1 / 1000)


class TisCamera(VideoSource):
    captures = {}
    capture_processes = {}

    @classmethod
    def capture(cls, image_provider_key):
        while True:
            cls.capture_processes[image_provider_key]["latest_frame"] = cls.captures[
                image_provider_key
            ].read()
            time.sleep(1 / 1000)

    def __init__(
        self, image_provider_key: str, width: int, jpeg_quality: int, config: dict
    ) -> None:
        image_provider_key = "cam1"
        super().__init__(
            image_provider_key=image_provider_key,
            width=width,
            jpeg_quality=jpeg_quality,
        )
        if image_provider_key not in TisCamera.captures.keys():
            TisCamera.captures[image_provider_key] = TisCameraCapture(
                image_provider_key=image_provider_key, config=config
            )
        if image_provider_key not in TisCamera.capture_processes.keys():
            TisCamera.capture_processes[image_provider_key] = {
                "process": multiprocessing.Process(
                    target=TisCamera.capture, args=(image_provider_key,)
                ),
                "latest_frame": None,
            }
            TisCamera.capture_processes[image_provider_key]["process"].start()

    def get_frame(self):
        frame = None
        while frame is None:
            time.sleep(1 / 1000)
            frame = TisCamera.capture_processes[self.image_provider_key]["latest_frame"]
        return frame

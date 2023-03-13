import ctypes
import os
import time


import numpy as np

from fastapi_video_streaming.video_sources.tisgrabber import tisgrabber as tis
from fastapi_video_streaming.video_sources.video_source import BaseCapture


class TisCameraCapture(BaseCapture):
    def __init__(self, profile: dict):
        config_file = profile["device_config_file"]
        fps = profile["fps"]
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
            profile["show_config_gui"] = True
            self.ic.IC_MsgBox(
                tis.T("Configuration file not found. Required to configure on GUI."),
                tis.T("Config not found"),
            )
        if not self.ic.IC_IsDevValid(self.hGrabber):
            self.ic.IC_MsgBox(tis.T("No device opened"), tis.T("Simple Live Video"))
            exit(1)
        # config にて show_config_gui=Trueの場合，Viewerありでストリーミングを開始し，撮影設定及び設定内容の保存
        if profile["show_config_gui"]:
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
                time.sleep(0.1)

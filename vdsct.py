"""Vicon DataStream SDK ctypes interface."""


import contextlib
import ctypes
import ctypes.util


class Client:
    """Vicon DataStreamSDK Client."""

    def __init__(self) -> None:
        self._client_p: ctypes.c_void_p = _client_create()
        """Pointer to ViconDataStreamSDK_C client object."""

    def destroy(self) -> None:
        _client_destroy(self._client_p)
        self._client_p = None

    def connect(self, host: bytes | str) -> None:
        _client_connect(self._client_p, host)

    def get_frame(self):
        _client_getframe(self._client_p)

    def get_subject_count(self) -> int:
        return _client_getsubjectcount(self._client_p)

    def get_segment_count(self, subject: bytes | str) -> int:
        return _client_getsegmentcount(self._client_p, subject)


class Output_GetSubjectCount(ctypes.Structure):
    _fields_ = [("Result", ctypes.c_int),
                ("SubjectCount", ctypes.c_uint)]


class Output_GetSegmentCount(ctypes.Structure):
    _fields_ = [("Result", ctypes.c_int),
                ("SegmentCount", ctypes.c_uint)]


def load_library(path=None):
    global _so
    # Load the library
    if path is None:
        path = (ctypes.util.find_library("ViconDataStreamSDK_C") 
                or "libViconDataStreamSDK_C.so")
    _so = ctypes.cdll.LoadLibrary(path)

    # Configure the functions
    _so.Client_Create.restype = ctypes.c_void_p
    _so.Client_Connect.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _so.Client_Destroy.argtypes = [ctypes.c_void_p]
    _so.Client_Destroy.restype = None
    _so.Client_GetFrame.argtypes = [ctypes.c_void_p]
    _so.Client_GetSubjectCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _so.Client_GetSegmentCount.argtypes = [
        ctypes.c_void_p,  ctypes.c_char_p, ctypes.c_void_p
    ]


def so():
    if _so is None:
        load_library()
    return _so


def _client_create():
    """Low-level interface to ViconDataStreamSDK_C Client_Create"""
    client_p = so().Client_Create()
    assert client_p, "Null pointer returned by client_create"
    return client_p


def _client_destroy(client):
    """Low-level interface to ViconDataStreamSDK_C Client_Destroy"""
    if client:
        so().Client_Destroy(client)


def _client_connect(client_p, host: bytes | str):
    """Low-level interface to ViconDataStreamSDK_C Client_Connect"""
    # Convert host to bytes, if str
    if isinstance(host, str):
        host = host.encode()

    r = so().Client_Connect(client_p, host)
    if Result[r] != 'Success':
        raise RuntimeError(Result[r])


def _client_getframe(client_p):
    """Low-level interface to ViconDataStreamSDK_C Client_GetFrame"""
    r = so().Client_GetFrame(client_p)
    if Result[r] != 'Success':
        raise RuntimeError(Result[r])


def _client_getsubjectcount(client_p):
    """Low-level interface to ViconDataStreamSDK_C Client_GetSubjectCount"""
    out = Output_GetSubjectCount()
    so().Client_GetSubjectCount(client_p, ctypes.byref(out))
    if Result[out.Result] != 'Success':
        raise RuntimeError(Result[out.Result])
    return out.SubjectCount


def _client_getsegmentcount(client_p, subject):
    """Low-level interface to ViconDataStreamSDK_C Client_GetSegmentCount"""
    # Convert subject to bytes, if str
    if isinstance(subject, str):
        subject = subject.encode()

    out = Output_GetSegmentCount()
    so().Client_GetSegmentCount(client_p, subject, ctypes.byref(out))
    if Result[out.Result] != 'Success':
        raise RuntimeError(Result[out.Result])
    return out.SegmentCount


@contextlib.contextmanager
def client():
    c = Client()
    try:
        yield c
    finally:
        c.destroy()


_so = None
"""DataStreamSDK library shared object."""


Result = [
    'Unknown',
    'NotImplemented',
    'Success',
    'InvalidHostName',
    'InvalidMulticastIP',
    'ClientAlreadyConnected',
    'ClientConnectionFailed',
    'ServerAlreadyTransmittingMulticast',
    'ServerNotTransmittingMulticast',
    'NotConnected',
    'NoFrame',
    'InvalidIndex',
    'InvalidCameraName',
    'InvalidSubjectName',
    'InvalidSegmentName',
    'InvalidMarkerName',
    'InvalidDeviceName',
    'InvalidDeviceOutputName',
    'InvalidLatencySampleName',
    'CoLinearAxes',
    'LeftHandedAxes',
    'HapticAlreadySet',
    'EarlyDataRequested',
    'LateDataRequested',
    'InvalidOperation',
    'NotSupported',
    'ConfigurationFailed',
    'NotPresent',
]
"""ViconDataStreamSDK result codes enum."""

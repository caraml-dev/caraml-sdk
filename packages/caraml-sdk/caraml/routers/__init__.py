from __future__ import absolute_import

import signal
import sys

from caraml.routers.ensembler import Ensembler, EnsemblerType, PyFuncEnsembler
from caraml.routers.project import Project
from caraml.routers.router.router import Router
from caraml.routers.session import TuringSession
from caraml.routers.version import VERSION as __version__

import caraml.routers as turing

active_session: TuringSession = TuringSession(
    host="http://localhost:8080", use_google_oauth=False
)


def set_url(url: str, use_google_oauth: bool = True):
    """
    Set Turing API URL

    :param url: Turing API URL
    :param use_google_oauth: whether use google auth or not
    """

    global active_session
    active_session = TuringSession(host=url, use_google_oauth=use_google_oauth)


def set_project(project_name: str):
    """
    Set active project

    :param project_name: project name
    """
    active_session.set_project(project_name)


__all__ = ["set_url", "set_project", "active_session"]

def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

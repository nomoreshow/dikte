"""Menu-bar activation behavior, without constructing the whole application."""

import sys
import types
import unittest
from typing import cast
from unittest import mock

from PyQt6.QtWidgets import QSystemTrayIcon  # type: ignore[import-not-found]

from dikte import app


class TrayClicks(unittest.TestCase):
    @staticmethod
    def target(*, recording=False, ask_state=app.IDLE):
        calls = []
        target = types.SimpleNamespace(
            recording=recording,
            ask_state=ask_state,
            menu=types.SimpleNamespace(popup=lambda _position: calls.append("menu")),
            open_settings=lambda: calls.append("settings"),
            _toggle=lambda: calls.append("toggle"),
            _toggle_ask=lambda: calls.append("ask"),
        )
        return target, calls

    def test_macos_does_not_attach_the_native_context_menu(self):
        self.assertFalse(app._uses_native_tray_context_menu("darwin"))

    def test_other_platforms_keep_the_native_context_menu(self):
        self.assertTrue(app._uses_native_tray_context_menu("linux"))

    def test_an_idle_macos_left_click_starts_dictation_only(self):
        target, calls = self.target()
        with mock.patch.object(sys, "platform", "darwin"):
            app.Dikte._tray_clicked(
                cast(app.Dikte, target), QSystemTrayIcon.ActivationReason.Trigger,
            )
        self.assertEqual(calls, ["toggle"])

    def test_a_macos_right_click_opens_the_menu_only(self):
        target, calls = self.target()
        with mock.patch.object(sys, "platform", "darwin"):
            app.Dikte._tray_clicked(
                cast(app.Dikte, target), QSystemTrayIcon.ActivationReason.Context,
            )
        self.assertEqual(calls, ["menu"])

    def test_a_recording_macos_left_click_stops_dictation(self):
        target, calls = self.target(recording=True)
        with mock.patch.object(sys, "platform", "darwin"):
            app.Dikte._tray_clicked(
                cast(app.Dikte, target), QSystemTrayIcon.ActivationReason.Trigger,
            )
        self.assertEqual(calls, ["toggle"])

    def test_a_recording_macos_left_click_stops_the_agent_capture(self):
        target, calls = self.target(recording=True, ask_state=app.RECORDING)
        with mock.patch.object(sys, "platform", "darwin"):
            app.Dikte._tray_clicked(
                cast(app.Dikte, target), QSystemTrayIcon.ActivationReason.Trigger,
            )
        self.assertEqual(calls, ["ask"])

    def test_other_platforms_keep_left_click_recording(self):
        target, calls = self.target()
        with mock.patch.object(sys, "platform", "linux"):
            app.Dikte._tray_clicked(
                cast(app.Dikte, target), QSystemTrayIcon.ActivationReason.Trigger,
            )
        self.assertEqual(calls, ["toggle"])


if __name__ == "__main__":
    unittest.main()
